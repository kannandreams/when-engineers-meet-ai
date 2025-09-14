import time
import random
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional
from enum import Enum

# Install these libraries first:
# pip install langchain langchain-openai tenacity pybreaker pydantic

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import BaseTool, StructuredTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.runnable import RunnableConfig

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from pybreaker import CircuitBreaker, CircuitBreakerError
from pydantic import BaseModel, Field


# --- Configuration and Models ---

class RefundDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REVIEW = "review"

class RefundRequest(BaseModel):
    user_id: str = Field(description="User ID requesting refund")
    amount: float = Field(description="Refund amount")
    reason: str = Field(description="Reason for refund")
    order_id: Optional[str] = Field(default=None, description="Order ID if applicable")

class RefundAnalysis(BaseModel):
    decision: RefundDecision = Field(description="AI decision for refund")
    confidence: float = Field(description="AI confidence score (0-1)")
    reasoning: str = Field(description="AI reasoning for the decision")
    risk_factors: list[str] = Field(default=[], description="Identified risk factors")

class RefundResult(BaseModel):
    approved: bool = Field(description="Final refund approval status")
    decision_maker: str = Field(description="Who made the final decision")
    transaction_id: Optional[str] = Field(default=None, description="Transaction ID if processed")
    notes: str = Field(default="", description="Additional notes")


# --- Mock Payment Gateway (Enhanced) ---

def mock_payment_gateway_api(amount: float, user_id: str) -> Dict[str, Any]:
    """Enhanced mock payment gateway with more realistic behavior."""
    if random.random() < 0.7:  # 70% failure rate for demonstration
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Payment Gateway: Processing refund for {user_id} of ${amount:.2f}...")
        time.sleep(0.5)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Payment Gateway: FAILED!")
        raise ConnectionError("Mock Payment Gateway API is unavailable or timed out.")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Payment Gateway: Processing refund for {user_id} of ${amount:.2f}...")
        time.sleep(0.2)
        transaction_id = f"TXN-{random.randint(10000, 99999)}"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Payment Gateway: SUCCESS for {user_id}! Transaction: {transaction_id}")
        return {"status": "success", "transaction_id": transaction_id, "amount": amount}


# --- Circuit Breaker Setup ---

payment_gateway_breaker = CircuitBreaker(
    fail_max=3,
    reset_timeout=5,
    exclude=[ValueError]
)

@retry(stop=stop_after_attempt(2),
       wait=wait_fixed(1),
       retry=retry_if_exception_type(ConnectionError),
       reraise=True)
