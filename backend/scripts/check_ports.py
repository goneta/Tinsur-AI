
import socket

ports = {
    "Frontend": 3000,
    "Backend": 8000,
    "Orchestrator": 8025,
    "Claims Agent": 8019,
    "Quote Agent": 8020,
    "Policy Agent": 8021
}

print("Checking ports...")
for name, port in ports.items():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    if result == 0:
        print(f"✅ {name} ({port}) is OPEN")
    else:
        print(f"❌ {name} ({port}) is CLOSED")
    sock.close()
