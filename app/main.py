from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "ML API is alive"}


@app.post("/predict")
def predict():
    return {"prediction": "hardcoded_result"}