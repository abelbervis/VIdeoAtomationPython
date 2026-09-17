"""
Core Domain Entities and Object-Oriented Host Models.
"""

from .hosts import OrbHost, CosmicDebateShow, DEFAULT_QUANTUM_HOST, DEFAULT_SOLAR_HOST, HostRegistry
from .domains import TopicDomain, DomainRegistry
from .rules import (
    CameraShotType,
    EditorialProfile,
    PromptRule,
    ScientificRigorAndQuarantineRule,
    ConversationalChainingRule,
    SceneCountRule,
    SingleClosingSceneRule,
    CameraMatchingRule,
    EditorialToneRule,
    RuleEngine,
)
from .script_models import Scene, HologramData, DebateScript
from .prompt_builder import DebatePromptBuilder

__all__ = [
    "OrbHost",
    "CosmicDebateShow",
    "DEFAULT_QUANTUM_HOST",
    "DEFAULT_SOLAR_HOST",
    "HostRegistry",
    "TopicDomain",
    "DomainRegistry",
    "CameraShotType",
    "EditorialProfile",
    "PromptRule",
    "ScientificRigorAndQuarantineRule",
    "ConversationalChainingRule",
    "SceneCountRule",
    "SingleClosingSceneRule",
    "CameraMatchingRule",
    "EditorialToneRule",
    "RuleEngine",
    "Scene",
    "HologramData",
    "DebateScript",
    "DebatePromptBuilder",
]
