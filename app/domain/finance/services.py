import uuid
from typing import List, Optional
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import math

from app.domain.finance.entities import Loan, LoanStatus, AmortizationEntry, AmortizationStatus
from app.domain.finance.repositories import LoanRepository
# Dependencies for Journal Entry creation would stay in interface or be injected here. 
# For strict DDD, we might emit events, but for this size, we'll expose methods to get data needed for posting.

class FinanceService:
    def __init__(self, repository: LoanRepository):
        self.repository = repository

    def _calculate_french_amortization(self, principal: float, annual_rate_percent: float, months: int, start_date: date) -> List[AmortizationEntry]:
        schedule = []
        monthly_rate = (annual_rate_percent / 100) / 12
        
        # Formula for monthly payment (PMT): P * r * (1+r)^n / ((1+r)^n - 1)
        if monthly_rate > 0:
            monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
        else:
            monthly_payment = principal / months

        remaining_balance = principal
        
        current_date = start_date
        
        for i in range(1, months + 1):
            # Move to next month (simplification: same day next month)
            current_date = start_date + relativedelta(months=i)
            
            interest_payment = remaining_balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            
            # Adjust last payment to fix rounding issues
            if i == months:
                principal_payment = remaining_balance
                monthly_payment = principal_payment + interest_payment
            
            remaining_balance -= principal_payment
            
            entry = AmortizationEntry(
                id=str(uuid.uuid4()),
                loan_id="", # Assigned later
                installment_number=i,
                due_date=current_date,
                principal_payment=round(principal_payment, 2),
                interest_payment=round(interest_payment, 2),
                total_payment=round(monthly_payment, 2),
                remaining_balance=round(max(0, remaining_balance), 2),
                status=AmortizationStatus.PENDING
            )
            schedule.append(entry)
            
        return schedule

    def create_loan(self, 
                    name: str, 
                    lender_partner_id: str, 
                    principal_amount: float, 
                    interest_rate: float, 
                    start_date: date, 
                    duration_months: int,
                    account_principal_long_term: str,
                    account_principal_short_term: str,
                    account_interest_expense: str,
                    account_bank: str,
                    description: str = None) -> Loan:
        
        schedule = self._calculate_french_amortization(principal_amount, interest_rate, duration_months, start_date)
        
        loan_id = str(uuid.uuid4())
        
        # Update loan_id in schedule
        for entry in schedule:
            entry.loan_id = loan_id

        loan = Loan(
            id=loan_id,
            name=name,
            lender_partner_id=lender_partner_id,
            principal_amount=principal_amount,
            interest_rate=interest_rate,
            start_date=start_date,
            duration_months=duration_months,
            description=description,
            status=LoanStatus.ACTIVE,
            amortization_schedule=schedule,
            account_principal_long_term=account_principal_long_term,
            account_principal_short_term=account_principal_short_term,
            account_interest_expense=account_interest_expense,
            account_bank=account_bank
        )
        
        return self.repository.save(loan)

    def get_loan(self, loan_id: str) -> Optional[Loan]:
        return self.repository.find_by_id(loan_id)

    def list_loans(self) -> List[Loan]:
        return self.repository.list_all()

    def mark_installment_as_posted(self, loan_id: str, installment_id: str, journal_entry_id: str) -> bool:
        loan = self.repository.find_by_id(loan_id)
        if not loan:
            return False
            
        for entry in loan.amortization_schedule:
            if entry.id == installment_id:
                entry.status = AmortizationStatus.POSTED
                entry.journal_entry_id = journal_entry_id
                self.repository.save(loan)
                return True
        
        return False
