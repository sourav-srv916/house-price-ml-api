
# Test prediction with valid input
def test_predict_valid_input(client):
    payload = {
        "OverallQual": 7,
        "GrLivArea": 1800,
        "BedroomAbvGr": 3,
        "FullBath": 2,
        "GarageCars": 2
    }

    response = client.post(
        "/api/v1/predict",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert "prediction" in data
    assert isinstance(data["prediction"], float)
    assert data["prediction"] > 0

    assert "model_version" in data
    assert "request_id" in data


# Test validation when a required field is missing
def test_predict_missing_field(client):
    payload = {
        "OverallQual": 7,
        "GrLivArea": 1800,
        "BedroomAbvGr": 3,
        "FullBath": 2
        # GarageCars is missing
    }

    response = client.post(
        "/api/v1/predict",
        json=payload
    )

    assert response.status_code == 422


# Test validation with an invalid OverallQual value
def test_predict_invalid_input(client):
    payload = {
        "OverallQual": 15,
        "GrLivArea": 1800,
        "BedroomAbvGr": 3,
        "FullBath": 2,
        "GarageCars": 2
    }

    response = client.post(
        "/api/v1/predict",
        json=payload
    )

    assert response.status_code == 422


# Test rejection of a batch larger than the configured limit
def test_predict_batch_oversized(client):
    house = {
        "OverallQual": 7,
        "GrLivArea": 1800,
        "BedroomAbvGr": 3,
        "FullBath": 2,
        "GarageCars": 2
    }

    payload = {
        "houses": [house, house, house]
    }

    response = client.post(
        "/api/v1/predict-batch",
        json=payload
    )

    assert response.status_code == 400
    assert "Maximum batch size" in response.json()["detail"]
