def build_payload(api_type, user_input, model=None):
    if api_type == "openai":
        return {
            "model": model or "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": user_input}],
            "temperature": 0.7
        }
    elif api_type == "gemini":
        return {"contents": [{"parts": [{"text": user_input}]}]}
    elif api_type == "ollama":
        return {"model": model or "llama2", "prompt": user_input}
    else:
        raise ValueError(f"Unknown API type: {api_type}")
