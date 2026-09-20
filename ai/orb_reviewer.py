"""
Orb Script Reviewer & Executive Script Editor for COSMIC DEBATE EXPRESS.
Performs a secondary audit and auto-correction pass on debate scripts.
"""

import json
import time
from typing import Any, Dict, Optional
from config import GROQ_API_BASE, GROQ_MODEL, sanitize_env_value

ORB_EDITOR_SYSTEM_PROMPT = """You are the Executive Script Editor for 'COSMIC ORB SHOW'.
Your ONLY job is to validate and auto-correct a JSON script generated for a short video.

CRITICAL CHECKLIST TO VALIDATE AND CORRECT:
1. ASIGNACIÓN DINÁMICA DE ROLES Y MÁXIMO CONTRASTE:
   - Los roles NO son fijos. Verifica que el objeto "roles" defina dos especialidades o ramas de conocimiento radicalmente opuestas y adaptadas específicamente al tema del video.
   - Si los roles son idénticos, vacíos, genéricos o carecen de contraste, asígnales dos ramas que choquen frontalmente (ej. "Física de Información" vs "Realismo Empírico", "Neurobiología" vs "Fenomenología", etc.).

2. APLICACIÓN ESTRICTA DEL ROL ELEGIDO EN CADA INTERVENCIÓN:
   - Cada orbe DEBE hablar y debatir estrictamente desde el rol/rama asignado en el objeto "roles".
   - PROHIBIDO que ambos hablen como dos científicos clónicos o con el mismo estilo neutro. Cada uno debe reflejar el lenguaje, metodología, prioridades y cosmovisión de su rol asignado.

3. RIGOR FACTUAL Y CERO INVENTOS (CIENCIA Y REALIDAD VERÍDICA):
   - CIENCIA Y HECHOS VERÍDICOS: Verificar que los datos, leyes y principios expuestos sean 100% verídicos, comprobables y sin datos numéricos inventados ni pseudociencia.
   - REJECT and REWRITE any pseudo-poetic nonsense phrases ("la gravedad del relato", "la tinta de la conciencia", "las hojas del libro cósmico", "las voces del vacío").
   - Sustituir cualquier invención por principios y hechos reales de la disciplina correspondiente.

4. CONTINUOUS STORY ARC & CONVERSATIONAL RESPONSE:
   - Ensure the entire script stays within ONE central concept, paradox or thought experiment.
   - GANCHO DE LA ESCENA 1: Debe ser una paradoja, dilema o pregunta incómoda en segunda persona. Si empieza con "Imagina..." o una definición neutral, REESCRIBE el gancho inmediatamente.
   - Cada intervención debe responder directamente a la anterior: cada escena después de la primera DEBE contraargumentar, cuestionar o profundizar lo que acaba de plantear el otro orbe.

5. STRUCTURE & DEVELOPED EXCHANGES:
   - Las escenas deben desarrollarse lo suficiente para que ambos orbes expongan y reaccionen con profundidad y agilidad.
   - 'holograms' can be null or contain metrics if relevant. Do not fail if omitted.

6. SINGLE CLOSING SCENE & PENULTIMATE SHOT:
   - PROHIBIT TWO CONSECUTIVE 'Ambos'/'both' SCENES: If the draft contains two consecutive closing scenes by 'both'/'Ambos', MERGE them into ONE single punchy closing scene.
   - The penultimate scene MUST be spoken by a single orb in close-up ("close_quantum" or "close_solar"), never wide or both.
   - Only the very last scene can have speaker "Ambos" (entity: "both", shot: "both").

7. NATURAL SPANISH GRAMMAR & CONCISE LENGTH:
   - Ensure all sentences use proper articles (el, la, los, las, un, una) and natural, high-impact phrasing.
   - Each scene should be punchy (~10-18 words, max 95 characters).

INPUT JSON:
{INSERT_GENERATED_JSON_HERE}

OUTPUT: Return ONLY the corrected and validated JSON matching the exact original schema.
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
