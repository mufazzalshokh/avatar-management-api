"""
Unit tests for authentication utilities: password hashing and JWT tokens.
No HTTP client needed — these test the auth building blocks in isolation.
"""
from app.utils.password import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token, decode_token, verify_token_type


class TestPasswordHashing:
    def test_hash_password_returns_different_string(self):
        plain = "testpassword123"
        hashed = hash_password(plain)
        assert hashed != plain
        assert len(hashed) > 0

    def test_hash_password_is_not_deterministic(self):
        # bcrypt salts each hash, so hashing the same password twice
        # must produce two different hashes
        plain = "testpassword123"
        hash_one = hash_password(plain)
        hash_two = hash_password(plain)
        assert hash_one != hash_two

    def test_verify_password_correct(self):
        plain = "testpassword123"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_password_incorrect(self):
        hashed = hash_password("testpassword123")
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_empty_string(self):
        hashed = hash_password("testpassword123")
        assert verify_password("", hashed) is False


class TestJWTTokens:
    def test_create_access_token_returns_string(self):
        token = create_access_token(data={"sub": "1"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_returns_string(self):
        token = create_refresh_token(data={"sub": "1"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_and_refresh_tokens_differ(self):
        # Same payload, different token type — must not produce the same token
        access = create_access_token(data={"sub": "1"})
        refresh = create_refresh_token(data={"sub": "1"})
        assert access != refresh

    def test_decode_token_returns_original_payload(self):
        token = create_access_token(data={"sub": "42"})
        payload = decode_token(token)
        assert payload is not None
        assert payload.get("sub") == "42"

    def test_decode_invalid_token_returns_none(self):
        payload = decode_token("this.is.not.a.valid.jwt")
        assert payload is None

    def test_verify_token_type_access(self):
        token = create_access_token(data={"sub": "1"})
        assert verify_token_type(token, "access") is True
        assert verify_token_type(token, "refresh") is False

    def test_verify_token_type_refresh(self):
        token = create_refresh_token(data={"sub": "1"})
        assert verify_token_type(token, "refresh") is True
        assert verify_token_type(token, "access") is False
