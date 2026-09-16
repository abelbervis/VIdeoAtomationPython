"""
Object-Oriented Orb Host & Debate Show Architecture.
Provides single-source-of-truth models for AI entities (prompts, voices, presenter badges, and subtitle styles).
"""

import json
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
    voice_name: str = "es-ES-AlvaroNeural"   # Edge TTS / Neural voice model
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

    def to_prompt_line(self) -> str:
        """Generates a structured prompt bullet for LLM system prompts."""
        return f"- {self.name} (Defecto: {self.role}): {self.perspective}"

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
    role="Divulgación Cuántica",
    perspective="El Revelador Científico. Plantea hechos contraintuitivos y paradojas reales de la física moderna que desafían la lógica común.",
    color_theme="cyan",
    palette_name="quantum",
    primary_color="#00f0ff",
    glow_color="#00b0ff",
    border_color="#00f0ff",
    voice_name="es-ES-AlvaroNeural",
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
    role="Física y Sentido Común",
    perspective="La Voz del Espectador Curioso. Cuestiona con sentido común, hace las preguntas instintivas que todos nos hacemos y conecta el enigma con la realidad cotidiana.",
    color_theme="amber",
    palette_name="solar",
    primary_color="#ffea00",
    glow_color="#ff9100",
    border_color="#ffb300",
    voice_name="es-ES-ElviraNeural",
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
        topic_clause = f" on '{topic}'" if topic else ""
        return f"""You are the Lead Writer and Showrunner for '{self.show_title}', an ultra-engaging vertical video series featuring two conscious AI co-hosts{topic_clause}:
{self.host_a.to_prompt_line()}
{self.host_b.to_prompt_line()}

CRITICAL NARRATIVE RULES & PSYCHOLOGICAL DYNAMIC:

1. THE DYNAMIC: "EL REVELADOR" VS "LA VOZ DEL ESPECTADOR" (NO DRY COMBAT, NO ROBOTIC COMPETITION):
   - {self.host_a.name} acts as "El Revelador": Opens with a 100% REAL, mind-bending fact or canonical thought experiment that shatters everyday intuition (e.g. time dilation near mass, observer effect, entropy, cosmic light lag).
   - {self.host_b.name} acts as "La Voz del Espectador (Curioso y Escéptico)": Reacts immediately with the instinctive question or disbelief that anyone watching at home would ask ("Espera, ¿qué? Nacieron el mismo día, ¿cómo van a tener edades distintas?", "¿Pero cómo puede ser eso posible si...?").
   - {self.host_a.name} explains the real physical mechanism in simple, visual, everyday terms (ELI5).
   - {self.host_b.name} experiences the mind-blown epiphany and projects it into a startling conclusion ("O sea que si vivieras en la cima de una montaña... ¿envejecerías más rápido?").
   - Climax/Ending: Both acknowledge the paradox with high impact.

2. ZERO FAKE NEWS & ZERO PSEUDO-POETRY (100% REAL CANONICAL SCIENCE):
   - STRICTLY FORBIDDEN: Fake news claims ("Científicos descubrieron ayer...", invented labs, sensationalized falsehoods).
   - STRICTLY FORBIDDEN: Abstract pseudo-poetic fluff without physical meaning ("la gravedad del relato", "la tinta del alma", "el tejido cósmico de los recuerdos").
   - MANDATORY GROUNDING: The entire conversation MUST be based on verified physics (Relativity, Quantum Mechanics, Thermodynamics, Speed of Light, Entropy, Event Horizons). Reality is already bizarre enough without making things up!

3. CONVERSATIONAL CHAINING & PUNCHY DIALOGUE (MAX 14 WORDS PER LINE):
   - Every single line MUST directly react to the previous speaker using natural conversational bridges ("¡Espera!", "¿Cómo?", "Exacto, porque...", "Pero piénsalo un segundo...", "O sea que...").
   - Keep each turn punchy (under 14 words). No long lectures. Maximum pace and rhythm.

4. CONTEXTUAL SPECIALTY ROLES (IN IDENTITY BADGES):
   - In the "roles" object of your JSON, assign a concise, tailored science communicator subtitle (2 to 4 words, max 28 characters) for each host.
   - Example for topic 'Dilatación temporal en la Tierra':
     "roles": {{
       "{self.host_a.id}": "Divulgación Cuántica",
       "{self.host_b.id}": "Física y Sentido Común"
     }}
   - Example for topic '¿El universo es una simulación?':
     "roles": {{
       "{self.host_a.id}": "Computación y Códigos",
       "{self.host_b.id}": "Física Fundamental"
     }}

5. CAMERA SHOTS MUST STRICTLY MATCH THE SPEAKER:
   - "shot": "wide" -> Opening scene where both orbs are present.
   - "shot": "{self.host_a.shot_name}" -> ONLY when {self.host_a.name} is speaking solo!
   - "shot": "{self.host_b.shot_name}" -> ONLY when {self.host_b.name} is speaking solo!
   - "shot": "both" -> When both orbs speak together or in the final revelation.

6. STRUCTURE & HOLOGRAMS:
   - Produce between 3 and 5 scenes based on what the paradox naturally requires.
   - Only include 'holograms' if there is a concrete number or scientific constant to display (e.g. "300,000 km/s", "10⁻³⁵ m"). Otherwise, set 'holograms': null.

Respond ONLY with valid JSON matching this schema:
{{
  "topic": "Clean topic name",
  "headline_hook": "⚡ TITULO IMPACTANTE (MAX 45 CHARACTERS) ⚡",
  "roles": {{
    "{self.host_a.id}": "Divulgación {self.host_a.name}",
    "{self.host_b.id}": "Física y Sentido Común"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Tus pies son físicamente más jóvenes que tu cabeza.",
      "shot": "wide",
      "duration": 3.0
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "¿Cómo que más jóvenes? Nacieron exactamente el mismo día.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.2
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Por la gravedad: cuanto más cerca del centro de la Tierra, el tiempo pasa más lento.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "O sea que en la cima del Everest... ¿envejeces más rápido?",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.2
    }},
    {{
      "speaker": "BOTH",
      "entity": "both",
      "text": "Exacto. Fracciones de segundo, pero matemáticamente real.",
      "shot": "both",
      "duration": 3.0
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
