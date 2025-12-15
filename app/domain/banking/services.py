import uuid
from typing import List, Optional
from datetime import datetime
import csv
import io

from app.domain.banking.entities import BankStatement, BankStatementLine, StatementStatus
from app.domain.banking.repositories import BankStatementRepository

from decimal import Decimal
from app.domain.sales.entities import InvoiceStatus, PaymentStatus

class BankingService:
    def __init__(self, repository: BankStatementRepository, invoice_repository=None):
        self.repository = repository
        self.invoice_repository = invoice_repository # Optional dependency for reconciliation suggestions

    def get_reconciliation_suggestions(self, line_id: str) -> List[dict]:
        """
        Suggests invoices that match the given bank statement line amount.
        Returns a list of matching sales invoices (as dicts or entities).
        """
        if not self.invoice_repository:
            return []
            
        # Find the line (inefficient but works for now, or add find_line method to repo)
        # We need the amount of the line. 
        # Since repo.find_by_id returns a Statement, not a Line, we iterate.
        # This is a bit slow for large datasets, but ok for MVP.
        # Ideally repo should have find_line_by_id(line_id).
        
        target_line = None
        statements = self.repository.list_all()
        for stmt in statements:
            for line in stmt.lines:
                if line.id == line_id:
                    target_line = line
                    break
            if target_line: break
            
        if not target_line:
            return []
            
        # Logic: Payment received (positive amount) -> Sales Invoice (Total matches amount)
        # Logic: Payment made (negative amount) -> Purchase Bill (Total matches abs(amount))
        
        candidates = []
        
        if target_line.amount > 0:
            # Sales Invoices
            # We fetch POSTED invoices.
            # In a real app we'd filter by payment_status != PAID in the DB query
            all_invoices = self.invoice_repository.list_by_status(InvoiceStatus.POSTED)
            amount_to_match = Decimal(str(target_line.amount))
            
            for inv in all_invoices:
                if inv.payment_status != PaymentStatus.PAID:
                    # Tolerance could be added here
                    if inv.total == amount_to_match:
                        candidates.append({
                            "type": "SalesInvoice",
                            "id": inv.id,
                            "number": inv.invoice_number,
                            "partner": inv.partner_id, # Should fetch name but ID for now
                            "date": inv.invoice_date,
                            "amount": inv.total,
                            "match_score": 100 # Perfect match on amount
                        })
        
        return candidates

    def upload_statement(self, account_id: str, filename: str, file_content: bytes) -> List[BankStatement]:
        """
        Uploads a bank statement file. Supports CSV and CSB43 (Norma 43).
        Returns a list of created statements (CSB43 can contain multiple).
        """
        created_statements = []
        
        # Detect format based on extension or content
        is_csb43 = filename.lower().endswith(('.n43', '.csb', '.txt'))
        
        if is_csb43:
            try:
                from app.domain.banking.csb43 import CSB43Parser
                parser = CSB43Parser()
                statements = parser.parse(filename, file_content)
                
                for stmt in statements:
                    stmt.id = str(uuid.uuid4())
                    stmt.account_id = account_id # Link to the account uploaded for (or use the one in file?)
                    # If the file has account info, we might want to validate it matches account_id
                    
                    for line in stmt.lines:
                        line.id = str(uuid.uuid4())
                        line.statement_id = stmt.id
                        
                    self.repository.save(stmt)
                    created_statements.append(stmt)
                    
                return created_statements
            except Exception as e:
                print(f"[ERROR] Failed to parse CSB43: {e}")
                # Fallback to CSV or raise? Let's proceed to try CSV if it fails strictly? 
                # Actually, better to fail if it looks like CSB43.
                raise e

        # Default to CSV Parser
        statement_id = str(uuid.uuid4())
        lines = []
        
        # Decode and parse CSV
        content_str = file_content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content_str), delimiter=',')
        
        # Skip header if present (simple check)
        rows = list(csv_reader)
        if rows and len(rows) > 0 and "Date" in str(rows[0][0]): 
             rows = rows[1:]

        for row in rows:
            if len(row) < 3: continue
            
            try:
                date_str = row[0].strip()
                concept = row[1].strip()
                amount = float(row[2].strip())
                balance = float(row[3].strip()) if len(row) > 3 else 0.0
                
                line = BankStatementLine(
                    id=str(uuid.uuid4()),
                    statement_id=statement_id,
                    date=datetime.strptime(date_str, "%Y-%m-%d").date(),
                    amount=amount,
                    concept=concept,
                    balance=balance,
                    status="PENDING"
                )
                lines.append(line)
            except Exception as e:
                print(f"Skipping row {row}: {e}")
                continue

        statement = BankStatement(
            id=statement_id,
            account_id=account_id,
            filename=filename,
            upload_date=datetime.now(),
            status=StatementStatus.PENDING,
            lines=lines
        )
        
        self.repository.save(statement)
        created_statements.append(statement)
        
        return created_statements

    def get_statement(self, statement_id: str) -> Optional[BankStatement]:
        return self.repository.find_by_id(statement_id)

    def list_statements(self) -> List[BankStatement]:
        return self.repository.list_all()

    def reconcile_line(self, statement_id: str, line_id: str, journal_entry_id: str) -> bool:
        statement = self.repository.find_by_id(statement_id)
        if not statement:
            return False
            
        line_found = False
        all_reconciled = True
        
        for line in statement.lines:
            if line.id == line_id:
                line.reconciled_entry_id = journal_entry_id
                line.status = "MATCHED"
                line_found = True
            
            if line.status != "MATCHED":
                all_reconciled = False
        
        if line_found:
            statement.status = StatementStatus.RECONCILED if all_reconciled else StatementStatus.PARTIAL
            self.repository.save(statement)
            return True
            
        return False
