import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.models.database import Base, get_db

# ── In-memory test database ──────────────────────────────────────
# StaticPool forces ALL code paths to share one connection,
# so tables created by create_all() are visible to the app under test.
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,          # ← the critical fix
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True, scope="function")
def reset_db():
    """Create all tables in the in-memory DB before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(reset_db):
    """
    TestClient with:
    - DB dependency overridden to in-memory SQLite
    - init_db() and ChromaDB warm_up patched out so the lifespan
      does NOT touch the real carebuddy.db during tests
    - memory backend reset each test so no cross-test state leaks
    """
    from app.main import app
    from app.core.memory import memory, InMemoryStore

    # Reset memory backend so each test gets a fresh InMemoryStore
    memory._backend = InMemoryStore()

    app.dependency_overrides[get_db] = override_get_db

    # Patch out only the DB and ChromaDB startup calls.
    with patch("app.main.init_db"), \
         patch("app.main.rag_retriever.warm_up"):
        with TestClient(app) as c:
            yield c

    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """Register a test user and return their credentials + token."""
    resp = client.post("/api/auth/register", json={
        "email": "test@carebuddy.com",
        "username": "testuser",
        "password": "securepass123",
        "full_name": "Test User",
    })
    assert resp.status_code == 201, f"Registration failed: {resp.json()}"
    return {
        "username": "testuser",
        "password": "securepass123",
        "token": resp.json()["access_token"],
    }


@pytest.fixture
def auth_headers(registered_user):
    """Authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {registered_user['token']}"}
