import requests

def test_cors():
    url = "http://localhost:8000/api/v1/auth/login"
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"
    }
    try:
        print(f"Testing CORS OPTIONS at {url}...")
        response = requests.options(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Headers:")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")
            
        if "Access-Control-Allow-Origin" in response.headers:
            print(f"CORS Origin Allowed: {response.headers['Access-Control-Allow-Origin']}")
        else:
            print("CORS Origin Header MISSING!")

    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_cors()
