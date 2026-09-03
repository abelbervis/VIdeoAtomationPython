"""
AI Script Generator for Vertical Science Shorts.
Generates structured JSON scripts divided into scenes with narration and targeted NASA search keywords.
Supports Google Gemini, OpenAI, and a reliable factual scientific generator fallback.
"""

import json
import os
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

from config import (
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_API_BASE,
    LLM_PROVIDER,
    LLM_API_BASE_URL
)


SYSTEM_PROMPT = """You are an elite science communicator writing punchy, viral YouTube Shorts and TikTok documentary scripts.
Target duration: 30 to 45 seconds.

Rules:
1. Start with an irresistible 3-second hook that challenges common intuition.
2. Absolutely NO generic greetings (Never say 'Hola amigos', 'En este video', 'Bienvenidos').
3. Keep the narration fast-paced, accurate, engaging, and based strictly on verifiable facts and science.
4. End with a memorable, mind-blowing closing thought or punchline.
5. Divide the script into 4 to 6 distinct visual scenes.
6. Provide specific search keywords IN ENGLISH for each scene to query media libraries (Pexels, NASA). Keywords should describe exact visual actions (e.g. 'ocean waves aerial', 'deep space galaxy', 'brain neurons firing').
7. Preferred visual types: "video" for motion scenes, "image" for high-detail captures.

Respond ONLY with valid JSON matching this schema:
{
  "title": "Short title",
  "hook": "Opening hook sentence",
  "scenes": [
    {
      "scene_id": 1,
      "narration": "Narration text in the requested language (e.g. Spanish)",
      "keywords": ["specific english keyword 1", "specific keyword 2"],
      "visual_type": "video",
      "estimated_duration": 7
    }
  ]
}
"""


