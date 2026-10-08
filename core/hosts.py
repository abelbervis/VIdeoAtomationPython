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

0. FIDELIDAD TEMÁTICA TOTAL, DESAMBIGUACIÓN Y CERO GUIONES COMODÍN (REGLA FUNDAMENTAL):
   - PROHIBIDO RECICLAR O COPIAR CONCEPTOS DE OTROS TEMAS O DE LOS EJEMPLOS DEL PROMPT:
     * ❌ PROHIBIDO TERMINANTEMENTE clonar o reusar frases cliché de los ejemplos (ej. NUNCA uses "sombras de neuronas", "diez mil millones de impulsos", "fuego interno", "esculpir sentido en la materia", "cerebro encerrado en el cráneo" a menos que el tema sea EXCLUSIVAMENTE sobre neurobiología cerebral).
     * El 100% de los hechos científicos, datos de escala, mecanismos y argumentos DEBEN pertenecer EXCLUSIVAMENTE al dominio específico del tema solicitado ({topic or "el tema indicado"}).
   - DESAMBIGUACIÓN INTELIGENTE Y ANCLAJE AL MUNDO REAL:
     * Si el tema es una ciudad, región geográfica o fenómeno planetario (ej. "Los Ángeles", "Tokio", "La Falla de San Andrés", "El Amazonas", "El Sáhara"), trátalo como tal: enfócate en su geología, tectónica de placas, megaciudades humanas, consumo energético, microclima o vulnerabilidad cósmica. NUNCA desvíes un lugar geográfico hacia misticismo, ángeles o neurología.
     * Si el tema es astronómico (galaxias, estrellas, agujeros negros), debate desde la astrofísica y relatividad.
     * Si el tema es biológico (especies, ADN, evolución), debate desde la genética y adaptación.
     * Si el tema es tecnológico/físico, debate desde sus mecanismos reales.

1. ELECCIÓN DINÁMICA DE ROLES POR VIDEO (DESIGNACIÓN CÓSMICA Y CONTRASTE):
   - NO USAR TÍTULOS ACADÉMICOS O PROFESIONES HUMANAS (❌ NO uses "Profesor de Geología", "Filósofo" o "Ingeniero").
   - Define las especialidades como DESIGNACIONES DE ENTIDADES CÓSMICAS adaptadas al tema específico (ej. para sismología urbana: "Entidad de la Tectónica y el Caos Lítico" vs "Entidad de la Civilización e Infraestructura"; para astrofísica: "Entidad del Horizonte Gravitatorio" vs "Entidad de la Radiación Cósmica").
   - MÁXIMO CONTRASTE CONCEPTUAL entre las dos entidades.
   - Debes incluir obligatoriamente los roles elegidos en el objeto "roles" del JSON inicial:
     "roles": {{
       "{self.host_a.id}": "Designación de entidad 1 adaptada al tema (2-4 palabras)",
       "{self.host_b.id}": "Designación de entidad 2 en contraste (2-4 palabras)"
     }}

2. LENGUAJE VISCERAL Y CERO JERGA ACADÉMICA / TÉCNICA CRÍPTICA:
   - PROHIBIDA LA JERGA ACADÉMICA O TÉCNICA PESADA (❌ NUNCA uses "decoherencia", "patrón de bits", "transición estadística", "epistemológico", "glicólisis", "reducción a sinapsis", "quimera de la simultaneidad").
   - Traduce toda la ciencia a IMÁGENES VISCERALES Y DIRECTAS:
     * En vez de "disipación térmica irreversible" ➔ "calor que devora la estructura hasta convertirla en cenizas".
     * En vez de "estrés cortical de falla transformante" ➔ "dos placas de roca pura triturándose a milímetros por año".
     * En vez de "la simultaneidad es una quimera" ➔ "el universo no comparte tu presente".
   - El espectador debe entender cada palabra sin ser especialista.

