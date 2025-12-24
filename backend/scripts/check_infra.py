
import socket
import sys
import time

def check_port(host, port, timeout=2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False

def main():
    infra = [
        {"name": "PostgreSQL", "host": "localhost", "port": 5432},
        {"name": "MongoDB", "host": "localhost", "port": 27017},
        {"name": "Redis", "host": "localhost", "port": 6379},
    ]

    print("--- Infrastructure Pre-flight Check ---")
    all_ready = True
    for item in infra:
        ready = check_port(item["host"], item["port"])
        status = "READY" if ready else "OFFLINE"
        icon = "✅" if ready else "❌"
        print(f"{icon} {item['name']} ({item['port']}): {status}")
        if not ready:
            all_ready = False

    if not all_ready:
        print("\nERROR: Infrastructure dependencies are not fully ready.")
        print("Please ensure Docker containers or local services are running.")
        sys.exit(1)
    
    print("\nAll infrastructure dependencies are READY.")
    sys.exit(0)

if __name__ == "__main__":
    main()
