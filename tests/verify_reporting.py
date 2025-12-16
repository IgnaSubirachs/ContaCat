import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8002"

def verify_reports():
    print("--- Verifying Financial Reports (Live Server) ---")
    
    # Wait for server
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/", timeout=1)
            break
        except:
            print(f"Waiting for server... {i}")
            time.sleep(1)
            
    try:
        # 1. Balance Sheet HTML
        print("\n1. Testing Balance Sheet (HTML)...")
        response = requests.get(f"{BASE_URL}/accounting/reports/balance-sheet")
        if response.status_code == 200:
            print("[OK] HTML OK")
        else:
            print(f"[FAIL] Failed: {response.status_code}")
            
        # 2. Profit & Loss HTML
        print("\n2. Testing Profit & Loss (HTML)...")
        response = requests.get(f"{BASE_URL}/accounting/reports/profit-loss")
        if response.status_code == 200:
            print("[OK] HTML OK")
        else:
            print(f"[FAIL] Failed: {response.status_code}")
            
        # 3. Balance Sheet PDF
        print("\n3. Testing Balance Sheet (PDF Export)...")
        response = requests.get(f"{BASE_URL}/accounting/reports/balance-sheet/export?format=pdf")
        if response.status_code == 200 and response.headers["content-type"] == "application/pdf":
            print(f"[OK] PDF OK ({len(response.content)} bytes)")
        else:
            print(f"[FAIL] Failed: Status={response.status_code}, Type={response.headers.get('content-type')}")
            if response.status_code != 200:
                print(response.content[:200])

        # 4. Profit & Loss PDF
        print("\n4. Testing Profit & Loss (PDF Export)...")
        response = requests.get(f"{BASE_URL}/accounting/reports/profit-loss/export?format=pdf")
        if response.status_code == 200 and response.headers["content-type"] == "application/pdf":
             print(f"[OK] PDF OK ({len(response.content)} bytes)")
        else:
            print(f"[FAIL] Failed: Status={response.status_code}, Type={response.headers.get('content-type')}")
            
    except requests.RequestException as e:
        print(f"[FAIL] Connection Error: {e}")

if __name__ == "__main__":
    verify_reports()