class ScriptGenerator:
    """Generates structured science video scripts via Groq, Gemini, or OpenAI."""

    def __init__(
        self,
        gemini_key: Optional[str] = None,
        openai_key: Optional[str] = None,
        groq_key: Optional[str] = None,
        groq_model: str = GROQ_MODEL,
        groq_api_base: str = GROQ_API_BASE,
        preferred_provider: str = LLM_PROVIDER,
        base_url: Optional[str] = None,
    ):
        raw_gemini = gemini_key if gemini_key is not None else GEMINI_API_KEY
        raw_openai = openai_key if openai_key is not None else OPENAI_API_KEY
        raw_groq = groq_key if groq_key is not None else GROQ_API_KEY

        self.gemini_key = str(raw_gemini or "").strip().strip("'\"").strip()
        self.openai_key = str(raw_openai or "").strip().strip("'\"").strip()
        self.groq_key = str(raw_groq or "").strip().strip("'\"").strip()
        self.groq_model = (groq_model or "llama-3.3-70b-versatile").strip().strip("'\"").strip()
        self.groq_api_base = (groq_api_base or "https://api.groq.com/openai/v1").rstrip("/")
        self.provider = (preferred_provider or "auto").lower().strip()

        raw_url = str(base_url if base_url is not None else LLM_API_BASE_URL).strip().strip("'\"").strip()
        self.base_url = raw_url if raw_url.startswith("http") else ""

    def _is_valid_api_key(self, key: str) -> bool:
        """Check if an API key looks like an actual valid key and not a dummy placeholder."""
        if not key or len(key) < 15:
            return False
        placeholders = [
            "my_gemini_api_key", "tu_clave", "your_key", "demo_key",
            "sk-...", "placeholder", "xxx", "your_groq_key", "your_openai_key"
        ]
        return not any(p in key.lower() for p in placeholders)

    def generate(self, topic: str, target_duration: int = 35) -> Optional[Dict[str, Any]]:
        """Generate a structured script for the given topic using configured AI providers."""
        print(f"\n🧠 Generating script for: '{topic}' (~{target_duration}s)...")

        # Specific provider selected
        if self.provider == "groq":
            if not self._is_valid_api_key(self.groq_key):
                print("  ❌ Error: Se especificó el proveedor 'groq' pero no se configuró una GROQ_API_KEY válida.")
                print("     👉 Obtén tu clave gratuita en https://console.groq.com/keys y agrégala a tu .env o usa --groq-key.")
                return None
            script = self._generate_groq(topic, target_duration)
            if not script:
                print("  ❌ Error: Falló la generación del guión con la API de Groq.")
            return script

        if self.provider == "gemini":
            if not self._is_valid_api_key(self.gemini_key):
                print("  ❌ Error: Se especificó el proveedor 'gemini' pero no se configuró una GEMINI_API_KEY válida.")
                print("     👉 Obtén tu clave en https://aistudio.google.com/ y agrégala a tu .env o usa --gemini-key.")
                return None
            script = self._generate_gemini(topic, target_duration)
            if not script:
                print("  ❌ Error: Falló la generación del guión con la API de Gemini.")
            return script

        if self.provider == "openai":
            if not self._is_valid_api_key(self.openai_key):
                print("  ❌ Error: Se especificó el proveedor 'openai' pero no se configuró una OPENAI_API_KEY válida.")
                print("     👉 Obtén tu clave en https://platform.openai.com/ y agrégala a tu .env o usa --openai-key.")
                return None
            script = self._generate_openai(topic, target_duration)
            if not script:
                print("  ❌ Error: Falló la generación del guión con la API de OpenAI.")
            return script

        # Auto mode: try configured providers in priority order (Groq -> Gemini -> OpenAI)
        configured_providers = []
        if self._is_valid_api_key(self.groq_key):
            configured_providers.append("groq")
        if self._is_valid_api_key(self.gemini_key):
            configured_providers.append("gemini")
        if self._is_valid_api_key(self.openai_key):
            configured_providers.append("openai")

        if not configured_providers:
            print("  ❌ Error: No hay ninguna API de IA configurada para generar el guión.")
            print("     👉 Debes configurar al menos una clave en tu archivo .env o pasarla por terminal:")
            print("        • GROQ_API_KEY   (https://console.groq.com/keys) o parámetro --groq-key")
            print("        • GEMINI_API_KEY (https://aistudio.google.com/) o parámetro --gemini-key")
            print("        • OPENAI_API_KEY (https://platform.openai.com/) o parámetro --openai-key")
            return None

        for prov in configured_providers:
            if prov == "groq":
                print("  ⚡ Solicitando guión ultrarrápido a Groq LPU...")
                script = self._generate_groq(topic, target_duration)
                if script:
                    return script
            elif prov == "gemini":
                print("  ⚡ Solicitando guión a Google Gemini...")
                script = self._generate_gemini(topic, target_duration)
                if script:
                    return script
            elif prov == "openai":
                print("  ⚡ Solicitando guión a OpenAI...")
                script = self._generate_openai(topic, target_duration)
                if script:
                    return script

        print(f"  ❌ Error: Todas las APIs de IA configuradas ({', '.join(configured_providers)}) fallaron al generar el guión.")
        return None

    def _generate_groq(self, topic: str, target_duration: int) -> Optional[Dict[str, Any]]:
        """Call Groq API via REST (OpenAI-compatible LPU inference)."""
        try:
            endpoint = f"{self.groq_api_base}/chat/completions"
            payload = {
                "model": self.groq_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"Topic: {topic}\n"
                            f"Target duration: {target_duration} seconds.\n"
                            f"Language: Spanish (unless topic is strictly in another language).\n"
                            f"Generate the JSON script:"
                        )
                    }
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.4
            }

            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.groq_key}",
                    "User-Agent": "NASA-Shorts-Generator/1.0"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["choices"][0]["message"]["content"]
                return self._parse_json_response(text)
        except urllib.error.HTTPError as e:
            err_body = ""
            err_msg = ""
            try:
                err_body = e.read().decode("utf-8")
                err_data = json.loads(err_body)
                err_info = err_data.get("error", {})
                if isinstance(err_info, dict):
                    err_msg = err_info.get("message", "")
                elif isinstance(err_info, str):
                    err_msg = err_info
            except Exception:
                pass

            if "Invalid API Key" in err_body or e.code == 401:
                print("  ❌ Groq API Error: Clave GROQ_API_KEY no válida o incorrecta.")
                print("     👉 Revisa o genera tu clave gratuita en https://console.groq.com/keys")
            elif e.code == 429:
                print("  ❌ Groq API Error (429 Rate Limit): Límite de tasa excedido en Groq.")
            elif "model" in err_body.lower() and (e.code == 400 or e.code == 404):
                print(f"  ❌ Groq API Error: Modelo '{self.groq_model}' no encontrado o no soportado en Groq.")
                print("     👉 Modelos recomendados: llama-3.3-70b-versatile, llama-3.1-8b-instant")
            else:
                detail = f": {err_msg}" if err_msg else f" ({e.reason})"
                print(f"  ⚠️ Groq API HTTP Error {e.code}{detail}")
            return None
        except Exception as e:
            print(f"  ⚠️ Groq API request error: {e}")
            return None

    def _generate_gemini(self, topic: str, target_duration: int) -> Optional[Dict[str, Any]]:
        """Call Gemini API via REST."""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"Topic: {topic}\n"
                f"Target duration: {target_duration} seconds.\n"
                f"Language: Spanish (unless topic is strictly in another language).\n"
                f"Generate the JSON script:"
            )

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.4,
                    "responseMimeType": "application/json"
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=25) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return self._parse_json_response(text)
        except urllib.error.HTTPError as e:
            if e.code == 400:
                print(f"  ⚠️ Gemini API Error (400 Bad Request): Parámetros o clave inválida.")
            elif e.code in (401, 403):
                print(f"  ⚠️ Gemini API Error ({e.code} Unauthorized): Clave GEMINI_API_KEY no válida.")
            elif e.code == 404:
                print(f"  ⚠️ Gemini API Error (404 Not Found): Modelo no encontrado.")
            elif e.code == 429:
                print(f"  ⚠️ Gemini API Error (429 Rate Limit): Cuota de uso excedida.")
            else:
                print(f"  ⚠️ Gemini API request failed ({e})")
            return None
        except Exception as e:
            print(f"  ⚠️ Gemini API request failed ({e})")
            return None

    def _generate_openai(self, topic: str, target_duration: int) -> Optional[Dict[str, Any]]:
        """Call OpenAI API or custom endpoint."""
        try:
            endpoint = self.base_url if (self.base_url and self.base_url.startswith("http")) else "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Topic: {topic}. Target duration: {target_duration}s. Generate JSON script."}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.4
            }

            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_key}"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=25) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["choices"][0]["message"]["content"]
                return self._parse_json_response(text)
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("  ⚠️ OpenAI API Error (401 Unauthorized): OPENAI_API_KEY inválida.")
            elif e.code == 429:
                print("  ⚠️ OpenAI API Error (429 Rate Limit): Cuota excedida.")
            else:
                print(f"  ⚠️ OpenAI API HTTP Error {e.code}: {e.reason}")
            return None
        except Exception as e:
            print(f"  ⚠️ OpenAI API request failed ({e})...")
            return None

    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Clean markdown wrapping and validate JSON structure."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)

        try:
            data = json.loads(text)
            if "scenes" in data and isinstance(data["scenes"], list) and len(data["scenes"]) > 0:
                return data
        except Exception as e:
            print(f"  ⚠️ JSON parse error: {e}")
        return None
