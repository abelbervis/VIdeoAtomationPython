"""
AI Video Thumbnail & Cover Generator for COSMIC DEBATE EXPRESS.
Renders studio-grade 1080x1920 (9:16) cinematic posters with:
- Dynamic Cosmic Color Themes & Thematic Archetypes (Cyber Mint, Supernova Flame, Singularity Void, Chrono Cobalt, Aurora Multiverse)
- Context-Aware Semantic Theme Detection based on video topic & hook keywords
- Authentic 3D bio-reactive Orbs in topic-matched color pairings (Emerald, Solar, Quantum, Singularity, Supernova, Antimatter)
- Topic-seeded celestial starfields, volumetric multi-colored nebulae & procedural energy lightning arcs
- High-CTR viral headline typography with key emotional word highlighting, frosted glass card & atmospheric glows
- 100% deterministic, zero watermarks, studio-level retention design
"""

import hashlib
import json
import math
import random
import re
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from video.orb import ORB_PALETTES


# Curated high-impact emotional trigger words to highlight in titles
VIRAL_TRIGGER_WORDS = {
    "JAMÁS", "NADA", "NUNCA", "TODO", "REAL", "MENTIRA", "IMPOSIBLE",
    "SECRETO", "ILUSIÓN", "TIEMPO", "UNIVERSO", "TOCADO", "EXISTE",
    "DESTRUIR", "MUERTE", "CÓDIGO", "SIMULACIÓN", "VERDAD", "EXPLOTA",
    "ERROR", "PELIGRO", "GRAVEDAD", "SINGULARIDAD", "PASADO", "FUTURO",
    "PARADOJA", "FIN", "VIDA", "CEREBRO", "MATRIZ", "SOMOS"
}


