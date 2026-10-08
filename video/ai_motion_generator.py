"""
AI-Powered Lightweight Motion Video Generator for Google Cloud Platform.
Integrates Motion Template Registry (RAG for Components) with semantic vector classification,
surgical prompt injection, auto-indexing of organic templates, and multi-layout vector rendering.
"""

import json
import math
import os
import re
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from config import BASE_DIR, OUTPUT_DIR, TEMP_DIR, GEMINI_API_KEY, sanitize_env_value
from utils.fonts import resolve_best_font_path
from video.motion_template_registry import MotionTemplateRegistry, MotionTemplate


def escape_xml(text: Any) -> str:
    """Escapes XML/SVG special characters."""
    t = str(text)
    return (t.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))


class AIMotionGenerator:
    """Generates on-the-fly animated explanatory video clips for any GCP concept using Gemini Flash and RAG Templates."""

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        fps: int = 10,
        crf: int = 26,
        temp_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None
    ):
        self.width = width
        self.height = height
        self.fps = fps
        self.crf = crf
        self.temp_dir = Path(temp_dir) if temp_dir else TEMP_DIR / "ai_motion"
        self.output_dir = Path(output_dir) if output_dir else OUTPUT_DIR / "gcp_tutorials" / "ai_animations"

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.registry = MotionTemplateRegistry()
        self.gemini_key = sanitize_env_value(os.getenv("GEMINI_API_KEY", GEMINI_API_KEY))

    def generate_motion_for_topic(
        self,
        topic: str,
        user_notes: str = "",
        output_filename: Optional[str] = None
    ) -> Tuple[Path, Dict[str, Any]]:
        """
        Main pipeline:
        1. Semantic classification to find best matching template (RAG for Components).
        2. Surgical prompt injection (only targeted schema, ~300 bytes).
        3. Fallback or organic auto-indexing if similarity is low (<50%).
        4. Multi-layout vector SVG keyframing and FFmpeg compilation to ultra-lightweight MP4.
        """
        print(f"\n🧠 [AI Motion Generator • RAG] Analizando concepto: '{topic}'...")
        template, similarity, is_match = self.registry.find_best_template(topic, user_notes, threshold=0.50)

        if is_match and template:
            print(f"   🔍 [Clasificador Semántico] Coincidencia: {similarity * 100:.1f}% con '{template.id}'")
            print(f"      • Tipo de layout: {template.renderer_type}")
            choreography = self._resolve_choreography_with_template(template, topic, user_notes)
        else:
            sim_str = f"{similarity * 100:.1f}%" if template else "0.0%"
            print(f"   🔍 [Clasificador Semántico] Similitud baja ({sim_str} < 50%). Activando generación orgánica...")
            choreography = self._resolve_organic_new_template(topic, user_notes)

        slug = "".join(c for c in topic.lower().replace(" ", "_") if c.isalnum() or c == "_")[:28]
        out_name = output_filename or f"ai_motion_{slug}.mp4"
        final_video_path = self.output_dir / out_name

        print(f"🎬 [Renderizado Vectorial] Generando clip ({choreography.get('renderer_type', 'network_flow')}): '{choreography.get('title')}'...")
        video_path = self._render_choreography_to_video(choreography, final_video_path)

        return video_path, choreography

    def _resolve_choreography_with_template(
        self,
        template: MotionTemplate,
        topic: str,
        user_notes: str
    ) -> Dict[str, Any]:
        """Uses surgical prompt with Gemini to populate only the specific selected template schema."""
        self.registry.record_usage(template.id)
        surgical_prompt = self.registry.build_surgical_prompt(template, topic, user_notes)
        prompt_bytes = len(surgical_prompt.encode("utf-8"))
        print(f"   🎯 [Prompt Quirúrgico] Inyección mínima de {prompt_bytes} bytes enviada a Gemini...")

        if self._is_valid_key(self.gemini_key):
            try:
                ai_data = self._call_gemini_json(surgical_prompt, timeout_secs=15)
                if ai_data and ("stages" in ai_data or "etapas" in ai_data):
                    # Normalize stages key
                    if "etapas" in ai_data and "stages" not in ai_data:
                        ai_data["stages"] = ai_data.pop("etapas")
                    ai_data["renderer_type"] = template.renderer_type
                    ai_data["template_id"] = template.id
                    print(f"   ⚡ Gemini pobló con éxito la plantilla '{template.id}'.")
                    return ai_data
            except Exception as e:
                print(f"   ⚠️ Aviso: Gemini API ({e}), usando datos curados de alta fidelidad.")

        # Fallback to template default high-fidelity data adapted to topic
        fallback = json.loads(json.dumps(template.default_example))
        fallback["renderer_type"] = template.renderer_type
        fallback["template_id"] = template.id
        fallback["title"] = f"{template.name}: {topic.title()}"
        return fallback

    def _resolve_organic_new_template(self, topic: str, user_notes: str) -> Dict[str, Any]:
        """Generates a novel animation layout and auto-indexes it into SQLite."""
        prompt = f"""Actúa como Diseñador de Motion Graphics y Arquitecto Cloud.
Crea una nueva plantilla de animación para explicar este tema técnico de Google Cloud: "{topic}".
Devuelve ÚNICAMENTE un JSON con:
{{
  "template_id": "plantilla_{re.sub(r'[^a-z0-9_]', '_', topic.lower()[:20])}",
  "name": "Nombre descriptivo de la plantilla",
  "description": "Descripción visual de qué representa",
  "renderer_type": "network_flow",
  "tags": ["gcp", "{topic.lower()}"],
  "title": "Título corto (máx 6 palabras)",
  "subtitle": "Subtítulo explicativo",
  "nodes": [
    {{"id": 0, "name": "Entrada / Cliente", "type": "client", "subtext": "Origen"}},
    {{"id": 1, "name": "Procesamiento Central", "type": "compute", "subtext": "Lógica de {topic}"}},
    {{"id": 2, "name": "Almacenamiento / Salida", "type": "database", "subtext": "Destino"}}
  ],
  "stages": [
    {{"stage_num": 1, "title": "Fase 1: Inicio", "badge": "INICIAL", "active_node_id": 0, "packet_from": null, "packet_to": null, "metric_label": "Estado", "metric_value": "Reposo", "explanation": "Inicio del flujo de {topic}."}},
    {{"stage_num": 2, "title": "Fase 2: Ejecución Activa", "badge": "EN PROCESO", "active_node_id": 1, "packet_from": 0, "packet_to": 1, "metric_label": "Throughput", "metric_value": "Activo", "explanation": "Procesamiento del evento en tiempo real."}},
    {{"stage_num": 3, "title": "Fase 3: Persistencia y Cierre", "badge": "COMPLETO", "active_node_id": 2, "packet_from": 1, "packet_to": 2, "metric_label": "Resultado", "metric_value": "100% OK", "explanation": "Finalización segura del ciclo."}}
  ]
}}"""

        if self._is_valid_key(self.gemini_key):
            try:
                ai_data = self._call_gemini_json(prompt, timeout_secs=15)
                if ai_data and "stages" in ai_data:
                    # Auto-index into SQLite
                    tpl_id = ai_data.get("template_id", f"plantilla_{re.sub(r'[^a-z0-9_]', '_', topic.lower()[:20])}")
                    self.registry.auto_index_template(
                        template_id=tpl_id,
                        name=ai_data.get("name", f"Plantilla Dinámica de {topic}"),
                        description=ai_data.get("description", f"Animación para {topic}"),
                        tags=ai_data.get("tags", ["gcp", topic.lower()]),
                        schema={"title": "str", "subtitle": "str", "nodes": "list", "stages": "list"},
                        default_example=ai_data,
                        renderer_type=ai_data.get("renderer_type", "network_flow")
                    )
                    return ai_data
            except Exception as e:
                print(f"   ⚠️ Aviso: Error generando nueva plantilla ({e}), usando motor procedimental.")

        # Procedural fallback for novel topic
        default_choreo = {
            "title": f"Arquitectura Dinámica: {topic.title()}",
            "subtitle": "Simulación visual interactiva de componentes",
            "renderer_type": "network_flow",
            "nodes": [
                {"id": 0, "name": "Usuario / Petición", "type": "client", "subtext": "Entrada de tráfico"},
                {"id": 1, "name": f"{topic.title()} Core", "type": "compute", "subtext": "Procesamiento elástico"},
                {"id": 2, "name": "Destino de Datos", "type": "database", "subtext": "Persistencia de alta disponibilidad"}
            ],
            "stages": [
                {
                    "stage_num": 1,
                    "title": "Fase Inicial en Reposo",
                    "badge": "REPOSO",
                    "active_node_id": 0,
                    "packet_from": None,
                    "packet_to": None,
                    "metric_label": "Consumo",
                    "metric_value": "0€ sin actividad",
                    "explanation": f"La infraestructura de {topic} permanece lista sin incurrir en costes innecesarios."
                },
                {
                    "stage_num": 2,
                    "title": "Llegada de Carga y Activación",
                    "badge": "EN EJECUCIÓN",
                    "active_node_id": 1,
                    "packet_from": 0,
                    "packet_to": 1,
                    "metric_label": "Latencia",
                    "metric_value": "Respuesta subsegundo",
                    "explanation": f"Llegan las peticiones y el sistema procesa el flujo de trabajo de {topic}."
                },
                {
                    "stage_num": 3,
                    "title": "Persistencia y Auditoría",
                    "badge": "FINALIZADO",
                    "active_node_id": 2,
                    "packet_from": 1,
                    "packet_to": 2,
                    "metric_label": "Confiabilidad",
                    "metric_value": "99.99% SLA",
                    "explanation": "Los resultados se guardan de forma segura y se genera la métrica de observabilidad."
                }
            ]
        }
        return default_choreo

    def _is_valid_key(self, key: Optional[str]) -> bool:
        if not key or len(key) < 15:
            return False
        return not any(p in key.lower() for p in ["placeholder", "demo", "xxx", "your_key"])

    def _call_gemini_json(self, prompt: str, timeout_secs: int = 15) -> Optional[Dict[str, Any]]:
        """Makes a direct, lightweight JSON call to Gemini Flash."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout_secs) as res:
            data = json.loads(res.read().decode("utf-8"))
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            raw_text = re.sub(r"^```json\s*", "", raw_text)
            raw_text = re.sub(r"\s*```$", "", raw_text)
            return json.loads(raw_text)

    def _render_choreography_to_video(self, choreo: Dict[str, Any], output_path: Path) -> Path:
        """Renders the stages into a sequence of animated SVG frames and compiles to MP4."""
        w, h = self.width, self.height
        frames_dir = self.temp_dir / f"frames_{output_path.stem}"
        frames_dir.mkdir(parents=True, exist_ok=True)

        stages = choreo.get("stages", [])
        renderer_type = choreo.get("renderer_type", "network_flow")

        frame_idx = 0
        frames_per_stage = 15  # 15 frames per stage @ 10 FPS = 1.5s per stage

        for s_idx, stage in enumerate(stages):
            for f_in_stage in range(frames_per_stage):
                progress = f_in_stage / max(1, frames_per_stage - 1)

                if renderer_type == "hierarchy_tree":
                    svg_frame = self._build_hierarchy_tree_svg(
                        choreo=choreo,
                        stage=stage,
                        stage_idx=s_idx,
                        total_stages=len(stages),
                        progress=progress
                    )
                elif renderer_type == "scaling_elastic":
                    svg_frame = self._build_scaling_elastic_svg(
                        choreo=choreo,
                        stage=stage,
                        stage_idx=s_idx,
                        total_stages=len(stages),
                        progress=progress
                    )
                else:
                    # network_flow, storage_lifecycle, iam_security or general
                    svg_frame = self._build_network_flow_svg(
                        choreo=choreo,
                        stage=stage,
                        stage_idx=s_idx,
                        total_stages=len(stages),
                        progress=progress
                    )

                frame_svg = frames_dir / f"frame_{frame_idx:04d}.svg"
                frame_svg.write_text(svg_frame, encoding="utf-8")
                frame_idx += 1

        # Encode direct SVG sequence into super-lightweight MP4 in a single FFmpeg call
        cmd = [
            "ffmpeg", "-y",
            "-r", str(self.fps),
            "-i", str(frames_dir / "frame_%04d.svg"),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", str(self.crf),
            "-tune", "stillimage",
            "-pix_fmt", "yuv420p",
            str(output_path)
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Cleanup SVG frames
        try:
            for f in frames_dir.glob("*.svg"):
                f.unlink(missing_ok=True)
            frames_dir.rmdir()
        except Exception:
            pass

        file_size_kb = output_path.stat().st_size / 1024 if output_path.exists() else 0
        total_dur = frame_idx / self.fps
        print(f"   ✅ Video animado ({renderer_type}) generado con éxito:")
        print(f"      • Archivo: {output_path}")
        print(f"      • Peso: {file_size_kb:.1f} KB (Ultra ligero)")
        print(f"      • Duración: {total_dur:.1f}s @ {self.fps} FPS")

        return output_path

    # =========================================================================
    # RENDERER 1: HIERARCHY TREE (GCP Organization, Folders, Projects, IAM)
    # =========================================================================
    def _build_hierarchy_tree_svg(
        self,
        choreo: Dict[str, Any],
        stage: Dict[str, Any],
        stage_idx: int,
        total_stages: int,
        progress: float
    ) -> str:
        """Renders Google Cloud Resource Hierarchy Tree (Org -> Folders -> Projects)."""
        w, h = self.width, self.height
        title = escape_xml(choreo.get("title", "Estructura Organizacional en Google Cloud"))
        subtitle = escape_xml(choreo.get("subtitle", "Jerarquía de Recursos: Organización > Carpetas > Proyectos"))
        stage_title = escape_xml(stage.get("title", ""))
        stage_badge = escape_xml(stage.get("badge", "HERENCIA"))
        metric_label = escape_xml(stage.get("metric_label", "Nivel"))
        metric_val = escape_xml(stage.get("metric_value", ""))
        explanation = escape_xml(stage.get("explanation", ""))
        active_id = stage.get("active_node_id", 0)

        # Layout node coordinates
        # Level 0 (Org): Center (960, 240)
        # Level 1 (Folders): Left (640, 440), Right (1280, 440)
        # Level 2 (Projects): (420, 650), (860, 650), (1060, 650), (1500, 650)
        nodes = choreo.get("nodes", [])

        # Default fallback structure if needed
        node_pos = {
            0: (960, 230, "org", "Organización (Raíz)"),
            1: (650, 440, "folder", "Carpeta Producción"),
            2: (1270, 440, "folder", "Carpeta Desarrollo"),
            3: (450, 650, "project", "Proyecto Backend"),
            4: (850, 650, "project", "Proyecto Frontend"),
            5: (1270, 650, "project", "Proyecto Sandbox")
        }

        # Hierarchy connecting branches
        branches = [
            # Org to Folders
            ("M 960 280 L 960 350 L 650 350 L 650 395", 0, 1),
            ("M 960 280 L 960 350 L 1270 350 L 1270 395", 0, 2),
            # Folder 1 to Projects 3 and 4
            ("M 650 485 L 650 560 L 450 560 L 450 610", 1, 3),
            ("M 650 485 L 650 560 L 850 560 L 850 610", 1, 4),
            # Folder 2 to Project 5
            ("M 1270 485 L 1270 610", 2, 5),
        ]

        branches_svg = ""
        for path_d, p_from, p_to in branches:
            is_branch_active = (active_id == p_to or (active_id == p_from and progress > 0.4))
            line_col = "#00F0FF" if is_branch_active else "#334155"
            line_w = 4 if is_branch_active else 2.5
            glow = 'filter="url(#glow)"' if is_branch_active else ""
            branches_svg += f"""<path d="{path_d}" fill="none" stroke="{line_col}" stroke-width="{line_w}" stroke-linecap="round" stroke-linejoin="round" {glow}/>\n"""

        # Render Nodes
        nodes_svg = ""
        for n_idx, (nx, ny, default_type, default_name) in node_pos.items():
            n_data = next((n for n in nodes if n.get("id") == n_idx), None)
            name = escape_xml(n_data.get("name") if n_data else default_name)
            sub = escape_xml(n_data.get("subtext") if n_data else "")
            ntype = n_data.get("type", default_type) if n_data else default_type

            is_active = (n_idx == active_id)

            if ntype == "org":
                nw, nh = 360, 95
                bg_col = "#1E293B" if not is_active else "#1E3A8A"
                border_col = "#F59E0B" if not is_active else "#00F0FF"
                badge_bg = "#F59E0B"
                badge_text = "🏢 NODO RAÍZ (ORGANIZACIÓN)"
            elif ntype == "folder":
                nw, nh = 290, 85
                bg_col = "#0F172A" if not is_active else "#172554"
                border_col = "#38BDF8" if not is_active else "#00F0FF"
                badge_bg = "#0284C7"
                badge_text = "📁 CARPETA (ENTORNO)"
            else:
                nw, nh = 250, 75
                bg_col = "#0B1120" if not is_active else "#162035"
                border_col = "#64748B" if not is_active else "#34D399"
                badge_bg = "#059669"
                badge_text = "📦 PROYECTO (AISLADO)"

            glow_effect = 'filter="url(#glow)"' if is_active else ""
            active_beacon = ""
            if is_active:
                active_beacon = f"""
                <circle cx="{nw - 20}" cy="20" r="6" fill="#10B981"/>
                <circle cx="{nw - 20}" cy="20" r="14" fill="#10B981" opacity="{0.4 * (1.0 - progress)}"/>
                """

            nodes_svg += f"""
            <g transform="translate({nx - nw/2}, {ny - nh/2})" {glow_effect}>
              <rect x="0" y="0" width="{nw}" height="{nh}" rx="14" fill="{bg_col}" stroke="{border_col}" stroke-width="{3 if is_active else 1.5}"/>
              <rect x="14" y="10" width="160" height="20" rx="5" fill="{badge_bg}" opacity="0.9"/>
              <text x="94" y="24" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="9" font-weight="bold" text-anchor="middle">{badge_text}</text>
              {active_beacon}
              <text x="16" y="52" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="16" font-weight="bold">{name}</text>
              <text x="16" y="72" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="12">{sub}</text>
            </g>
            """

        overall_progress = (stage_idx + progress) / total_stages
        progress_bar_w = (w - 240) * overall_progress

        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <linearGradient id="bgMotion" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#050811"/>
      <stop offset="50%" stop-color="#0B132B"/>
      <stop offset="100%" stop-color="#111B38"/>
    </linearGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="0" stdDeviation="12" flood-color="#00F0FF" flood-opacity="0.7"/>
    </filter>
  </defs>

  <rect width="{w}" height="{h}" fill="url(#bgMotion)"/>
  
  <!-- Top Progress Bar -->
  <rect x="120" y="30" width="{w - 240}" height="6" rx="3" fill="#1E293B"/>
  <rect x="120" y="30" width="{progress_bar_w}" height="6" rx="3" fill="#00F0FF"/>

  <!-- Header -->
  <g transform="translate(120, 65)">
    <rect x="0" y="0" width="310" height="28" rx="14" fill="#1E3A8A" stroke="#38BDF8" stroke-width="1.5"/>
    <text x="155" y="19" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">
      🏛️ ARQUITECTURA JERÁRQUICA DE GCP
    </text>
    <text x="0" y="65" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="34" font-weight="bold">
      {title}
    </text>
    <text x="0" y="94" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="16">
      {subtitle}
    </text>
  </g>

  <!-- Hierarchy Tree Elements -->
  {branches_svg}
  {nodes_svg}

  <!-- Bottom Stage HUD -->
  <g transform="translate(120, {h - 180})">
    <rect x="0" y="0" width="{w - 240}" height="120" rx="16" fill="#091122" stroke="#1E293B" stroke-width="2"/>
    <rect x="24" y="24" width="220" height="28" rx="8" fill="#0284C7"/>
    <text x="134" y="42" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="12" font-weight="bold" text-anchor="middle">
      ETAPA {stage_idx + 1}/{total_stages}: {stage_badge}
    </text>
    <text x="265" y="44" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="20" font-weight="bold">
      {stage_title}
    </text>
    <text x="24" y="86" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="16">
      {explanation}
    </text>
    <g transform="translate({w - 240 - 320}, 20)">
      <rect x="0" y="0" width="300" height="80" rx="10" fill="#131F38" stroke="#38BDF8" stroke-width="1.5"/>
      <text x="16" y="28" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="12" font-weight="bold">
        {metric_label.upper()}
      </text>
      <text x="16" y="60" fill="#34D399" font-family="'Liberation Sans', sans-serif" font-size="18" font-weight="bold">
        {metric_val}
      </text>
    </g>
  </g>
</svg>"""

    # =========================================================================
    # RENDERER 2: SCALING ELASTIC (Cloud Run, Serverless, Concurrency)
    # =========================================================================
    def _build_scaling_elastic_svg(
        self,
        choreo: Dict[str, Any],
        stage: Dict[str, Any],
        stage_idx: int,
        total_stages: int,
        progress: float
    ) -> str:
        """Renders Serverless elastic scaling from 0 to N container instances."""
        w, h = self.width, self.height
        title = escape_xml(choreo.get("title", "Cloud Run: Escalado Automático"))
        subtitle = escape_xml(choreo.get("subtitle", "Elasticidad Serverless de Cero a Infinito"))
        stage_title = escape_xml(stage.get("title", ""))
        stage_badge = escape_xml(stage.get("badge", "ESCALADO"))
        metric_label = escape_xml(stage.get("metric_label", "Instancias"))
        metric_val = escape_xml(stage.get("metric_value", ""))
        explanation = escape_xml(stage.get("explanation", ""))
        instances = stage.get("instances_count", stage_idx)

        overall_progress = (stage_idx + progress) / total_stages
        progress_bar_w = (w - 240) * overall_progress

        # Container pods visualization
        pods_svg = ""
        pod_w, pod_h = 240, 180
        pod_coords = [(600, 480), (960, 480), (1320, 480)]

        for i, (px, py) in enumerate(pod_coords):
            is_pod_active = (i < instances)
            pulse = 1.0 + 0.05 * math.sin(progress * math.pi) if is_pod_active else 1.0

            if is_pod_active:
                pod_bg = "#172554"
                pod_border = "#00F0FF"
                pod_status = "🟢 ACTIVO (HTTP 200)"
                pod_metric = f"Pod #{i+1} • 80 Concurrencia"
                glow = 'filter="url(#glow)"'
            else:
                pod_bg = "#0B1120"
                pod_border = "#334155"
                pod_status = "⚪ APAGADO (0.00€ Coste)"
                pod_metric = "Recurso en reposo"
                glow = ""

            pods_svg += f"""
            <g transform="translate({px - pod_w/2}, {py - pod_h/2})" {glow}>
              <rect x="0" y="0" width="{pod_w}" height="{pod_h}" rx="16" fill="{pod_bg}" stroke="{pod_border}" stroke-width="{3 if is_pod_active else 1}"/>
              <rect x="18" y="16" width="130" height="22" rx="6" fill="#0284C7" opacity="{0.9 if is_pod_active else 0.3}"/>
              <text x="83" y="31" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="10" font-weight="bold" text-anchor="middle">
                CONTENEDOR #{i+1}
              </text>
              <text x="18" y="80" fill="{ '#34D399' if is_pod_active else '#64748B'}" font-family="'Liberation Sans', sans-serif" font-size="14" font-weight="bold">
                {pod_status}
              </text>
              <text x="18" y="115" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="18" font-weight="bold">
                Instancia Cloud Run
              </text>
              <text x="18" y="145" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="13">
                {pod_metric}
              </text>
            </g>
            """

        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <linearGradient id="bgMotion" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#050811"/>
      <stop offset="50%" stop-color="#0B132B"/>
      <stop offset="100%" stop-color="#111B38"/>
    </linearGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="0" stdDeviation="12" flood-color="#00F0FF" flood-opacity="0.7"/>
    </filter>
  </defs>

  <rect width="{w}" height="{h}" fill="url(#bgMotion)"/>
  <rect x="120" y="30" width="{w - 240}" height="6" rx="3" fill="#1E293B"/>
  <rect x="120" y="30" width="{progress_bar_w}" height="6" rx="3" fill="#00F0FF"/>

  <g transform="translate(120, 65)">
    <rect x="0" y="0" width="310" height="28" rx="14" fill="#1E3A8A" stroke="#38BDF8" stroke-width="1.5"/>
    <text x="155" y="19" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">
      🚀 ESCALADO SERVERLESS EN TIEMPO REAL
    </text>
    <text x="0" y="65" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="34" font-weight="bold">
      {title}
    </text>
    <text x="0" y="94" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="16">
      {subtitle}
    </text>
  </g>

  <!-- Container Pods -->
  {pods_svg}

  <!-- Bottom Stage HUD -->
  <g transform="translate(120, {h - 180})">
    <rect x="0" y="0" width="{w - 240}" height="120" rx="16" fill="#091122" stroke="#1E293B" stroke-width="2"/>
    <rect x="24" y="24" width="220" height="28" rx="8" fill="#0284C7"/>
    <text x="134" y="42" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="12" font-weight="bold" text-anchor="middle">
      ETAPA {stage_idx + 1}/{total_stages}: {stage_badge}
    </text>
    <text x="265" y="44" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="20" font-weight="bold">
      {stage_title}
    </text>
    <text x="24" y="86" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="16">
      {explanation}
    </text>
    <g transform="translate({w - 240 - 320}, 20)">
      <rect x="0" y="0" width="300" height="80" rx="10" fill="#131F38" stroke="#38BDF8" stroke-width="1.5"/>
      <text x="16" y="28" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="12" font-weight="bold">
        {metric_label.upper()}
      </text>
      <text x="16" y="60" fill="#34D399" font-family="'Liberation Sans', sans-serif" font-size="18" font-weight="bold">
        {metric_val}
      </text>
    </g>
  </g>
