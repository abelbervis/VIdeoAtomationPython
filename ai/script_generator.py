"""
AI Script Generator for Vertical Science Shorts.
Generates structured JSON scripts divided into scenes with narration and targeted NASA search keywords.
Supports Google Gemini, OpenAI, and a reliable factual scientific generator fallback.
"""

import json
import os
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

from config import GEMINI_API_KEY, OPENAI_API_KEY, LLM_API_BASE_URL


SYSTEM_PROMPT = """You are an elite science communicator writing punchy, viral YouTube Shorts and TikTok documentary scripts.
Target duration: 30 to 45 seconds.

Rules:
1. Start with an irresistible 3-second hook that challenges common intuition.
2. Absolutely NO generic greetings (Never say 'Hola amigos', 'En este video', 'Bienvenidos').
3. Keep the narration fast-paced, accurate, engaging, and based strictly on verifiable facts and science.
4. End with a memorable, mind-blowing closing thought or punchline.
5. Divide the script into 4 to 6 distinct visual scenes.
6. Provide specific search keywords IN ENGLISH for each scene to query media libraries (Pexels, NASA). Keywords should describe exact visual actions (e.g. 'ocean waves aerial', 'deep space galaxy', 'brain neurons firing').
7. Preferred visual types: "video" for motion scenes, "image" for high-detail captures.

Respond ONLY with valid JSON matching this schema:
{
  "title": "Short title",
  "hook": "Opening hook sentence",
  "scenes": [
    {
      "scene_id": 1,
      "narration": "Narration text in the requested language (e.g. Spanish)",
      "keywords": ["specific english keyword 1", "specific keyword 2"],
      "visual_type": "video",
      "estimated_duration": 7
    }
  ]
}
"""