@payment_gateway_breaker
def safe_payment_gateway_call(amount: float, user_id: str) -> Dict[str, Any]:
    """Circuit breaker and retry-protected payment gateway call."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Attempting payment gateway call for {user_id}...")
    return mock_payment_gateway_api(amount, user_id)


# --- LangChain Tools ---

class PaymentGatewayTool(BaseTool):
    """LangChain tool for payment gateway integration."""
    name: str = "payment_gateway"
    description: str = "Process refund through payment gateway. Use when refund is approved."
    
    def _run(self, user_id: str, amount: float) -> str:
        """Execute the payment gateway call."""
        try:
            result = safe_payment_gateway_call(amount, user_id)
            return f"Refund processed successfully. Transaction ID: {result['transaction_id']}"
        except CircuitBreakerError:
            return "Payment gateway circuit breaker is OPEN. Refund queued for manual processing."
        except ConnectionError as e:
            return f"Payment gateway connection error: {str(e)}. Refund queued for retry."
        except Exception as e:
            return f"Unexpected error processing refund: {str(e)}"

class HumanReviewTool(BaseTool):
    """LangChain tool for human review integration."""
    name: str = "human_review"
    description: str = "Escalate refund decision to human review when needed."
    
    def _run(self, user_id: str, amount: float, reason: str, ai_reasoning: str) -> str:
        """Escalate to human review."""
        print(f"\n--- HUMAN REVIEW REQUIRED ---")
        print(f"User ID: {user_id}")
        print(f"Amount: ${amount:.2f}")
        print(f"Reason: {reason}")
        print(f"AI Reasoning: {ai_reasoning}")
        
        # In a real system, this would integrate with a ticketing system
        human_decision = input("Human review - Approve (A) or Reject (R)? ").upper()
        
        if human_decision == 'A':
            return f"Human approved refund for {user_id} of ${amount:.2f}"
        else:
            return f"Human rejected refund for {user_id} of ${amount:.2f}"

class RefundAnalysisTool(BaseTool):
    """LangChain tool for refund risk analysis."""
    name: str = "analyze_refund_risk"
    description: str = "Analyze refund request for risk factors and generate recommendation."
    
    def _run(self, user_id: str, amount: float, reason: str) -> str:
        """Analyze refund request for risks."""
        risk_factors = []
        confidence = random.uniform(0.6, 0.95)
        
        # Risk analysis logic
        if amount > 500:
            risk_factors.append("high_value")
            confidence -= 0.1
            
        if any(word in reason.lower() for word in ["suspicious", "fraud", "chargeback"]):
            risk_factors.append("suspicious_keywords")
            confidence -= 0.2
            
        if "damaged" in reason.lower() and amount > 100:
            risk_factors.append("high_value_damage_claim")
            confidence -= 0.05
            
        if "mistake" in reason.lower() and amount < 50:
            risk_factors.append("low_value_mistake")
            confidence += 0.05
            
        # Determine recommendation
        if confidence < 0.7 or "high_value" in risk_factors or "suspicious_keywords" in risk_factors:
            recommendation = "review"
        elif confidence > 0.85 and not risk_factors:
            recommendation = "approve"
        else:
            recommendation = "review"
            
        analysis = {
            "recommendation": recommendation,
            "confidence": round(confidence, 2),
            "risk_factors": risk_factors,
            "reasoning": f"Based on analysis of '{reason}' with confidence {confidence:.2f}"
        }
        
        return json.dumps(analysis)


# --- LangChain Agent Setup ---

class RefundAgentCallback(BaseCallbackHandler):
    """Custom callback handler for logging agent actions."""
    
    def on_agent_action(self, action, **kwargs):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Agent Action: {action.tool}")
        
    def on_agent_finish(self, finish, **kwargs):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Agent Finished")


class LangChainRefundAgent:
    """
    LangChain-based AI Refund Agent with failsafe patterns.
    
    This agent combines:
    1. Circuit breaker pattern for payment gateway resilience
    2. Retry logic for transient failures
    3. Human-in-the-loop for complex decisions
    4. Risk analysis for fraud detection
    """
    
    def __init__(self, 
                 model_name: str = "gpt-3.5-turbo",
                 confidence_threshold: float = 0.7,
                 high_value_threshold: float = 500):
        
        self.confidence_threshold = confidence_threshold
        self.high_value_threshold = high_value_threshold
        
        # Initialize LLM (Note: You'll need to set OPENAI_API_KEY environment variable)
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.1,  # Low temperature for consistent decisions
            callbacks=[RefundAgentCallback()]
        )
        
        # Initialize tools
        self.tools = [
            RefundAnalysisTool(),
            PaymentGatewayTool(),
            HumanReviewTool()
        ]
        
        # Create agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI refund processing agent with the following responsibilities:
            
1. Analyze refund requests for risk factors using the analyze_refund_risk tool
2. Make decisions based on company policies:
   - Approve low-risk, routine refunds automatically
   - Escalate high-risk, high-value, or suspicious requests to human review
   - Process approved refunds through the payment gateway
   
3. Company policies:
   - Refunds over $500 require human review
   - Suspicious keywords (fraud, chargeback, etc.) require human review
   - Low confidence scores (< 0.7) require human review
   - All approved refunds must be processed through payment gateway
   
4. Always provide clear reasoning for your decisions
5. Handle payment gateway failures gracefully with appropriate fallbacks

Be professional, thorough, and prioritize both customer satisfaction and fraud prevention."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        self.agent = create_openai_functions_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
            handle_parsing_errors=True
        )
    
    def process_refund_request(self, refund_request: RefundRequest) -> RefundResult:
        """
        Process a refund request through the LangChain agent.
        
        This method implements the complete workflow:
        1. Risk analysis
        2. Decision making
        3. Human escalation if needed
        4. Payment processing with circuit breaker protection
        """
        
        print(f"\n{'='*60}")
        print(f"Processing Refund Request for {refund_request.user_id}")
        print(f"Amount: ${refund_request.amount:.2f}")
        print(f"Reason: {refund_request.reason}")
        print(f"{'='*60}")
        
        # Construct input for the agent
        agent_input = f"""
