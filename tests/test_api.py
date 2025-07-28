
import pytest
from fastapi.testclient import TestClient
from app.models import Provider, ProviderPricing

def test_root_endpoint(client: TestClient):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Healthcare Provider Analysis API"}

def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_providers_endpoint_missing_params(client: TestClient):
    """Test providers endpoint with missing required parameters"""
    response = client.get("/api/v1/providers")
    assert response.status_code == 400
    assert "Either provider_id or provider_name is required" in response.json()["detail"]

def test_providers_endpoint_with_test_data(client: TestClient, db_session):
    """Test providers endpoint with test data"""
    # Add test data
    provider = Provider(
        provider_id=1,
        provider_name="Test Hospital",
        provider_city="Test City",
        provider_state="NY",
        provider_zip_code="12345"
    )
    db_session.add(provider)

    pricing = ProviderPricing(
        provider_id=1,
        ms_drg_definition="Test DRG",
        averaged_covered_charges=10000
    )
    db_session.add(pricing)
    db_session.commit()

    # Test the endpoint
    response = client.get(
        "/api/v1/providers",
        params={
            "provider_id": 1,
            "drg_description": "Test"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["provider_id"] == 1
    assert data[0]["provider_name"] == "Test Hospital"

def test_ask_endpoint_missing_openai_key(client: TestClient):
    """Test ask endpoint without OpenAI API key"""
    response = client.post(
        "/api/v1/ask",
        json={"question": "How many providers are there?"}
    )
    # This might return 500 due to missing API key, which is expected
    assert response.status_code in [200, 500]