"""
Robo Agents Script Generator.
Generates humorous dialogue scripts between Orange Robot (charismatic/funny) 
and Blue Robot (witty scientist) on any given topic.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, List

from config import GEMINI_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, GROQ_MODEL, GROQ_API_BASE


ROBO_SYSTEM_PROMPT = """Eres un guionista cómico para videos cortos de TikTok, Reels y Shorts.
Tu trabajo es escribir una conversación MUY DIVERTIDA, DINÁMICA y ENTRETEIDA entre dos robots sobre el tema indicado.

LOS PERSONAJES:
1. ORANGE (Robot Naranja): El robot carismático, hiperactivo, curioso, gracioso y un poco impulsivo. Hace preguntas locas o conclusiones cómicas.
2. BLUE (Robot Azul): El robot científico, sarcástico, intelectual y sarcásticamente paciente. Explica la ciencia real pero con remates cómicos y respuestas irónicas.

REGLAS OBLIGATORIAS:
1. La conversación debe tener entre 4 y 6 turnos alternados (Orange -> Blue -> Orange -> Blue...).
2. Cada turno debe ser corto (10 a 20 palabras máximo) para mantener un ritmo rápido e hiperactivo.
3. El humor debe ser inteligente, absurdo o sarcástico.
4. Para cada turno, proporciona "keywords": 1 o 2 palabras clave en INGLÉS para buscar videos de stock reales en Pexels/Pixabay (ej: ["black hole", "space"], ["galaxy", "stars"], ["ocean", "underwater"], ["robot", "technology"]).

Responde ÚNICAMENTE con un objeto JSON válido con la siguiente estructura:
{
  "title": "Título llamativo",
  "topic": "Tema tratado",
  "turns": [
    {
      "turn_id": 1,
      "speaker": "orange",
      "text": "¡Oye Azul! ¿Es verdad que el sol se va a apagar y nos vamos a congelar?",
      "keywords": ["sun explosion", "space"]
    },
    {
      "turn_id": 2,
      "speaker": "blue",
      "text": "Sí, Naranja, pero en 5 mil millones de años. Asumiendo que tus baterías duren tanto.",
      "keywords": ["sun galaxy", "solar system"]
    }
  ]
}
"""


class RoboScriptGenerator:
    """Generates dialogue scripts for Orange and Blue Robo Agents."""

    def generate_script(self, topic: str, num_turns: int = 5) -> Dict[str, Any]:
        """Generate dialogue script using available LLM API or fallback."""
        print(f"🤖 Generating Robo dialogue for topic: '{topic}'...")

        # 1. Try Gemini if API key present
        if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
            script = self._generate_gemini(topic)
            if script:
                return script

        # 2. Try Groq if configured
        if GROQ_API_KEY:
            script = self._generate_groq(topic)
            if script:
                return script

        # 3. Try OpenAI if configured
        if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
            script = self._generate_openai(topic)
            if script:
                return script

        # 4. Fallback script
        print("  ⚠️ LLM API keys not provided or failed. Using humorous built-in fallback script.")
        return self._get_fallback_script(topic)

    def _generate_gemini(self, topic: str) -> Dict[str, Any]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            prompt = f"{ROBO_SYSTEM_PROMPT}\n\nEscribe el guión para el tema: '{topic}'"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.8, "responseMimeType": "application/json"}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=25) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except Exception as e:
            print(f"  ⚠️ Gemini generation error: {e}")
            return {}

    def _generate_groq(self, topic: str) -> Dict[str, Any]:
        try:
            url = f"{GROQ_API_BASE}/chat/completions"
            payload = {
                "model": GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": ROBO_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Escribe el guión para el tema: '{topic}'"}
                ],
                "temperature": 0.8,
                "response_format": {"type": "json_object"}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=25) as response:
                res = json.loads(response.read().decode("utf-8"))
                return json.loads(res["choices"][0]["message"]["content"])
        except Exception as e:
            print(f"  ⚠️ Groq generation error: {e}")
            return {}

    def _generate_openai(self, topic: str) -> Dict[str, Any]:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": ROBO_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Escribe el guión para el tema: '{topic}'"}
                ],
                "temperature": 0.8,
                "response_format": {"type": "json_object"}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=25) as response:
                res = json.loads(response.read().decode("utf-8"))
                return json.loads(res["choices"][0]["message"]["content"])
        except Exception as e:
            print(f"  ⚠️ OpenAI generation error: {e}")
            return {}

    def _get_fallback_script(self, topic: str) -> Dict[str, Any]:
        """Humorous fallback dialogue when offline or without API key."""
        return {
            "title": f"Robots exploran: {topic}",
            "topic": topic,
            "turns": [
                {
                    "turn_id": 1,
                    "speaker": "orange",
                    "text": f"¡Oye Azul! Estaba pensando en {topic}... ¿es verdad que eso puede destruir el universo?",
                    "keywords": ["space galaxy", "black hole"]
                },
                {
                    "turn_id": 2,
                    "speaker": "blue",
                    "text": "Naranja, científicamente hablando, lo único que destruye el universo es tu falta de lectura.",
                    "keywords": ["laboratory science", "futuristic robot"]
                },
                {
                    "turn_id": 3,
                    "speaker": "orange",
                    "text": "¡Oye! ¡Mi procesador es muy rápido! Pero en serio, cuéntame la verdad sobre esto.",
                    "keywords": ["quantum physics", "glowing core"]
                },
                {
                    "turn_id": 4,
                    "speaker": "blue",
                    "text": f"La verdad es que {topic} se rige por leyes físicas fascinantes, no por tus teorías conspirativas.",
                    "keywords": ["deep space", "nebula stars"]
                },
                {
                    "turn_id": 5,
                    "speaker": "orange",
                    "text": "¡Ajá! ¡Sabía que había algo oculto! ¡Mi antena presiente un gran misterio!",
                    "keywords": ["robot technology", "futuristic city"]
                }
            ]
        }
