@echo off
REM Create Odoo MCP Server for Gold Tier
cd /d "%~dp0"

set "MCP_FILE=C:\Users\PMLS\Desktop\Hackathon-0\Gold-tier\mcp\odoo_mcp.py"

(
echo #!/usr/bin/env python3
echo """
echo Odoo JSON-RPC MCP Server - Gold Tier
echo Connects to Odoo ERP for accounting, invoicing, and financial operations.
echo """
echo.
echo import json
echo import logging
echo import sys
echo from pathlib import Path
echo from datetime import datetime
echo from flask import Flask, request, jsonify
echo import requests
echo.
echo LOGS_FOLDER = Path('../logs').resolve()
echo LOGS_FOLDER.mkdir(parents=True, exist_ok=True)
echo.
echo logging.basicConfig(
echo     level=logging.DEBUG,
echo     format='%%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s',
echo     handlers=[
echo         logging.FileHandler(LOGS_FOLDER / 'odoo_mcp.log', mode='a'),
echo         logging.StreamHandler(sys.stdout)
echo     ]
echo )
echo logger = logging.getLogger('OdooMCP')
echo.
echo ODOO_URL = 'http://localhost:8069'
echo ODOO_DB = 'odoo_db'
echo ODOO_USERNAME = 'admin'
echo ODOO_PASSWORD = 'admin'
echo MCP_PORT = 3001
echo.
echo app = Flask(__name__)
echo.
echo class OdooClient:
echo     def __init__(self, url, db, username, password):
echo         self.url = url.rstrip('/')
echo         self.db = db
echo         self.username = username
echo         self.password = password
echo         self.uid = None
echo         self.session = requests.Session()
echo.
echo     def _json_request(self, endpoint, params, data=None):
echo         rpc_url = f"{self.url}/{endpoint}"
echo         payload = {'jsonrpc': '2.0', 'method': 'call', 'params': params, 'id': 1}
echo         if data:
echo             payload['params'].update(data)
echo         try:
echo             response = self.session.post(rpc_url, json=payload, timeout=30)
echo             response.raise_for_status()
echo             result = response.json()
echo             if 'error' in result:
echo                 logger.error(f"Odoo RPC Error: {result['error']}")
echo                 return None
echo             return result.get('result', {})
echo         except Exception as e:
echo             logger.error(f"RPC request failed: {e}")
echo             return None
echo.
echo     def authenticate(self):
echo         logger.info(f"Authenticating with Odoo at {self.url}")
echo         result = self._json_request('web/session/authenticate', {'db': self.db, 'login': self.username, 'password': self.password})
echo         if result and result.get('uid'):
echo             self.uid = result['uid']
echo             logger.info(f"Authenticated as user ID: {self.uid}")
echo             return True
echo         logger.error("Authentication failed")
echo         return False
echo.
echo     def get_account_summary(self):
echo         receivables = self.search_read('account.move', domain=[('move_type', '=', 'out_invoice'), ('state', '=', 'posted')], fields=['amount_residual'], limit=1000)
echo         payables = self.search_read('account.move', domain=[('move_type', '=', 'in_invoice'), ('state', '=', 'posted')], fields=['amount_residual'], limit=1000)
echo         total_receivable = sum(r.get('amount_residual', 0) for r in (receivables or []))
echo         total_payable = sum(r.get('amount_residual', 0) for r in (payables or []))
echo         return {'total_receivable': total_receivable, 'total_payable': total_payable, 'balance': total_receivable - total_payable}
echo.
echo     def search_read(self, model, domain=None, fields=None, limit=80):
echo         if not self.uid:
echo             if not self.authenticate():
echo                 return []
echo         params = {'model': model, 'domain': domain or [], 'fields': fields or [], 'limit': limit}
echo         return self._json_request('web/dataset/search_read', params)
echo.
echo     def get_invoices(self, state='posted', limit=10):
echo         domain = [('move_type', '=', 'out_invoice'), ('state', '=', state)]
echo         fields = ['id', 'name', 'partner_id', 'invoice_date', 'amount_total', 'amount_residual', 'state']
echo         return self.search_read('account.move', domain=domain, fields=fields, limit=limit)
echo.
echo     def get_bills(self, state='posted', limit=10):
echo         domain = [('move_type', '=', 'in_invoice'), ('state', '=', state)]
echo         fields = ['id', 'name', 'partner_id', 'invoice_date', 'amount_total', 'amount_residual', 'state']
echo         return self.search_read('account.move', domain=domain, fields=fields, limit=limit)
echo.
echo odoo_client = None
echo.
echo def init_odoo_client():
echo     global odoo_client
echo     odoo_client = OdooClient(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)
echo     odoo_client.authenticate()
echo.
echo @app.route('/health', methods=['GET'])
echo def health():
echo     return jsonify({'status': 'healthy', 'service': 'odoo-mcp', 'odoo_connected': odoo_client is not None and odoo_client.uid is not None, 'timestamp': datetime.now().isoformat()})
echo.
echo @app.route('/account/summary', methods=['GET'])
echo def account_summary():
echo     if not odoo_client or not odoo_client.uid:
echo         return jsonify({'error': 'Not connected to Odoo'}), 503
echo     try:
echo         summary = odoo_client.get_account_summary()
echo         return jsonify(summary)
echo     except Exception as e:
echo         return jsonify({'error': str(e)}), 500
echo.
echo @app.route('/invoices', methods=['GET'])
echo def get_invoices():
echo     if not odoo_client or not odoo_client.uid:
echo         return jsonify({'error': 'Not connected to Odoo'}), 503
echo     state = request.args.get('state', 'posted')
echo     limit = int(request.args.get('limit', 10))
echo     try:
echo         invoices = odoo_client.get_invoices(state=state, limit=limit)
echo         return jsonify({'invoices': invoices, 'count': len(invoices)})
echo     except Exception as e:
echo         return jsonify({'error': str(e)}), 500
echo.
echo @app.route('/bills', methods=['GET'])
echo def get_bills():
echo     if not odoo_client or not odoo_client.uid:
echo         return jsonify({'error': 'Not connected to Odoo'}), 503
echo     state = request.args.get('state', 'posted')
echo     limit = int(request.args.get('limit', 10))
echo     try:
echo         bills = odoo_client.get_bills(state=state, limit=limit)
echo         return jsonify({'bills': bills, 'count': len(bills)})
echo     except Exception as e:
echo         return jsonify({'error': str(e)}), 500
echo.
echo @app.route('/partners', methods=['GET'])
echo def get_partners():
echo     if not odoo_client or not odoo_client.uid:
echo         return jsonify({'error': 'Not connected to Odoo'}), 503
echo     limit = int(request.args.get('limit', 50))
echo     try:
echo         partners = odoo_client.search_read('res.partner', fields=['id', 'name', 'email', 'phone'], limit=limit)
echo         return jsonify({'partners': partners, 'count': len(partners)})
echo     except Exception as e:
echo         return jsonify({'error': str(e)}), 500
echo.
echo if __name__ == '__main__':
echo     logger.info("Starting Odoo MCP Server...")
echo     init_odoo_client()
echo     print("")
echo     print("=" * 60)
echo     print("Odoo JSON-RPC MCP Server")
echo     print("=" * 60)
echo     print(f"Server starting on port {MCP_PORT}")
echo     print(f"Odoo Connected: {'Yes' if odoo_client and odoo_client.uid else 'No'}")
echo     print("=" * 60)
echo     app.run(host='0.0.0.0', port=MCP_PORT, debug=False)
) > "%MCP_FILE%"

echo Odoo MCP Server created at: %MCP_FILE%
echo.
echo To run:
echo   cd C:\Users\PMLS\Desktop\Hackathon-0\Gold-tier\mcp
echo   pip install flask requests
echo   python odoo_mcp.py
pause
