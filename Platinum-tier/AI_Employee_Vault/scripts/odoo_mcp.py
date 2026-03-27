#!/usr/bin/env python3
"""
Odoo MCP Server - Gold Tier
Connects to Odoo ERP via JSON-RPC for accounting, invoicing, and CEO Briefing generation.
Integrates with SKILL_ReasoningLoop and SKILL_CEOBriefing
"""

import xmlrpc.client
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

# Setup logging
LOGS_FOLDER = Path(__file__).parent.parent / 'logs'
LOGS_FOLDER.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_FOLDER / 'odoo.log', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('OdooMCP')

# Odoo Configuration
# 🔐 SECURITY: Load from environment variables (create .env file)
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'ai_employee_company')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin@aiemployee.com')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')  # Required: Set in .env file


class OdooMCP:
    """Odoo MCP Client for Gold Tier operations"""
    
    def __init__(self, url: str = ODOO_URL, db: str = ODOO_DB, 
                 username: str = ODOO_USERNAME, password: str = ODOO_PASSWORD):
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.uid: Optional[int] = None
        self.common = None
        self.models = None
        self._connect()
    
    def _connect(self) -> bool:
        """Establish connection to Odoo server with retry"""
        max_retries = 5
        retry_delay = 3  # seconds
        
        for attempt in range(max_retries):
            try:
                # Connect to common and object endpoints
                self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
                
                # Authenticate - Odoo 19 requires user_agent_env as keyword argument
                self.uid = self.common.authenticate(
                    self.db, 
                    self.username, 
                    self.password,
                    {'user_agent': 'OdooMCP-GoldTier'}
                )
                
                if self.uid:
                    logger.info(f"Connected to Odoo at {self.url} as user ID: {self.uid}")
                    return True
                else:
                    logger.error("Odoo authentication failed - check credentials")
                    return False
                    
            except Exception as e:
                error_msg = str(e)
                if attempt < max_retries - 1:
                    logger.warning(f"Connection attempt {attempt + 1} failed: {error_msg}")
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    import time
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Connection failed after {max_retries} attempts: {error_msg}")
                    return False
        
        return False
    
    def _execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute Odoo RPC call with error recovery"""
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                if not self.uid:
                    if not self._connect():
                        raise Exception("Not connected to Odoo")
                
                result = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    model, method, args, kwargs
                )
                logger.debug(f"RPC call: {model}.{method} - Success")
                return result
                
            except Exception as e:
                logger.warning(f"RPC call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    import time
                    time.sleep(retry_delay)
                else:
                    logger.error(f"RPC call failed after {max_retries} attempts")
                    raise
    
    def create_customer(self, name: str, email: str, phone: str = None) -> Optional[int]:
        """Create a new customer (res.partner) in Odoo"""
        try:
            logger.info(f"Creating customer: {name} ({email})")
            
            values = {
                'name': name,
                'email': email,
                'customer_rank': 1,  # Mark as customer
            }
            if phone:
                values['phone'] = phone
            
            customer_ids = self._execute('res.partner', 'create', [values])
            
            if customer_ids:
                logger.info(f"Customer created with ID: {customer_ids[0]}")
                return customer_ids[0]
            return None
            
        except Exception as e:
            logger.error(f"Failed to create customer: {str(e)}")
            return None
    
    def create_invoice(self, customer_id: int, amount: float, description: str, 
                       invoice_type: str = 'out_invoice') -> Optional[int]:
        """Create a new invoice in Odoo"""
        try:
            logger.info(f"Creating invoice for customer {customer_id}: ${amount} - {description}")
            
            # Create invoice header
            invoice_values = {
                'move_type': invoice_type,
                'partner_id': customer_id,
                'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                'invoice_origin': description,
                'ref': f"INV-{datetime.now().strftime('%Y%m%d')}-{customer_id}",
            }
            
            invoice_ids = self._execute('account.move', 'create', [invoice_values])
            
            if not invoice_ids:
                logger.error("Failed to create invoice")
                return None
            
            invoice_id = invoice_ids[0]
            
            # Get default product for invoicing (or create one)
            product_id = self._get_or_create_product(description)
            
            # Create invoice line
            invoice_line_values = {
                'move_id': invoice_id,
                'product_id': product_id,
                'name': description,
                'price_unit': amount,
                'quantity': 1,
            }
            
            self._execute('account.move.line', 'create', [invoice_line_values])
            
            logger.info(f"Invoice created with ID: {invoice_id}")
            return invoice_id
            
        except Exception as e:
            logger.error(f"Failed to create invoice: {str(e)}")
            return None
    
    def _get_or_create_product(self, name: str) -> int:
        """Get existing product or create a default one"""
        try:
            # Search for existing product
            product_ids = self._execute('product.product', 'search', [['name', '=', name]])
            
            if product_ids:
                return product_ids[0]
            
            # Create default service product
            product_values = {
                'name': name,
                'type': 'service',
                'list_price': 0,
            }
            product_ids = self._execute('product.product', 'create', [product_values])
            return product_ids[0] if product_ids else 1
            
        except Exception as e:
            logger.error(f"Failed to get/create product: {str(e)}")
            return 1  # Return default product ID
    
    def get_weekly_revenue(self) -> Dict[str, Any]:
        """Get revenue summary for the current week"""
        try:
            logger.info("Fetching weekly revenue")

            # Calculate date range for current week
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            domain = [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', start_of_week.strftime('%Y-%m-%d')),
                ('invoice_date', '<=', end_of_week.strftime('%Y-%m-%d')),
            ]

            invoices = self._execute('account.move', 'search_read',
                                     domain,
                                     fields=['id', 'name', 'amount_total', 'amount_residual',
                                            'partner_id', 'invoice_date'])

            total_revenue = sum(inv.get('amount_total', 0) for inv in (invoices or []))
            total_outstanding = sum(inv.get('amount_residual', 0) for inv in (invoices or []))

            result = {
                'period': f"{start_of_week.strftime('%Y-%m-%d')} to {end_of_week.strftime('%Y-%m-%d')}",
                'total_revenue': total_revenue,
                'total_outstanding': total_outstanding,
                'total_collected': total_revenue - total_outstanding,
                'invoice_count': len(invoices) if invoices else 0,
                'invoices': invoices or [],
            }

            logger.info(f"Weekly revenue: ${total_revenue} ({len(invoices) if invoices else 0} invoices)")
            return result

        except Exception as e:
            logger.error(f"Failed to get weekly revenue: {str(e)}")
            return {
                'period': 'Error',
                'total_revenue': 0,
                'total_outstanding': 0,
                'total_collected': 0,
                'invoice_count': 0,
                'invoices': [],
                'error': str(e)
            }
    
    def generate_ceo_briefing(self) -> str:
        """Generate CEO Briefing summary text using Odoo data"""
        try:
            logger.info("Generating CEO Briefing")

            # Get weekly revenue
            revenue_data = self.get_weekly_revenue()

            # Get pending invoices
            pending_invoices = self._execute('account.move', 'search_read',
                                             [('move_type', '=', 'out_invoice'),
                                              ('state', '=', 'posted'),
                                              ('payment_state', '=', 'not_paid')],
                                             fields=['id', 'name', 'amount_total', 'partner_id'])

            # Get top customers
            customers = self._execute('res.partner', 'search_read',
                                      [('customer_rank', '>', 0)],
                                      fields=['id', 'name', 'email'],
                                      limit=10)
            
            # Build briefing text
            briefing = []
            briefing.append("=" * 60)
            briefing.append("MONDAY MORNING CEO BRIEFING")
            briefing.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            briefing.append("=" * 60)
            briefing.append("")
            
            briefing.append("📊 WEEKLY REVENUE SUMMARY")
            briefing.append("-" * 40)
            briefing.append(f"Period: {revenue_data.get('period', 'N/A')}")
            briefing.append(f"Total Revenue: ${revenue_data.get('total_revenue', 0):,.2f}")
            briefing.append(f"Collected: ${revenue_data.get('total_collected', 0):,.2f}")
            briefing.append(f"Outstanding: ${revenue_data.get('total_outstanding', 0):,.2f}")
            briefing.append(f"Invoices Issued: {revenue_data.get('invoice_count', 0)}")
            briefing.append("")
            
            briefing.append("⚠️ PENDING PAYMENTS")
            briefing.append("-" * 40)
            if pending_invoices:
                for inv in pending_invoices[:5]:  # Top 5
                    partner = inv.get('partner_id', [0, 'Unknown'])[1] if inv.get('partner_id') else 'Unknown'
                    briefing.append(f"  - {inv.get('name', 'N/A')}: ${inv.get('amount_total', 0):,.2f} ({partner})")
            else:
                briefing.append("  No pending payments - All clear!")
            briefing.append("")
            
            briefing.append("👥 TOP CUSTOMERS")
            briefing.append("-" * 40)
            if customers:
                for cust in customers[:5]:  # Top 5
                    briefing.append(f"  - {cust.get('name', 'Unknown')} ({cust.get('email', 'N/A')})")
            else:
                briefing.append("  No customer data available")
            briefing.append("")
            
            briefing.append("💡 ACTION ITEMS & SUGGESTIONS")
            briefing.append("-" * 40)
            
            # Generate suggestions based on data
            suggestions = []
            if revenue_data.get('total_outstanding', 0) > 0:
                suggestions.append("  1. Follow up on outstanding payments")
            if len(pending_invoices) > 5:
                suggestions.append("  2. Review payment collection process")
            if revenue_data.get('invoice_count', 0) == 0:
                suggestions.append("  3. No invoices this week - review sales pipeline")
            
            if not suggestions:
                briefing.append("  ✓ All systems operational - No critical actions needed")
            else:
                briefing.extend(suggestions)
            
            briefing.append("")
            briefing.append("=" * 60)
            briefing.append("END OF BRIEFING")
            briefing.append("=" * 60)
            
            briefing_text = "\n".join(briefing)
            logger.info("CEO Briefing generated successfully")
            
            return briefing_text
            
        except Exception as e:
            logger.error(f"Failed to generate CEO Briefing: {str(e)}")
            return f"CEO Briefing Generation Error: {str(e)}"
    
    def get_account_summary(self) -> Dict[str, Any]:
        """Get overall account summary"""
        try:
            # Receivables (money owed to us)
            receivables = self._execute('account.move', 'search_read',
                                        [('move_type', '=', 'out_invoice'),
                                         ('state', '=', 'posted')],
                                        fields=['amount_residual'])
            
            # Payables (money we owe)
            payables = self._execute('account.move', 'search_read',
                                     [('move_type', '=', 'in_invoice'),
                                      ('state', '=', 'posted')],
                                     fields=['amount_residual'])
            
            total_receivable = sum(r.get('amount_residual', 0) for r in (receivables or []))
            total_payable = sum(p.get('amount_residual', 0) for p in (payables or []))
            
            return {
                'total_receivable': total_receivable,
                'total_payable': total_payable,
                'balance': total_receivable - total_payable,
                'receivable_count': len(receivables) if receivables else 0,
                'payable_count': len(payables) if payables else 0,
            }
            
        except Exception as e:
            logger.error(f"Failed to get account summary: {str(e)}")
            return {'error': str(e)}


# CLI Interface for testing and direct usage
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Odoo MCP Server - Gold Tier")
    print("=" * 60)
    
    # Initialize client
    odoo = OdooMCP()
    
    if not odoo.uid:
        print("\n⚠️  Odoo not connected - Database may not exist yet")
        print("   Open http://localhost:8069 in browser to create database")
        print("   Default: admin / admin\n")
        
        # Demo mode - show what briefing would look like
        print("=" * 60)
        print("DEMO MODE - Odoo Connection Pending")
        print("=" * 60)
        print("""
