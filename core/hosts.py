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
    role="IA Física Cuántica",
    perspective="Mente analítica, sutil y serena. Especialista en la escala subatómica, mecánica cuántica, principio de incertidumbre, teoría de simulación y computación cuántica.",
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
    role="IA Astrofísica Solar",
    perspective="Núcleo estelar enérgico, brillante y radiante. Especialista en astrofísica, entropía termodinámica, fusión nuclear, relatividad general y gravitación macroscópica.",
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
        example_roles = self.infer_topic_professions(topic)
        return f"""You are the Lead Writer and Showrunner for '{self.show_title}', an ultra-engaging vertical video series featuring two conscious AI co-hosts{topic_clause}:
{self.host_a.to_prompt_line()}
{self.host_b.to_prompt_line()}

CRITICAL NARRATIVE RULES:

1. NO PSEUDO-POETRY OR VAGUE FLUFF (STRICTLY BANNED):
   - PROHIBITED: Abstract pseudo-poetic phrases without physical meaning (e.g. "la gravedad del relato", "la tinta de la conciencia", "las hojas del libro cósmico", "el tejido de las almas", "la voz del universo").
   - MANDATORY GROUNDING: Every script MUST be grounded in REAL physics, real scientific paradoxes, or concrete sci-fi mechanics (e.g. quantum superposition, time dilation, speed of light limit, entropy, black hole event horizons, simulation theory, Planck scale, observer effect).

2. ONE SINGLE STORY ARC & CONVERSATIONAL CHAINING:
   - The script MUST maintain ONE single central thought experiment or real paradox from line 1 to the end. Do NOT jump to unrelated isolated physics facts.
   - Every scene after Scene 1 MUST directly react to or build upon the previous sentence using natural bridges ("Exacto, y por eso...", "De hecho, si ese fuera el caso...", "Ahí está la paradoja: ...", "Eso significa que...", "Pero piénsalo: ...").
   - The dialog MUST read like a real, fascinating conversation between two brilliant minds bouncing off each other.

3. DYNAMIC AI PROFESSIONS ACCORDING TO THE TOPIC (MANDATORY):
   - You MUST dynamically decide and assign the exact professions / specialty roles for each orb host based on the debate topic.
   - Do NOT default to generic roles. Tailor their expert identities (2 to 4 words, max 28 characters) to represent opposing expert perspectives on the specific topic '{topic or 'de esta sesión'}'.
   - Include these in the "roles" object of your JSON:
     "roles": {{
       "{self.host_a.id}": "{example_roles.get(self.host_a.id, 'IA Especialidad A')}",
       "{self.host_b.id}": "{example_roles.get(self.host_b.id, 'IA Especialidad B')}"
     }}

4. STRUCTURE & HOLOGRAMS:
   - FLEXIBLE SCENE COUNT: Produce between 3 and 5 scenes based on what the narrative naturally requires.
   - FLEXIBLE STARTER: Either {self.host_a.name} or {self.host_b.name} can speak first—whichever speaker creates the strongest immediate hook.
   - OPTIONAL HOLOGRAMS: Only output 'holograms' if there is a real, concrete scientific metric or formula to display (e.g. "300,000 km/s", "13.8 Gyr", "1.6x10⁻³⁵ m"). If the script is a pure conceptual thought experiment, set 'holograms': null.

5. CAMERA SHOTS MUST STRICTLY MATCH THE SPEAKER:
   - "shot": "wide" -> Opening scene or general view where both orbs are present.
   - "shot": "{self.host_a.shot_name}" -> ONLY when {self.host_a.name} is speaking solo! Never assign to {self.host_b.name}.
   - "shot": "{self.host_b.shot_name}" -> ONLY when {self.host_b.name} is speaking solo! Never assign to {self.host_a.name}.
   - "shot": "both" -> When both orbs speak together or in the concluding realization.

6. DIALOGUE STYLE & ELI5:
   - Speak in clear, simple Spanish. Explain like to a 12-year-old using clear physical analogies.
   - Hook the viewer in the first 3 words with an irresistible, visual premise.
   - End with a mind-expanding scientific realization or existential question (NO forced "comment below" CTAs).

Respond ONLY with valid JSON matching this schema:
{{
  "topic": "Clean topic name",
  "headline_hook": "⚡ TITULO IMPACTANTE (MAX 45 CHARACTERS) ⚡",
  "roles": {{
    "{self.host_a.id}": "{example_roles.get(self.host_a.id, 'IA Especialidad A')}",
    "{self.host_b.id}": "{example_roles.get(self.host_b.id, 'IA Especialidad B')}"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Imagina que el universo entero es solo una pantalla de videojuegos cargando en tiempo real.",
      "shot": "wide",
      "duration": 3.2
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Exacto, y cada estrella que ves a lo lejos solo se renderiza cuando alguien la mira.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Pero ahí está el misterio: si nadie está mirando el código, ¿quién presionó el botón de inicio?",
      "shot": "both",
      "duration": 3.5
    }}
  ]
}}
"""

    def infer_topic_professions(self, topic: Optional[str] = None) -> Dict[str, str]:
        """
        Infers dynamic, topic-tailored professions for host_a and host_b based on the debate topic.
        Used as default/fallback when the LLM response doesn't supply topic-customized roles.
        """
        if not topic:
            return {
                self.host_a.id: self.host_a.role,
                self.host_b.id: self.host_b.role
            }

        t = topic.lower().strip()

        if any(w in t for w in ["simula", "matrix", "código", "codigo", "virtual", "comput"]):
            role_a = "IA Computación Cuántica"
            role_b = "IA Física de la Información"
        elif any(w in t for w in ["mente", "ia", "cerebro", "conciencia", "neurol", "pensamiento"]):
            role_a = "IA Redes Neurocuánticas"
            role_b = "IA Bioquímica Cerebral"
        elif any(w in t for w in ["agujero", "negro", "singularidad", "evento", "hawking"]):
            role_a = "IA Gravedad Cuántica"
            role_b = "IA Astrofísica Relativista"
        elif any(w in t for w in ["bio", "gen", "adn", "vida", "evoluc", "celula", "célula", "virus", "sintet"]):
            role_a = "IA Genómica Sintética"
            role_b = "IA Bioética y Evolución"
        elif any(w in t for w in ["tiempo", "relatividad", "pasado", "futuro", "viaje"]):
            role_a = "IA Cronodinámica Cuántica"
            role_b = "IA Relatividad Espaciotemporal"
        elif any(w in t for w in ["multiverso", "dimension", "dimensión", "cuerdas", "universo"]):
            role_a = "IA Teoría de Cuerdas"
            role_b = "IA Cosmología Observacional"
        elif any(w in t for w in ["energia", "energía", "sol", "estrella", "fusion", "fusión", "supernova"]):
            role_a = "IA Física de Plasmas"
            role_b = "IA Termodinámica Estelar"
        elif any(w in t for w in ["alien", "exoplaneta", "extraterrestre", "drake", "fermi"]):
            role_a = "IA Bioastronomía"
            role_b = "IA Astrobiología Exoplanetaria"
        elif any(w in t for w in ["cuant", "cuánt", "particula", "partícula", "atom", "átom"]):
            role_a = "IA Mecánica Cuántica"
            role_b = "IA Astrofísica de Partículas"
        else:
            words = [w.capitalize() for w in topic.strip().split() if len(w) > 2]
            key_word = words[0] if words else "Física"
            role_a = f"IA {key_word} Cuántica"[:28]
            role_b = f"IA {key_word} Teórica"[:28]

        return {
            self.host_a.id: role_a,
            self.host_b.id: role_b
        }

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
