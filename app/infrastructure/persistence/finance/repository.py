from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.domain.finance.entities import Loan, AmortizationEntry
from app.domain.finance.repositories import LoanRepository
from app.infrastructure.persistence.finance.models import LoanModel, AmortizationEntryModel

class SqlAlchemyLoanRepository(LoanRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_entity(self, model: LoanModel) -> Loan:
        schedule = []
        if model.amortization_schedule:
            for item in model.amortization_schedule:
                schedule.append(AmortizationEntry(
                    id=item.id,
                    loan_id=item.loan_id,
                    installment_number=item.installment_number,
                    due_date=item.due_date,
                    principal_payment=item.principal_payment,
                    interest_payment=item.interest_payment,
                    total_payment=item.total_payment,
                    remaining_balance=item.remaining_balance,
                    status=item.status,
                    journal_entry_id=item.journal_entry_id
                ))
        
        loan = Loan(
            id=model.id,
            name=model.name,
            lender_partner_id=model.lender_partner_id,
            principal_amount=model.principal_amount,
            interest_rate=model.interest_rate,
            start_date=model.start_date,
            duration_months=model.duration_months,
            description=model.description,
            status=model.status,
            account_principal_long_term=model.account_principal_long_term,
            account_principal_short_term=model.account_principal_short_term,
            account_interest_expense=model.account_interest_expense,
            account_bank=model.account_bank,
            created_at=model.created_at,
            updated_at=model.updated_at,
            amortization_schedule=schedule
        )
        return loan

    def save(self, loan: Loan) -> Loan:
        model = self.session.query(LoanModel).filter_by(id=loan.id).first()
        
        if not model:
            model = LoanModel(id=loan.id)
            self.session.add(model)
            
        model.name = loan.name
        model.lender_partner_id = loan.lender_partner_id
        model.principal_amount = loan.principal_amount
        model.interest_rate = loan.interest_rate
        model.start_date = loan.start_date
        model.duration_months = loan.duration_months
        model.description = loan.description
        model.status = loan.status
        model.account_principal_long_term = loan.account_principal_long_term
        model.account_principal_short_term = loan.account_principal_short_term
        model.account_interest_expense = loan.account_interest_expense
        model.account_bank = loan.account_bank
        model.updated_at = loan.updated_at
        
        # Handle schedule updates
        # For simplicity, we assume schedule is generated once on creation. 
        # But for updates (status changes), we need to update items.
        
        current_entry_ids = {entry.id for entry in loan.amortization_schedule if entry.id}
        
        # Remove deleted
        for existing_entry in model.amortization_schedule:
             if existing_entry.id not in current_entry_ids:
                 self.session.delete(existing_entry)
        
        # Add/Update
        for entry in loan.amortization_schedule:
            entry_model = next((e for e in model.amortization_schedule if e.id == entry.id), None)
            if not entry_model:
                entry_model = AmortizationEntryModel(
                    id=entry.id,
                    loan_id=model.id,
                    installment_number=entry.installment_number,
                    due_date=entry.due_date,
                    principal_payment=entry.principal_payment,
                    interest_payment=entry.interest_payment,
                    total_payment=entry.total_payment,
                    remaining_balance=entry.remaining_balance,
                    status=entry.status,
                    journal_entry_id=entry.journal_entry_id
                )
                self.session.add(entry_model)
            else:
                entry_model.status = entry.status
                entry_model.journal_entry_id = entry.journal_entry_id
        
        self.session.commit()
        self.session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, loan_id: str) -> Optional[Loan]:
        model = self.session.query(LoanModel).options(joinedload(LoanModel.amortization_schedule)).filter_by(id=loan_id).first()
        if model:
            return self._to_entity(model)
        return None

    def list_all(self) -> List[Loan]:
        models = self.session.query(LoanModel).all() # Lazy load schedule for list
        return [self._to_entity(m) for m in models]

    def delete(self, loan_id: str) -> bool:
        model = self.session.query(LoanModel).filter_by(id=loan_id).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False
