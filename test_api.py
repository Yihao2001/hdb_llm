from fastapi.testclient import TestClient
from backend.api import app 

client = TestClient(app)

# Unit test: valid input
def test_predict_price_valid():
    response = client.post("/predict_price", json={
        "town": "ANG MO KIO",
        "flat_type": "4 ROOM",
        "storey_range": "04 TO 06",
        "floor_area_sqm": 100,
        "flat_model": "Model A",
        "remaining_lease": 85
    })
    assert response.status_code == 200
    data = response.json()
    assert "predicted_price" in data
    assert "model_version" in data

# Edge case test: small values
def test_predict_price_edge_case():
    response = client.post("/predict_price", json={
        "town": "TOA PAYOH",
        "flat_type": "3 ROOM",
        "storey_range": "01 TO 03",
        "floor_area_sqm": 1,
        "flat_model": "Model B",
        "remaining_lease": 0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_price"] >= 0 

# Validation test: missing field
def test_predict_price_missing_field():
    response = client.post("/predict", json={
        "town": "ANG MO KIO",
        "flat_type": "4 ROOM"
    })
    assert response.status_code == 422 