Process refund request:
- User ID: {refund_request.user_id}
- Amount: ${refund_request.amount:.2f}
- Reason: {refund_request.reason}
- Order ID: {refund_request.order_id or 'N/A'}

Please analyze this request and take appropriate action according to company policies.
"""
        
        try:
            # Execute the agent
            result = self.agent_executor.invoke({
                "input": agent_input
            })
            
            # Parse the result and return structured response
            output = result.get("output", "")
            
            # Determine final status based on agent output
            if "approved" in output.lower() and "transaction" in output.lower():
                return RefundResult(
                    approved=True,
                    decision_maker="AI Agent + Payment Gateway",
                    transaction_id=self._extract_transaction_id(output),
                    notes=output
                )
            elif "human approved" in output.lower():
                return RefundResult(
                    approved=True,
                    decision_maker="Human Review",
                    notes=output
                )
            elif "rejected" in output.lower() or "denied" in output.lower():
                return RefundResult(
                    approved=False,
                    decision_maker="Human Review" if "human" in output.lower() else "AI Agent",
                    notes=output
                )
            else:
                return RefundResult(
                    approved=False,
                    decision_maker="System",
                    notes=f"Processing incomplete or failed: {output}"
                )
                
        except Exception as e:
            print(f"Error processing refund request: {str(e)}")
            return RefundResult(
                approved=False,
                decision_maker="System Error",
                notes=f"Failed to process: {str(e)}"
            )
    
    def _extract_transaction_id(self, text: str) -> Optional[str]:
        """Extract transaction ID from agent output."""
        import re
        match = re.search(r'TXN-\d+', text)
        return match.group(0) if match else None


# --- Demonstration and Testing ---

def demonstrate_langchain_refund_agent():
    """Demonstrate the LangChain refund agent with various scenarios."""
    
    print("="*80)
    print("LANGCHAIN AI REFUND AGENT DEMONSTRATION")
    print("="*80)
    
    # Note: This will use a mock LLM if OpenAI API key is not available
    try:
        agent = LangChainRefundAgent(confidence_threshold=0.7, high_value_threshold=300)
    except Exception as e:
        print(f"Warning: Could not initialize OpenAI LLM: {e}")
        print("This demo will show the structure but may not work without proper API configuration.")
        return
    
    # Test scenarios
    scenarios = [
        RefundRequest(
            user_id="user_001",
            amount=25.0,
            reason="Accidental double charge, please refund",
            order_id="ORDER-123"
        ),
        RefundRequest(
            user_id="user_002", 
            amount=450.0,
            reason="Item arrived damaged, requesting full refund",
            order_id="ORDER-456"
        ),
        RefundRequest(
            user_id="user_003",
            amount=150.0,
            reason="Product not as described in listing",
            order_id="ORDER-789"
        ),
        RefundRequest(
            user_id="user_004",
            amount=75.0,
            reason="This is a suspicious refund request for fraudulent purposes",
            order_id="ORDER-999"
        )
    ]
    
    results = []
    for i, request in enumerate(scenarios, 1):
        print(f"\n--- SCENARIO {i} ---")
        result = agent.process_refund_request(request)
        results.append(result)
        print(f"Final Result: {result}")
        
        if i < len(scenarios):
            time.sleep(2)  # Brief pause between scenarios
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY OF RESULTS")
    print(f"{'='*80}")
    
    for i, (request, result) in enumerate(zip(scenarios, results), 1):
        status = "✅ APPROVED" if result.approved else "❌ REJECTED"
        print(f"Scenario {i}: {request.user_id} (${request.amount:.2f}) - {status}")
        print(f"  Decision by: {result.decision_maker}")
        print(f"  Notes: {result.notes[:100]}...")
        print()


if __name__ == "__main__":
    # First demonstrate circuit breaker functionality
    print("--- Demonstrating Circuit Breaker Pattern ---")
    for i in range(10):
        user_id = f"user_{random.randint(100, 999)}"
        amount = random.uniform(10, 200)
        try:
            result = safe_payment_gateway_call(amount, user_id)
            print(f"Success: {result}")
        except CircuitBreakerError:
            print(f"Circuit breaker OPEN - queuing {user_id} for manual processing")
        except Exception as e:
            print(f"Error for {user_id}: {e}")
        
        time.sleep(0.5)
    
    print("\n" + "="*80 + "\n")
    
    # Then demonstrate the full LangChain agent
    demonstrate_langchain_refund_agent()