import json, os, time
from pydantic import BaseModel, ValidationError
from google import genai
from google.genai import types
class GeminiProvider:
    def __init__(self, api_key: str, model: str): self.api_key, self.model, self.client = api_key, model, genai.Client(api_key=api_key)
    def close(self):
        if self.client: self.client.close(); self.client = None
    def _send(self, system_prompt: str, user_prompt: str, mime: str) -> str:
        last = None
        max_attempts = int(os.getenv("GEMINI_MAX_ATTEMPTS", "3"))
        base_backoff = float(os.getenv("GEMINI_RETRY_BASE_SECONDS", "5"))
        for attempt in range(max_attempts):
            try:
                if not self.client: raise RuntimeError("Gemini client is closed")
                chat = self.client.chats.create(model=self.model, config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.2, response_mime_type=mime))
                response = chat.send_message(user_prompt)
                if not response.text: raise RuntimeError("Gemini returned an empty response")
                return response.text
            except Exception as error:
                last = error
                code = getattr(error, "status", None) or getattr(error, "code", None)
                if code not in (429, 500, 503) or attempt == max_attempts - 1: break
                # 429 is quota/rate limiting; 503 is temporary service capacity.
                delay = min(base_backoff * (2 ** attempt) * (3 if code == 429 else 1), 60)
                time.sleep(delay)
        raise RuntimeError(f"Gemini request failed after {max_attempts} attempts: {last}")
    def generate_text(self, *, system_prompt: str, user_prompt: str) -> str: return self._send(system_prompt, user_prompt, "text/plain")
    def generate_structured(self, *, system_prompt: str, user_prompt: str, schema: type[BaseModel]) -> BaseModel:
        raw = self._send(system_prompt, user_prompt, "application/json")
        for repair in range(2):
            try: return schema.model_validate(json.loads(raw))
            except (json.JSONDecodeError, ValidationError) as error:
                if repair: raise RuntimeError(f"Gemini returned invalid {schema.__name__} JSON: {error}") from error
                repair_prompt = "Schema: " + json.dumps(schema.model_json_schema()) + "\nInvalid response: " + raw
                raw = self._send("Repair JSON only. Return an object that validates this schema; do not add prose.", repair_prompt, "application/json")
        raise AssertionError("unreachable")
