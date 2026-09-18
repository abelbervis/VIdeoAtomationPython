"""
AI Video Thumbnail & Cover Generator for COSMIC DEBATE EXPRESS.
Renders studio-grade 1080x1920 (9:16) cinematic posters with:
- Authentic Video Orbs: Always Quantum (Cyan #00e5ff) on left and Solar (Amber #ffb300) on right, exactly matching the debate characters.
- AI-Generated Deep Space Backgrounds: Contextual prompts generated via Pollinations (FLUX/Turbo) tailored to the topic (with procedural cosmic fallback).
- Dynamic Neon Typography & Text Color Themes: High-impact keyword highlighting, eyebrow badges, card borders and CTA colors varying per topic (Cyber Mint, Solar Magma, Singularity Lilac, Chrono Cyan, Hyper Pink, Electric Emerald).
- Maximum Space Utilization: Optimized 9:16 vertical balance filling the entire canvas with massive 520px orbs, high-impact headline card, and bottom engagement hook.
- 100% deterministic, zero watermarks, studio-level retention design.
"""

import hashlib
import json
import math
import random
import re
import subprocess
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from video.orb import ORB_PALETTES
from providers.pollinations import PollinationsProvider


# Curated high-impact emotional trigger words to highlight in titles
VIRAL_TRIGGER_WORDS = {
    "JAMÁS", "NADA", "NUNCA", "TODO", "REAL", "MENTIRA", "IMPOSIBLE",
    "SECRETO", "ILUSIÓN", "TIEMPO", "UNIVERSO", "TOCADO", "EXISTE",
    "DESTRUIR", "MUERTE", "CÓDIGO", "SIMULACIÓN", "VERDAD", "EXPLOTA",
    "ERROR", "PELIGRO", "GRAVEDAD", "SINGULARIDAD", "PASADO", "FUTURO",
    "PARADOJA", "FIN", "VIDA", "CEREBRO", "MATRIZ", "SOMOS", "ÁTOMOS",
    "ATOMOS", "LUZ", "ENERGÍA", "ENERGIA", "CUÁNTICO", "CUANTICO", "SOL",
    "DIOS", "MENTE", "HORIZONTE", "SUCESO", "VACÍO", "VACIO"
}