# Thematic visual archetypes: each has unique background gradients, nebulae, orbs, badges and typography
COSMIC_THEMES: Dict[str, Dict[str, Any]] = {
    "supernova": {
        "id": "supernova",
        "name": "Supernova & Fuego Solar",
        "orb_left": "supernova",
        "orb_right": "solar",
        "bg_top": (36, 6, 12),
        "bg_bottom": (8, 1, 3),
        "nebula_left": (255, 23, 68, 55),
        "nebula_right": (255, 145, 0, 55),
        "accent_glow": (255, 61, 0, 32),
        "border_color": (255, 90, 20, 230),
        "accent_line": (255, 215, 0, 255),
        "eyebrow_text": "🔥  COLISIÓN TERMODINÁMICA  🔥",
        "eyebrow_color": (255, 190, 40),
        "eyebrow_border": (255, 90, 20, 210),
        "highlight_color": (255, 215, 60),
        "sub_color": (255, 190, 40),
        "badge_left": ("💥  SUPERNOVA", (255, 70, 70), (45, 10, 16, 235), (255, 50, 60, 255)),
        "badge_right": ("☀  SOLAR", (255, 200, 50), (42, 22, 10, 235), (255, 180, 0, 255)),
        "vs_color": (255, 220, 90),
        "vs_shield_border": (255, 180, 0, 255),
        "lightning_colors": [(255, 215, 0, 180), (255, 60, 60, 160), (255, 140, 0, 180)],
        "cta_text": "⚔  ¿QUIÉN TIENE LA RAZÓN?  ⚔",
        "cta_color": (255, 220, 80),
        "cta_border": (255, 180, 0, 240),
        "keywords": [
            "sol", "solar", "estrella", "fuego", "calor", "termodinamica", "termodinámica",
            "supernova", "fusion", "fusión", "magma", "infierno", "plasma", "explotar",
            "explosion", "explosión", "quemar", "llama", "ardiente"
        ]
    },
    "cyber": {
        "id": "cyber",
        "name": "Matriz Cuántica & Simulación",
        "orb_left": "emerald",
        "orb_right": "quantum",
        "bg_top": (2, 26, 18),
        "bg_bottom": (1, 6, 4),
        "nebula_left": (0, 255, 157, 50),
        "nebula_right": (0, 229, 255, 50),
        "accent_glow": (0, 255, 180, 28),
        "border_color": (0, 255, 157, 210),
        "accent_line": (0, 229, 255, 255),
        "eyebrow_text": "💻  REALIDAD SIMULADA O CÓDIGO  💻",
        "eyebrow_color": (0, 255, 157),
        "eyebrow_border": (0, 255, 157, 200),
        "highlight_color": (0, 255, 157),
        "sub_color": (0, 240, 255),
        "badge_left": ("❇  MATRIZ", (0, 255, 157), (6, 30, 22, 235), (0, 255, 157, 255)),
        "badge_right": ("⚛  CUÁNTICO", (0, 240, 255), (8, 25, 42, 235), (0, 240, 255, 255)),
        "vs_color": (0, 255, 200),
        "vs_shield_border": (0, 255, 157, 255),
        "lightning_colors": [(0, 255, 157, 180), (0, 229, 255, 180), (200, 255, 220, 180)],
        "cta_text": "⚔  ¿VIVIMOS EN UNA SIMULACIÓN?  ⚔",
        "cta_color": (0, 255, 180),
        "cta_border": (0, 255, 157, 240),
        "keywords": [
            "simulacion", "simulación", "matrix", "matriz", "codigo", "código",
            "computadora", "virtual", "informacion", "información", "holograma",
            "pixel", "ia", "algoritmo", "cerebro", "mente", "conciencia", "digital"
        ]
    },
    "singularity": {
        "id": "singularity",
        "name": "Singularidad & Gravedad Extrema",
        "orb_left": "singularity",
        "orb_right": "quantum",
        "bg_top": (26, 4, 40),
        "bg_bottom": (5, 1, 10),
        "nebula_left": (213, 0, 249, 52),
        "nebula_right": (0, 229, 255, 46),
        "accent_glow": (190, 0, 255, 30),
        "border_color": (213, 0, 249, 210),
        "accent_line": (255, 64, 129, 255),
        "eyebrow_text": "🌌  SINGULARIDAD Y AGUJERO NEGRO  🌌",
        "eyebrow_color": (235, 110, 255),
        "eyebrow_border": (213, 0, 249, 200),
        "highlight_color": (255, 110, 220),
        "sub_color": (255, 215, 0),
        "badge_left": ("🕳  SINGULARIDAD", (220, 80, 255), (32, 8, 50, 235), (213, 0, 249, 255)),
        "badge_right": ("⚛  CUÁNTICO", (0, 240, 255), (8, 25, 45, 235), (0, 240, 255, 255)),
        "vs_color": (255, 215, 0),
        "vs_shield_border": (213, 0, 249, 255),
        "lightning_colors": [(213, 0, 249, 180), (0, 240, 255, 180), (255, 255, 255, 190)],
        "cta_text": "⚔  ¿QUÉ HAY TRAS EL HORIZONTE?  ⚔",
        "cta_color": (255, 120, 240),
        "cta_border": (213, 0, 249, 240),
        "keywords": [
            "agujero negro", "gravedad", "relatividad", "einstein", "vacio", "vacío",
            "nada", "tocar", "horizonte", "suceso", "infinito", "curvatura", "masa",
            "singularidad", "abismo"
        ]
    },
    "chrono": {
        "id": "chrono",
        "name": "Paradoja Temporal & Relatividad",
        "orb_left": "quantum",
        "orb_right": "solar",
        "bg_top": (6, 16, 44),
        "bg_bottom": (2, 4, 12),
        "nebula_left": (41, 121, 255, 52),
        "nebula_right": (255, 171, 0, 52),
        "accent_glow": (0, 150, 255, 28),
        "border_color": (41, 121, 255, 210),
        "accent_line": (255, 215, 0, 255),
        "eyebrow_text": "⏳  DILEMA TEMPORAL Y RELATIVIDAD  ⏳",
        "eyebrow_color": (130, 195, 255),
        "eyebrow_border": (41, 121, 255, 200),
        "highlight_color": (255, 215, 0),
        "sub_color": (255, 215, 0),
        "badge_left": ("⚛  CUÁNTICO", (0, 240, 255), (10, 25, 48, 235), (0, 240, 255, 255)),
        "badge_right": ("☀  SOLAR", (255, 200, 50), (38, 22, 10, 235), (255, 180, 0, 255)),
        "vs_color": (255, 215, 0),
        "vs_shield_border": (255, 215, 0, 255),
        "lightning_colors": [(0, 240, 255, 180), (255, 180, 0, 180), (255, 255, 255, 190)],
        "cta_text": "⚔  ¿EL TIEMPO ES REAL O ILUSIÓN?  ⚔",
        "cta_color": (255, 215, 0),
        "cta_border": (255, 215, 0, 240),
        "keywords": [
            "tiempo", "pasado", "futuro", "velocidad", "luz", "reloj", "dilatacion",
            "dilatación", "gemelos", "paradoja", "entropia", "entropía", "viajar",
            "anos luz", "años luz", "cronologia"
        ]
    },
    "antimatter": {
        "id": "antimatter",
        "name": "Aniquilación de Antimateria",
        "orb_left": "antimatter",
        "orb_right": "quantum",
        "bg_top": (30, 3, 26),
        "bg_bottom": (4, 3, 14),
        "nebula_left": (255, 0, 127, 52),
        "nebula_right": (0, 229, 255, 50),
        "accent_glow": (255, 0, 200, 26),
        "border_color": (255, 0, 127, 210),
        "accent_line": (0, 240, 255, 255),
        "eyebrow_text": "⚡  MATERIA VS ANTIMATERIA  ⚡",
        "eyebrow_color": (255, 90, 170),
        "eyebrow_border": (255, 0, 127, 200),
        "highlight_color": (0, 240, 255),
        "sub_color": (255, 90, 170),
        "badge_left": ("⚡  ANTIMATERIA", (255, 0, 127), (40, 8, 30, 235), (255, 0, 127, 255)),
        "badge_right": ("⚛  CUÁNTICO", (0, 240, 255), (8, 25, 45, 235), (0, 240, 255, 255)),
        "vs_color": (255, 230, 80),
        "vs_shield_border": (255, 0, 127, 255),
        "lightning_colors": [(255, 0, 127, 180), (0, 240, 255, 180), (255, 255, 255, 190)],
        "cta_text": "⚔  ¿QUIÉN PREVALECERÁ?  ⚔",
        "cta_color": (255, 100, 180),
        "cta_border": (255, 0, 127, 240),
        "keywords": [
            "antimateria", "colision", "colisión", "particula", "partícula", "cern",
            "aniquilacion", "aniquilación", "atomo", "átomo", "boson", "bosón",
            "colisionador", "acelerador"
        ]
    },
    "aurora": {
        "id": "aurora",
        "name": "Multiverso & Dimensiones Ocultas",
        "orb_left": "singularity",
        "orb_right": "emerald",
        "bg_top": (16, 8, 36),
        "bg_bottom": (3, 4, 14),
        "nebula_left": (0, 229, 255, 48),
        "nebula_right": (255, 64, 129, 48),
        "accent_glow": (0, 255, 220, 25),
        "border_color": (0, 229, 255, 210),
        "accent_line": (255, 64, 129, 255),
        "eyebrow_text": "🌀  MULTIVERSO Y OTRAS DIMENSIONES  🌀",
        "eyebrow_color": (0, 240, 255),
        "eyebrow_border": (0, 229, 255, 200),
        "highlight_color": (255, 100, 180),
        "sub_color": (0, 240, 255),
        "badge_left": ("🕳  MULTIVERSO", (210, 100, 255), (32, 12, 45, 235), (210, 100, 255, 255)),
        "badge_right": ("❇  DIMENSIÓN", (0, 255, 160), (8, 32, 25, 235), (0, 255, 160, 255)),
        "vs_color": (255, 230, 80),
        "vs_shield_border": (0, 229, 255, 255),
        "lightning_colors": [(210, 100, 255, 180), (0, 255, 160, 180), (255, 255, 255, 190)],
        "cta_text": "⚔  ¿EXISTEN OTROS UNIVERSOS?  ⚔",
        "cta_color": (0, 240, 255),
        "cta_border": (0, 229, 255, 240),
        "keywords": [
            "multiverso", "dimension", "dimensión", "dimensiones", "universo", "universos",
            "paralelo", "cuerdas", "realidad", "vida", "extraterrestre", "alien", "origen",
            "cosmos", "cuantica", "cuántica"
        ]
    }
}


