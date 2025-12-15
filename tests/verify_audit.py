import sys
import os
sys.path.append(os.getcwd())

from app.infrastructure.db.base import SessionLocal
from app.infrastructure.persistence.audit.models import AuditLogModel
from sqlalchemy import select

def verify_audit_logs():
    print("Verifying Audit Logs...")
    session = SessionLocal()
    try:
        stmt = select(AuditLogModel).order_by(AuditLogModel.timestamp.desc()).limit(5)
        result = session.execute(stmt)
        logs = result.scalars().all()
        
        if not logs:
            print("[WARN] No audit logs found. Run verify_sales.py first.")
            return

        print(f"Found {len(logs)} recent logs:")
        for log in logs:
            print(f" - [{log.timestamp}] {log.action} on {log.entity_type} {log.entity_id} by {log.user}")
            print(f"   Changes: {log.changes}")
        
        print("[OK] Audit logs verification completed.")
    finally:
        session.close()

if __name__ == "__main__":
    verify_audit_logs()
