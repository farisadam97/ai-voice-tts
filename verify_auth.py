import httpx

BASE_URL = "http://localhost:8000/api/v1"

def test_signup():
    print("Testing Signup...")
    email = "testuser@example.com"
    password = "securepassword123"
    
    response = httpx.post(f"{BASE_URL}/auth/signup", json={
        "email": email,
        "password": password,
        "full_name": "Test User"
    })
    
    if response.status_code == 200:
        print("Signup Success:", response.json())
        return email, password
    elif response.status_code == 400 and "already exists" in response.text:
         print("User already exists, proceeding to login.")
         return email, password
    else:
        print("Signup Failed:", response.text)
        return None, None

def test_login(email, password):
    print("\nTesting Login...")
    response = httpx.post(f"{BASE_URL}/auth/login", data={
        "username": email,
        "password": password
    })
    
    if response.status_code == 200:
        token = response.json()
        print("Login Success! Token:", token["access_token"][:20] + "...")
        return token["access_token"]
    else:
        print("Login Failed:", response.text)
        return None

def main():
    email, password = test_signup()
    if email:
        test_login(email, password)

if __name__ == "__main__":
    main()
