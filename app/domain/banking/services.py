import uuid
from typing import List, Optional
from datetime import datetime
import csv
import io

from app.domain.banking.entities import BankStatement, BankStatementLine, StatementStatus
from app.domain.banking.repositories import BankStatementRepository

class BankingService:
    def __init__(self, repository: BankStatementRepository):
        self.repository = repository

    def upload_statement(self, account_id: str, filename: str, file_content: bytes) -> BankStatement:
        # Simple CSV parser assuming columns: Date, Concept, Amount, Balance
        # Format assumed: YYYY-MM-DD, Concept, Amount, Balance
        
        statement_id = str(uuid.uuid4())
        lines = []
        
        # Decode and parse CSV
        content_str = file_content.decode('utf-8')
        csv_reader = csv.reader(io.StringIO(content_str), delimiter=',')
        
        # Skip header if present (simple check)
        rows = list(csv_reader)
        if rows and "Date" in rows[0][0]: 
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
        
        return self.repository.save(statement)

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
