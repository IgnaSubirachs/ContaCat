import asyncio
import httpx
import sys

# Configuration
BASE_URL = "http://localhost:8001"
USERNAME = "Ignasi"
PASSWORD = "Vinyet_2024"

ROUTES_TO_CHECK = [
    "/",
    "/partners",
    "/employees",
    "/accounting",
    "/inventory",
    "/quotes",
    "/sales/orders",
    "/assets",
    "/accounts",
    "/analytics",
    "/fiscal"
]

async def verify():
    print(f"[*] Verificant desplegament a {BASE_URL}...")
    
    async with httpx.AsyncClient(base_url=BASE_URL, follow_redirects=True) as client:
        # 1. Login
        print("[*] Intentant fer login...")
        try:
            login_data = {"username": USERNAME, "password": PASSWORD}
            response = await client.post("/auth/login", data=login_data)
            
            if response.status_code != 200:
                print(f"[ERROR] Error al login: {response.status_code}")
                print(response.text)
                return False
                
            token_data = response.json()
            access_token = token_data["access_token"]
            print("[OK] Login correcte! Token obtingut.")
            
            client.cookies.set("access_token", access_token)
            
        except Exception as e:
            print(f"[ERROR] Excepció durant el login: {e}")
            print("[!] Assegura't que el servidor està corrent al port 8001.")
            return False

        # 2. Verify Routes
        all_passed = True
        print("\n[*] Verificant mòduls...")
        
        for route in ROUTES_TO_CHECK:
            try:
                headers = {"Authorization": f"Bearer {access_token}"}
                resp = await client.get(route, headers=headers)
                
                if resp.status_code == 200:
                    print(f"  [OK] {route:<20} -> 200 OK")
                elif resp.status_code == 404:
                    print(f"  [WARN] {route:<20} -> 404 NOT FOUND")
                    all_passed = False
                elif resp.status_code == 500:
                    print(f"  [FAIL] {route:<20} -> 500 INTERNAL SERVER ERROR")
                    all_passed = False
                else:
                    print(f"  [?] {route:<20} -> {resp.status_code}")
            except Exception as e:
                print(f"  [FAIL] {route:<20} -> Error de connexió: {e}")
                all_passed = False
                
        print("\n" + "="*30)
        if all_passed:
            print("[SUCCESS] TOTS ELS SISTEMES OPERATIUS!")
        else:
            print("[WARN] S'han detectat problemes.")
            
if __name__ == "__main__":
    try:
        asyncio.run(verify())
    except ImportError:
        print("Error: Cal instal·lar 'httpx' (pip install httpx)")
