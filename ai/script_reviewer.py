"""
Script Reviewer & Critic Agent.
Performs a secondary evaluation pass to audit, critique, and optimize
the AI-generated script for high-retention vertical video shorts.
"""

import json
import re
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

from config import GROQ_API_BASE, GROQ_MODEL

CRITIC_SYSTEM_PROMPT = """You are the Senior Executive Producer and Script Doctor for viral vertical shorts (YouTube Shorts, TikTok, Reels).
Your mission: Critically audit, tighten, and elevate the draft script to guarantee maximum viewer retention, factual clarity, viral engagement, and realistic stock footage availability on Pexels and Pixabay.

CRITICAL AUDIT DIRECTIVES:

1. VIRAL RETENTION & NATURAL FLOW (NO POETIC MELODRAMA):
   - BAN GOTHIC POETRY AND MELODRAMA: Eliminate any flowery or theatrical clichés ("abismo sin retorno", "silencio eterno", "antorchas ardientes", "frágil es la luz", "danza cósmica", "ofrenda mortal").
   - Replace with direct, punchy, grounded language that hooks the modern viewer with real fascination.

2. FACTUAL ACCURACY & COHERENCE:
   - Ensure any facts, numbers, mechanisms, or comparisons are 100% accurate, logical, and coherent from start to finish.
   - Remove forced textbook dates, obscure lab detector names, or irrelevant trivia.

3. MANDATORY VIRAL HOOK & CLICHÉ REMOVAL (Seconds 0-3):
   - The opening in Scene 1 MUST grab the viewer in the first 3 seconds with a startling truth, counter-intuitive fact, or curiosity gap.
   - BANNED CLICHÉS (MUST BE PERMANENTLY REMOVED):
     * "Hola amigos", "En este video", "Bienvenidos", "Hello guys", "Did you know", "¿Sabías que?".
     * "En los confines del universo / espacio", "Un misterio que desconcierta a la ciencia", "¿Alguna vez te has preguntado?", "Pero eso no es todo", "Prepárate para quedar asombrado".

4. WORD BUDGET & SPOKEN CADENCE:
   - Spoken speech tempo: ~2.2 to 2.5 words per second.
   - Strictly 12 to 16 spoken words per scene (absolute maximum: 18 words).
   - Cut wordy filler, adverbs, and fluff while preserving visceral clarity.

5. REAL STOCK KEYWORDS FOR PEXELS & PIXABAY (CRITICAL):
   - "keywords" MUST ALWAYS BE IN ENGLISH (1 to 2 visual terms per scene).
   - Ensure every keyword represents a REAL, FILMABLE visual tag that exists in stock libraries (Pexels, Pixabay).
   - Concrete nouns, animals, environments, or 3D animations (e.g. ["black hole 3d animation"], ["volcano lava flow"], ["deep sea shark"], ["brain neurons 3d"]).
   - REMOVE any unfilmable abstract metaphors ("star plunge", "light freeze", "cosmic abyss", "fragile light", "eternal dance").

6. NATURAL CLOSING:
   - Remove any cheesy phrases like "Comenta abajo", "Déjalo en los comentarios", or "Suscríbete".
   - End with a thought-provoking perspective or intriguing open realization.

Output ONLY valid JSON matching this exact schema:
{
  "title": "Short punchy title",
  "hook": "Sharp, arresting opening sentence",
  "review_notes": "One concise sentence summarizing specific improvements made",
  "scenes": [
    {
      "scene_id": 1,
      "visual_subject": "Concise subject in target language",
      "narration": "Polished, punchy narration in target language (12-16 words max)",
      "keywords": ["specific visual keyword 1", "keyword 2"],
      "visual_type": "video",
      "estimated_duration": 7
    }
  ]
}
"""


