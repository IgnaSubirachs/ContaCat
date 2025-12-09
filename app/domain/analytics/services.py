from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import date


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
    
    def __init__(self, db_session):
        self._session = db_session
    
    def get_summary_data(self, fiscal_year_id: Optional[int] = None) -> Dict[str, Any]:
        """Get summary financial data for dashboard."""
        # This would query real data from the accounting module
        # For now, return sample structure
        return {
            "total_income": Decimal("0"),
            "total_expenses": Decimal("0"),
            "net_profit": Decimal("0"),
            "total_assets": Decimal("0"),
            "total_liabilities": Decimal("0"),
            "equity": Decimal("0"),
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
        return {
            "monthly_income": {
                "labels": ["Gen", "Feb", "Mar", "Abr", "Mai", "Jun", 
                          "Jul", "Ago", "Set", "Oct", "Nov", "Des"],
                "data": [0] * 12,
            },
            "monthly_expenses": {
                "labels": ["Gen", "Feb", "Mar", "Abr", "Mai", "Jun",
                          "Jul", "Ago", "Set", "Oct", "Nov", "Des"],
                "data": [0] * 12,
            },
            "account_breakdown": {
                "labels": [],
                "data": [],
            }
        }
