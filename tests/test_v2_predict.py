# ---------------------------------------------------------
# TEST V2 VALID PREDICTION
# ---------------------------------------------------------

def test_predict_v2_valid_input(client):

    # Valid house input
    payload = {
        "OverallQual": 7,
        "GrLivArea": 1800,
        "BedroomAbvGr": 3,
        "FullBath": 2,
        "GarageCars": 2
    }

    response = client.post(
        "/api/v2/predict",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    # Check prediction
    assert "prediction" in data
    assert isinstance(data["prediction"], float)
    assert data["prediction"] > 0

    # Check existing fields
    assert "confidence" in data
    assert "model_version" in data
    assert "request_id" in data

    # Check new V2 field
    assert data["prediction_unit"] == "USD"


# ---------------------------------------------------------
# TEST V1 VS V2 RESPONSE SHAPE
# ---------------------------------------------------------

def test_v1_and_v2_have_different_response_shapes(client):

    # Same input for both API versions
    payload = {
        "OverallQual": 7,
        "GrLivArea": 1800,
        "BedroomAbvGr": 3,
        "FullBath": 2,
        "GarageCars": 2
    }

    # Call V1
    v1_response = client.post(
        "/api/v1/predict",
        json=payload
    )

    # Call V2
    v2_response = client.post(
        "/api/v2/predict",
        json=payload
    )

    assert v1_response.status_code == 200
    assert v2_response.status_code == 200

    v1_data = v1_response.json()
    v2_data = v2_response.json()

    # V1 must not contain the new V2 field
    assert "prediction_unit" not in v1_data

    # V2 must contain the new field
    assert "prediction_unit" in v2_data
    assert v2_data["prediction_unit"] == "USD"

    # Both versions still return a prediction
    assert "prediction" in v1_data
    assert "prediction" in v2_data


# ---------------------------------------------------------
# TEST V2 INVALID INPUT
# ---------------------------------------------------------

def test_predict_v2_invalid_input(client):

    # OverallQual must be between 1 and 10
    payload = {
        "OverallQual": 15,
        "GrLivArea": 1800,
        "BedroomAbvGr": 3,
        "FullBath": 2,
        "GarageCars": 2
    }

    response = client.post(
        "/api/v2/predict",
        json=payload
    )

    assert response.status_code == 422