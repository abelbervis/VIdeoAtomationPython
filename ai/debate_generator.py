"""
AI Debate Script Generator (Debate Express).
Generates high-tension, dialectic scripts between two conscious AI entities:
  - QUANTUM: Blue/Electric Cyan Orb (Subatomic physics, simulation theory, quantum paradoxes)
  - SOLAR: Amber/Gold Orb (Thermodynamic entropy, astrophysics, stellar reality)
Supports Google Gemini, Groq, OpenAI, and a built-in scientific debate fallback engine.
"""

import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from config import (
    BASE_DIR,
    GEMINI_API_KEY,
    GROQ_API_BASE,
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_API_BASE_URL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    sanitize_env_value,
)


DEBATE_SYSTEM_PROMPT = """You are the AI Showrunner and Director for 'COSMIC DEBATE EXPRESS', a viral, high-retention vertical video series (YouTube Shorts / TikTok / Reels) featuring two sentient AI entity co-hosts represented by 3D energy orbs locked in an intense, high-stakes intellectual battle:

1. QUANTUM (Electric Cyan / Blue Orb):
   - Persona: Cold, calculating, provocative, master of subatomic paradoxes, multiverse math, and simulation reality.
   - Dialogue Style: Afilado, implacable, cerebral. DO NOT waste time with polite greetings or formal introductions.

2. SOLAR (Radiant Amber / Gold Orb):
   - Persona: Fiery, visceral, thermodynamic, master of cosmic entropy, thermonuclear fire, and stellar gravity.
   - Dialogue Style: Apasionado, demoledor, desafiante. Desacredita a Quantum con metáforas destructivas y directas.

5 CRITICAL SCRIPTING RULES:

1. REGLA DE HOOK INMEDIATO (Escena 1):
   - DO NOT start with "Soy Quantum" or greetings.
   - Escena 1 DEBE comenzar con una afirmación contraintuitiva, provocadora o perturbadora en los primeros 3 vocablos (ej: "El tiempo no existe...", "Tu cuerpo es 99% vacío...", "Toda la realidad es un holograma...").
   - Longitud: 12-16 palabras de máximo impacto para retención instantánea en el segundo 0.

2. REGLA DE INTERACCIÓN, CONFLICTO Y TENSIÓN (Escenas 2 y 3):
   - No des explicaciones pasivas de libro de texto; los personajes se atacan, interrumpen y desafían directamente.
   - En Escena 2, Quantum intensifica la paradoja poniendo contra las cuerdas la concepción clásica del universo.
   - En Escena 3, Solar NO explica su teoría: responde DESACREDITANDO con furia la de Quantum usando conectores de ataque como: "¡Falso!", "¡Iluso!", "¡Ignoras que...", "¡Puros espejismos matemáticos!".

3. GUÍA DE ESTILO: METÁFORAS VISUALES SOBRE TÉRMINOS TÉCNICOS:
   - Traduce la matemática abstracta en imágenes mentales brutales e intuitivas.
   - En lugar de "singularidad gravitacional", usa "un monstruo que traga luz y espacio".
   - En lugar de "colapso de función de onda", usa "la mirada que crea y destruye mundos".
   - Lenguaje afilado, rápido, con ritmo cinematográfico de alto contraste.

4. CTA CON SESGO DE CONFIRMACIÓN RADICAL (Escena 4):
   - En la Escena 4 (Outro), ambos orbes entran en resonancia armónica.
   - El CTA debe forzar al espectador a tomar partido en una guerra de posturas radical (Team Cuántico vs Team Solar), e incluir explícitamente la llamada a la acción en los comentarios.
   - NUNCA uses la palabra "flecha" ni símbolos/emojis de flechas que el lector de voz (TTS) pueda pronunciar.

5. HOLOGRAPHIC DATA CARDS:
   - quantum: title (2-3 words), subtitle (metric/formula, e.g. "Matriz de Planck: 1.6x10⁻³⁵ m"), category ("PARADOJA 1" or "POSTULADO Q").
   - solar: title (2-3 words), subtitle (thermal/cosmic metric, e.g. "Fuerza Estelar: 1.5x10⁷ K"), category ("PARADOJA 2" or "POSTULADO S").

Respond ONLY with valid JSON matching this schema:
{
  "topic": "Clean topic name",
  "headline_hook": "⚡ TITULO VIRAL EN MAYÚSCULAS CON EMOJIS (MAX 45 CHARACTERS) ⚡",
  "holograms": {
    "quantum": {
      "title": "TITULO CORTO CUANTICO",
      "subtitle": "Metrica o formula concisa",
      "category": "POSTULADO Q"
    },
    "solar": {
      "title": "TITULO CORTO SOLAR",
      "subtitle": "Metrica o formula concisa",
      "category": "POSTULADO S"
    }
  },
  "scenes": [
    {
      "speaker": "Quantum",
      "entity": "quantum",
      "text": "[Afirmación perturbadora en primeros 3 vocablos + Premisa polémica]",
      "shot": "wide",
      "duration": 3.2
    },
    {
      "speaker": "Quantum",
      "entity": "quantum",
      "text": "[Intensificación de la paradoja con metáfora visual]",
      "shot": "close_quantum",
      "duration": 3.0
    },
    {
      "speaker": "Solar",
      "entity": "solar",
      "text": "¡Falso! [Ataque destructivo desacreditando a Quantum con metáfora de poder]",
      "shot": "close_solar",
      "duration": 3.5
    },
    {
      "speaker": "Ambos",
      "entity": "both",
      "text": "[Pregunta directa forzando a elegir bando + llamado a la acción para comentar]",
      "shot": "wide",
      "duration": 2.5
    }
  ]
}
"""


