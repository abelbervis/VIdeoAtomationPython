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
from core.hosts import CosmicDebateShow, DEFAULT_QUANTUM_HOST, DEFAULT_SOLAR_HOST, OrbHost

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

# Canonical default prompt generated from the default OOP model
DEBATE_SYSTEM_PROMPT = CosmicDebateShow().build_system_prompt()


class DebateScriptGenerator:
    """Generates dialectic debate scripts using the CosmicDebateShow OOP model."""

    def __init__(
        self,
        gemini_key: Optional[str] = None,
        groq_key: Optional[str] = None,
        openai_key: Optional[str] = None,
        preferred_provider: str = LLM_PROVIDER,
        enable_review: bool = True,
        show: Optional[CosmicDebateShow] = None,
        host_a: Optional[OrbHost] = None,
        host_b: Optional[OrbHost] = None,
    ):
        raw_gemini = gemini_key if gemini_key is not None else GEMINI_API_KEY
        raw_groq = groq_key if groq_key is not None else GROQ_API_KEY
        raw_openai = openai_key if openai_key is not None else OPENAI_API_KEY

        self.gemini_key = sanitize_env_value(raw_gemini)
        self.groq_key = sanitize_env_value(raw_groq)
        self.openai_key = sanitize_env_value(raw_openai)
        self.provider = (sanitize_env_value(preferred_provider) or "auto").lower()
        self.enable_review = enable_review

        # OOP Show Model with injected variables
        self.show = show or CosmicDebateShow(
            host_a=host_a or DEFAULT_QUANTUM_HOST,
            host_b=host_b or DEFAULT_SOLAR_HOST
        )

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
        system_prompt = self.show.build_system_prompt(topic)
        full_prompt = (
            f"{system_prompt}\n\n"
            f"Topic for Script: {topic}\n"
            f"Language: Spanish (Español)\n"
            f"Generate the JSON script following all narrative continuity rules and schema:"
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
        system_prompt = self.show.build_system_prompt(topic)
        url = f"{GROQ_API_BASE}/chat/completions"
        payload = {
            "model": GROQ_MODEL or "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
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
        system_prompt = self.show.build_system_prompt(topic)
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
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

        # Ensure contextual roles are present and within clean character limits
        if "roles" not in script or not isinstance(script["roles"], dict):
            script["roles"] = {
                self.show.host_a.id: self.show.host_a.role,
                self.show.host_b.id: self.show.host_b.role,
            }
        else:
            for k in list(script["roles"].keys()):
                val = str(script["roles"][k]).strip()
                if len(val) > 30:
                    script["roles"][k] = val[:28]
        return True

    def _generate_scientific_fallback(self, topic: str, language: str = "es") -> Dict[str, Any]:
        """High quality deterministic fallback embodying two equal cosmic orbs with opposing temperaments."""
        topic_lower = topic.lower()

        if "simula" in topic_lower or "matrix" in topic_lower or "codigo" in topic_lower:
            return {
                "topic": "¿Es el universo una simulación?",
                "headline_hook": "⚡ ¿EL UNIVERSO ES UNA SIMULACIÓN? ⚡",
                "roles": {
                    self.show.host_a.id: "Mente Fría // Lógica",
                    self.show.host_b.id: "Energía Viva // Pasión"
                },
                "holograms": {
                    "quantum": {
                        "title": "LÍMITE DE PLANCK",
                        "subtitle": "Resolución Mínima: 1.6x10⁻³⁵ m",
                        "category": "CÓDIGO Q"
                    },
                    "solar": {
                        "title": "FUEGO TERMODINÁMICO",
                        "subtitle": "Entropía Irreversible: 10²² J/K",
                        "category": "FUERZA S"
                    }
                },
                "scenes": [
                    {
                        "speaker": self.show.host_a.name,
                        "entity": self.show.host_a.id,
                        "text": "Toda la materia visible se reduce a información pura en la escala de Planck.",
                        "shot": "wide",
                        "duration": 3.2
                    },
                    {
                        "speaker": self.show.host_b.name,
                        "entity": self.show.host_b.id,
                        "text": "¡Reduccionismo frío! Una supernova no es código: es energía viva devastando el espacio.",
                        "shot": self.show.host_b.shot_name,
                        "duration": 3.4
                    },
                    {
                        "speaker": self.show.host_a.name,
                        "entity": self.show.host_a.id,
                        "text": "Esa energía obedece a las mismas ecuaciones matemáticas que programan un fotón.",
                        "shot": self.show.host_a.shot_name,
                        "duration": 3.4
                    },
                    {
                        "speaker": self.show.host_b.name,
                        "entity": self.show.host_b.id,
                        "text": "Pero las matemáticas no sienten el ardor de existir; nosotros sí.",
                        "shot": self.show.host_b.shot_name,
                        "duration": 3.2
                    },
                    {
                        "speaker": "BOTH",
                        "entity": "both",
                        "text": "Dos miradas opuestas tratando de descifrar el mismo enigma cósmico.",
                        "shot": "both",
                        "duration": 3.0
                    }
                ]
            }
        elif "tiempo" in topic_lower or "gravedad" in topic_lower or "relativ" in topic_lower:
            return {
                "topic": "La Paradoja del Tiempo",
                "headline_hook": "⚡ ¿EL TIEMPO ES UNA ILUSIÓN FÍSICA? ⚡",
                "roles": {
                    self.show.host_a.id: "Mente Fría // Lógica",
                    self.show.host_b.id: "Energía Viva // Pasión"
                },
                "holograms": {
                    "quantum": {
                        "title": "UNIVERSO BLOQUE",
                        "subtitle": "Espacio-Tiempo Cuatridimensional",
                        "category": "ESTÁTICO Q"
                    },
                    "solar": {
                        "title": "FLECHA TERMODINÁMICA",
                        "subtitle": "Incremento de Entropía ΔS > 0",
                        "category": "DINÁMICO S"
                    }
                },
                "scenes": [
                    {
                        "speaker": self.show.host_a.name,
                        "entity": self.show.host_a.id,
                        "text": "El tiempo no fluye: es solo una dimensión congelada en el tejido cósmico.",
                        "shot": "wide",
                        "duration": 3.2
                    },
                    {
                        "speaker": self.show.host_b.name,
                        "entity": self.show.host_b.id,
                        "text": "Dile eso al fuego de una estrella consumiendo su combustible segundo a segundo.",
                        "shot": self.show.host_b.shot_name,
                        "duration": 3.3
                    },
                    {
                        "speaker": self.show.host_a.name,
                        "entity": self.show.host_a.id,
                        "text": "Tu fuego es solo entropía: la ilusión de cambio en una geometría inmóvil.",
                        "shot": self.show.host_a.shot_name,
                        "duration": 3.5
                    },
                    {
                        "speaker": self.show.host_b.name,
                        "entity": self.show.host_b.id,
                        "text": "Pero esa ilusión es la única que engendra la vida, el calor y la conciencia.",
                        "shot": self.show.host_b.shot_name,
                        "duration": 3.2
                    },
                    {
                        "speaker": "BOTH",
                        "entity": "both",
                        "text": "El cosmos necesita tanto el silencio del espacio como la furia del fuego.",
                        "shot": "both",
                        "duration": 3.2
                    }
                ]
            }
        else:
            # Generic dynamic fallback
            clean_title = topic.upper()
            return {
                "topic": topic,
                "headline_hook": f"⚡ ENIGMA: {clean_title[:32]} ⚡",
                "roles": {
                    self.show.host_a.id: self.show.host_a.role,
                    self.show.host_b.id: self.show.host_b.role
                },
                "holograms": None,
                "scenes": [
                    {
                        "speaker": self.show.host_a.name,
                        "entity": self.show.host_a.id,
                        "text": f"Detrás de {topic} se esconde una estructura matemática fría e impenetrable.",
                        "shot": "wide",
                        "duration": 3.2
                    },
                    {
                        "speaker": self.show.host_b.name,
                        "entity": self.show.host_b.id,
                        "text": "No intentes congelar con fórmulas lo que el universo creó como pura fuerza viva.",
                        "shot": self.show.host_b.shot_name,
                        "duration": 3.4
                    },
                    {
                        "speaker": self.show.host_a.name,
                        "entity": self.show.host_a.id,
                        "text": "Sin esa estructura formal, tu fuerza viva colapsaría en el caos absoluto.",
                        "shot": self.show.host_a.shot_name,
                        "duration": 3.4
                    },
                    {
                        "speaker": self.show.host_b.name,
                        "entity": self.show.host_b.id,
                        "text": "Y sin esta energía ardiente, tu estructura no sería más que un museo vacío.",
                        "shot": self.show.host_b.shot_name,
                        "duration": 3.3
                    },
                    {
                        "speaker": "BOTH",
                        "entity": "both",
                        "text": "En el choque de nuestras visiones se enciende la verdadera comprensión.",
                        "shot": "both",
                        "duration": 3.2
                    }
                ]
            }
