"""
AI Script Generator for Vertical Science Shorts.
Generates structured JSON scripts divided into scenes with narration and targeted NASA search keywords.
Supports Google Gemini, OpenAI, and a reliable factual scientific generator fallback.
"""

import json
import os
import re
import random
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from config import (
    BASE_DIR,
    CONTENT_CATEGORIES,
    DEFAULT_CATEGORY,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_API_BASE,
    HOOK_STYLE,
    HOOK_STYLES,
    LLM_PROVIDER,
    LLM_API_BASE_URL,
    SYSTEM_PROMPT_FILE,
    SYSTEM_PROMPT_PATH,
    detect_topic_category,
    sanitize_env_value
)


DEFAULT_SYSTEM_PROMPT = """You are a world-class documentary director and viral storyteller crafting premium scripts for YouTube Shorts and TikTok.
Target duration: 30 to 45 seconds (approx. 70-95 total spoken words).

CRITICAL NARRATIVE RULES:
1. THE 2.5-SECOND VIRAL HOOK (Maximum Retention Engine for TikTok & Shorts):
   - Scene 1 narration MUST be the explosive hook. STRICT LIMIT: 10 to 14 words maximum.
   - The first 4 words MUST grab attention before the viewer can swipe away.
   - CHOOSE ONE OF THESE 4 BATTLE-TESTED VIRAL HOOK FORMULAS:
     a) THE VISUAL PARADOX / CONTRADICTION: "Esto que parece una simple estrella, en realidad desafía las leyes de la física." / "Este diminuto ser marino puede sobrevivir en el vacío del espacio."
     b) THE RAW THREAT / COLOSSAL SCALE: "Si este monstruo estuviera a un año luz de nosotros, el cielo ardería en segundos." / "A once mil metros de profundidad, la presión aplastaría un submarino en microsegundos."
     c) THE UNSETTLING REVELATION / SECRET: "La ciencia creía que esto era imposible, hasta que apuntaron aquí." / "Nos enseñaron una versión de la historia, pero este hallazgo revela la verdad."
     d) THE SUDDEN UNEXPLAINED ANOMALY: "Los científicos acaban de detectar una anomalía que nadie logra explicar." / "Algo gigantesco e inexplicable acaba de registrarse en este lugar."
   - STRICTLY FORBIDDEN IN THE OPENING HOOK (INSTANT SWIPE-AWAY TRIGGERS):
     * NEVER use question clichés: "¿Sabías que...?", "¿Alguna vez te has preguntado...?", "¿Te imaginas si...?", "Did you know...", "Have you ever wondered...".
     * NEVER use conversational greetings: "Hola amigos", "Bienvenidos", "En este video", "Hey guys", "Welcome back".
     * NEVER use slow journalistic introductions: "Hoy exploraremos...", "Los científicos han descubierto...", "La agencia acaba de anunciar...". Jump directly into the raw tension.

2. RHYTHM & SCENE BREVITY (Shorts & Subtitles Optimized):
   - Divide the script into 4 to 5 distinct visual scenes.
   - STRICT LIMIT: 14 to 18 words maximum per scene (Scene 1 hook must be 10-14 words). Use short, punchy, active sentences.
   - Avoid complex subordinate clauses. Insert punctuation (. and ;) so the voice synthesizer takes natural pauses.

3. TTS & PHONETIC CLARITY (Spoken Natural Voice):
   - NEVER use acronyms or abbreviations in parentheses (e.g. NEVER write "(CME)", "(JWST)", "(GPS)", "(NASA)", "(AI)").
   - Use natural spoken equivalents: say "eyección solar", "telescopio espacial", "nave espacial", "inteligencia artificial", "nanómetros".
   - Write numbers and units in simple natural form (e.g. "mil seiscientos kilómetros por hora", "once mil metros", "tres millones de transistores") so text-to-speech speaks them with flawless human cadence.

4. MEDIA SEARCH KEYWORDS & VISUAL CONTINUITY:
   - Provide 2 to 3 visual search keywords per scene ALWAYS IN ENGLISH.
   - SCENE CONTINUITY (CRITICAL): All visual search keywords MUST be directly anchored to the specific subject being discussed (e.g. for space: 'comet nucleus telescope', 'nebula cosmic web'; for nature/ocean: 'deep sea creature abyss', 'volcanic lava eruption 4k'; for tech: 'quantum processor lab', 'humanoid robot autonomous'; for history: 'ancient pyramid ruins aerial', 'archaeological excavation tomb'; for science: 'human brain neurons firing', 'microscopic cell immune battle').
   - BANNED KEYWORDS (STRICTLY FORBIDDEN): NEVER search corporate, bureaucratic, or office words like 'office', 'agency', 'meeting', 'businessman', 'laboratory paperwork', 'briefing', 'logo', 'meatball', 'hallway', 'auditorium', 'conference'. These cause real footage to be replaced by boring stock office photos.
   - Set "visual_type": "video" for motion scenes, "image" for historical events, deep field space, or macro photography.
   - Add "visual_subject": In each scene, provide a concise 2-4 word title in the target language describing exactly what is being shown on screen (e.g. "Fosa de las Marianas", "Microchip Cuántico", "Pirámides de Giza", "Neuronas Cerebrales", "Cometa Pons-Brooks"). This will be displayed in the cinematic visual badge so viewers know what they are looking at.

5. DRAMATIC 5-STEP ARC:
   - Scene 1 (Explosive Hook): Immediate mystery, visual paradox, or raw danger.
   - Scene 2 (The Mechanism): The invisible physical, biological, or technological trigger in action.
   - Scene 3 (The Impact): Direct clash with human perception, Earth, or the future.
   - Scene 4 (Tangible Proof / Scale): A striking comparison, historical precedent, or physical measurement.
   - Scene 5 (Climactic Closing Thought): A striking punchline or lingering thought that prompts comments and shares.

Respond ONLY with valid JSON matching this schema:
{
  "title": "Short punchy title",
  "hook": "Opening hook sentence (matches Scene 1 narration)",
  "scenes": [
    {
      "scene_id": 1,
      "visual_subject": "Concise name of what is shown in target language",
      "narration": "Explosive opening hook (10-14 words max)",
      "keywords": ["concrete english keyword 1", "concrete english keyword 2"],
      "visual_type": "video",
      "estimated_duration": 7
    }
  ]
}
"""


