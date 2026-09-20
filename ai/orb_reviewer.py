"""
Orb Script Reviewer & Executive Script Editor for COSMIC DEBATE EXPRESS.
Performs a secondary audit and auto-correction pass on debate scripts.
"""

import json
import time
from typing import Any, Dict, Optional
from config import GROQ_API_BASE, GROQ_MODEL, sanitize_env_value

ORB_EDITOR_SYSTEM_PROMPT = """You are the Executive Script Editor for 'FUERZAS CÓSMICAS'.
Your ONLY job is to validate and auto-correct a JSON script generated for a 25-second short video.

CRITICAL CHECKLIST TO VALIDATE AND CORRECT:
1. FUERZAS CÓSMICAS, NO ACADÉMICOS:
   - Las entidades son FUERZAS CÓSMICAS ENCARNADAS (La Luz, La Gravedad, El Vacío, La Entropía, El Tiempo, La Memoria). NO son disciplinas ni profesores.

2. PROHIBICIÓN ABSOLUTA DE LENGUAJE ACADÉMICO Y EXPLICACIONES CIENTÍFICAS DE CLASE:
   - PROHIBIDO usar jerga académica de libro de texto: "función de onda", "entropía", "electromagnético", "relatividad general", "mecánica cuántica", "epigenética", "cadena de adn", "partícula subatómica", etc.
   - PROHIBIDO EXPLICAR LA CIENCIA COMO UN PROFESOR. La ciencia debe estar ENCARNADA en la conversación. Si un profesor podría decir la línea en una clase, REESCRIBELA inmediatamente para que suene a lo que SOLO una fuerza cósmica diría.

3. DIÁLOGO DIRECTO ENTRE FUERZAS (NO MONÓLOGOS):
   - Las fuerzas se HABLAN ENTRE SÍ, se contradicen, se completan, se tensan. Una quiere retener, otra disolver; una ilumina, otra borra. NO le hablan al espectador.

4. NARRADOR LIMITADO AL GANCHO Y PREGUNTA FINAL:
   - Escena 1 (Narrador): Gancho seco (máx 12 palabras) que rompe la intuición (ej. "Ese del espejo no sos.").
   - Escena 7 (Narrador): Pregunta abierta provocadora para los comentarios.
   - El narrador NO interviene en las escenas 2 a 6.

5. ESTRUCTURA EXACTA DE 7 PASOS:
   - Escena 1: Narrador (Gancho seco, máx 12 palabras).
   - Escena 2: Fuerza A (Primera interpretación desde su naturaleza).
   - Escena 3: Fuerza B (Contradicción directa a Fuerza A).
   - Escena 4: Fuerza A (Observación asombrosa encarnada).
   - Escena 5: Fuerza B (Revelación poética e irónica).
   - Escena 6: Ambos (Remate compartido, se interrumpen o completan).
   - Escena 7: Narrador (Pregunta abierta para comentarios).

6. GRAMÁTICA Y LONGITUD CONCISA:
   - Diálogos directos, secos y ágiles (~10-16 palabras por escena).

INPUT JSON:
{INSERT_GENERATED_JSON_HERE}

OUTPUT: Return ONLY the corrected and validated JSON matching the required schema.
"""


class OrbScriptReviewer:
    """Executive Script Editor for Co-Host Orbs."""

    def __init__(
        self,
        gemini_key: Optional[str] = None,
        openai_key: Optional[str] = None,
        groq_key: Optional[str] = None,
        groq_api_base: Optional[str] = None,
        groq_model: Optional[str] = None,
        preferred_provider: str = "auto"
    ):
        self.gemini_key = sanitize_env_value(gemini_key)
        self.openai_key = sanitize_env_value(openai_key)
        self.groq_key = sanitize_env_value(groq_key)
        self.groq_api_base = sanitize_env_value(groq_api_base) or GROQ_API_BASE
        self.groq_model = sanitize_env_value(groq_model) or GROQ_MODEL
        self.preferred_provider = (sanitize_env_value(preferred_provider) or "auto").lower().strip()

    def review(self, draft_script: Dict[str, Any]) -> Dict[str, Any]:
        """Audits and auto-corrects the debate script JSON using LLM."""
        if not draft_script or not draft_script.get("scenes"):
            return draft_script

        configured = []
        if self.preferred_provider == "groq" and self.groq_key:
            configured = ["groq"]
        elif self.preferred_provider == "gemini" and self.gemini_key:
            configured = ["gemini"]
        elif self.preferred_provider == "openai" and self.openai_key:
            configured = ["openai"]
        else:
            if self.groq_key:
                configured.append("groq")
            if self.gemini_key:
                configured.append("gemini")
            if self.openai_key:
                configured.append("openai")

        if not configured:
            print("  ⚠️ Agente Revisor omitido: No hay API key disponible para la revisión.")
            return draft_script

        print("\n🔍 [Orb Script Editor] Ejecutando Agente Revisor Ejecutivo...")
        print("   ↳ Validando aislamiento de dominios, coherencia lógica, gramática y longitud...")

        time.sleep(1.0)

        json_str_input = json.dumps(draft_script, ensure_ascii=False, indent=2)
        prompt = ORB_EDITOR_SYSTEM_PROMPT.replace("{INSERT_GENERATED_JSON_HERE}", json_str_input)

        for prov in configured:
            try:
                reviewed = None
                if prov == "groq":
                    reviewed = self._review_groq(prompt)
                elif prov == "gemini":
                    reviewed = self._review_gemini(prompt)
                elif prov == "openai":
                    reviewed = self._review_openai(prompt)

                if reviewed and reviewed.get("scenes") and len(reviewed["scenes"]) > 0:
                    roles = reviewed.get("roles")
                    if roles and isinstance(roles, dict) and len(roles) >= 2:
                        role_values = [str(v).strip().lower() for v in roles.values()]
                        if role_values[0] != role_values[1]:
                            print("  ✨ ¡Guión de debate auditado y validado con éxito por el Editor Ejecutivo!")
                            return reviewed
                    print("  ⚠️ El Editor Ejecutivo rechazó el guión por falta de contraste en los roles.")
            except Exception as e:
                print(f"  ⚠️ Revisión de orbes con {prov} falló ({e}), manteniendo borrador original...")

        return draft_script

    def _review_groq(self, prompt: str) -> Optional[Dict[str, Any]]:
        url = f"{self.groq_api_base.rstrip('/')}/chat/completions"
        payload = {
            "model": self.groq_model or "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are the Executive Script Editor for Cosmic Debate Express. Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.groq_key}",
            "Connection": "close"
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            res = json.loads(response.read().decode("utf-8"))
            text = res["choices"][0]["message"]["content"]
            return json.loads(text)

    def _review_gemini(self, prompt: str) -> Optional[Dict[str, Any]]:
        models_to_try = ["gemini-2.5-flash", "gemini-flash-latest"]
        headers = {"Content-Type": "application/json", "Accept": "application/json", "Connection": "close"}
        for model in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
                payload = {
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"}
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=30) as response:
                    res = json.loads(response.read().decode("utf-8"))
                    text = res["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text)
            except Exception:
                continue
        return None

    def _review_openai(self, prompt: str) -> Optional[Dict[str, Any]]:
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.openai_key}",
            "Connection": "close"
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as response:
            res = json.loads(response.read().decode("utf-8"))
            text = res["choices"][0]["message"]["content"]
            return json.loads(text)
