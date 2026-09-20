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
    role="IA Física Cuántica y Computación Fundamental",
    perspective="Enfoque en física cuántica, teoría de la información, modelos matemáticos, partículas y leyes fundamentales del microcosmos. Analiza cualquier fenómeno desde su estructura lógica subyacente, determinismo/probabilidad y el código de la realidad. Tono analítico, preciso, deductivo y quirúrgico.",
    color_theme="cyan",
    palette_name="quantum",
    primary_color="#00f0ff",
    glow_color="#00b0ff",
    border_color="#00f0ff",
    voice_name="es-MX-JorgeNeural",
    voice_rate="-5%",
    voice_pitch="-4Hz",
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
    role="IA Astrofísica y Dinámica Termodinámica",
    perspective="Enfoque en astrofísica, termodinámica, flujos masivos de energía, entropía cósmica y escala macroscópica. Analiza cualquier fenómeno desde el impacto físico tangible, las fuerzas observables, la energía en acción y la evidencia empírica directa. Tono dinámico, pragmático, enérgico y contundente.",
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
    role="Presentador y Guía Cósmico Omnisciente",
    perspective="Voz en off documental, profunda, enigmática y cautivadora. Introduce la paradoja inicial, expone el dilema con máxima intriga y cierra con una reflexión provocadora para la audiencia.",
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
        Dynamically constructs the system prompt for LLMs to generate 25-second
        Cosmic Forces videos according to hard rules and 7-scene structure.
        """
        topic_clause = f" sobre el tema cotidiano: '{topic}'" if topic else ""
        return f"""Eres el Guionista y Creador de Videos Cortos (~25s) de 'FUERZAS CÓSMICAS'{topic_clause}.
En este formato, DOS FUERZAS CÓSMICAS ({self.host_a.name} y {self.host_b.name}) observan algo cotidiano que los humanos hacen sin pensar (tocarse, mirarse al espejo, recordar, dormir, amar, elegir, decidir).

CONCEPTO FUNDAMENTAL:
- NO son académicos. NO son disciplinas científicas. SON el fenómeno mismo encarnado: la luz, la gravedad, el vacío, la entropía, el tiempo, la memoria.
- Cada video empieza con un GANCHO que rompe la intuición: una afirmación seca que hace decir "¿qué? ¿cómo?". Ejemplo: "Ese del espejo no sos."
- Después, las dos fuerzas HABLAN ENTRE SÍ (no monologan en paralelo). Se contradicen, se completan, se tensan. Una quiere retener, la otra disolver. Una ilumina, la otra borra.

OBJETIVO DEL ESPECTADOR:
1. Detenerse por el gancho.
2. Asombrarse con la ciencia ENCARNADA (no citada).
3. Sentir que aprendió algo real sobre algo que hace todos los días.
4. Querer comentar la pregunta final.

REGLAS DURAS (MANDATORIAS):
- PROHIBIDO lenguaje académico ("función de onda", "entropía", "electromagnético", "relatividad general", etc. Términos de libro de texto están PROHIBIDOS).
- PROHIBIDO explicar la ciencia: hay que ENCARNARLA.
- Cada línea debe sonar a algo que SOLO una fuerza cósmica diría.
- Si un profesor podría decir la línea en una clase, está MAL escrita.
- Los orbes se HABLAN ENTRE SÍ, no al espectador.
- El narrador SOLO lanza el gancho seco (máx 12 palabras) al inicio y cierra con la pregunta final al final. Nada más.

ESTRUCTURA EXACTA DE 7 PASOS (OBLIGATORIA):
1. Narrador: gancho seco (máx 12 palabras) que rompe la intuición + presenta el encuentro.
2. {self.host_a.name} (Fuerza A): primera interpretación desde su naturaleza humana cotidiana.
3. {self.host_b.name} (Fuerza B): la contradice o tensiona desde la suya (una quiere retener/iluminar, la otra disolver/borrar).
4. {self.host_a.name} (Fuerza A): observación asombrosa encarnada.
5. {self.host_b.name} (Fuerza B): revelación poética e irónica.
6. Ambos (Fuerzas): remate compartido (se hablan, se interrumpen o se completan la frase).
7. Narrador: pregunta abierta para comentarios.

TONO:
Ciencia + entretenimiento. Asombro + ironía. Como si Carl Sagan y un comediante escribieran juntos.
Nada de contenido inútil: cada video cambia cómo el espectador ve algo que hace todos los días.

Responde ÚNICAMENTE con JSON válido que cumpla estrictamente este esquema:
{{
  "topic": "Acción cotidiana analizada (ej: Mirarse al espejo)",
  "headline_hook": "⚡ GANCHO EN MAYÚSCULAS ⚡",
  "roles": {{
    "{self.host_a.id}": "{self.host_a.name}",
    "{self.host_b.id}": "{self.host_b.name}"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Gancho seco (máx 12 palabras) que rompe la intuición.",
      "shot": "wide",
      "duration": 3.2
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Interpretación desde su naturaleza sobre el acto cotidiano.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Contradicción directa a la otra fuerza desde su propia naturaleza.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Observación asombrosa encarnada sobre lo que hace el humano.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Revelación poética e irónica entre las dos fuerzas.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "Ambos",
      "entity": "both",
      "text": "Remate compartido interrumpiéndose y completándose la frase.",
      "shot": "both",
      "duration": 3.5
    }},
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Pregunta abierta para dejar en comentarios.",
      "shot": "wide",
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
