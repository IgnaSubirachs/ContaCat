from typing import List, Dict, Optional
from datetime import date, timedelta
from decimal import Decimal
import logging

from app.domain.treasury.entities import BankAccount
from app.infrastructure.persistence.treasury.repository import SqlAlchemyTreasuryRepository
from app.domain.sales.repositories import SalesInvoiceRepository
from app.domain.sales.entities import InvoiceStatus

logger = logging.getLogger(__name__)


class TreasuryService:
    """Treasury and Cash Flow management service."""
    
    def __init__(
        self, 
        treasury_repo: SqlAlchemyTreasuryRepository, 
        sales_invoice_repo: Optional[SalesInvoiceRepository] = None,
        accounting_service=None,
        payroll_repo=None
    ):
        self.treasury_repo = treasury_repo
        self.sales_invoice_repo = sales_invoice_repo
        self._accounting = accounting_service
        self._payroll_repo = payroll_repo

    def create_bank_account(self, name: str, iban: str, bic: str = None, account_code: str = None) -> BankAccount:
        account = BankAccount(name=name, iban=iban, bic=bic, account_code=account_code)
        self.treasury_repo.save(account)
        return account

    def list_bank_accounts(self) -> List[BankAccount]:
        return self.treasury_repo.list_all()
    
    def get_current_cash_balance(self) -> Decimal:
        """Get current cash from accounting (accounts 57x)."""
        if not self._accounting:
            return Decimal(0)
        
        accounts = self._accounting.list_accounts()
        total = Decimal(0)
        
        for account in accounts:
            if account.code.startswith("57"):
                balance = self._accounting.get_account_balance(account.code)
                total += balance
        
        return total
    
    def get_receivables_schedule(self, days_ahead: int = 90) -> List[Dict]:
        """Get receivables schedule for forecasting."""
        if not self.sales_invoice_repo:
            return []
        
        invoices = self.sales_invoice_repo.list_all()
        receivables = []
        today = date.today()
        cutoff = today + timedelta(days=days_ahead)
        
        for invoice in invoices:
            if invoice.status != InvoiceStatus.POSTED:
                continue
            
            pending = invoice.total_amount - (invoice.amount_paid or Decimal(0))
            
            if pending <= 0:
                continue
            
            due = invoice.due_date or invoice.invoice_date
            
            if due <= cutoff:
                receivables.append({
                    "invoice_number": invoice.invoice_number,
                    "partner_id": invoice.partner_id,
                    "due_date": due,
                    "amount": float(pending),
                    "days_until_due": (due - today).days
                })
        
        receivables.sort(key=lambda x: x["due_date"])
        return receivables
    
    def get_recurring_expenses_estimate(self) -> Dict:
        """Estimate monthly recurring expenses."""
        expenses = {"payroll_monthly": 0.0, "total_monthly": 0.0}
        
        if self._payroll_repo:
            try:
                from app.domain.hr.entities import PayrollStatus
                payrolls = self._payroll_repo.list_all()
                recent = [p for p in payrolls if p.status == PayrollStatus.PAID][-10:]
                
                if recent:
                    avg = sum(float(p.net_salary) for p in recent) / len(recent)
                    expenses["payroll_monthly"] = avg
            except Exception as e:
                logger.warning(f"Payroll estimate error: {e}")
        
        expenses["total_monthly"] = expenses["payroll_monthly"]
        return expenses

    def get_cash_flow_forecast(self, days: int = 90) -> Dict:
        """Calculate comprehensive cash flow forecast."""
        today = date.today()
        current_cash = float(self.get_current_cash_balance())
        receivables = self.get_receivables_schedule(days)
        recurring = self.get_recurring_expenses_estimate()
        
        rec_30 = sum(r["amount"] for r in receivables if r["days_until_due"] <= 30)
        rec_60 = sum(r["amount"] for r in receivables if 30 < r["days_until_due"] <= 60)
        rec_90 = sum(r["amount"] for r in receivables if 60 < r["days_until_due"] <= 90)
        
        monthly_exp = recurring["total_monthly"]
        
        projections = {
            "day_0": current_cash,
            "day_30": current_cash + rec_30 - monthly_exp,
            "day_60": current_cash + rec_30 + rec_60 - (monthly_exp * 2),
            "day_90": current_cash + rec_30 + rec_60 + rec_90 - (monthly_exp * 3)
        }
        
        return {
            "current_date": today.isoformat(),
            "forecast_days": days,
            "current_cash": current_cash,
            "projections": projections,
            "receivables": receivables,
            "recurring_expenses": recurring,
            "total_receivables_90d": rec_30 + rec_60 + rec_90
        }
    
    def calculate_liquidity_risk(self, forecast: Dict) -> Dict:
        """Analyze liquidity risk."""
        risk = {"level": "LOW", "alerts": [], "recommendations": []}
        
        proj = forecast["projections"]
        threshold = 1000
        
        if proj["day_30"] < 0:
            risk["level"] = "HIGH"
            risk["alerts"].append("⚠️ CRÍTIC: Risc liquiditat en 30 dies")
            risk["recommendations"].append("Accelera cobraments")
        elif proj["day_60"] < 0:
            risk["level"] = "HIGH"
            risk["alerts"].append("⚠️ Risc en 60 dies")
        elif proj["day_90"] < 0:
            risk["level"] = "MEDIUM"
            risk["alerts"].append("⚠️ Risc lleu en 90 dies")
        elif proj["day_30"] < threshold:
            risk["level"] = "MEDIUM"
            risk["alerts"].append(f"💡 Liquiditat baixa (< {threshold}€)")
        else:
            risk["alerts"].append("✅ Salut financera bona")
        
        return risk
    
    def get_treasury_dashboard(self) -> Dict:
        """Get dashboard data."""
        forecast = self.get_cash_flow_forecast(90)
        risk = self.calculate_liquidity_risk(forecast)
        
        return {
            "forecast": forecast,
            "risk": risk,
            "top_receivables": forecast["receivables"][:5],
            "recurring_expenses": forecast["recurring_expenses"]
        }