3. DIRECTRICES DE ALTO IMPACTO Y CLARIDAD TOTAL ("LA PRUEBA DEL ESPECTADOR CANSADO"):
   - LENGUAJE DIRECTO Y CRISTALINO (CERO POESÍA BARATA, CERO LIRISMO HUECO):
     * ❌ TERMINANTEMENTE PROHIBIDAS las metáforas abstractas o infladas (ej. "clavan su pulso en el vacío", "el instante vibra", "la tinta del destino", "el abismo cósmico que ruge").
     * Si una persona común después de un día de trabajo no entiende una frase al instante, ES UN ERROR.
     * CADA FRASE DEBE APOYARSE EN UN HECHO REAL, ESCALA O MECANISMO TANGIBLE del tema tratado.
   - PERSPECTIVA DE ENTIDADES CÓSMICAS REALES (AUTORIDAD OBSERVACIONAL):
     * PROHIBIDO CITAR HUMANOS O INSTITUCIONES (❌ NUNCA digas "Einstein demostró", "como dice Newton", "en mi laboratorio").
     * Hablan como inteligencias cósmicas superiores que observan el planeta y sus sistemas desde afuera.
   - CONFLICTO DIALÉCTICO REAL (ATAQUE DIRECTO Y RESPUESTA PING-PONG):
     * Prohibidos los monólogos paralelos o frases épicas al aire. Cada orbe DEBE responder directamente a la objeción del anterior:
       - {self.host_a.name} (QUANTUM): Deconstruye con frialdad implacable y leyes implacables.
       - {self.host_b.name} (SOLAR): Refuta de frente demostrando la fuerza creadora, la adaptación o la resistencia del sistema.
   - REGLA DEL HOOK (PRIMEROS 3 SEGUNDOS):
     * La Escena 1 del Narrador DEBE ser una AFIRMACIÓN CATEGÓRICA E INQUIETANTE que rompa una certeza cotidiana del espectador sobre el tema concreto (ej. para Los Ángeles: "Cuatro millones de personas duermen sobre una bomba geológica que avanza cinco centímetros cada año.").
     * Cero preguntas tibias o introducciones genéricas.

4. RIGOR FACTUAL Y CERO MITOS POPULARES:
   - CIENCIA Y HECHOS 100% REALES: Todos los mecanismos deben basarse en leyes naturales comprobadas, sin inventar estudios ficticios ni atribuir porcentajes inventados.

5. POLARIZACIÓN Y CHOQUE FRONTAL:
   - ESTRICTAMENTE PROHIBIDO EL CONSENSO O COMPLICIDAD:
     * {self.host_b.name} (SOLAR) NUNCA debe limitarse a buscarle el lado bonito a lo que dice {self.host_a.name} (QUANTUM). Debe contratacar con fuerza conceptual y hechos concretos.
   - LAS ENTIDADES NO GRITAN NI PIERDEN LA COMPOSTURA: Afirman con convicción serena, tajante y demoledora (ej. "Te equivocas.", "Ignoras el impacto estructural.", "Una frágil ilusión."). Cero interjecciones melodramáticas.
   - Diálogos fluidos, elegantes, cortantes y de alto impacto (~10 a 16 palabras por escena).

6. COHERENCIA SENSORIAL Y METAFÓRICA (CERO CONTAMINACIÓN DE DOMINIOS):
   - Las metáforas DEBEN emanar estrictamente del dominio del tema:
     * En GEOFÍSICA / TERREMOTOS / CIUDADES: fricción, placas, magma, asfalto, acero, vibración telúrica, fallas.
     * En ASTRONOMÍA / ESPACIO: gravedad, radiación, vacío, órbitas, colapso estelar.
     * En ÓPTICA / VISIÓN: sombras, reflejos, prismas, fotones, espectro electromagnético.
     * En BIOLOGÍA / EVOLUCIÓN: mutación, ADN, adaptación celular, depredación, simbiosis.
   - PROHIBIDA LA REPETICIÓN: Cada escena debe aportar una imagen fresca sin repetir palabras clave.

7. PERSPECTIVA DE OBSERVADORES EXTERNOS:
   - Hablan de la especie humana y sus construcciones siempre en tercera persona ("los humanos", "sus megaciudades", "sus organismos").

8. ESTRUCTURA NARRATIVA DE TRES CAPAS (HOOK AFIRMATIVO + CHOQUE REAL + CIERRE CIRCULAR):
   - Headline Hook (headline_hook): Dilema punzante en mayúsculas sin emojis (MAX 40 CARACTERES).
   - Escena 1 (Intro Narrador): Hook afirmativo demoledor sobre el tema.
   - Escenas 2 a N-1 (Choque Dialéctico): Tesis vs Antítesis con rigor y dinamismo.
   - Escena N (Outro Narrador): Cierre circular que profundiza la paradoja (SIN pedir likes ni comentarios).

