# House Price Prediction ML API

## Project Overview

This project aims to develop a machine learning model that predicts house prices and exposes the model through a monitored REST API. The project will gradually introduce FastAPI, Pydantic, Docker, monitoring, and deployment.

## Machine Learning Problem

The machine learning problem is **House Price Prediction**.

This is a regression problem because the model predicts a continuous numerical value representing the sale price of a house.

## Dataset

The project will use the **Kaggle House Prices dataset**.

The dataset contains information about residential properties and their corresponding sale prices.

Selected house features will be used as inputs to the machine learning model, and the sale price will be used as the target variable.

## API Contract

The `/predict` endpoint will accept house-related information such as overall quality, living area, number of bedrooms, number of bathrooms, and number of garage cars. The API will validate the input data before passing it to the trained machine learning regression model. The model will predict the estimated sale price of the house, and the API will return the predicted price as a JSON response. If the input data is invalid or missing, the API will return an appropriate validation error.

## Request Flow

The application will follow this flow:

```text
┌─────────────────────┐
│    Client / User    │
└──────────┬──────────┘
           │
           │  POST /predict
           ▼
┌─────────────────────┐
│   Request Data      │
│   House Features    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Input Validation  │
│      Pydantic       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   ML Regression     │
│       Model         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Predicted House    │
│       Price         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    JSON Response    │
└─────────────────────┘
```

The client sends house features to the `/predict` endpoint. The API first validates the received data. If the data is valid, it is passed to the trained machine learning regression model. The model generates an estimated house price, which is returned to the client as a JSON response.

## Project Goal

The goal of this project is to understand how a machine learning regression model can be developed, exposed through a REST API, containerized using Docker, and monitored in a practical software engineering workflow.

## How to Run This Project

### Prerequisites

Before running the project, make sure you have:

- Git installed
- Docker Desktop installed and running
- Python installation is not required because the application runs inside a Docker container.

### 1. Clone the Repository

Clone the project from GitHub:

```bash
git clone https://github.com/sourav-srv916/house-price-ml-api
```

Move into the project directory:

```bash
cd house-price-ml-api
```

### 2. Create the `.env` File

Create your local `.env` file from `.env.example`:

```powershell
Copy-Item .env.example .env
```

### 3. Start the Application

Build the Docker image and start the API using Docker Compose:

```bash
docker compose up --build
```

### 4. Access the API

Open Swagger UI in your browser:

```text
http://localhost:8000/docs
```

Use Swagger UI to test the **Health** and **Prediction** endpoints.

### 5. Run the Project Again

If no project changes were made and the image is already built:

```bash
docker compose up
```

No rebuild is required.

### 6. Stop the Application

Press `Ctrl+C` or run:

```bash
docker compose down
```

### 7. Rebuild After Project Changes

If project files, dependencies, the Dockerfile, or model configuration changes:

```bash
docker compose up --build
```