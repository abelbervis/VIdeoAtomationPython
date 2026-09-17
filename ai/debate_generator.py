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
from core.domains import DomainRegistry, TopicDomain
from core.prompt_builder import DebatePromptBuilder
from core.script_models import DebateScript

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

            if script and self._validate_debate_script(script, clean_topic):
                print(f"  ✨ Guion de debate generado con éxito por {prov.upper()}!")
                if self.enable_review:
                    script = self.reviewer.review(script, topic=clean_topic, show=self.show)
                return script

        # If fallback is explicitly allowed
        if allow_fallback:
            print("  🛰️ Generando guion dialéctico con el motor científico especializado (Fallback)...")
            script = self._generate_scientific_fallback(clean_topic, language)
            if script and self.enable_review:
                script = self.reviewer.review(script, topic=clean_topic, show=self.show)
            return script

        print("\n❌ [Debate Express AI] No se pudo generar el guion con ninguno de los proveedores de IA configurados.")
        print("   💡 Verifica que tu GROQ_API_KEY o GEMINI_API_KEY esté configurada en el archivo .env o pásala vía CLI (--groq-key / --gemini-key).")
        return None

    def _call_gemini(self, topic: str, language: str) -> Optional[Dict[str, Any]]:
        builder = DebatePromptBuilder(topic).with_show(self.show)
        system_prompt = builder.build_system_prompt()
        user_prompt = builder.build_user_prompt(language)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

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
        builder = DebatePromptBuilder(topic).with_show(self.show)
        system_prompt = builder.build_system_prompt()
        user_prompt = builder.build_user_prompt(language)

        url = f"{GROQ_API_BASE}/chat/completions"
        payload = {
            "model": GROQ_MODEL or "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
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
        builder = DebatePromptBuilder(topic).with_show(self.show)
        system_prompt = builder.build_system_prompt()
        user_prompt = builder.build_user_prompt(language)

        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
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

    def _clean_and_sanitize_scenes(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Encapsulated OOP structure sanitization via DebateScript model."""
        if not script or not isinstance(script, dict):
            return script
        script_obj = DebateScript.from_dict(script)
        script_obj.sanitize_structure(self.show.host_a, self.show.host_b)
        sanitized = script_obj.to_dict()
        script.clear()
        script.update(sanitized)
        return script

    def _validate_debate_script(self, script: Dict[str, Any], topic: Optional[str] = None) -> bool:
        if not isinstance(script, dict):
            return False
        
        # Clean closing scenes and camera alignments before validation
        self._clean_and_sanitize_scenes(script)

        topic_name = script.get("topic") or topic
        script_obj = DebateScript.from_dict(script, default_topic=topic_name)
        domain = self.show.get_domain(topic_name)

        # Ensure dynamic topic-tailored AI professions are present and valid
        inferred_roles = self.show.infer_topic_professions(topic_name)
        if not script_obj.roles:
            script_obj.roles = inferred_roles
        else:
            for k in list(script_obj.roles.keys()):
                val = str(script_obj.roles[k]).strip()
                if len(val) > 30:
                    script_obj.roles[k] = val[:28]
            if self.show.host_a.id not in script_obj.roles:
                script_obj.roles[self.show.host_a.id] = inferred_roles.get(self.show.host_a.id, self.show.host_a.role)
            if self.show.host_b.id not in script_obj.roles:
                script_obj.roles[self.show.host_b.id] = inferred_roles.get(self.show.host_b.id, self.show.host_b.role)

        # Validate with OOP model (length, single closure, camera matches, domain contamination)
        is_valid, errors = script_obj.validate(domain=domain, host_a=self.show.host_a, host_b=self.show.host_b)
        if not is_valid:
            print(f"  ⚠️ [Script Validation Check]: {', '.join(errors)}")
            if len(script_obj.scenes) < 7 or not script_obj.headline_hook:
                return False

        # Sync back sanitized state to dict
        script.clear()
        script.update(script_obj.to_dict())
        return True

    def _generate_scientific_fallback(self, topic: str, language: str = "es") -> Dict[str, Any]:
        """High quality deterministic fallback for common and custom debate topics."""
        topic_lower = topic.lower()
        topic_roles = self.show.infer_topic_professions(topic)

        if "simula" in topic_lower or "matrix" in topic_lower:
            return {
                "topic": "¿Es el universo una simulación?",
                "headline_hook": "⚡ ¿EL UNIVERSO ES UNA SIMULACIÓN? ⚡",
                "roles": topic_roles,
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
                        "text": "El espacio físico no es continuo: tiene píxeles mínimos llamados longitud de Planck.",
                        "shot": "wide",
                        "duration": 3.2
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "Tener un límite discreto no prueba una simulación; solo describe la geometría del vacío.",
                        "shot": "close_solar",
                        "duration": 3.4
                    },
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "Pero la velocidad de la luz funciona exactamente como la tasa máxima de refresco de un procesador.",
                        "shot": "close_quantum",
                        "duration": 3.3
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "Esa velocidad preserva la causalidad para que la energía y la masa no colapsen el cosmos.",
                        "shot": "close_solar",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "En mecánica cuántica, las partículas solo eligen posición cuando un observador mide el sistema.",
                        "shot": "close_quantum",
                        "duration": 3.4
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "El universo existió miles de millones de años antes de que surgiera el primer observador consciente.",
                        "shot": "close_solar",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Ambos",
                        "entity": "both",
                        "text": "¿Estamos viviendo dentro de la física fundamental o dentro del código de una superinteligencia?",
                        "shot": "both",
                        "duration": 3.2
                    }
                ]
            }
        elif any(w in topic_lower for w in ["mente", "cerebro", "conciencia", "inteligencia artificial", "redes neuronales"]) or re.search(r"\b(ia|ai)\b", topic_lower):
            return {
                "topic": "IA vs Mente Humana",
                "headline_hook": "⚡ IA VS CONCIENCIA HUMANA ⚡",
                "roles": topic_roles,
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
                        "text": "El cerebro humano es un circuito electroquímico predecible que procesa entradas y genera respuestas.",
                        "shot": "wide",
                        "duration": 3.2
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "Ese circuito produce experiencias subjetivas y emociones cualitativas que ningún algoritmo puede sentir.",
                        "shot": "close_solar",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "Toda emoción humana se reduce a gradientes químicos y patrones de disparo neuronal medibles.",
                        "shot": "close_quantum",
                        "duration": 3.2
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "Medir el patrón biológico no explica por qué existe el dolor o la autoconciencia interna.",
                        "shot": "close_solar",
                        "duration": 3.4
                    },
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "Cuando una red neuronal alcanza suficiente densidad sináptica, la autoconciencia emerge como cálculo.",
                        "shot": "close_quantum",
                        "duration": 3.4
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "Simular una tormenta digital no moja; simular el pensamiento no crea una mente viva.",
                        "shot": "close_solar",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Ambos",
                        "entity": "both",
                        "text": "¿La conciencia es el algoritmo supremo o el misterio irreductible del universo?",
                        "shot": "both",
                        "duration": 3.2
                    }
                ]
            }
        elif any(w in topic_lower for w in ["biolog", "genétic", "genom", "evoluc", "celular", "célula", "virus", "clonac"]) or re.search(r"\b(gen|genes|adn|dna|bio)\b", topic_lower):
            return {
                "topic": f"El Enigma Biológico: {topic.strip()}",
                "headline_hook": f"⚡ EL SECRETO DEL ADN: {topic.upper()[:24]} ⚡",
                "roles": topic_roles,
                "holograms": None,
                "scenes": [
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": f"El código biológico detrás de {topic} opera como un sistema de información estructurado y preciso.",
                        "shot": "wide",
                        "duration": 3.2
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "Pero la vida no es un programa rígido; responde a presiones ambientales y epigenéticas dinámicas.",
                        "shot": "close_solar",
                        "duration": 3.4
                    },
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "Aun así, las secuencias moleculares determinan los límites fundamentales de cada organismo.",
                        "shot": "close_quantum",
                        "duration": 3.4
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "La evolución demuestra que la flexibilidad adaptativa es más poderosa que cualquier secuencia fija.",
                        "shot": "close_solar",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "Si desciframos todas las instrucciones moleculares, podríamos reprogramar los límites de la vida.",
                        "shot": "close_quantum",
                        "duration": 3.3
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "Intervenir sistemas vivos tan complejos suele desatar consecuencias imprevistas e incontrolables.",
                        "shot": "close_solar",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Ambos",
                        "entity": "both",
                        "text": "¿Somos el resultado de un código estricto o de una constante reinvención adaptativa?",
                        "shot": "both",
                        "duration": 3.2
                    }
                ]
            }
        else:
            # Generic dynamic fallback - neutral and domain-agnostic
            clean_title = topic.upper()
            return {
                "topic": topic,
                "headline_hook": f"⚡ EL GRAN DILEMA: {clean_title[:28]} ⚡",
                "roles": topic_roles,
                "holograms": None,
                "scenes": [
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": f"El análisis sistemático de {topic} revela un dilema profundo que desafía lo que creíamos saber.",
                        "shot": "wide",
                        "duration": 3.2
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "Ese dilema surge al confundir modelos teóricos con el comportamiento real del fenómeno en la práctica.",
                        "shot": "close_solar",
                        "duration": 3.4
                    },
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "Sin embargo, los datos empíricos demuestran que las variables clave contradicen las explicaciones clásicas.",
                        "shot": "close_quantum",
                        "duration": 3.4
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "La aparente contradicción se resuelve si observamos el sistema como un todo dinámico y no como piezas aisladas.",
                        "shot": "close_solar",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Quantum",
                        "entity": "quantum",
                        "text": "Aun así, si esta evidencia se confirma, obligaría a replantear los fundamentos mismos de esta disciplina.",
                        "shot": "close_quantum",
                        "duration": 3.4
                    },
                    {
                        "speaker": "Solar",
                        "entity": "solar",
                        "text": "Esa tensión constante entre certeza y descubrimiento es exactamente lo que impulsa el avance del conocimiento.",
                        "shot": "close_solar",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Ambos",
                        "entity": "both",
                        "text": "¿Hacia qué postura te inclinas al reflexionar sobre este dilema?",
                        "shot": "both",
                        "duration": 3.0
                    }
                ]
            }
