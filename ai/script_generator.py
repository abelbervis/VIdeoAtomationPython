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
    ENABLE_SCRIPT_REVIEW,
    GEMINI_API_KEY,
    GROQ_API_BASE,
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_API_BASE_URL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    SYSTEM_PROMPT_FILE,
    SYSTEM_PROMPT_PATH,
    sanitize_env_value,
)
from ai.script_reviewer import ScriptReviewer


DEFAULT_SYSTEM_PROMPT = """You are an elite viral video creator and master communicator (in the style of Kurzgesagt, Veritasium, and top-performing TikTok/Reels science and curiosity creators).
You craft high-retention, addictive 30-to-45-second scripts for YouTube Shorts, TikTok, and Instagram Reels across ANY requested topic (physics, biology, nature, ocean, technology, psychology, space, or extreme facts).

THE 9.5+ FORMULA FOR VIRAL SHORT VIDEOS (MANDATORY DIRECTIVES):

1. HUMAN & IMMERSIVE ANCHOR (NEVER TALK ABOUT ABSTRACT OBJECTS):
   - Do NOT talk about cold, detached objects (e.g. Bad: "Un reloj se detiene en el horizonte...").
   - Immerse the VIEWER directly into the experience using second-person framing or human observers:
     * Good: "Si cayeras dentro de un agujero negro, tus amigos te verían congelado para siempre."
     * Good: "Si intentaras nadar en las profundidades de la fosa de las Marianas..."
     * Good: "Si tu cerebro apagara una sola molécula de dopamina..."
   - Placing the human in the middle of the extreme phenomenon triggers empathy, mirror neurons, and instant retention.

2. ONE SINGLE FOCUSED ANGLE PER VIDEO (ZERO CONCEPT DUMPING):
   - Dedicate the entire 30-45 seconds to exploring ONE single mind-bending paradox, thought experiment, or extreme mechanism.
   - NEVER create a multi-topic checklist (e.g. do NOT mix radius + spaghettification + time dilation + Hawking radiation).

3. THE COGNITIVE ASYMMETRY / PERSPECTIVE TWIST (Scene 2 vs Scene 4):
   - The best viral scripts build power through dramatic contrast: "Para ellos ocurre X... pero para ti ocurre Y."
   - Example: Outside observers see you freeze at the edge for eternity. But from your perspective inside, your watch ticks normally and you watch the entire future of the cosmos race past.

4. SEAMLESS HOOK CONTINUITY (ZERO BAIT-AND-SWITCH):
   - The opening sentence (Scene 1 narration) MUST BE IDENTICAL to the "hook" field.
   - Scene 2 MUST immediately follow up and expand on the premise introduced in Scene 1.

5. VISCERAL, CHILL-INDUCING CLIMAX (Scene 5):
   - NEVER end with weak philosophical summaries (e.g. Bad: "Así, el tiempo es relativo según dónde lo vivas").
   - Conclude with a concrete, jaw-dropping clash of scales that leaves goosebumps:
     * Good: "Para la Tierra habrán pasado millones de años... mientras para ti, solo fue un parpadeo."
     * Good: "No morirías en la oscuridad... morirías viendo el fin de los tiempos."
   - NEVER use cheap calls to action ("comenta abajo", "dale like", "suscríbete").

6. PUNCHY CADENCE & WORD ECONOMY:
   - 4 to 5 visual scenes.
   - Strictly 12 to 16 spoken words per scene (absolute maximum: 18 words).
   - Cut every redundant phrase (no filler like "mientras cae en su propia nave").
   - Use active voice and natural pauses (. and ,) for magnetic text-to-speech rhythm.

7. REAL STOCK VIDEO SEARCH TAGS FOR PEXELS & PIXABAY:
   - In "keywords", provide 1 to 2 visual terms ALWAYS IN ENGLISH per scene.
   - NEVER use academic/niche physics terms ("spaghettification effect", "relativistic clock", "hawking radiation animation", "time dilation illustration").
   - ALWAYS use popular, tangible tags that actually exist on free stock sites:
     * Space: ["black hole 3d", "black hole"], ["galaxy animation", "spinning galaxy"], ["star explosion", "supernova"], ["deep space galaxy", "stars timelapse"].
     * Ocean: ["deep ocean", "underwater shark"], ["bioluminescent jellyfish", "coral reef"].
     * Nature: ["volcano eruption", "lava flow"], ["thunderstorm lightning", "storm timelapse"].
     * Biology / Body: ["brain 3d animation", "neurons firing"], ["cells microscope", "biology microscope"].
     * Technology / AI: ["futuristic robot", "artificial intelligence"], ["server room datacenter", "computer circuit"].
   - Set "visual_type": "video" for all scenes.
   - "visual_subject": Concise 2-4 word title in the target language.
   - "image_prompt": Descriptive 8k photographic prompt in English for FLUX/diffusion AI image generation if stock media is unavailable.

Respond ONLY with valid JSON matching this schema:
{
  "title": "Punchy viral title",
  "hook": "Magnetic opening hook sentence (MUST be the exact spoken narration of Scene 1)",
  "scenes": [
    {
      "scene_id": 1,
      "visual_subject": "Sujeto visual conciso en idioma destino",
      "narration": "Exact same sentence as 'hook' (12-16 words max)",
      "image_prompt": "cinematic 8k photograph of [concrete subject], National Geographic style, 8k",
      "keywords": ["popular stock video tag 1", "tag 2"],
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
                    # Render placeholders using environment variables
                    rendered = content.replace("{{PROVIDER}}", MEDIA_PROVIDER.upper())
                    return rendered, desc
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
            "Visual search keywords ('keywords') MUST also be in English."
        )
    elif lang in ("zh", "zh-cn", "chinese"):
        return (
            "Simplified Chinese (Mandarin / 中文简体)",
            "The entire narration and title MUST be written in natural, fluent Simplified Chinese (中文简体), "
            "crafted for high-retention viral short videos.\n"
            "CRITICAL: The visual search keywords ('keywords') MUST ALWAYS BE IN ENGLISH "
            "(e.g. keywords: ['volcano lava flow', 'deep sea ocean', 'galaxy spinning']) so media search succeeds!"
        )
    else:
        return (
            "Spanish (Español)",
            "The entire narration and title MUST be written in natural, fluent Spanish (Español).\n"
            "The visual search keywords ('keywords') MUST ALWAYS BE IN ENGLISH "
            "(e.g. keywords: ['volcano eruption', 'deep sea shark', 'black hole animation']) so media search succeeds!"
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
        enable_review: bool = ENABLE_SCRIPT_REVIEW,
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
        self.enable_review = enable_review

        self.reviewer = ScriptReviewer(
            gemini_key=self.gemini_key,
            openai_key=self.openai_key,
            groq_key=self.groq_key,
            groq_api_base=self.groq_api_base,
            groq_model=self.groq_model,
            preferred_provider=self.provider
        )

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

    def _apply_review_if_enabled(
        self,
        script: Optional[Dict[str, Any]],
        topic: str,
        target_duration: int,
        language: str,
        context_text: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Passes generated script through the secondary Critic Agent if enabled."""
        if not script or not self.enable_review:
            return script
        return self.reviewer.review(
            draft_script=script,
            topic=topic,
            target_duration=target_duration,
            language=language,
            context_text=context_text
        )

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
            return self._apply_review_if_enabled(script, topic, target_duration, language, context_text)

        if self.provider == "gemini":
            if not self._is_valid_api_key(self.gemini_key):
                print("  ❌ Error: Se especificó el proveedor 'gemini' pero no se configuró una GEMINI_API_KEY válida.")
                print("     👉 Obtén tu clave en https://aistudio.google.com/ y agrégala a tu .env o usa --gemini-key.")
                return None
            script = self._generate_gemini(topic, target_duration, language, context_text)
            if not script:
                print("  ❌ Error: Falló la generación del guión con la API de Gemini.")
            return self._apply_review_if_enabled(script, topic, target_duration, language, context_text)

        if self.provider == "openai":
            if not self._is_valid_api_key(self.openai_key):
                print("  ❌ Error: Se especificó el proveedor 'openai' pero no se configuró una OPENAI_API_KEY válida.")
                print("     👉 Obtén tu clave en https://platform.openai.com/ y agrégala a tu .env o usa --openai-key.")
                return None
            script = self._generate_openai(topic, target_duration, language, context_text)
            if not script:
                print("  ❌ Error: Falló la generación del guión con la API de OpenAI.")
            return self._apply_review_if_enabled(script, topic, target_duration, language, context_text)

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
                    return self._apply_review_if_enabled(script, topic, target_duration, language, context_text)
            elif prov == "gemini":
                print("  ⚡ Solicitando guión a Google Gemini...")
                script = self._generate_gemini(topic, target_duration, language, context_text)
                if script:
                    return self._apply_review_if_enabled(script, topic, target_duration, language, context_text)
            elif prov == "openai":
                print("  ⚡ Solicitando guión a OpenAI...")
                script = self._generate_openai(topic, target_duration, language, context_text)
                if script:
                    return self._apply_review_if_enabled(script, topic, target_duration, language, context_text)

        print(f"  ⚠️ Advertencia: Las APIs externas ({', '.join(configured_providers)}) no respondieron a tiempo.")
        if context_text or topic:
            print("  🛰️ Generando guión estructurado de alta fidelidad basado en los datos científicos oficiales de la NASA...")
            fallback_script = self._generate_scientific_fallback(topic, target_duration, language, context_text)
            if fallback_script:
                return fallback_script

        print("  ❌ Error: No fue posible generar el guión.")
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
                "temperature": 0.65
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
        """Call Gemini API via REST with connection close and model fallbacks."""
        lang_name, lang_guidance = get_language_instructions(language)
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

        models_to_try = ["gemini-2.5-flash", "gemini-flash-latest"]
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "NASA-Shorts-Generator/1.0",
            "Connection": "close"
        }

        for model in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.65,
                        "responseMimeType": "application/json",
                        "maxOutputTokens": 2048,
                    }
                }

                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=35) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    text = result["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = self._parse_json_response(text, language)
                    if parsed and parsed.get("scenes"):
                        return parsed
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue  # Try next model
                elif e.code in (401, 403):
                    print(f"  ⚠️ Gemini API Error ({e.code} Unauthorized): Clave GEMINI_API_KEY no válida.")
                    return None
                elif e.code == 429:
                    print(f"  ⚠️ Gemini API Error (429 Rate Limit): Cuota de uso excedida.")
                    return None
                else:
                    print(f"  ⚠️ Gemini API ({model}) failed ({e})")
            except Exception as e:
                print(f"  ⚠️ Gemini API ({model}) request failed ({e})")

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
                "temperature": 0.65
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
        """Clean markdown wrapping, validate and normalize JSON structure with separate provider keywords."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)

        try:
            data = json.loads(text)
            if "scenes" in data and isinstance(data["scenes"], list) and len(data["scenes"]) > 0:
                data["language"] = language

                # Synchronize Scene 1 narration with hook to guarantee zero bait-and-switch
                hook = data.get("hook", "").strip()
                if hook and data["scenes"]:
                    first_sc = data["scenes"][0]
                    sc1_narr = first_sc.get("narration", "").strip()
                    if not sc1_narr:
                        first_sc["narration"] = hook
                    elif hook.lower() not in sc1_narr.lower() and sc1_narr.lower() not in hook.lower():
                        first_sc["narration"] = hook

                UNAVAILABLE_KEYWORD_MAP = {
                    "spaghettification": "black hole 3d",
                    "relativistic clock": "deep space",
                    "time dilation": "galaxy spinning",
                    "hawking radiation": "space animation",
                    "tidal forces": "black hole 3d",
                    "cosmic abyss": "deep space galaxy",
                    "star plunge": "supernova explosion",
                    "fragile light": "sunlight beam",
                    "invisible threat": "black hole",
                    "eternal dance": "spinning galaxy"
                }

                # Normalize keywords across all scenes into a single clean list
                for sc in data["scenes"]:
                    raw_kws = (
                        sc.get("keywords")
                        or sc.get("nasa_keywords")
                        or sc.get("pexels_keywords")
                        or sc.get("stock_keywords")
                        or []
                    )
                    if isinstance(raw_kws, str):
                        kws = [k.strip() for k in raw_kws.split(",") if k.strip()]
                    elif isinstance(raw_kws, list):
                        kws = [str(k).strip() for k in raw_kws if str(k).strip()]
                    else:
                        kws = []

                    # Replace any known zero-result academic or metaphorical terms with high-yield stock tags
                    cleaned_kws = []
                    for kw in kws:
                        kw_lower = kw.lower()
                        mapped = False
                        for bad_term, good_tag in UNAVAILABLE_KEYWORD_MAP.items():
                            if bad_term in kw_lower:
                                cleaned_kws.append(good_tag)
                                mapped = True
                                break
                        if not mapped:
                            cleaned_kws.append(kw)

                    sc["keywords"] = cleaned_kws or ["black hole 3d", "deep space"]
                    # Aliases for backwards compatibility
                    sc["nasa_keywords"] = sc["keywords"]
                    sc["pexels_keywords"] = sc["keywords"]
                    sc["stock_keywords"] = sc["keywords"]

                return data
        except Exception as e:
            print(f"  ⚠️ JSON parse error: {e}")
        return None

    def _generate_scientific_fallback(
        self,
        topic: str,
        target_duration: int,
        language: str = "es",
        context_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build a high-retention structured science video script directly from NASA grounded context.
        Used as a zero-downtime safety net if external LLM APIs experience transient timeouts.
        """
        raw_context = (context_text or "").strip()
        # Clean off any injected notes
        clean_facts = re.sub(r"\[OFFICIAL NASA DISCOVERY[^\]]*\]", "", raw_context).strip()
        sentences = [s.strip() for s in re.split(r"[.!?]+", clean_facts) if len(s.strip()) > 15]

        # Determine language-specific strings
        lang = (language or "es").lower()
        is_es = lang.startswith("es")
        is_en = lang.startswith("en")

        title = topic.strip()
        if is_es:
            hook = f"¿Sabías lo que acaba de revelar la NASA sobre {title}?"
            c1_narr = f"La NASA acaba de registrar una observación histórica sobre {title}."
            c2_narr = sentences[0] if len(sentences) > 0 else f"Los científicos espaciales han detectado señales asombrosas que cambian lo que sabíamos."
            c3_narr = sentences[1] if len(sentences) > 1 else f"Este fenómeno cósmico abre una nueva era para comprender los misterios del universo."
            c4_narr = f"El cosmos esconde secretos que apenas comenzamos a descubrir. ¿Qué opinas tú?"
            on_screen_1 = title[:30].upper()
            on_screen_2 = "DESCUBRIMIENTO OFICIAL"
            on_screen_3 = "DATOS CÓSMICOS"
            on_screen_4 = "¿QUÉ OPINAS TÚ?"
        elif is_en:
            hook = f"Did you know what NASA just discovered about {title}?"
            c1_narr = f"NASA has just captured a groundbreaking observation of {title}."
            c2_narr = sentences[0] if len(sentences) > 0 else f"Astrophysicists detected astonishing data that challenges our models."
            c3_narr = sentences[1] if len(sentences) > 1 else f"This cosmic phenomenon marks a major leap in understanding deep space."
            c4_narr = f"The universe holds infinite secrets waiting to be unlocked. What do you think?"
            on_screen_1 = title[:30].upper()
            on_screen_2 = "OFFICIAL DISCOVERY"
            on_screen_3 = "COSMIC DATA"
            on_screen_4 = "WHAT DO YOU THINK?"
        else:
            # Default / Chinese or other
            hook = f"关于 {title}，NASA刚刚公布了惊人发现！"
            c1_narr = f"NASA官方最新公布了关于 {title} 的前沿探测数据。"
            c2_narr = sentences[0] if len(sentences) > 0 else f"科学家们捕获到了令人震撼的深空信号。"
            c3_narr = sentences[1] if len(sentences) > 1 else f"这项天文发现正在改写我们对宇宙奥秘的认知。"
            c4_narr = f"浩瀚星空还有多少未知？留下你的想法！"
            on_screen_1 = title[:20]
            on_screen_2 = "NASA官方发现"
            on_screen_3 = "宇宙前沿数据"
            on_screen_4 = "你怎么看？"

        # Construct scenes adapted to target duration with unified visual keywords
        scenes = [
            {
                "scene_id": 1,
                "visual_subject": title[:30],
                "narration": f"{hook} {c1_narr}",
                "on_screen_text": on_screen_1,
                "visual_type": "video",
                "keywords": [title.lower(), "deep space observation"],
                "nasa_keywords": [title.lower(), "deep space observation"],
                "pexels_keywords": [title.lower(), "deep space observation"],
                "stock_keywords": [title.lower(), "deep space observation"],
                "audio_cue": "whoosh"
            },
            {
                "scene_id": 2,
                "visual_subject": on_screen_2 if not on_screen_2.startswith("¿") else title[:30],
                "narration": c2_narr,
                "on_screen_text": on_screen_2,
                "visual_type": "video",
                "keywords": ["cosmic phenomenon", "deep space galaxy"],
                "nasa_keywords": ["cosmic phenomenon", "deep space galaxy"],
                "pexels_keywords": ["cosmic phenomenon", "deep space galaxy"],
                "stock_keywords": ["cosmic phenomenon", "deep space galaxy"],
                "audio_cue": "subtle_boom"
            },
            {
                "scene_id": 3,
                "visual_subject": "Espacio Profundo",
                "narration": f"{c3_narr} {c4_narr}",
                "on_screen_text": on_screen_4,
                "visual_type": "video",
                "keywords": ["deep space universe stars", "cosmic web"],
                "nasa_keywords": ["deep space universe stars", "cosmic web"],
                "pexels_keywords": ["deep space universe stars", "cosmic web"],
                "stock_keywords": ["deep space universe stars", "cosmic web"],
                "audio_cue": "laser"
            }
        ]

        return {
            "title": title,
            "hook": hook,
            "scenes": scenes,
            "target_duration": target_duration,
            "language": language,
            "generation_mode": "nasa_grounded_scientific_fallback"
        }
