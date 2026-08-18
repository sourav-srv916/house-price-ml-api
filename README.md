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