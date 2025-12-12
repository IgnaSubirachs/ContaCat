from typing import List, Dict, Optional
from datetime import date, timedelta
from app.domain.treasury.entities import BankAccount
from app.infrastructure.persistence.treasury.repository import SqlAlchemyTreasuryRepository
from app.domain.sales.repositories import SalesInvoiceRepository
from app.domain.sales.entities import InvoiceStatus

class TreasuryService:
    def __init__(self, treasury_repo: SqlAlchemyTreasuryRepository, sales_invoice_repo: Optional[SalesInvoiceRepository] = None):
        self.treasury_repo = treasury_repo
        self.sales_invoice_repo = sales_invoice_repo

    def create_bank_account(self, name: str, iban: str, bic: str = None, account_code: str = None) -> BankAccount:
        account = BankAccount(name=name, iban=iban, bic=bic, account_code=account_code)
        self.treasury_repo.save(account)
        return account

    def list_bank_accounts(self) -> List[BankAccount]:
        return self.treasury_repo.list_all()

    def get_cash_flow_forecast(self, days: int = 30) -> Dict:
        """
        Calculates expected inflows and outflows for the next `days`.
        """
        today = date.today()
        limit_date = today + timedelta(days=days)
        
        inflow_items = []
        outflow_items = []
        total_inflow = 0
        total_outflow = 0
        
        # 1. Inflows from Posted Sales Invoices (Pending Payment)
        if self.sales_invoice_repo:
            pending_invoices = self.sales_invoice_repo.list_by_status(InvoiceStatus.POSTED)
            for invoice in pending_invoices:
                # Assuming invoice.due_date exists. If not, use date + 30 days default
                # But entity definition usually has due_date
                due_date = getattr(invoice, 'due_date', invoice.date + timedelta(days=30))
                
                if due_date <= limit_date:  # Only include if within forecast period (or overdue?)
                    # Overdue are strictly strictly strictly needed for cash flow too
                    amount = float(invoice.total_amount)
                    inflow_items.append({
                        "date": due_date,
                        "description": f"Factura Venda {invoice.series}/{invoice.year}-{invoice.number}",
                        "amount": amount,
                        "partner": invoice.partner_id # ideally partner name but we might not have it loaded deep
                    })
                    total_inflow += amount
        
        # Sort by date
        inflow_items.sort(key=lambda x: x['date'])
        
        return {
            "forecast_days": days,
            "inflow": inflow_items,
            "outflow": outflow_items,
            "total_inflow": total_inflow,
            "total_outflow": total_outflow,
            "net_flow": total_inflow - total_outflow
        }
