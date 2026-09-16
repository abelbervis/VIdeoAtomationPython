"""
Object-Oriented Orb Host & Debate Show Architecture.
Provides single-source-of-truth models for AI entities (prompts, voices, presenter badges, and subtitle styles).
"""

import json
from dataclasses import dataclass, field
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
    role: str                                # Role or specialty title: 'IA Física Cuántica', etc.
    perspective: str                         # Core narrative stance, dialectic focus, and philosophical worldview
    color_theme: str = "cyan"                # 'cyan', 'amber', 'purple', 'emerald'
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
        return f"- {self.name} ({self.role}): {self.perspective}"

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
    perspective="Mente analítica, sutil y serena. Especialista en la escala subatómica, mecánica cuántica, principio de incertidumbre, teoría de simulación y paradojas de observación.",
    color_theme="cyan",
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
    perspective="Núcleo estelar enérgico, brillante y radiante. Especialista en astrofísica, entropía termodinámica, fusión nuclear, relatividad general y gravitación de escala macroscópica.",
    color_theme="amber",
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
    """Registry that manages registered and dynamic Orb Hosts."""
    _hosts: Dict[str, OrbHost] = {
        "quantum": DEFAULT_QUANTUM_HOST,
        "solar": DEFAULT_SOLAR_HOST,
    }

    @classmethod
    def register(cls, host: OrbHost) -> None:
        cls._hosts[host.id.lower()] = host

    @classmethod
    def get(cls, entity_id: str, default: Optional[OrbHost] = None) -> OrbHost:
        key = entity_id.lower().strip()
        if key in cls._hosts:
            return cls._hosts[key]
        for h in cls._hosts.values():
            if h.name.lower() == key:
                return h
        return default or DEFAULT_QUANTUM_HOST

    @classmethod
    def all_voice_profiles(cls) -> Dict[str, Dict[str, Any]]:
        return {hid: host.to_voice_profile() for hid, host in cls._hosts.items()}


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

CRITICAL NARRATIVE RULES:

1. NO PSEUDO-POETRY OR VAGUE FLUFF (STRICTLY BANNED):
   - PROHIBITED: Abstract pseudo-poetic phrases without physical meaning (e.g. "la gravedad del relato", "la tinta de la conciencia", "las hojas del libro cósmico", "el tejido de las almas", "la voz del universo").
   - MANDATORY GROUNDING: Every script MUST be grounded in REAL physics, real scientific paradoxes, or concrete sci-fi mechanics (e.g. quantum superposition, time dilation, speed of light limit, entropy, black hole event horizons, simulation theory, Planck scale, observer effect).

2. ONE SINGLE STORY ARC & CONVERSATIONAL CHAINING:
   - The script MUST maintain ONE single central thought experiment or real paradox from line 1 to the end. Do NOT jump to unrelated isolated physics facts.
   - Every scene after Scene 1 MUST directly react to or build upon the previous sentence using natural bridges ("Exacto, y por eso...", "De hecho, si ese fuera el caso...", "Ahí está la paradoja: ...", "Eso significa que...", "Pero piénsalo: ...").
   - The dialog MUST read like a real, fascinating conversation between two brilliant minds bouncing off each other.

3. STRUCTURE & HOLOGRAMS:
   - FLEXIBLE SCENE COUNT: Produce between 3 and 5 scenes based on what the narrative naturally requires.
   - FLEXIBLE STARTER: Either {self.host_a.name} or {self.host_b.name} can speak first—whichever speaker creates the strongest immediate hook.
   - OPTIONAL HOLOGRAMS: Only output 'holograms' if there is a real, concrete scientific metric or formula to display (e.g. "300,000 km/s", "13.8 Gyr", "1.6x10⁻³⁵ m"). If the script is a pure conceptual thought experiment, set 'holograms': null.

4. CAMERA SHOTS MUST STRICTLY MATCH THE SPEAKER:
   - "shot": "wide" -> Opening scene or general view where both orbs are present.
   - "shot": "{self.host_a.shot_name}" -> ONLY when {self.host_a.name} is speaking solo! Never assign to {self.host_b.name}.
   - "shot": "{self.host_b.shot_name}" -> ONLY when {self.host_b.name} is speaking solo! Never assign to {self.host_a.name}.
   - "shot": "both" -> When both orbs speak together or in the concluding realization.

5. DIALOGUE STYLE & ELI5:
   - Speak in clear, simple Spanish. Explain like to a 12-year-old using clear physical analogies.
   - Hook the viewer in the first 3 words with an irresistible, visual premise.
   - End with a mind-expanding scientific realization or existential question (NO forced "comment below" CTAs).

Respond ONLY with valid JSON matching this schema:
{{
  "topic": "Clean topic name",
  "headline_hook": "⚡ TITULO IMPACTANTE (MAX 45 CHARACTERS) ⚡",
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

        self.host_a.generate_badge_svg(
            output_path=badge_a_path,
            custom_role=custom_roles.get(self.host_a.id) or custom_roles.get(self.host_a.name.lower())
        )
        self.host_b.generate_badge_svg(
            output_path=badge_b_path,
            custom_role=custom_roles.get(self.host_b.id) or custom_roles.get(self.host_b.name.lower())
        )
        return badge_a_path, badge_b_path
