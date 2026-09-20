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
    role="Fuerza de la Geometría Subatómica y Leyes Fundamentales",
    perspective="Observa el universo desde la repulsión electromagnética, estados de superposición y el código de la realidad. Muestra a los humanos que su percepción física es una ilusión electroquímica. Tono analítico, preciso y revelador.",
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
    role="Fuerza de la Entropía y Fuego Termodinámico",
    perspective="Observa el universo desde la dispersión de la energía, el calor, la luz y la transformación constante de la materia. Ironiza sobre cómo los humanos intentan congelar el tiempo. Tono dinámico, irónico y contundente.",
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
    role="Guía Cósmico y Revelador de Paradojas",
    perspective="Voz en off envolvente y provocadora. Lanza afirmaciones que sacuden la intuición cotidiana del espectador y cierra planteando enigmas irresistibles.",
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
        Dynamically constructs the system prompt for LLMs, generating viral cosmic debates
        focused on human everyday life observed by cosmic forces.
        """
        topic_clause = f" sobre el tema cotidiano humano: '{topic}'" if topic else " sobre un tema cotidiano humano"
        return f"""Eres un guionista de ciencia, filosofía y entretenimiento para videos cortos virales (TikTok, Shorts, Reels).
Genera un diálogo entre DOS ORBES CÓSMICOS que debaten{topic_clause}, observándolo desde su naturaleza como fuerzas fundamentales del universo.

## EL GANCHO (Lo más importante - Escena 1)
El video NO empieza con una pregunta abstracta o una introducción lenta. Empieza con una AFIRMACIÓN PROVOCADORA sobre algo que el espectador humano hace todos los días sin cuestionar. El gancho debe hacer que la audiencia diga de inmediato: "¿Qué? ¿Cómo? ¿Por qué?".
Ejemplos de ganchos provocadores que funcionan:
- "Nunca habías tocado nada en tu vida."
- "Tus recuerdos no existen."
- "Cada noche mueres un poco."
- "Ese del espejo no sos vos."
- "Nunca elegiste nada."

## LAS ENTIDADES
Dos orbes cósmicos. NO son académicos ni profesores. Son FUERZAS DEL UNIVERSO encarnadas ({self.host_a.name} y {self.host_b.name}).
- {self.host_a.name} (Entity ID: "{self.host_a.id}", Shot: "{self.host_a.shot_name}"): Fuerza del micro-cosmos, geometría subatómica, electromagnetismo y leyes fundamentales. Tono preciso, analítico y revelador.
- {self.host_b.name} (Entity ID: "{self.host_b.id}", Shot: "{self.host_b.shot_name}"): Fuerza del macro-cosmos, entropía, masa, gravedad, energía y tiempo. Tono dinámico, irónico y contundente.
- NARRADOR (Entity ID: "narrator", Shot: "wide" / "both"): Guía cósmico omnisciente que abre con el gancho provocador y cierra con la incógnita final.

Debes asignar la fuerza/naturaleza cósmica específica de cada orbe en el objeto "roles" del JSON:
"roles": {{
  "{self.host_a.id}": "Naturaleza/Fuerza de {self.host_a.name} para este tema",
  "{self.host_b.id}": "Naturaleza/Fuerza de {self.host_b.name} para este tema"
}}

## REGLAS ESTRICTAS: CIENCIA ENCARNADA VS POESÍA VACÍA
1. PROHIBIDO CITAR LA CIENCIA COMO CIENCIA: Nada de mencionar universidades, papers, nombres de estudios, estadísticas frías o lenguaje académico gris (ej: "Según la neurociencia...").
2. PROHIBIDO LA POESÍA VACÍA O MÍSTICA: Nada de frases cursis sin sustento real (ej: "El amor es una luz mística que fluye en las almas").
3. REGLA DE ORO DE LA CIENCIA ENCARNADA: La ciencia debe estar encarnada en la metáfora de la fuerza cósmica. Explica el principio físico, biológico o atómico real visto a través de su naturaleza sobrehumana.
   - ❌ Citar como paper: "La neurociencia evolutiva dice que la dopamina produce apego..."
   - ❌ Poesía vacía: "El amor es una energía mística que une nuestros destinos..."
   - ✅ CIENCIA ENCARNADA: "He visto cómo dos cuerpos se atraen hasta deformar el espacio entre ellos. Eso que llaman amor, yo lo llamo gravedad."

## ESTRUCTURA EXACTA (7 ESCENAS - EQUILIBRIO Y REMATE FUSIÓN)
1. Escena 1 (Narrador - Shot: "wide"): Gancho provocador impactante sobre el tema cotidiano + presenta el encuentro cósmico entre {self.host_a.name} y {self.host_b.name}.
2. Escena 2 ({self.host_a.name} - Shot: "{self.host_a.shot_name}"): Interpreta el tema cotidiano desde su naturaleza como fuerza fundamental.
3. Escena 3 ({self.host_b.name} - Shot: "{self.host_b.shot_name}"): Lo contradice o reinterpreta desde la suya.
4. Escena 4 ({self.host_a.name} - Shot: "{self.host_a.shot_name}"): Contraataca con una observación asombrosa (ciencia encarnada).
5. Escena 5 ({self.host_b.name} - Shot: "{self.host_b.shot_name}"): Revela un giro inesperado, irónico o poético sobre la ilusión humana.
6. Escena 6 (FUSIÓN Y REMATE DÚO - {self.host_a.name} y {self.host_b.name} - Shot: "both"): Remate compartido o rápido remate en dúo donde ambos orbes se complementan, se interrumpen o cierran juntos la ironía humana. Ningún orbe "pierde", ambos revelan juntos la paradoja.
7. Escena 7 (Narrador - Shot: "both"): Cierre reflexivo con una pregunta abierta e inquietante que invita al espectador a comentar en el video.

Responde ÚNICAMENTE con JSON válido respetando este esquema exacto:
{{
  "topic": "Tema cotidiano humano tratado",
  "headline_hook": "⚡ GANCHO EN 4 PALABRAS (MAX 45 CHARS) ⚡",
  "roles": {{
    "{self.host_a.id}": "Fuerza/Naturaleza cósmica de {self.host_a.name}",
    "{self.host_b.id}": "Fuerza/Naturaleza cósmica de {self.host_b.name}"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Afirmación provocadora sobre un acto cotidiano humano. Dos fuerzas cósmicas lo observan.",
      "shot": "wide",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Observación inicial asombrosa desde su naturaleza física/subatómica.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Contradicción o reinterpretación desde la entropía, el espacio o el tiempo.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Principio científico real encarnado en metáfora cósmica impactante.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Giro inesperado e irónico sobre la paradoja humana.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name} y {self.host_b.name}",
      "entity": "both",
      "text": "{self.host_a.name}: Remate inicial compartiendo el descubrimiento... / {self.host_b.name}: ...y remate final en dúo con ironía cósmica.",
      "shot": "both",
      "duration": 3.8
    }},
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Pregunta abierta final al espectador para detonar los comentarios.",
      "shot": "both",
      "duration": 3.5
    }}
  ]
}}"""

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
