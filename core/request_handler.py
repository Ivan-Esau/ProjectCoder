"""
core/request_handler.py

Dieses Modul stellt eine Funktion bereit, um eine Anfrage über die
Model Context Protocol (MCP) zu senden.
"""

import requests
from mcp.types import CallToolRequestParams, JSONRPCRequest, CallToolResult


def send_llm_request(
    api_url: str,
    api_key: str,
    user_input: str,
    model: str
):
    """
    Sendet eine Anfrage an die angegebene LLM-API und gibt die geparste Antwort zurück.

    Der Ablauf:
      1. Zusammenstellung einer MCP "tools/call" Anfrage.
      2. Absenden des HTTP-POST-Requests.
      3. Fehlerbehandlung bei HTTP-Statuscodes >= 400.
      4. Extraktion des Textes aus dem MCP Ergebnis.

    Args:
        api_url (str): MCP-Endpunkt.
        api_key (str): API-Schlüssel für die Authentifizierung. Wenn leer, wird keine Authorization-Header gesetzt.
        user_input (str): Der Eingabetext, der an das LLM gesendet wird.
        model (str): Modellname, der im Payload verwendet werden soll (z. B. "gpt-4" oder "llama2").

    Returns:
        str: Der extrahierte Text des Tools.

    Raises:
        requests.HTTPError: Wenn der HTTP-Statuscode des API-Responses auf einen Fehler hinweist.
        KeyError / TypeError: Wenn das erwartete Format der API-Antwort nicht vorliegt.
    """
    # 1. Payload bauen
    request_obj = JSONRPCRequest(
        jsonrpc="2.0",
        id=1,
        method="tools/call",
        params=CallToolRequestParams(
            name="generateText",
            arguments={"prompt": user_input, "model": model},
        ).model_dump(),
    )

    payload = request_obj.model_dump()

    # 2. Header zusammenstellen
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # 3. Anfrage senden und auf HTTP-Fehler prüfen
    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()

    # 4. Antwort parsen und zurückgeben
    data = response.json()
    result = CallToolResult.model_validate(data.get("result", {}))
    text = "".join(
        part.text for part in result.content if getattr(part, "type", None) == "text"
    )
    return text
