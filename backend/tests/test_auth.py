"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status


class TestAuthRegistration:
    """Test user registration."""
    
    def test_register_new_company_and_admin(self, client):
        """Test registering a new company with admin user."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newadmin@newcompany.com",
                "password": "SecurePass123!",
                "first_name": "New",
                "last_name": "Admin",
                "phone": "+225 07 00 00 00 00",
                "company_name": "New Insurance Co",
                "company_subdomain": "newcompany"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newadmin@newcompany.com"
        assert data["role"] == "company_admin"
        assert "password" not in data
    
    def test_register_duplicate_email(self, client, test_admin_user):
        """Test registering with duplicate email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "admin@test.com",  # Already exists
                "password": "SecurePass123!",
                "first_name": "Duplicate",
                "last_name": "User",
                "company_name": "Another Co",
                "company_subdomain": "another"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_duplicate_subdomain(self, client, test_company):
        """Test registering with duplicate company subdomain fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newemail@example.com",
                "password": "SecurePass123!",
                "first_name": "New",
                "last_name": "User",
                "company_name": "Test Insurance Co",
                "company_subdomain": "test"  # Already exists
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "subdomain" in response.json()["detail"].lower()


class TestAuthLogin:
    """Test user login."""
    
    def test_login_success(self, client, test_admin_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@test.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "admin@test.com"
        assert data["user"]["role"] == "company_admin"
    
    def test_login_wrong_password(self, client, test_admin_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@test.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthMe:
    """Test get current user endpoint."""
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["role"] == "company_admin"
    
    def test_get_current_user_no_auth(self, client):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAuthRefreshToken:
    """Test token refresh."""
    
    def test_refresh_token_success(self, client, test_admin_user):
        """Test successful token refresh."""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@test.com",
                "password": "testpass123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