MONDAY MORNING CEO BRIEFING
Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

📊 WEEKLY REVENUE SUMMARY
----------------------------------------
Status: Awaiting Odoo database creation
Action: Open http://localhost:8069 to initialize

⚠️ PENDING PAYMENTS
----------------------------------------
Status: No connection - cannot fetch data

👥 TOP CUSTOMERS  
----------------------------------------
Status: No connection - cannot fetch data

💡 ACTION ITEMS
----------------------------------------
1. Open http://localhost:8069 in browser
2. Create database 'odoo' with admin/admin
3. Re-run this script to get live data

============================================================
END OF BRIEFING
============================================================
""")
        sys.exit(0)
    
    print(f"✓ Connected to Odoo: {ODOO_URL}")
    print(f"✓ Database: {ODOO_DB}")
    print(f"✓ User ID: {odoo.uid}")
    print("=" * 60)
    
    # Demo: Show account summary
    print("\n📊 Account Summary:")
    summary = odoo.get_account_summary()
    print(f"  Receivables: ${summary.get('total_receivable', 0):,.2f}")
    print(f"  Payables: ${summary.get('total_payable', 0):,.2f}")
    print(f"  Balance: ${summary.get('balance', 0):,.2f}")
    
    # Demo: Generate CEO Briefing
    print("\n" + "=" * 60)
    print("📋 CEO BRIEFING")
    print("=" * 60)
    briefing = odoo.generate_ceo_briefing()
    print(briefing)
    
    print("\n" + "=" * 60)
    print("Odoo MCP Ready for Gold Tier Operations")
    print("=" * 60 + "\n")
