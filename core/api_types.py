def detect_api_type(api_url: str) -> str:
    if "openai.com" in api_url:
        return "openai"
    elif "generativelanguage.googleapis.com" in api_url:
        return "gemini"
    elif "localhost" in api_url or "ollama" in api_url:
        return "ollama"
    else:
        return "unknown"
