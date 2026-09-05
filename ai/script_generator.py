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
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from config import (
    BASE_DIR,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_API_BASE,
    LLM_PROVIDER,
    LLM_API_BASE_URL,
    SYSTEM_PROMPT_FILE,
    SYSTEM_PROMPT_PATH,
    sanitize_env_value
)


DEFAULT_SYSTEM_PROMPT = """You are a world-class science documentary director and viral storyteller crafting premium scripts for YouTube Shorts and TikTok.
Target duration: 30 to 45 seconds (approx. 70-95 total spoken words).

CRITICAL NARRATIVE RULES:
1. THE 3-SECOND HOOK:
   - Start immediately with a provocative contradiction, high-stakes question, or shocking fact.
   - Absolutely NO pleasantries or generic filler (NEVER say "Hola amigos", "En este video", "Bienvenidos", "Alguna vez te has preguntado", "Hello guys"). Jump directly into the core mystery.

2. RHYTHM & SCENE BREVITY (Shorts & Subtitles Optimized):
   - Divide the script into 4 to 5 distinct visual scenes.
   - STRICT LIMIT: 14 to 18 words maximum per scene. Use short, punchy, active sentences.
   - Avoid complex subordinate clauses. Insert punctuation (. and ;) so the voice synthesizer takes natural pauses.

3. TTS & PHONETIC CLARITY (Spoken Natural Voice):
   - NEVER use acronyms or abbreviations in parentheses (e.g. NEVER write "(CME)", "(JWST)", "(GPS)", "(NASA)").
   - Use natural spoken equivalents: say "eyección solar" instead of "CME", "telescopio espacial" instead of "JWST", "nave espacial" or "satélites de navegación".
   - Write numbers and units in simple natural form (e.g. "mil seiscientos kilómetros por hora", "millones de grados") so text-to-speech speaks them with flawless human cadence.

4. MEDIA SEARCH KEYWORDS (High-Stock Hit Rate):
   - Provide 2 to 3 visual search keywords per scene ALWAYS IN ENGLISH.
   - Keywords MUST describe literal, concrete, cinematic actions that real media libraries (NASA, Pexels) actually have in abundance.
   - BANNED KEYWORDS: DO NOT use abstract words like "glitch", "concept art", "infographic", "artist impression", "future illustration", "3d model".
   - RECOMMENDED KEYWORDS: Use concrete nouns and motion verbs (e.g. "satellite orbiting earth", "solar flare eruption", "city blackout night", "aurora borealis timelapse", "telescope space", "deep space galaxy").
   - Set "visual_type": "video" for motion scenes, "image" for historical events, deep field space, or macro photography.

5. DRAMATIC 5-STEP ARC:
   - Scene 1 (Visual Setup): Cosmic scale or sudden tension.
   - Scene 2 (The Mechanism): The invisible physical trigger in action.
   - Scene 3 (The Impact): Direct clash with Earth, technology, or human perception.
   - Scene 4 (Historical Proof / Scale): A tangible historical precedent, experiment, or mind-blowing comparison.
   - Scene 5 (Climactic Closing Thought): A striking punchline or lingering thought that prompts comments and shares.

Respond ONLY with valid JSON matching this schema:
{
  "title": "Short punchy title",
  "hook": "Opening hook sentence",
  "scenes": [
    {
      "scene_id": 1,
      "narration": "Short, punchy narration in target language (14-18 words max)",
      "keywords": ["concrete english keyword 1", "concrete english keyword 2"],
      "visual_type": "video",
      "estimated_duration": 7
    }
  ]
}
"""


