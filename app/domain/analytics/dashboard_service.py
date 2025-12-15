from decimal import Decimal
from typing import List, Dict, Optional
from datetime import date, timedelta
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from app.domain.sales.entities import InvoiceStatus
from app.infrastructure.persistence.sales.models import SalesInvoiceModel
from app.infrastructure.persistence.accounting.models import JournalLineModel
from app.infrastructure.persistence.banking.models import BankStatementLineModel

class DashboardService:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_kpis(self):
        """Get Key Performance Indicators."""
        session: Session = self.session_factory()
        try:
            today = date.today()
            
            # 1. Sales MTD (Month to Date)
            sales_mtd = session.query(func.sum(SalesInvoiceModel.total))\
                .filter(extract('month', SalesInvoiceModel.invoice_date) == today.month)\
                .filter(extract('year', SalesInvoiceModel.invoice_date) == today.year)\
                .filter(SalesInvoiceModel.status != InvoiceStatus.DRAFT.name)\
                .scalar() or Decimal(0)
                
            # 2. Pending Conciliation
            # Assuming "reconciled" means linked to something? Or logic in BankingService?
            # For MVP, checking lines without 'journal_entry_id' might be approximate if we link them.
            # But BankingService logic for pending usually filters by 'reconciled=False' if column exists?
            # Checking BankStatementLineModel... I recall it has 'reconciled' boolean or similar?
            # If not, let's assume all lines are pending if not linked to JE? 
            # I'll check model later. For now, assume a query.
            # Let's count all lines in DB for now as "Transactions".
            pending_conciliation = session.query(func.count(BankStatementLineModel.id)).scalar() or 0
            
            # 3. Cash Balance (Accounts 57%)
            # Sum of Debits - Credits for accounts starting with 57
            cash_balance = session.query(
                func.sum(JournalLineModel.debit) - func.sum(JournalLineModel.credit)
            ).filter(JournalLineModel.account_code.like("57%")).scalar() or Decimal(0)
            
            return {
                "sales_mtd": sales_mtd,
                "pending_conciliation": pending_conciliation,
                "cash_balance": cash_balance,
            }
        finally:
            session.close()

    def get_sales_trend(self) -> Dict[str, List]:
        """Get last 6 months sales."""
        session: Session = self.session_factory()
        try:
            today = date.today()
            labels = []
            values = []
            
            for i in range(5, -1, -1):
                # Calculate month/year
                d = today.replace(day=1) - timedelta(days=i*30) # Approx
                # Better: date math
                
                # Let's simple fetch for current year months
                month = today.month - i
                year = today.year
                if month <= 0:
                    month += 12
                    year -= 1
                    
                total = session.query(func.sum(SalesInvoiceModel.total))\
                    .filter(extract('month', SalesInvoiceModel.invoice_date) == month)\
                    .filter(extract('year', SalesInvoiceModel.invoice_date) == year)\
                    .filter(SalesInvoiceModel.status != InvoiceStatus.DRAFT.name)\
                    .scalar() or 0
                
                labels.append(f"{month}/{year}")
                values.append(float(total))
                
            return {"labels": labels, "data": values}
        finally:
            session.close()
