from prometheus_client import Counter


house_price_predictions_total = Counter(
    "house_price_predictions_total",
    "Total number of successful house price predictions"
)