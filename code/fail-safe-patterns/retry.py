from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_service():
    print("Trying service...")
    # simulate service failure
    raise Exception("Service unavailable")

try:
    call_service()
except Exception as e:
    print(f"Service failed after retries: {e}")
    # fallback logic
    print("Using fallback service")