def get_font(size: int = 56) -> ImageFont.FreeTypeFont:
    """Finds and loads a bold TrueType font with full Spanish UTF-8 character support."""
    candidate_paths = [
        Path("assets/fonts/LiberationSans-Bold.ttf"),
        Path("assets/fonts/FreeSansBold.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/Library/Fonts/Arial Bold.ttf"),
    ]
    for p in candidate_paths:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def render_orb_asset(palette_key: str, size: int = 470) -> Image.Image:
    """Renders the authentic bio-reactive 3D orb with full spectral aura and concentric rings."""
    palette = ORB_PALETTES.get(palette_key, ORB_PALETTES["quantum"])
    canvas_size = 600
    c = canvas_size // 2
    r_sphere = int(canvas_size * 0.28)
    r_aura_outer = int(canvas_size * 0.46)
    r_aura_inner = int(canvas_size * 0.36)
    ring_r = int(r_sphere + 20)

    spot1_x = int(c - r_sphere * 0.30)
    spot1_y = int(c - r_sphere * 0.26)
    spot1_rx = int(r_sphere * 0.52)
    spot1_ry = int(r_sphere * 0.48)

    spot2_x = int(c + r_sphere * 0.28)
    spot2_y = int(c + r_sphere * 0.26)
    spot2_rx = int(r_sphere * 0.44)
    spot2_ry = int(r_sphere * 0.40)

    svg = f"""<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="spillBlur" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="65" />
    </filter>
    <filter id="auraDeep" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="30" />
    </filter>
    <filter id="auraMid" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="18" />
    </filter>
    <filter id="coreBlur" x="-25%" y="-25%" width="150%" height="150%">
      <feGaussianBlur stdDeviation="10" />
    </filter>
    <clipPath id="sphereClip">
      <circle cx="{c}" cy="{c}" r="{r_sphere}" />
    </clipPath>
    <radialGradient id="ambientSpill" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['spot1_glow']}" stop-opacity="0.95" />
      <stop offset="30%" stop-color="{palette['aura_inner']}" stop-opacity="0.75" />
      <stop offset="65%" stop-color="{palette['aura_outer']}" stop-opacity="0.40" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>
    <radialGradient id="outerAura" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['aura_inner']}" stop-opacity="0.95" />
      <stop offset="40%" stop-color="{palette['aura_mid']}" stop-opacity="0.70" />
      <stop offset="75%" stop-color="{palette['aura_outer']}" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>
    <radialGradient id="innerAura" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['aura_bright']}" stop-opacity="0.92" />
      <stop offset="50%" stop-color="{palette['aura_inner']}" stop-opacity="0.60" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>
    <radialGradient id="sphereBody" cx="42%" cy="38%" r="62%">
      <stop offset="0%" stop-color="{palette['body_c0']}" />
      <stop offset="22%" stop-color="{palette['body_c1']}" />
      <stop offset="48%" stop-color="{palette['body_c2']}" />
      <stop offset="72%" stop-color="{palette['body_c3']}" />
      <stop offset="88%" stop-color="{palette['body_c4']}" />
      <stop offset="100%" stop-color="{palette['body_c5']}" />
    </radialGradient>
    <radialGradient id="primarySpot" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['spot1_core']}" stop-opacity="1.0" />
      <stop offset="26%" stop-color="{palette['spot1_glow']}" stop-opacity="0.95" />
      <stop offset="60%" stop-color="{palette['spot1_outer']}" stop-opacity="0.65" />
      <stop offset="100%" stop-color="{palette['body_c3']}" stop-opacity="0.0" />
    </radialGradient>
    <radialGradient id="secondarySpot" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['spot2_core']}" stop-opacity="0.90" />
      <stop offset="40%" stop-color="{palette['spot2_mid']}" stop-opacity="0.65" />
      <stop offset="80%" stop-color="{palette['spot2_outer']}" stop-opacity="0.30" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>
  </defs>
  <circle cx="{c}" cy="{c}" r="{canvas_size // 2 - 10}" fill="url(#ambientSpill)" filter="url(#spillBlur)" />
  <circle cx="{c}" cy="{c}" r="{r_aura_outer}" fill="url(#outerAura)" filter="url(#auraDeep)" />
  <circle cx="{c}" cy="{c}" r="{r_aura_inner}" fill="url(#innerAura)" filter="url(#auraMid)" />
  <circle cx="{c}" cy="{c}" r="{ring_r + 4}" fill="none" stroke="{palette['aura_inner']}" stroke-width="6" opacity="0.8" filter="url(#auraMid)" />
  <circle cx="{c}" cy="{c}" r="{ring_r}" fill="none" stroke="{palette['ring_stroke']}" stroke-width="2.5" opacity="0.95" />
  <circle cx="{c}" cy="{c}" r="{r_sphere}" fill="url(#sphereBody)" />
  <g clip-path="url(#sphereClip)">
    <ellipse cx="{spot2_x}" cy="{spot2_y}" rx="{spot2_rx}" ry="{spot2_ry}" fill="url(#secondarySpot)" filter="url(#coreBlur)" />
    <ellipse cx="{spot1_x}" cy="{spot1_y}" rx="{spot1_rx}" ry="{spot1_ry}" fill="url(#primarySpot)" filter="url(#coreBlur)" />
    <circle cx="{spot1_x}" cy="{spot1_y}" r="{int(spot1_rx * 0.45)}" fill="{palette['spot1_core']}" opacity="0.98" filter="url(#coreBlur)" />
    <circle cx="{c}" cy="{c}" r="{r_sphere - 3}" fill="none" stroke="{palette['rim_stroke']}" stroke-width="4" opacity="0.55" filter="url(#coreBlur)" />
  </g>
  <circle cx="{c}" cy="{c}" r="{r_sphere - 2}" fill="none" stroke="{palette['aura_inner']}" stroke-width="3" opacity="0.75" />
</svg>"""

    temp_dir = Path("/tmp/_orb_gen")
    temp_dir.mkdir(parents=True, exist_ok=True)
    svg_path = temp_dir / f"orb_{palette_key}.svg"
    png_path = temp_dir / f"orb_{palette_key}.png"

    svg_path.write_text(svg, encoding="utf-8")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(svg_path), str(png_path)
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    orb_img = Image.open(png_path).convert("RGBA")
    if (size, size) != orb_img.size:
        orb_img = orb_img.resize((size, size), Image.Resampling.LANCZOS)
    return orb_img


