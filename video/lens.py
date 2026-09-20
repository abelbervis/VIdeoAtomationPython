"""
Gravitational Lens Visual Support Generator.
Generates an ultra-refined, circular/elliptical Gravitational Lens Projection asset:
- Outer Astrometric Reticle & Gravitational Refraction Rim (Cyan / Amber / Purple / Emerald / Crimson)
- Circular/Oval masked image/illustration projection with subtle chromatic aberration
- Concept Badge & Key Term label
- Bioluminescent particle sparks around the lens perimeter
"""

import base64
from pathlib import Path
from typing import Optional, Tuple


def _hex_to_rgb_str(hex_color: str) -> str:
    clean = hex_color.strip().lstrip("#")
    if len(clean) == 3:
        clean = "".join(c + c for c in clean)
    try:
        val = int(clean, 16)
        r = (val >> 16) & 255
        g = (val >> 8) & 255
        b = val & 255
        return f"{r}, {g}, {b}"
    except Exception:
        return "0, 240, 255"


def generate_gravitational_lens_svg(
    concept_badge: str = "NEUROCIENCIA EVOLUTIVA",
    key_term: str = "CIRCUITOS DE DOPAMINA",
    image_path: Optional[Path] = None,
    color_theme: str = "cyan",  # "cyan", "amber", "purple", "emerald", "crimson"
    width: int = 560,
    height: int = 420,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Generates a Gravitational Lens Projection SVG asset.
    If image_path is provided and exists, embeds it as a base64 encoded image inside the circular aperture.
    """
    if color_theme == "amber":
        accent_hex = "#ffea00"
        glow_hex = "#ff9100"
        rim_hex = "#ff3d00"
    elif color_theme == "purple":
        accent_hex = "#d500f9"
        glow_hex = "#7c4dff"
        rim_hex = "#304ffe"
    elif color_theme == "emerald":
        accent_hex = "#00ff9d"
        glow_hex = "#00e676"
        rim_hex = "#00b0ff"
    elif color_theme == "crimson":
        accent_hex = "#ff1744"
        glow_hex = "#ff5252"
        rim_hex = "#ffd600"
    else:  # cyan / default
        accent_hex = "#00f0ff"
        glow_hex = "#0284c7"
        rim_hex = "#3b82f6"

    rgb_accent = _hex_to_rgb_str(accent_hex)
    rgb_glow = _hex_to_rgb_str(glow_hex)

    # Center coordinates & lens radius
    cx = width // 2
    cy = height // 2 - 10
    lens_r = 135

    # Encode image if provided
    img_embed_data = ""
    if image_path and Path(image_path).exists():
        try:
            raw_bytes = Path(image_path).read_bytes()
            b64_str = base64.b64encode(raw_bytes).decode("utf-8")
            suffix = Path(image_path).suffix.lower().replace(".", "")
            mime = "image/png" if suffix in ["png", "webp"] else "image/jpeg"
            img_embed_data = f"data:{mime};base64,{b64_str}"
        except Exception:
            img_embed_data = ""

    image_element_svg = ""
    if img_embed_data:
        image_element_svg = f"""
    <image href="{img_embed_data}" x="{cx - lens_r}" y="{cy - lens_r}" width="{lens_r * 2}" height="{lens_r * 2}" preserveAspectRatio="xMidYMid slice" clip-path="url(#lensClip)" />
    <!-- Chromatic Aberration & Lens Glass Reflection -->
    <circle cx="{cx}" cy="{cy}" r="{lens_r}" fill="url(#lensGlassGrad)" mix-blend-mode="overlay" opacity="0.65" clip-path="url(#lensClip)" />
"""
    else:
        # Abstract Procedural Gravitational Singularity Pattern if no external image
        image_element_svg = f"""
    <!-- Procedural Cosmic Core -->
    <circle cx="{cx}" cy="{cy}" r="{lens_r}" fill="url(#proceduralSingularity)" clip-path="url(#lensClip)" />
    <circle cx="{cx - 30}" cy="{cy - 35}" r="{lens_r * 0.45}" fill="{accent_hex}" opacity="0.35" filter="url(#lensBlur)" clip-path="url(#lensClip)" />
    <circle cx="{cx + 40}" cy="{cy + 30}" r="{lens_r * 0.35}" fill="{glow_hex}" opacity="0.25" filter="url(#lensBlur)" clip-path="url(#lensClip)" />
"""

    badge_text_clean = concept_badge.upper().strip()
    term_text_clean = key_term.upper().strip()

    dest_path = output_path or (Path(__file__).resolve().parent.parent / "assets" / "lenses" / "gravitational_lens.svg")
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <!-- Filters for Gravitational Lens Optics -->
    <filter id="lensGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="12" result="blur1" />
      <feGaussianBlur stdDeviation="4" result="blur2" />
      <feMerge>
        <feMergeNode in="blur1" />
        <feMergeNode in="blur2" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <filter id="lensBlur" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="16" />
    </filter>

    <clipPath id="lensClip">
      <circle cx="{cx}" cy="{cy}" r="{lens_r}" />
    </clipPath>

    <!-- Glass Lens Reflections -->
    <linearGradient id="lensGlassGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.38" />
      <stop offset="40%" stop-color="{accent_hex}" stop-opacity="0.12" />
      <stop offset="80%" stop-color="#000000" stop-opacity="0.40" />
      <stop offset="100%" stop-color="{glow_hex}" stop-opacity="0.25" />
    </linearGradient>

    <!-- Procedural Singularity Gradient -->
    <radialGradient id="proceduralSingularity" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{accent_hex}" stop-opacity="0.95" />
      <stop offset="40%" stop-color="{glow_hex}" stop-opacity="0.65" />
      <stop offset="80%" stop-color="#070a14" stop-opacity="0.90" />
      <stop offset="100%" stop-color="#020306" stop-opacity="1.0" />
    </radialGradient>

    <!-- Reticle Outer Halo -->
    <radialGradient id="outerAura" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="rgba({rgb_accent}, 0.35)" />
      <stop offset="60%" stop-color="rgba({rgb_glow}, 0.12)" />
      <stop offset="100%" stop-color="rgba(0, 0, 0, 0)" />
    </radialGradient>
  </defs>

  <!-- 1. Ambient Background Halo -->
  <circle cx="{cx}" cy="{cy}" r="{lens_r + 45}" fill="url(#outerAura)" filter="url(#lensBlur)" />

  <!-- 2. Main Lens Aperture & Image Content -->
  {image_element_svg}

  <!-- 3. Astrometric Refraction Ring & Reticle Overlay -->
  <circle cx="{cx}" cy="{cy}" r="{lens_r}" fill="none" stroke="{accent_hex}" stroke-width="2.2" opacity="0.88" filter="url(#lensGlow)" />
  <circle cx="{cx}" cy="{cy}" r="{lens_r + 6}" fill="none" stroke="rgba({rgb_glow}, 0.60)" stroke-width="1.2" stroke-dasharray="8 14 28 14" opacity="0.75" />
  <circle cx="{cx}" cy="{cy}" r="{lens_r + 14}" fill="none" stroke="{accent_hex}" stroke-width="1.0" stroke-dasharray="3 9" opacity="0.50" />

  <!-- Orbital Spark Particles around Lens Rim -->
  <circle cx="{cx - lens_r + 12}" cy="{cy - 45}" r="3.2" fill="#ffffff" opacity="0.95" filter="url(#lensGlow)" />
  <circle cx="{cx + lens_r - 18}" cy="{cy + 52}" r="2.8" fill="{accent_hex}" opacity="0.85" />
  <circle cx="{cx + 65}" cy="{cy - lens_r + 8}" r="2.2" fill="{glow_hex}" opacity="0.90" />

  <!-- 4. Top Concept Badge -->
  <g transform="translate({cx}, {cy - lens_r - 28})">
    <rect x="-150" y="-16" width="300" height="32" rx="16" fill="rgba(8, 12, 22, 0.88)" stroke="{accent_hex}" stroke-width="1.4" filter="url(#lensGlow)" />
    <text x="0" y="5" font-family="'Plus Jakarta Sans', system-ui, -apple-system, sans-serif" font-weight="700" font-size="12" fill="{accent_hex}" text-anchor="middle" letter-spacing="2.5">
      {badge_text_clean}
    </text>
  </g>

  <!-- 5. Bottom Key Term Label -->
  <g transform="translate({cx}, {cy + lens_r + 32})">
    <rect x="-170" y="-18" width="340" height="36" rx="18" fill="rgba(4, 6, 12, 0.92)" stroke="rgba({rgb_accent}, 0.65)" stroke-width="1.2" />
    <text x="0" y="6" font-family="'Plus Jakarta Sans', system-ui, -apple-system, sans-serif" font-weight="800" font-size="14" fill="#ffffff" text-anchor="middle" letter-spacing="2.0">
      {term_text_clean}
    </text>
  </g>
</svg>"""

    dest_path.write_text(svg_content, encoding="utf-8")
    return dest_path
