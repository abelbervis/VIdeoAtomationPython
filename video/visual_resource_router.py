"""
Visual Resource Router & Semantic Dispatcher.
Orchestrates multi-resource video timelines, dispatching each scene to the most appropriate
visual medium (Static/Highlighted Slide, AI Vector Motion Clip, Simulated GCP Console, or Live Terminal)
based on pedagogical intent and semantic keyword analysis with zero context bloat.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from config import BASE_DIR
from video.motion_template_registry import MotionTemplateRegistry


@dataclass
class VisualResourceDescriptor:
    """Descriptor for a registered visual rendering capability."""
    id: str
    kind: str  # 'slide', 'motion', 'console', 'terminal'
    name: str
    description: str
    intent_keywords: List[str]
    priority: int = 1


class VisualResourceRouter:
    """
    Semantic Router that matches each dialogue line / scene goal to the best visual resource.
    Eliminates prompt bloat by selecting the visual medium locally (<1ms) before generating content.
    """

    def __init__(self):
        self.motion_registry = MotionTemplateRegistry()
        self._init_catalog()

    def _init_catalog(self):
        self.catalog: Dict[str, VisualResourceDescriptor] = {
            # 1. SLIDES (Ideal for structured definitions, tables, checklists)
            "slide_concept_card": VisualResourceDescriptor(
                id="slide_concept_card",
                kind="slide",
                name="Diapositiva: Tarjeta Conceptual Clave",
                description="Ideal para definiciones, problemas fundamentales y reglas de oro con bullets.",
                intent_keywords=["concepto", "definicion", "que es", "regla de oro", "importante", "resumen", "fundamento", "alerta"],
                priority=1
            ),
            "slide_comparison_table": VisualResourceDescriptor(
                id="slide_comparison_table",
                kind="slide",
                name="Diapositiva: Matriz Comparativa de Servicios",
                description="Ideal para comparar 2 o más servicios, pros, contras, tarifas y casos de uso.",
                intent_keywords=["vs", "comparativa", "diferencia", "frente a", "tabla", "pros", "contras", "cual elegir", "ventajas"],
                priority=3
            ),
            "slide_checklist": VisualResourceDescriptor(
                id="slide_checklist",
                kind="slide",
                name="Diapositiva: Checklist de Buenas Prácticas",
                description="Ideal para pasos numerados, requisitos previos y listas de verificación.",
                intent_keywords=["checklist", "requisitos", "pasos", "mejores practicas", "verificacion", "paso a paso"],
                priority=2
            ),

            # 2. MOTION CLIPS (Ideal for dynamic flows, scaling, hierarchies, moving packets)
            "motion_hierarchy_tree": VisualResourceDescriptor(
                id="motion_hierarchy_tree",
                kind="motion",
                name="Animación RAG: Árbol Jerárquico de Recursos",
                description="Visualiza la jerarquía de gobierno: Organización > Carpetas > Proyectos con herencia de políticas.",
                intent_keywords=["jerarquia", "arbol", "organizacion", "carpetas", "proyectos", "herencia", "estructura", "gobierno"],
                priority=4
            ),
            "motion_elastic_scale": VisualResourceDescriptor(
                id="motion_elastic_scale",
                kind="motion",
                name="Animación RAG: Escalado Serverless Elástico",
                description="Visualiza contenedores multiplicándose de 0 a N réplicas bajo demanda y retorno a 0 coste.",
                intent_keywords=["escala", "escalado", "serverless", "instancias", "pods", "concurrencia", "cold start", "auto-scaling", "multiplica", "demanda"],
                priority=4
            ),
            "motion_packet_flow": VisualResourceDescriptor(
                id="motion_packet_flow",
                kind="motion",
                name="Animación RAG: Flujo de Paquetes en Red",
                description="Visualiza paquetes y eventos viajando entre componentes en tiempo real (VPC, Pub/Sub).",
                intent_keywords=["flujo", "viajan", "paquetes", "pubsub", "cola", "mensajes", "red", "vpc", "fan-out", "latencia", "trafico"],
                priority=4
            ),
            "motion_storage_lifecycle": VisualResourceDescriptor(
                id="motion_storage_lifecycle",
                kind="motion",
                name="Animación RAG: Ciclo de Vida y Transición de Datos",
                description="Visualiza objetos transitando automáticamente a clases frías (Coldline) con cifrado AES-256.",
                intent_keywords=["ciclo de vida", "transicion", "coldline", "archive", "cifrado", "objetos", "retencion", "aes-256"],
                priority=4
            ),

            # 3. CONSOLE SIMULATION (Hands-on UI walkthrough)
            "console_walkthrough": VisualResourceDescriptor(
                id="console_walkthrough",
                kind="console",
                name="Consola Real de GCP: Simulación de Interfaz y Clics",
                description="Demostración visual de la interfaz gráfica real de Google Cloud Console con cursor y menús.",
                intent_keywords=["consola", "interfaz", "clic", "boton", "pantalla", "menu", "navegador", "ui", "abrimos la consola", "crear en consola"],
                priority=3
            ),

            # 4. LIVE TERMINAL (CLI execution)
            "terminal_cli": VisualResourceDescriptor(
                id="terminal_cli",
                kind="terminal",
                name="Terminal en Vivo: Comandos gcloud CLI",
                description="Simulación de terminal tecleándose en vivo con comandos bash / gcloud y salida de ejecución.",
                intent_keywords=["terminal", "comando", "gcloud", "bash", "cli", "tecleamos", "linea de comandos", "flags", "script"],
                priority=3
            )
        }

        # Load persisted custom visual resources if present
        try:
            custom_file = BASE_DIR / "data" / "custom_visual_resources.json"
            if custom_file.exists():
                saved = json.loads(custom_file.read_text(encoding="utf-8"))
                for k, v in saved.items():
                    self.catalog[k] = VisualResourceDescriptor(
                        id=v["id"],
                        kind=v["kind"],
                        name=v["name"],
                        description=v["description"],
                        intent_keywords=v.get("intent_keywords", []),
                        priority=v.get("priority", 2)
                    )
        except Exception:
            pass

    def route_text_to_resource(
        self,
        text: str,
        topic: str = "",
        explicit_kind: Optional[str] = None
    ) -> Tuple[str, str, float]:
        """
        Routes a single segment or scene text to the best visual resource.
        Returns: (kind: 'slide'|'motion'|'console'|'terminal', resource_id: str, confidence: float)
        """
        if explicit_kind and explicit_kind in ("slide", "motion", "console", "terminal"):
            # If user explicitly asks for a kind, find best descriptor inside that kind
            matching = [d for d in self.catalog.values() if d.kind == explicit_kind]
            if matching:
                best = max(matching, key=lambda d: self._score_text_for_descriptor(text, d))
                return explicit_kind, best.id, 1.0

        clean_text = text.lower()
        best_desc: Optional[VisualResourceDescriptor] = None
        best_score = -1.0

        for desc in self.catalog.values():
            score = self._score_text_for_descriptor(clean_text, desc)
            if score > best_score:
                best_score = score
                best_desc = desc

        if best_desc and best_score >= 1.0:
            return best_desc.kind, best_desc.id, min(1.0, best_score / 3.0)

        # Default fallback: Slide for general explanations
        return "slide", "slide_concept_card", 0.60

    def _score_text_for_descriptor(self, text: str, desc: VisualResourceDescriptor) -> float:
        score = 0.0
        for kw in desc.intent_keywords:
            if kw in text:
                score += 1.5 * desc.priority
        return score

    def register_resource(self, descriptor: VisualResourceDescriptor, persist: bool = True):
        """Registers a new visual resource into the catalog dynamically."""
        self.catalog[descriptor.id] = descriptor
        if persist:
            self._save_custom_resources()

    def _save_custom_resources(self):
        try:
            custom_dir = BASE_DIR / "data"
            custom_dir.mkdir(parents=True, exist_ok=True)
            custom_file = custom_dir / "custom_visual_resources.json"
            data = {}
            for k, v in self.catalog.items():
                data[k] = {
                    "id": v.id,
                    "kind": v.kind,
                    "name": v.name,
                    "description": v.description,
                    "intent_keywords": v.intent_keywords,
                    "priority": v.priority
                }
            custom_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def plan_hybrid_timeline(self, lesson: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transforms any lesson into a rich, diversified multi-resource timeline.
        Mixes slides, animations, console, and terminal for an engaging tutorial pacing.
        """
        timeline: List[Dict[str, Any]] = []
        topic = lesson.get("title", lesson.get("topic", "GCP Tutorial"))

        # Case A: Lesson already has structured scenes
        if "scenes" in lesson:
            for idx, scene in enumerate(lesson.get("scenes", []), start=1):
                text = scene.get("dialogue", "")
                user_kind = scene.get("resource_kind") or scene.get("type")
                
                # If scene type is explicitly console or terminal, respect it
                if user_kind:
                    kind = user_kind
                    r_id = f"{user_kind}_scene"
                    conf = 1.0
                else:
                    kind, r_id, conf = self.route_text_to_resource(text, topic=topic)

                timeline.append({
                    "scene_index": idx,
                    "resource_kind": kind,
                    "resource_id": r_id,
                    "confidence": conf,
                    "title": scene.get("title", f"Escena {idx}"),
                    "dialogue": text,
                    "scene_data": scene
                })
            return timeline

        # Case B: Classic lesson with slides and dialogue turns
        slides_dict = {}
        slides_list = lesson.get("slides", [])
        for s_idx, s in enumerate(slides_list, start=1):
            if isinstance(s, dict):
                s_id = s.get("slide_id") or s.get("id") or s.get("slide_number") or s.get("number") or s_idx
                try:
                    s_id = int(s_id)
                except (ValueError, TypeError):
                    s_id = s_idx
                s["slide_id"] = s_id
                slides_dict[s_id] = s

        dialogue_turns = lesson.get("dialogue", [])

        # To maintain dynamic rhythm: alternating didactic pacing
        # Intro: Slide -> Deep-dive: Motion Animation -> Detail: Slide / Terminal -> Conclusion: Slide
        for idx, turn in enumerate(dialogue_turns, start=1):
            text = turn.get("text", "")
            raw_s_id = turn.get("slide_id") or turn.get("id") or 1
            try:
                slide_id = int(raw_s_id)
            except (ValueError, TypeError):
                slide_id = 1

            slide_data = slides_dict.get(slide_id)
            if not slide_data and slides_dict:
                keys = list(slides_dict.keys())
                slide_data = slides_dict.get(keys[min(idx - 1, len(keys) - 1)], {})
            elif not slide_data:
                slide_data = {}
            user_override = turn.get("resource_kind")

            # Route turn
            if user_override:
                kind = user_override
                r_id = f"{user_override}_turn"
                conf = 1.0
            else:
                kind, r_id, conf = self.route_text_to_resource(text, topic=topic)
                
                # Context boost: If text explicitly talks about movement/scaling/flow/hierarchy, elevate to motion
                if any(w in text.lower() for w in ["escala", "mira cómo", "observa", "árbol", "jerarquía", "flujo", "paquetes"]):
                    kind = "motion"

            timeline.append({
                "scene_index": idx,
                "title": slide_data.get("title", f"Escena {idx}: {topic}"),
                "resource_kind": kind,
                "resource_id": r_id,
                "confidence": conf,
                "slide_id": slide_id,
                "speaker": turn.get("speaker", "Alex"),
                "dialogue": text,
                "slide_data": slide_data
            })

        return timeline
