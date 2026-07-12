import time

from app.tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD


def test_login_success(db_client) -> None:
    response = db_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ecosphere.local", "password": "ChangeMe123!"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"]
    assert body["data"]["refresh_token"]
    assert body["data"]["user"]["email"] == "admin@ecosphere.local"
    assert "ADMIN" in [role["name"] for role in body["data"]["user"]["roles"]]


def test_login_invalid_credentials(db_client) -> None:
    response = db_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ecosphere.local", "password": "WrongPassword1"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"


def test_me_requires_authentication(client) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"


def test_me_returns_profile(db_client, admin_tokens) -> None:
    response = db_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "admin@ecosphere.local"
    assert "dashboard:read" in body["data"]["permissions"]


def test_refresh_token_rotation(db_client) -> None:
    login_response = db_client.post(
        "/api/v1/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()["data"]

    # Ensure the rotated refresh token gets a distinct JWT payload (exp claim).
    time.sleep(1)

    response = db_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_data["refresh_token"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"]
    assert body["data"]["refresh_token"] != login_data["refresh_token"]


def test_session_requires_rbac_permission(db_client, admin_tokens) -> None:
    response = db_client.get(
        "/api/v1/auth/session",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["session"]["email"] == "admin@ecosphere.local"
    assert "dashboard:read" in body["data"]["session"]["permissions"]


def test_logout_revokes_session(db_client, admin_tokens) -> None:
    logout_response = db_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {admin_tokens['access_token']}"},
        json={"refresh_token": admin_tokens["refresh_token"]},
    )
    assert logout_response.status_code == 200

    refresh_response = db_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": admin_tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 401
