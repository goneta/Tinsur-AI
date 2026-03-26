"""
Test configuration and fixtures.
"""
import pytest
import warnings
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

warnings.filterwarnings(
    "ignore",
    message="Accessing argon2.__version__ is deprecated*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r"passlib\\.handlers\\.argon2",
)

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models.company import Company
from app.models.user import User
from app.models.client import Client

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_company(db_session):
    """Create a test company."""
    company = Company(
        name="Test Insurance Co",
        subdomain="test",
        email="test@insurance.com",
        phone="+225 27 20 00 00 00"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def test_admin_user(db_session, test_company):
    """Create a test admin user."""
    user = User(
        company_id=test_company.id,
        email="admin@test.com",
        password_hash=get_password_hash("testpass123"),
        first_name="Admin",
        last_name="User",
        role="company_admin",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_agent_user(db_session, test_company):
    """Create a test agent user."""
    user = User(
        company_id=test_company.id,
        email="agent@test.com",
        password_hash=get_password_hash("testpass123"),
        first_name="Agent",
        last_name="User",
        role="agent",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_client_record(db_session, test_company):
    """Create a test client record."""
    client = Client(
        company_id=test_company.id,
        client_type="individual",
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="+225 07 11 22 33 44",
        city="Abidjan",
        country="Côte d'Ivoire"
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client


@pytest.fixture
def auth_headers(client, test_admin_user):
    """Get authentication headers for admin user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@test.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def agent_auth_headers(client, test_agent_user):
    """Get authentication headers for agent user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "agent@test.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
