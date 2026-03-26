#!/usr/bin/env python
"""Generate test JWT tokens for API testing"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Any

# Settings from config
SECRET_KEY = "dev_secret_key_123456789"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(
    subject: str,
    user_id: str,
    role: str = "user",
    expires_delta: timedelta = None
) -> str:
    """Create a JWT access token"""
    
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "sub": subject,
        "user_id": user_id,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def main():
    print("=" * 60)
    print("TINSUR-AI TEST TOKEN GENERATOR")
    print("=" * 60)
    print()
    
    # Generate admin token
    admin_token = create_access_token(
        subject="admin@example.com",
        user_id="admin_001",
        role="admin"
    )
    
    print("[ADMIN TOKEN]")
    print(f"Token: {admin_token}")
    print()
    print("Use in requests:")
    print('  Authorization: Bearer ' + admin_token)
    print()
    
    # Generate client token
    client_token = create_access_token(
        subject="client@example.com",
        user_id="client_001",
        role="user"
    )
    
    print("[CLIENT TOKEN]")
    print(f"Token: {client_token}")
    print()
    print("Use in requests:")
    print('  Authorization: Bearer ' + client_token)
    print()
    
    print("=" * 60)
    print("TOKENS ARE VALID FOR 60 MINUTES")
    print("=" * 60)
    
    return admin_token, client_token

if __name__ == "__main__":
    admin, client = main()
    
    # Export for test script
    import json
    tokens = {
        "admin_token": admin,
        "client_token": client
    }
    
    with open("test_tokens.json", "w") as f:
        json.dump(tokens, f)
    
    print("\nTokens saved to test_tokens.json")
