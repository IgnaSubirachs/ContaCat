#!/bin/bash
set -e

echo "Waiting for MySQL to be ready..."

# Wait for MySQL using Python
python3 -c "
import time
import pymysql
import sys

max_attempts = 30
attempt = 0

while attempt < max_attempts:
    try:
        conn = pymysql.connect(
            host='db',
            user='erpuser',
            password='erppass',
            database='erpdb'
        )
        conn.close()
        print('✓ MySQL is ready!')
        sys.exit(0)
    except Exception as e:
        attempt += 1
        print(f'Waiting for MySQL... (attempt {attempt}/{max_attempts})')
        time.sleep(2)

print('ERROR: MySQL did not become ready in time')
sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "Failed to connect to database"
    exit 1
fi

echo "Running database initialization..."
python3 scripts/init_db.py || echo "Database initialization completed or already done"

echo "Creating admin user..."
python3 -c "
try:
    from app.infrastructure.db.base import SessionLocal
    from app.domain.auth.services import AuthService
    from app.infrastructure.persistence.auth.repositories import SqlAlchemyUserRepository
    from app.domain.auth.entities import UserRole
    
    db = SessionLocal()
    try:
        repo = SqlAlchemyUserRepository(db)
        service = AuthService(repo)
        
        # Check if admin exists
        existing = service.get_user_by_username('admin')
        if not existing:
            user = service.create_user('admin', 'admin', UserRole.ADMIN)
            print(f'✓ Created admin user: {user.username}')
            db.commit()
        else:
            print('✓ Admin user already exists')
    except Exception as e:
        print(f'Note: {e}')
        db.rollback()
    finally:
        db.close()
except Exception as e:
    print(f'User creation skipped: {e}')
" || echo "Admin user creation completed or already done"

echo "✓ Initialization complete! Starting application..."
exec uvicorn app.interface.api.main:app --host 0.0.0.0 --port 8000