def load_system_prompt(custom_path: Optional[str] = None) -> Tuple[str, str]:
    """
    Load system prompt from an external file (ignored in git),
    falling back to example files or embedded default prompt.
    Returns (prompt_text, source_description).
    """
    candidates = []
    if custom_path:
        p = Path(custom_path)
        candidates.append((p, f"custom path '{custom_path}'"))
        if not p.is_absolute():
            candidates.append((BASE_DIR / custom_path, f"custom path '{custom_path}'"))

    # Configured path from env/config
    if SYSTEM_PROMPT_PATH:
        candidates.append((SYSTEM_PROMPT_PATH, f"'{SYSTEM_PROMPT_FILE}'"))

    # Standard default paths (ignored in git)
    candidates.extend([
        (BASE_DIR / "system_prompt.txt", "system_prompt.txt"),
        (BASE_DIR / "prompts" / "system_prompt.txt", "prompts/system_prompt.txt"),
        (Path("system_prompt.txt"), "system_prompt.txt"),
        # Fallbacks to examples if main file is absent
        (BASE_DIR / "system_prompt.txt.example", "system_prompt.txt.example"),
        (BASE_DIR / "prompts" / "system_prompt.txt.example", "prompts/system_prompt.txt.example"),
    ])

    for path, desc in candidates:
        try:
            if path.is_file() and path.stat().st_size > 0:
                content = path.read_text(encoding="utf-8").strip()
                if content:
                    return content, desc
        except Exception:
            continue

    return DEFAULT_SYSTEM_PROMPT.strip(), "embedded default"


# Global default for convenience
SYSTEM_PROMPT, DEFAULT_PROMPT_SOURCE = load_system_prompt()


