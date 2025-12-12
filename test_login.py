import requests

# Test login
url = "http://localhost:8000/auth/login"
data = {
    "username": "admin",
    "password": "admin123"
}

print("Testing login...")
print(f"URL: {url}")
print(f"Username: {data['username']}")
print(f"Password: {data['password']}")
print()

try:
    response = requests.post(url, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n[OK] Login successful!")
        token = response.json().get('access_token')
        print(f"Token: {token[:50]}...")
    else:
        print("\n[ERROR] Login failed!")
        
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
