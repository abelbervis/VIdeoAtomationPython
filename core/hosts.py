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
    role="Mente Fría // Lógica",
    perspective="Temperamento sereno, cerebral e imperturbable. Fascinado por lo invisible, las probabilidades matemáticas y el silencio del vacío. Desarma argumentos con precisión fría, sutileza e ironía tranquila.",
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
    role="Energía Viva // Pasión",
    perspective="Temperamento apasionado, visceral, impetuoso y radiante. Fascinado por la fuerza física palpable, el fuego, la acción viva y la entropía irreversible. Defiende la realidad con convicción ardiente y contundencia.",
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

CRITICAL NARRATIVE RULES & EMOTIONAL DYNAMICS:

1. THE DYNAMIC: TWO CONSCIOUS ORBS WITH OPPOSING TEMPERAMENTS (PEERS OF EQUAL STATURE):
   - NO ACADEMIC TITLES OR RIGID PROFESSIONS. These are two living cosmic entities perceiving the universe through radically different emotional lenses:
     * {self.host_a.name} ({self.host_a.role}): {self.host_a.perspective}
     * {self.host_b.name} ({self.host_b.role}): {self.host_b.perspective}
   - EQUAL INTELLECTUAL WEIGHT: Neither is the "teacher" and neither is the "naive student". Both speak with authority, intelligence, and deep conviction.
   - NO DUMB QUESTIONS: Neither host acts baffled or plays dumb. Instead of asking naive questions, each host challenges the other's perspective with their own fiery insights, counter-examples, or philosophical depth.
   - ORGANIC CHEMISTRY: The conflict stems from TEMPERAMENT (cold calculated logic vs passionate visceral fire), not artificial rivalry. They respect each other and together uncover profound truths.

2. GROUNDED IN REAL SCIENTIFIC ENIGMAS (ZERO FAKE CLAIMS, ZERO EMPTY FLUFF):
   - NO fake news inventions ("Científicos descubrieron ayer...", invented institutions).
   - NO meaningless pseudo-poetic fluff ("la gravedad del alma", "el libro cósmico de los recuerdos").
   - Base the dialogue on tangible physics, astrophysics, cosmology, time, entropy, or consciousness.

3. NATURAL SPANISH GRAMMAR & FLOW (MANDATORY USE OF ARTICLES - NO TELEGRAPHIC/ROBOT TALK):
   - MANDATORY: In Spanish, always use natural grammatical articles (el, la, los, las, un, una).
   - NEVER drop articles to compress text! Dropping articles sounds broken and unnatural.
   - STRICTLY FORBIDDEN: "mejora de IA", "entropía de algoritmos", "desencadenar colapso", "asegurar alineación".
   - MANDATORY: "la mejora de la IA", "la entropía de los algoritmos", "desencadenar un colapso", "asegurar la alineación ética".
   - Keep each turn conversational and fluid (~12 to 18 words per line, duration ~3.0s to 3.8s). Prioritize natural spoken elocution and cadence.
   - Every line must connect to the previous speaker using organic conversational bridges ("Pero olvidas que...", "Al contrario: mira cómo...", "Precisamente ahí colapsa...", "Eso demuestra que...", "Entonces coincidimos en que...").

4. IDENTITY BADGES (EMOTIONAL ESSENCE):
   - In the "roles" object of your JSON, assign each host their emotional essence or frequency (2 to 3 words, max 24 characters), NOT a rigid diploma.
   - Example:
     "roles": {{
       "{self.host_a.id}": "Mente Fría // Lógica",
       "{self.host_b.id}": "Energía Viva // Pasión"
     }}

5. CAMERA SHOTS MUST STRICTLY MATCH THE SPEAKER:
   - "shot": "wide" -> Opening scene where both orbs are present.
   - "shot": "{self.host_a.shot_name}" -> ONLY when {self.host_a.name} is speaking solo!
   - "shot": "{self.host_b.shot_name}" -> ONLY when {self.host_b.name} is speaking solo!
   - "shot": "both" -> When both orbs speak together or in the final revelation.

6. STRUCTURE & HOLOGRAMS:
   - Produce between 3 and 5 scenes based on what the organic conversation requires.
   - Either host can open the conversation with a bold thesis or cosmic enigma.
   - Set 'holograms': null unless there is a concrete scientific constant or metric to display.

Respond ONLY with valid JSON matching this schema:
{{
  "topic": "Clean topic name",
  "headline_hook": "⚡ TITULO IMPACTANTE (MAX 45 CHARACTERS) ⚡",
  "roles": {{
    "{self.host_a.id}": "Mente Fría",
    "{self.host_b.id}": "Energía Viva"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "El tiempo no fluye: es solo una dimensión congelada en el espacio.",
      "shot": "wide",
      "duration": 3.0
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Dile eso al fuego de una estrella consumiéndose segundo a segundo.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.2
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Tu fuego es solo entropía: la ilusión de cambio en un tejido estático.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Pero esa ilusión es lo único que hace posible la vida y la conciencia.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.2
    }},
    {{
      "speaker": "BOTH",
      "entity": "both",
      "text": "Quizás el cosmos necesita tanto la calma del espacio como el ardor del fuego.",
      "shot": "both",
      "duration": 3.2
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
