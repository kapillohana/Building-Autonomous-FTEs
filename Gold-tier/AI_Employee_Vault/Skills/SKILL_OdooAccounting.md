---
name: odoo-accounting
description: Manages Odoo ERP for business accounting and weekly briefing
when_to_use: Weekly or when financial data needed
---

## Description
Connects to local Odoo ERP (http://localhost:8069) via JSON-RPC.
Handles customers, products, invoices, revenue tracking, and CEO Briefing generation.

## Models

### Customers (res.partner)
- Create and manage customer records
- Store name, email, phone, address

### Products (product.product)
- Service and product catalog
- Pricing and categorization

### Invoices (account.move)
- Customer invoices (out_invoice)
- Vendor bills (in_invoice)
- Payment tracking

## Functions

### create_invoice(customer, amount)
Creates invoice for customer with specified amount.
Returns invoice ID.

### get_weekly_revenue()
Returns current week's revenue summary:
- Total revenue, collected, outstanding
- Invoice count and list

### generate_ceo_briefing()
Generates Monday Morning CEO Briefing:
- Weekly revenue
- Pending payments
- Top customers
- Action items

## Integration with SKILL_ReasoningLoop

```
1. Reasoning loop runs weekly audit (Sunday night)
2. Triggers odoo-accounting skill
3. Calls generate_ceo_briefing()
4. Saves briefing to /Briefings/
5. Logs to audit trail
6. Moves to /Done
```

## Usage Prompt
Invoke odoo-accounting: Generate weekly CEO briefing and check invoices

## Parameters
- period: weekly (default)
- include_suggestions: true

## Logging
All operations logged to: ../logs/odoo.log
