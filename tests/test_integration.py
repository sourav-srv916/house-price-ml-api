import httpx

from app.config import settings

BASE_URL = "http://localhost:8000"
API_KEY = settings.API_KEY

VALID_INPUT = {
    "OverallQual": 7,
    "GrLivArea": 1710,
    "BedroomAbvGr": 3,
    "FullBath": 2,
    "GarageCars": 2,
}

BATCH_INPUT = {
    "houses": [
        {
            "OverallQual": 7,
            "GrLivArea": 1710,
            "BedroomAbvGr": 3,
            "FullBath": 2,
            "GarageCars": 2,
        },
        {
            "OverallQual": 6,
            "GrLivArea": 1500,
            "BedroomAbvGr": 3,
            "FullBath": 2,
            "GarageCars": 1,
        },
    ]
}


def test_container_health():
    response = httpx.get(f"{BASE_URL}/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_container_prediction():
    response = httpx.post(
        f"{BASE_URL}/api/v1/predict",
        json=VALID_INPUT,
        headers={"X-API-Key": API_KEY},
    )

    assert response.status_code == 200

    data = response.json()

    assert "prediction" in data
    assert "model_version" in data
    assert "request_id" in data


def test_container_batch_prediction():
    response = httpx.post(
        f"{BASE_URL}/api/v1/predict-batch",
        json=BATCH_INPUT,
        headers={"X-API-Key": API_KEY},
    )

    assert response.status_code == 200

    data = response.json()

    assert "predictions" in data
    assert len(data["predictions"]) == 2


def test_container_v2_prediction():
    response = httpx.post(
        f"{BASE_URL}/api/v2/predict",
        json=VALID_INPUT,
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "model_version" in data
    assert "request_id" in data

    
def test_container_metrics():
    response = httpx.get(f"{BASE_URL}/metrics")

    assert response.status_code == 200

    assert "http_requests_total" in response.text
    assert "house_price_predictions_total" in response.text