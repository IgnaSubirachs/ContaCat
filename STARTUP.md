# 🚀 ERP System Startup Guide

## Quick Start (3 Steps)

### 1. Start Docker Desktop
- Open **Docker Desktop** application
- Wait for it to fully start (whale icon in system tray should be stable)

### 2. Start the Database
```powershell
cd c:\ERP
docker-compose up -d
```

This will start:
- MySQL database on port 3306
- Accessible at `localhost:3306`

### 3. Initialize Database Tables
```powershell
python init_db.py
```

This creates all tables for:
- Partners (clients/suppliers)
- Employees (HR)
- Accounts (chart of accounts)
- Journal Entries & Lines (accounting)
- Documents (attachments)

### 4. Start the Application
```powershell
uvicorn app.interface.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Access the Application

Once running, open your browser:

### Main Pages
- **Home**: http://localhost:8000/
- **Partners**: http://localhost:8000/partners/
- **Employees**: http://localhost:8000/employees/
- **Accounts**: http://localhost:8000/accounts/
- **Accounting**: http://localhost:8000/accounting/journal
- **Quotes (NEW)**: http://localhost:8000/quotes/
- **Sales Orders (NEW)**: http://localhost:8000/sales/orders/
- **Sales Invoices (NEW)**: http://localhost:8000/sales/invoices/

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing the New Modules

### Test Accounts Module
1. Go to http://localhost:8000/accounts/
2. Click "Nou Compte"
3. Create a test account:
   - Code: `4300001`
   - Name: `Client Test S.L.`
   - Type: `ASSET`
   - Group: `4`

### Test Accounting Module
1. Create at least 3 accounts (Client, Sales, VAT)
2. Go to http://localhost:8000/accounting/journal
3. Create a journal entry (invoice example):
   - Client account (debit): 121.00€
   - Sales account (credit): 100.00€
   - VAT account (credit): 21.00€

### Run Verification Script
```powershell
python verify_accounting.py
```

This will:
- Create sample accounts
- Create a journal entry
- Post the entry
- Calculate balances
- Generate trial balance

## 🐛 Troubleshooting

### Docker Desktop Not Running
**Error**: `unable to get image 'erp-app'`
**Solution**: Start Docker Desktop manually

### Port Already in Use
**Error**: `Address already in use`
**Solution**: 
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### Database Connection Failed
**Error**: `Can't connect to MySQL server`
**Solution**: 
1. Check Docker is running: `docker ps`
2. Check MySQL logs: `docker-compose logs db`
3. Restart containers: `docker-compose restart`

### Missing Python Dependencies
**Error**: `ModuleNotFoundError`
**Solution**:
```powershell
pip install -r requirements.txt
pip install fastapi uvicorn sqlalchemy pymysql python-dotenv cryptography
```

## 📁 Project Structure

```
c:\ERP\
├── app\
│   ├── domain\              # Business logic
│   │   ├── accounts\        # ✨ NEW: Chart of accounts
│   │   ├── accounting\      # ✨ UPDATED: Journal entries
│   │   ├── partners\
│   │   └── hr\
│   ├── infrastructure\      # Data persistence
│   │   └── persistence\
│   │       ├── accounts\    # ✨ NEW
│   │       └── accounting\  # ✨ UPDATED
│   └── interface\           # API & Web
│       ├── api\routers\
│       │   ├── accounts.py  # ✨ NEW
│       │   └── accounting.py
│       └── web\templates\
│           ├── accounts\    # ✨ NEW
│           └── accounting\  # ✨ NEW
├── docker-compose.yml
├── init_db.py              # ✨ NEW: DB initialization
├── verify_accounting.py    # ✨ NEW: Testing script
└── README.md
```

## 🎯 Next Steps

After testing the current modules:

1. **Choose Next Module** (from task.md):
   - Inventory & Warehouse
   - Sales & Orders
   - Procurement
   - CRM

2. **Set Up Alembic** (for database migrations):
   ```powershell
   pip install alembic
   alembic init alembic
   ```

3. **Add VeriFactu Compliance** (AEAT requirement)

4. **Implement Additional Features**:
   - Account editing/deletion
   - Journal entry editing (drafts only)
   - Financial reports (P&L, Balance Sheet)
   - Multi-currency support

## 📚 Documentation

- **Walkthrough**: See `walkthrough.md` for implementation details
- **Task List**: See `task.md` for roadmap
- **README**: See `README.md` for project overview