</svg>"""

    # =========================================================================
    # RENDERER 3: NETWORK FLOW & DATA PACKETS (PubSub, VPC, Cloud Storage, IAM)
    # =========================================================================
    def _build_network_flow_svg(
        self,
        choreo: Dict[str, Any],
        stage: Dict[str, Any],
        stage_idx: int,
        total_stages: int,
        progress: float
    ) -> str:
        """Constructs an individual SVG frame with pulsing energy and flowing data packets."""
        w, h = self.width, self.height
        title = escape_xml(choreo.get("title", "Simulación Visual GCP"))
        subtitle = escape_xml(choreo.get("subtitle", "Animación Conceptual Generada con IA"))
        stage_title = escape_xml(stage.get("title", ""))
        stage_badge = escape_xml(stage.get("badge", "EN PROCESO"))
        metric_label = escape_xml(stage.get("metric_label", "Métrica"))
        metric_val = escape_xml(stage.get("metric_value", ""))
        explanation = escape_xml(stage.get("explanation", ""))
        nodes = choreo.get("nodes", [])
        active_node_id = stage.get("active_node_id", 0)
        pkt_from = stage.get("packet_from")
        pkt_to = stage.get("packet_to")

        # Calculate node coordinates across the canvas
        node_coords = []
        n_nodes = len(nodes)
        spacing = (w - 240) / max(1, n_nodes - 1)
        for i in range(n_nodes):
            nx = 120 + i * spacing
            ny = h / 2 - 20
            node_coords.append((nx, ny))

        # Connection lines between nodes
        connections_svg = ""
        for i in range(len(node_coords) - 1):
            x1, y1 = node_coords[i]
            x2, y2 = node_coords[i + 1]
            connections_svg += f"""
            <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1E293B" stroke-width="6" stroke-linecap="round"/>
            <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#334155" stroke-width="2" stroke-dasharray="8,8"/>
            """

        # Animated Traveling Data Packet (Energy Pulse)
        packet_svg = ""
        if pkt_from is not None and pkt_to is not None and 0 <= pkt_from < len(node_coords) and 0 <= pkt_to < len(node_coords):
            fx, fy = node_coords[pkt_from]
            tx, ty = node_coords[pkt_to]
            cur_x = fx + (tx - fx) * progress
            cur_y = fy + (ty - fy) * progress
            pulse_size = 14 + 4 * (0.5 - abs(progress - 0.5))

            packet_svg = f"""
            <!-- Traveling Packet Pulse -->
            <g transform="translate({cur_x}, {cur_y})">
              <circle cx="0" cy="0" r="{pulse_size * 2}" fill="#38BDF8" opacity="0.25" filter="url(#glow)"/>
              <circle cx="0" cy="0" r="{pulse_size}" fill="#00F0FF" stroke="#FFFFFF" stroke-width="2"/>
              <text x="0" y="4" fill="#000000" font-family="'Liberation Sans', sans-serif" font-size="9" font-weight="bold" text-anchor="middle">DATA</text>
            </g>
            """

        # Render Nodes (Servers / Clients / Storage)
        nodes_svg = ""
        card_w, card_h = 240, 160
        for i, (node, (nx, ny)) in enumerate(zip(nodes, node_coords)):
            is_active = (i == active_node_id)
            node_name = escape_xml(node.get("name", f"Nodo {i+1}"))
            node_sub = escape_xml(node.get("subtext", ""))
            ntype = node.get("type", "compute")

            theme_col = "#4285F4"
            if ntype == "security":
                theme_col = "#EA4335"
            elif ntype == "database":
                theme_col = "#FBBC05"
            elif ntype == "client":
                theme_col = "#38BDF8"

            card_border = "#00F0FF" if is_active else theme_col
            card_fill = "#17233D" if is_active else "#0B1120"
            border_w = 3.5 if is_active else 1.5
            glow_attr = 'filter="url(#glow)"' if is_active else ""

            active_beacon = ""
            if is_active:
                active_beacon = f"""
                <circle cx="{card_w - 24}" cy="24" r="7" fill="#10B981"/>
                <circle cx="{card_w - 24}" cy="24" r="14" fill="#10B981" opacity="{0.4 * (1.0 - progress)}"/>
                """

            nodes_svg += f"""
            <g transform="translate({nx - card_w/2}, {ny - card_h/2})" {glow_attr}>
              <rect x="0" y="0" width="{card_w}" height="{card_h}" rx="16" fill="{card_fill}" stroke="{card_border}" stroke-width="{border_w}"/>
              <rect x="18" y="16" width="70" height="22" rx="6" fill="{theme_col}" opacity="0.25"/>
              <text x="53" y="31" fill="{theme_col}" font-family="'Liberation Sans', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">
                {ntype.upper()}
              </text>
              {active_beacon}
              <text x="18" y="80" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="19" font-weight="bold">
                {node_name}
              </text>
              <text x="18" y="112" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="13">
                {node_sub}
              </text>
            </g>
            """

        overall_progress = (stage_idx + progress) / total_stages
        progress_bar_w = (w - 240) * overall_progress

        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <linearGradient id="bgMotion" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070A12"/>
      <stop offset="50%" stop-color="#0E1628"/>
      <stop offset="100%" stop-color="#121D36"/>
    </linearGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="0" stdDeviation="12" flood-color="#00F0FF" flood-opacity="0.6"/>
    </filter>
  </defs>

  <rect width="{w}" height="{h}" fill="url(#bgMotion)"/>
  <rect x="120" y="30" width="{w - 240}" height="6" rx="3" fill="#1E293B"/>
  <rect x="120" y="30" width="{progress_bar_w}" height="6" rx="3" fill="#00F0FF"/>

  <g transform="translate(120, 70)">
    <rect x="0" y="0" width="260" height="30" rx="15" fill="#1E3A8A" stroke="#38BDF8" stroke-width="1.5"/>
    <text x="130" y="20" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="12" font-weight="bold" text-anchor="middle">
      ⚡ ANIMACIÓN TÉCNICA EN VIVO
    </text>
    <text x="0" y="70" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="36" font-weight="bold">
      {title}
    </text>
    <text x="0" y="102" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="18">
      {subtitle}
    </text>
  </g>

  {connections_svg}
  {packet_svg}
  {nodes_svg}

  <g transform="translate(120, {h - 180})">
    <rect x="0" y="0" width="{w - 240}" height="120" rx="16" fill="#091122" stroke="#1E293B" stroke-width="2"/>
    <rect x="24" y="24" width="200" height="28" rx="8" fill="#0284C7"/>
    <text x="124" y="42" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="13" font-weight="bold" text-anchor="middle">
      FASE {stage_idx + 1}/{total_stages}: {stage_badge}
    </text>
    <text x="245" y="44" fill="#FFFFFF" font-family="'Liberation Sans', sans-serif" font-size="20" font-weight="bold">
      {stage_title}
    </text>
    <text x="24" y="86" fill="#94A3B8" font-family="'Liberation Sans', sans-serif" font-size="16">
      {explanation}
    </text>
    <g transform="translate({w - 240 - 320}, 20)">
      <rect x="0" y="0" width="300" height="80" rx="10" fill="#131F38" stroke="#38BDF8" stroke-width="1.5"/>
      <text x="16" y="28" fill="#38BDF8" font-family="'Liberation Sans', sans-serif" font-size="12" font-weight="bold">
        {metric_label.upper()}
      </text>
      <text x="16" y="60" fill="#34D399" font-family="'Liberation Sans', sans-serif" font-size="18" font-weight="bold">
        {metric_val}
      </text>
    </g>
  </g>
</svg>"""
