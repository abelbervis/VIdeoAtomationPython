"""
Futuristic Sci-Fi Hologram & Floating Reference Card Generator.
Generates SVG vector hologram overlays with scanlines, corner reticles, glowing borders,
diagrams, and projector light beams.
"""

from pathlib import Path
from typing import Optional


def generate_hologram_card_svg(
    title: str = "FÍSICA CUÁNTICA",
    subtitle: str = "Estado: Superposición |ψ⟩ = α|0⟩ + β|1⟩",
    category: str = "CONCEPTO",
    color_theme: str = "cyan",  # "cyan", "amber", "purple"
    width: int = 540,
    height: int = 320,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Generates a high-tech sci-fi glassmorphism hologram SVG card with scanlines,
    glowing borders, corner crosshairs, and dynamic vector icons.
    """
    if color_theme == "amber":
        primary_color = "#ffb300"
        secondary_color = "#ff6d00"
        bg_glow = "#ff9100"
    elif color_theme == "purple":
        primary_color = "#d500f9"
        secondary_color = "#651fff"
        bg_glow = "#aa00ff"
    else:  # cyan
        primary_color = "#00f0ff"
        secondary_color = "#0077ff"
        bg_glow = "#00e5ff"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <!-- Background Glass Glow Gradient -->
    <radialGradient id="holoBg" cx="50%" cy="50%" r="70%">
      <stop offset="0%" stop-color="{primary_color}" stop-opacity="0.18" />
      <stop offset="60%" stop-color="#070d1a" stop-opacity="0.75" />
      <stop offset="100%" stop-color="#04070f" stop-opacity="0.90" />
    </radialGradient>

    <!-- Border Glow Filter -->
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <!-- Scanlines Pattern -->
    <pattern id="scanlines" width="100" height="6" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="100" y2="0" stroke="{primary_color}" stroke-opacity="0.12" stroke-width="1.5" />
    </pattern>

    <!-- Holographic Beam Cone (Bottom Projector) -->
    <linearGradient id="beamGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{primary_color}" stop-opacity="0.45" />
      <stop offset="100%" stop-color="{primary_color}" stop-opacity="0.0" />
    </linearGradient>
  </defs>

  <!-- Main Hologram Container Card -->
  <rect x="12" y="12" width="{width - 24}" height="{height - 36}" rx="16" ry="16" 
        fill="url(#holoBg)" stroke="{primary_color}" stroke-width="2" stroke-opacity="0.85" filter="url(#glow)" />

  <!-- Inner Scanline Texture -->
  <rect x="12" y="12" width="{width - 24}" height="{height - 36}" rx="16" ry="16" 
        fill="url(#scanlines)" />

  <!-- Corner Tech Reticles (+) -->
  <g stroke="{primary_color}" stroke-width="2" stroke-opacity="0.9">
    <!-- Top Left -->
    <path d="M 24 28 L 40 28 M 28 24 L 28 40" />
    <!-- Top Right -->
    <path d="M {width - 40} 28 L {width - 24} 28 M {width - 28} 24 L {width - 28} 40" />
    <!-- Bottom Left -->
    <path d="M 24 {height - 52} L 40 {height - 52} M 28 {height - 56} L 28 {height - 40}" />
    <!-- Bottom Right -->
    <path d="M {width - 40} {height - 52} L {width - 24} {height - 52} M {width - 28} {height - 56} L {width - 28} {height - 40}" />
  </g>

  <!-- Top Category Tag -->
  <rect x="36" y="32" width="120" height="22" rx="4" fill="{primary_color}" fill-opacity="0.2" stroke="{primary_color}" stroke-width="1" stroke-opacity="0.6"/>
  <text x="96" y="47" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="{primary_color}" letter-spacing="1.5" text-anchor="middle">
    {category}
  </text>

  <!-- Central Atom / Holographic Diagram Icon -->
  <g transform="translate(70, 160)" filter="url(#glow)">
    <!-- Central Nucleus -->
    <circle cx="0" cy="0" r="10" fill="{primary_color}" />
    <!-- Orbit 1 -->
    <ellipse cx="0" cy="0" rx="38" ry="14" fill="none" stroke="{primary_color}" stroke-width="1.8" stroke-dasharray="4,2" transform="rotate(30)" opacity="0.85" />
    <!-- Orbit 2 -->
    <ellipse cx="0" cy="0" rx="38" ry="14" fill="none" stroke="{secondary_color}" stroke-width="1.8" transform="rotate(-30)" opacity="0.85" />
    <!-- Electron Dots -->
    <circle cx="28" cy="-12" r="3.5" fill="#ffffff" />
    <circle cx="-25" cy="14" r="3.5" fill="{primary_color}" />
  </g>

  <!-- Main Title Text -->
  <text x="140" y="140" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="#ffffff" filter="url(#glow)" letter-spacing="1">
    {title}
  </text>

  <!-- Subtitle / Formula Text -->
  <text x="140" y="180" font-family="Arial, sans-serif" font-size="16" fill="{primary_color}" fill-opacity="0.95">
    {subtitle}
  </text>

  <!-- Bottom Holographic Light Beam Cone -->
  <polygon points="{width//2 - 40},{height - 24} {width//2 + 40},{height - 24} {width//2 + 90},{height} {width//2 - 90},{height}" 
           fill="url(#beamGrad)" />
</svg>
"""

    if output_path is None:
        output_path = Path("output/hologram_sample.svg")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return output_path
