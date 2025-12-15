#!/usr/bin/env python3
"""
Production Readiness Verification Script
Executes all verification tests and checks system configuration
"""
import sys
import os
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def run_test(test_file, test_name):
    """Run a verification test and return success status"""
    print(f"\n[INFO] Running {test_name}...")
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"[SUCCESS] {test_name} PASSED")
            return True
        else:
            print(f"[FAILURE] {test_name} FAILED")
            print("STDOUT:", result.stdout[-500:])
            print("STDERR:", result.stderr[-500:])
            return False
    except subprocess.TimeoutExpired:
        print(f"[FAILURE] {test_name} TIMEOUT")
        return False
    except Exception as e:
        print(f"[ERROR] {test_name} ERROR: {e}")
        return False

def check_file_exists(filepath, description):
    """Check if a critical file exists"""
    if os.path.exists(filepath):
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[MISSING] {description}: {filepath}")
        return False

def main():
    print_header("ContaCAT ERP - Production Readiness Check")
    
    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    all_passed = True
    
    # 1. File Structure Check
    print_header("1. Checking Critical Files")
    files_ok = True
    files_ok &= check_file_exists("app/interface/api/main.py", "Main Application")
    files_ok &= check_file_exists("app/infrastructure/db/base.py", "Database Config")
    files_ok &= check_file_exists("requirements.txt", "Dependencies")
    files_ok &= check_file_exists("scripts/init_db.py", "DB Initialization")
    
    if not files_ok:
        print("\n[WARNING] Some critical files are missing!")
        all_passed = False
    
    # 2. Verification Tests
    print_header("2. Running Verification Tests")
    
    tests = [
        ("tests/verify_sales.py", "Sales Module"),
        ("tests/verify_inventory.py", "Inventory Integration"),
        ("tests/verify_hr.py", "HR Payroll Calculations")
    ]
    
    tests_passed = 0
    for test_file, test_name in tests:
        if run_test(test_file, test_name):
            tests_passed += 1
        else:
            all_passed = False
    
    print(f"\n[INFO] Tests Passed: {tests_passed}/{len(tests)}")
    
    # 3. Environment Check
    print_header("3. Environment Configuration")
    
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"[OK] .env file exists")
        # Check for critical vars
        with open(env_file, 'r') as f:
            env_content = f.read()
            if "SECRET_KEY" in env_content:
                print("[OK] SECRET_KEY is configured")
            else:
                print("[WARNING] SECRET_KEY not found in .env")
                all_passed = False
    else:
        print(f"[WARNING] .env file not found - create it for production!")
        print("[INFO] Copy .env.example to .env and configure it")
        all_passed = False
    
    # 4. Dependencies Check
    print_header("4. Checking Dependencies")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True
        )
        if "No broken requirements found" in result.stdout or result.returncode == 0:
            print("[OK] All dependencies are satisfied")
        else:
            print("[WARNING] Dependency issues detected:")
            print(result.stdout)
            all_passed = False
    except Exception as e:
        print(f"[ERROR] Could not check dependencies: {e}")
    
    # Final Summary
    print_header("PRODUCTION READINESS SUMMARY")
    
    if all_passed:
        print("""
[SUCCESS] ALL CHECKS PASSED!

Your ERP system is ready for production deployment.

Next steps:
1. Review the DEPLOYMENT.md guide
2. Configure production database (PostgreSQL recommended)
3. Set up proper .env file with secure SECRET_KEY
4. Configure web server (Nginx + Gunicorn)
5. Set up SSL certificate
6. Configure automated backups
7. Change default admin password after first login

Access the deployment guide:
    .gemini/antigravity/brain/DEPLOYMENT.md
""")
        return 0
    else:
        print("""
[FAILURE] SOME CHECKS FAILED!

Your system is NOT ready for production deployment.

Please fix the issues listed above before deploying.

Common fixes:
- Install missing dependencies: pip install -r requirements.txt
- Create .env file with proper configuration
- Initialize database: python init_db.py
- Fix failing tests by reviewing error messages

Run this script again after fixes.
""")
        return 1

if __name__ == "__main__":
    sys.exit(main())
