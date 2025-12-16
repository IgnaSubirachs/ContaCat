from typing import List, Dict, Optional
from datetime import date
from decimal import Decimal

from app.domain.accounts.entities import Account, AccountType
from app.domain.accounting.services import AccountingService

class ReportingService:
    """Service for generating official financial reports (Spanish PGC)."""
    
    def __init__(self, accounting_service: AccountingService):
        self._accounting_service = accounting_service

    def get_balance_sheet_report(self, end_date: Optional[date] = None) -> Dict:
        """
        Generate official Balance Sheet (Balanç de Situació) structured by PGC.
        
        Returns a dictionary with 'actiu' and 'patrimoni_net_i_passiu'.
        """
        accounts = self._accounting_service.list_accounts()
        
        # Initialize structure
        report = {
            "actiu": {
                "no_corrent": {"total": Decimal(0), "groups": {}},
                "corrent": {"total": Decimal(0), "groups": {}},
                "total": Decimal(0)
            },
            "patrimoni_net_i_passiu": {
                "patrimoni_net": {"total": Decimal(0), "groups": {}},
                "passiu_no_corrent": {"total": Decimal(0), "groups": {}},
                "passiu_corrent": {"total": Decimal(0), "groups": {}},
                "total": Decimal(0)
            },
            "end_date": end_date
        }
        
        # Helper to add amount to structure
        def add_to_category(main_cat, sub_cat, group_name, account, amount):
            if amount == 0: return
            
            target = report[main_cat][sub_cat]
            if group_name not in target["groups"]:
                target["groups"][group_name] = {"total": Decimal(0), "accounts": []}
            
            target["groups"][group_name]["accounts"].append({
                "code": account.code,
                "name": account.name,
                "balance": amount
            })
            target["groups"][group_name]["total"] += amount
            target["total"] += amount
            report[main_cat]["total"] += amount

        for account in accounts:
            balance = self._accounting_service.get_account_balance(account.code, end_date)
            if balance == 0:
                continue
                
            code = account.code
            
            # --- ACTIU ---
            if account.account_type == AccountType.ASSET:
                # Actiu No Corrent (Group 2)
                if code.startswith("2"):
                    if code.startswith("20"): group = "I. Immobilitzat Intangible"
                    elif code.startswith("21"): group = "II. Immobilitzat Material"
                    elif code.startswith("22"): group = "III. Inversions Immobiliàries"
                    elif code.startswith("25") or code.startswith("26"): group = "V. Inversions financeres a llarg termini"
                    else: group = "VI. Altres actius no corrents"
                    add_to_category("actiu", "no_corrent", group, account, balance)
                
                # Actiu Corrent (Group 3, 4, 5)
                elif code.startswith("3"):
                    group = "I. Existències"
                    add_to_category("actiu", "corrent", group, account, balance)
                elif code.startswith("43") or code.startswith("44"):
                    group = "II. Deutors comercials i altres comptes a cobrar"
                    add_to_category("actiu", "corrent", group, account, balance)
                elif code.startswith("57"):
                    group = "VII. Efectiu i altres actius líquids equivalents"
                    add_to_category("actiu", "corrent", group, account, balance)
                else: 
                    # Default fallback for other assets
                    group = "VI. Altres actius corrents"
                    add_to_category("actiu", "corrent", group, account, balance)

            # --- PATRIMONI NET I PASSIU ---
            elif account.account_type in [AccountType.LIABILITY, AccountType.EQUITY]:
                # Patrimoni Net (Group 1 - Ecquity parts like 10, 11, 12)
                # Group 1 can be both Equity and Liability, need careful check or simplify
                # Simplified PGC: 10, 11, 12, 129 -> Equity
                if code.startswith("10") or code.startswith("11") or code.startswith("12"):
                    group = "A-1) Fons Propis"
                    add_to_category("patrimoni_net_i_passiu", "patrimoni_net", group, account, balance)
                    
                # Passiu No Corrent (Long term debts)
                elif code.startswith("13") or code.startswith("14") or code.startswith("15") or code.startswith("16") or code.startswith("17"):
                    group = "II. Deutes a llarg termini"
                    add_to_category("patrimoni_net_i_passiu", "passiu_no_corrent", group, account, balance)
                
                # Passiu Corrent (Short term)
                elif code.startswith("40") or code.startswith("41"):
                    group = "IV. Creditors comercials i altres comptes a pagar"
                    add_to_category("patrimoni_net_i_passiu", "passiu_corrent", group, account, balance)
                elif code.startswith("52"):
                    group = "III. Deutes a curt termini"
                    add_to_category("patrimoni_net_i_passiu", "passiu_corrent", group, account, balance)
                else:
                    # Generic fallback based on type
                    if account.account_type == AccountType.EQUITY:
                         group = "A-1) Fons Propis"
                         add_to_category("patrimoni_net_i_passiu", "patrimoni_net", group, account, balance)
                    else:
                        group = "V. Altres passius corrents"
                        add_to_category("patrimoni_net_i_passiu", "passiu_corrent", group, account, balance)

        return report

    def get_profit_loss_report(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict:
        """
        Generate official Profit & Loss (Compte de Pèrdues i Guanys).
        
        Returns dictionary with 'operacions_continuades' structure.
        """
        # Get raw data from accounting service to calculate balances
        # We need balances of Group 6 and 7 within dates
        # AccountingService logic for get_profit_loss is reused or reimplemented?
        # Let's use `get_profit_loss` from service as base or fetch accounts and filter entries myself.
        # But `AccountingService` already does `get_profit_loss` which aggregates by account.
        # Let's calculate balances myself to control structure better or reuse `get_account_balance` but that takes all history for balance sheet.
        # For P&L we strictly need period movement.
        
        # Reuse existing service method to get raw balances for the period? 
        # Existing `get_profit_loss` returns {ingressos: {}, despeses: {}}. We can transform that.
        
        basic_pl = self._accounting_service.get_profit_loss(start_date, end_date)
        
        report = {
            "resultat_explotacio": Decimal(0),
            "resultat_financer": Decimal(0),
            "resultat_abans_impostos": Decimal(0),
            "resultat_exercici": Decimal(0),
            "groups": {},
            "start_date": start_date,
            "end_date": end_date
        }
        
        # Config Map
        # 1. Import Net de la Xifra de Negocis (70, 75)
        # 4. Aprovisionaments (60, 61)
        # 6. Despeses de personal (64)
        # 7. Altres despeses d'explotació (62)
        # ...
        
        def add_item(report_group, code, name, amount):
            if report_group not in report["groups"]:
                report["groups"][report_group] = {"total": Decimal(0), "account_lines": []}
            
            report["groups"][report_group]["account_lines"].append({
                "code": code,
                "name": name,
                "amount": amount
            })
            report["groups"][report_group]["total"] += amount

        # Process Income (Ingressos - have positive balance in basic_pl result)
        for code, data in basic_pl["ingressos"].items():
            amount = data["balance"]
            if code.startswith("70"):
                add_item("1. Import net de la xifra de negocis", code, data["name"], amount)
                report["resultat_explotacio"] += amount
            elif code.startswith("74"):
                add_item("3. Subvencions d'explotació", code, data["name"], amount)
                report["resultat_explotacio"] += amount
            elif code.startswith("76"):
                add_item("12. Ingressos financers", code, data["name"], amount)
                report["resultat_financer"] += amount
            else:
                add_item("5. Altres ingressos d'explotació", code, data["name"], amount)
                report["resultat_explotacio"] += amount

        # Process Expenses (Despeses - have positive balance in basic_pl result, need to substract)
        for code, data in basic_pl["despeses"].items():
            amount = -data["balance"] # Expenses reduce profit
            if code.startswith("60"):
                add_item("4. Aprovisionaments", code, data["name"], amount)
                report["resultat_explotacio"] += amount
            elif code.startswith("64"):
                add_item("6. Despeses de personal", code, data["name"], amount)
                report["resultat_explotacio"] += amount
            elif code.startswith("62"):
                add_item("7. Altres despeses d'explotació", code, data["name"], amount)
                report["resultat_explotacio"] += amount
            elif code.startswith("68"):
                add_item("8. Amortització de l'immobilitzat", code, data["name"], amount)
                report["resultat_explotacio"] += amount
            elif code.startswith("66"):
                add_item("13. Despeses financeres", code, data["name"], amount)
                report["resultat_financer"] += amount
            elif code.startswith("63"):
                 add_item("16. Impostos sobre beneficis", code, data["name"], amount)
                 # Taxes are calculated after BeforeTax result
            else:
                add_item("7. Altres despeses d'explotació", code, data["name"], amount)
                report["resultat_explotacio"] += amount

        report["resultat_abans_impostos"] = report["resultat_explotacio"] + report["resultat_financer"]
        
        # Add taxes (Group 63 usually)
        taxes = Decimal(0)
        if "16. Impostos sobre beneficis" in report["groups"]:
            taxes = report["groups"]["16. Impostos sobre beneficis"]["total"]
            
        report["resultat_exercici"] = report["resultat_abans_impostos"] + taxes # Taxes are already negative
        
        # Sort groups by index (hacky string sort works for "1.", "4.", "6.")
        return report
