from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI

# ----------------------
# 1️⃣ Define tools dynamically
# ----------------------


# Tool function: performs a web search
def search_web(query: str) -> str:
    return f"Simulated search result for: {query}"


# Tool function: performs math evaluation
def calculate_math(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception:
        return "Invalid expression"


# Wrap functions as LangChain Tools
search_tool = Tool(
    name="SearchTool",
    func=search_web,  # method-level dynamic dispatch: agent will call this dynamically
    description="Search the web for a query",
)

math_tool = Tool(
    name="MathTool",
    func=calculate_math,  # method-level dynamic dispatch happens here too
    description="Evaluate a math expression",
)

tools = [search_tool, math_tool]  # tools are registered dynamically

# ----------------------
# 2️⃣ Initialize the agent
# ----------------------
llm = OpenAI(temperature=0)  # Using OpenAI LLM
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

# ----------------------
# 3️⃣ Dynamic tool invocation
# ----------------------
queries = ["2 + 2", "Python AI frameworks"]

for query in queries:
    # ----------------------
    # Layer 1: Tool selection dispatch
    # ----------------------
    # The agent uses its reasoning (LLM + logic) to pick the right tool
    # It does NOT need to know upfront which tool is required
    result = agent.run(query)

    # ----------------------
    # Layer 2: Method-level dynamic dispatch
    # ----------------------
    # Once the agent selects a tool, Python dynamically dispatches
    # to the correct 'func' method of that tool
    print(f"Query: {query} -> Result: {result}")
