import pytest
from fastapi.testclient import TestClient
import asyncio

from src.app.main import app
from src.app.db.database import Base, get_async_session
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Setup a test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)

async def override_get_async_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    async def setup():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(setup())
    yield

    async def teardown():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(teardown())


def test_register_and_login():
    # Register a new user
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password"
    })
    assert response.status_code == 201

    # Login with the new user
    response = client.post("/api/v1/auth/jwt/login", data={
        "username": "test@example.com",
        "password": "password"
    })
    assert response.status_code == 204 # No content on successful login
    assert "greencheck" in response.cookies


def test_get_me():
    # Register and login to get a token
    client.post("/api/v1/auth/register", json={"email": "me@example.com", "password": "password"})
    login_response = client.post("/api/v1/auth/jwt/login", data={"username": "me@example.com", "password": "password"})

    cookies = {"greencheck": login_response.cookies["greencheck"]}

    # Get the current user
    response = client.get("/api/v1/users/me", cookies=cookies)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
