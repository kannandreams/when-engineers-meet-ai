import time
import random
from datetime import datetime, timedelta

# Install these libraries first:
# pip install tenacity pybreaker

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from pybreaker import CircuitBreaker, CircuitBreakerError

# --- Mock External Service (Remains similar) ---
def mock_payment_gateway_api(amount, user_id):
    """Simulates an external payment gateway API call with a higher failure rate."""
    if random.random() < 0.7:  # 70% chance of failure for demonstration
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Payment Gateway: Processing refund for {user_id} of ${amount:.2f}...")
        time.sleep(0.5)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Payment Gateway: FAILED!")
        raise ConnectionError("Mock Payment Gateway API is unavailable or timed out.")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Payment Gateway: Processing refund for {user_id} of ${amount:.2f}...")
        time.sleep(0.2)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Payment Gateway: SUCCESS for {user_id}!")
        return {"status": "success", "transaction_id": f"TXN-{random.randint(10000, 99999)}"}

# --- 1. Circuit Breaker and Retries with pybreaker and tenacity ---

# Configure the Circuit Breaker for the payment gateway
# Falls back to OPEN after 3 failures, stays open for 5 seconds
payment_gateway_breaker = CircuitBreaker(
    fail_max=3,            # Number of failures before opening
    reset_timeout=5,       # Time in seconds before attempting to half-open
    exclude=[ValueError]   # Example: don't open circuit for invalid input errors
)

# Apply tenacity retry logic for *individual* attempts before the circuit opens.
# Only retry if it's a ConnectionError, up to 2 times, waiting 1 second between retries.
# The circuit breaker will then take over if retries also fail consistently.
@retry(stop=stop_after_attempt(2),
       wait=wait_fixed(1),
       retry=retry_if_exception_type(ConnectionError),
       reraise=True) # Ensure the last exception is re-raised to inform the circuit breaker
@payment_gateway_breaker  # Decorate with the circuit breaker
def safe_mock_payment_gateway_api(amount, user_id):
    """
    Combines tenacity for retries and pybreaker for circuit breaking.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Attempting API call for {user_id}...")
    return mock_payment_gateway_api(amount, user_id)

# --- 2. Human-in-the-Loop Example (Remains similar as it's more logic-driven) ---

class AIRefundAgent:
    """
    Simulates an AI agent that proposes refund decisions.
    """
    def __init__(self, confidence_threshold=0.7, high_value_threshold=500):
        self.confidence_threshold = confidence_threshold
        self.high_value_threshold = high_value_threshold

    def analyze_refund_request(self, user_id, reason, amount):
        """
        AI logic to analyze a refund request and propose an action.
        Returns (decision, confidence).
        """
        time.sleep(0.1) # Simulate AI processing

        decision = {"action": "approve", "amount": amount, "user_id": user_id}
        confidence = random.uniform(0.5, 0.95) # Simulate varying AI confidence

        if "damaged" in reason.lower() and amount > 100:
            confidence -= 0.1
        elif "mistake" in reason.lower() and amount < 50:
            confidence += 0.05

        if confidence < self.confidence_threshold:
            decision["action"] = "review"
        elif amount > self.high_value_threshold:
            decision["action"] = "review"
        elif "suspicious" in reason.lower() or "fraud" in reason.lower():
             decision["action"] = "review"

        return decision, confidence

def process_refund_with_human_review(agent, user_id, reason, amount):
    """
    Integrates the AI agent's decision with a human review step.
    This is the "Human-in-the-Loop" pattern.
    """
    print(f"\n--- Processing Refund Request for {user_id} ---")
    proposed_decision, confidence = agent.analyze_refund_request(user_id, reason, amount)
    print(f"AI Proposed Decision: {proposed_decision['action']}, Amount: ${proposed_decision['amount']:.2f}, Confidence: {confidence:.2f}")

    if proposed_decision['action'] == "review":
        print(f"--> Human-in-the-Loop: Decision requires human review due to '{reason}' or high value/low confidence.")
        print("    Sending to human supervisor queue...")
        # Simulate human decision (in a real system, this is an asynchronous step)
        human_input = input("    Human review: Approve (A) or Reject (R)? ").upper()
        if human_input == 'A':
            print("    Human approved the refund.")
            return True, "Human Approved"
        else:
            print("    Human rejected/modified the refund.")
            return False, "Human Rejected"
    elif proposed_decision['action'] == "approve":
        print("--> AI approved the refund automatically.")
        return True, "AI Approved"
    else:
        print("--> AI proposed an unknown action. Sending to human review.")
        return False, "Unknown AI Action, Human Review Needed"


# --- Main Execution Flow ---
if __name__ == "__main__":
    print("--- Demonstrating pybreaker Circuit Breaker and tenacity Retries ---")

    # Simulate multiple calls to the payment gateway
    for i in range(20): # Increased iterations to better observe circuit breaker behavior
        user_id = f"user_{random.randint(100, 999)}"
        amount = random.uniform(10, 200)
        try:
            # Call the safe, decorated API function
            result = safe_mock_payment_gateway_api(amount, user_id)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Application: Refund request {user_id} processed: {result}")
        except CircuitBreakerError:
            # Fallback when circuit is OPEN
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Application: Circuit is OPEN - Initiating fallback: Logging for manual refund.")
            # This is where you'd queue the request for later processing by a human or a batch job
        except ConnectionError as e:
            # This exception might only be caught if tenacity retries are exhausted
            # but the circuit breaker hasn't tripped yet or is in HALF-OPEN state.
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Application: An individual connection error occurred for {user_id}: {e} (Fallback for individual error)")
        except Exception as e:
            # Catch any other unexpected errors
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Application: An unexpected error occurred for {user_id}: {e}")
        finally:
            time.sleep(0.7) # Simulate some processing time between requests


    print("\n" + "="*50 + "\n")
    print("--- Demonstrating Human-in-the-Loop Pattern ---")

    ai_refund_agent = AIRefundAgent(confidence_threshold=0.75, high_value_threshold=300)

    # Scenario 1: Low-value, simple request (AI approves)
    approved, reason_for_decision = process_refund_with_human_review(ai_refund_agent, "user_A", "Accidental double charge of $25", 25.00)
    print(f"Final Decision for user_A: {approved} ({reason_for_decision})\n")

    # Scenario 2: High-value request (Human review)
    approved, reason_for_decision = process_refund_with_human_review(ai_refund_agent, "user_B", "Item damaged on arrival, refund $450", 450.00)
    print(f"Final Decision for user_B: {approved} ({reason_for_decision})\n")

    # Scenario 3: AI low confidence (Human review)
    # To reliably trigger low confidence for demonstration, we'll temporarily adjust the threshold
    original_threshold = ai_refund_agent.confidence_threshold
    ai_refund_agent.confidence_threshold = 0.95 # Make it harder for AI to be confident
    approved, reason_for_decision = process_refund_with_human_review(ai_refund_agent, "user_C", "Product not as described, return $150", 150.00)
    print(f"Final Decision for user_C: {approved} ({reason_for_decision})\n")
    ai_refund_agent.confidence_threshold = original_threshold # Reset it

    # Scenario 4: Suspicious keyword (Human review)
    approved, reason_for_decision = process_refund_with_human_review(ai_refund_agent, "user_D", "This is a suspicious refund for $75.", 75.00)
    print(f"Final Decision for user_D: {approved} ({reason_for_decision})\n")