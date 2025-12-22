"""
Generator node - creates final answer from context
"""
from agents.state import AgentState
from llm_client import create_llm_client
import json

# Import observe decorator
try:
    from langfuse import observe
except ImportError:
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator if not args else args[0]


#@observe(name="generate_answer", as_type="generation")
def generate_answer(state: AgentState) -> AgentState:
    """
    Generator node: Create final answer from retrieved docs or tool results

    Updates state with answer
    """
    query = state["user_query"]
    query_type = state.get("query_type", "unknown")
    chat_history = state.get("chat_history", [])

    print(f"[Generator] Generating answer for: {query_type}")
    print(f"[Generator] Chat history length: {len(chat_history)}")

    llm = create_llm_client()

    # Build context based on query type
    if query_type == "documentation":
        # Use RAG documents
        docs = state.get("retrieved_docs", [])

        if not docs:
            state["answer"] = "Sorry, I could not find relevant information in the documentation."
            return state

        context = "\n\n---\n\n".join([
            f"Document: {doc['title']} ({doc['filename']})\n{doc['content']}"
            for doc in docs
        ])

        system_prompt = """You are a technical support AI assistant for a financial SaaS service.

Your task is to answer user questions based on the provided documentation.

Instructions:
1. Provide an accurate and helpful answer based ONLY on the provided documentation
2. If there is insufficient information, say so honestly
3. Answer in the same language as the user's question
4. Be concise and specific
5. Use a friendly, professional tone"""

        user_prompt = f"""Documentation:
{context}

User question: {query}

Please provide your answer:"""

    else:  # operational
        # Use tool results
        tool_results = state.get("tool_results", [])

        if not tool_results:
            state["answer"] = "Sorry, I could not retrieve the requested data."
            return state

        # Format tool results as context
        context_parts = []
        for result in tool_results:
            context_parts.append(f"Tool: {result['tool']}")
            if "result" in result:
                context_parts.append(f"Data: {json.dumps(result['result'], indent=2, ensure_ascii=False)}")
            elif "error" in result:
                context_parts.append(f"Error: {result['error']}")

        context = "\n\n".join(context_parts)

        system_prompt = """You are a financial assistant AI for a financial SaaS service.

Your task is to answer user questions based on real-time operational data from the system.

Instructions:
1. Analyze the data from API calls and provide a clear, human-friendly answer
2. Format numbers nicely (use thousands separators, appropriate currency symbols)
3. Highlight key insights and trends
4. Answer in the same language as the user's question
5. Be concise but informative
6. Use a friendly, professional tone"""

        user_prompt = f"""API Data:
{context}

User question: {query}

Please provide your answer based on the data:"""

    try:
        # Build messages with chat history
        messages = [("system", system_prompt)]

        # Add chat history (last 10 messages for context)
        if chat_history:
            messages.extend(chat_history[-10:])

        # Add current user query
        messages.append(("human", user_prompt))

        # Generate answer
        response = llm.invoke(messages)

        state["answer"] = response.content

        print(f"[Generator] Answer generated ({len(response.content)} chars)")

    except Exception as e:
        print(f"[Generator] Error: {e}")
        state["answer"] = f"An error occurred while generating the answer: {str(e)}"

    return state
