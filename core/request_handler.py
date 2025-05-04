import requests
from core.api_types import detect_api_type
from core.payload_builder import build_payload
from core.response_parser import parse_response

def send_llm_request(api_url, api_key, user_input, model):
    api_type = detect_api_type(api_url)
    payload = build_payload(api_type, user_input, model)
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    resp = requests.post(api_url, headers=headers, json=payload)
    resp.raise_for_status()
    return parse_response(api_type, resp.json())