class ThumbnailGenerator:
    """Generates high-retention, studio-grade vertical thumbnails for Cosmic Debate Express."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def detect_theme(self, topic: str, hook: str, theme_override: Optional[str] = None) -> Dict[str, Any]:
        """Detects the optimal cosmic theme based on semantic keywords or explicit override."""
        if theme_override and theme_override.lower() in COSMIC_THEMES:
            return COSMIC_THEMES[theme_override.lower()]

        if theme_override == "random":
            return random.choice(list(COSMIC_THEMES.values()))

        # Normalize text and search keywords with word boundaries
        full_text = f"{topic} {hook}".lower()
        full_text = full_text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

        # Check priority order
        theme_keys = ["chrono", "cyber", "supernova", "singularity", "antimatter", "aurora"]
        for t_key in theme_keys:
            theme_def = COSMIC_THEMES[t_key]
            for kw in theme_def["keywords"]:
                norm_kw = kw.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                if re.search(r"(?i)\b" + re.escape(norm_kw) + r"\b", full_text):
                    return theme_def

        # Deterministic cyclic fallback based on topic hash so two unknown topics differ
        hash_val = int(hashlib.md5(full_text.encode("utf-8")).hexdigest()[:8], 16)
        all_themes = list(COSMIC_THEMES.values())
        return all_themes[hash_val % len(all_themes)]

    def format_title_text(self, hook: str, topic: str) -> Tuple[str, str]:
        """Cleans and extracts the punchiest headline title and scientific subtitle."""
        raw = hook or topic or "DEBATE CÓSMICO"
        clean = re.sub(r"[⚡🔥💥✨🚀👁️⚛️☀️🌀⏳💻🕳️❇️]", "", raw).strip()
        clean = clean.replace("¡", "").replace("!", "").strip().upper()
        if not clean or len(clean) < 5:
            clean = (topic or "DEBATE CÓSMICO").upper()

        sub = (topic or "FÍSICA CUÁNTICA VS ASTROFÍSICA").upper()
        sub = re.sub(r"[⚡🔥💥✨🚀👁️⚛️☀️🌀⏳💻🕳️❇️]", "", sub).strip()
        return clean, sub

    def render_highlighted_headline(
        self,
        draw: ImageDraw.Draw,
        lines: List[str],
        start_y: int,
        line_height: int,
        font: ImageFont.FreeTypeFont,
        canvas_width: int,
        highlight_color: Tuple[int, int, int],
        glow_color: Tuple[int, int, int] = (0, 160, 255),
    ):
        """Renders multiline text with emotional trigger words highlighted in neon accent."""
        space_bbox = draw.textbbox((0, 0), " ", font=font)
        space_w = space_bbox[2] - space_bbox[0]

        curr_y = start_y
        for line in lines:
            words = line.split()
            if not words:
                curr_y += line_height
                continue

            word_boxes = [draw.textbbox((0, 0), w, font=font) for w in words]
            word_widths = [b[2] - b[0] for b in word_boxes]
            total_line_w = sum(word_widths) + space_w * (len(words) - 1)
            start_x = (canvas_width - total_line_w) // 2

            curr_x = start_x
            for w, w_w in zip(words, word_widths):
                # Clean punctuation to check dictionary
                clean_w = re.sub(r"[^A-ZÁÉÍÓÚÑ]", "", w.upper())
                is_highlight = (clean_w in VIRAL_TRIGGER_WORDS) or (len(clean_w) >= 6 and clean_w.isupper())

                text_fill = highlight_color if is_highlight else (255, 255, 255, 255)

                # 1. Deep drop shadow
                draw.text((curr_x + 4, curr_y + 4), w, font=font, fill=(0, 0, 0, 240))
                draw.text((curr_x + 2, curr_y + 2), w, font=font, fill=(0, 0, 0, 240))

                # 2. Atmospheric luminous aura
                glow_fill = (*highlight_color, 180) if is_highlight else (*glow_color, 140)
                draw.text((curr_x - 1, curr_y), w, font=font, fill=glow_fill)
                draw.text((curr_x + 1, curr_y), w, font=font, fill=glow_fill)
                draw.text((curr_x, curr_y - 1), w, font=font, fill=glow_fill)
                draw.text((curr_x, curr_y + 1), w, font=font, fill=glow_fill)

                # 3. Main crisp text
                draw.text((curr_x, curr_y), w, font=font, fill=text_fill)
                curr_x += w_w + space_w

            curr_y += line_height

    def render_studio_poster(
        self,
        hook: str,
        topic: str,
        output_path: Path,
        theme_name: Optional[str] = None,
    ) -> Path:
        """
        Renders an ultra-high quality 1080x1920 cinematic YouTube Shorts/TikTok cover
        with dynamic cosmic color themes tailored to the topic.
        """
        theme = self.detect_theme(topic, hook, theme_override=theme_name)
        clean_headline, clean_sub = self.format_title_text(hook, topic)

        # Generate topic-derived deterministic seed so each topic gets unique stars and nebula shapes
        topic_seed = int(hashlib.md5(f"{topic}_{hook}".encode("utf-8")).hexdigest()[:8], 16)
        rng = random.Random(topic_seed)

        W, H = 1080, 1920
        poster = Image.new("RGBA", (W, H), (*theme["bg_top"], 255))
        pdraw = ImageDraw.Draw(poster)

        # 1. Atmospheric cosmic space gradient (Theme-specific top & bottom tones)
        top_r, top_g, top_b = theme["bg_top"]
        bot_r, bot_g, bot_b = theme["bg_bottom"]
        for y in range(H):
            factor = y / H
            r = int(top_r * (1.0 - factor * 0.7) + bot_r * (factor * 0.7))
            g = int(top_g * (1.0 - factor * 0.7) + bot_g * (factor * 0.7))
            b = int(top_b * (1.0 - factor * 0.7) + bot_b * (factor * 0.7))
            pdraw.line([(0, y), (W, y)], fill=(r, g, b, 255))

        # 2. Topic-seeded rich celestial starfield with colored stellar points
        stars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(stars)
        star_palette = [
            (255, 255, 255),
            (200, 235, 255),
            theme["highlight_color"],
            (220, 200, 255),
            (255, 240, 200),
        ]
        for _ in range(520):
            sx = rng.randint(0, W)
            sy = rng.randint(0, H)
            col = rng.choice(star_palette)
            sr = rng.choice([1, 1, 1, 2, 2, 3])
            opacity = rng.randint(90, 255)
            sdraw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(*col, opacity))
        poster = Image.alpha_composite(poster, stars)

        # 3. Volumetric nebula glows in theme-specific clashing hues
        nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ndraw = ImageDraw.Draw(nebula)

        # Left faction nebula
        neb_left_col = theme["nebula_left"]
        ndraw.ellipse([-170 + rng.randint(-30, 30), 680 + rng.randint(-40, 40), 690, 1420], fill=neb_left_col)

        # Right faction nebula
        neb_right_col = theme["nebula_right"]
        ndraw.ellipse([W - 690, 680 + rng.randint(-40, 40), W + 170 + rng.randint(-30, 30), 1420], fill=neb_right_col)

        # Central accent flare
        cent_glow = theme["accent_glow"]
        ndraw.ellipse([W // 2 - 380, 80, W // 2 + 380, 520], fill=cent_glow)
        ndraw.ellipse([W // 2 - 180, 920, W // 2 + 180, 1220], fill=cent_glow)

        nebula = nebula.filter(ImageFilter.GaussianBlur(95))
        poster = Image.alpha_composite(poster, nebula)

        # 4. Render and place authentic orbs tailored to the theme
        orb_l_key = theme["orb_left"]
        orb_r_key = theme["orb_right"]
        orb_left_img = render_orb_asset(orb_l_key, size=470)
        orb_right_img = render_orb_asset(orb_r_key, size=470)

        # Subtly dynamic orb placement based on seed
        y_offset_l = rng.randint(-15, 15)
        y_offset_r = rng.randint(-15, 15)
        q_pos = (int(W * 0.04), 820 + y_offset_l)
        s_pos = (int(W * 0.52), 820 + y_offset_r)
        poster.paste(orb_left_img, q_pos, orb_left_img)
        poster.paste(orb_right_img, s_pos, orb_right_img)

        # 5. Energy divide, procedural lightning arcs & Center VS Shield
        vs_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        vdraw = ImageDraw.Draw(vs_layer)
        vs_cx = W // 2
        vs_cy = 1055

        # Vertical energy divide lines
        vdraw.line([(vs_cx, 750), (vs_cx, 1360)], fill=(255, 255, 255, 75), width=3)
        l_color = theme.get("energy_line_left", (0, 240, 255, 130))
        r_color = theme.get("energy_line_right", (255, 180, 0, 130))
        vdraw.line([(vs_cx - 1, 840), (vs_cx - 1, 1270)], fill=l_color, width=2)
        vdraw.line([(vs_cx + 1, 840), (vs_cx + 1, 1270)], fill=r_color, width=2)

        # Procedural electric lightning crackles between orbs
        lightning_palette = theme.get("lightning_colors", [(255, 255, 255, 180)])
        for _ in range(4):
            bolt_color = rng.choice(lightning_palette)
            cur_lx = vs_cx + rng.randint(-40, 40)
            cur_ly = 850 + rng.randint(0, 40)
            target_ly = 1250 + rng.randint(-40, 0)
            while cur_ly < target_ly:
                next_lx = cur_lx + rng.randint(-16, 16)
                next_ly = cur_ly + rng.randint(25, 60)
                vdraw.line([(cur_lx, cur_ly), (next_lx, next_ly)], fill=bolt_color, width=rng.choice([1, 2]))
                cur_lx, cur_ly = next_lx, next_ly

        # Center VS Metallic Shield
        shield_border = theme.get("vs_shield_border", (255, 215, 0, 255))
        vdraw.ellipse([vs_cx - 56, vs_cy - 56, vs_cx + 56, vs_cy + 56], fill=(12, 16, 32, 245), outline=shield_border, width=4)
        vs_font = get_font(46)
        vbbox = vdraw.textbbox((0, 0), "VS", font=vs_font)
        vw = vbbox[2] - vbbox[0]
        vh = vbbox[3] - vbbox[1]
        vdraw.text((vs_cx - vw // 2, vs_cy - vh // 2 - 4), "VS", font=vs_font, fill=theme["vs_color"])
        poster = Image.alpha_composite(poster, vs_layer)

        # 6. Entity Badges below orbs matching their factions
        badge_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(badge_layer)
        badge_font = get_font(28)

        # Left Badge
        b_label_l, b_txt_col_l, b_bg_l, b_border_l = theme["badge_left"]
        bdraw.rounded_rectangle([120, 1310, 400, 1375], radius=18, fill=b_bg_l, outline=b_border_l, width=3)
        bbbox_l = bdraw.textbbox((0, 0), b_label_l, font=badge_font)
        bw_l = bbbox_l[2] - bbbox_l[0]
        bdraw.text((120 + (280 - bw_l) // 2, 1326), b_label_l, font=badge_font, fill=b_txt_col_l)

        # Right Badge
        b_label_r, b_txt_col_r, b_bg_r, b_border_r = theme["badge_right"]
        bdraw.rounded_rectangle([W - 400, 1310, W - 120, 1375], radius=18, fill=b_bg_r, outline=b_border_r, width=3)
        bbbox_r = bdraw.textbbox((0, 0), b_label_r, font=badge_font)
        bw_r = bbbox_r[2] - bbbox_r[0]
        bdraw.text((W - 400 + (280 - bw_r) // 2, 1326), b_label_r, font=badge_font, fill=b_txt_col_r)

        poster = Image.alpha_composite(poster, badge_layer)

        # 7. Hero Headline Glass Card
        title_card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        tdraw = ImageDraw.Draw(title_card)

        # Top Eyebrow Tag
        eyebrow_font = get_font(24)
        eb_text = theme["eyebrow_text"]
        ebbox = tdraw.textbbox((0, 0), eb_text, font=eyebrow_font)
        ebw = ebbox[2] - ebbox[0]
        eb_x = (W - ebw) // 2
        tdraw.rounded_rectangle([eb_x - 24, 100, eb_x + ebw + 24, 150], radius=16, fill=(10, 18, 38, 225), outline=theme["eyebrow_border"], width=2)
        tdraw.text((eb_x, 113), eb_text, font=eyebrow_font, fill=theme["eyebrow_color"])

        # Main Title Card Glass Box
        card_x1, card_y1, card_x2, card_y2 = 45, 175, W - 45, 595
        tdraw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=28, fill=(10, 15, 30, 235), outline=theme["border_color"], width=3)
        # Accent gradient top line
        tdraw.line([(card_x1 + 30, card_y1), (card_x2 - 30, card_y1)], fill=theme["accent_line"], width=4)

        # Word wrap Headline Text
        title_font = get_font(58)
        words = clean_headline.split()
        lines: List[str] = []
        curr: List[str] = []
        for w in words:
            curr.append(w)
            tb = tdraw.textbbox((0, 0), " ".join(curr), font=title_font)
            if (tb[2] - tb[0]) > (card_x2 - card_x1 - 80):
                curr.pop()
                lines.append(" ".join(curr))
                curr = [w]
        if curr:
            lines.append(" ".join(curr))

        # Limit to max 3 lines for high-retention layout
        lines = lines[:3]
        start_headline_y = card_y1 + 45
        line_spacing = 76

        # Render headline with highlighted viral keywords
        self.render_highlighted_headline(
            draw=tdraw,
            lines=lines,
            start_y=start_headline_y,
            line_height=line_spacing,
            font=title_font,
            canvas_width=W,
            highlight_color=theme["highlight_color"],
            glow_color=theme["eyebrow_color"],
        )

        # Subtitle inside the card
        sub_font = get_font(30)
        stb = tdraw.textbbox((0, 0), clean_sub, font=sub_font)
        stw = stb[2] - stb[0]
        stx = (W - stw) // 2
        sub_y = start_headline_y + len(lines) * line_spacing + 16
        tdraw.text((stx + 2, sub_y + 2), clean_sub, font=sub_font, fill=(0, 0, 0, 220))
        tdraw.text((stx, sub_y), clean_sub, font=sub_font, fill=theme["sub_color"])

        # 8. Bottom Call To Action Badge (Safely above TikTok/Shorts UI controls)
        cta_font = get_font(32)
        cta_text = theme["cta_text"]
        ctb = tdraw.textbbox((0, 0), cta_text, font=cta_font)
        ctw = ctb[2] - ctb[0]
        cx = (W - ctw) // 2
        tdraw.rounded_rectangle([cx - 32, 1460, cx + ctw + 32, 1530], radius=24, fill=(15, 22, 42, 235), outline=theme["cta_border"], width=3)
        tdraw.text((cx, 1478), cta_text, font=cta_font, fill=theme["cta_color"])

        poster = Image.alpha_composite(poster, title_card)

        # 9. Save final thumbnail image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_rgb = poster.convert("RGB")
        final_rgb.save(output_path, "JPEG", quality=96)
        print(f"  ✨ ¡Portada cinematográfica generada con éxito en: {output_path}!")
        print(f"     🎨 Estilo Cósmico: '{theme['name']}' (Orbes: {theme['orb_left']} vs {theme['orb_right']})")
        return output_path

    def generate_thumbnail_for_script(
        self,
        script_path: Path,
        output_image_path: Optional[Path] = None,
        theme_name: Optional[str] = None
    ) -> Optional[Path]:
        """Generates a 9:16 cinematic thumbnail for a given script.json file."""
        script_path = Path(script_path)
        if not script_path.exists():
            print(f"❌ Error: No se encontró el archivo de guión en {script_path}")
            return None

        try:
            data = json.loads(script_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"❌ Error leyendo el JSON {script_path}: {e}")
            return None

        topic = data.get("topic", "Física Cuántica vs Astrofísica Solar")
        hook = data.get("headline_hook", "¡JAMÁS HAS TOCADO NADA EN TU VIDA!")

        if output_image_path is None:
            output_image_path = script_path.parent / "thumbnail.jpg"
        else:
            output_image_path = Path(output_image_path)

        print(f"\n🖼️ [Thumbnail Studio] Generando portada cinematográfica:")
        print(f"   • Tema: '{topic}'")
        print(f"   • Gancho: '{hook}'")
        return self.render_studio_poster(hook, topic, output_image_path, theme_name=theme_name)

    def batch_generate_thumbnails(
        self,
        base_output_dir: Path = Path("output") / "orb_previews",
        theme_name: Optional[str] = None
    ) -> int:
        """Scans all video folders in base_output_dir and regenerates studio thumbnails."""
        base_dir = Path(base_output_dir)
        if not base_dir.exists():
            print(f"⚠️ El directorio de salida {base_dir} no existe.")
            return 0

        count = 0
        script_files = list(base_dir.glob("**/script.json"))
        print(f"\n🔍 [Thumbnail Batch] Encontrados {len(script_files)} proyectos en {base_dir}...")

        for script_f in script_files:
            thumb_f = script_f.parent / "thumbnail.jpg"
            print(f"\n📁 Procesando portada para: {script_f.parent.name}")
            res = self.generate_thumbnail_for_script(script_f, thumb_f, theme_name=theme_name)
            if res:
                count += 1

        print(f"\n✨ [Thumbnail Batch] Proceso completado. Se generaron {count} portadas profesionales.")
        return count
