import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import get_db
from backend.models import Base, User, Organization

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="function")
def db_session() -> Session:
    """Yield a new database session for a test, and rollback any changes."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """
    A fixture to get a TestClient that uses the same DB session as the test.
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """Create a test user and org, and yield the user."""
    org = Organization(name="Test Org")
    db_session.add(org)
    db_session.commit()

    user = User(email="test@example.com", name="Test User", org_id=org.id, role="owner")
    db_session.add(user)
    db_session.commit()
    return user
