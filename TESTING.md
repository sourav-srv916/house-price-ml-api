# Testing

## Integration Testing, Load Testing and Bug Fixing

This document records the integration testing, load testing, issues found and fixes applied to the containerized **House Price ML API**.

## 1. Integration Testing

The running Docker API was tested using real HTTP requests with `httpx`.

| Endpoint | Test | Result |
| :--- | :--- | :---: |
| `/api/v1/health` | API and model health | Passed |
| `/api/v1/predict` | Single prediction | Passed |
| `/api/v1/predict-batch` | Batch prediction | Passed |
| `/api/v2/predict` | V2 prediction | Passed |
| `/metrics` | Prometheus metrics | Passed |

**Result: 5 passed, 0 failed**

## 2. Load Testing

100 concurrent requests were sent to `/api/v1/predict`.

| Metric | 1 Worker | 2 Workers |
| :--- | ---: | ---: |
| Requests | 100 | 100 |
| Successful | 100 | 100 |
| Failed | 0 | 0 |
| Total duration | 3.9970 s | 1.8055 s |
| Average response | 3.8753 s | 1.7322 s |
| Maximum response | 3.9362 s | 1.7855 s |

The 2-worker configuration reduced the total test duration by approximately **55%** in this test environment.

## 3. Issues Found and Fixes

| Issue | Fix |
| :--- | :--- |
| Single worker was slower under 100 concurrent requests | Changed Uvicorn configuration from 1 worker to 2 workers |
| Prometheus prediction counter did not initially aggregate correctly across 2 Uvicorn workers | Enabled Prometheus multiprocess mode using a shared `PROMETHEUS_MULTIPROC_DIR` and `MultiProcessCollector` |
| Docker worker change was not reflected immediately | Rebuilt the Docker image using `docker compose up --build` |
| PowerShell `curl` caused a warning | Used `curl.exe` to check `/metrics` |
| Starlette/httpx deprecation warning appeared | Confirmed that tests still passed; warning did not affect functionality |

### Testing Investigation
Several areas were investigated, including **batch performance, log growth, timeout behavior and concurrent request handling**. No confirmed defects were found in the first three areas. A performance issue was identified under 100 concurrent requests with a single Uvicorn worker, which was addressed by configuring two workers.

The **Prometheus counter** did not initially aggregate correctly across 2 Uvicorn workers. This was fixed using **Prometheus multiprocess mode**. After rebuilding, the load test achieved **100/100** successful requests and `/metrics` reported **104.0**, confirming correct aggregation.

### Prometheus Multi-Worker Testing

| Stage | Request Flow | `/metrics` Result |
| :--- | :--- | :---: |
| **Before the fix** | 100 requests → Worker 1 + Worker 2 | **49 or 51** |
| **After the fix** | 100 requests → Worker 1 + Worker 2 → `MultiProcessCollector` | **100.0** |

### Final `/metrics` Verification

| Source | Successful predictions |
| :--- | ---: |
| Load test | 100 |
| V1 `/predict` | 1 |
| V1 `/predict-batch` | 2 |
| V2 `/predict` | 1 |
| **Total `/metrics`** | **104.0** |

**Calculation:** `100 + 1 + 2 + 1 = 104`
## 4. Final Verification

After the fixes:

- Docker API started successfully.
- ML model loaded successfully.
- Integration tests: **5 passed**
- Load test: **100 successful / 0 failed**
- Prometheus `/metrics` verified successfully.
- Prometheus **multi-worker aggregation** verified successfully.
- Final `house_price_predictions_total`: **104.0**
- 2-worker configuration verified successfully.

## Conclusion

The API was successfully verified through integration testing, concurrent load testing, monitoring and bug fixing. The 2-worker configuration provided faster concurrent request handling while maintaining 100% successful requests in the test environment.