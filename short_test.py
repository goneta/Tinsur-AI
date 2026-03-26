import requests
try:
    auth = requests.post("http://localhost:8000/api/v1/auth/login", json={"email":"admin@demoinsurance.com","password":"Admin123!"}).json()
    token = auth['access_token']
    print("Login OK")
    clients = requests.get("http://localhost:8000/api/v1/clients", headers={"Authorization":f"Bearer {token}"}).json()
    print(f"Clients: {len(clients)}")
    print(f"First: {clients[0]['first_name']}")
except Exception as e:
    print(f"Error: {e}")
    try:
        if 'clients' in locals() and not isinstance(clients, list):
             print(f"Response text: {clients}")
        elif 'auth' in locals() and 'access_token' in auth:
             # Retrying to get text from the request that failed
             res = requests.get("http://localhost:8000/api/v1/clients", headers={"Authorization":f"Bearer {auth['access_token']}"})
             print(f"Response Status: {res.status_code}")
             print(f"Response Text: {res.text}")
    except:
        pass
