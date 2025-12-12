from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import date


from app.domain.accounting.services import AccountingService
from collections import defaultdict
import datetime

@dataclass
class FinancialRatios:
    """Financial ratios for a fiscal period."""
    # Liquiditat
    current_ratio: Optional[Decimal] = None  # Actiu Corrent / Passiu Corrent
    quick_ratio: Optional[Decimal] = None    # (Actiu Corrent - Existències) / Passiu Corrent
    
    # Solvència
    solvency_ratio: Optional[Decimal] = None  # Actiu Total / Passiu Total
    debt_ratio: Optional[Decimal] = None      # Passiu Total / Patrimoni Net
    
    # Rendibilitat
    roa: Optional[Decimal] = None  # Return on Assets = Benefici Net / Actiu Total
    roe: Optional[Decimal] = None  # Return on Equity = Benefici Net / Patrimoni Net
    
    # Marges
    gross_margin: Optional[Decimal] = None   # (Vendes - Cost Vendes) / Vendes
    net_margin: Optional[Decimal] = None     # Benefici Net / Vendes


class AnalyticsService:
    """Service for calculating financial analytics and ratios."""
    
    def __init__(self, accounting_service: AccountingService):
        self._accounting_service = accounting_service
    
    def get_summary_data(self, fiscal_year_id: Optional[int] = None) -> Dict[str, Any]:
        """Get summary financial data for dashboard."""
        # TODO: Filter by fiscal year dates if provided
        
        # Get Profit & Loss data
        pl = self._accounting_service.get_profit_loss()
        
        # Get Balance Sheet data
        bs = self._accounting_service.get_balance_sheet()
        
        return {
            "total_income": pl["total_ingressos"],
            "total_expenses": pl["total_despeses"],
            "net_profit": pl["resultat"],
            "total_assets": bs["total_actiu"],
            "total_liabilities": bs["total_passiu"],
            "equity": bs["total_patrimoni_net"],
        }
    
    def calculate_ratios(self, fiscal_year_id: Optional[int] = None) -> FinancialRatios:
        """Calculate financial ratios for a fiscal period."""
        data = self.get_summary_data(fiscal_year_id)
        
        ratios = FinancialRatios()
        
        # Calculate ratios with safe division
        if data["total_liabilities"] > 0:
            ratios.solvency_ratio = data["total_assets"] / data["total_liabilities"]
        
        if data["equity"] > 0:
            ratios.debt_ratio = data["total_liabilities"] / data["equity"]
            if data["net_profit"]:
                ratios.roe = data["net_profit"] / data["equity"]
        
        if data["total_assets"] > 0 and data["net_profit"]:
            ratios.roa = data["net_profit"] / data["total_assets"]
        
        return ratios
    
    def get_chart_data(self, fiscal_year_id: Optional[int] = None) -> Dict[str, Any]:
        """Get data formatted for Chart.js charts."""
        # Calculate monthly income and expenses for current year
        current_year = date.today().year
        monthly_income = [Decimal(0)] * 12
        monthly_expenses = [Decimal(0)] * 12
        
        # Get all journal entries 
        # Ideally we should filter by year in the repo but list_all is what we have exposed easily
        # or we update accounting service to aggregate.
        # For MVP: List all entries and filter in Python
        entries = self._accounting_service.list_journal_entries()
        
        for entry in entries:
            # Filter by current year (or fiscal year if implemented)
            if entry.entry_date.year != current_year:
                continue
                
            month_idx = entry.entry_date.month - 1
            
            # Identify income (Group 7) and expense (Group 6) lines
            for line in entry.lines:
                if line.account_code.startswith('7'):
                    # Income accounts have credit balance (negative in standard notation? 
                    # AccountingService treats income as credit balance positive for display usually)
                    # Checking get_profit_loss implementation:
                    # Income accounts (Group 7) -> balance = credit - debit
                    # So credit adds to income
                    monthly_income[month_idx] += line.credit - line.debit
                elif line.account_code.startswith('6'):
                    # Expense accounts (Group 6) -> balance = debit - credit
                    # So debit adds to expense
                    monthly_expenses[month_idx] += line.debit - line.credit
                    
        return {
            "monthly_income": {
                "labels": ["Gen", "Feb", "Mar", "Abr", "Mai", "Jun", 
                          "Jul", "Ago", "Set", "Oct", "Nov", "Des"],
                "data": [float(val) for val in monthly_income],
            },
            "monthly_expenses": {
                "labels": ["Gen", "Feb", "Mar", "Abr", "Mai", "Jun",
                          "Jul", "Ago", "Set", "Oct", "Nov", "Des"],
                "data": [float(val) for val in monthly_expenses],
            },
            "account_breakdown": {
                "labels": [],
                "data": [],
            }
        }
