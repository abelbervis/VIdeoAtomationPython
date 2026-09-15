"""
Futuristic Sci-Fi Glassmorphism Floating Card Generator.
Refactored with:
- Warm/Cyan orb projection beam connection (laser glow emitter).
- High-contrast visual hierarchy (dominant title, subtle muted secondary text).
- Minimalist top-line edge glow border (no heavy full box strokes).
- Atmosphere & depth gradient with warm bottom ambient glow from the orb.
- Generous internal padding & breathing room.
"""

from pathlib import Path
from typing import Optional


def generate_hologram_card_svg(
    title: str = "FÍSICA CUÁNTICA",
    subtitle: str = "Estado: Superposición |ψ⟩ = α|0⟩ + β|1⟩",
    category: str = "CONCEPTO",
    color_theme: str = "cyan",  # "cyan", "amber", "purple"
    width: int = 640,
    height: int = 280,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Generates a ultra-refined floating card with projection beam accents,
    high-contrast visual hierarchy, top edge glow border, and orb ambient depth.
    """
    if color_theme == "amber":
        accent_color = "#ffb300"
        pill_bg = "#3a2800"
        pill_border = "#996a00"
        glow_color = "#ff9100"
        beam_color = "#ffa000"
    elif color_theme == "purple":
        accent_color = "#e040fb"
        pill_bg = "#2b003d"
        pill_border = "#8e00b3"
        glow_color = "#d500f9"
        beam_color = "#aa00ff"
    else:  # cyan / default
        accent_color = "#00f0ff"
        pill_bg = "#002838"
        pill_border = "#007799"
        glow_color = "#00e5ff"
        beam_color = "#00f0ff"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <!-- Soft Drop Shadow for Real Elevation Depth -->
    <filter id="cardShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="20" flood-color="#000000" flood-opacity="0.85" />
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="{glow_color}" flood-opacity="0.20" />
    </filter>

    <!-- Translucent Dark Glass Body with Orb Bottom Ambient Aura -->
    <linearGradient id="glassBodyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#101827" stop-opacity="0.88" />
      <stop offset="70%" stop-color="#080d17" stop-opacity="0.92" />
      <stop offset="100%" stop-color="#04070d" stop-opacity="0.95" />
    </linearGradient>

    <!-- Bottom Orb Projection Ambient Glow -->
    <radialGradient id="bottomOrbAura" cx="50%" cy="110%" r="90%">
      <stop offset="0%" stop-color="{accent_color}" stop-opacity="0.22" />
      <stop offset="45%" stop-color="{accent_color}" stop-opacity="0.05" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <!-- Minimalist Top Edge Luminous Blade Gradient -->
    <linearGradient id="topBladeGlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent_color}" stop-opacity="0.0" />
      <stop offset="25%" stop-color="{accent_color}" stop-opacity="0.75" />
      <stop offset="50%" stop-color="#ffffff" stop-opacity="1.0" />
      <stop offset="75%" stop-color="{accent_color}" stop-opacity="0.75" />
      <stop offset="100%" stop-color="{accent_color}" stop-opacity="0.0" />
    </linearGradient>

    <!-- Soft Projection Cone Light Beam Downward -->
    <linearGradient id="projectionBeam" x1="50%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="{beam_color}" stop-opacity="0.6" />
      <stop offset="30%" stop-color="{beam_color}" stop-opacity="0.2" />
      <stop offset="100%" stop-color="{beam_color}" stop-opacity="0.0" />
    </linearGradient>

    <!-- Icon Neon Glow Filter -->
    <filter id="iconGlow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- Projection Connection Beam Cone (Radiating down toward Orb) -->
  <polygon points="{width//2 - 70},{height - 30} {width//2 + 70},{height - 30} {width//2 + 140},{height} {width//2 - 140},{height}" 
           fill="url(#projectionBeam)" />

  <!-- Main Floating Card Outer Rectangle -->
  <rect x="20" y="16" width="{width - 40}" height="{height - 46}" rx="26" ry="26" 
        fill="url(#glassBodyGrad)" 
        filter="url(#cardShadow)" />

  <!-- Bottom Ambient Aura overlay -->
  <rect x="20" y="16" width="{width - 40}" height="{height - 46}" rx="26" ry="26" 
        fill="url(#bottomOrbAura)" />

  <!-- Extremely Subtle Hairline Outer Border (No harsh box border) -->
  <rect x="20" y="16" width="{width - 40}" height="{height - 46}" rx="26" ry="26" 
        fill="none" 
        stroke="{accent_color}" stroke-opacity="0.18" stroke-width="1" />

  <!-- Top Accent Luminous Blade Line -->
  <path d="M 50 16 L {width - 50} 16" stroke="url(#topBladeGlow)" stroke-width="2" />

  <!-- Bottom Projection Emitter Dot Light -->
  <circle cx="{width//2}" cy="{height - 30}" r="3" fill="#ffffff" filter="url(#iconGlow)" />
  <circle cx="{width//2}" cy="{height - 30}" r="7" fill="{accent_color}" fill-opacity="0.4" />

  <!-- Category Pill Badge (Top Left with Padding) -->
  <g transform="translate(48, 44)">
    <rect x="0" y="0" width="136" height="30" rx="15" ry="15" 
          fill="{pill_bg}" fill-opacity="0.88" 
          stroke="{pill_border}" stroke-width="1.2" />

    <!-- Sparkle Icon Circle (✦) -->
    <circle cx="15" cy="15" r="8.5" fill="{accent_color}" filter="url(#iconGlow)" />
    <!-- 4-Point Sparkle Star inside circle -->
    <path d="M 15 9.5 L 16 13.5 L 20 15 L 16 16.5 L 15 20.5 L 14 16.5 L 10 15 L 14 13.5 Z" fill="#040810" />

    <!-- Category Label Text -->
    <text x="32" y="20" font-family="'Montserrat', 'Inter', 'Arial', sans-serif" 
          font-size="11" font-weight="700" fill="{accent_color}" letter-spacing="1.5">
      {category}
    </text>
  </g>

  <!-- Title Text (Dominant, Prominent, Crisp White) -->
  <text x="48" y="128" font-family="'Montserrat', 'Inter', 'Arial', sans-serif" 
        font-size="31" font-weight="800" fill="#ffffff" letter-spacing="0.4">
    {title}
  </text>

  <!-- Subtitle Text (Subtle, Muted Secondary Text with Generous Line Height) -->
  <text x="48" y="168" font-family="'Inter', 'Arial', sans-serif" 
        font-size="15" font-weight="400" fill="#8b9cb0" letter-spacing="0.3">
    {subtitle}
  </text>
</svg>
"""

    if output_path is None:
        output_path = Path("output/hologram_sample.svg")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return output_path
