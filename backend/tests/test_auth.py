"""
Tests for authentication endpoints
"""
import pytest


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test login with nonexistent user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "password"}
    )
    assert response.status_code == 401


def test_get_me_authenticated(client, auth_headers):
    """Test getting current user when authenticated."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


def test_get_me_unauthenticated(client):
    """Test getting current user when not authenticated."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

