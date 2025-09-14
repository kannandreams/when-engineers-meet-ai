import pybreaker
import random
import time

# Simulate GPT-4 API call
def call_gpt4_api(request):
    # Randomly fail to simulate API downtime
    if random.random() < 0.7:  # 70% chance of success
        return f"GPT-4 Response for '{request}'"
    else:
        raise Exception("GPT-4 API Failure")

# Fallback model call (local)
def call_local_llama(request):
    return f"Llama Degraded Response for '{request}'"

# Listener to track state changes (optional)
class CircuitBreakerListener(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old_state, new_state):
        print(f"[Circuit Breaker] State changed from {old_state} to {new_state}")

# Create a circuit breaker
breaker = pybreaker.CircuitBreaker(
    fail_max=3,             # Trip after 3 failures
    reset_timeout=10,       # Try again after 10 seconds
    listeners=[CircuitBreakerListener()]
)

# Client request function using circuit breaker
def client_request(request):
    try:
        # Protected call
        result = breaker.call(call_gpt4_api, request)
        print(f"[Client] Got GPT-4 result: {result}")
    except pybreaker.CircuitBreakerError:
        # Circuit is open, use fallback
        print("[Client] Circuit Open. Using fallback.")
        result = call_local_llama(request)
        print(f"[Client] Got fallback result: {result}")
    except Exception as e:
        # API failed but circuit still closed
        print(f"[Client] GPT-4 failed: {e}. Using fallback.")
        result = call_local_llama(request)
        print(f"[Client] Got fallback result: {result}")

# Simulate multiple requests
for i in range(10):
    print(f"\nRequest {i+1}:")
    client_request(f"My request {i+1}")
    time.sleep(1)
