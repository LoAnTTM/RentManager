"""
Tests for location endpoints
"""
import pytest


def test_create_location(client, auth_headers):
    """Test creating a new location."""
    response = client.post(
        "/api/v1/locations",
        headers=auth_headers,
        json={
            "name": "Test Location",
            "address": "123 Test Street",
            "electric_price": "3500",
            "water_price": "8000",
            "garbage_fee": "30000"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Location"
    assert data["room_count"] == 0


def test_get_locations(client, auth_headers):
    """Test getting all locations."""
    # Create a location first
    client.post(
        "/api/v1/locations",
        headers=auth_headers,
        json={"name": "Test Location"}
    )
    
    response = client.get("/api/v1/locations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_location_by_id(client, auth_headers):
    """Test getting a location by ID."""
    # Create a location first
    create_response = client.post(
        "/api/v1/locations",
        headers=auth_headers,
        json={"name": "Test Location"}
    )
    location_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/locations/{location_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == location_id


def test_update_location(client, auth_headers):
    """Test updating a location."""
    # Create a location first
    create_response = client.post(
        "/api/v1/locations",
        headers=auth_headers,
        json={"name": "Test Location"}
    )
    location_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/v1/locations/{location_id}",
        headers=auth_headers,
        json={"name": "Updated Location"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Location"


def test_delete_location(client, auth_headers):
    """Test deleting a location."""
    # Create a location first
    create_response = client.post(
        "/api/v1/locations",
        headers=auth_headers,
        json={"name": "Test Location"}
    )
    location_id = create_response.json()["id"]
    
    response = client.delete(f"/api/v1/locations/{location_id}", headers=auth_headers)
    assert response.status_code == 204


def test_locations_unauthenticated(client):
    """Test accessing locations without authentication."""
    response = client.get("/api/v1/locations")
    assert response.status_code == 401

