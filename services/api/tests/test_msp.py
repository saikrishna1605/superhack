"""
Tests for MSP endpoints
"""
import pytest
from datetime import datetime, timedelta


def test_msp_dashboard(client, auth_headers, db_session):
    """Test MSP dashboard endpoint"""
    from models.models import Client
    
    # Create test client
    client_obj = Client(
        name="Test Client",
        industry="Technology",
        employee_count=100,
        monthly_revenue=10000,
        contract_start_date=datetime.now() - timedelta(days=365),
        contract_end_date=datetime.now() + timedelta(days=365),
        health_score=85.0,
        is_active=True
    )
    db_session.add(client_obj)
    db_session.commit()
    
    response = client.get("/msp/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_clients" in data
    assert "active_clients" in data
    assert "monthly_revenue" in data
    assert "avg_health_score" in data


def test_get_clients_list(client, auth_headers, db_session):
    """Test getting list of clients"""
    from models.models import Client
    
    # Create test clients
    for i in range(3):
        client_obj = Client(
            name=f"Client {i}",
            industry="Technology",
            employee_count=100,
            monthly_revenue=10000,
            health_score=80.0,
            is_active=True
        )
        db_session.add(client_obj)
    db_session.commit()
    
    response = client.get("/msp/clients", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_client_details(client, auth_headers, db_session):
    """Test getting client details"""
    from models.models import Client
    
    client_obj = Client(
        name="Test Client",
        industry="Technology",
        employee_count=100,
        monthly_revenue=10000,
        health_score=85.0,
        is_active=True
    )
    db_session.add(client_obj)
    db_session.commit()
    
    response = client.get(f"/msp/clients/{client_obj.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Client"
    assert data["health_score"] == 85.0


def test_get_nonexistent_client(client, auth_headers):
    """Test getting nonexistent client"""
    response = client.get("/msp/clients/99999", headers=auth_headers)
    assert response.status_code == 404
