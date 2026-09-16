import asyncio
import time

import httpx

from app.config import settings


BASE_URL = "http://localhost:8000"
API_KEY = settings.API_KEY

TOTAL_REQUESTS = 100

VALID_INPUT = {
    "OverallQual": 7,
    "GrLivArea": 1710,
    "BedroomAbvGr": 3,
    "FullBath": 2,
    "GarageCars": 2,
}


async def send_prediction(
    client: httpx.AsyncClient,
    request_number: int,
):
    start_time = time.perf_counter()

    try:
        response = await client.post(
            f"{BASE_URL}/api/v1/predict",
            json=VALID_INPUT,
            headers={"X-API-Key": API_KEY},
        )

        duration = time.perf_counter() - start_time

        return {
            "request_number": request_number,
            "status_code": response.status_code,
            "duration": duration,
        }

    except Exception as error:
        duration = time.perf_counter() - start_time

        return {
            "request_number": request_number,
            "status_code": None,
            "duration": duration,
            "error": str(error),
        }


async def run_load_test():
    timeout = httpx.Timeout(30.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = [
            send_prediction(client, request_number)
            for request_number in range(1, TOTAL_REQUESTS + 1)
        ]

        start_time = time.perf_counter()

        results = await asyncio.gather(*tasks)

        total_duration = time.perf_counter() - start_time

    successful = [
        result
        for result in results
        if result["status_code"] == 200
    ]

    failed = [
        result
        for result in results
        if result["status_code"] != 200
    ]

    response_times = [
        result["duration"]
        for result in results
    ]

    average_response_time = sum(response_times) / len(response_times)
    maximum_response_time = max(response_times)

    print("\n===== LOAD TEST RESULTS =====")
    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Successful requests: {len(successful)}")
    print(f"Failed requests: {len(failed)}")
    print(f"Total test duration: {total_duration:.4f} seconds")
    print(f"Average response time: {average_response_time:.4f} seconds")
    print(f"Maximum response time: {maximum_response_time:.4f} seconds")

    if failed:
        print("\nFailed requests:")

        for result in failed:
            print(result)


if __name__ == "__main__":
    asyncio.run(run_load_test())