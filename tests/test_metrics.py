from prometheus_client import REGISTRY

from app.config import settings


VALID_INPUT = {
    "OverallQual": 7,
    "GrLivArea": 1710,
    "BedroomAbvGr": 3,
    "FullBath": 2,
    "GarageCars": 2
}


def test_metrics_endpoint(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "house_price_predictions_total" in response.text


def test_prediction_counter_increases(client):
    before = REGISTRY.get_sample_value("house_price_predictions_total")

    response = client.post(
        "/api/v1/predict",
        json=VALID_INPUT,
        headers={"X-API-Key": settings.API_KEY}
    )

    assert response.status_code == 200

    after = REGISTRY.get_sample_value("house_price_predictions_total")

    assert after == before + 1