from core.request_handler import send_llm_request

def generate_project_plan(api_url, api_key, project_desc, model):
    prompt = (
        f"Erstelle eine detaillierte, schrittweise Projektplanung für folgendes Projekt:\n"
        f"{project_desc}\n"
        "Nutze klare Überschriften und nummerierte Schritte."
    )
    return send_llm_request(api_url, api_key, prompt, model)
