"""
Futuristic Sci-Fi Hologram & Floating Reference Card Generator.
Generates ultra-minimalist, elegant glassmorphism projection overlays
inspired by Google / Apple / ElevenLabs futuristic ads.
"""

from pathlib import Path
from typing import Optional


def generate_hologram_card_svg(
    title: str = "FÍSICA CUÁNTICA",
    subtitle: str = "Estado: Superposición  |ψ⟩ = α|0⟩ + β|1⟩",
    category: str = "CONCEPTO",
    color_theme: str = "cyan",  # "cyan", "amber", "purple"
    width: int = 560,
    height: int = 240,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Generates a minimalist, ultra-elegant holographic projection card.
    Uses clean typography, subtle frosted glass luminosity, glowing accent lines,
    and light projector beams instead of heavy boxy HUD frames.
    """
    if color_theme == "amber":
        primary_color = "#ffb300"
        secondary_color = "#ff8f00"
        glow_color = "#ff6d00"
    elif color_theme == "purple":
        primary_color = "#e040fb"
        secondary_color = "#7c4dff"
        glow_color = "#aa00ff"
    else:  # cyan
        primary_color = "#00f0ff"
        secondary_color = "#00b0ff"
        glow_color = "#00e5ff"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <!-- Soft Neon Glow Filter -->
    <filter id="holoGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="8" result="blur1" />
      <feGaussianBlur stdDeviation="3" result="blur2" />
      <feMerge>
        <feMergeNode in="blur1" />
        <feMergeNode in="blur2" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <!-- Subtle Radial Core Glow -->
    <radialGradient id="cardRadialGlow" cx="50%" cy="40%" r="60%">
      <stop offset="0%" stop-color="{primary_color}" stop-opacity="0.15" />
      <stop offset="70%" stop-color="{primary_color}" stop-opacity="0.04" />
      <stop offset="100%" stop-color="#050a14" stop-opacity="0.65" />
    </radialGradient>

    <!-- Bottom Hologram Emitter Light Beam -->
    <linearGradient id="emitterBeam" x1="50%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="{primary_color}" stop-opacity="0.8" />
      <stop offset="40%" stop-color="{primary_color}" stop-opacity="0.25" />
      <stop offset="100%" stop-color="{primary_color}" stop-opacity="0.0" />
    </linearGradient>

    <!-- Horizontal Projection Accent Line -->
    <linearGradient id="lineGlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{primary_color}" stop-opacity="0.0" />
      <stop offset="20%" stop-color="{primary_color}" stop-opacity="0.9" />
      <stop offset="50%" stop-color="#ffffff" stop-opacity="1.0" />
      <stop offset="80%" stop-color="{primary_color}" stop-opacity="0.9" />
      <stop offset="100%" stop-color="{primary_color}" stop-opacity="0.0" />
    </linearGradient>
  </defs>

  <!-- Ethereal Projection Light Pedestal (Bottom Emitter Cone) -->
  <polygon points="{width//2 - 60},{height - 18} {width//2 + 60},{height - 18} {width//2 + 130},{height} {width//2 - 130},{height}" 
           fill="url(#emitterBeam)" />

  <!-- Main Ultra-Minimalist Glass Card Body -->
  <rect x="16" y="16" width="{width - 32}" height="{height - 40}" rx="20" ry="20" 
        fill="url(#cardRadialGlow)" 
        stroke="{primary_color}" stroke-width="1.2" stroke-opacity="0.55" 
        filter="url(#holoGlow)" />

  <!-- Top Accent Glowing Blade Line -->
  <path d="M 40 16 L {width - 40} 16" stroke="url(#lineGlow)" stroke-width="2" />

  <!-- Category Tag (Minimalist Glowing Pill with Bullet) -->
  <g transform="translate(40, 42)">
    <rect x="0" y="0" width="110" height="20" rx="10" 
          fill="{primary_color}" fill-opacity="0.12" 
          stroke="{primary_color}" stroke-width="1" stroke-opacity="0.4" />
    <circle cx="12" cy="10" r="3" fill="{primary_color}" filter="url(#holoGlow)" />
    <text x="24" y="14" font-family="'Montserrat', 'Inter', 'Roboto', 'Arial', sans-serif" 
          font-size="10" font-weight="700" fill="{primary_color}" letter-spacing="1.8">
      {category}
    </text>
  </g>

  <!-- Minimalist Orbital Hologram Icon -->
  <g transform="translate(68, 128)" filter="url(#holoGlow)">
    <circle cx="0" cy="0" r="7" fill="#ffffff" />
    <circle cx="0" cy="0" r="14" fill="none" stroke="{primary_color}" stroke-width="1" stroke-opacity="0.6" />
    <ellipse cx="0" cy="0" rx="32" ry="11" fill="none" stroke="{primary_color}" stroke-width="1.5" transform="rotate(-25)" opacity="0.9" />
    <ellipse cx="0" cy="0" rx="32" ry="11" fill="none" stroke="{secondary_color}" stroke-width="1.5" transform="rotate(35)" opacity="0.7" />
    <circle cx="24" cy="-8" r="3" fill="{primary_color}" />
  </g>

  <!-- Main Title Text -->
  <text x="124" y="118" font-family="'Montserrat', 'Inter', 'Roboto', 'Arial', sans-serif" 
        font-size="26" font-weight="800" fill="#ffffff" filter="url(#holoGlow)" letter-spacing="1.2">
    {title}
  </text>

  <!-- Subtitle / Data Formula Text -->
  <text x="124" y="152" font-family="'Inter', 'Roboto', 'Arial', sans-serif" 
        font-size="14" font-weight="500" fill="{primary_color}" fill-opacity="0.9" letter-spacing="0.5">
    {subtitle}
  </text>

  <!-- Bottom Accent Light Line Base -->
  <path d="M {width//2 - 90} {height - 24} L {width//2 + 90} {height - 24}" 
        stroke="url(#lineGlow)" stroke-width="2.5" />
</svg>
"""

    if output_path is None:
        output_path = Path("output/hologram_sample.svg")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return output_path
