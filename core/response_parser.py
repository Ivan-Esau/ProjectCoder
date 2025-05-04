def parse_response(api_type, response_json):
    try:
        if api_type == "openai":
            return response_json["choices"][0]["message"]["content"]
        elif api_type == "gemini":
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        elif api_type == "ollama":
            return response_json["response"]
        else:
            return str(response_json)
    except Exception as e:
        return f"[Parse error]: {e}"