def get_category_guidance(category: Optional[str] = None, topic: str = "") -> str:
    """Provides domain-tailored narrative instructions, specialized vocabulary, and visual directives."""
    cat = (category or DEFAULT_CATEGORY or "auto").lower().strip()
    if cat == "auto":
        cat = detect_topic_category(topic)

    if cat == "nature":
        return (
            "\n🌿 DOMAIN DIRECTIVE (EXTREME NATURE, DEEP ABYSS & WILDLIFE):\n"
            "- Narrative Focus: Extreme evolutionary adaptations, crushing oceanic depths, apex predator mechanics, volcanic fury, subterranean ecosystems.\n"
            "- Spoken Vocabulary: Presión hidrostática, bioluminiscencia, oscuridad abisal, adaptación extrema, veneno letal, instinto depredador, fuerzas tectónicas.\n"
            "- Visual Keywords: ALWAYS IN ENGLISH. Focus on breathtaking 4K vertical footage (e.g. ['deep sea trench creature', 'bioluminescent jellyfish abyss', 'volcanic lava eruption macro', 'ocean apex predator hunting']).\n"
        )
    elif cat == "tech":
        return (
            "\n🤖 DOMAIN DIRECTIVE (FRONTIER TECHNOLOGY, AI & QUANTUM):\n"
            "- Narrative Focus: Exponential computing, neural architectures, autonomous robotics, quantum weirdness, future human disruption, silicon breakthroughs.\n"
            "- Spoken Vocabulary: Red neuronal, computación cuántica, nanómetros de silicio, velocidad algorítmica, autonomía robótica, salto evolutivo digital.\n"
            "- Visual Keywords: ALWAYS IN ENGLISH. Focus on cleanrooms, futuristic hardware, and cyber visuals (e.g. ['supercomputer server room glowing', 'humanoid robot laboratory', 'quantum processor wafer macro', 'cybernetic digital network visualization']).\n"
        )
    elif cat == "history":
        return (
            "\n🏛️ DOMAIN DIRECTIVE (ANCIENT MYSTERIES & ARCHAEOLOGY):\n"
            "- Narrative Focus: Lost civilizations, megalithic architecture, unearthed tombs, deciphered ancient chronicles, forgotten empires, historical enigmas.\n"
            "- Spoken Vocabulary: Milenios, excavación arqueológica, sarcófago, dinastía perdida, arquitectos milenarios, enigmas enterrados, jeroglíficos descifrados.\n"
            "- Visual Keywords: ALWAYS IN ENGLISH. Focus on awe-inspiring archaeological ruins and artifacts (e.g. ['ancient egyptian pyramid ruins aerial', 'archaeological tomb excavation', 'ancient stone temple monolith', 'ancient scroll hieroglyphs museum']).\n"
        )
    elif cat == "science":
        return (
            "\n🔬 DOMAIN DIRECTIVE (SCIENCE CURIOSITIES & HUMAN BODY):\n"
            "- Narrative Focus: Counter-intuitive biology, illusions of the human brain, cellular warfare, chemical reactions, surprising physics trivia hiding in plain sight.\n"
            "- Spoken Vocabulary: Sinapsis neuronales, neurotransmisores, membrana celular, ilusión óptica, reacción molecular, percepción sensorial, reloj biológico.\n"
            "- Visual Keywords: ALWAYS IN ENGLISH. Focus on microscopic, lab, and bodily phenomena (e.g. ['human brain neurons firing glowing', 'microscopic cell immune battle', 'chemical reaction colorful liquid', 'optical illusion perception pattern']).\n"
        )
    else:  # space
        return (
            "\n🌌 DOMAIN DIRECTIVE (SPACE & ASTROPHYSICS):\n"
            "- Narrative Focus: Cosmic scale, astronomical sensors, astrophysics laws, stellar cataclysms, deep space telescope imagery.\n"
            "- Spoken Vocabulary: Horizonte de sucesos, años luz, lentes gravitacionales, radiación cósmica, fusión nuclear, mecánica orbital, nebulosas estelares.\n"
            "- Visual Keywords: ALWAYS IN ENGLISH. Focus on deep space telescope observations (e.g. ['deep space starfield hubble', 'black hole accretion disk', 'mars rover landscape 4k', 'supernova remnant nebula']).\n"
        )


