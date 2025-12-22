import os
from langchain_openai import AzureChatOpenAI, ChatOpenAI


LLM_PROVIDER = os.getenv("LLM_PROVIDER", "azure-openai").lower()  # "ollama" or "azure-openai"

# AzureOpenAI Configuration
AZURE_OPENAI_BASE_URL = os.getenv("AZURE_OPENAI_BASE_URL")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Local ollama models configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

print(f"""
LLM_PROVIDER: {LLM_PROVIDER}
AZURE_OPENAI_API_KEY: {AZURE_OPENAI_API_KEY}
AZURE_OPENAI_API_VERSION: {AZURE_OPENAI_API_VERSION}
AZURE_OPENAI_DEPLOYMENT: {AZURE_OPENAI_DEPLOYMENT}
""")

def create_llm_client():
    if LLM_PROVIDER == "azure-openai":
        client = AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_BASE_URL,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_deployment=AZURE_OPENAI_DEPLOYMENT,
            temperature=0.7,
            max_tokens=1000
        )

        return client
    elif LLM_PROVIDER == "ollama":
        client = ChatOpenAI(
            base_url=f"{OLLAMA_URL}/v1",
            api_key="ollama",  # Ollama doesn't require a real API key,
            model=OLLAMA_MODEL
        )

        return client
    else: 
        raise Exception("Cannot define the LLM provider")

