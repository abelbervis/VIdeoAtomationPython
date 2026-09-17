"""
OOP Rule Engine, Editorial Profiles, and Camera Shot Specifications for Cosmic Debates.
Replaces static prompt strings and hardcoded validation with modular, polymorphic rule objects.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from core.domains import TopicDomain
    from core.hosts import OrbHost
    from core.script_models import DebateScript, Scene


class CameraShotType(str, Enum):
    """Enumeration of camera shot styles in vertical video production."""
    WIDE = "wide"
    CLOSE = "close"
    DUAL = "both"

    @classmethod
    def resolve_shot_name(cls, shot_type: CameraShotType, host: Optional[OrbHost] = None) -> str:
        """Resolves the exact camera string identifier expected by video renderers."""
        if shot_type == cls.WIDE:
            return "wide"
        if shot_type == cls.DUAL:
            return "both"
        if host:
            return host.shot_name
        return "close"

    @classmethod
    def is_valid_shot(cls, shot_str: str, host_a: Optional[OrbHost] = None, host_b: Optional[OrbHost] = None) -> bool:
        """Checks whether a camera shot string is recognized."""
        s = str(shot_str).lower().strip()
        valid_shots = {"wide", "both", "close"}
        if host_a:
            valid_shots.add(host_a.shot_name.lower())
        if host_b:
            valid_shots.add(host_b.shot_name.lower())
        return s in valid_shots


@dataclass
class EditorialProfile:
    """
    Encapsulates tone, audience target, and duration constraints for the debate show.
    Decouples editorial formatting from prompts and enables multi-format adaptability.
    """
    name: str = "Vertical Shorts Debate (Default)"
    language: str = "es"
    audience_level: str = "ELI12 (Explicación intuitiva para mentes curiosas sin tecnicismos oscuros)"
    min_words_per_scene: int = 8
    max_words_per_scene: int = 20
    max_headline_length: int = 45
    tone_description: str = "dinámico, riguroso, directo y magnético"
    hook_style: str = "Pregunta visual o dilema impactante en las primeras 3 palabras"

    @classmethod
    def short_form_viral(cls) -> EditorialProfile:
        """Optimized for 40-60s fast-paced vertical video (TikTok, Shorts, Reels)."""
        return cls(
            name="Viral Short-Form",
            min_words_per_scene=8,
            max_words_per_scene=16,
            max_headline_length=40,
            tone_description="ritmo acelerado, tensión dialéctica alta, sin preámbulos",
        )

    @classmethod
    def deep_dive(cls) -> EditorialProfile:
        """Optimized for longer analytical deep dives."""
        return cls(
            name="Deep Dive Analysis",
            min_words_per_scene=14,
            max_words_per_scene=26,
            max_headline_length=50,
            audience_level="Académico divulgativo accesible",
            tone_description="profundo, analítico y conceptualmente denso",
        )


class PromptRule(ABC):
    """
    Abstract rule specification that governs both:
    1. The generation instructions rendered in the LLM prompt.
    2. The programmatic validation of the resulting DebateScript.
    """
    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier for the rule."""
        pass

    @abstractmethod
    def to_prompt_text(
        self,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> str:
        """Renders the prompt clause instructing the LLM on this rule."""
        pass

    @abstractmethod
    def validate_script(
        self,
        script: DebateScript,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> List[str]:
        """Validates the script against this rule, returning any error descriptions."""
        pass


class ScientificRigorAndQuarantineRule(PromptRule):
    """Enforces strict scientific grounding and prevents domain cross-contamination."""
    @property
    def rule_id(self) -> str:
        return "scientific_rigor_quarantine"

    def to_prompt_text(
        self,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> str:
        text = (
            "1. RIGOR CIENTÍFICO Y AISLAMIENTO TEMÁTICO:\n"
            f"   - Disciplina asignada: '{domain.display_name}'.\n"
            f"   - Enfoque: {domain.allowed_focus_hint}\n"
            "   - PROHIBIDO: Frases pseudo-poéticas vacías (ej. 'la gravedad del relato', 'el lienzo cuántico').\n"
        )
        if domain.forbidden_terms:
            terms = ", ".join(domain.forbidden_terms[:10])
            text += f"   - TÉRMINOS EXPRESAMENTE PROHIBIDOS en este guion: [{terms}]."
        return text

    def validate_script(
        self,
        script: DebateScript,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> List[str]:
        errors = []
        violations = script.detect_contamination(domain)
        for v in violations:
            errors.append(
                f"Contaminación temática en Escena {v['scene_index']+1}: "
                f"Término prohibido '{v['forbidden_term']}' en disciplina '{domain.display_name}'."
            )
        return errors


class ConversationalChainingRule(PromptRule):
    """Enforces dialectic continuity: each scene directly answers the previous opponent."""
    @property
    def rule_id(self) -> str:
        return "conversational_chaining"

    def to_prompt_text(
        self,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> str:
        return (
            "2. HILO CONDUCTOR Y CONTINUIDAD DIALÉCTICA:\n"
            "   - El guion debe sostener una única premisa central de inicio a fin.\n"
            "   - Cada escena debe contraargumentar, profundizar o responder directamente a lo dicho por el rival en la escena previa."
        )

    def validate_script(
        self,
        script: DebateScript,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> List[str]:
        errors = []
        scenes = script.scenes
        if len(scenes) >= 2:
            for i in range(len(scenes) - 2):
                curr = scenes[i]
                nxt = scenes[i + 1]
                if curr.is_solo() and nxt.is_solo() and curr.entity == nxt.entity:
                    errors.append(f"Falta de alternancia: Escenas {i+1} y {i+2} son del mismo orbe ({curr.speaker}).")
        return errors


class SceneCountRule(PromptRule):
    """Configurable rule establishing min and max scene volume."""
    def __init__(self, min_scenes: int = 7, max_scenes: int = 10):
        self.min_scenes = max(4, min_scenes)
        self.max_scenes = max(self.min_scenes, max_scenes)

    @property
    def rule_id(self) -> str:
        return "scene_count"

    def to_prompt_text(
        self,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> str:
        return (
            f"3. ESTRUCTURA Y NÚMERO DE ESCENAS:\n"
            f"   - MÍNIMO OBLIGATORIO: Debe haber entre {self.min_scenes} y {self.max_scenes} escenas.\n"
            f"   - Cualquiera de los dos ({host_a.name} o {host_b.name}) puede abrir el debate con el gancho más fuerte."
        )

    def validate_script(
        self,
        script: DebateScript,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> List[str]:
        count = len(script.scenes)
        if count < self.min_scenes:
            return [f"Escenas insuficientes: {count} (requerido mínimo {self.min_scenes})."]
        if count > self.max_scenes + 2:
            return [f"Demasiadas escenas para formato vertical: {count} (máximo {self.max_scenes})."]
        return []


class SingleClosingSceneRule(PromptRule):
    """Enforces exactly one joint closing scene and individual penultimate shot."""
    @property
    def rule_id(self) -> str:
        return "single_closing_scene"

    def to_prompt_text(
        self,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> str:
        return (
            "4. CIERRE CONJUNTO ÚNICO Y PENÚLTIMA ESCENA INDIVIDUAL:\n"
            "   - SOLO PUEDE HABER UNA ESCENA DE 'Ambos' ('both') al final del guion.\n"
            f"   - La penúltima escena (N-1) DEBE ser individual ({host_a.name} o {host_b.name}) en plano cerrado ('{host_a.shot_name}' o '{host_b.shot_name}').\n"
            "   - La última escena (N) es de 'Ambos' con 'shot': 'both' lanzando la pregunta final reflexiva."
        )

    def validate_script(
        self,
        script: DebateScript,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> List[str]:
        errors = []
        both_indices = [i for i, s in enumerate(script.scenes) if s.is_both()]
        if len(both_indices) > 1:
            errors.append(f"Se encontraron {len(both_indices)} escenas conjuntas; solo se permite una única escena final.")

        if len(script.scenes) >= 2:
            penult = script.scenes[-2]
            if penult.is_both():
                errors.append("La penúltima escena no puede ser de 'Ambos'; debe ser individual en plano cerrado.")
            elif penult.shot in ["wide", "both"]:
                errors.append(f"La penúltima escena tiene toma '{penult.shot}'; debe ser plano cerrado.")
        return errors


class CameraMatchingRule(PromptRule):
    """Verifies that camera cuts strictly correlate with the active speaker."""
    @property
    def rule_id(self) -> str:
        return "camera_matching"

    def to_prompt_text(
        self,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> str:
        return (
            "5. CORRESPONDENCIA ESTRICTA DE CÁMARAS:\n"
            "   - 'wide': Únicamente escena 1 (apertura general opcional).\n"
            f"   - '{host_a.shot_name}': Exclusivo para {host_a.name} hablando en solitario.\n"
            f"   - '{host_b.shot_name}': Exclusivo para {host_b.name} hablando en solitario.\n"
            "   - 'both': Exclusivo para la escena de cierre compartido."
        )

    def validate_script(
        self,
        script: DebateScript,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> List[str]:
        errors = []
        for idx, sc in enumerate(script.scenes):
            if sc.entity == host_a.id and sc.shot == host_b.shot_name:
                errors.append(f"Escena {idx+1}: {host_a.name} tiene asignada la cámara de su rival ({host_b.shot_name}).")
            elif sc.entity == host_b.id and sc.shot == host_a.shot_name:
                errors.append(f"Escena {idx+1}: {host_b.name} tiene asignada la cámara de su rival ({host_a.shot_name}).")
            elif sc.is_both() and sc.shot not in ["both", "wide"]:
                errors.append(f"Escena {idx+1} conjunta no usa shot 'both'.")
        return errors


class EditorialToneRule(PromptRule):
    """Enforces tone, word counts, and headline length based on the EditorialProfile."""
    @property
    def rule_id(self) -> str:
        return "editorial_tone"

    def to_prompt_text(
        self,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> str:
        return (
            "6. ESTILO, TONO Y FORMATO:\n"
            f"   - Nivel de audiencia: {profile.audience_level}.\n"
            f"   - Tono: {profile.tone_description}.\n"
            f"   - Longitud por escena: {profile.min_words_per_scene} a {profile.max_words_per_scene} palabras.\n"
            f"   - Headline Hook: Máximo {profile.max_headline_length} caracteres. {profile.hook_style}."
        )

    def validate_script(
        self,
        script: DebateScript,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> List[str]:
        errors = []
        if len(script.headline_hook) > profile.max_headline_length + 15:
            errors.append(
                f"Headline hook demasiado largo ({len(script.headline_hook)} car., máx: {profile.max_headline_length})."
            )
        return errors


class RuleEngine:
    """
    Composite Rule Engine that manages a pipeline of PromptRules.
    Used by PromptBuilder to construct instructions and by DebateScript to validate outputs.
    """
    def __init__(self, rules: Optional[List[PromptRule]] = None):
        if rules is not None:
            self.rules = list(rules)
        else:
            self.rules = [
                ScientificRigorAndQuarantineRule(),
                ConversationalChainingRule(),
                SceneCountRule(min_scenes=7, max_scenes=10),
                SingleClosingSceneRule(),
                CameraMatchingRule(),
                EditorialToneRule(),
            ]

    def add_rule(self, rule: PromptRule) -> RuleEngine:
        self.rules.append(rule)
        return self

    def set_scene_count(self, min_scenes: int, max_scenes: int) -> None:
        """Updates or replaces the SceneCountRule."""
        self.rules = [r for r in self.rules if not isinstance(r, SceneCountRule)]
        self.rules.insert(2, SceneCountRule(min_scenes=min_scenes, max_scenes=max_scenes))

    def build_prompt_sections(
        self,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> str:
        """Renders all active rules into structured prompt text."""
        sections = []
        for r in self.rules:
            text = r.to_prompt_text(domain, host_a, host_b, profile)
            if text:
                sections.append(text)
        return "\n\n".join(sections)

    def validate_all(
        self,
        script: DebateScript,
        domain: TopicDomain,
        host_a: OrbHost,
        host_b: OrbHost,
        profile: EditorialProfile
    ) -> Tuple[bool, List[str]]:
        """Runs all rules against the script, aggregating errors."""
        all_errors: List[str] = []
        for r in self.rules:
            errs = r.validate_script(script, domain, host_a, host_b, profile)
            all_errors.extend(errs)
        return (len(all_errors) == 0, all_errors)
