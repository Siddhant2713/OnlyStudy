import json, time
from pydantic import BaseModel, ValidationError
from google import genai
from google.genai import types
class GeminiProvider:
    def __init__(self, api_key: str, model: str): self.api_key, self.model = api_key, model
    def _send(self, system_prompt: str, user_prompt: str, mime: str) -> str:
        last = None
        for attempt in range(3):
            client = None
            try:
                client = genai.Client(api_key=self.api_key)
                chat = client.chats.create(model=self.model, config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.2, response_mime_type=mime))
                response = chat.send_message(user_prompt)
                if not response.text: raise RuntimeError("Gemini returned an empty response")
                return response.text
            except Exception as error:
                last = error
                if (getattr(error, "status", None) or getattr(error, "code", None)) not in (429, 500, 503) or attempt == 2: break
                time.sleep(2 ** attempt)
            finally:
                if client is not None: client.close()
        raise RuntimeError(f"Gemini request failed: {last}")
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
