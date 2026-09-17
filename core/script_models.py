"""
Object-Oriented Data Models for Cosmic Orb Debate Scripts.
Provides encapsulated domain models (Scene, HologramData, DebateScript)
with built-in structural sanitization, camera angle verification, and
anti-contamination validation.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from core.domains import TopicDomain
    from core.hosts import OrbHost


@dataclass
class Scene:
    """Individual dialogue intervention in a co-host debate video."""
    speaker: str
    entity: str
    text: str
    shot: str = "wide"
    duration: float = 3.2

    def is_both(self) -> bool:
        """Checks if the scene is delivered jointly by both co-hosts."""
        spk = str(self.speaker).strip().lower()
        ent = str(self.entity).strip().lower()
        return spk in ["ambos", "both"] or ent == "both" or self.shot == "both"

    def is_solo(self) -> bool:
        """Checks if the scene is an individual host intervention."""
        return not self.is_both()

    def word_count(self) -> int:
        """Returns the total word count of the spoken dialogue."""
        return len(self.text.split())

    def char_count(self) -> int:
        """Returns character length of the spoken dialogue."""
        return len(self.text)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes scene to JSON-compatible dictionary."""
        return {
            "speaker": self.speaker,
            "entity": self.entity,
            "text": self.text,
            "shot": self.shot,
            "duration": round(float(self.duration), 2),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Scene:
        """Deserializes a scene from a dictionary with defensive type coercion."""
        return cls(
            speaker=str(data.get("speaker", "Quantum")).strip(),
            entity=str(data.get("entity", "quantum")).strip().lower(),
            text=str(data.get("text", "")).strip(),
            shot=str(data.get("shot", "wide")).strip().lower(),
            duration=max(1.5, min(10.0, float(data.get("duration", 3.2)))),
        )


@dataclass
class HologramData:
    """HUD holographic metrics floating next to an orb host."""
    title: str
    subtitle: str
    category: str = "DATOS"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title.upper(),
            "subtitle": self.subtitle,
            "category": self.category.upper(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HologramData:
        return cls(
            title=str(data.get("title", "")).strip().upper(),
            subtitle=str(data.get("subtitle", "")).strip(),
            category=str(data.get("category", "DATOS")).strip().upper(),
        )


@dataclass
class DebateScript:
    """
    Complete dialectic debate script with topic, roles, scenes, and optional HUD holograms.
    Encapsulates all validation, decontamination, and sanitization logic.
    """
    topic: str
    headline_hook: str
    roles: Dict[str, str] = field(default_factory=dict)
    scenes: List[Scene] = field(default_factory=list)
    holograms: Optional[Dict[str, Any]] = None
    cohosts: Optional[str] = None
    domain_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the entire debate script to a dictionary."""
        res: Dict[str, Any] = {
            "topic": self.topic,
            "headline_hook": self.headline_hook,
            "roles": self.roles,
            "scenes": [s.to_dict() for s in self.scenes],
        }
        if self.holograms is not None:
            res["holograms"] = self.holograms
        if self.cohosts is not None:
            res["cohosts"] = self.cohosts
        return res

    def to_json(self, indent: int = 2) -> str:
        """Serializes the script to a cleanly formatted JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], default_topic: Optional[str] = None) -> DebateScript:
        """Constructs a DebateScript from raw JSON/dict with safe defaults."""
        raw_scenes = data.get("scenes", [])
        parsed_scenes: List[Scene] = []
        if isinstance(raw_scenes, list):
            for s in raw_scenes:
                if isinstance(s, dict):
                    parsed_scenes.append(Scene.from_dict(s))

        roles = data.get("roles", {})
        if not isinstance(roles, dict):
            roles = {}

        return cls(
            topic=str(data.get("topic") or default_topic or "Debate").strip(),
            headline_hook=str(data.get("headline_hook", "⚡ DEBATE EXPRESS ⚡")).strip(),
            roles={str(k).strip(): str(v).strip() for k, v in roles.items()},
            scenes=parsed_scenes,
            holograms=data.get("holograms"),
            cohosts=data.get("cohosts"),
        )

    def sanitize_structure(
        self,
        host_a: Optional[OrbHost] = None,
        host_b: Optional[OrbHost] = None
    ) -> DebateScript:
        """
        Applies rigorous structural rules to the script:
        1. Merges consecutive 'both' / 'Ambos' closing scenes into exactly one single closing scene.
        2. Enforces that the penultimate scene (N-1) is delivered solo in close-up.
        3. Realigns camera shots with the active speaker.
        """
        if not self.scenes:
            return self

        # 1. Merge consecutive 'both' / 'Ambos' scenes
        cleaned: List[Scene] = []
        i = 0
        while i < len(self.scenes):
            curr = self.scenes[i]
            if curr.is_both() and i + 1 < len(self.scenes):
                nxt = self.scenes[i + 1]
                if nxt.is_both():
                    # Merge text
                    merged_txt = curr.text.strip()
                    if nxt.text.strip() and nxt.text.strip() not in merged_txt:
                        merged_txt = f"{merged_txt} {nxt.text.strip()}"
                    merged_dur = round(min(5.5, max(3.0, curr.duration + nxt.duration * 0.7)), 1)
                    cleaned.append(Scene(
                        speaker="Ambos",
                        entity="both",
                        text=merged_txt,
                        shot="both",
                        duration=merged_dur
                    ))
                    i += 2
                    continue
            cleaned.append(curr)
            i += 1

        # 2. Enforce penultimate solo shot & close camera
        host_a_id = host_a.id if host_a else "quantum"
        host_b_id = host_b.id if host_b else "solar"
        host_a_name = host_a.name if host_a else "Quantum"
        host_b_name = host_b.name if host_b else "Solar"
        host_a_shot = host_a.shot_name if host_a else "close_quantum"
        host_b_shot = host_b.shot_name if host_b else "close_solar"

        if len(cleaned) >= 2:
            last = cleaned[-1]
            penultimate = cleaned[-2]

            if last.is_both():
                if penultimate.is_both():
                    # Penultimate was both, convert to solo
                    alt_host = host_b_name if len(cleaned) % 2 == 0 else host_a_name
                    alt_ent = host_b_id if len(cleaned) % 2 == 0 else host_a_id
                    alt_shot = host_b_shot if len(cleaned) % 2 == 0 else host_a_shot
                    penultimate.speaker = alt_host
                    penultimate.entity = alt_ent
                    penultimate.shot = alt_shot

                # Ensure penultimate shot is close-up, never wide or both
                if penultimate.shot in ["wide", "both"]:
                    if penultimate.entity == host_a_id:
                        penultimate.shot = host_a_shot
                    else:
                        penultimate.shot = host_b_shot

        # 3. Align camera shots strictly with speakers
        for idx, sc in enumerate(cleaned):
            if sc.is_both():
                sc.speaker = "Ambos"
                sc.entity = "both"
                sc.shot = "both"
            elif idx == 0 and sc.shot == "wide":
                pass  # Wide opening scene is permitted
            elif sc.entity == host_a_id or sc.speaker.lower() == host_a_name.lower():
                sc.entity = host_a_id
                sc.speaker = host_a_name
                if sc.shot != "wide":
                    sc.shot = host_a_shot
            elif sc.entity == host_b_id or sc.speaker.lower() == host_b_name.lower():
                sc.entity = host_b_id
                sc.speaker = host_b_name
                if sc.shot != "wide":
                    sc.shot = host_b_shot

        self.scenes = cleaned
        return self

    def validate(
        self,
        domain: Optional[TopicDomain] = None,
        host_a: Optional[OrbHost] = None,
        host_b: Optional[OrbHost] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validates the script against length, camera rules, and domain anti-contamination rules.
        Returns (is_valid, list_of_errors_or_warnings).
        """
        errors: List[str] = []

        if len(self.scenes) < 7:
            errors.append(f"Mínimo de escenas no alcanzado: {len(self.scenes)} (requerido: 7+)")

        if not self.headline_hook:
            errors.append("Falta 'headline_hook' de apertura.")

        # Check closing scenes count
        both_scenes = [i for i, s in enumerate(self.scenes) if s.is_both()]
        if len(both_scenes) > 1:
            errors.append(f"Hay {len(both_scenes)} escenas con 'Ambos'; solo se permite una escena de cierre conjunta.")

        # Check camera shots vs speaker
        host_a_id = host_a.id if host_a else "quantum"
        host_b_id = host_b.id if host_b else "solar"
        for i, s in enumerate(self.scenes):
            if s.entity == host_a_id and s.shot == f"close_{host_b_id}":
                errors.append(f"Escena {i+1}: El anfitrión '{s.speaker}' tiene asignada la cámara del rival '{s.shot}'.")
            elif s.entity == host_b_id and s.shot == f"close_{host_a_id}":
                errors.append(f"Escena {i+1}: El anfitrión '{s.speaker}' tiene asignada la cámara del rival '{s.shot}'.")

        # Check domain anti-contamination
        if domain:
            contaminations = self.detect_contamination(domain)
            for item in contaminations:
                errors.append(
                    f"Contaminación temática en Escena {item['scene_index']+1}: "
                    f"Se detectó el término prohibido '{item['forbidden_term']}' en dominio '{domain.display_name}'."
                )

        return (len(errors) == 0, errors)

    def detect_contamination(self, domain: TopicDomain) -> List[Dict[str, Any]]:
        """Scans all dialogue scenes for forbidden concepts from unrelated disciplines."""
        violations: List[Dict[str, Any]] = []
        for idx, sc in enumerate(self.scenes):
            found_terms = domain.detect_contamination(sc.text)
            for term in found_terms:
                violations.append({
                    "scene_index": idx,
                    "speaker": sc.speaker,
                    "forbidden_term": term,
                    "text_snippet": sc.text
                })
        return violations