# Text & Graphic Accent Color Themes (The Orbs ALWAYS stay Quantum & Solar!)
TEXT_THEMES: Dict[str, Dict[str, Any]] = {
    "cyber": {
        "id": "cyber",
        "name": "Matrix Cyber Mint",
        "highlight_color": (0, 255, 157),      # Neon Mint
        "secondary_color": (0, 229, 255),      # Electric Cyan
        "eyebrow_text": "💻  REALIDAD SIMULADA O CÓDIGO  💻",
        "eyebrow_color": (0, 255, 157),
        "eyebrow_border": (0, 255, 157, 200),
        "card_border": (0, 255, 157, 210),
        "accent_line": (0, 229, 255, 255),
        "cta_text": "⚔  ¿VIVIMOS EN UNA SIMULACIÓN?  ⚔",
        "cta_color": (0, 255, 180),
        "cta_border": (0, 255, 157, 240),
        "prompt_concept": "cyberpunk dark cosmic matrix grid, quantum cyberspace nebula, holographic stellar dust, dark universe, glowing cyber particles",
        "keywords": [
            "simulacion", "simulación", "matrix", "matriz", "codigo", "código",
            "computadora", "virtual", "informacion", "información", "holograma",
            "pixel", "ia", "algoritmo", "cerebro", "mente", "conciencia", "digital"
        ]
    },
    "supernova": {
        "id": "supernova",
        "name": "Supernova Solar Gold",
        "highlight_color": (255, 215, 0),      # Molten Gold
        "secondary_color": (255, 140, 0),      # Amber Orange
        "eyebrow_text": "🔥  COLISIÓN TERMODINÁMICA  🔥",
        "eyebrow_color": (255, 200, 50),
        "eyebrow_border": (255, 120, 20, 210),
        "card_border": (255, 160, 20, 210),
        "accent_line": (255, 215, 0, 255),
        "cta_text": "⚔  ¿QUIÉN TIENE LA RAZÓN?  ⚔",
        "cta_color": (255, 220, 80),
        "cta_border": (255, 180, 0, 240),
        "prompt_concept": "colossal supernova explosion in deep space, glowing cosmic dust filaments, intense starburst, stellar nursery nebula, photorealistic astronomy",
        "keywords": [
            "sol", "solar", "estrella", "fuego", "calor", "termodinamica", "termodinámica",
            "supernova", "fusion", "fusión", "magma", "infierno", "plasma", "explotar",
            "explosion", "explosión", "quemar", "llama", "ardiente"
        ]
    },
    "singularity": {
        "id": "singularity",
        "name": "Singularidad Lilac & Violet",
        "highlight_color": (234, 128, 252),    # Neon Lilac
        "secondary_color": (213, 0, 249),      # Electric Magenta
        "eyebrow_text": "🌌  SINGULARIDAD Y GRAVEDAD  🌌",
        "eyebrow_color": (235, 110, 255),
        "eyebrow_border": (213, 0, 249, 200),
        "card_border": (213, 0, 249, 210),
        "accent_line": (255, 64, 129, 255),
        "cta_text": "⚔  ¿QUÉ HAY TRAS EL HORIZONTE?  ⚔",
        "cta_color": (255, 140, 250),
        "cta_border": (213, 0, 249, 240),
        "prompt_concept": "supermassive black hole with glowing relativistic accretion disk, gravitational lensing distortion, deep space cosmic void, stars and dust",
        "keywords": [
            "agujero negro", "gravedad", "relatividad", "einstein", "vacio", "vacío",
            "nada", "tocar", "horizonte", "suceso", "infinito", "curvatura", "masa",
            "singularidad", "abismo"
        ]
    },
    "chrono": {
        "id": "chrono",
        "name": "Paradoja Temporal Azure",
        "highlight_color": (0, 229, 255),      # High-voltage Cyan
        "secondary_color": (255, 215, 0),      # Solar Gold
        "eyebrow_text": "⏳  DILEMA TEMPORAL Y RELATIVIDAD  ⏳",
        "eyebrow_color": (100, 210, 255),
        "eyebrow_border": (0, 180, 255, 200),
        "card_border": (0, 180, 255, 210),
        "accent_line": (255, 215, 0, 255),
        "cta_text": "⚔  ¿EL TIEMPO ES REAL O ILUSIÓN?  ⚔",
        "cta_color": (0, 240, 255),
        "cta_border": (0, 200, 255, 240),
        "prompt_concept": "cosmic gravitational spacetime curvature, warping of space and time, quantum time rift, celestial nebula particles, photorealistic space art",
        "keywords": [
            "tiempo", "pasado", "futuro", "velocidad", "luz", "reloj", "dilatacion",
            "dilatación", "gemelos", "paradoja", "entropia", "entropía", "viajar",
            "anos luz", "años luz", "cronologia"
        ]
    },
    "hyper_pink": {
        "id": "hyper_pink",
        "name": "Antimateria Hyper Pink",
        "highlight_color": (255, 0, 127),      # Neon Fuchsia
        "secondary_color": (0, 229, 255),      # Electric Cyan
        "eyebrow_text": "⚡  MATERIA VS ANTIMATERIA  ⚡",
        "eyebrow_color": (255, 80, 160),
        "eyebrow_border": (255, 0, 127, 200),
        "card_border": (255, 0, 127, 210),
        "accent_line": (0, 240, 255, 255),
        "cta_text": "⚔  ¿QUIÉN PREVALECERÁ?  ⚔",
        "cta_color": (255, 90, 180),
        "cta_border": (255, 0, 127, 240),
        "prompt_concept": "collision of subatomic matter and antimatter particles in cosmos, high energy quantum annihilation glow, cosmic particle shockwave, dark background",
        "keywords": [
            "antimateria", "colision", "colisión", "particula", "partícula", "cern",
            "aniquilacion", "aniquilación", "atomo", "átomo", "boson", "bosón",
            "colisionador", "acelerador"
        ]
    },
    "antimatter": {
        "id": "antimatter",
        "name": "Antimateria Hyper Pink",
        "highlight_color": (255, 0, 127),      # Neon Fuchsia
        "secondary_color": (0, 229, 255),      # Electric Cyan
        "eyebrow_text": "⚡  MATERIA VS ANTIMATERIA  ⚡",
        "eyebrow_color": (255, 80, 160),
        "eyebrow_border": (255, 0, 127, 200),
        "card_border": (255, 0, 127, 210),
        "accent_line": (0, 240, 255, 255),
        "cta_text": "⚔  ¿QUIÉN PREVALECERÁ?  ⚔",
        "cta_color": (255, 90, 180),
        "cta_border": (255, 0, 127, 240),
        "prompt_concept": "collision of subatomic matter and antimatter particles in cosmos, high energy quantum annihilation glow, cosmic particle shockwave, dark background",
        "keywords": [
            "antimateria", "colision", "colisión", "particula", "partícula", "cern",
            "aniquilacion", "aniquilación", "atomo", "átomo", "boson", "bosón",
            "colisionador", "acelerador"
        ]
    },
    "aurora": {
        "id": "aurora",
        "name": "Multiverso & Teoría Cuántica",
        "highlight_color": (0, 255, 200),      # Turquoise Mint
        "secondary_color": (255, 100, 200),    # Rose Pink
        "eyebrow_text": "🌀  FÍSICA CUÁNTICA VS ASTROFÍSICA  🌀",
        "eyebrow_color": (0, 240, 255),
        "eyebrow_border": (0, 229, 255, 200),
        "card_border": (0, 229, 255, 210),
        "accent_line": (255, 64, 129, 255),
        "cta_text": "⚔  ¿QUIÉN TIENE LA RAZÓN?  ⚔",
        "cta_color": (0, 240, 255),
        "cta_border": (0, 229, 255, 240),
        "prompt_concept": "subatomic quantum realm, glowing atomic orbitals, electromagnetic electron fields, cosmic nebula particles, volumetric lighting, dark sci-fi cosmos",
        "keywords": [
            "multiverso", "dimension", "dimensión", "dimensiones", "universo", "universos",
            "paralelo", "cuerdas", "realidad", "vida", "extraterrestre", "alien", "origen",
            "cosmos", "cuantica", "cuántica", "electrones", "campo"
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


def render_orb_asset(palette_key: str, size: int = 520) -> Image.Image:
    """Renders the authentic bio-reactive 3D orb with full spectral aura, internal granulation flare detail, and concentric quantum rings."""
    palette = ORB_PALETTES.get(palette_key, ORB_PALETTES["quantum"])
    is_solar = ("solar" in palette_key)
    canvas_size = 650
    c = canvas_size // 2
    r_sphere = int(canvas_size * 0.28)
    r_aura_outer = int(canvas_size * 0.46)
    r_aura_inner = int(canvas_size * 0.36)
    quantum_ring_r = int(r_sphere + 42)

    spot1_x = int(c - r_sphere * 0.28)
    spot1_y = int(c - r_sphere * 0.24)
    spot1_rx = int(r_sphere * 0.52)
    spot1_ry = int(r_sphere * 0.48)

    spot2_x = int(c + r_sphere * 0.26)
    spot2_y = int(c + r_sphere * 0.24)
    spot2_rx = int(r_sphere * 0.44)
    spot2_ry = int(r_sphere * 0.40)

    # Extra internal plasma nodes for Solar
    swirl1_x = int(c + r_sphere * 0.14)
    swirl1_y = int(c - r_sphere * 0.18)
    swirl1_rx = int(r_sphere * 0.46)
    swirl1_ry = int(r_sphere * 0.38)

    swirl2_x = int(c - r_sphere * 0.18)
    swirl2_y = int(c + r_sphere * 0.16)
    swirl2_rx = int(r_sphere * 0.42)
    swirl2_ry = int(r_sphere * 0.34)

    arc_path = f"M {c - int(r_sphere*0.42)} {c + int(r_sphere*0.08)} Q {c + int(r_sphere*0.1)} {c - int(r_sphere*0.35)} {c + int(r_sphere*0.42)} {c + int(r_sphere*0.12)}"

    solar_body_stops = """
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="10%" stop-color="{palette['body_c0']}" />
      <stop offset="26%" stop-color="{palette['body_c1']}" />
      <stop offset="48%" stop-color="{palette['body_c2']}" />
      <stop offset="68%" stop-color="{palette['body_c3']}" />
      <stop offset="85%" stop-color="{palette['body_c4']}" />
      <stop offset="95%" stop-color="{palette['body_c5']}" />
      <stop offset="100%" stop-color="#120005" />
""".format(palette=palette) if is_solar else """
      <stop offset="0%" stop-color="{palette['body_c0']}" />
      <stop offset="22%" stop-color="{palette['body_c1']}" />
      <stop offset="48%" stop-color="{palette['body_c2']}" />
      <stop offset="72%" stop-color="{palette['body_c3']}" />
      <stop offset="88%" stop-color="{palette['body_c4']}" />
      <stop offset="100%" stop-color="{palette['body_c5']}" />
""".format(palette=palette)

    extra_solar_rings = f"""
  <!-- Quantum Orbital Energy Ring for Solar -->
  <circle cx="{c}" cy="{c}" r="{quantum_ring_r + 7}" fill="none" stroke="{palette['aura_inner']}" stroke-width="7.0" opacity="0.65" filter="url(#auraMid)" />
  <circle cx="{c}" cy="{c}" r="{quantum_ring_r}" fill="none" stroke="{palette['ring_stroke']}" stroke-width="2.8" stroke-dasharray="28 14 56 14" opacity="0.95" />
  <circle cx="{c}" cy="{c}" r="{quantum_ring_r - 1}" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.80" />

  <!-- Tilted Heliospheric Belts -->
  <ellipse cx="{c}" cy="{c}" rx="{quantum_ring_r + 12}" ry="{(quantum_ring_r + 12)*0.38}" transform="rotate(-22 {c} {c})" fill="none" stroke="{palette['aura_inner']}" stroke-width="5" opacity="0.55" filter="url(#auraMid)" />
  <ellipse cx="{c}" cy="{c}" rx="{quantum_ring_r + 12}" ry="{(quantum_ring_r + 12)*0.38}" transform="rotate(-22 {c} {c})" fill="none" stroke="{palette['ring_stroke']}" stroke-width="2.2" stroke-dasharray="32 16 48 16" opacity="0.88" />
  <ellipse cx="{c}" cy="{c}" rx="{quantum_ring_r + 32}" ry="{(quantum_ring_r + 32)*0.32}" transform="rotate(32 {c} {c})" fill="none" stroke="{palette['aura_bright']}" stroke-width="2.0" stroke-dasharray="24 20 40 20" opacity="0.70" />
""" if is_solar else f"""
  <circle cx="{c}" cy="{c}" r="{quantum_ring_r + 5}" fill="none" stroke="{palette['aura_inner']}" stroke-width="7" opacity="0.8" filter="url(#auraMid)" />
  <circle cx="{c}" cy="{c}" r="{quantum_ring_r}" fill="none" stroke="{palette['ring_stroke']}" stroke-width="3.0" opacity="0.95" />
"""

    svg = f"""<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="spillBlur" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="65" />
    </filter>
    <filter id="auraDeep" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="32" />
    </filter>
    <filter id="auraMid" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="18" />
    </filter>
    <filter id="coreBlur" x="-25%" y="-25%" width="150%" height="150%">
      <feGaussianBlur stdDeviation="9" />
    </filter>
    <clipPath id="sphereClip">
      <circle cx="{c}" cy="{c}" r="{r_sphere}" />
    </clipPath>
    <radialGradient id="ambientSpill" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['spot1_glow']}" stop-opacity="0.95" />
      <stop offset="20%" stop-color="{palette['body_c1']}" stop-opacity="0.80" />
      <stop offset="45%" stop-color="{palette['aura_inner']}" stop-opacity="0.60" />
      <stop offset="70%" stop-color="{palette['aura_outer']}" stop-opacity="0.30" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>
    <radialGradient id="outerAura" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['aura_inner']}" stop-opacity="0.95" />
      <stop offset="30%" stop-color="{palette['aura_mid']}" stop-opacity="0.70" />
      <stop offset="65%" stop-color="{palette['aura_outer']}" stop-opacity="0.35" />
      <stop offset="85%" stop-color="{palette['body_c5']}" stop-opacity="0.12" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>
    <radialGradient id="innerAura" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['aura_bright']}" stop-opacity="0.95" />
      <stop offset="40%" stop-color="{palette['spot1_glow']}" stop-opacity="0.70" />
      <stop offset="75%" stop-color="{palette['aura_inner']}" stop-opacity="0.45" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>
    <radialGradient id="sphereBody" cx="42%" cy="38%" r="62%">
      {solar_body_stops}
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
  <circle cx="{c}" cy="{c}" r="{canvas_size // 2 - 12}" fill="url(#ambientSpill)" filter="url(#spillBlur)" />
  <circle cx="{c}" cy="{c}" r="{r_aura_outer}" fill="url(#outerAura)" filter="url(#auraDeep)" />
  <circle cx="{c}" cy="{c}" r="{r_aura_inner}" fill="url(#innerAura)" filter="url(#auraMid)" />
  {extra_solar_rings}
  <circle cx="{c}" cy="{c}" r="{r_sphere}" fill="url(#sphereBody)" />
  <g clip-path="url(#sphereClip)">
    <ellipse cx="{swirl1_x}" cy="{swirl1_y}" rx="{swirl1_rx}" ry="{swirl1_ry}" fill="url(#primarySpot)" opacity="0.85" filter="url(#coreBlur)" />
    <ellipse cx="{swirl2_x}" cy="{swirl2_y}" rx="{swirl2_rx}" ry="{swirl2_ry}" fill="url(#secondarySpot)" opacity="0.80" filter="url(#coreBlur)" />
    <path d="{arc_path}" fill="none" stroke="{palette['body_c0']}" stroke-width="3.5" opacity="0.60" filter="url(#coreBlur)" />
    <ellipse cx="{spot2_x}" cy="{spot2_y}" rx="{spot2_rx}" ry="{spot2_ry}" fill="url(#secondarySpot)" filter="url(#coreBlur)" />
    <ellipse cx="{spot1_x}" cy="{spot1_y}" rx="{spot1_rx}" ry="{spot1_ry}" fill="url(#primarySpot)" filter="url(#coreBlur)" />
    <circle cx="{spot1_x}" cy="{spot1_y}" r="{int(spot1_rx * 0.45)}" fill="{palette['spot1_core']}" opacity="0.98" filter="url(#coreBlur)" />
    <circle cx="{c}" cy="{c}" r="{r_sphere - 3}" fill="none" stroke="{palette['rim_stroke']}" stroke-width="4.5" opacity="0.55" filter="url(#coreBlur)" />
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
        self.pollinations = PollinationsProvider(api_key=api_key)
        self.bg_cache_dir = Path("output") / "thumbnails" / "bg_cache"
        self.bg_cache_dir.mkdir(parents=True, exist_ok=True)

    def detect_theme(self, topic: str, hook: str, theme_override: Optional[str] = None) -> Dict[str, Any]:
        """Detects the optimal color theme based on semantic keywords or explicit override."""
        if theme_override and theme_override.lower() in TEXT_THEMES:
            return TEXT_THEMES[theme_override.lower()]

        if theme_override == "random":
            return random.choice(list(TEXT_THEMES.values()))

        # Normalize text and search keywords
        full_text = f"{topic} {hook}".lower()
        full_text = full_text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

        # Priority order
        theme_keys = ["chrono", "cyber", "supernova", "singularity", "hyper_pink", "aurora"]
        for t_key in theme_keys:
            theme_def = TEXT_THEMES[t_key]
            for kw in theme_def["keywords"]:
                norm_kw = kw.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                if re.search(r"(?i)\b" + re.escape(norm_kw) + r"\b", full_text):
                    return theme_def

        # Deterministic fallback based on hash
        hash_val = int(hashlib.md5(full_text.encode("utf-8")).hexdigest()[:8], 16)
        all_themes = list(TEXT_THEMES.values())
        return all_themes[hash_val % len(all_themes)]

    def generate_ai_background(self, topic: str, hook: str, theme: Dict[str, Any]) -> Image.Image:
        """
        Generates a photorealistic, cinematic deep-space cosmic background using Pollinations AI
        customized to the specific debate topic, with smooth procedural fallback.
        """
        # Create unique cache filename per topic+hook
        hash_id = hashlib.md5(f"{topic}_{hook}".encode("utf-8")).hexdigest()[:12]
        cached_bg = self.bg_cache_dir / f"bg_{hash_id}.jpg"

        if cached_bg.exists() and cached_bg.stat().st_size > 5000:
            try:
                img = Image.open(cached_bg).convert("RGBA")
                return ImageOps.fit(img, (1080, 1920), method=Image.Resampling.LANCZOS)
            except Exception:
                pass

        # Build prompt emphasizing cinematic scale and deep cosmic contrast
        concept = theme.get("prompt_concept", "deep space nebula wallpaper, starfield, cosmic dust clouds")
        prompt = (
            f"Cinematic 8k vertical deep space wallpaper of {concept}, "
            f"intense celestial glow, stellar dust filaments, photorealistic astrophotography, "
            f"dark cosmic void, epic depth, no text, no words, no letters, no watermark, no logos, clean image"
        )

        print(f"   🤖 [AI Background] Generando fondo espacial con IA...")
        print(f"      Prompt: '{concept[:60]}...'")
        success = False
        try:
            success = self.pollinations.generate_image(
                prompt=prompt,
                out_path=cached_bg,
                width=768,
                height=1344,
                model="turbo",
                seed=int(hash_id, 16) % 100000,
                max_retries=1,
                timeout=12
            )
        except Exception as e:
            print(f"      ⚠️ No se pudo contactar a Pollinations ({e}), usando fondo procedimental.")

        if success and cached_bg.exists():
            try:
                img = Image.open(cached_bg).convert("RGBA")
                print(f"      ✨ Fondo IA generado y guardado en caché.")
                return ImageOps.fit(img, (1080, 1920), method=Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"      ⚠️ Error abriendo imagen IA ({e}), usando fondo procedimental.")

        # Procedural fallback: Rich atmospheric cosmic gradient and nebula
        W, H = 1080, 1920
        bg = Image.new("RGBA", (W, H), (6, 8, 20, 255))
        draw = ImageDraw.Draw(bg)
        for y in range(H):
            f = y / H
            r = int(14 * (1.0 - f) + 4 * f)
            g = int(8 * (1.0 - f) + 4 * f)
            b = int(32 * (1.0 - f) + 12 * f)
            draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

        # Starfield
        rng = random.Random(int(hash_id, 16))
        for _ in range(350):
            sx = rng.randint(0, W)
            sy = rng.randint(0, H)
            sr = rng.choice([1, 1, 2])
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255, rng.randint(120, 255)))

        return bg

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
        glow_color: Tuple[int, int, int] = (0, 229, 255),
    ):
        """Renders multiline text with emotional trigger words highlighted in theme neon accent."""
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
                clean_w = re.sub(r"[^A-ZÁÉÍÓÚÑ]", "", w.upper())
                is_highlight = (clean_w in VIRAL_TRIGGER_WORDS) or (len(clean_w) >= 6 and clean_w.isupper())

                text_fill = highlight_color if is_highlight else (255, 255, 255, 255)

                # 1. Deep drop shadow for maximum separation
                draw.text((curr_x + 5, curr_y + 5), w, font=font, fill=(0, 0, 0, 255))
                draw.text((curr_x + 3, curr_y + 3), w, font=font, fill=(0, 0, 0, 255))

                # 2. Atmospheric luminous aura
                glow_fill = (*highlight_color, 190) if is_highlight else (*glow_color, 140)
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
        with AI background, authentic Quantum/Solar video orbs, and optimized vertical space.
        """
        theme = self.detect_theme(topic, hook, theme_override=theme_name)
        clean_headline, clean_sub = self.format_title_text(hook, topic)
        W, H = 1080, 1920

        print(f"\n🎨 [Thumbnail Render] Tema Visual: '{theme['name']}'")
        print(f"   • Orbes: Quantum (#00e5ff) vs Solar (#ffb300) [Idénticos al vídeo]")
        print(f"   • Resaltado tipográfico: RGB{theme['highlight_color']}")

        # 1. Generate or load contextual AI Background
        ai_bg = self.generate_ai_background(topic, hook, theme)

        # 2. Apply cinematic dark scrim gradient so text and orbs pop out
        scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(scrim)
        for y in range(H):
            # Controlled opacity: darker behind headline and bottom CTA, translucent in center
            if y < 680:
                alpha = int(185 + (680 - y) * 0.08)
            elif y > 1460:
                alpha = int(195 + (y - 1460) * 0.12)
            else:
                alpha = 115
            alpha = min(245, max(85, alpha))
            sdraw.line([(0, y), (W, y)], fill=(6, 8, 18, alpha))

        poster = Image.alpha_composite(ai_bg, scrim)

        # 3. Volumetric nebula glows behind the orbs
        nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ndraw = ImageDraw.Draw(nebula)
        # Left cyan glow for Quantum
        ndraw.ellipse([-160, 720, 640, 1420], fill=(0, 229, 255, 55))
        # Right amber glow for Solar
        ndraw.ellipse([W - 640, 720, W + 160, 1420], fill=(255, 171, 0, 55))
        # Center clash flare
        ndraw.ellipse([W // 2 - 200, 880, W // 2 + 200, 1260], fill=(*theme["highlight_color"], 30))
        nebula = nebula.filter(ImageFilter.GaussianBlur(80))
        poster = Image.alpha_composite(poster, nebula)

        # 4. Render and place AUTHENTIC VIDEO ORBS (Always Quantum and Solar!)
        orb_size = 520
        orb_quantum = render_orb_asset("quantum", size=orb_size)
        orb_solar = render_orb_asset("solar", size=orb_size)

        # Better space utilization: larger, majestic placement in center zone
        orb_y = 770
        q_pos = (int(W * 0.02), orb_y)
        s_pos = (int(W * 0.50), orb_y)
        poster.paste(orb_quantum, q_pos, orb_quantum)
        poster.paste(orb_solar, s_pos, orb_solar)

        # 5. Energy divide, procedural lightning arcs & Center VS Shield
        vs_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        vdraw = ImageDraw.Draw(vs_layer)
        vs_cx = W // 2
        vs_cy = orb_y + orb_size // 2

        # Vertical energetic boundary line
        vdraw.line([(vs_cx, 730), (vs_cx, 1370)], fill=(255, 255, 255, 70), width=3)
        vdraw.line([(vs_cx - 1, 800), (vs_cx - 1, 1300)], fill=(0, 240, 255, 140), width=2)
        vdraw.line([(vs_cx + 1, 800), (vs_cx + 1, 1300)], fill=(255, 180, 0, 140), width=2)

        # Procedural electric lightning crackles between orbs
        rng = random.Random(int(hashlib.md5(f"{topic}_{hook}".encode()).hexdigest()[:8], 16))
        lightning_colors = [
            (0, 240, 255, 200),
            (255, 215, 0, 200),
            (255, 255, 255, 220),
            (*theme["highlight_color"], 180)
        ]
        for _ in range(5):
            bolt_color = rng.choice(lightning_colors)
            cur_lx = vs_cx + rng.randint(-35, 35)
            cur_ly = 810 + rng.randint(0, 30)
            target_ly = 1270 + rng.randint(-30, 0)
            while cur_ly < target_ly:
                next_lx = cur_lx + rng.randint(-18, 18)
                next_ly = cur_ly + rng.randint(25, 55)
                vdraw.line([(cur_lx, cur_ly), (next_lx, next_ly)], fill=bolt_color, width=rng.choice([1, 2]))
                cur_lx, cur_ly = next_lx, next_ly

        # Center VS Metallic Shield (Radiant Gold Border)
        vdraw.ellipse([vs_cx - 58, vs_cy - 58, vs_cx + 58, vs_cy + 58], fill=(10, 14, 28, 245), outline=(255, 215, 0, 255), width=4)
        vs_font = get_font(48)
        vbbox = vdraw.textbbox((0, 0), "VS", font=vs_font)
        vw = vbbox[2] - vbbox[0]
        vh = vbbox[3] - vbbox[1]
        vdraw.text((vs_cx - vw // 2, vs_cy - vh // 2 - 4), "VS", font=vs_font, fill=(255, 215, 0))
        poster = Image.alpha_composite(poster, vs_layer)

        # 6. Entity Badges below orbs (Always CUÁNTICO on left and SOLAR on right)
        badge_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(badge_layer)
        badge_font = get_font(28)

        # Left Badge: ⚛ CUÁNTICO (Cyan)
        b_label_l = "⚛  CUÁNTICO"
        bdraw.rounded_rectangle([110, 1335, 410, 1400], radius=18, fill=(6, 24, 40, 240), outline=(0, 229, 255, 255), width=3)
        bbbox_l = bdraw.textbbox((0, 0), b_label_l, font=badge_font)
        bw_l = bbbox_l[2] - bbbox_l[0]
        bdraw.text((110 + (300 - bw_l) // 2, 1351), b_label_l, font=badge_font, fill=(0, 240, 255))

        # Right Badge: ☀ SOLAR (Gold)
        b_label_r = "☀  SOLAR"
        bdraw.rounded_rectangle([W - 410, 1335, W - 110, 1400], radius=18, fill=(40, 24, 8, 240), outline=(255, 180, 0, 255), width=3)
        bbbox_r = bdraw.textbbox((0, 0), b_label_r, font=badge_font)
        bw_r = bbbox_r[2] - bbbox_r[0]
        bdraw.text((W - 410 + (300 - bw_r) // 2, 1351), b_label_r, font=badge_font, fill=(255, 200, 50))

        poster = Image.alpha_composite(poster, badge_layer)

        # 7. Hero Headline Glass Card (Maximizing top space, tight padding, big text)
        title_card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        tdraw = ImageDraw.Draw(title_card)

        # Top Eyebrow Tag
        eyebrow_font = get_font(25)
        eb_text = theme["eyebrow_text"]
        ebbox = tdraw.textbbox((0, 0), eb_text, font=eyebrow_font)
        ebw = ebbox[2] - ebbox[0]
        eb_x = (W - ebw) // 2
        tdraw.rounded_rectangle([eb_x - 26, 75, eb_x + ebw + 26, 128], radius=16, fill=(8, 14, 30, 235), outline=theme["eyebrow_border"], width=2)
        tdraw.text((eb_x, 89), eb_text, font=eyebrow_font, fill=theme["eyebrow_color"])

        # Main Title Card Glass Box (From y=145 to y=665)
        card_x1, card_y1, card_x2, card_y2 = 40, 145, W - 40, 665
        tdraw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=28, fill=(10, 14, 28, 235), outline=theme["card_border"], width=3)
        # Accent gradient top line
        tdraw.line([(card_x1 + 30, card_y1), (card_x2 - 30, card_y1)], fill=theme["accent_line"], width=4)

        # Word wrap Headline Text with LARGE, impactful typography
        title_font = get_font(66)
        words = clean_headline.split()
        lines: List[str] = []
        curr: List[str] = []
        max_line_w = card_x2 - card_x1 - 70

        for w in words:
            curr.append(w)
            tb = tdraw.textbbox((0, 0), " ".join(curr), font=title_font)
            if (tb[2] - tb[0]) > max_line_w:
                curr.pop()
                lines.append(" ".join(curr))
                curr = [w]
        if curr:
            lines.append(" ".join(curr))

        # Limit to max 4 lines
        lines = lines[:4]
        line_spacing = 84
        start_headline_y = card_y1 + 40

        # Render headline with highlighted viral keywords in theme color
        self.render_highlighted_headline(
            draw=tdraw,
            lines=lines,
            start_y=start_headline_y,
            line_height=line_spacing,
            font=title_font,
            canvas_width=W,
            highlight_color=theme["highlight_color"],
            glow_color=theme["secondary_color"],
        )

        # Subtitle Pill inside the bottom of the card
        sub_font = get_font(28)
        stb = tdraw.textbbox((0, 0), clean_sub, font=sub_font)
        stw = stb[2] - stb[0]
        stx = (W - stw) // 2
        sub_y = card_y2 - 62
        tdraw.rounded_rectangle([stx - 22, sub_y - 8, stx + stw + 22, sub_y + 40], radius=14, fill=(16, 24, 44, 210), outline=(*theme["secondary_color"], 160), width=1)
        tdraw.text((stx, sub_y + 2), clean_sub, font=sub_font, fill=theme["secondary_color"])

        # 8. Bottom Zone: High-CTR Call To Action + Curiosity Badge
        cta_font = get_font(34)
        cta_text = theme["cta_text"]
        ctb = tdraw.textbbox((0, 0), cta_text, font=cta_font)
        ctw = ctb[2] - ctb[0]
        cx = (W - ctw) // 2
        tdraw.rounded_rectangle([cx - 36, 1500, cx + ctw + 36, 1575], radius=24, fill=(12, 18, 38, 240), outline=theme["cta_border"], width=3)
        tdraw.text((cx, 1519), cta_text, font=cta_font, fill=theme["cta_color"])

        # Channel & Engagement badge
        extra_font = get_font(22)
        extra_text = "🎙️  COSMIC DEBATE EXPRESS  •  COMENTA TU TEORÍA"
        etb = tdraw.textbbox((0, 0), extra_text, font=extra_font)
        etw = etb[2] - etb[0]
        ex = (W - etw) // 2
        tdraw.rounded_rectangle([ex - 20, 1615, ex + etw + 20, 1665], radius=14, fill=(8, 12, 24, 210), outline=(255, 255, 255, 60), width=1)
        tdraw.text((ex, 1629), extra_text, font=extra_font, fill=(210, 225, 255))

        poster = Image.alpha_composite(poster, title_card)

        # 9. Save final studio thumbnail
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_rgb = poster.convert("RGB")
        final_rgb.save(output_path, "JPEG", quality=96)
        print(f"  ✨ ¡Portada cinematográfica generada con éxito en: {output_path}!")
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
