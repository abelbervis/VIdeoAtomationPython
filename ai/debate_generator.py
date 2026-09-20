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

            if script and self._validate_debate_script(script, clean_topic):
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

    def _clean_and_sanitize_scenes(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures single unified closing scene and prevents wide/both shots on penultimate scene."""
        if not script or not isinstance(script.get("scenes"), list):
            return script

        scenes = script["scenes"]
        if not scenes:
            return script

        cleaned_scenes = []
        i = 0
        while i < len(scenes):
            curr = scenes[i]
            is_curr_both = (
                str(curr.get("speaker", "")).strip().lower() in ["ambos", "both"]
                or str(curr.get("entity", "")).strip().lower() == "both"
            )

            # Check if next scene is ALSO both
            if is_curr_both and i + 1 < len(scenes):
                nxt = scenes[i + 1]
                is_nxt_both = (
                    str(nxt.get("speaker", "")).strip().lower() in ["ambos", "both"]
                    or str(nxt.get("entity", "")).strip().lower() == "both"
                )
                if is_nxt_both:
                    # Merge consecutive both scenes into one single final scene
                    merged_text = curr.get("text", "").strip()
                    nxt_text = nxt.get("text", "").strip()
                    if nxt_text and nxt_text not in merged_text:
                        merged_text = f"{merged_text} {nxt_text}"
                    merged_dur = round(min(5.5, max(3.0, float(curr.get("duration", 3.2)) + float(nxt.get("duration", 3.2)) * 0.7)), 1)
                    merged_scene = {
                        "speaker": "Ambos",
                        "entity": "both",
                        "text": merged_text,
                        "shot": "both",
                        "duration": merged_dur
                    }
                    cleaned_scenes.append(merged_scene)
                    i += 2
                    continue

            cleaned_scenes.append(curr)
            i += 1

        # Enforce rule: Penultimate scene cannot be 'both' or wide shot
        if len(cleaned_scenes) >= 2:
            penultimate = cleaned_scenes[-2]
            last = cleaned_scenes[-1]
            last_is_both = (
                str(last.get("speaker", "")).strip().lower() in ["ambos", "both"]
                or str(last.get("entity", "")).strip().lower() == "both"
            )
            if last_is_both:
                # If penultimate was accidentally labeled both/wide, assign to previous opposite entity
                penult_entity = str(penultimate.get("entity", "")).strip().lower()
                if penult_entity == "both" or str(penultimate.get("speaker", "")).strip().lower() in ["ambos", "both"]:
                    # Assign to host_b or host_a
                    assigned_host = self.show.host_b if len(cleaned_scenes) % 2 == 0 else self.show.host_a
                    penultimate["speaker"] = assigned_host.name
                    penultimate["entity"] = assigned_host.id
                    penultimate["shot"] = assigned_host.shot_name
                elif penultimate.get("shot") in ["wide", "both"]:
                    # Fix shot to match the solo speaker
                    if penult_entity == self.show.host_a.id:
                        penultimate["shot"] = self.show.host_a.shot_name
                    elif penult_entity == self.show.host_b.id:
                        penultimate["shot"] = self.show.host_b.shot_name
                    else:
                        penultimate["shot"] = self.show.host_b.shot_name

        script["scenes"] = cleaned_scenes
        return script

    def _validate_debate_script(self, script: Dict[str, Any], topic: Optional[str] = None) -> bool:
        if not isinstance(script, dict):
            return False
        
        # Clean closing scenes before validation
        self._clean_and_sanitize_scenes(script)

        scenes = script.get("scenes", [])
        if len(scenes) < 4:
            return False
        if not script.get("headline_hook"):
            return False

        roles = script.get("roles")
        if not roles or not isinstance(roles, dict) or len(roles) < 2:
            return False
        
        role_a_val = str(roles.get(self.show.host_a.id, "")).strip().lower()
        role_b_val = str(roles.get(self.show.host_b.id, "")).strip().lower()
        
        if not role_a_val or not role_b_val or role_a_val == role_b_val:
            return False

        return True

    def _generate_scientific_fallback(self, topic: str, language: str = "es") -> Dict[str, Any]:
        """High quality deterministic fallback for Cosmic Forces videos on everyday human actions."""
        topic_lower = topic.lower()
        host_a_name = self.show.host_a.name
        host_b_name = self.show.host_b.name
        host_a_id = self.show.host_a.id
        host_b_id = self.show.host_b.id
        host_a_shot = self.show.host_a.shot_name
        host_b_shot = self.show.host_b.shot_name

        topic_roles = {
            host_a_id: host_a_name,
            host_b_id: host_b_name
        }

        if any(w in topic_lower for w in ["espejo", "mirarse", "reflejo", "rostro"]):
            return {
                "topic": "Mirarse al espejo",
                "headline_hook": "⚡ ESE DEL ESPEJO NO SOS ⚡",
                "roles": topic_roles,
                "holograms": None,
                "scenes": [
                    {
                        "speaker": "Narrador",
                        "entity": "narrator",
                        "text": "Ese del espejo no sos.",
                        "shot": "wide",
                        "duration": 3.0
                    },
                    {
                        "speaker": host_a_name,
                        "entity": host_a_id,
                        "text": "Creen que se miran a sí mismos, pero solo reciben mi rebote de hace tres nanosegundos.",
                        "shot": host_a_shot,
                        "duration": 3.4
                    },
                    {
                        "speaker": host_b_name,
                        "entity": host_b_id,
                        "text": "Y la cara que ven ya no existe; la rehacen con pedazos de ayer para no asustarse.",
                        "shot": host_b_shot,
                        "duration": 3.5
                    },
                    {
                        "speaker": host_a_name,
                        "entity": host_a_id,
                        "text": "Buscan un centro donde solo hay fotones rebotando en una superficie de plata.",
                        "shot": host_a_shot,
                        "duration": 3.4
                    },
                    {
                        "speaker": host_b_name,
                        "entity": host_b_id,
                        "text": "Pintan un fantasma estable sobre un río que no para de fluir.",
                        "shot": host_b_shot,
                        "duration": 3.5
                    },
                    {
                        "speaker": "Ambos",
                        "entity": "both",
                        "text": "Se saludan como dueños... cuando solo son el último parpadeo.",
                        "shot": "both",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Narrador",
                        "entity": "narrator",
                        "text": "¿A quién ves realmente cuando te miras fijamente al espejo?",
                        "shot": "wide",
                        "duration": 3.5
                    }
                ]
            }
        elif any(w in topic_lower for w in ["tocar", "tacto", "contacto", "piel"]):
            return {
                "topic": "Piel y contacto",
                "headline_hook": "⚡ NUNCA HAS TOCADO NADA EN TU VIDA ⚡",
                "roles": topic_roles,
                "holograms": None,
                "scenes": [
                    {
                        "speaker": "Narrador",
                        "entity": "narrator",
                        "text": "Nunca has tocado nada en tu vida.",
                        "shot": "wide",
                        "duration": 3.0
                    },
                    {
                        "speaker": host_a_name,
                        "entity": host_a_id,
                        "text": "Sus átomos repelen los míos. El contacto físico es una ilusión de campos flotantes.",
                        "shot": host_a_shot,
                        "duration": 3.4
                    },
                    {
                        "speaker": host_b_name,
                        "entity": host_b_id,
                        "text": "Sienten calor y peso, pero en verdad flotan a un suspiro de distancia sin rozarse jamás.",
                        "shot": host_b_shot,
                        "duration": 3.5
                    },
                    {
                        "speaker": host_a_name,
                        "entity": host_a_id,
                        "text": "Creen que abrazan a alguien, cuando solo chocan escudos invisibles.",
                        "shot": host_a_shot,
                        "duration": 3.4
                    },
                    {
                        "speaker": host_b_name,
                        "entity": host_b_id,
                        "text": "Y aun así inventan la caricia en medio de un abismo insuperable.",
                        "shot": host_b_shot,
                        "duration": 3.5
                    },
                    {
                        "speaker": "Ambos",
                        "entity": "both",
                        "text": "Se sienten tan cerca... estando para siempre separados.",
                        "shot": "both",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Narrador",
                        "entity": "narrator",
                        "text": "¿Cambia tu idea del amor saber que nunca rozas a nadie?",
                        "shot": "wide",
                        "duration": 3.5
                    }
                ]
            }
        elif any(w in topic_lower for w in ["recordar", "memoria", "pasado", "olvido", "pensamiento"]):
            return {
                "topic": "Recordar y memoria",
                "headline_hook": "⚡ TUS RECUERDOS SON FICCIONES DE HOY ⚡",
                "roles": topic_roles,
                "holograms": None,
                "scenes": [
                    {
                        "speaker": "Narrador",
                        "entity": "narrator",
                        "text": "Tus recuerdos son ficciones de hoy.",
                        "shot": "wide",
                        "duration": 3.0
                    },
                    {
                        "speaker": host_a_name,
                        "entity": host_a_id,
                        "text": "Cada vez que recuerdan un instante, no visitan el pasado: lo reescriben por completo.",
                        "shot": host_a_shot,
                        "duration": 3.4
                    },
                    {
                        "speaker": host_b_name,
                        "entity": host_b_id,
                        "text": "Borro los trazos originales y ellos rellenan el vacío con inventos confortables.",
                        "shot": host_b_shot,
                        "duration": 3.5
                    },
                    {
                        "speaker": host_a_name,
                        "entity": host_a_id,
                        "text": "Guardan nostalgia de cosas que nunca ocurrieron como las juran.",
                        "shot": host_a_shot,
                        "duration": 3.4
                    },
                    {
                        "speaker": host_b_name,
                        "entity": host_b_id,
                        "text": "Lloran por fotos que su propia mente acaba de pintar esta mañana.",
                        "shot": host_b_shot,
                        "duration": 3.5
                    },
                    {
                        "speaker": "Ambos",
                        "entity": "both",
                        "text": "Viven atrapados en un museo... donde todas las obras son falsas.",
                        "shot": "both",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Narrador",
                        "entity": "narrator",
                        "text": "¿Confías en lo que recuerdas de tu propia infancia?",
                        "shot": "wide",
                        "duration": 3.5
                    }
                ]
            }
        else:
            # Universal fallback for any everyday action
            clean_title = topic.strip().capitalize()
            return {
                "topic": clean_title,
                "headline_hook": f"⚡ LO QUE HACES AL {clean_title.upper()[:22]} ⚡",
                "roles": topic_roles,
                "holograms": None,
                "scenes": [
                    {
                        "speaker": "Narrador",
                        "entity": "narrator",
                        "text": f"Crees que decides al {topic.lower()}... pero el cosmos ya lo hizo.",
                        "shot": "wide",
                        "duration": 3.2
                    },
                    {
                        "speaker": host_a_name,
                        "entity": host_a_id,
                        "text": "Observo cómo ejecutan ese acto automático creyendo que dominan la materia.",
                        "shot": host_a_shot,
                        "duration": 3.4
                    },
                    {
                        "speaker": host_b_name,
                        "entity": host_b_id,
                        "text": "Muestran orgullo por un gesto que solo responde a mi arrastre silencioso.",
                        "shot": host_b_shot,
                        "duration": 3.5
                    },
                    {
                        "speaker": host_a_name,
                        "entity": host_a_id,
                        "text": "Ilumino el escenario para que crean que tienen el control del segundo.",
                        "shot": host_a_shot,
                        "duration": 3.4
                    },
                    {
                        "speaker": host_b_name,
                        "entity": host_b_id,
                        "text": "Y yo disuelvo la certeza antes de que terminen de pestañear.",
                        "shot": host_b_shot,
                        "duration": 3.5
                    },
                    {
                        "speaker": "Ambos",
                        "entity": "both",
                        "text": "Juegan a ser eternos... en una pausa que dura un suspiro.",
                        "shot": "both",
                        "duration": 3.5
                    },
                    {
                        "speaker": "Narrador",
                        "entity": "narrator",
                        "text": "¿Qué sientes al descubrir lo frágil que es cada uno de tus actos?",
                        "shot": "wide",
                        "duration": 3.5
                    }
                ]
            }
