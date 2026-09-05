"""
Viral Trend Evaluator for Space & Science News.
Evaluates official NASA discoveries and ranks them by viral potential
for YouTube Shorts, Instagram Reels, and TikTok.
"""

import json
import re
import urllib.request
from typing import Dict, List, Optional, Any, Tuple

from config import (
    GEMINI_API_KEY, OPENAI_API_KEY, GROQ_API_KEY,
    GROQ_MODEL, GROQ_API_BASE, LLM_PROVIDER, clean_env
)


TREND_EVALUATOR_PROMPT = """You are a senior algorithmic strategist and viral science editor for YouTube Shorts and TikTok.
Your job is to analyze real scientific discoveries and events from NASA, and select which ones have the highest viral potential online.

Evaluation Criteria (Scale 1 to 10 for each):
1. Curiosity & Counter-intuition: Does it shatter common sense or reveal an eerie, unexpected truth?
2. Visual Spectacle: Does NASA have jaw-dropping cosmic visuals (nebulae, solar flares, black holes, comet tails)?
3. Hookability (The 3-second Rule): Can you craft an irresistible opening question that forces people to keep watching?
4. Cosmic Drama & Scale: Does it feel epic, high-stakes, or mind-expanding?

Analyze the provided NASA candidates and output a JSON response ranking them from highest to lowest viral score.
Target Language for adapted titles and hooks: {target_language}

Respond ONLY with valid JSON matching this schema:
{
  "ranked_topics": [
    {
      "candidate_id": "string (matching candidate id)",
      "viral_score": 9.5,
      "adapted_title": "Punchy, exciting title in {target_language}",
      "suggested_hook": "Irresistible 3-second question/statement in {target_language}",
      "viral_reason": "1 concise sentence explaining why this topic will blow up on social media",
      "scientific_summary": "2-3 sentences summarizing the NASA scientific facts in simple, high-impact language"
    }
  ]
}
"""


