"""
LLM Client Factory - clean infrastructure component
No env reading, all configuration passed via settings object
"""
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from config.settings import LLMSettings


def create_llm_client(llm_settings: LLMSettings):
    """
    Create LLM client based on settings

    Args:
        llm_settings: LLMSettings configuration object

    Returns:
        LLM client instance

    Raises:
        ValueError: If provider is unknown or required settings are missing
    """
    provider = llm_settings.provider.lower()

    if provider == "azure-openai":
        if not all([
            llm_settings.azure_endpoint,
            llm_settings.azure_api_key,
            llm_settings.azure_api_version,
            llm_settings.azure_deployment
        ]):
            raise ValueError(
                "Azure OpenAI provider requires: azure_endpoint, azure_api_key, "
                "azure_api_version, azure_deployment"
            )

        print(f"✓ Creating Azure OpenAI client (deployment: {llm_settings.azure_deployment})")
        return AzureChatOpenAI(
            azure_endpoint=llm_settings.azure_endpoint,
            api_key=llm_settings.azure_api_key,
            api_version=llm_settings.azure_api_version,
            azure_deployment=llm_settings.azure_deployment,
            temperature=llm_settings.temperature,
            max_tokens=llm_settings.max_tokens
        )

    elif provider == "openai":
        if not llm_settings.api_key:
            raise ValueError("OpenAI provider requires: api_key")

        print(f"✓ Creating OpenAI client (model: {llm_settings.model})")
        return ChatOpenAI(
            api_key=llm_settings.api_key,
            model=llm_settings.model or "gpt-4",
            temperature=llm_settings.temperature,
            max_tokens=llm_settings.max_tokens
        )

    elif provider == "ollama":
        print(f"✓ Creating Ollama client (model: {llm_settings.ollama_model})")
        return ChatOpenAI(
            base_url=f"{llm_settings.ollama_url}/v1",
            api_key="ollama",  # Ollama doesn't require a real API key
            model=llm_settings.ollama_model,
            temperature=llm_settings.temperature,
            max_tokens=llm_settings.max_tokens
        )

    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. "
            f"Supported providers: azure-openai, openai, ollama"
        )
