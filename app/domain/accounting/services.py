from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal

from app.domain.accounts.entities import Account, AccountType
from app.domain.accounts.repositories import AccountRepository
from app.domain.accounting.entities import JournalEntry, JournalLine, JournalEntryStatus
from app.domain.accounting.repositories import JournalRepository


class AccountingService:
    """Service for accounting operations."""
    
    def __init__(
        self,
        account_repo: AccountRepository,
        journal_repo: JournalRepository
    ):
        self._account_repo = account_repo
        self._journal_repo = journal_repo
    
    # Account operations (Delegated to AccountRepository, but ideally should be in AccountService)
    def create_account(
        self,
        code: str,
        name: str,
        account_type: AccountType,
        group: int,
        parent_code: Optional[str] = None
    ) -> Account:
        """Create a new account."""
        # Check if code already exists
        existing = self._account_repo.find_by_code(code)
        if existing:
            raise ValueError(f"Ja existeix un compte amb el codi {code}")
        
        account = Account(
            code=code,
            name=name,
            account_type=account_type,
            group=group,
            parent_code=parent_code
        )
        account.validate()
        
        self._account_repo.add(account)
        return account
    
    def get_account(self, code: str) -> Optional[Account]:
        """Get account by code."""
        return self._account_repo.find_by_code(code)
    
    def list_accounts(self) -> List[Account]:
        """List all accounts."""
        return self._account_repo.list_all()
    
    def list_accounts_by_group(self, group: int) -> List[Account]:
        """List accounts by group."""
        return self._account_repo.list_by_group(group)
    
    # Journal entry operations
    def create_journal_entry(
        self,
        entry_date: date,
        description: str,
        lines: List[tuple[str, Decimal, Decimal, str]],  # (account_code, debit, credit, desc)
        attachment_path: Optional[str] = None
    ) -> JournalEntry:
        """Create a new journal entry."""
        # Get next entry number
        entry_number = self._journal_repo.get_next_entry_number()
        
        # Create journal lines
        journal_lines = []
        for account_code, debit, credit, line_desc in lines:
            # Verify account exists
            account = self._account_repo.find_by_code(account_code)
            if not account:
                raise ValueError(f"El compte {account_code} no existeix")
            
            line = JournalLine(
                account_code=account_code,
                debit=debit,
                credit=credit,
                description=line_desc
            )
            journal_lines.append(line)
        
        # Create entry
        entry = JournalEntry(
            entry_number=entry_number,
            entry_date=entry_date,
            description=description,
            lines=journal_lines,
            attachment_path=attachment_path
        )
        
        # Validate (including double-entry check)
        entry.validate()
        
        self._journal_repo.add(entry)
        return entry
    
    def post_journal_entry(self, entry_id: str) -> JournalEntry:
        """Post a journal entry (make it permanent)."""
        entry = self._journal_repo.find_by_id(entry_id)
        if not entry:
            raise ValueError(f"No s'ha trobat l'assentament amb ID {entry_id}")
        
        if entry.status == JournalEntryStatus.POSTED:
            raise ValueError("L'assentament ja està comptabilitzat")
        
        entry.post()
        self._journal_repo.update(entry)
        return entry
    
    def get_journal_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """Get journal entry by ID."""
        return self._journal_repo.find_by_id(entry_id)
    
    def list_journal_entries(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[JournalEntry]:
        """List journal entries, optionally filtered by date range."""
        if start_date and end_date:
            return self._journal_repo.list_by_date_range(start_date, end_date)
        return self._journal_repo.list_all()
    
    # Reporting
    def get_account_balance(
        self,
        account_code: str,
        end_date: Optional[date] = None
    ) -> Decimal:
        """Calculate account balance up to a date."""
        account = self._account_repo.find_by_code(account_code)
        if not account:
            raise ValueError(f"El compte {account_code} no existeix")
        
        # Get all journal entries (Optimization: should filter in DB)
        entries = self._journal_repo.list_all()
        
        total_debit = Decimal("0")
        total_credit = Decimal("0")
        
        for entry in entries:
            if entry.status != JournalEntryStatus.POSTED:
                continue
            
            if end_date and entry.entry_date > end_date:
                continue
            
            for line in entry.lines:
                if line.account_code == account_code:
                    total_debit += line.debit
                    total_credit += line.credit
        
        # Calculate balance based on account type
        if account.is_debit_account:
            return total_debit - total_credit
        else:
            return total_credit - total_debit
    
    def get_trial_balance(self, end_date: Optional[date] = None) -> Dict[str, Dict]:
        """Get trial balance (balanç de comprovació)."""
        accounts = self._account_repo.list_all()
        trial_balance = {}
        
        for account in accounts:
            balance = self.get_account_balance(account.code, end_date)
            if balance != 0:  # Only include accounts with balance
                trial_balance[account.code] = {
                    "name": account.name,
                    "type": account.account_type.value,
                    "balance": balance
                }
        
        return trial_balance
    
    def get_balance_sheet(self, end_date: Optional[date] = None) -> Dict:
        """Get balance sheet (balanç de situació).
        
        Returns a dictionary with:
        - actiu: Dict with non_corrent and corrent assets
        - passiu: Dict with non_corrent and corrent liabilities
        - patrimoni_net: Dict with equity accounts
        - total_actiu, total_passiu, total_patrimoni_net
        """
        accounts = self._account_repo.list_all()
        
        # Initialize structure
        balance_sheet = {
            "actiu": {
                "no_corrent": {},  # Group 2
                "corrent": {}      # Groups 3, 4, 5 (debit balance)
            },
            "passiu": {
                "no_corrent": {},  # Group 1 (liability part)
                "corrent": {}      # Group 4, 5 (credit balance)
            },
            "patrimoni_net": {}    # Group 1 (equity part)
        }
        
        for account in accounts:
            balance = self.get_account_balance(account.code, end_date)
            if balance == 0:
                continue
            
            account_data = {
                "code": account.code,
                "name": account.name,
                "balance": balance
            }
            
            # Classify by account type and group
            if account.account_type == AccountType.ASSET:
                if account.group == 2:
                    balance_sheet["actiu"]["no_corrent"][account.code] = account_data
                else:  # Groups 3, 4, 5
                    balance_sheet["actiu"]["corrent"][account.code] = account_data
            
            elif account.account_type == AccountType.LIABILITY:
                if account.group == 1:
                    balance_sheet["passiu"]["no_corrent"][account.code] = account_data
                else:
                    balance_sheet["passiu"]["corrent"][account.code] = account_data
            
            elif account.account_type == AccountType.EQUITY:
                balance_sheet["patrimoni_net"][account.code] = account_data
        
        # Calculate totals
        balance_sheet["total_actiu_no_corrent"] = sum(
            acc["balance"] for acc in balance_sheet["actiu"]["no_corrent"].values()
        )
        balance_sheet["total_actiu_corrent"] = sum(
            acc["balance"] for acc in balance_sheet["actiu"]["corrent"].values()
        )
        balance_sheet["total_actiu"] = (
            balance_sheet["total_actiu_no_corrent"] + 
            balance_sheet["total_actiu_corrent"]
        )
        
        balance_sheet["total_passiu_no_corrent"] = sum(
            acc["balance"] for acc in balance_sheet["passiu"]["no_corrent"].values()
        )
        balance_sheet["total_passiu_corrent"] = sum(
            acc["balance"] for acc in balance_sheet["passiu"]["corrent"].values()
        )
        balance_sheet["total_passiu"] = (
            balance_sheet["total_passiu_no_corrent"] + 
            balance_sheet["total_passiu_corrent"]
        )
        
        balance_sheet["total_patrimoni_net"] = sum(
            acc["balance"] for acc in balance_sheet["patrimoni_net"].values()
        )
        
        balance_sheet["end_date"] = end_date
        
        return balance_sheet
    
    def get_profit_loss(
        self, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """Get profit and loss statement (compte de pèrdues i guanys).
        
        Returns a dictionary with:
        - ingressos: Dict with income accounts (Group 7)
        - despeses: Dict with expense accounts (Group 6)
        - resultat: Net profit/loss
        """
        # Get all journal entries in the period
        if start_date and end_date:
            entries = self._journal_repo.list_by_date_range(start_date, end_date)
        else:
            entries = self._journal_repo.list_all()
        
        accounts = self._account_repo.list_all()
        account_map = {acc.code: acc for acc in accounts}
        
        # Initialize structure
        profit_loss = {
            "ingressos": {},
            "despeses": {},
            "start_date": start_date,
            "end_date": end_date
        }
        
        # Accumulate balances for income and expense accounts
        account_balances = {}
        
        for entry in entries:
            if entry.status != JournalEntryStatus.POSTED:
                continue
            
            # Filter by date if specified
            if start_date and entry.entry_date < start_date:
                continue
            if end_date and entry.entry_date > end_date:
                continue
            
            for line in entry.lines:
                if line.account_code not in account_balances:
                    account_balances[line.account_code] = {
                        "debit": Decimal("0"),
                        "credit": Decimal("0")
                    }
                
                account_balances[line.account_code]["debit"] += line.debit
                account_balances[line.account_code]["credit"] += line.credit
        
        # Classify accounts
        for account_code, balances in account_balances.items():
            if account_code not in account_map:
                continue
            
            account = account_map[account_code]
            
            # Calculate balance based on account type
            if account.account_type == AccountType.INCOME:
                # Income accounts have credit balance
                balance = balances["credit"] - balances["debit"]
                if balance != 0:
                    profit_loss["ingressos"][account_code] = {
                        "code": account.code,
                        "name": account.name,
                        "balance": balance
                    }
            
            elif account.account_type == AccountType.EXPENSE:
                # Expense accounts have debit balance
                balance = balances["debit"] - balances["credit"]
                if balance != 0:
                    profit_loss["despeses"][account_code] = {
                        "code": account.code,
                        "name": account.name,
                        "balance": balance
                    }
        
        # Calculate totals
        profit_loss["total_ingressos"] = sum(
            acc["balance"] for acc in profit_loss["ingressos"].values()
        )
        profit_loss["total_despeses"] = sum(
            acc["balance"] for acc in profit_loss["despeses"].values()
        )
        profit_loss["resultat"] = (
            profit_loss["total_ingressos"] - profit_loss["total_despeses"]
        )
        
        return profit_loss