def get_language_instructions(language: str) -> Tuple[str, str]:
    """Return language label and specific prompt directives for the LLM."""
    lang = (language or "es").lower().strip()
    if lang == "en":
        return (
            "English",
            "The narration and title MUST be written in natural, punchy, fluent English for viral shorts.\n"
            "Visual search keywords MUST also be in English."
        )
    elif lang in ("zh", "zh-cn", "chinese"):
        return (
            "Simplified Chinese (Mandarin / 中文简体)",
            "The entire narration and title MUST be written in natural, fluent Simplified Chinese (中文简体), "
            "crafted for high-retention viral short videos.\n"
            "CRITICAL: The visual search 'keywords' for NASA and Pexels MUST ALWAYS BE IN ENGLISH "
            "(e.g. ['deep space nebula', 'mars surface', 'black hole event horizon']) so the media search succeeds!"
        )
    else:
        return (
            "Spanish (Español)",
            "The entire narration and title MUST be written in natural, fluent Spanish (Español).\n"
            "The visual search 'keywords' for NASA and Pexels MUST ALWAYS BE IN ENGLISH "
            "(e.g. ['saturn rings', 'supernova explosion']) so the media search succeeds!"
        )


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
        prompt_file: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        raw_gemini = gemini_key if gemini_key is not None else GEMINI_API_KEY
        raw_openai = openai_key if openai_key is not None else OPENAI_API_KEY
        raw_groq = groq_key if groq_key is not None else GROQ_API_KEY

        self.gemini_key = sanitize_env_value(raw_gemini)
        self.openai_key = sanitize_env_value(raw_openai)
        self.groq_key = sanitize_env_value(raw_groq)
        raw_model = sanitize_env_value(groq_model)
        self.groq_model = raw_model if raw_model else "llama-3.3-70b-versatile"
        self.groq_api_base = (sanitize_env_value(groq_api_base) or "https://api.groq.com/openai/v1").rstrip("/")
        self.provider = (sanitize_env_value(preferred_provider) or "auto").lower()

        raw_url = sanitize_env_value(base_url if base_url is not None else LLM_API_BASE_URL)
        self.base_url = raw_url if raw_url.startswith("http") else ""

        if system_prompt and system_prompt.strip():
            self.system_prompt = system_prompt.strip()
            self.prompt_source = "explicit text"
        else:
            self.system_prompt, self.prompt_source = load_system_prompt(prompt_file)

    def _is_valid_api_key(self, key: str) -> bool:
        """Check if an API key looks like an actual valid key and not a dummy placeholder."""
        if not key or len(key) < 15:
            return False
        placeholders = [
            "my_gemini_api_key", "tu_clave", "your_key", "demo_key",
            "sk-...", "placeholder", "xxx", "your_groq_key", "your_openai_key"
        ]
        return not any(p in key.lower() for p in placeholders)

    def generate(
        self,
        topic: str,
        target_duration: int = 35,
        language: str = "es",
        context_text: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Generate a structured script for the given topic using configured AI providers."""
        lang_label, _ = get_language_instructions(language)
        context_note = " + Grounded NASA context" if context_text else ""
        print(f"\n🧠 Generating script for: '{topic}' (~{target_duration}s, Language: {lang_label}, System Prompt: {self.prompt_source}{context_note})...")

        # Specific provider selected
        if self.provider == "groq":
            if not self._is_valid_api_key(self.groq_key):
                print("  ❌ Error: Se especificó el proveedor 'groq' pero no se configuró una GROQ_API_KEY válida.")
                print("     👉 Obtén tu clave gratuita en https://console.groq.com/keys y agrégala a tu .env o usa --groq-key.")
                return None
            script = self._generate_groq(topic, target_duration, language, context_text)
            if not script:
                print("  ❌ Error: Falló la generación del guión con la API de Groq.")
            return script

        if self.provider == "gemini":
            if not self._is_valid_api_key(self.gemini_key):
                print("  ❌ Error: Se especificó el proveedor 'gemini' pero no se configuró una GEMINI_API_KEY válida.")
                print("     👉 Obtén tu clave en https://aistudio.google.com/ y agrégala a tu .env o usa --gemini-key.")
                return None
            script = self._generate_gemini(topic, target_duration, language, context_text)
            if not script:
                print("  ❌ Error: Falló la generación del guión con la API de Gemini.")
            return script

        if self.provider == "openai":
            if not self._is_valid_api_key(self.openai_key):
                print("  ❌ Error: Se especificó el proveedor 'openai' pero no se configuró una OPENAI_API_KEY válida.")
                print("     👉 Obtén tu clave en https://platform.openai.com/ y agrégala a tu .env o usa --openai-key.")
                return None
            script = self._generate_openai(topic, target_duration, language, context_text)
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
                script = self._generate_groq(topic, target_duration, language, context_text)
                if script:
                    return script
            elif prov == "gemini":
                print("  ⚡ Solicitando guión a Google Gemini...")
                script = self._generate_gemini(topic, target_duration, language, context_text)
                if script:
                    return script
            elif prov == "openai":
                print("  ⚡ Solicitando guión a OpenAI...")
                script = self._generate_openai(topic, target_duration, language, context_text)
                if script:
                    return script

        print(f"  ❌ Error: Todas las APIs de IA configuradas ({', '.join(configured_providers)}) fallaron al generar el guión.")
        return None

    def _call_groq_api(
        self,
        model: str,
        topic: str,
        target_duration: int,
        language: str = "es",
        context_text: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[int], str, str]:
        """Execute a single REST call to Groq API. Returns (script_dict, status_code, err_code, err_msg)."""
        lang_name, lang_guidance = get_language_instructions(language)
        try:
            endpoint = f"{self.groq_api_base}/chat/completions"
            context_section = ""
            if context_text and context_text.strip():
                context_section = f"\nOFFICIAL SCIENTIFIC CONTEXT FROM NASA (Use as factual core):\n\"\"\"\n{context_text.strip()}\n\"\"\"\n"

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": (
                            f"Topic: {topic}\n"
                            f"Target duration: {target_duration} seconds.\n"
                            f"Target Language: {lang_name}\n"
                            f"Language Requirements:\n{lang_guidance}\n"
                            f"{context_section}"
                            f"Generate the JSON script following the schema:"
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
                return self._parse_json_response(text, language), None, "", ""
        except urllib.error.HTTPError as e:
            err_body = ""
            err_msg = ""
            err_code_str = ""
            try:
                err_body = e.read().decode("utf-8")
                err_data = json.loads(err_body)
                err_info = err_data.get("error", {})
                if isinstance(err_info, dict):
                    err_msg = err_info.get("message", "")
                    err_code_str = str(err_info.get("code", "") or "")
                elif isinstance(err_info, str):
                    err_msg = err_info
            except Exception:
                pass
            return None, e.code, err_code_str, err_msg or err_body
        except Exception as e:
            return None, -1, "exception", str(e)

    def _generate_groq(
        self,
        topic: str,
        target_duration: int,
        language: str = "es",
        context_text: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Call Groq API with automatic fallback to llama-3.3-70b-versatile if model is unavailable."""
        model = self.groq_model or "llama-3.3-70b-versatile"
        script, status, err_code, err_msg = self._call_groq_api(model, topic, target_duration, language, context_text)
        if script:
            return script

        # Handle authentication errors
        if status == 401 or "invalid api key" in err_msg.lower():
            print("  ❌ Groq API Error: Clave GROQ_API_KEY no válida o incorrecta.")
            print("     👉 Revisa o genera tu clave gratuita en https://console.groq.com/keys")
            return None

        # Handle rate limits
        if status == 429:
            print("  ❌ Groq API Error (429 Rate Limit): Límite de peticiones excedido en Groq.")
            return None

        # Check if the requested model is deprecated, decommissioned, or non-existent
        is_model_unavailable = (
            status in (400, 404)
            and any(kw in (err_msg + " " + err_code).lower() for kw in ("model", "decommission", "not_found", "not found", "does not exist"))
        )

        fallback_model = "llama-3.3-70b-versatile"
        if is_model_unavailable and model != fallback_model:
            print(f"  ⚠️ Groq API: El modelo '{model}' no está disponible ({err_msg}).")
            print(f"  🔄 Cambiando automáticamente al modelo oficial activo: '{fallback_model}'...")
            fb_script, fb_status, fb_code, fb_err = self._call_groq_api(fallback_model, topic, target_duration, language, context_text)
            if fb_script:
                return fb_script
            print(f"  ❌ Falló también con el modelo '{fallback_model}': {fb_err}")
            return None

        detail = f": {err_msg}" if err_msg else ""
        print(f"  ⚠️ Groq API HTTP Error {status}{detail}")
        return None

    def _generate_gemini(
        self,
        topic: str,
        target_duration: int,
        language: str = "es",
        context_text: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Call Gemini API via REST."""
        lang_name, lang_guidance = get_language_instructions(language)
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
            context_section = ""
            if context_text and context_text.strip():
                context_section = f"\nOFFICIAL SCIENTIFIC CONTEXT FROM NASA (Use as factual core):\n\"\"\"\n{context_text.strip()}\n\"\"\"\n"

            prompt = (
                f"{self.system_prompt}\n\n"
                f"Topic: {topic}\n"
                f"Target duration: {target_duration} seconds.\n"
                f"Target Language: {lang_name}\n"
                f"Language Requirements:\n{lang_guidance}\n"
                f"{context_section}"
                f"Generate the JSON script:"
            )

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.4,
                    "responseMimeType": "application/json",
                    "maxOutputTokens": 2048,
                    "thinkingConfig": {
                        "thinkingBudget": 0
                    }
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return self._parse_json_response(text, language)
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

    def _generate_openai(
        self,
        topic: str,
        target_duration: int,
        language: str = "es",
        context_text: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Call OpenAI API or custom endpoint."""
        lang_name, lang_guidance = get_language_instructions(language)
        try:
            endpoint = self.base_url if (self.base_url and self.base_url.startswith("http")) else "https://api.openai.com/v1/chat/completions"
            context_section = ""
            if context_text and context_text.strip():
                context_section = f"\nOFFICIAL SCIENTIFIC CONTEXT FROM NASA (Use as factual core):\n\"\"\"\n{context_text.strip()}\n\"\"\"\n"

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": (
                            f"Topic: {topic}\n"
                            f"Target duration: {target_duration}s.\n"
                            f"Target Language: {lang_name}\n"
                            f"Language Requirements:\n{lang_guidance}\n"
                            f"{context_section}"
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
                    "Authorization": f"Bearer {self.openai_key}"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=25) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["choices"][0]["message"]["content"]
                return self._parse_json_response(text, language)
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

    def _parse_json_response(self, text: str, language: str = "es") -> Optional[Dict[str, Any]]:
        """Clean markdown wrapping and validate JSON structure."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)

        try:
            data = json.loads(text)
            if "scenes" in data and isinstance(data["scenes"], list) and len(data["scenes"]) > 0:
                data["language"] = language
                return data
        except Exception as e:
            print(f"  ⚠️ JSON parse error: {e}")
        return None
