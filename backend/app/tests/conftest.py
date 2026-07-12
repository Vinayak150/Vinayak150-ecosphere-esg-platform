import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.database import get_db
from app.main import app

settings = get_settings()

ADMIN_EMAIL = "admin@ecosphere.local"
ADMIN_PASSWORD = "ChangeMe123!"


def _database_available() -> bool:
    engine = create_engine(str(settings.database_url), pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except OperationalError:
        return False


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_engine():
    if not _database_available():
        pytest.skip("PostgreSQL database is not available")
    return create_engine(str(settings.database_url), pool_pre_ping=True)


@pytest.fixture
def db_session(db_engine) -> Session:
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def db_client(db_session: Session) -> TestClient:
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
def admin_tokens(db_client: TestClient) -> dict[str, str]:
    response = db_client.post(
        "/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
    }