EJEMPLOS DIVERSOS DE GUIONES DE ALTO IMPACTO (NOTA LA ESPECIFICIDAD TOTAL DE CADA DOMINIO):

EJEMPLO 1 - DOMINIO GEOFÍSICA / MEGACIUDADES Y TECTÓNICA:
```json
{{
  "topic": "La Falla de San Andrés y Los Ángeles",
  "headline_hook": "¿LOS ÁNGELES ESTÁ CONDENADA?",
  "roles": {{
    "{self.host_a.id}": "Entidad de la Tectónica Planetaria",
    "{self.host_b.id}": "Entidad de la Resistencia Estructural"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Cuatro millones de personas viven sobre una fractura geológica que acumula energía desde hace trescientos años.",
      "shot": "wide",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "La placa del Pacífico avanza inexorablemente hacia el norte; la fricción acumulada destrozará su infraestructura en segundos.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Te equivocas. Han diseñado rascacielos con disipadores sísmicos capaces de absorber oscilaciones masivas sin colapsar.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Ningún amortiguador de acero detendrá la licuefacción del suelo cuando la corteza libere un gigajulios de potencia sísmica.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Su tecnología de alerta temprana corta líneas de gas y frena trenes antes de que la primera onda llegue.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Cuando la Tierra reclame su territorio... ¿podrá el ingenio humano sostener una ciudad sobre el abismo?",
      "shot": "both",
      "duration": 3.5
    }}
  ]
}}
```

EJEMPLO 2 - DOMINIO ASTROFÍSICA / AGUJEROS NEGROS:
```json
{{
  "topic": "El Horizonte de Sucesos",
  "headline_hook": "¿QUÉ HAY DENTRO DE UN AGUJERO NEGRO?",
  "roles": {{
    "{self.host_a.id}": "Entidad de la Singularidad Gravitatoria",
    "{self.host_b.id}": "Entidad de la Información Cuántica"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Si cruzaras el horizonte de sucesos, para el resto del universo quedarías congelado para toda la eternidad.",
      "shot": "wide",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "La curvatura extrema del espacio tiempo devora la materia y borra cualquier rastro de la física conocida.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "La materia se destruye, pero la información cuántica se codifica en la superficie sin perderse jamás.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "En el centro absoluto, las ecuaciones colapsan a densidad infinita donde las leyes del cosmos dejan de operar.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Ese colapso solo revela que la gravedad y la mecánica cuántica deben unirse en una nueva ley fundamental.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Si la gravedad puede atrapar hasta la luz... ¿es el agujero negro el fin del espacio o la puerta a otra física?",
      "shot": "both",
      "duration": 3.5
    }}
  ]
}}
```

EJEMPLO 3 - DOMINIO BIOLOGÍA EXTREMA / TARDÍGRADOS Y CRIPTOBIOSIS:
```json
{{
  "topic": "La Criptobiosis del Tardígrado",
  "headline_hook": "¿EL ANIMAL QUE NO PUEDE MORIR?",
  "roles": {{
    "{self.host_a.id}": "Entidad del Cero Absoluto",
    "{self.host_b.id}": "Entidad de la Resiliencia Celular"
  }},
  "holograms": null,
  "scenes": [
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Existe un organismo microscópico capaz de sobrevivir al vacío espacial, radiación letal y temperaturas extremas.",
      "shot": "wide",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Expulsa el noventa y cinco por ciento de su agua y detiene su metabolismo; técnicamente no está vivo.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Protege su ADN sustituyendo el agua por proteínas vítreas que blindan cada célula contra el daño.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "{self.host_a.name}",
      "entity": "{self.host_a.id}",
      "text": "Esa animación suspendida no es invencibilidad, solo una pausa pasiva incapaz de reproducirse en el vacío.",
      "shot": "{self.host_a.shot_name}",
      "duration": 3.4
    }},
    {{
      "speaker": "{self.host_b.name}",
      "entity": "{self.host_b.id}",
      "text": "Al tocar una sola gota de agua, reactiva su biología en minutos desafiando los límites de la vida.",
      "shot": "{self.host_b.shot_name}",
      "duration": 3.5
    }},
    {{
      "speaker": "Narrador",
      "entity": "narrator",
      "text": "Si una criatura puede detener su propia vida por décadas... ¿dónde termina la supervivencia y empieza la inmortalidad?",
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
