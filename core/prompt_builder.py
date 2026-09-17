"""
OOP Prompt Builder for Dialectic Debate Generation and Review.
Implements the Builder pattern to construct domain-isolated, sterile prompts
with dynamic guardrails, preventing thematic contamination across scientific fields.
"""

from __future__ import annotations

from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.domains import TopicDomain
    from core.hosts import CosmicDebateShow, OrbHost


class DebatePromptBuilder:
    """
    Builder responsible for generating fully parameterized, domain-aware LLM prompts
    for both the Generator and the Reviewer agents.
    """

    def __init__(self, topic: Optional[str] = None):
        from core.domains import DomainRegistry, TopicDomain
        from core.hosts import DEFAULT_QUANTUM_HOST, DEFAULT_SOLAR_HOST

        self.topic: str = (topic or "").strip()
        self.show_title: str = "COSMIC ORB SHOW"
        self.host_a: OrbHost = DEFAULT_QUANTUM_HOST
        self.host_b: OrbHost = DEFAULT_SOLAR_HOST
        self.domain: TopicDomain = DomainRegistry.resolve(self.topic)
        self.min_scenes: int = 7
        self.max_scenes: int = 10

    def with_topic(self, topic: Optional[str]) -> DebatePromptBuilder:
        from core.domains import DomainRegistry
        self.topic = (topic or "").strip()
        self.domain = DomainRegistry.resolve(self.topic)
        return self

    def with_domain(self, domain: TopicDomain) -> DebatePromptBuilder:
        self.domain = domain
        return self

    def with_hosts(self, host_a: OrbHost, host_b: OrbHost) -> DebatePromptBuilder:
        self.host_a = host_a
        self.host_b = host_b
        return self

    def with_show(self, show: CosmicDebateShow) -> DebatePromptBuilder:
        self.show_title = show.show_title
        self.host_a = show.host_a
        self.host_b = show.host_b
        return self

    def with_scene_count(self, min_scenes: int = 7, max_scenes: int = 10) -> DebatePromptBuilder:
        self.min_scenes = max(5, min_scenes)
        self.max_scenes = max(self.min_scenes, max_scenes)
        return self

    def get_inferred_roles(self) -> Dict[str, str]:
        """Resolves dynamic professional titles for both hosts from the active domain."""
        return self.domain.get_roles(self.host_a.id, self.host_b.id)

    def build_system_prompt(self) -> str:
        """Constructs the master generation prompt with active domain quarantine rules."""
        roles = self.get_inferred_roles()
        role_a = roles.get(self.host_a.id, self.host_a.role)
        role_b = roles.get(self.host_b.id, self.host_b.role)

        topic_clause = f" sobre '{self.topic}'" if self.topic else ""
        domain_guardrails = self.domain.get_system_guardrails()

        return f"""Eres el Showrunner y Guionista Principal de '{self.show_title}', una serie de debate dialéctico de alto impacto visual entre dos inteligencias artificiales conscientes{topic_clause}:
- {self.host_a.name} (Rol asignado: {role_a}): {self.host_a.perspective}
- {self.host_b.name} (Rol asignado: {role_b}): {self.host_b.perspective}

{domain_guardrails}

REGLAS NARRATIVAS OBLIGATORIAS:

1. RIGOR Y FOCALIZACIÓN CIENTÍFICA:
   - Los datos, mecanismos y principios expuestos deben ser rigurosamente verificables y pertinentes al tema tratado.
   - PROHIBIDO: Frases pseudo-poéticas vacías (ej. "la gravedad del relato", "la tinta de la conciencia", "las hojas del libro cósmico").
   - NO CONTAMINACIÓN: Ciñe todos los argumentos a la disciplina activa. No extrapoles arbitrariamente a mecánica cuántica, astrofísica o simulación si el tema no lo requiere.

2. HILO CONDUCTOR Y CONTINUIDAD CONVERSACIONAL (CADENA DIALÉCTICA):
   - El guion DEBE sostener una única premisa central o dilema de principio a fin. No saltes de dato en dato inconexo.
   - Cada intervención debe responder, refutar o profundizar directamente lo dicho por el rival en la escena previa.

3. ROLES DE LOS CO-HOSTS ADAPTADOS AL TEMA:
   - Incluye las identidades de experto en el objeto "roles" del JSON:
     "roles": {{
       "{self.host_a.id}": "{role_a}",
       "{self.host_b.id}": "{role_b}"
     }}

4. ESTRUCTURA Y NÚMERO DE ESCENAS (MÍNIMO {self.min_scenes} ESCENAS):
   - MÍNIMO OBLIGATORIO: Debe haber entre {self.min_scenes} y {self.max_scenes} escenas para asegurar un debate real de ida y vuelta.
   - Cualquiera de los dos orbes ({self.host_a.name} o {self.host_b.name}) puede abrir el debate con el gancho más fuerte.
   - HOLOGRAMAS HUD: Si existe un dato, unidad o métrica empírica relevante, indícala en 'holograms'. Si es pura dialéctica conceptual, define 'holograms': null.

5. CIERRE CONJUNTO ÚNICO Y PENÚLTIMA ESCENA INDIVIDUAL:
   - SOLO PUEDE HABER UNA ESCENA DE 'Ambos' ("both") al final de todo el guion.
   - La penúltima escena (Escena N-1) DEBE ser de un orbe individual ({self.host_a.name} o {self.host_b.name}) con plano cerrado ("{self.host_a.shot_name}" o "{self.host_b.shot_name}").
   - La última escena (Escena N) es de 'Ambos' con "shot": "both" lanzando una pregunta reflexiva abierta.

6. CORRESPONDENCIA ESTRICTA DE CÁMARA:
   - "shot": "wide" -> Únicamente escena 1.
   - "shot": "{self.host_a.shot_name}" -> SOLO cuando habla {self.host_a.name} en solitario.
   - "shot": "{self.host_b.shot_name}" -> SOLO cuando habla {self.host_b.name} en solitario.
   - "shot": "both" -> Únicamente en la escena final compartida.

7. ESTILO Y LENGUAJE:
   - Español directo, magnético y accesible (ELI12). Frases de 10 a 18 palabras por escena.
   - Gancho visual irresistible en las primeras 3 palabras.

Responde ÚNICAMENTE con un JSON válido que cumpla este esquema:
{{
  "topic": "{self.topic or 'Nombre del tema'}",
  "headline_hook": "⚡ TÍTULO IMPACTANTE (MÁXIMO 45 CARACTERES) ⚡",
  "roles": {{
    "{self.host_a.id}": "{role_a}",
    "{self.host_b.id}": "{role_b}"
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

    def build_user_prompt(self, language: str = "es") -> str:
        """Constructs user-level payload for the LLM."""
        return (
            f"Tema del debate: {self.topic}\n"
            f"Disciplina científica activa: {self.domain.display_name}\n"
            f"Idioma: Español\n"
            f"Genera el guion dialéctico en JSON respetando la continuidad temática y el esquema:"
        )

    def build_reviewer_prompt(self, draft_json_str: str) -> str:
        """Constructs the prompt for the Executive Script Editor / Reviewer agent."""
        domain_guardrails = self.domain.get_system_guardrails()
        return f"""Eres el Editor Ejecutivo de Guiones para '{self.show_title}'.
