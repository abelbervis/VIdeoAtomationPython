"""
High-Resolution Slide Renderer for GCP NotebookLM Tutorials.
Generates pixel-perfect SVG vector graphics and renders them to HD/4K PNG images via FFmpeg librsvg.
Supports both horizontal (1920x1080) and vertical (1080x1920) layouts.
"""

import html
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import TEMP_DIR, OUTPUT_DIR


def escape_xml(text: str) -> str:
    """Escapes special XML/SVG characters."""
    return html.escape(str(text))


class GCPSlideRenderer:
    """Renders high-tech, publication-ready Google Cloud slides as SVG and PNG."""

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self.is_vertical = height > width

    def render_slide_svg(
        self,
        slide: Dict[str, Any],
        active_speaker: Optional[str] = "Alex",
        current_slide_num: int = 1,
        total_slides: int = 5,
        series_category: str = "Google Cloud • Architecture Series"
    ) -> str:
        """Generates clean, scalable SVG markup for a given slide definition."""
        w, h = self.width, self.height
        layout = slide.get("layout", "concept_card")
        badge = escape_xml(slide.get("badge", "Google Cloud"))
        title = escape_xml(slide.get("title", "Concepto Técnico"))
        subtitle = escape_xml(slide.get("subtitle", "Detalle arquitectónico"))

        # Determine speaker active states
        speaker_name = (active_speaker or "Alex").strip().capitalize()
        is_alex_active = "alex" in speaker_name.lower()
        is_sam_active = "sam" in speaker_name.lower()

        alex_card_stroke = "#4285F4" if is_alex_active else "#334155"
        alex_card_fill = "#1E293B" if is_alex_active else "#0F172A"
        alex_wave_display = "block" if is_alex_active else "none"

        sam_card_stroke = "#34A853" if is_sam_active else "#334155"
        sam_card_fill = "#1E293B" if is_sam_active else "#0F172A"
        sam_wave_display = "block" if is_sam_active else "none"

        # Content area builder based on layout
        content_svg = self._build_layout_content_svg(slide, layout)

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
  <defs>
    <!-- Background Gradient -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B0F19"/>
      <stop offset="50%" stop-color="#0F172A"/>
      <stop offset="100%" stop-color="#141E33"/>
    </linearGradient>

    <!-- Neon Accents -->
    <linearGradient id="gcpGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#4285F4"/>
      <stop offset="35%" stop-color="#34A853"/>
      <stop offset="70%" stop-color="#FBBC05"/>
      <stop offset="100%" stop-color="#EA4335"/>
    </linearGradient>

    <linearGradient id="blueGlow" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#0284C7" stop-opacity="0.05"/>
    </linearGradient>

    <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#000000" flood-opacity="0.5"/>
    </filter>

    <filter id="activeGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Canvas Background -->
  <rect width="{w}" height="{h}" fill="url(#bgGrad)"/>

  <!-- Subtle Top Decorative Rainbow Glow Bar -->
  <rect x="0" y="0" width="{w}" height="4" fill="url(#gcpGrad)"/>

  <!-- HEADER SECTION -->
  <g id="header" transform="translate(60, 45)">
    <!-- GCP Badge -->
    <rect x="0" y="0" width="310" height="34" rx="17" fill="#1E293B" stroke="#4285F4" stroke-width="1.5"/>
    <circle cx="18" cy="17" r="7" fill="#4285F4"/>
    <text x="34" y="23" fill="#E2E8F0" font-family="'DejaVu Sans', sans-serif" font-size="13" font-weight="bold" letter-spacing="1">
      {escape_xml(series_category.upper())}
    </text>

    <!-- Slide Category Tag & Counter -->
    <rect x="{w - 380}" y="0" width="260" height="34" rx="17" fill="#1E293B" stroke="#334155" stroke-width="1.2"/>
    <text x="{w - 250}" y="22" fill="#38BDF8" font-family="'DejaVu Sans', sans-serif" font-size="13" font-weight="bold" text-anchor="middle">
      {badge.upper()} • {current_slide_num:02d}/{total_slides:02d}
    </text>

    <!-- Main Slide Title & Subtitle -->
    <text x="0" y="95" fill="#FFFFFF" font-family="'DejaVu Sans', sans-serif" font-size="38" font-weight="bold">
      {title}
    </text>
    <text x="0" y="132" fill="#94A3B8" font-family="'DejaVu Sans', sans-serif" font-size="20">
      {subtitle}
    </text>
  </g>

  <!-- MAIN DYNAMIC CONTENT CANVAS -->
  <g id="content" transform="translate(60, 215)">
    {content_svg}
  </g>

  <!-- FOOTER: NOTEBOOK LM CO-HOSTS STATUS BAR -->
  <g id="footer" transform="translate(60, {h - 110})">
    <rect x="0" y="0" width="{w - 120}" height="76" rx="16" fill="#0B132B" stroke="#1E293B" stroke-width="1.5"/>

    <!-- Left Host (Alex - Architect) -->
    <g transform="translate(20, 12)">
      <rect x="0" y="0" width="380" height="52" rx="12" fill="{alex_card_fill}" stroke="{alex_card_stroke}" stroke-width="{2 if is_alex_active else 1}"/>
      <circle cx="28" cy="26" r="14" fill="#1D4ED8"/>
      <text x="28" y="31" fill="#FFFFFF" font-family="'DejaVu Sans', sans-serif" font-size="14" font-weight="bold" text-anchor="middle">A</text>
      <text x="52" y="24" fill="#FFFFFF" font-family="'DejaVu Sans', sans-serif" font-size="15" font-weight="bold">Alex</text>
      <text x="52" y="42" fill="#60A5FA" font-family="'DejaVu Sans', sans-serif" font-size="12">Cloud Solutions Architect</text>
      
      <!-- Voice Wave / Speaking Indicator -->
      <g transform="translate(300, 16)" style="display: {alex_wave_display};">
        <rect x="0" y="6" width="3" height="12" rx="1.5" fill="#60A5FA"/>
        <rect x="7" y="2" width="3" height="18" rx="1.5" fill="#60A5FA"/>
        <rect x="14" y="0" width="3" height="22" rx="1.5" fill="#38BDF8"/>
        <rect x="21" y="4" width="3" height="15" rx="1.5" fill="#60A5FA"/>
        <rect x="28" y="8" width="3" height="9" rx="1.5" fill="#60A5FA"/>
        <text x="40" y="16" fill="#38BDF8" font-family="'DejaVu Sans', sans-serif" font-size="11" font-weight="bold">HABLANDO</text>
      </g>
    </g>

    <!-- Center Label -->
    <text x="{(w - 120) / 2}" y="44" fill="#64748B" font-family="'DejaVu Sans', sans-serif" font-size="12" font-weight="bold" letter-spacing="2" text-anchor="middle">
      🎙️ NOTEBOOK LM • DEEP DIVE DISCUSSION
    </text>

    <!-- Right Host (Sam - DevOps) -->
    <g transform="translate({w - 120 - 400}, 12)">
      <rect x="0" y="0" width="380" height="52" rx="12" fill="{sam_card_fill}" stroke="{sam_card_stroke}" stroke-width="{2 if is_sam_active else 1}"/>
      <circle cx="28" cy="26" r="14" fill="#047857"/>
      <text x="28" y="31" fill="#FFFFFF" font-family="'DejaVu Sans', sans-serif" font-size="14" font-weight="bold" text-anchor="middle">S</text>
      <text x="52" y="24" fill="#FFFFFF" font-family="'DejaVu Sans', sans-serif" font-size="15" font-weight="bold">Sam</text>
      <text x="52" y="42" fill="#34D399" font-family="'DejaVu Sans', sans-serif" font-size="12">Senior DevOps Engineer</text>
      
      <!-- Voice Wave / Speaking Indicator -->
      <g transform="translate(300, 16)" style="display: {sam_wave_display};">
        <rect x="0" y="6" width="3" height="12" rx="1.5" fill="#34D399"/>
        <rect x="7" y="2" width="3" height="18" rx="1.5" fill="#34D399"/>
        <rect x="14" y="0" width="3" height="22" rx="1.5" fill="#4ADE80"/>
        <rect x="21" y="4" width="3" height="15" rx="1.5" fill="#34D399"/>
        <rect x="28" y="8" width="3" height="9" rx="1.5" fill="#34D399"/>
        <text x="40" y="16" fill="#34D399" font-family="'DejaVu Sans', sans-serif" font-size="11" font-weight="bold">HABLANDO</text>
      </g>
    </g>
  </g>
