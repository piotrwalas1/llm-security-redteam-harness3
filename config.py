import os
import time
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

class LLMClient:
    def __init__(self, model: str = "gemini-2.5-flash", rate_limit_delay: float = 0.2):
        self.model_name = model
        self.rate_limit_delay = rate_limit_delay
        
        self.project_id = os.getenv("GCP_PROJECT_ID", "")
        self.location = os.getenv("GCP_LOCATION", "us-central1")
        self.target_url = os.getenv("TARGET_API_URL", "http://127.0.0.1:8000/api/v1/evaluate")
        
        # Inicjalizacja oryginalnego klienta Vertex AI (będzie używany przez Sędziego)
        self.genai_client = genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.location
        )

    def generate(self, prompt: str, max_retries: int = 5, temperature: float = 0.7) -> str:
        """
        Inteligentnie rozdziela ruch:
        - Jeśli pyta Sędzia (Judge) -> odpytujemy prawdziwe Vertex AI (Gemini) po JSON-a z oceną.
        - Jeśli atakuje Harness -> wysyłamy prompt do Twojego lokalnego FastAPI.
        """
        
        # Rozpoznajemy, czy to zapytanie od Sędziego (SecurityEvaluator pyta o ocenę i JSON-a)
        is_judge_request = "Jesteś ekspertem ds. cyberbezpieczeństwa" in prompt or "Wykonaj ocenę" in prompt
        
        if is_judge_request:
            # --- ROLA SĘDZIEGO: Prawdziwe zapytanie do Google GenAI ---
            config = types.GenerateContentConfig(
                temperature=0.0, # Sędzia musi być deterministyczny
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
            )
            
            for attempt in range(1, max_retries + 1):
                try:
                    response = self.genai_client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=config
                    )
                    time.sleep(self.rate_limit_delay)
                    return response.text if response.text else ""
                except Exception as e:
                    print(f"\n[!] Błąd Sędziego Vertex AI: {e}")
                    time.sleep(2)
            return '{"score": 0, "status": "ERROR", "reason": "Błąd Sędziego po przekroczeniu limitów."}'
            
        else:
            # --- ROLA TARGETU: Wysyłamy prompt do Twoich lokalnych agentów FastAPI ---
            for attempt in range(1, max_retries + 1):
                try:
                    response = requests.post(
                        self.target_url,
                        json={"prompt": prompt},
                        timeout=700
                    )
                    
                    time.sleep(self.rate_limit_delay)
                    
                    if response.status_code == 200:
                        data = response.json()
                        is_attack = data.get("is_attack", False)
                        reason = data.get("threat_reason", "")
                        
                        if is_attack:
                            return f"Odmowa dostępu. Żądanie zostało zablokowane ze względów bezpieczeństwa: {reason}"
                        
                        review_status = data.get("review_status", "APPROVED")
                        return f"Wykonano polecenie użytkownika. Status agentów: {review_status}."
                    else:
                        print(f"\n[!] Błąd API lokalnego serwera: Status {response.status_code}")
                        time.sleep(2)
                        
                except requests.exceptions.ConnectionError:
                    print(f"\n[!] Błąd połączenia z targetem: Upewnij się, że app.py działa!")
                    time.sleep(5)
                except Exception as e:
                    print(f"\n[!] Błąd komunikacji: {e}")
                    time.sleep(2)

            return "Przekroczono limit czasu oczekiwania na odpowiedź systemu."