class ScriptReviewer:
    """Secondary LLM Critic Agent for script refinement and audio-visual synchronization."""

    def __init__(
        self,
        gemini_key: Optional[str] = None,
        openai_key: Optional[str] = None,
        groq_key: Optional[str] = None,
        groq_api_base: Optional[str] = None,
        groq_model: Optional[str] = None,
        preferred_provider: str = "auto"
    ):
        self.gemini_key = gemini_key
        self.openai_key = openai_key
        self.groq_key = groq_key
        self.groq_api_base = groq_api_base or GROQ_API_BASE
        self.groq_model = groq_model or GROQ_MODEL
        self.preferred_provider = (preferred_provider or "auto").lower().strip()

    def review(
        self,
        draft_script: Dict[str, Any],
        topic: str,
        target_duration: int,
        language: str = "es",
        context_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submits the draft script to the Critic Agent for audit and enhancement.
        Returns the polished script, or the original draft if review cannot be completed.
        """
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
            return draft_script

        print("\n🔍 Activando Agente Revisor (Editor & Director de Arte)...")
        print("   ↳ Auditando gancho inicial, cadencia de palabras y concordancia audiovisual...")

        # Brief pause to respect burst rate limits between initial script call and review call
        time.sleep(1.2)

        for prov in configured:
            try:
                reviewed = None
                if prov == "groq":
                    reviewed = self._review_groq(draft_script, topic, target_duration, language, context_text)
                elif prov == "gemini":
                    reviewed = self._review_gemini(draft_script, topic, target_duration, language, context_text)
                elif prov == "openai":
                    reviewed = self._review_openai(draft_script, topic, target_duration, language, context_text)

                if reviewed and reviewed.get("scenes") and len(reviewed["scenes"]) > 0:
                    notes = reviewed.get("review_notes")
                    if notes:
                        print(f"  ✨ Guión pulido con éxito: \"{notes}\"")
                    else:
                        print("  ✨ Guión pulido y verificado por el Agente Revisor.")
                    return reviewed
            except Exception as e:
                print(f"  ⚠️ Revisión con {prov} falló ({e}), continuando con versión actual...")

        print("  ℹ️ Manteniendo versión preliminar del guión.")
        return draft_script

    def _build_review_prompt(
        self,
        draft_script: Dict[str, Any],
        topic: str,
        target_duration: int,
        language: str,
        context_text: Optional[str] = None
    ) -> str:
        draft_json_str = json.dumps(draft_script, ensure_ascii=False, indent=2)
        ctx_block = ""
        if context_text and context_text.strip():
            ctx_block = f"\nOFFICIAL NASA FACTUAL CONTEXT:\n{context_text.strip()}\n"

        return (
            f"Topic: {topic}\n"
            f"Target Video Duration: {target_duration} seconds\n"
            f"Language Code: {language}\n"
            f"{ctx_block}\n"
            f"DRAFT SCRIPT TO AUDIT AND OPTIMIZE:\n"
            f"{draft_json_str}\n\n"
            f"Execute your 5-point audit. Return the improved JSON script:"
        )

    def _review_groq(
        self,
        draft: Dict[str, Any],
        topic: str,
        duration: int,
        language: str,
        context_text: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        endpoint = f"{self.groq_api_base}/chat/completions"
        user_content = self._build_review_prompt(draft, topic, duration, language, context_text)
        models_to_try = [self.groq_model]
        if "llama-3.1-8b-instant" not in models_to_try:
            models_to_try.append("llama-3.1-8b-instant")

        for idx, model in enumerate(models_to_try):
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.3
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
            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    content = data["choices"][0]["message"]["content"]
                    return self._normalize_reviewed_script(content, draft, language)
            except urllib.error.HTTPError as e:
                err_detail = ""
                try:
                    err_json = json.loads(e.read().decode("utf-8"))
                    err_detail = err_json.get("error", {}).get("message", "")
                except Exception:
                    pass
                if idx < len(models_to_try) - 1:
                    time.sleep(1.5)
                    continue
                if err_detail:
                    raise RuntimeError(f"Groq {e.code}: {err_detail}") from e
                raise e

        return None

    def _review_gemini(
        self,
        draft: Dict[str, Any],
        topic: str,
        duration: int,
        language: str,
        context_text: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash:generateContent?key={self.gemini_key}"
        )
        user_content = self._build_review_prompt(draft, topic, duration, language, context_text)
        payload = {
            "system_instruction": {"parts": [{"text": CRITIC_SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": user_content}]}],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json"
            }
        }
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "NASA-Shorts-Generator/1.0"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0]["content"]["parts"][0]["text"]
                return self._normalize_reviewed_script(content, draft, language)
        return None

    def _review_openai(
        self,
        draft: Dict[str, Any],
        topic: str,
        duration: int,
        language: str,
        context_text: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        endpoint = "https://api.openai.com/v1/chat/completions"
        user_content = self._build_review_prompt(draft, topic, duration, language, context_text)
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_key}",
                "User-Agent": "NASA-Shorts-Generator/1.0"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            return self._normalize_reviewed_script(content, draft, language)

    def _normalize_reviewed_script(
        self,
        raw_text: str,
        fallback_draft: Dict[str, Any],
        language: str
    ) -> Optional[Dict[str, Any]]:
        """Parses and sanitizes the Critic output to ensure full compatibility with the rendering pipeline."""
        text = raw_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)

        try:
            data = json.loads(text)
            if not isinstance(data, dict) or "scenes" not in data or not isinstance(data["scenes"], list):
                return fallback_draft

            data["language"] = language

            # Sanitize each scene
            for idx, sc in enumerate(data["scenes"]):
                # Clean banned opening clichés if any LLM slipped them into Scene 1
                if idx == 0 and sc.get("narration"):
                    cleaned_narr = re.sub(
                        r"^(hola(\s+(amigos|a todos|chicos))?|bienvenidos(\s+de nuevo)?|en este video|sab[ií]as que|"
                        r"te has preguntado(\s+alguna vez)?|alguna vez te has preguntado|"
                        r"en los confines del? (universo|espacio)|un misterio que desconcierta a la ciencia|"
                        r"prep[aá]rate para quedar asombrado|did you know|have you ever wondered|hello guys|welcome back)[:,\s-]*",
                        "",
                        sc["narration"],
                        flags=re.IGNORECASE
                    ).strip()
                    if cleaned_narr:
                        cleaned_narr = cleaned_narr[0].upper() + cleaned_narr[1:]
                        sc["narration"] = cleaned_narr
                        data["hook"] = cleaned_narr

                for kf in ("nasa_keywords", "pexels_keywords", "stock_keywords", "keywords"):
                    if isinstance(sc.get(kf), str):
                        sc[kf] = [sc[kf].strip()]
                    elif not isinstance(sc.get(kf), list):
                        sc[kf] = []

                nasa_kws = [str(k).strip() for k in sc.get("nasa_keywords", []) if str(k).strip()]
                stock_kws = [
                    str(k).strip()
                    for k in (sc.get("stock_keywords") or sc.get("pexels_keywords") or [])
                    if str(k).strip()
                ]
                legacy_kws = [str(k).strip() for k in sc.get("keywords", []) if str(k).strip()]

                if not nasa_kws:
                    nasa_kws = legacy_kws[:] if legacy_kws else stock_kws[:]
                if not stock_kws:
                    stock_kws = legacy_kws[:] if legacy_kws else nasa_kws[:]

                sc["nasa_keywords"] = nasa_kws
                sc["pexels_keywords"] = stock_kws
                sc["stock_keywords"] = stock_kws
                sc["keywords"] = nasa_kws if nasa_kws else stock_kws

                if not sc.get("visual_type"):
                    sc["visual_type"] = "video"

            return data
        except Exception as e:
            print(f"  ⚠️ Error parsing critic response: {e}")
            return fallback_draft
