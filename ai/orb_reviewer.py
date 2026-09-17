"""
Orb Script Reviewer & Executive Script Editor for COSMIC DEBATE EXPRESS.
Performs a secondary audit and auto-correction pass on debate scripts.
"""

import json
import time
from typing import Any, Dict, Optional
from config import GROQ_API_BASE, GROQ_MODEL, sanitize_env_value
from core.prompt_builder import DebatePromptBuilder
from core.script_models import DebateScript


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

    def review(
        self,
        draft_script: Dict[str, Any],
        topic: Optional[str] = None,
        show: Optional[Any] = None
    ) -> Dict[str, Any]:
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

        effective_topic = topic or draft_script.get("topic") or "Debate"
        print("\n🔍 [Orb Script Editor] Ejecutando Agente Revisor Ejecutivo...")
        print(f"   ↳ Validando aislamiento de dominio, dialéctica, gramática y cámaras para '{effective_topic}'...")

        time.sleep(1.0)

        json_str_input = json.dumps(draft_script, ensure_ascii=False, indent=2)
        builder = DebatePromptBuilder(effective_topic)
        if show:
            builder.with_show(show)
        prompt = builder.build_reviewer_prompt(json_str_input)

        host_a = show.host_a if show else None
        host_b = show.host_b if show else None

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
                    print("  ✨ ¡Guión de debate auditado y corregido con éxito por el Editor Ejecutivo!")
                    # Use OOP script model for sanitization
                    script_obj = DebateScript.from_dict(reviewed, default_topic=effective_topic)
                    if "roles" in draft_script and not script_obj.roles:
                        script_obj.roles = draft_script["roles"]
                    script_obj.sanitize_structure(host_a, host_b)
                    return script_obj.to_dict()
            except Exception as e:
                print(f"  ⚠️ Revisión de orbes con {prov} falló ({e}), manteniendo borrador original...")

        # Fallback to sanitized draft
        script_obj = DebateScript.from_dict(draft_script, default_topic=effective_topic)
        script_obj.sanitize_structure(host_a, host_b)
        return script_obj.to_dict()

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