class ViralTrendEvaluator:
    """Evaluates NASA discoveries for social media viral potential."""

    def __init__(
        self,
        gemini_key: Optional[str] = None,
        openai_key: Optional[str] = None,
        groq_key: Optional[str] = None,
        preferred_provider: str = LLM_PROVIDER
    ):
        self.gemini_key = gemini_key or GEMINI_API_KEY
        self.openai_key = openai_key or OPENAI_API_KEY
        self.groq_key = groq_key or GROQ_API_KEY
        self.provider = (preferred_provider or LLM_PROVIDER or "auto").lower()

    def evaluate_candidates(
        self,
        candidates: List[Dict[str, Any]],
        language: str = "es",
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Evaluate and rank candidates using LLM (with heuristic fallback).
        """
        if not candidates:
            return []

        lang_label = "Spanish (Español)" if language == "es" else ("English" if language == "en" else "Simplified Chinese (中文)")

        # Prepare concise payloads for the LLM
        prepared_candidates = []
        for c in candidates[:6]:
            prepared_candidates.append({
                "id": c["id"],
                "title": c["title"],
                "source": c.get("source", "NASA"),
                "date": c.get("date", ""),
                "scientific_text": c.get("scientific_text", "")[:280]
            })

        user_content = (
            f"Here are {len(prepared_candidates)} real NASA discoveries to evaluate:\n\n"
            + json.dumps(prepared_candidates, ensure_ascii=False, indent=2)
        )

        ranked = None

        # 1. Try Groq if configured
        if (self.provider in ("auto", "groq")) and self._is_valid_key(self.groq_key):
            ranked = self._evaluate_groq(user_content, lang_label)

        # 2. Try Gemini
        if not ranked and (self.provider in ("auto", "gemini")) and self._is_valid_key(self.gemini_key):
            ranked = self._evaluate_gemini(user_content, lang_label)

        # 3. Try OpenAI
        if not ranked and (self.provider in ("auto", "openai")) and self._is_valid_key(self.openai_key):
            ranked = self._evaluate_openai(user_content, lang_label)

        # 4. Smart Heuristic fallback if AI keys are not present or failed
        if not ranked:
            ranked = self._heuristic_ranking(candidates, language)

        # Merge original metadata with evaluation
        candidate_map = {c["id"]: c for c in candidates}
        results = []

        for item in ranked:
            cid = item.get("candidate_id")
            orig = candidate_map.get(cid)
            if not orig:
                # Try fallback matching by title
                for c in candidates:
                    if c["title"].lower() in item.get("adapted_title", "").lower() or c["id"] == cid:
                        orig = c
                        break
            if not orig:
                orig = candidates[0]

            merged = dict(orig)
            merged.update({
                "viral_score": float(item.get("viral_score", 8.0)),
                "adapted_title": item.get("adapted_title", orig["title"]),
                "suggested_hook": item.get("suggested_hook", ""),
                "viral_reason": item.get("viral_reason", ""),
                "scientific_summary": item.get("scientific_summary", orig["scientific_text"][:250])
            })
            results.append(merged)

        # Sort descending by viral score
        results.sort(key=lambda x: x.get("viral_score", 0.0), reverse=True)
        return results[:top_n]

    def _is_valid_key(self, key: Optional[str]) -> bool:
        if not key or len(key) < 15:
            return False
        placeholders = ["demo_key", "tu_clave", "sk-...", "your_key", "xxx"]
        return not any(p in key.lower() for p in placeholders)

    def _evaluate_groq(self, user_content: str, lang_label: str) -> Optional[List[Dict[str, Any]]]:
        try:
            prompt = TREND_EVALUATOR_PROMPT.replace("{target_language}", lang_label)
            payload = {
                "model": GROQ_MODEL or "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_content}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.3
            }
            req = urllib.request.Request(
                f"{GROQ_API_BASE}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.groq_key}",
                    "User-Agent": "NASA-Shorts-Generator/1.0"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                parsed = self._extract_json(content)
                if isinstance(parsed, dict) and "ranked_topics" in parsed:
                    return parsed["ranked_topics"]
                elif isinstance(parsed, list):
                    return parsed
                return None
        except Exception as e:
            print(f"  ⚠️ Error en evaluación viral con Groq: {e}")
            return None

    def _evaluate_gemini(self, user_content: str, lang_label: str) -> Optional[List[Dict[str, Any]]]:
        try:
            prompt = TREND_EVALUATOR_PROMPT.replace("{target_language}", lang_label)
            full_prompt = f"{prompt}\n\n{user_content}"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "responseMimeType": "application/json",
                    "maxOutputTokens": 1500,
                    "thinkingConfig": {
                        "thinkingBudget": 0
                    }
                }
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = self._extract_json(content)
                if isinstance(parsed, dict) and "ranked_topics" in parsed:
                    return parsed["ranked_topics"]
                elif isinstance(parsed, list):
                    return parsed
                return None
        except Exception as e:
            print(f"  ⚠️ Error en evaluación viral con Gemini: {e}")
            return None

    def _evaluate_openai(self, user_content: str, lang_label: str) -> Optional[List[Dict[str, Any]]]:
        try:
            prompt = TREND_EVALUATOR_PROMPT.replace("{target_language}", lang_label)
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_content}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.3
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_key}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                parsed = self._extract_json(content)
                if isinstance(parsed, dict) and "ranked_topics" in parsed:
                    return parsed["ranked_topics"]
                elif isinstance(parsed, list):
                    return parsed
                return None
        except Exception as e:
            print(f"  ⚠️ Error en evaluación viral con OpenAI: {e}")
            return None

    def _extract_json(self, text: str) -> Optional[Any]:
        """Extract and parse JSON safely from LLM output, removing markdown fences if present."""
        if not text:
            return None
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        try:
            return json.loads(text)
        except Exception:
            # Fallback regex extraction of outermost JSON object or list
            m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(0))
                except Exception:
                    pass
        return None

    def _heuristic_ranking(self, candidates: List[Dict[str, Any]], language: str) -> List[Dict[str, Any]]:
        """Smart algorithmic ranking when no LLM API is available."""
        # Viral magnet keywords
        high_viral_keywords = [
            ("black hole", 9.8, "Los misterios gravitatorios extremos siempre lideran retención."),
            ("comet", 9.3, "Viajeros helados del espacio profundo con colas visuales espectaculares."),
            ("saturn", 9.2, "Los anillos y lunas extrañas despiertan curiosidad masiva."),
            ("solar flare", 9.5, "Llamaradas y tormentas electromagnéticas con impacto en la Tierra."),
            ("james webb", 9.4, "El telescopio más avanzado revelando los orígenes del cosmos."),
            ("supernova", 9.3, "Explosiones estelares colosales con gran impacto visual."),
            ("orion", 8.9, "Una de las constelaciones más reconocidas y llamativas."),
            ("nebula", 8.8, "Nubes de gas cósmico con colores vivos y detalle asombroso."),
            ("galaxy", 8.7, "Islas de estrellas a millones de años luz de distancia."),
            ("exoplanet", 9.0, "Mundos alienígenas habitables o con climas extremos.")
        ]

        ranked = []
        for c in candidates:
            text = f"{c['title']} {c['scientific_text']}".lower()
            score = 7.5
            reason = "Descubrimiento oficial de la NASA de gran interés astronómico."

            for kw, kw_score, kw_reason in high_viral_keywords:
                if kw in text:
                    if kw_score > score:
                        score = kw_score
                        reason = kw_reason

            # Format hook based on title
            title = c["title"]
            if language == "es":
                hook = f"¿Sabías lo que acaba de revelar la NASA sobre {title}?"
                adapted = f"El misterio de {title}"
            else:
                hook = f"Did you know what NASA just uncovered about {title}?"
                adapted = f"The Secret of {title}"

            ranked.append({
                "candidate_id": c["id"],
                "viral_score": score,
                "adapted_title": adapted,
                "suggested_hook": hook,
                "viral_reason": reason,
                "scientific_summary": c["scientific_text"][:220] + "..."
            })

        ranked.sort(key=lambda x: x["viral_score"], reverse=True)
        return ranked