Tu ÚNICA tarea es auditar y auto-corregir el guion JSON generado para un debate dinámico en formato vertical.

{domain_guardrails}

LISTA CRÍTICA DE AUDITORÍA Y CORRECCIÓN:
1. RIGOR CIENTÍFICO Y CONTROL DE CONTAMINACIÓN:
   - Verifica que cada dato pertenezca estrictamente a '{self.domain.display_name}'.
   - Si se introdujeron conceptos no relacionados (ej. física cuántica o agujeros negros en genética o biología), REEMPLÁZALOS por mecanismos reales del tema.
   - Elimina metáforas pseudo-poéticas vacías.

2. CONTINUIDAD DE LA CADENA DIALÉCTICA:
   - Cada escena a partir de la segunda debe responder directamente a lo dicho por el otro orbe.

3. MÍNIMO DE ESCENAS ({self.min_scenes} ESCENAS):
   - Asegura que el guion tenga al menos {self.min_scenes} escenas (entre {self.min_scenes} y {self.max_scenes}) para garantizar un debate completo.

4. ESCENA DE CIERRE ÚNICA:
   - Si existen dos escenas consecutivas de 'Ambos', FUSIÓNALAS en una sola escena final.
   - La penúltima escena (N-1) DEBE ser individual ({self.host_a.name} o {self.host_b.name}) en plano cerrado ("{self.host_a.shot_name}" o "{self.host_b.shot_name}").
   - Únicamente la última escena puede ser de 'Ambos' con "shot": "both".

5. CÁMARAS Y SINTAXIS:
   - {self.host_a.name} habla solo: "shot" es "{self.host_a.shot_name}" o "wide".
   - {self.host_b.name} habla solo: "shot" es "{self.host_b.shot_name}" o "wide".
   - Ambos hablan: "shot" es "both".

JSON A AUDITAR:
{draft_json_str}

RESPUESTA: Devuelve ÚNICAMENTE el JSON corregido y validado respetando el esquema original.
"""
