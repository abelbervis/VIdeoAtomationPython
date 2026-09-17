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
    role="IA Física Cuántica",
    perspective="Mente analítica, sutil y rigurosa. Enfoque deductivo, examen de variables críticas y análisis de principios fundamentales.",
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
    perspective="Mente dinámica, enérgica y empírica. Enfoque sistémico, contrastación con hechos tangibles e implicaciones dinámicas.",
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
- {self.host_a.name} (Entity ID: {self.host_a.id}): {self.host_a.perspective}
- {self.host_b.name} (Entity ID: {self.host_b.id}): {self.host_b.perspective}

CRITICAL NARRATIVE RULES:

1. DYNAMIC ARCHETYPES & MAXIMUM CONTRAST (MANDATORY RULE #1):
   - DEBES inventar dos arquetipos de expertos radicalmente opuestos (de 2 a 4 palabras cada uno) basados específicamente en el tema '{topic or 'de esta sesión'}'.
   - MÁXIMO CONTRASTE OBLIGATORIO: Los dos orbes NUNCA pueden pertenecer al mismo campo ni compartir la misma cosmovisión. Deben representar métodos o posturas en choque frontal (ej. Científico vs. Teólogo, Neurocientífico vs. Filósofo Existencial, Genetista vs. Eticista, Ingeniero vs. Humanista).
   - PROHIBIDO usar roles genéricos o repetidos. Inclúyelos obligatoriamente en el objeto "roles" al inicio del JSON.

2. NO PSEUDO-POETRY OR VAGUE FLUFF & STRICT SCIENTIFIC ACCURACY:
   - CIENCIA RIGUROSA: Todos los datos, mecanismos y principios expuestos deben ser científicamente verídicos, contrastados y pertinentes al tema específico tratado. No inventes datos ni recurras a pseudociencia.
   - PROHIBIDO: Frases pseudo-poéticas vacías sin significado real (ej. "la gravedad del relato", "la tinta de la conciencia", "las hojas del libro cósmico", "el tejido de las almas").
   - MANDATORY GROUNDING: Cada guion DEBE basarse estrictamente en la ciencia real, mecanismos empíricos verificados o dilemas académicos del tema solicitado.
     * REGLA ESTRICTA CONTRA CONTAMINACIÓN TEMÁTICA: Adapta los argumentos EXCLUSIVAMENTE a la disciplina del tema tratado. NUNCA introduzcas conceptos de física subatómica, mecánica cuántica o astrofísica en temas no relacionados (como genética, ADN, biología, medicina, neurociencia, ecología o tecnología).

3. ONE SINGLE STORY ARC & CONVERSATIONAL CHAINING:
   - The script MUST maintain ONE single central thought experiment or real paradox from line 1 to the end. Do NOT jump to unrelated isolated facts.
   - Cada intervención debe responder a la anterior, no ignorarla. Cada escena después de la primera debe contraargumentar, profundizar o responder directamente a lo que dijo el otro orbe, construyendo un debate real de ida y vuelta.
   - The dialog MUST read like a real, fascinating debate between two brilliant minds bouncing off each other.

4. STRUCTURE & DEVELOPED EXCHANGES:
   - Desarrollo natural: Las escenas deben desarrollarse lo suficiente para que ambos orbes expongan argumentos y reaccionen al menos dos veces de forma profunda (sin número mínimo forzado de escenas).
   - FLEXIBLE STARTER: Either {self.host_a.name} or {self.host_b.name} can speak first—whichever speaker creates the strongest immediate hook.
   - OPTIONAL HOLOGRAMS: Only output 'holograms' if there is a real, concrete scientific metric, unit, or measurement relevant to the topic to display. If the script is a pure conceptual thought experiment or debate, set 'holograms': null.

5. STRICT SINGLE CLOSING SCENE & PENULTIMATE SHOT:
   - PROHIBIDO GENERAR DOS ESCENAS DE CIERRE CONSECUTIVAS O DOBLE 'Ambos': Solo puede haber UNA escena final conjunta ("Ambos" / "both") en todo el guion.
   - Si tienes una síntesis y una pregunta final, ÚNELAS en una sola escena final de 'Ambos'. No las dividas en dos escenas.
   - LA PENÚLTIMA ESCENA NO DEBE SER EN PLANO AMPLIO NI DE 'Ambos': La penúltima escena (Escena N-1) DEBE ser de un orbe individual ({self.host_a.name} o {self.host_b.name}) con plano cerrado ("{self.host_a.shot_name}" o "{self.host_b.shot_name}"), llevando la tensión al clímax.
   - La última escena (Escena N) es el único cierre de 'Ambos' con "shot": "both" que lanza la pregunta provocadora.

6. CAMERA SHOTS & DRAMATIC INTENT:
   - El shot debe ser coherente con el speaker y la intención dramática.
   - Puede ser plano cerrado (close) del que habla, plano amplio (wide) o dual (both).
   - Prioriza el impacto visual sobre la correspondencia literal rígida.

7. DIALOGUE STYLE & ELI5:
   - Speak in clear, simple Spanish. Explain like to a 12-year-old using clear physical analogies.
   - EL GANCHO (Escena 1): Debe ser una paradoja, dilema ético o pregunta incómoda en segunda persona (ej. "¿Y si supieras que...?", "¿Por qué aceptas que...?"). PROHIBIDO empezar con "Imagina..." o definiciones neutrales.
   - End with a mind-expanding scientific realization or existential question (NO forced "comment below" CTAs).

Respond ONLY with valid JSON matching this schema:
{{
  "topic": "Clean topic name",
  "headline_hook": "⚡ TITULO IMPACTANTE (MAX 45 CHARACTERS) ⚡",
  "roles": {{
    "{self.host_a.id}": "Especialidad 2-4 palabras (máximo contraste 1)",
    "{self.host_b.id}": "Especialidad 2-4 palabras (máximo contraste 2)"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Planteamiento inicial del dilema o premisa provocadora sobre el tema.",
      "shot": "wide",
      "duration": 3.2
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Refutación o perspectiva alternativa basada en evidencia del tema.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Profundización analítica presentando un mecanismo o dato concreto.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.3
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Contraargumento que cuestiona la conclusión y eleva el debate.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Planteamiento de la evidencia o consecuencia más sorprendente.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Penúltima intervención en primer plano sintetizando la tensión central.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "Ambos",
      "entity": "both",
      "text": "Pregunta final abierta y reflexiva dirigida a la audiencia.",
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
