"""
Topic Domain Architecture and Thematic Quarantine for Cosmic Orb Debates.
Implements the Strategy pattern to isolate scientific disciplines, define expert roles,
and enforce strict anti-contamination guardrails (preventing concepts like quantum physics
or astrophysics from leaking into biology, sociology, or genetics topics).
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TopicDomain(ABC):
    """
    Abstract Strategy representing a distinct scientific or philosophical discipline.
    Encapsulates domain-specific boundaries, forbidden contamination terms, and expert identities.
    """
    domain_id: str
    display_name: str
    description: str
    keywords: List[str] = field(default_factory=list)
    forbidden_terms: List[str] = field(default_factory=list)
    allowed_focus_hint: str = ""
    default_role_a: str = "IA Analítica"
    default_role_b: str = "IA Empírica"

    @property
    def name(self) -> str:
        return self.display_name

    def matches(self, topic: str) -> bool:
        """Determines if the topic belongs to this scientific domain."""
        if not topic:
            return False
        t = topic.lower().strip()
        for kw in self.keywords:
            if kw in t:
                return True
            # Check whole word regex for short acronyms like dna, adn, ia, ai
            if len(kw) <= 4:
                if re.search(rf"\b{re.escape(kw)}\b", t, re.IGNORECASE):
                    return True
        return False

    def detect_contamination(self, text: str) -> List[str]:
        """
        Scans dialogue or text for unauthorized concepts from unrelated domains.
        Returns a list of forbidden terms found in the text.
        """
        if not text or not self.forbidden_terms:
            return []
        t = text.lower()
        violations = []
        for term in self.forbidden_terms:
            pattern = rf"\b{re.escape(term.lower())}\b"
            if re.search(pattern, t, re.IGNORECASE):
                violations.append(term)
        return list(set(violations))

    def get_system_guardrails(self) -> str:
        """Generates dynamic, domain-specific prompt rules to prevent hallucinated concept-leaks."""
        lines = [
            f"DISCIPLINA ACADÉMICA DEL DEBATE: '{self.display_name}'.",
            f"ENFOQUE OBLIGATORIO: {self.allowed_focus_hint}"
        ]
        if self.forbidden_terms:
            terms_sample = ", ".join(self.forbidden_terms[:10])
            lines.append(
                f"REGLA DE NO CONTAMINACIÓN TEMÁTICA: NUNCA menciones conceptos ajenos a '{self.display_name}'. "
                f"Términos expresamente PROHIBIDOS en este guion: [{terms_sample}]."
            )
        return "\n".join(lines)

    def get_roles(self, host_a_id: str = "quantum", host_b_id: str = "solar") -> Dict[str, str]:
        """Returns topic-tailored professional roles for the co-hosts."""
        return {
            host_a_id: self.default_role_a,
            host_b_id: self.default_role_b
        }

    def get_host_roles(self, host_a: Any, host_b: Any) -> Dict[str, str]:
        """Helper that accepts OrbHost objects or string IDs."""
        a_id = getattr(host_a, "id", str(host_a))
        b_id = getattr(host_b, "id", str(host_b))
        return self.get_roles(a_id, b_id)


class BiologyAndGeneticsDomain(TopicDomain):
    """Domain for molecular biology, genetics, epigenetics, evolution, and medicine."""
    def __init__(self):
        super().__init__(
            domain_id="biology_genetics",
            display_name="Biología Molecular, Genética y Evolución",
            description="Ciencias biológicas, genómica, ADN, herencia, bioética y medicina.",
            keywords=[
                "adn", "dna", "gen", "genes", "genom", "celular", "célula", "celula",
                "virus", "bacteria", "crispr", "epigenet", "clonac", "bioetica", "bioética",
                "vida sintética", "organismo", "proteina", "proteína", "mutacion", "mutación",
                "herencia", "biolog", "medicina", "terapia génica", "fauna", "zoolog", "especie"
            ],
            forbidden_terms=[
                "cuántico", "cuántica", "superposición", "horizonte de eventos", "horizonte de sucesos",
                "agujero negro", "velocidad de la luz", "dilatación temporal", "partícula subatómica",
                "antimateria", "fusión termodinámica", "espaciotiempo", "teoría de cuerdas",
                "mecánica cuántica", "ordenador cuántico", "planck"
            ],
            allowed_focus_hint="Enfócate con total rigurosidad en secuencias genéticas, mecanismos moleculares, expresión proteica, selección natural, adaptación o dilemas bioéticos reales.",
            default_role_a="IA Genómica Molecular",
            default_role_b="IA Bioética y Evolución"
        )


class NeuroscienceAndCognitionDomain(TopicDomain):
    """Domain for neuroscience, philosophy of mind, cognitive science, and AI consciousness."""
    def __init__(self):
        super().__init__(
            domain_id="neuroscience_cognition",
            display_name="Neurociencia, Cognición e Inteligencia Artificial",
            description="Redes neuronales, arquitectura sináptica, cognición, conciencia y mente.",
            keywords=[
                "cerebro", "mente", "conciencia", "neurol", "sinapsis", "cogniti",
                "pensamiento", "inteligencia artificial", "ia", "ai", "redes neuronales",
                "pulpo", "psicolog", "memoria", "subjetividad", "percepcion", "percepción"
            ],
            forbidden_terms=[
                "superposición cuántica", "horizonte de eventos", "horizonte de sucesos",
                "agujero negro", "fusión nuclear estelar", "singularidad espaciotemporal",
                "dilatación temporal gravitatoria", "astrofísica", "supernova"
            ],
            allowed_focus_hint="Enfócate en circuitos electroquímicos, arquitectura sináptica, algoritmos de aprendizaje, comportamiento biológico o el enigma de la experiencia subjetiva.",
            default_role_a="IA Neurociencia Cognitiva",
            default_role_b="IA Biología y Conducta"
        )


class EcologyAndEarthDomain(TopicDomain):
    """Domain for climatology, ecology, oceanography, geology, and planetary dynamics."""
    def __init__(self):
        super().__init__(
            domain_id="ecology_earth",
            display_name="Ciencias de la Tierra, Climatología y Ecología",
            description="Dinámica climática, biosfera, geología, océanos y sustentabilidad planetaria.",
            keywords=[
                "clima", "climát", "tierra", "atmósfera", "atmosfera", "oceano", "océano",
                "ecolog", "geolog", "biosfera", "planeta", "ecosistema", "biodiversidad",
                "calentamiento global", "carbono", "glaciar"
            ],
            forbidden_terms=[
                "cuántico", "cuántica", "superposición", "horizonte de eventos",
                "horizonte de sucesos", "agujero negro", "partícula subatómica", "antimateria",
                "teoría de cuerdas", "singularidad gravitatoria"
            ],
            allowed_focus_hint="Enfócate en dinámicas termodinámicas planetarias, ciclos biogeoquímicos, equilibrio ecológico y evidencia científica observable del clima.",
            default_role_a="IA Dinámica Planetaria",
            default_role_b="IA Ecología y Biosfera"
        )


class AstrophysicsAndCosmologyDomain(TopicDomain):
    """Domain for astrophysics, cosmology, general relativity, and stellar dynamics."""
    def __init__(self):
        super().__init__(
            domain_id="astrophysics_cosmology",
            display_name="Astrofísica y Cosmología Relativista",
            description="Gravitación, espaciotiempo, estrellas, agujeros negros y evolución cósmica.",
            keywords=[
                "agujero negro", "estrella", "sol", "galaxia", "cosmos", "espaciotiempo",
                "gravedad", "relatividad", "supernova", "hawking", "singularidad",
                "universo", "astrofisic", "astrofísica", "radiacion cósmica", "exoplaneta"
            ],
            forbidden_terms=[
                "adn", "adn recombinante", "epigenética", "genes", "clonación",
                "sinapsis cerebral", "terapia génica", "células madre"
            ],
            allowed_focus_hint="Enfócate en relatividad general, curvatura del espaciotiempo, límite de Chandrasekhar, radiación de Hawking y física estelar.",
            default_role_a="IA Gravedad y Cosmología",
            default_role_b="IA Astrofísica Relativista"
        )


class QuantumPhysicsDomain(TopicDomain):
    """Domain for quantum mechanics, subatomic particles, and fundamental fields."""
    def __init__(self):
        super().__init__(
            domain_id="quantum_physics",
            display_name="Física Cuántica y Escala Subatómica",
            description="Mecánica cuántica, campos cuánticos, partículas fundamentales y decoherencia.",
            keywords=[
                "cuantic", "cuántic", "subatomic", "subatómic", "planck", "entrelazamiento",
                "fotón", "foton", "electrón", "electron", "superposic", "quark", "boson", "bosón",
                "incertidumbre", "heisenberg", "colapso de onda"
            ],
            forbidden_terms=[
                "adn recombinante", "epigenética", "clonación", "psicoanálisis",
                "zoología marina", "botánica"
            ],
            allowed_focus_hint="Enfócate en principios fundamentales como la dualidad onda-partícula, el principio de incertidumbre, estados superpuestos y decoherencia experimental.",
            default_role_a="IA Física Cuántica",
            default_role_b="IA Física de Partículas"
        )


class ComputerScienceAndSimulationDomain(TopicDomain):
    """Domain for theoretical computer science, simulation hypothesis, and algorithms."""
    def __init__(self):
        super().__init__(
            domain_id="computer_science_simulation",
            display_name="Computación Teórica, Algoritmos y Simulación",
            description="Complejidad algorítmica, teoría de la información y límites computacionales.",
            keywords=[
                "simulac", "simula", "matrix", "código", "codigo", "virtual",
                "algoritmo", "turing", "computa", "software", "autómata"
            ],
            forbidden_terms=[
                "adn recombinante", "epigenética", "clonación de mamíferos", "zoología", "terapia celular"
            ],
            allowed_focus_hint="Enfócate en límites computacionales, principio de Landauer, autómatas celulares, teoría de la información de Shannon y física de la computación.",
            default_role_a="IA Algoritmos Teóricos",
            default_role_b="IA Física de la Información"
        )


class GeneralScienceDomain(TopicDomain):
    """Neutral fallback domain for interdisciplinary or general science topics."""
    def __init__(self):
        super().__init__(
            domain_id="general_science",
            display_name="Metodología Científica y Filosofía Natural",
            description="Dominio general neutral con cero contaminación previa.",
            keywords=[],
            forbidden_terms=[],
            allowed_focus_hint="Adapta la argumentación de forma rigurosa y directa a la naturaleza del tema tratado, contrastando modelos analíticos con evidencia empírica.",
            default_role_a="IA Analítica y Metódica",
            default_role_b="IA Empírica y Sistémica"
        )


class DomainRegistry:
    """Registry managing domain strategies and automated topic resolution."""
    _domains: List[TopicDomain] = [
        BiologyAndGeneticsDomain(),
        NeuroscienceAndCognitionDomain(),
        EcologyAndEarthDomain(),
        AstrophysicsAndCosmologyDomain(),
        QuantumPhysicsDomain(),
        ComputerScienceAndSimulationDomain(),
    ]
    _fallback_domain: TopicDomain = GeneralScienceDomain()

    @classmethod
    def resolve(cls, topic: Optional[str]) -> TopicDomain:
        """Resolves the best matching scientific domain for a given topic."""
        if not topic:
            return cls._fallback_domain

        clean_topic = topic.strip()
        for domain in cls._domains:
            if domain.matches(clean_topic):
                return domain

        # Dynamically tailor generic role names based on topic keywords
        words = [w.capitalize() for w in clean_topic.split() if len(w) > 2]
        key_word = words[0] if words else "Ciencia"
        custom_domain = GeneralScienceDomain()
        custom_domain.default_role_a = f"IA {key_word} Analítica"[:28]
        custom_domain.default_role_b = f"IA {key_word} Empírica"[:28]
        return custom_domain

    @classmethod
    def register_domain(cls, domain: TopicDomain) -> None:
        """Registers an additional domain into the active registry."""
        cls._domains.insert(0, domain)
