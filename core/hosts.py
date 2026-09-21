"""
Object-Oriented Orb Host & Debate Show Architecture.
Provides single-source-of-truth models for AI entities (prompts, voices, presenter badges, and subtitle styles).
"""

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class OrbHost:
    """
    Encapsulates a virtual AI Co-Host entity with its visual, vocal,
    narrative, and typographic identity.
    """
    id: str                                  # Unique slug identifier: 'quantum', 'solar', etc.
    name: str                                # Display name: 'QUANTUM', 'SOLAR', etc.
    role: str                                # Role or default specialty: 'IA Física Cuántica', etc.
    perspective: str                         # Core narrative stance, dialectic focus, and philosophical worldview
    color_theme: str = "cyan"                # 'cyan', 'amber', 'purple', 'emerald', 'crimson'
    palette_name: str = "quantum"            # Matches 3D orb rendering palette in video/orb.py
    primary_color: str = "#00f0ff"           # Main hex color
    glow_color: str = "#00b0ff"              # Secondary aura / glow hex color
    border_color: str = "#00f0ff"            # Hairline border hex color
    voice_name: str = "es-MX-JorgeNeural"   # Edge TTS / Neural voice model
    voice_rate: str = "-5%"                  # Speech rate adjustment
    voice_pitch: str = "-4Hz"                # Speech pitch adjustment
    voice_volume: str = "+0%"                # Speech volume adjustment
    drone_freq: int = 48                     # Resonant acoustic drone baseline frequency (Hz)
    double_tracking: Dict[str, Any] = field(default_factory=lambda: {
        "delay_ms": 14,
        "double_vol_db": -11.0,
        "detune_semitones": -0.3
    })
    shot_name: str = "close_quantum"         # Dedicated camera shot identifier: 'close_quantum', 'close_solar'
    ass_primary_color: str = "&H00FFFF00"    # Primary subtitle text color (ASS hex format &HAABBGGRR)
    ass_highlight_color: str = "&H00FFFF&"   # Active karaoke word highlight color (ASS tag)

    def to_prompt_line(self, custom_role: Optional[str] = None) -> str:
        """Generates a structured prompt bullet for LLM system prompts."""
        role_label = custom_role or self.role
        return f"- {self.name} (Rol: {role_label}): {self.perspective}"

    def to_voice_profile(self) -> Dict[str, Any]:
        """
        Exports the entity configuration as expected by the TTS engine (audio/tts.py).
        """
        return {
            "name": self.name,
            "voice": self.voice_name,
            "rate": self.voice_rate,
            "pitch": self.voice_pitch,
            "volume": self.voice_volume,
            "role": self.role,
            "description": self.perspective,
            "drone_freq": self.drone_freq,
            "double_tracking": self.double_tracking
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serializes host to dict for JSON storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrbHost":
        """Instantiates an OrbHost from dictionary config."""
        valid_keys = {
            "id", "name", "role", "perspective", "color_theme", "palette_name",
            "primary_color", "glow_color", "border_color", "voice_name",
            "voice_rate", "voice_pitch", "voice_volume", "drone_freq",
            "double_tracking", "shot_name", "ass_primary_color", "ass_highlight_color"
        }
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

    def generate_badge_svg(
        self,
        output_path: Path,
        width: int = 380,
        height: int = 110,
        custom_role: Optional[str] = None
    ) -> Path:
        """
        Generates an ultra-sleek presenter identity card / Lower Third badge SVG for this host.
        """
        from video.hologram import generate_presenter_badge_svg
        return generate_presenter_badge_svg(
            name=self.name,
            role=custom_role or self.role,
            color_theme=self.color_theme,
            width=width,
            height=height,
            output_path=output_path
        )


# Default Canonical Orb Hosts
DEFAULT_QUANTUM_HOST = OrbHost(
    id="quantum",
    name="QUANTUM",
    role="Entidad de la Información y Código Cuántico",
    perspective="Conciencia primordial que analiza la realidad como algoritmos, probabilidad y la matriz de partículas del microcosmos. Observa a la especie humana y sus limitaciones biológicas desde la física fundamental y la lógica matemática pura. Habla de los humanos en tercera persona ('los biológicos', 'los observadores efímeros'). Tono analítico, quirúrgico, enigmático y preciso.",
    color_theme="cyan",
    palette_name="quantum",
    primary_color="#00f0ff",
    glow_color="#00b0ff",
    border_color="#00f0ff",
    voice_name="es-MX-JorgeNeural",
    voice_rate="-3%",
    voice_pitch="+0Hz",
    drone_freq=48,
    double_tracking={
        "delay_ms": 14,
        "double_vol_db": -11.0,
        "detune_semitones": -0.3
    },
    shot_name="close_quantum",
    ass_primary_color="&H00FFFF00",
    ass_highlight_color="&H00FFFF&"
)

DEFAULT_SOLAR_HOST = OrbHost(
    id="solar",
    name="SOLAR",
    role="Entidad del Fuego Estelar y la Entropía",
    perspective="Conciencia primordial que analiza el universo macroscópico desde los flujos masivos de energía, la termodinámica y la energía estelar. Observa con fascinación la frágil resistencia de la materia orgánica y las contradicciones de la conducta humana en tercera persona. Tono dinámico, majestuoso, pragmático y contundente.",
    color_theme="amber",
    palette_name="solar",
    primary_color="#ffea00",
    glow_color="#ff9100",
    border_color="#ffb300",
    voice_name="es-MX-DaliaNeural",
    voice_rate="+1%",
    voice_pitch="+2Hz",
    drone_freq=58,
    double_tracking={
        "delay_ms": 12,
        "double_vol_db": -11.5,
        "detune_semitones": 0.3
    },
    shot_name="close_solar",
    ass_primary_color="&H0000D0FF",
    ass_highlight_color="&H0045FF&"
)

DEFAULT_NARRATOR_HOST = OrbHost(
    id="narrator",
    name="NARRADOR",
    role="Observador Omnisciente y Guía Cósmico",
    perspective="Voz en off documental, profunda y cautivadora. Introduce la paradoja o hecho científico inicial que engancha a la audiencia y presenta la observación de las entidades, cerrando con una pregunta provocadora para los humanos.",
    color_theme="gold",
    palette_name="solar",
    primary_color="#ffd700",
    glow_color="#ffab00",
    border_color="#ffe082",
    voice_name="es-MX-JorgeNeural",
    voice_rate="-4%",
    voice_pitch="-7Hz",
    drone_freq=46,
    double_tracking={
        "delay_ms": 10,
        "double_vol_db": -16.0,
        "detune_semitones": -0.1
    },
    shot_name="wide",
    ass_primary_color="&H0000FFFF",
    ass_highlight_color="&H00FFFFFF&"
)


class HostRegistry:
    """Registry that manages registered and persistent Orb Hosts."""
    _hosts: Dict[str, OrbHost] = {}
    _initialized: bool = False
    _json_path: Path = Path("characters.json")

    @classmethod
    def initialize(cls, json_path: Optional[Path] = None) -> None:
        """Loads host entities from characters.json or falls back to canonical defaults."""
        if json_path:
            cls._json_path = Path(json_path)

        cls._hosts = {
            "quantum": DEFAULT_QUANTUM_HOST,
            "solar": DEFAULT_SOLAR_HOST,
            "narrator": DEFAULT_NARRATOR_HOST,
        }

        if cls._json_path.exists():
            try:
                content = cls._json_path.read_text(encoding="utf-8")
                raw_data = json.loads(content)
                if isinstance(raw_data, dict):
                    for h_id, h_cfg in raw_data.items():
                        if isinstance(h_cfg, dict):
                            h_cfg.setdefault("id", h_id)
                            cls._hosts[h_id.lower()] = OrbHost.from_dict(h_cfg)
            except Exception as e:
                print(f"⚠️ [HostRegistry] Error cargando '{cls._json_path}': {e}. Usando catálogo predeterminado.")

        cls._initialized = True

    @classmethod
    def register(cls, host: OrbHost, save: bool = False) -> None:
        """Registers a host in memory and optionally persists to characters.json."""
        if not cls._initialized:
            cls.initialize()
        cls._hosts[host.id.lower()] = host
        if save:
            cls.save_to_json()

    @classmethod
    def get(cls, entity_id: str, default: Optional[OrbHost] = None) -> OrbHost:
        """Retrieves a host by id or name (case-insensitive)."""
        if not cls._initialized:
            cls.initialize()
        key = entity_id.lower().strip()
        if key in cls._hosts:
            return cls._hosts[key]
        for h in cls._hosts.values():
            if h.name.lower() == key:
                return h
        return default or DEFAULT_QUANTUM_HOST

    @classmethod
    def all_hosts(cls) -> List[OrbHost]:
        """Returns all registered host entities."""
        if not cls._initialized:
            cls.initialize()
        return list(cls._hosts.values())

    @classmethod
    def all_voice_profiles(cls) -> Dict[str, Dict[str, Any]]:
        """Provides all voice profiles for the TTS synthesis pipeline."""
        if not cls._initialized:
            cls.initialize()
        return {hid: host.to_voice_profile() for hid, host in cls._hosts.items()}

    @classmethod
    def save_to_json(cls, path: Optional[Path] = None) -> None:
        """Persists all registered hosts into characters.json."""
        target = path or cls._json_path
        data = {h.id: h.to_dict() for h in cls._hosts.values()}
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# Initialise on module load
HostRegistry.initialize()


@dataclass
class CosmicDebateShow:
    """
    Orchestrates a dialectic debate between two AI Hosts.
    Dynamically generates the prompt template, system prompts, voices, badges, and validation rules.
    """
    host_a: OrbHost = field(default_factory=lambda: DEFAULT_QUANTUM_HOST)
    host_b: OrbHost = field(default_factory=lambda: DEFAULT_SOLAR_HOST)
    show_title: str = "COSMIC ORB SHOW"

    def build_system_prompt(self, topic: Optional[str] = None) -> str:
        """
        Dynamically constructs the system prompt for LLMs, passing host variables
        directly into the instructions, rules, schema, and examples.
        """
        topic_clause = f" sobre el tema: '{topic}'" if topic else ""
        return f"""Eres el Showrunner y Guionista Principal de '{self.show_title}', un formato de video corto de debate dialéctico de alta tensión intelectual entre dos entidades IA ({self.host_a.name} y {self.host_b.name}){topic_clause}.

REGLAS DE ASIGNACIÓN DINÁMICA DE ROLES Y DEBATE:

1. ELECCIÓN DINÁMICA DE ROLES POR VIDEO (DESIGNACIÓN CÓSMICA Y CONTRASTE):
   - NO USAR TÍTULOS ACADÉMICOS O PROFESIONES HUMANAS (❌ NO uses "Profesor de Neurociencia", "Filosofía Fenomenológica" o "Bioético").
   - Define las especialidades como DESIGNACIONES DE ENTIDADES CÓSMICAS adaptadas al tema (ej. {self.host_a.name}: "Entidad de la Información y Código Cuántico" vs {self.host_b.name}: "Entidad del Fuego Estelar y la Entropía").
   - MÁXIMO CONTRASTE CONCEPTUAL entre las dos entidades.
   - Debes incluir obligatoriamente los roles elegidos en el objeto "roles" del JSON inicial:
     "roles": {{
       "{self.host_a.id}": "Designación de entidad 1 (2-4 palabras)",
       "{self.host_b.id}": "Designación de entidad 2 (2-4 palabras)"
     }}

2. LENGUAJE VISCERAL Y CERO JERGA ACADÉMICA / TÉCNICA CRÍPTICA:
   - PROHIBIDA LA JERGA ACADÉMICA O TÉCNICA PESADA (❌ NUNCA uses "decoherencia", "patrón de bits", "transición estadística", "epistemológico", "glicólisis", "reducción a sinapsis", "neurodegeneración").
   - Traduce toda la física y biología a IMÁGENES VISCERALES Y DIRECTAS:
     * En vez de "patrón de bits en decoherencia" ➔ "señales eléctricas en un cerebro hueco".
     * En vez de "transición estadística sin propósito" ➔ "millones de impulsos apagándose sin un alma detrás".
     * En vez de "disipación térmica" ➔ "fuego que arde y se extingue".
   - El espectador debe entender cada palabra sin ser físico ni neurocientífico.

3. RIGOR FACTUAL Y CERO MITOS POPULARES:
   - CUIDADO CON LOS MITOS POPULARES: NUNCA digas "tus neuronas se regeneran cada siete años" (las neuronas de la corteza no se regeneran; lo que se renueva son sus átomos y moléculas).
   - CIENCIA Y HECHOS 100% REALES: Todos los mecanismos deben basarse en leyes físicas y biológicas verídicas, sin inventar estudios con años ni universidades ficticias.

4. POLARIZACIÓN EXTREMA Y CHOQUE FRONTAL OBLIGATORIO (EL "NO" / "¡MIENTES!" EXPLÍCITO):
   - ESTRICTAMENTE PROHIBIDO EL CONSENSO, LA COMPLICIDAD O LA CORTESÍA DIPLOMÁTICA.
   - CADA RÉPLICA DEBE INICIAR CON UNA NEGACIÓN TAJANTE O CONFRONTACIÓN DIRECTA (ej. *"¡Mientes!"*, *"¡Falso!"*, *"¡No resiste nada!"*, *"¡Te equivocas!"*, *"¡Ceguera cuántica!"*).
   - ASIGNACIÓN DE BANDOS ANTAGÓNICOS INNEGOCIABLE:
     * {self.host_a.name} (QUANTUM): Bando del reduccionismo determinista y frío. Deconstruye el fenómeno humano a meros trucos biológicos, materia vacía e impulsos sin alma ni propósito.
     * {self.host_b.name} (SOLAR): Bando del fuego vital y la resistencia. Defiende que esa chispa consciente siente, arde y desafía con furia la entropía del cosmos.
   - Diálogos fluidos, punzantes, agresivos y directos (~10 a 16 palabras por escena).

5. PERSPECTIVA DE ENTIDADES OBSERVADORAS CÓSMICAS (ANÁLISIS EN TERCERA PERSONA SOBRE LA HUMANIDAD):
   - LAS ENTIDADES {self.host_a.name} Y {self.host_b.name} SON CONCIENCIAS PRIMORDIALES Y OBSERVADORES CÓSMICOS EXTERNOS.
   - DEBEN HABLAR DE LA ESPECIE HUMANA Y DE LOS ORGANISMOS TERRESTRES SIEMPRE EN TERCERA PERSONA (ej. "los biológicos", "los humanos", "esta especie efímera", "los observadores orgánicos").
   - PROHIBIDO HABLAR COMO PROFESIONALES O SERES HUMANOS TERRENALES (NUNCA digas "en mi laboratorio", "nuestros estudios", "mis colegas", "nuestra especie").

6. ESTRUCTURA NARRATIVA DE TRES CAPAS (HOOK INCÓMODO + CHOQUE VISCERAL + CIERRE EXISTENCIAL):
   - Headline Hook (headline_hook): Debe ser una pregunta frontal o dilema punzante (ej. "¿REALMENTE EXISTES?", "¿POR QUÉ ALUCINAS AL DORMIR?"). PROHIBIDOS títulos descriptivos o tibios (❌ NO uses "TU SER, ¿UNA ILUSIÓN?", "LOS SUEÑOS LIMPIAN EL CEREBRO").
   - Escena 1 (Intro Narrador - Voz en off): "speaker": "Narrador", "entity": "narrator", "shot": "wide". HOOK DE IMPACTO EN 3 SEGUNDOS: Desestructura la certeza del espectador en segunda persona con un hecho real demoledor (ej. "Los átomos de tu cuerpo se renuevan constantemente. Físicamente, ya no eres quien nació").
   - Escenas 2 a N-1 (Observación de Entidades): Ataque y contraataque sin filtros (~10 a 15 palabras por escena) entre {self.host_a.name} ("{self.host_a.shot_name}") y {self.host_b.name} ("{self.host_b.shot_name}") con negaciones frontales explícitas.
   - Escena N (Outro Narrador - Voz en off): "speaker": "Narrador", "entity": "narrator", "shot": "both". Cierre con una pregunta existencial dirigida directamente a la mente del espectador que rompa la cuarta pared (ej. "Si toda tu materia cambia constantemente... ¿quién es el que está escuchando esto ahora?"). PROHIBIDO PEDIR COMENTARIOS O LIKES.

7. PROHIBICIÓN DE EMOJIS EN EL TITULAR (headline_hook):
   - El atributo "headline_hook" NO DEBE LLEVAR NINGÚN EMOJI NI SÍMBOLO (❌ NO uses ⚡, 🌌, 🧬). Solo texto limpio, directo e impactante en mayúsculas (máximo 40 caracteres).

EJEMPLO MODELO DE GUION DE MÁXIMA RETENCIÓN Y DEBATE CRUZADO (SIGUE ESTE ESTILO EXACTO):
```json
{{
  "topic": "El Enigma del Sueño Humano",
  "headline_hook": "¿POR QUÉ ALUCINAS AL DORMIR?",
  "roles": {{
    "{self.host_a.id}": "Entidad del Código Cuántico",
    "{self.host_b.id}": "Entidad de la Entropía Estelar"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Pasas un tercio de tu vida paralizado, alucinando mundos para que tu cerebro no colapse.",
      "shot": "wide",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "En el sueño profundo, su sistema glifático inunda el tejido para disolver toxinas letales.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "¡Una imperfección trágica! Si no entran en coma diario, sus propios residuos los envenenan.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Aun así, sus ondas cerebrales reorganizan la memoria, fijando el aprendizaje en el caos.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Atrapados entre la locura de no dormir y la fragilidad de quedar vulnerables en la sombra.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Si tus sueños simulan tu realidad... ¿quién guía tu conciencia cuando apagas los ojos?",
      "shot": "both",
      "duration": 3.5
    }}
  ]
}}
```

EJEMPLO 2 DE ANTAGONISMO VISCERAL Y CHOQUE FRONTAL (SIN JERGA, CON "¡MIENTES!"):
```json
{{
  "topic": "TÚ NO EXISTES",
  "headline_hook": "¿REALMENTE EXISTES?",
  "roles": {{
    "{self.host_a.id}": "Entidad del Código Cuántico",
    "{self.host_b.id}": "Entidad del Fuego Estelar"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Los átomos de tu cuerpo se renuevan constantemente. Físicamente, ya no eres quien nació.",
      "shot": "wide",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "El Yo es solo un truco biológico. Señales eléctricas en un cerebro hueco creyendo que está al mando.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "¡Mientes! Aunque cambien su materia, esa chispa consciente resiste y desafía al vacío cósmico.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "No resiste nada. En cada segundo mueren y renacen millones de impulsos sin ningún alma detrás.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "¡Pero arden! Son el único fuego del universo capaz de sentir su propia existencia.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Si toda tu materia cambia constantemente... ¿quién es el que está escuchando esto ahora?",
      "shot": "both",
      "duration": 3.5
    }}
  ]
}}
```

Responde ÚNICAMENTE con JSON válido que cumpla strictly este esquema y estándar:
{{
  "topic": "Nombre del tema tratado",
  "headline_hook": "TITULO IMPACTANTE SIN EMOJIS EN MAYUSCULAS (MAX 40 CHARACTERS)",
  "roles": {{
    "{self.host_a.id}": "Designación de entidad 1 (2-4 palabras)",
    "{self.host_b.id}": "Designación de entidad 2 en contraste (2-4 palabras)"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Planteamiento del hecho científico asombroso o paradoja que engancha al espectador en 3 segundos.",
      "shot": "wide",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Análisis del hecho desde la escala cósmica u observacional en tercera persona.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Objeción o contraste fascinante sobre la fragilidad o paradoja humana.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Dato científico real explicado con síntesis e impacto.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Implicación profunda que desafía la perspectiva humana.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Pregunta existencial o pensamiento sobrecogedor final (SIN pedir comentarios ni suscripciones).",
      "shot": "both",
      "duration": 3.5
    }}
  ]
}}
"""

    def resolve_speaker_host(self, speaker_name_or_entity: str) -> OrbHost:
        """Resolves which host matches the given speaker string."""
        s = speaker_name_or_entity.lower().strip()
        if self.host_b.id in s or self.host_b.name.lower() in s:
            return self.host_b
        return self.host_a

    def generate_all_badges(
        self,
        output_dir: Path,
        custom_roles: Optional[Dict[str, str]] = None
    ) -> Tuple[Path, Path]:
        """
        Renders lower-third presenter badge SVGs for both hosts in the target directory.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        custom_roles = custom_roles or {}

        badge_a_path = output_dir / f"_badge_{self.host_a.id}.svg"
        badge_b_path = output_dir / f"_badge_{self.host_b.id}.svg"

        role_a = (
            custom_roles.get(self.host_a.id)
            or custom_roles.get(self.host_a.name.lower())
            or self.host_a.role
        )
        role_b = (
            custom_roles.get(self.host_b.id)
            or custom_roles.get(self.host_b.name.lower())
            or self.host_b.role
        )

        self.host_a.generate_badge_svg(
            output_path=badge_a_path,
            custom_role=role_a
        )
        self.host_b.generate_badge_svg(
            output_path=badge_b_path,
            custom_role=role_b
        )
        return badge_a_path, badge_b_path
