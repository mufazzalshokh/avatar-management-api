"""
Integration tests for the API endpoints, exercised through the FastAPI
TestClient with an in-memory SQLite database (see conftest.py).
"""
import io

from PIL import Image


def _make_valid_png_bytes() -> bytes:
    """Generate a real, valid 1x1 PNG in memory via Pillow — a hand-crafted
    byte literal is too easy to get a CRC wrong on, which PIL's own
    Image.verify() correctly rejects."""
    buf = io.BytesIO()
    Image.new("RGB", (1, 1), color=(255, 0, 0)).save(buf, format="PNG")
    return buf.getvalue()


class TestAuthRegister:
    def test_register_new_user_success(self, client):
        response = client.post(
            "/api/auth/register",
            json={"identifier": "newuser1", "password": "securepass123"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["user"]["identifier"] == "newuser1"
        assert "access_token" in body["data"]["tokens"]
        assert "refresh_token" in body["data"]["tokens"]

    def test_register_duplicate_identifier_fails(self, client, test_user):
        response = client.post(
            "/api/auth/register",
            json={"identifier": "testuser", "password": "anotherpass123"},
        )
        assert response.status_code == 400
        assert response.json()["status"] == "fail"

    def test_register_password_too_short(self, client):
        response = client.post(
            "/api/auth/register",
            json={"identifier": "shortpassuser", "password": "abc"},
        )
        assert response.status_code == 422


class TestAuthLogin:
    def test_login_success(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            json={"identifier": "testuser", "password": "testpassword123"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert "access_token" in body["data"]["tokens"]

    def test_login_wrong_password_fails(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            json={"identifier": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert response.json()["status"] == "fail"

    def test_login_nonexistent_user_fails(self, client):
        response = client.post(
            "/api/auth/login",
            json={"identifier": "ghostuser", "password": "whatever123"},
        )
        assert response.status_code == 401


class TestAuthRefresh:
    def test_refresh_token_rotation(self, client, test_user):
        login_response = client.post(
            "/api/auth/login",
            json={"identifier": "testuser", "password": "testpassword123"},
        )
        old_refresh = login_response.json()["data"]["tokens"]["refresh_token"]

        refresh_response = client.post(
            "/api/auth/refresh", json={"refresh_token": old_refresh}
        )
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()["data"]
        assert new_tokens["refresh_token"] != old_refresh

    def test_refresh_with_old_token_after_rotation_fails(self, client, test_user):
        # OAuth2.0 rotation: once a refresh token is used, it must be revoked
        login_response = client.post(
            "/api/auth/login",
            json={"identifier": "testuser", "password": "testpassword123"},
        )
        old_refresh = login_response.json()["data"]["tokens"]["refresh_token"]

        # Use it once — this rotates and revokes it
        client.post("/api/auth/refresh", json={"refresh_token": old_refresh})

        # Reusing the same (now revoked) refresh token must fail
        second_attempt = client.post(
            "/api/auth/refresh", json={"refresh_token": old_refresh}
        )
        assert second_attempt.status_code == 401

    def test_refresh_with_invalid_token_fails(self, client):
        response = client.post(
            "/api/auth/refresh", json={"refresh_token": "not-a-real-token"}
        )
        assert response.status_code == 401


class TestUsersMe:
    def test_get_current_user_requires_auth(self, client):
        response = client.get("/api/users/me")
        assert response.status_code in (401, 403)

    def test_get_current_user_with_valid_token(self, client, auth_headers):
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["identifier"] == "testuser"

    def test_delete_current_user(self, client, auth_headers):
        response = client.delete("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # The account should no longer be able to log in
        login_response = client.post(
            "/api/auth/login",
            json={"identifier": "testuser", "password": "testpassword123"},
        )
        assert login_response.status_code == 401


class TestAvatarUpload:
    def test_upload_requires_auth(self, client):
        response = client.post("/avatars/upload")
        assert response.status_code in (401, 403)

    def test_upload_rejects_non_image_file(self, client, auth_headers):
        response = client.post(
            "/avatars/upload",
            headers=auth_headers,
            files={"file": ("test.txt", b"not an image", "text/plain")},
        )
        assert response.status_code == 400
        assert response.json()["status"] == "fail"

    def test_upload_valid_image_returns_url(self, client, auth_headers):
        png_bytes = _make_valid_png_bytes()
        response = client.post(
            "/avatars/upload",
            headers=auth_headers,
            files={"file": ("avatar.png", png_bytes, "image/png")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["avatar_url"].startswith("/uploads/")