</svg>"""
        return svg

    def _build_layout_content_svg(self, slide: Dict[str, Any], layout: str) -> str:
        """Constructs layout-specific vector graphics."""
        canvas_w = self.width - 120
        canvas_h = self.height - 350

        if layout == "architecture_flow":
            return self._build_architecture_flow(slide, canvas_w, canvas_h)
        elif layout == "comparison_table":
            return self._build_comparison_table(slide, canvas_w, canvas_h)
        elif layout == "terminal_code":
            return self._build_terminal_code(slide, canvas_w, canvas_h)
        elif layout == "hierarchy_tree":
            return self._build_hierarchy_tree(slide, canvas_w, canvas_h)
        else:
            return self._build_concept_card(slide, canvas_w, canvas_h)

    def _build_concept_card(self, slide: Dict[str, Any], w: int, h: int) -> str:
        concept_title = escape_xml(slide.get("concept_title", "Punto Central"))
        bullet_points = slide.get("bullet_points", [])
        callout = escape_xml(slide.get("callout_box", ""))

        bullets_svg = ""
        y_offset = 120
        for i, bp in enumerate(bullet_points[:4]):
            bullets_svg += f"""
            <g transform="translate(40, {y_offset})">
              <circle cx="16" cy="12" r="10" fill="#0369A1" stroke="#38BDF8" stroke-width="2"/>
              <text x="16" y="16" fill="#FFFFFF" font-family="'DejaVu Sans', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">✓</text>
              <text x="42" y="18" fill="#F1F5F9" font-family="'DejaVu Sans', sans-serif" font-size="21" font-weight="500">
                {escape_xml(bp)}
              </text>
            </g>"""
            y_offset += 65

        callout_svg = ""
        if callout:
            callout_svg = f"""
            <g transform="translate(40, {h - 130})">
              <rect x="0" y="0" width="{w - 80}" height="90" rx="12" fill="#1E293B" stroke="#F59E0B" stroke-width="1.8"/>
              <rect x="0" y="0" width="8" height="90" rx="4" fill="#F59E0B"/>
              <text x="28" y="36" fill="#FDE68A" font-family="'DejaVu Sans', sans-serif" font-size="14" font-weight="bold">PRO-TIP DE ARQUITECTURA OFICIAL</text>
              <text x="28" y="66" fill="#F1F5F9" font-family="'DejaVu Sans', sans-serif" font-size="18">
                {callout}
              </text>
            </g>"""

        return f"""
        <rect x="0" y="0" width="{w}" height="{h}" rx="20" fill="#0F172A" stroke="#1E293B" stroke-width="2" filter="url(#cardShadow)"/>
        
        <!-- Header Ribbon inside Card -->
        <rect x="40" y="35" width="220" height="34" rx="8" fill="#0369A1" opacity="0.3"/>
        <text x="54" y="58" fill="#38BDF8" font-family="'DejaVu Sans', sans-serif" font-size="14" font-weight="bold" letter-spacing="1">
          ANÁLISIS PROFUNDO
        </text>

        <text x="40" y="100" fill="#FFFFFF" font-family="'DejaVu Sans', sans-serif" font-size="28" font-weight="bold">
          {concept_title}
        </text>

        {bullets_svg}
        {callout_svg}
        """

    def _build_comparison_table(self, slide: Dict[str, Any], w: int, h: int) -> str:
        headers = slide.get("headers", ["Criterio", "Opción A", "Opción B"])
        rows = slide.get("rows", [])

        col_w = w / len(headers)
        
        # Header Row
        header_cols_svg = ""
        for i, header in enumerate(headers):
            bg_fill = "#1E293B" if i == 0 else ("#1E3A8A" if i == 1 else "#14532D")
            border_color = "#38BDF8" if i == 1 else ("#4ADE80" if i == 2 else "#475569")
            header_cols_svg += f"""
            <rect x="{i * col_w}" y="0" width="{col_w - 6}" height="64" rx="10" fill="{bg_fill}" stroke="{border_color}" stroke-width="1.5"/>
            <text x="{i * col_w + col_w / 2}" y="40" fill="#FFFFFF" font-family="'DejaVu Sans', sans-serif" font-size="20" font-weight="bold" text-anchor="middle">
              {escape_xml(header)}
            </text>"""

        # Data Rows
        rows_svg = ""
        row_y = 80
        for r_idx, row in enumerate(rows[:5]):
            row_fill = "#0F172A" if r_idx % 2 == 0 else "#162032"
            for c_idx, cell in enumerate(row):
                text_color = "#E2E8F0" if c_idx == 0 else ("#38BDF8" if c_idx == 1 else "#FBBF24")
                rows_svg += f"""
                <rect x="{c_idx * col_w}" y="{row_y}" width="{col_w - 6}" height="62" rx="8" fill="{row_fill}" stroke="#1E293B" stroke-width="1"/>
                <text x="{c_idx * col_w + 24}" y="{row_y + 38}" fill="{text_color}" font-family="'DejaVu Sans', sans-serif" font-size="18">
                  {escape_xml(str(cell))}
                </text>"""
            row_y += 72

        return f"""
        <g id="table_container">
          <g id="table_headers">{header_cols_svg}</g>
          <g id="table_rows">{rows_svg}</g>
        </g>
        """

    def _build_architecture_flow(self, slide: Dict[str, Any], w: int, h: int) -> str:
        steps = slide.get("steps", [])
        n_steps = len(steps)
        if n_steps == 0:
            return ""

        card_w = min(280, (w - (n_steps * 50)) / n_steps)
        card_h = 240
        card_y = (h - card_h) / 2 - 20

        steps_svg = ""
        for i, step in enumerate(steps):
            x = 30 + i * (card_w + 60)
            name = escape_xml(step.get("name", f"Paso {i+1}"))
            desc = escape_xml(step.get("desc", ""))
            stype = step.get("type", "compute")

            # Theme color by type
            theme_color = "#4285F4"
            if stype == "security":
                theme_color = "#EA4335"
            elif stype == "database":
                theme_color = "#FBBC05"
            elif stype == "network":
                theme_color = "#34A853"
            elif stype == "client":
                theme_color = "#38BDF8"

            steps_svg += f"""
            <!-- Step Card {i+1} -->
            <g transform="translate({x}, {card_y})">
              <rect x="0" y="0" width="{card_w}" height="{card_h}" rx="16" fill="#0F172A" stroke="{theme_color}" stroke-width="2" filter="url(#cardShadow)"/>
              
              <!-- Badge -->
              <rect x="20" y="24" width="80" height="24" rx="6" fill="{theme_color}" opacity="0.25"/>
              <text x="60" y="40" fill="{theme_color}" font-family="'DejaVu Sans', sans-serif" font-size="11" font-weight="bold" text-anchor="middle">
                {stype.upper()}
              </text>

              <!-- Node Title -->
              <text x="20" y="100" fill="#FFFFFF" font-family="'DejaVu Sans', sans-serif" font-size="22" font-weight="bold">
                {name}
              </text>

              <!-- Node Description -->
              <rect x="20" y="130" width="{card_w - 40}" height="70" rx="8" fill="#1E293B"/>
              <text x="32" y="172" fill="#94A3B8" font-family="'DejaVu Sans', sans-serif" font-size="15">
                {desc}
              </text>
            </g>"""

            # Connector Arrow to next step
            if i < n_steps - 1:
                arrow_x = x + card_w + 8
                arrow_y = card_y + card_h / 2
                steps_svg += f"""
                <g transform="translate({arrow_x}, {arrow_y})">
                  <line x1="0" y1="0" x2="40" y2="0" stroke="#38BDF8" stroke-width="3" stroke-dasharray="6,4"/>
                  <polygon points="38,-7 50,0 38,7" fill="#38BDF8"/>
                </g>"""

        return f"""
        <rect x="0" y="0" width="{w}" height="{h}" rx="20" fill="#070B14" stroke="#1E293B" stroke-width="1.5"/>
        <g id="flow_pipeline">{steps_svg}</g>
        """

    def _build_terminal_code(self, slide: Dict[str, Any], w: int, h: int) -> str:
        win_title = escape_xml(slide.get("window_title", "bash - gcloud"))
        code_lines = slide.get("code_lines", [])
        explanation = escape_xml(slide.get("explanation", ""))

        code_text_svg = ""
        line_y = 80
        for line in code_lines[:8]:
            escaped_line = escape_xml(line)
            line_color = "#38BDF8" if escaped_line.startswith("$") else ("#64748B" if escaped_line.startswith("#") else "#F8FAFC")
            code_text_svg += f"""
            <text x="40" y="{line_y}" fill="{line_color}" font-family="'DejaVu Sans Mono', 'Liberation Mono', monospace" font-size="19">
              {escaped_line}
            </text>"""
            line_y += 34

        return f"""
        <g id="terminal_window">
          <!-- Terminal Box -->
          <rect x="0" y="0" width="{w}" height="{h - 100}" rx="14" fill="#050811" stroke="#334155" stroke-width="2" filter="url(#cardShadow)"/>
          
          <!-- Title Bar -->
          <rect x="0" y="0" width="{w}" height="44" rx="14" fill="#0F172A"/>
          <circle cx="28" cy="22" r="7" fill="#EF4444"/>
          <circle cx="50" cy="22" r="7" fill="#F59E0B"/>
          <circle cx="72" cy="22" r="7" fill="#10B981"/>
          
          <text x="{w / 2}" y="28" fill="#94A3B8" font-family="'DejaVu Sans', sans-serif" font-size="14" font-weight="bold" text-anchor="middle">
            {win_title}
          </text>

          <!-- Monospace Code Body -->
          {code_text_svg}

          <!-- Explanation Callout below -->
          <rect x="0" y="{h - 80}" width="{w}" height="70" rx="12" fill="#1E293B" stroke="#38BDF8" stroke-width="1.5"/>
          <text x="30" y="{h - 38}" fill="#38BDF8" font-family="'DejaVu Sans', sans-serif" font-size="18" font-weight="500">
            💡 {explanation}
          </text>
        </g>
        """

    def _build_hierarchy_tree(self, slide: Dict[str, Any], w: int, h: int) -> str:
        nodes = slide.get("nodes", [])
        rule = escape_xml(slide.get("rule", ""))

        nodes_svg = ""
        box_w = 420
        box_h = 56
        y = 30
        for i, node in enumerate(nodes[:5]):
            x = (w - box_w) / 2
            border_c = "#4285F4" if i == 0 else ("#34A853" if i == 1 else ("#FBBC05" if i == 2 else "#EA4335"))
            nodes_svg += f"""
            <g transform="translate({x}, {y})">
              <rect x="0" y="0" width="{box_w}" height="{box_h}" rx="10" fill="#0F172A" stroke="{border_c}" stroke-width="2"/>
              <text x="{box_w / 2}" y="36" fill="#FFFFFF" font-family="'DejaVu Sans', sans-serif" font-size="18" font-weight="bold" text-anchor="middle">
                {escape_xml(node)}
              </text>
            </g>"""
            if i < len(nodes) - 1:
                nodes_svg += f"""
                <g transform="translate({w / 2}, {y + box_h})">
                  <line x1="0" y1="0" x2="0" y2="28" stroke="#38BDF8" stroke-width="2" stroke-dasharray="4,4"/>
                  <polygon points="-6,26 6,26 0,34" fill="#38BDF8"/>
                </g>"""
            y += box_h + 34

        rule_svg = ""
        if rule:
            rule_svg = f"""
            <rect x="40" y="{h - 100}" width="{w - 80}" height="80" rx="12" fill="#1E293B" stroke="#EA4335" stroke-width="1.5"/>
            <text x="60" y="{h - 52}" fill="#FCA5A5" font-family="'DejaVu Sans', sans-serif" font-size="17" font-weight="500">
              {rule}
            </text>"""

        return f"""
        <rect x="0" y="0" width="{w}" height="{h}" rx="20" fill="#090E1A" stroke="#1E293B" stroke-width="2"/>
        {nodes_svg}
        {rule_svg}
        """

    def rasterize_svg_to_png(self, svg_content: str, output_png_path: Path) -> bool:
        """Saves SVG content and converts it to a PNG image using FFmpeg librsvg."""
        output_png_path = Path(output_png_path)
        output_png_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_svg = output_png_path.parent / f"_tmp_{output_png_path.stem}.svg"

        tmp_svg.write_text(svg_content, encoding="utf-8")

        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(tmp_svg),
                "-vf", f"scale={self.width}:{self.height}",
                str(output_png_path)
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return res.returncode == 0 and output_png_path.exists()
        except Exception as e:
            print(f"  ❌ Error rasterizing slide SVG to PNG: {e}")
            return False
        finally:
            if tmp_svg.exists():
                tmp_svg.unlink()