class ScriptGenerator:
    """Generates structured science video scripts via LLM APIs with fallback."""

    def __init__(self):
        self.gemini_key = str(GEMINI_API_KEY or "").strip().strip("'\"").strip()
        self.openai_key = str(OPENAI_API_KEY or "").strip().strip("'\"").strip()
        raw_url = str(LLM_API_BASE_URL or "").strip().strip("'\"").strip()
        self.base_url = raw_url if raw_url.startswith("http") else ""

    def _is_valid_api_key(self, key: str) -> bool:
        """Check if an API key looks like an actual valid key and not a dummy placeholder."""
        if not key or len(key) < 15:
            return False
        placeholders = ["my_gemini_api_key", "tu_clave", "your_key", "demo_key", "sk-...", "placeholder", "xxx"]
        return not any(p in key.lower() for p in placeholders)

    def generate(self, topic: str, target_duration: int = 35) -> Dict[str, Any]:
        """Generate a structured script for the given topic."""
        print(f"\n🧠 Generating script for: '{topic}' (~{target_duration}s)...")

        # 1. Try Gemini if configured with a real key
        if self._is_valid_api_key(self.gemini_key):
            script = self._generate_gemini(topic, target_duration)
            if script:
                return script

        # 2. Try OpenAI if configured with a real key
        if self._is_valid_api_key(self.openai_key):
            script = self._generate_openai(topic, target_duration)
            if script:
                return script

        # 3. Intelligent factual scientific script builder (zero-key fallback)
        print("  ℹ️ Using built-in scientific script engine...")
        return self._generate_fallback(topic, target_duration)

    def _generate_gemini(self, topic: str, target_duration: int) -> Optional[Dict[str, Any]]:
        """Call Gemini API via REST."""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"Topic: {topic}\n"
                f"Target duration: {target_duration} seconds.\n"
                f"Language: Spanish (unless topic is strictly in another language).\n"
                f"Generate the JSON script:"
            )

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.4,
                    "responseMimeType": "application/json"
                }
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
                return self._parse_json_response(text)
        except Exception as e:
            print(f"  ⚠️ Gemini API request failed ({e}), trying next provider...")
            return None

    def _generate_openai(self, topic: str, target_duration: int) -> Optional[Dict[str, Any]]:
        """Call OpenAI API or custom endpoint."""
        try:
            endpoint = self.base_url if (self.base_url and self.base_url.startswith("http")) else "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Topic: {topic}. Target duration: {target_duration}s. Generate JSON script."}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.4
            }

            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_key}"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=25) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["choices"][0]["message"]["content"]
                return self._parse_json_response(text)
        except Exception as e:
            print(f"  ⚠️ OpenAI API request failed ({e})...")
            return None

    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """Clean markdown wrapping and validate JSON structure."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)

        try:
            data = json.loads(text)
            if "scenes" in data and isinstance(data["scenes"], list) and len(data["scenes"]) > 0:
                return data
        except Exception as e:
            print(f"  ⚠️ JSON parse error: {e}")
        return None

    def _generate_fallback(self, topic: str, target_duration: int) -> Dict[str, Any]:
        """
        Factual scientific script template generator when no LLM API key is present.
        Ensures 100% offline and standalone execution capability for any topic.
        """
        clean_topic = topic.strip()
        topic_lower = clean_topic.lower()

        # Tailored knowledge presets for popular queries
        if "tierra" in topic_lower and ("girar" in topic_lower or "rotar" in topic_lower or "rotacion" in topic_lower):
            return {
                "title": "¿Qué pasaría si la Tierra dejara de girar?",
                "hook": "Si la Tierra se detuviera de golpe, el apocalipsis ocurriría en un milisegundo.",
                "scenes": [
                    {
                        "scene_id": 1,
                        "narration": "En el ecuador nos movemos a más de mil seiscientos kilómetros por hora.",
                        "keywords": ["earth rotation", "planet earth space"],
                        "visual_type": "video",
                        "estimated_duration": 6
                    },
                    {
                        "scene_id": 2,
                        "narration": "Por inercia, la atmósfera, los océanos y todo lo que no esté anclado saldría despedido a velocidad supersónica.",
                        "keywords": ["earth atmosphere", "cyclone earth storm"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 3,
                        "narration": "Los océanos migrarían hacia los polos, creando dos gigantescos mares polares y un megacontinente seco en el centro.",
                        "keywords": ["earth ocean pacific", "earth globe topography"],
                        "visual_type": "image",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 4,
                        "narration": "Un día duraría un año entero: seis meses de calor abrasador seguidos de seis meses de congelación mortal.",
                        "keywords": ["sun solar flare", "sun earth orbit"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 5,
                        "narration": "Por suerte, la rotación de nuestro planeta está a salvo durante miles de millones de años.",
                        "keywords": ["earth deep space milky way", "apollo earth view"],
                        "visual_type": "video",
                        "estimated_duration": 6
                    }
                ]
            }

        elif "agujero" in topic_lower or "black hole" in topic_lower:
            return {
                "title": "El misterio de los Agujeros Negros",
                "hook": "Nada en el universo puede escapar de ellos, ni siquiera la luz.",
                "scenes": [
                    {
                        "scene_id": 1,
                        "narration": "Un agujero negro concentra tanta masa en un punto infinitesimal que deforma el tejido mismo del espacio-tiempo.",
                        "keywords": ["black hole event horizon", "singularity space"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 2,
                        "narration": "Al cruzar el horizonte de sucesos, la gravedad es tan extrema que el tiempo literalmente se ralentiza.",
                        "keywords": ["black hole accretion disk", "galaxy core chandra"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 3,
                        "narration": "Cualquier objeto que caiga experimentaría espaguetización: sería estirado como un hilo cósmico.",
                        "keywords": ["gravitational lensing hubble", "deep space galaxy"],
                        "visual_type": "image",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 4,
                        "narration": "En el centro de casi todas las galaxias habita un monstruo supermasivo millones de veces más pesado que nuestro Sol.",
                        "keywords": ["supermassive black hole", "milky way center sagittarius"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 5,
                        "narration": "Son los motores más fascinantes y oscuros de todo el cosmos.",
                        "keywords": ["cosmos nebula hubble space telescope", "galaxy cluster james webb"],
                        "visual_type": "video",
                        "estimated_duration": 6
                    }
                ]
            }

        elif "marte" in topic_lower or "mars" in topic_lower:
            return {
                "title": "Los Secretos Ocultos de Marte",
                "hook": "¿Sabías que Marte tuvo ríos y océanos más profundos que los de la Tierra?",
                "scenes": [
                    {
                        "scene_id": 1,
                        "narration": "Hace cuatro mil millones de años, el planeta rojo era un mundo cálido y húmedo.",
                        "keywords": ["mars planet", "mars surface curiosity rover"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 2,
                        "narration": "Allí se encuentra el Monte Olimpo, un volcán tres veces más alto que el Everest.",
                        "keywords": ["olympus mons mars", "mars topography global"],
                        "visual_type": "image",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 3,
                        "narration": "Cuando Marte perdió su campo magnético, el viento solar barrió casi toda su atmósfera al espacio.",
                        "keywords": ["solar wind mars maven", "mars atmosphere nasa"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 4,
                        "narration": "Hoy los rovers de la NASA buscan señales fósiles de antigua vida microscópica en sus cráteres.",
                        "keywords": ["perseverance rover mars", "jezero crater mars"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 5,
                        "narration": "¿Será la humanidad la próxima especie en pisar la arena roja marciana?",
                        "keywords": ["mars exploration astronaut artemis", "mars horizon sunset"],
                        "visual_type": "video",
                        "estimated_duration": 6
                    }
                ]
            }

        elif "webb" in topic_lower or "james webb" in topic_lower or "jwst" in topic_lower:
            return {
                "title": "El telescopio James Webb",
                "hook": "Este telescopio espacial está viendo el nacimiento de las primeras galaxias del universo.",
                "scenes": [
                    {
                        "scene_id": 1,
                        "narration": "El telescopio espacial James Webb orbita a un millón y medio de kilómetros de la Tierra.",
                        "keywords": ["james webb space telescope", "jwst launch deployment"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 2,
                        "narration": "Con su espejo bañado en oro y sus cámaras infrarrojas, atraviesa nubes de polvo cósmico impenetrables.",
                        "keywords": ["carina nebula jwst", "pillars of creation webb"],
                        "visual_type": "image",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 3,
                        "narration": "Ha capturado galaxias formadas apenas unos cientos de millones de años tras el Big Bang.",
                        "keywords": ["deep field jwst galaxy cluster", "tarántula nebula webb"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 4,
                        "narration": "También analiza las atmósferas de planetas lejanos buscando vapor de agua y biofirmas.",
                        "keywords": ["exoplanet atmosphere spectrum webb", "trappist 1 system space"],
                        "visual_type": "image",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 5,
                        "narration": "El universo primitivo ya no puede esconder sus secretos más profundos.",
                        "keywords": ["deep space universe cosmos webb", "stars galaxy cluster"],
                        "visual_type": "video",
                        "estimated_duration": 6
                    }
                ]
            }

        elif any(w in topic_lower for w in ["depresion", "depresión", "salud mental", "ansiedad", "estrés", "estres", "tristeza", "cerebro humano"]):
            return {
                "title": "La Ciencia Detrás de la Depresión",
                "hook": "La depresión no es una simple tristeza: es un cambio biológico profundo en las redes neuronales de nuestro cerebro.",
                "scenes": [
                    {
                        "scene_id": 1,
                        "narration": "A nivel microscópico, se produce un desbalance en neurotransmisores esenciales como la serotonina, dopamina y noradrenalina.",
                        "keywords": ["human brain neurons neuroscience", "mental health thoughtful"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 2,
                        "narration": "Estudios neurológicos revelan que regiones como el hipocampo y la corteza prefrontal reducen su actividad y conectividad.",
                        "keywords": ["sad thoughtful person looking at window rain", "deep contemplation emotion"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 3,
                        "narration": "No es una debilidad de carácter ni falta de voluntad: es una condición médica real que altera cómo procesamos las emociones.",
                        "keywords": ["person alone thoughtful dramatic lighting", "mental health support therapy"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 4,
                        "narration": "Gracias a la neuroplasticidad cerebral, la terapia y el tratamiento médico adecuado pueden regenerar estas conexiones neuronales.",
                        "keywords": ["hopeful person walking outside sunrise", "peaceful nature sunlight"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 5,
                        "narration": "Comprender la ciencia de lo que sentimos es el primer paso para acompañar, sanar y buscar ayuda profesional a tiempo.",
                        "keywords": ["support friendship empathy hands together", "warm morning golden light horizon"],
                        "visual_type": "video",
                        "estimated_duration": 6
                    }
                ]
            }

        elif any(w in topic_lower for w in ["oceano", "océano", "mar", "ocean", "marino", "ballena", "coral"]):
            return {
                "title": "Los Secretos del Océano Profundo",
                "hook": "Conocemos mejor la superficie de la Luna que el fondo de nuestros propios océanos.",
                "scenes": [
                    {
                        "scene_id": 1,
                        "narration": "Más del ochenta por ciento del océano permanece completamente inexplorado por el ser humano.",
                        "keywords": ["deep ocean underwater", "ocean waves aerial"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 2,
                        "narration": "A miles de metros de profundidad, la presión aplastante y la oscuridad absoluta ocultan criaturas bioluminiscentes.",
                        "keywords": ["bioluminescent underwater jellyfish", "deep sea creature"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 3,
                        "narration": "En la Fosa de las Marianas, el punto más bajo del planeta, la presión equivale a cien elefantes sobre tu cabeza.",
                        "keywords": ["underwater submarine exploration", "deep ocean trench"],
                        "visual_type": "image",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 4,
                        "narration": "Allí habitan ecosistemas enteros que sobreviven sin luz solar, alimentados por fumarolas volcánicas hidrotermales.",
                        "keywords": ["hydrothermal vent underwater", "coral reef marine life"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 5,
                        "narration": "El verdadero mundo alienígena no está en las estrellas, sino bajo nuestras olas.",
                        "keywords": ["ocean blue water sun rays", "underwater diving ocean"],
                        "visual_type": "video",
                        "estimated_duration": 6
                    }
                ]
            }

        elif any(w in topic_lower for w in ["inteligencia artificial", "ia", "robot", "tecnologia", "futuro", "computadora"]):
            return {
                "title": "La Revolución de la Inteligencia Artificial",
                "hook": "¿Puede una máquina llegar a pensar y crear como un cerebro humano?",
                "scenes": [
                    {
                        "scene_id": 1,
                        "narration": "La inteligencia artificial ya procesa millones de terabytes de datos por segundo superando la velocidad humana.",
                        "keywords": ["artificial intelligence data", "technology server room lights"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 2,
                        "narration": "Redes neuronales inspiradas en nuestra propia biología aprenden a pintar, programar y resolver enigmas científicos.",
                        "keywords": ["neural network futuristic technology", "cyber digital brain"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 3,
                        "narration": "Robots humanoides con visión por computadora empiezan a caminar y coordinarse de forma autónoma.",
                        "keywords": ["humanoid robot technology", "robotics factory automation"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 4,
                        "narration": "Desde curar enfermedades hasta explorar mundos lejanos, la IA transformará cada aspecto de nuestra civilización.",
                        "keywords": ["futuristic city technology", "quantum computer chip"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 5,
                        "narration": "No es ciencia ficción: el futuro digital ya está ocurriendo ahora.",
                        "keywords": ["future technology cybernetic", "abstract digital light code"],
                        "visual_type": "video",
                        "estimated_duration": 6
                    }
                ]
            }

        elif any(w in topic_lower for w in ["volcan", "volcán", "lava", "erupcion", "erupción", "magma"]):
            return {
                "title": "La Furia de los Volcanes",
                "hook": "Bajo nuestros pies arde una roca líquida a más de mil grados Celsius esperando salir.",
                "scenes": [
                    {
                        "scene_id": 1,
                        "narration": "Los volcanes son ventanas directas al ardiente interior del manto terrestre.",
                        "keywords": ["volcano eruption lava flow", "volcano aerial drone"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 2,
                        "narration": "Durante una erupción, la presión de los gases subterráneos dispara ceniza y piroclastos a la estratosfera.",
                        "keywords": ["volcano smoke ash cloud", "active volcano crater"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 3,
                        "narration": "Ríos de lava avanzan implacables devorando todo a su paso y remodelando el relieve.",
                        "keywords": ["glowing lava river basalt", "lava texture glowing red"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 4,
                        "narration": "Paradójicamente, las cenizas volcánicas crean los suelos agrícolas más fértiles y ricos del mundo.",
                        "keywords": ["volcanic mountain landscape", "iceland volcano eruption"],
                        "visual_type": "image",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 5,
                        "narration": "Destrucción y renacimiento: el poder geológico que mantiene vivo a nuestro planeta.",
                        "keywords": ["volcano night glowing magma", "mountain sunset nature landscape"],
                        "visual_type": "video",
                        "estimated_duration": 6
                    }
                ]
            }

        # Generic dynamic documentary template for any custom topic
        is_space_topic = any(w in topic_lower for w in ["espacio", "nasa", "galaxia", "estrella", "planeta", "cosmos", "universo", "astronomia"])
        if is_space_topic:
            return {
                "title": clean_topic,
                "hook": f"Esto es lo que la ciencia y la exploración espacial han descubierto sobre {clean_topic}.",
                "scenes": [
                    {
                        "scene_id": 1,
                        "narration": f"El cosmos nos sorprende constantemente con fenómenos increíbles relacionados con {clean_topic}.",
                        "keywords": [clean_topic, "space astronomy universe"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 2,
                        "narration": "Los telescopios y observatorios han recopilado datos reveladores sobre su comportamiento.",
                        "keywords": ["hubble space telescope observation", "deep space cosmos nebula"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 3,
                        "narration": "A través de la física moderna y la observación directa, entendemos las fuerzas que interactúan.",
                        "keywords": ["stars galaxy cluster", "deep space stars"],
                        "visual_type": "image",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 4,
                        "narration": "Cada nueva misión científica amplía las fronteras de nuestro conocimiento.",
                        "keywords": ["spacecraft exploration cosmos", "earth orbit satellite"],
                        "visual_type": "video",
                        "estimated_duration": 7
                    },
                    {
                        "scene_id": 5,
                        "narration": "El universo sigue guardando secretos esperando a ser descubiertos.",
                        "keywords": ["milky way galaxy universe stars", "deep space horizon stars"],
                        "visual_type": "video",
                        "estimated_duration": 6
                    }
                ]
            }

        # General nature / science / curiosity template
        return {
            "title": clean_topic,
            "hook": f"¿Alguna vez te has preguntado qué hace tan fascinante a {clean_topic}?",
            "scenes": [
                {
                    "scene_id": 1,
                    "narration": f"En el mundo que nos rodea, {clean_topic} esconde detalles asombrosos que pocos conocen.",
                    "keywords": [clean_topic, "nature cinematic aerial"],
                    "visual_type": "video",
                    "estimated_duration": 7
                },
                {
                    "scene_id": 2,
                    "narration": "Investigaciones científicas han revelado patrones y comportamientos realmente sorprendentes.",
                    "keywords": [f"{clean_topic} detail", "scientific technology macro"],
                    "visual_type": "video",
                    "estimated_duration": 7
                },
                {
                    "scene_id": 3,
                    "narration": "Cada aspecto de su estructura demuestra una precisión y complejidad extraordinaria.",
                    "keywords": [f"{clean_topic} close up", "dramatic landscape cinematic"],
                    "visual_type": "image",
                    "estimated_duration": 7
                },
                {
                    "scene_id": 4,
                    "narration": "Comprender este fenómeno nos permite entender mucho mejor cómo funciona la naturaleza.",
                    "keywords": [clean_topic, "discovery exploration cinematic"],
                    "visual_type": "video",
                    "estimated_duration": 7
                },
                {
                    "scene_id": 5,
                    "narration": "El conocimiento avanza rápido, y aún queda mucho por explorar.",
                    "keywords": ["cinematic horizon inspiring nature", "golden hour landscape"],
                    "visual_type": "video",
                    "estimated_duration": 6
                }
            ]
        }
