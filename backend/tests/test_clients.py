"""
Tests for client endpoints.
"""
import pytest
from fastapi import status


class TestClientCreation:
    """Test client creation."""
    
    def test_create_individual_client(self, client, agent_auth_headers):
        """Test creating an individual client."""
        response = client.post(
            "/api/v1/clients/",
            headers=agent_auth_headers,
            json={
                "client_type": "individual",
                "first_name": "Marie",
                "last_name": "Kouassi",
                "email": "marie.kouassi@example.com",
                "phone": "+225 07 11 22 33 44",
                "address": "Cocody, Angré",
                "city": "Abidjan",
                "country": "Côte d'Ivoire",
                "risk_profile": "low"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["first_name"] == "Marie"
        assert data["last_name"] == "Kouassi"
        assert data["client_type"] == "individual"
        assert data["status"] == "active"
    
    def test_create_corporate_client(self, client, agent_auth_headers):
        """Test creating a corporate client."""
        response = client.post(
            "/api/v1/clients/",
            headers=agent_auth_headers,
            json={
                "client_type": "corporate",
                "business_name": "Tech Corp CI",
                "email": "contact@techcorp.ci",
                "phone": "+225 27 20 11 22 33",
                "address": "Plateau",
                "city": "Abidjan",
                "country": "Côte d'Ivoire",
                "risk_profile": "medium"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["business_name"] == "Tech Corp CI"
        assert data["client_type"] == "corporate"
    
    def test_create_client_no_auth(self, client):
        """Test creating client without authentication."""
        response = client.post(
            "/api/v1/clients/",
            json={
                "client_type": "individual",
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "phone": "+225 07 11 22 33 44"
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestClientRetrieval:
    """Test client retrieval."""
    
    def test_get_all_clients(self, client, auth_headers, test_client_record):
        """Test getting all clients."""
        response = client.get(
            "/api/v1/clients/",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["email"] == "john.doe@example.com"
    
    def test_get_client_by_id(self, client, auth_headers, test_client_record):
        """Test getting a specific client."""
        response = client.get(
            f"/api/v1/clients/{test_client_record.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_client_record.id)
        assert data["email"] == "john.doe@example.com"
    
    def test_get_nonexistent_client(self, client, auth_headers):
        """Test getting a client that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/api/v1/clients/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_search_clients(self, client, auth_headers, test_client_record):
        """Test searching clients."""
        response = client.get(
            "/api/v1/clients/?search=John",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
        assert data[0]["first_name"] == "John"
    
    def test_filter_clients_by_status(self, client, auth_headers, test_client_record):
        """Test filtering clients by status."""
        response = client.get(
            "/api/v1/clients/?status=active",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(c["status"] == "active" for c in data)
    
    def test_count_clients(self, client, auth_headers, test_client_record):
        """Test counting clients."""
        response = client.get(
            "/api/v1/clients/count",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "count" in data
        assert data["count"] >= 1


class TestClientUpdate:
    """Test client update."""
    
    def test_update_client(self, client, agent_auth_headers, test_client_record):
        """Test updating a client."""
        response = client.put(
            f"/api/v1/clients/{test_client_record.id}",
            headers=agent_auth_headers,
            json={
                "first_name": "Jane",
                "phone": "+225 07 99 88 77 66"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["phone"] == "+225 07 99 88 77 66"
        # Last name should remain unchanged
        assert data["last_name"] == "Doe"
    
    def test_update_nonexistent_client(self, client, agent_auth_headers):
        """Test updating a client that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.put(
            f"/api/v1/clients/{fake_id}",
            headers=agent_auth_headers,
            json={"first_name": "Test"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestClientDeletion:
    """Test client deletion."""
    
    def test_delete_client(self, client, agent_auth_headers, test_client_record):
        """Test deleting a client."""
        response = client.delete(
            f"/api/v1/clients/{test_client_record.id}",
            headers=agent_auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify client is deleted
        get_response = client.get(
            f"/api/v1/clients/{test_client_record.id}",
            headers=agent_auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_nonexistent_client(self, client, agent_auth_headers):
        """Test deleting a client that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.delete(
            f"/api/v1/clients/{fake_id}",
            headers=agent_auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestClientMultiTenancy:
    """Test multi-tenant data isolation."""
    
    def test_cannot_access_other_company_clients(
        self,
        client,
        db_session,
        test_admin_user,
        auth_headers
    ):
        """Test that users cannot access clients from other companies."""
        from app.models.company import Company
        from app.models.client import Client
        
        # Create another company
        other_company = Company(
            name="Other Company",
            subdomain="other",
            email="other@test.com"
        )
        db_session.add(other_company)
        db_session.flush()
        
        # Create client for other company
        other_client = Client(
            company_id=other_company.id,
            client_type="individual",
            first_name="Other",
            last_name="Client",
            email="other@example.com",
            phone="+225 07 00 00 00 00"
        )
        db_session.add(other_client)
        db_session.commit()
        
        # Try to access other company's client
        response = client.get(
            f"/api/v1/clients/{other_client.id}",
            headers=auth_headers
        )
        
        # Should return 404 (not found), not the client data
        assert response.status_code == status.HTTP_404_NOT_FOUND
