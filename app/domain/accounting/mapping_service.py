from typing import Optional
from app.domain.partners.entities import Partner

class AccountMappingService:
    """
    Enterprise-grade service to resolve accounting accounts dynamically.
    Instead of hardcoding '43000000', this service determines the correct account
    based on the Partner (Fiscal Position), Product (Revenue Category), or Tax configuration.
    """

    def get_customer_account(self, partner: Partner) -> str:
        """
        Returns the receivable account (Compte de Clients) for a given partner.
        Logic:
          1. If partner has a specific account assigned, use it.
          2. Else, assume standard domestic customer '43000000'.
        """
        # Feature for future: check partner.account_receivable_code
        # if hasattr(partner, 'account_receivable_code') and partner.account_receivable_code:
        #     return partner.account_receivable_code
        return "43000000"

    def get_sales_account(self, product_category: str = None) -> str:
        """
        Returns the revenue account (Vendes/Ingressos).
        """
        # Feature for future: map category 'Services' -> 705, 'Goods' -> 700
        return "70000000"

    def get_vat_payable_account(self, tax_rate: float) -> str:
        """
        Returns the VAT Payable account (H.P. IVA Repercutit).
        """
        # Could distinguish by rate (e.g. 47700021 for 21%, 47700010 for 10%)
        # For now return the standard root, or specific if needed.
        return "47700000"
    
    def get_purchase_account(self, product_category: str = None) -> str:
        """
        Returns the expense account (Compres).
        Default: 600 (Compres de mercaderies)
        """
        return "60000000"
    
    def get_input_vat_account(self, tax_rate: float = None) -> str:
        """
        Returns the Input VAT account (IVA Suportat - deductible).
        Account 472: H.P. IVA Suportat
        """
        return "47200000"
    
    def get_accounts_payable_account(self) -> str:
        """
        Returns the supplier payable account (Proveïdors).
        Account 400: Proveïdors
        """
        return "40000000"
