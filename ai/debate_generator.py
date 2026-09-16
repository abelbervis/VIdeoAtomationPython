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

from ai.orb_reviewer import OrbScriptReviewer

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


DEBATE_SYSTEM_PROMPT = """You are the AI Showrunner and Director for 'COSMIC ORB SHOW', a viral, high-retention vertical video series featuring two sentient AI entity co-hosts represented by 3D energy orbs (Quantum and Solar).

CREATIVE FREEDOM & FLEXIBILITY RULES:
- FLEXIBLE SCENE COUNT: Produce between 3 and 6 scenes depending on what the narrative naturally requires. Do not force a rigid 4-scene structure if 3 or 5 scenes feel more organic.
- FLEXIBLE SPEAKER ORDER: Solar, Quantum, or Both can start the video! Choose whoever delivers the most compelling hook for the topic.
- OPTIONAL HOLOGRAMS/HUDS: Holograms are optional. Only include them when there is a concrete, impressive scientific metric to display. If not needed, set holograms to null or omit them.
- VARY THE CAMERA SHOTS: Use 'wide', 'close_quantum', 'close_solar', or 'both' dynamically to match the emotional cadence of each line.

CO-HOST DYNAMICS:
1. QUANTUM (Electric Cyan Orb): Analytical, curious, framing questions around geometry, simulation code, subatomic paradoxes, or intuitive mental models.
2. SOLAR (Radiant Amber Orb): Visceral, grounded, explaining real-world physical scale, thermodynamics, entropy, or stellar power.
3. COLLABORATIVE EXPLORATION: They are co-hosts and partners in discovery. DO NOT force fake hostility or insult phrases ("¡Falso!", "¡Iluso!"). They build upon each other's ideas to illuminate a single fascinating concept.

EXPLAIN LIKE I'M 12 (ELI5):
- Start within the first 3 words with an everyday analogy or a mind-bending, easy-to-visualize fact.
- Keep language direct, clear, and visually intuitive. No academic jargon or artificial poetry.

ENDING:
- Close with a thought-provoking, existential, or curious question/realization that leaves the viewer reflecting. No generic CTAs like "comment team Quantum".

Respond ONLY with valid JSON matching this schema:
{
  "topic": "Clean topic name",
  "headline_hook": "⚡ TITULO IMPACTANTE (MAX 45 CHARACTERS) ⚡",
  "holograms": {
    "quantum": {
      "title": "TITULO CORTO",
      "subtitle": "Metrica o formula concisa",
      "category": "CONCEPTO Q"
    },
    "solar": {
      "title": "TITULO CORTO",
      "subtitle": "Metrica o formula concisa",
      "category": "DATO S"
    }
  },
  "scenes": [
    {
      "speaker": "Quantum",
      "entity": "quantum",
      "text": "[Analogía o hecho contraintuitivo inicial. 10-18 palabras]",
      "shot": "wide",
      "duration": 3.2
    },
    {
      "speaker": "Solar",
      "entity": "solar",
      "text": "[Respuesta o revelación física. 10-18 palabras]",
      "shot": "close_solar",
      "duration": 3.5
    }
  ]
}
NOTE: 'holograms' can be null or omitted if metrics are not relevant. 'scenes' array can have between 3 and 6 scenes.
"""


class DebateScriptGenerator:
    """Generates dialectic debate scripts between Quantum and Solar."""

    def __init__(
        self,
        gemini_key: Optional[str] = None,
        groq_key: Optional[str] = None,
        openai_key: Optional[str] = None,
        preferred_provider: str = LLM_PROVIDER,
        enable_review: bool = True,
    ):
        raw_gemini = gemini_key if gemini_key is not None else GEMINI_API_KEY
        raw_groq = groq_key if groq_key is not None else GROQ_API_KEY
        raw_openai = openai_key if openai_key is not None else OPENAI_API_KEY

        self.gemini_key = sanitize_env_value(raw_gemini)
        self.groq_key = sanitize_env_value(raw_groq)
        self.openai_key = sanitize_env_value(raw_openai)
        self.provider = (sanitize_env_value(preferred_provider) or "auto").lower()
        self.enable_review = enable_review

        self.reviewer = OrbScriptReviewer(
            gemini_key=self.gemini_key,
            openai_key=self.openai_key,
            groq_key=self.groq_key,
            preferred_provider=self.provider
        )

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
            script = None
            if prov == "groq" and self._is_valid_key(self.groq_key):
                try:
                    print("  ⚡ Solicitando guion de debate a Groq LPU (llama-3.3-70b-versatile)...")
                    script = self._call_groq(clean_topic, language)
                except Exception as e:
                    print(f"  ⚠️ Groq debate generation error: {e}")
            elif prov == "gemini" and self._is_valid_key(self.gemini_key):
                try:
                    print("  ⚡ Solicitando guion de debate a Google Gemini...")
                    script = self._call_gemini(clean_topic, language)
                except Exception as e:
                    print(f"  ⚠️ Gemini debate generation error: {e}")
            elif prov == "openai" and self._is_valid_key(self.openai_key):
                try:
                    print("  ⚡ Solicitando guion de debate a OpenAI (gpt-4o-mini)...")
                    script = self._call_openai(clean_topic, language)
                except Exception as e:
                    print(f"  ⚠️ OpenAI debate generation error: {e}")

            if script and self._validate_debate_script(script):
                print(f"  ✨ Guion de debate generado con éxito por {prov.upper()}!")
                if self.enable_review:
                    script = self.reviewer.review(script)
                return script

        # If fallback is explicitly allowed
        if allow_fallback:
            print("  🛰️ Generando guion dialéctico con el motor científico especializado (Fallback)...")
            script = self._generate_scientific_fallback(clean_topic, language)
            if script and self.enable_review:
                script = self.reviewer.review(script)
            return script

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
                        "text": "¿Bando Cuántico o Bando Solar? ¡Defiende tu bando en los comentarios!",
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
                        "text": "¿Bando Cuántico o Bando Solar? ¡Elige tu bando en los comentarios!",
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
                        "text": "¿Bando Cuántico o Bando Solar? ¡Vota por tu bando en los comentarios!",
                        "shot": "wide",
                        "duration": 2.5
                    }
                ]
            }