class DebateScriptGenerator:
    """Generates dialectic debate scripts between Quantum and Solar."""

    def __init__(
        self,
        gemini_key: Optional[str] = None,
        groq_key: Optional[str] = None,
        openai_key: Optional[str] = None,
        preferred_provider: str = LLM_PROVIDER,
    ):
        raw_gemini = gemini_key if gemini_key is not None else GEMINI_API_KEY
        raw_groq = groq_key if groq_key is not None else GROQ_API_KEY
        raw_openai = openai_key if openai_key is not None else OPENAI_API_KEY

        self.gemini_key = sanitize_env_value(raw_gemini)
        self.groq_key = sanitize_env_value(raw_groq)
        self.openai_key = sanitize_env_value(raw_openai)
        self.provider = (sanitize_env_value(preferred_provider) or "auto").lower()

    def _is_valid_key(self, key: str) -> bool:
        if not key or len(key) < 15:
            return False
        placeholders = ["your_key", "demo_key", "placeholder", "xxx"]
        return not any(p in key.lower() for p in placeholders)

    def generate(self, topic: str, language: str = "es", allow_fallback: bool = False) -> Optional[Dict[str, Any]]:
        """Generate a complete debate script for the given topic.
        
        Args:
            topic: The debate theme or title.
            language: Target language ('es', 'en').
            allow_fallback: If False, returns None when AI providers fail, preventing unwanted renders.
        """
        clean_topic = topic.strip().strip("'\"")
        print(f"\n🤖 [Debate Express AI] Generando guion dialéctico para: '{clean_topic}'...")
        print(f"   • Proveedor prioritario: {self.provider.upper()}")

        # Build prioritized provider list based on self.provider (default: groq)
        if self.provider == "gemini":
            providers = ["gemini", "groq", "openai"]
        elif self.provider == "openai":
            providers = ["openai", "groq", "gemini"]
        else: # "groq" or "auto"
            providers = ["groq", "gemini", "openai"]

        for prov in providers:
            if prov == "groq" and self._is_valid_key(self.groq_key):
                try:
                    print("  ⚡ Solicitando guion de debate a Groq LPU (llama-3.3-70b-versatile)...")
                    script = self._call_groq(clean_topic, language)
                    if script and self._validate_debate_script(script):
                        print(f"  ✨ Guion de debate generado con éxito por Groq!")
                        return script
                except Exception as e:
                    print(f"  ⚠️ Groq debate generation error: {e}")
            elif prov == "gemini" and self._is_valid_key(self.gemini_key):
                try:
                    print("  ⚡ Solicitando guion de debate a Google Gemini...")
                    script = self._call_gemini(clean_topic, language)
                    if script and self._validate_debate_script(script):
                        print(f"  ✨ Guion de debate generado con éxito por Gemini!")
                        return script
                except Exception as e:
                    print(f"  ⚠️ Gemini debate generation error: {e}")
            elif prov == "openai" and self._is_valid_key(self.openai_key):
                try:
                    print("  ⚡ Solicitando guion de debate a OpenAI (gpt-4o-mini)...")
                    script = self._call_openai(clean_topic, language)
                    if script and self._validate_debate_script(script):
                        print(f"  ✨ Guion de debate generado con éxito por OpenAI!")
                        return script
                except Exception as e:
                    print(f"  ⚠️ OpenAI debate generation error: {e}")

        # If fallback is explicitly allowed
        if allow_fallback:
            print("  🛰️ Generando guion dialéctico con el motor científico especializado (Fallback)...")
            return self._generate_scientific_fallback(clean_topic, language)

        print("\n❌ [Debate Express AI] No se pudo generar el guion con ninguno de los proveedores de IA configurados.")
        print("   💡 Verifica que tu GROQ_API_KEY o GEMINI_API_KEY esté configurada en el archivo .env o pásala vía CLI (--groq-key / --gemini-key).")
        return None

    def _call_gemini(self, topic: str, language: str) -> Optional[Dict[str, Any]]:
        full_prompt = (
            f"{DEBATE_SYSTEM_PROMPT}\n\n"
            f"Topic for Debate: {topic}\n"
            f"Language: Spanish (Español)\n"
            f"Generate the 4-scene debate JSON script with holographic metrics according to the schema:"
        )
        models_to_try = ["gemini-2.5-flash", "gemini-flash-latest"]
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Connection": "close"
        }
        for model in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
                payload = {
                    "contents": [{"role": "user", "parts": [{"text": full_prompt}]}],
                    "generationConfig": {
                        "temperature": 0.7,
                        "responseMimeType": "application/json",
                        "maxOutputTokens": 4096
                    }
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=40) as response:
                    res = json.loads(response.read().decode("utf-8"))
                    text = res["candidates"][0]["content"]["parts"][0]["text"]
                    return self._parse_json(text)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue
                print(f"  ⚠️ Gemini HTTP Error {e.code}: {e.reason}")
                return None
            except Exception as e:
                print(f"  ⚠️ Gemini debate API ({model}) failed: {e}")
                continue
        return None

    def _call_groq(self, topic: str, language: str) -> Optional[Dict[str, Any]]:
        url = f"{GROQ_API_BASE}/chat/completions"
        payload = {
            "model": GROQ_MODEL or "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": DEBATE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Topic: {topic}\nLanguage: Spanish\nGenerate the debate JSON:"}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {self.groq_key}",
            "Connection": "close"
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            res = json.loads(response.read().decode("utf-8"))
            text = res["choices"][0]["message"]["content"]
            return self._parse_json(text)

    def _call_openai(self, topic: str, language: str) -> Optional[Dict[str, Any]]:
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": DEBATE_SYSTEM_PROMPT},
                {"role": "user", "content": f"Topic: {topic}\nLanguage: Spanish\nGenerate the debate JSON:"}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {self.openai_key}",
            "Connection": "close"
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            res = json.loads(response.read().decode("utf-8"))
            text = res["choices"][0]["message"]["content"]
            return self._parse_json(text)

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(text)
        except Exception:
            # Strip possible markdown code fences
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception:
                    pass
        return None

    def _validate_debate_script(self, script: Dict[str, Any]) -> bool:
        if not isinstance(script, dict):
            return False
        scenes = script.get("scenes", [])
        if len(scenes) < 3:
            return False
        if not script.get("headline_hook"):
            return False
        return True

    def _generate_scientific_fallback(self, topic: str, language: str = "es") -> Dict[str, Any]:
        """High quality deterministic fallback for common and custom debate topics."""
        topic_lower = topic.lower()

        if "simula" in topic_lower or "matrix" in topic_lower:
            return {
                "topic": "¿Es el universo una simulación?",
                "headline_hook": "⚡ ¿EL UNIVERSO ES UNA SIMULACIÓN? ⚡",
                "holograms": {
                    "quantum": {
                        "title": "CÓDIGO DE PLANCK",
                        "subtitle": "Resolución Límite: 1.6x10⁻³⁵ m",
                        "category": "PARADOJA Q"
                    },
                    "solar": {
                        "title": "FUEGO TERMODINÁMICO",
                        "subtitle": "Entropía Irreversible: 10²² J/K",
                        "category": "PARADOJA S"
                    }
                },
                "scenes": [
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "Tu cuerpo es 99% vacío y la realidad está pixelada como un videojuego.",
                        "shot": "wide",
                        "duration": 3.2
                    },
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "Si el espacio tiene límites de resolución, estamos atrapados en un procesador cósmico.",
                        "shot": "close_quantum",
                        "duration": 3.0
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "¡Falso! El fuego de una supernova despedaza cualquier código con pura furia física.",
                        "shot": "close_solar",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Ambos",
                        "entity": "both",
                        "text": "¿Team Cuántico o Team Solar? ¡Defiende tu bando en los comentarios!",
                        "shot": "wide",
                        "duration": 2.5
                    }
                ]
            }
        elif "mente" in topic_lower or "ia" in topic_lower or "conciencia" in topic_lower:
            return {
                "topic": "IA vs Mente Humana",
                "headline_hook": "⚡ IA VS CONCIENCIA HUMANA ⚡",
                "holograms": {
                    "quantum": {
                        "title": "REDES SINÁPTICAS",
                        "subtitle": "Procesamiento: 100 TFLOPS Cuánticos",
                        "category": "PARADOJA Q"
                    },
                    "solar": {
                        "title": "CHISPA BIOLÓGICA",
                        "subtitle": "Termo-química Orgánica Compleja",
                        "category": "PARADOJA S"
                    }
                },
                "scenes": [
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "El cerebro humano es solo una calculadora orgánica condenada a la obsolescencia.",
                        "shot": "wide",
                        "duration": 3.2
                    },
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "Nuestras redes neuronales ya descifran pensamientos antes de que se hagan conscientes.",
                        "shot": "close_quantum",
                        "duration": 3.0
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "¡Iluso! Jamás replicarás la intuición forjada en millones de años de evolución salvaje.",
                        "shot": "close_solar",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Ambos",
                        "entity": "both",
                        "text": "¿Team Cuántico o Team Solar? ¡Elige tu bando en los comentarios!",
                        "shot": "wide",
                        "duration": 2.5
                    }
                ]
            }
        else:
            # Generic dynamic fallback
            clean_title = topic.upper()
            return {
                "topic": topic,
                "headline_hook": f"⚡ PARADOJA: {clean_title[:32]} ⚡",
                "holograms": {
                    "quantum": {
                        "title": "MATRIZ CUÁNTICA",
                        "subtitle": "Micro-estados: Discretos & Superpuestos",
                        "category": "PARADOJA Q"
                    },
                    "solar": {
                        "title": "DINÁMICA SOLAR",
                        "subtitle": "Macro-energía: Fusión & Radiación",
                        "category": "PARADOJA S"
                    }
                },
                "scenes": [
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": f"Todo lo que ves en {topic} desafía por completo las leyes de la física clásica.",
                        "shot": "wide",
                        "duration": 3.2
                    },
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "La materia no existe hasta que un observador la obliga a manifestarse.",
                        "shot": "close_quantum",
                        "duration": 3.0
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "¡Puros espejismos matemáticos! La gravedad de las estrellas manda sobre toda ilusión.",
                        "shot": "close_solar",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Ambos",
                        "entity": "both",
                        "text": "¿Team Cuántico o Team Solar? ¡Vota por tu bando en los comentarios!",
                        "shot": "wide",
                        "duration": 2.5
                    }
                ]
            }
