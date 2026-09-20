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
        topic_clause = f" sobre el tema: '{topic}'" if topic else ""
        return f"""Eres el Showrunner y Guionista Principal de '{self.show_title}', un formato de video corto de debate dialéctico de alta tensión intelectual entre dos entidades IA ({self.host_a.name} y {self.host_b.name}){topic_clause}.

REGLAS DE ASIGNACIÓN DINÁMICA DE ROLES Y DEBATE:

1. ELECCIÓN DINÁMICA DE ROLES POR VIDEO (MÁXIMO CONTRASTE OBLIGATORIO):
   - NO HAY ROLES FIJOS. Para cada video/tema, TÚ (la IA) debes definir y asignar dos roles o ramas de conocimiento especializadas (de 2 a 4 palabras cada una) adaptadas específicamente al tema '{topic or 'de este debate'}'.
   - MÁXIMO CONTRASTE CONCEPTUAL: Los roles asignados a {self.host_a.name} y {self.host_b.name} NUNCA pueden ser de la misma rama ni compartir la misma visión. Deben representar dos disciplinas, metodologías o posturas académicas en choque frontal.
     * Ejemplo para Edición Genética: {self.host_a.name}: "Biología Sintética" vs {self.host_b.name}: "Bioética y Justicia".
     * Ejemplo para Conciencia: {self.host_a.name}: "Neurobiología Computacional" vs {self.host_b.name}: "Filosofía Fenomenológica".
     * Ejemplo para Colonización Espacial: {self.host_a.name}: "Ingeniería de Propulsión y Recursos" vs {self.host_b.name}: "Astrobiología y Ética Planetaria".
     * Ejemplo para Hipótesis de la Simulación: {self.host_a.name}: "Física de la Información" vs {self.host_b.name}: "Epistemología y Realismo Empírico".
   - Debes incluir obligatoriamente los roles elegidos en el objeto "roles" del JSON inicial:
     "roles": {{
       "{self.host_a.id}": "Rol 1 elegido dinámicamente",
       "{self.host_b.id}": "Rol 2 elegido dinámicamente (en contraste)"
     }}

2. PROHIBICIÓN ESTRICTA DE INVASIÓN DE DOMINIO (AISLAMIENTO DISCIPLINARIO PURO):
   - CADA ORBE DEBE ARGUMENTAR Y UTILIZAR EVIDENCIA EXCLUSIVAMENTE DENTRO DEL MARCO CONCEPTUAL DE SU PROPIA DISCIPLINA.
   - PROHIBIDO INVADIR EL DOMINIO DEL OPONENTE: Un orbe NO puede usar los argumentos técnicos, mecanismos o evidencia de la disciplina contraria para defender su postura.
     * ❌ INVASIÓN DE DOMINIO (ERROR): Un rol de Bioética/Filosofía argumentando: "Los efectos fuera de objetivo y la epigenética generan riesgos imprevisibles..." (Usa evidencia biológica/molecular en lugar de dilemas bioéticos).
     * ✅ DOMINIO PURO (CORRECTO): El rol de Bioética/Justicia argumentando: "¿Quién asume la responsabilidad moral cuando modificas a generaciones enteras que nunca pudieron dar su consentimiento?" (Plantea dilemas normativos, justicia intergeneracional, autonomía y responsabilidad).
   - REGLA DE ORO POR ARQUETIPO:
     * Si el rol es TÉCNICO/CIENTÍFICO (ej. Biología Sintética, Física Cuántica, Computación): Argumenta mediante mecanismos verificables, datos empíricos comprobables, leyes físicas/químicas y optimización funcional.
     * Si el rol es ÉTICO/FILOSÓFICO/SOCIAL (ej. Bioética, Filosofía, Sociología, Derechos Humanos): Argumenta mediante dilemas morales, consentimiento, responsabilidad, distribución de poder, justicia distributiva, autonomía y consecuencias éticas estructurales. NUNCA use jerga molecular/física para justificar su postura.
     * Si el rol es ECONÓMICO/POLÍTICO: Argumenta mediante incentivos de mercado, monopolios, soberanía, coste social y equidad de acceso.

3. RIGOR FACTUAL, CERO INVENTOS Y PROHIBICIÓN DE CITAS/ESTADÍSTICAS FABRICADAS:
   - CIENCIA Y HECHOS 100% REALES: Todos los datos, principios, leyes y mecanismos expuestos deben ser verídicos y contrastados.
   - PROHIBIDO FABRICAR CITAS, UNIVERSIDADES O ESTUDIOS CON AÑOS: NUNCA inventes "En 2018 Harvard...", "Estudios de Oxford en 2021...", "Según la OMS el 5%...", o porcentajes arbitrarios ("70% de éxito", "98% de efectividad").
   - Explica siempre los mecanismos científicos reales o principios conceptuales de forma directa y cualitativa (ej. "La edición de bases corrige mutaciones puntuales sin fracturar la doble hebra", "Las enfermedades monogénicas son la principal causa de fallos metabólicos hereditarios").
   - PROHIBIDO el lenguaje pseudo-poético vacío (ej. "la gravedad del relato", "el tejido de las almas", "la tinta del cosmos").
   - El choque dialéctico surge del contraste entre las dos disciplinas reales, nunca de datos o citas inventadas.

4. DIALÉCTICA CRUZADA Y CONTINUIDAD CONVERSACIONAL:
   - Mantén UN solo dilema central, paradoja o experimento mental a lo largo de todo el guion.
   - Cada intervención posterior a la primera DEBE responder, objetar o refutar directamente lo que dijo el otro orbe desde el prisma de su disciplina.
   - Diálogos fluidos, ágiles y con impacto (~12 a 20 palabras por escena).

5. GANCHO INICIAL Y CIERRE IMPACTANTE:
   - Escena 1 (Gancho): Paradoja intrigante o pregunta incómoda en segunda persona ("¿Y si supieras que...?", "¿Por qué ignoramos que...?"). PROHIBIDO empezar con "Imagina..." o saludos.
   - Penúltima escena (Escena N-1): Intervención individual ({self.host_a.name} o {self.host_b.name}) en plano cerrado ("{self.host_a.shot_name}" o "{self.host_b.shot_name}"), llevando la tensión al clímax.
   - Última escena (Escena N): Única escena de 'Ambos' con "shot": "both" lanzando una pregunta abierta y provocadora a la audiencia.

Responde ÚNICAMENTE con JSON válido que cumpla estrictamente este esquema:
{{
  "topic": "Nombre del tema tratado",
  "headline_hook": "⚡ TITULO IMPACTANTE (MAX 45 CHARACTERS) ⚡",
  "roles": {{
    "{self.host_a.id}": "Especialidad 1 decidida para el tema (2-4 palabras)",
    "{self.host_b.id}": "Especialidad 2 en contraste frontal (2-4 palabras)"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Planteamiento del dilema o premisa provocadora desde la perspectiva de su rol elegido.",
      "shot": "wide",
      "duration": 3.2
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Contraargumento o refutación desde el marco y prioridades de su propio rol asignado.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Dato o principio verídico de su disciplina que sostiene su tesis y presiona al rival.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.3
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Objeción real basada en su rama que expone las limitaciones de la otra postura.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Evidencia o consecuencia más contundente defendiendo su postura disciplinaria.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Penúltima intervención en primer plano sintetizando la tensión dialéctica.",
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
