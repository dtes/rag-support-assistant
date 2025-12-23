"""
Tools node - executes API calls for operational data
"""
from agents.state import AgentState
from llm_client import create_llm_client
from tools.tool_definitions import FINANCE_TOOLS, set_user_context
from langchain_core.messages import AIMessage, ToolMessage

# Import observe decorator
try:
    from langfuse import observe
except ImportError:
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else args[0]


def call_tools(state: AgentState) -> AgentState:
    """
    Tools node: Use LLM with tool calling to get operational data

    Updates state with tool_results
    """
    query = state["user_query"]
    user_id = state["user_id"]

    print(f"[Tools] Processing query: {query}")

    # Set user context for tools
    set_user_context(user_id)

    # Create LLM with tools
    llm = create_llm_client()
    llm_with_tools = llm.bind_tools(FINANCE_TOOLS)

    # System prompt for tool calling
    system_prompt = """You are a financial assistant with access to real-time financial data.

Use the available tools to answer user questions about:
- Account balances
- Transactions (income/expenses)
- Financial reports (Cash Flow, Profit & Loss)
- Reference data (categories, counterparties)

Choose the appropriate tool(s) based on the user's question.
If multiple tools are needed, call them in sequence.

User's question:"""

    try:
        # First LLM call - decide which tools to use
        messages = [
            ("system", system_prompt),
            ("human", query)
        ]

        response = llm_with_tools.invoke(messages)

        # Check if LLM wants to call tools
        tool_results = []

        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"[Tools] LLM requested {len(response.tool_calls)} tool call(s)")

            # Execute each tool call
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']

                print(f"[Tools] Calling {tool_name} with args: {tool_args}")

                # Find and execute the tool
                tool_func = next((t for t in FINANCE_TOOLS if t.name == tool_name), None)

                if tool_func:
                    try:
                        result = tool_func.invoke(tool_args)
                        tool_results.append({
                            "tool": tool_name,
                            "args": tool_args,
                            "result": result
                        })
                        print(f"[Tools] {tool_name} executed successfully")
                    except Exception as e:
                        print(f"[Tools] Error executing {tool_name}: {e}")
                        tool_results.append({
                            "tool": tool_name,
                            "args": tool_args,
                            "error": str(e)
                        })
                else:
                    print(f"[Tools] Tool {tool_name} not found")

        state["tool_results"] = tool_results

        # Store tool usage in sources
        if tool_results:
            state["sources"] = [
                {"title": f"API: {r['tool']}", "filename": "Operational Data"}
                for r in tool_results
            ]

    except Exception as e:
        print(f"[Tools] Error: {e}")
        state["tool_results"] = []
        state["sources"] = []

    return state