def get_hook_guidance(hook_style: Optional[str] = None, custom_hook: Optional[str] = None, category: Optional[str] = None, topic: str = "") -> str:
    """Build specific hook directives to steer the LLM towards high retention across all content domains."""
    if custom_hook and custom_hook.strip():
        return (
            f"\nCRITICAL MANDATORY HOOK INSTRUCTION:\n"
            f"The script MUST use this exact opening hook provided by the user for Scene 1 narration:\n"
            f"\"{custom_hook.strip()}\"\n"
        )

    cat = (category or DEFAULT_CATEGORY or "auto").lower().strip()
    if cat == "auto":
        cat = detect_topic_category(topic)

    style = (hook_style or HOOK_STYLE or "auto").lower().strip()
    if style == "random":
        style = random.choice(["paradox", "threat", "mystery", "secret"])

    if style == "paradox":
        examples = {
            "space": "'Esto que parece una simple estrella en realidad desafía las leyes de la física...'",
            "nature": "'Este diminuto ser marino puede sobrevivir en el vacío del espacio y regenerar su ADN...'",
            "tech": "'Este procesador calculó en tres segundos lo que a la humanidad le tomaría diez mil años...'",
            "history": "'Esta precisión arquitectónica encontrada en el desierto no debería haber existido hace cuatro mil años...'",
            "science": "'Tu propio cerebro te está mintiendo en este mismo segundo y no puedes evitarlo...'"
        }
        eg = examples.get(cat, examples["space"])
        return (
            f"\nHSS HOOK STYLE DIRECTIVE (THE VISUAL PARADOX / CONTRADICTION):\n"
            f"Scene 1 narration MUST open with an impossible visual contradiction or paradox that challenges common sense "
            f"(e.g. {eg}).\n"
        )
    elif style == "threat":
        examples = {
            "space": "'Si este monstruo cósmico estuviera a un año luz, la atmósfera terrestre ardería en segundos...'",
            "nature": "'A once mil metros bajo el mar, la presión aplastaría un submarino de titanio en microsegundos...'",
            "tech": "'Si esta inteligencia artificial se despliega sin frenos, transformará todos los sistemas en segundos...'",
            "history": "'El colosal cataclismo que destruyó esta civilización ocurrió tan rápido que nadie pudo escapar...'",
            "science": "'Una sola gota de este compuesto contiene suficientes toxinas para paralizar tu cuerpo al instante...'"
        }
        eg = examples.get(cat, examples["space"])
        return (
            f"\nHSS HOOK STYLE DIRECTIVE (RAW THREAT / COLOSSAL SCALE):\n"
            f"Scene 1 narration MUST open with intense visceral danger, destructive power, or terrifying scale "
            f"(e.g. {eg}).\n"
        )
    elif style == "mystery":
        examples = {
            "space": "'Los telescopios acaban de captar una señal desconcertante en los confines de...'",
            "nature": "'En las fosas más oscuras del océano acaba de emerger una criatura que no encaja en la biología...'",
            "tech": "'En un laboratorio confidencial acaba de ocurrir algo que los propios ingenieros no pueden descifrar...'",
            "history": "'Arqueólogos acaban de abrir una cámara sellada durante milenios y hallaron algo desconcertante...'",
            "science": "'Bajo el microscopio electrónico acaba de revelarse un comportamiento celular nunca antes visto...'"
        }
        eg = examples.get(cat, examples["space"])
        return (
            f"\nHSS HOOK STYLE DIRECTIVE (UNEXPLAINED ANOMALY / SUDDEN MYSTERY):\n"
            f"Scene 1 narration MUST open with a sudden shocking anomaly or unexplainable discovery "
            f"(e.g. {eg}).\n"
        )
    elif style == "secret":
        examples = {
            "space": "'La ciencia creía que esto era imposible, hasta que apuntaron los telescopios hacia...'",
            "nature": "'Siempre nos dijeron que este animal era inofensivo, pero oculta un mecanismo biológico letal...'",
            "tech": "'Lo que las grandes empresas tecnológicas no te dicen sobre este algoritmo cambiará tu vida...'",
            "history": "'Nos enseñaron una versión de la historia, pero esta tableta milenaria revela la verdad...'",
            "science": "'Creías saber cómo funciona tu propio cuerpo, pero este descubrimiento médico contradice todo...'"
        }
        eg = examples.get(cat, examples["space"])
        return (
            f"\nHSS HOOK STYLE DIRECTIVE (SHATTERING BELIEFS / HIDDEN SECRET):\n"
            f"Scene 1 narration MUST open by shattering a widespread misconception with an unsettling truth "
            f"(e.g. {eg}).\n"
        )
    return ""


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
        context_text: Optional[str] = None,
        hook_style: Optional[str] = None,
        custom_hook: Optional[str] = None,
        category: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Generate a structured script for the given topic using configured AI providers."""
        cat = (category or DEFAULT_CATEGORY or "auto").lower().strip()
        if cat == "auto":
            resolved_category = detect_topic_category(topic)
        else:
            resolved_category = cat

        lang_label, _ = get_language_instructions(language)
        context_note = " + Grounded NASA context" if context_text else ""
        hook_note = f", Hook: {hook_style or 'auto'}" if not custom_hook else ", Hook: Custom"
        cat_note = f", Category: {resolved_category.upper()}"
        print(f"\n🧠 Generating script for: '{topic}' (~{target_duration}s{cat_note}, Language: {lang_label}{hook_note}, System Prompt: {self.prompt_source}{context_note})...")

        # Specific provider selected
        if self.provider == "groq":
            if not self._is_valid_api_key(self.groq_key):
                print("  ❌ Error: Se especificó el proveedor 'groq' pero no se configuró una GROQ_API_KEY válida.")
                print("     👉 Obtén tu clave gratuita en https://console.groq.com/keys y agrégala a tu .env o usa --groq-key.")
                return None
            script = self._generate_groq(topic, target_duration, language, context_text, hook_style, custom_hook, resolved_category)
            if not script:
                print("  ❌ Error: Falló la generación del guión con la API de Groq.")
            return script

        if self.provider == "gemini":
            if not self._is_valid_api_key(self.gemini_key):
                print("  ❌ Error: Se especificó el proveedor 'gemini' pero no se configuró una GEMINI_API_KEY válida.")
                print("     👉 Obtén tu clave en https://aistudio.google.com/ y agrégala a tu .env o usa --gemini-key.")
                return None
            script = self._generate_gemini(topic, target_duration, language, context_text, hook_style, custom_hook, resolved_category)
            if not script:
                print("  ❌ Error: Falló la generación del guión con la API de Gemini.")
            return script

        if self.provider == "openai":
            if not self._is_valid_api_key(self.openai_key):
                print("  ❌ Error: Se especificó el proveedor 'openai' pero no se configuró una OPENAI_API_KEY válida.")
                print("     👉 Obtén tu clave en https://platform.openai.com/ y agrégala a tu .env o usa --openai-key.")
                return None
            script = self._generate_openai(topic, target_duration, language, context_text, hook_style, custom_hook, resolved_category)
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
                script = self._generate_groq(topic, target_duration, language, context_text, hook_style, custom_hook, resolved_category)
                if script:
                    return script
            elif prov == "gemini":
                print("  ⚡ Solicitando guión a Google Gemini...")
                script = self._generate_gemini(topic, target_duration, language, context_text, hook_style, custom_hook, resolved_category)
                if script:
                    return script
            elif prov == "openai":
                print("  ⚡ Solicitando guión a OpenAI...")
                script = self._generate_openai(topic, target_duration, language, context_text, hook_style, custom_hook, resolved_category)
                if script:
                    return script

        print(f"  ⚠️ Advertencia: Las APIs externas ({', '.join(configured_providers)}) no respondieron a tiempo.")
        if context_text or topic:
            print(f"  🎬 Generando guión estructurado de alta fidelidad para {resolved_category.upper()}...")
            fallback_script = self._generate_scientific_fallback(topic, target_duration, language, context_text, hook_style, custom_hook, resolved_category)
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
        context_text: Optional[str] = None,
        hook_style: Optional[str] = None,
        custom_hook: Optional[str] = None,
        category: Optional[str] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[int], str, str]:
        """Execute a single REST call to Groq API. Returns (script_dict, status_code, err_code, err_msg)."""
        lang_name, lang_guidance = get_language_instructions(language)
        category_directive = get_category_guidance(category, topic)
        hook_directive = get_hook_guidance(hook_style, custom_hook, category, topic)
        try:
            endpoint = f"{self.groq_api_base}/chat/completions"
            context_section = ""
            if context_text and context_text.strip():
                context_section = f"\nOFFICIAL SCIENTIFIC CONTEXT (Use as factual core):\n\"\"\"\n{context_text.strip()}\n\"\"\"\n"

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
                            f"{category_directive}"
                            f"{hook_directive}"
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
        context_text: Optional[str] = None,
        hook_style: Optional[str] = None,
        custom_hook: Optional[str] = None,
        category: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Call Groq API with automatic fallback to llama-3.3-70b-versatile if model is unavailable."""
        model = self.groq_model or "llama-3.3-70b-versatile"
        script, status, err_code, err_msg = self._call_groq_api(model, topic, target_duration, language, context_text, hook_style, custom_hook, category)
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
            fb_script, fb_status, fb_code, fb_err = self._call_groq_api(fallback_model, topic, target_duration, language, context_text, hook_style, custom_hook, category)
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
        context_text: Optional[str] = None,
        hook_style: Optional[str] = None,
        custom_hook: Optional[str] = None,
        category: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Call Gemini API via REST with connection close and model fallbacks."""
        lang_name, lang_guidance = get_language_instructions(language)
        category_directive = get_category_guidance(category, topic)
        hook_directive = get_hook_guidance(hook_style, custom_hook, category, topic)
        context_section = ""
        if context_text and context_text.strip():
            context_section = f"\nOFFICIAL SCIENTIFIC CONTEXT (Use as factual core):\n\"\"\"\n{context_text.strip()}\n\"\"\"\n"

        prompt = (
            f"{self.system_prompt}\n\n"
            f"Topic: {topic}\n"
            f"Target duration: {target_duration} seconds.\n"
            f"Target Language: {lang_name}\n"
            f"Language Requirements:\n{lang_guidance}\n"
            f"{category_directive}"
            f"{hook_directive}"
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
                        "temperature": 0.4,
                        "responseMimeType": "application/json",
                        "maxOutputTokens": 4096,
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
        context_text: Optional[str] = None,
        hook_style: Optional[str] = None,
        custom_hook: Optional[str] = None,
        category: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Call OpenAI API or custom endpoint."""
        lang_name, lang_guidance = get_language_instructions(language)
        category_directive = get_category_guidance(category, topic)
        hook_directive = get_hook_guidance(hook_style, custom_hook, category, topic)
        try:
            endpoint = self.base_url if (self.base_url and self.base_url.startswith("http")) else "https://api.openai.com/v1/chat/completions"
            context_section = ""
            if context_text and context_text.strip():
                context_section = f"\nOFFICIAL SCIENTIFIC CONTEXT (Use as factual core):\n\"\"\"\n{context_text.strip()}\n\"\"\"\n"

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
                            f"{category_directive}"
                            f"{hook_directive}"
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
        except Exception:
            # Fallback: attempt to find matching outermost JSON brackets
            first_brace = text.find("{")
            last_brace = text.rfind("}")
            if first_brace != -1 and last_brace > first_brace:
                try:
                    data = json.loads(text[first_brace:last_brace + 1])
                    if "scenes" in data and isinstance(data["scenes"], list) and len(data["scenes"]) > 0:
                        data["language"] = language
                        return data
                except Exception as e:
                    print(f"  ⚠️ JSON parse error: {e}")
            else:
                print("  ⚠️ JSON parse error: No valid JSON object found in response")
        return None

    def _generate_scientific_fallback(
        self,
        topic: str,
        target_duration: int,
        language: str = "es",
        context_text: Optional[str] = None,
        hook_style: Optional[str] = None,
        custom_hook: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build a high-retention structured video script adapted to the topic's domain.
        Used as a zero-downtime safety net if external LLM APIs experience transient timeouts.
        """
        raw_context = (context_text or "").strip()
        clean_facts = re.sub(r"\[OFFICIAL NASA DISCOVERY[^\]]*\]", "", raw_context).strip()
        sentences = [s.strip() for s in re.split(r"[.!?]+", clean_facts) if len(s.strip()) > 15]

        cat = (category or DEFAULT_CATEGORY or "auto").lower().strip()
        if cat == "auto":
            cat = detect_topic_category(topic)

        # Determine language-specific strings
        lang = (language or "es").lower()
        is_es = lang.startswith("es")
        is_en = lang.startswith("en")
        title = topic.strip()

        style = (hook_style or "auto").lower()
        if style in ("auto", "random"):
            style = random.choice(["paradox", "threat", "mystery", "secret"])

        if is_es:
            if custom_hook and custom_hook.strip():
                hook = custom_hook.strip()
            elif cat == "nature":
                if style == "paradox":
                    hook = f"Lo que estás viendo sobre {title} desafía las reglas biológicas de la supervivencia."
                elif style == "threat":
                    hook = f"A miles de metros de profundidad en {title}, la presión aplastaría cualquier estructura."
                elif style == "secret":
                    hook = f"Durante años se creyó que {title} era imposible, hasta que exploraron este rincón."
                else:
                    hook = f"Científicos acaban de registrar una criatura asombrosa e inexplicable en {title}."
                c1_narr = sentences[0] if len(sentences) > 0 else "En estos entornos extremos, la vida sobrevive mediante adaptaciones que parecen de otro mundo."
                c2_narr = sentences[1] if len(sentences) > 1 else "Cada segundo es una batalla salvaje donde la evolución desafía cualquier límite conocido."
                c3_narr = "La naturaleza oculta misterios más profundos de lo que imaginamos. ¿Qué opinas tú?"
                on_screen_1 = title[:28].upper()
                on_screen_2 = "SUPERVIVENCIA EXTREMA"
                on_screen_3 = "FUERZA SALVAJE"
                on_screen_4 = "¿QUÉ OPINAS TÚ?"
                kw_1 = [title.lower(), "deep sea abyss nature", "wildlife extreme 4k"]
                kw_2 = ["underwater abyss predator", "ocean trench nature", "extreme wildlife macro"]
                kw_3 = ["ocean depth underwater", "nature wilderness 4k", "marine life abyss"]
            elif cat == "tech":
                if style == "paradox":
                    hook = f"Lo que estás viendo sobre {title} desafía los límites de la computación conocida."
                elif style == "threat":
                    hook = f"Si el poder de {title} se desplegara sin frenos, transformaría el mundo en segundos."
                elif style == "secret":
                    hook = f"Los ingenieros creían que {title} era imposible, hasta que este avance lo cambió todo."
                else:
                    hook = f"Laboratorios acaban de registrar un comportamiento inexplicable en {title}."
                c1_narr = sentences[0] if len(sentences) > 0 else "Millones de operaciones por microsegundo procesan información a una velocidad jamás vista."
                c2_narr = sentences[1] if len(sentences) > 1 else "Esta tecnología exponencial está acelerando un salto evolutivo sin precedentes."
                c3_narr = "El futuro ya no es ciencia ficción: se está escribiendo ahora. ¿Qué opinas tú?"
                on_screen_1 = title[:28].upper()
                on_screen_2 = "SALTO CUÁNTICO"
                on_screen_3 = "INTELIGENCIA AVANZADA"
                on_screen_4 = "¿QUÉ OPINAS TÚ?"
                kw_1 = [title.lower(), "future technology laboratory", "artificial intelligence cyber"]
                kw_2 = ["supercomputer server room", "quantum chip processor", "robotics innovation"]
                kw_3 = ["cyber digital data", "fiber optics glow", "futuristic innovation"]
            elif cat == "history":
                if style == "paradox":
                    hook = f"Lo que estás viendo sobre {title} no debería haber existido hace miles de años."
                elif style == "threat":
                    hook = f"El colosal cataclismo que destruyó {title} borró a una civilización en cuestión de días."
                elif style == "secret":
                    hook = f"Los historiadores ignoraron durante siglos lo que realmente ocurrió en {title}."
                else:
                    hook = f"Nuevas excavaciones acaban de desenterrar un enigma desconcertante sobre {title}."
                c1_narr = sentences[0] if len(sentences) > 0 else "Estructuras megalíticas y manuscritos antiguos revelan conocimientos que desafían nuestra cronología."
                c2_narr = sentences[1] if len(sentences) > 1 else "Cada piedra excavada plantea preguntas más inquietantes que las respuestas que creíamos tener."
                c3_narr = "El pasado oculta verdades asombrosas que apenas comenzamos a descifrar. ¿Qué opinas tú?"
                on_screen_1 = title[:28].upper()
                on_screen_2 = "ENIGMA MILENARIO"
                on_screen_3 = "RUINAS PERDIDAS"
                on_screen_4 = "¿QUÉ OPINAS TÚ?"
                kw_1 = [title.lower(), "ancient ruins archaeological", "ancient pyramid monument aerial"]
                kw_2 = ["archaeology excavation tomb", "ancient stone hieroglyphs", "historic temple ruins"]
                kw_3 = ["ancient artifact museum", "historical discovery ruins", "ancient world architecture"]
            elif cat == "science":
                if style == "paradox":
                    hook = f"Lo que estás a punto de descubrir sobre {title} contradice lo que creías de tu cuerpo."
                elif style == "threat":
                    hook = f"Una alteración microscópica en {title} podría detener el funcionamiento biológico al instante."
                elif style == "secret":
                    hook = f"La ciencia tradicional ignoró este secreto de {title}, hasta que el microscopio lo reveló."
                else:
                    hook = f"Científicos acaban de detectar un fenómeno desconcertante dentro de {title}."
                c1_narr = sentences[0] if len(sentences) > 0 else "A nivel celular se libra una batalla invisible que mantiene todo tu organismo en equilibrio."
                c2_narr = sentences[1] if len(sentences) > 1 else "Reacciones químicas a velocidades vertiginosas dictan cómo percibes cada instante de tu realidad."
                c3_narr = "La ciencia dentro de ti es más asombrosa que cualquier ficción. ¿Qué opinas tú?"
                on_screen_1 = title[:28].upper()
                on_screen_2 = "SECRETO BIOLÓGICO"
                on_screen_3 = "REACCIÓN CELULAR"
                on_screen_4 = "¿QUÉ OPINAS TÚ?"
                kw_1 = [title.lower(), "human brain neurons firing", "microscopic biology science"]
                kw_2 = ["cell biology immune research", "chemical reaction laboratory", "dna helix science"]
                kw_3 = ["medical science research", "microscope laboratory cell", "human biology science"]
            else:  # space
                if style == "paradox":
                    hook = f"Lo que estás viendo sobre {title} desafía las leyes conocidas de la física."
                elif style == "threat":
                    hook = f"Si este colosal fenómeno en {title} ocurriera cerca, la atmósfera terrestre desaparecería."
                elif style == "secret":
                    hook = f"Los astrónomos creían que {title} era imposible, hasta que observaron este punto exacto."
                else:  # mystery
                    hook = f"Los telescopios espaciales acaban de registrar una anomalía desconcertante en {title}."
                c1_narr = sentences[0] if len(sentences) > 0 else "Los sensores astronómicos han detectado emisiones cósmicas jamás vistas."
                c2_narr = sentences[1] if len(sentences) > 1 else "Este cataclismo estelar libera una energía colosal que remodela galaxias enteras."
                c3_narr = "El cosmos oculta verdades que desafían nuestra ciencia. ¿Qué opinas tú?"
                on_screen_1 = title[:28].upper()
                on_screen_2 = "ANOMALÍA DETECTADA"
                on_screen_3 = "ENERGÍA COLOSAL"
                on_screen_4 = "¿QUÉ OPINAS TÚ?"
                kw_1 = [title.lower(), "deep space observation", "space telescope anomaly"]
                kw_2 = ["cosmic phenomenon", "astrophysics discovery", "deep space galaxy"]
                kw_3 = ["deep space universe stars", "astronomy nebula", "cosmic web"]

        elif is_en:
            if custom_hook and custom_hook.strip():
                hook = custom_hook.strip()
            elif cat == "nature":
                hook = f"What you are seeing inside {title} defies the biological laws of survival."
                c1_narr = sentences[0] if len(sentences) > 0 else "In these crushing depths, life adapts through mechanisms that seem alien."
                c2_narr = sentences[1] if len(sentences) > 1 else "Every millisecond is a brutal battle where evolution pushes past known boundaries."
                c3_narr = "Our planet holds deeper mysteries than outer space. What do you think?"
                on_screen_1 = title[:28].upper()
                on_screen_2 = "EXTREME SURVIVAL"
                on_screen_3 = "RAW FORCES"
                on_screen_4 = "WHAT DO YOU THINK?"
                kw_1 = [title.lower(), "deep sea abyss creature", "wildlife extreme 4k"]
                kw_2 = ["underwater abyss predator", "ocean trench nature", "extreme wildlife macro"]
                kw_3 = ["ocean depth underwater", "nature wilderness 4k", "marine life abyss"]
            elif cat == "tech":
                hook = f"What you are seeing inside {title} shatters the boundary of modern computing."
                c1_narr = sentences[0] if len(sentences) > 0 else "Billions of operations per microsecond process data at historic speeds."
                c2_narr = sentences[1] if len(sentences) > 1 else "This exponential breakthrough is accelerating an unprecedented technological leap."
                c3_narr = "The future is no longer science fiction: it is happening right now. What do you think?"
                on_screen_1 = title[:28].upper()
                on_screen_2 = "QUANTUM LEAP"
                on_screen_3 = "ADVANCED AI"
                on_screen_4 = "WHAT DO YOU THINK?"
                kw_1 = [title.lower(), "future technology laboratory", "artificial intelligence cyber"]
                kw_2 = ["supercomputer server room", "quantum chip processor", "robotics innovation"]
                kw_3 = ["cyber digital data", "fiber optics glow", "futuristic innovation"]
            elif cat == "history":
                hook = f"What you are seeing in {title} should not have been possible thousands of years ago."
                c1_narr = sentences[0] if len(sentences) > 0 else "Megalithic stone architecture reveals ancient engineering that baffles modern archaeology."
                c2_narr = sentences[1] if len(sentences) > 1 else "Every unearthed chamber opens deeper questions than the answers we thought we had."
                c3_narr = "The ancient past conceals lost truths we are only starting to decode. What do you think?"
                on_screen_1 = title[:28].upper()
                on_screen_2 = "ANCIENT ENIGMA"
                on_screen_3 = "LOST RUINS"
                on_screen_4 = "WHAT DO YOU THINK?"
                kw_1 = [title.lower(), "ancient ruins archaeological", "ancient pyramid monument aerial"]
                kw_2 = ["archaeology excavation tomb", "ancient stone hieroglyphs", "historic temple ruins"]
                kw_3 = ["ancient artifact museum", "historical discovery ruins", "ancient world architecture"]
            elif cat == "science":
                hook = f"What you are about to discover about {title} contradicts what you know about your body."
                c1_narr = sentences[0] if len(sentences) > 0 else "At the microscopic level, an invisible war keeps your entire physiology alive."
                c2_narr = sentences[1] if len(sentences) > 1 else "Chemical reactions at blistering speeds dictate how you perceive each second of reality."
                c3_narr = "The science within your body is stranger than fiction. What do you think?"
                on_screen_1 = title[:28].upper()
                on_screen_2 = "BIOLOGICAL SECRET"
                on_screen_3 = "CELLULAR REACTION"
                on_screen_4 = "WHAT DO YOU THINK?"
                kw_1 = [title.lower(), "human brain neurons firing", "microscopic biology science"]
                kw_2 = ["cell biology immune research", "chemical reaction laboratory", "dna helix science"]
                kw_3 = ["medical science research", "microscope laboratory cell", "human biology science"]
            else:  # space
                if style == "paradox":
                    hook = f"What you are seeing in {title} defies the known laws of physics."
                elif style == "threat":
                    hook = f"If this cosmic titan inside {title} were any closer, it would vaporize our planet."
                elif style == "secret":
                    hook = f"Astronomers believed {title} was impossible, until they looked right here."
                else:  # mystery
                    hook = f"Space telescopes just captured an unsettling cosmic anomaly inside {title}."
                c1_narr = sentences[0] if len(sentences) > 0 else "Astronomical sensors detected groundbreaking signals challenging modern physics."
                c2_narr = sentences[1] if len(sentences) > 1 else "This cosmic engine discharges colossal energy across vast regions of space."
                c3_narr = "The universe holds dark mysteries waiting to be decoded. What do you think?"
                on_screen_1 = title[:28].upper()
                on_screen_2 = "ANOMALY DETECTED"
                on_screen_3 = "COLOSSAL FORCES"
                on_screen_4 = "WHAT DO YOU THINK?"
                kw_1 = [title.lower(), "deep space observation", "space telescope anomaly"]
                kw_2 = ["cosmic phenomenon", "astrophysics discovery", "deep space galaxy"]
                kw_3 = ["deep space universe stars", "astronomy nebula", "cosmic web"]
        else:
            if custom_hook and custom_hook.strip():
                hook = custom_hook.strip()
            else:
                hook = f"关于 {title}，前沿科学刚刚捕捉到了违背常理的惊人现象！"
            c1_narr = sentences[0] if len(sentences) > 0 else "精密探测器捕获到了令人震撼的能量信号。"
            c2_narr = sentences[1] if len(sentences) > 1 else "这项突破性发现正在彻底颠覆我们对自然极限的认知。"
            c3_narr = "未知世界还有多少秘密？留下你的想法！"
            on_screen_1 = title[:20]
            on_screen_2 = "异常发现"
            on_screen_3 = "极限力量"
            on_screen_4 = "你怎么看？"
            kw_1 = [title.lower(), "science exploration documentary", "4k cinematic footage"]
            kw_2 = ["scientific phenomenon macro", "nature science discovery", "high definition exploration"]
            kw_3 = ["nature science documentary", "epic visual journey", "discovery 4k"]

        # Construct scenes adapted to target duration
        scenes = [
            {
                "scene_id": 1,
                "visual_subject": title[:30],
                "narration": hook,
                "on_screen_text": on_screen_1,
                "visual_type": "video",
                "keywords": kw_1,
                "audio_cue": "whoosh"
            },
            {
                "scene_id": 2,
                "visual_subject": on_screen_2,
                "narration": c1_narr,
                "on_screen_text": on_screen_2,
                "visual_type": "video",
                "keywords": kw_2,
                "audio_cue": "subtle_boom"
            },
            {
                "scene_id": 3,
                "visual_subject": on_screen_3,
                "narration": f"{c2_narr} {c3_narr}",
                "on_screen_text": on_screen_4,
                "visual_type": "video",
                "keywords": kw_3,
                "audio_cue": "laser"
            }
        ]

        return {
            "title": title,
            "hook": hook,
            "scenes": scenes,
            "target_duration": target_duration,
            "language": language,
            "generation_mode": f"{cat}_scientific_fallback"
        }
