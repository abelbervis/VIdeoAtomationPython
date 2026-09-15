"""
Futuristic Sci-Fi Glassmorphism Floating Card Generator.
Refactored to match modern Apple / Vercel floating notification & frosted glass aesthetic
with corrected proportions, natural typography line heights, and luminous glass gradients.
"""

from pathlib import Path
from typing import Optional


def generate_hologram_card_svg(
    title: str = "FÍSICA CUÁNTICA",
    subtitle: str = "Estado: Superposición |ψ⟩ = α|0⟩ + β|1⟩",
    category: str = "CONCEPTO",
    color_theme: str = "cyan",  # "cyan", "amber", "purple"
    width: int = 620,
    height: int = 240,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Generates a high-end, perfectly proportioned floating card based on Apple/Vercel notification UI
    and frosted glassmorphism references.
    """
    if color_theme == "amber":
        accent_color = "#ffb300"
        pill_bg = "#3d2b00"
        pill_border = "#996a00"
        glow_color = "#ff9100"
    elif color_theme == "purple":
        accent_color = "#e040fb"
        pill_bg = "#2b003d"
        pill_border = "#8e00b3"
        glow_color = "#d500f9"
    else:  # cyan / default
        accent_color = "#00f0ff"
        pill_bg = "#002a3a"
        pill_border = "#007799"
        glow_color = "#00e5ff"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <!-- Soft Drop Shadow for Real Elevation Depth -->
    <filter id="cardShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#000000" flood-opacity="0.80" />
      <feDropShadow dx="0" dy="2" stdDeviation="6" flood-color="{glow_color}" flood-opacity="0.25" />
    </filter>

    <!-- Frosted Translucent Glass Gradient (Image 1 Frosted Aesthetics) -->
    <linearGradient id="glassGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#142238" stop-opacity="0.82" />
      <stop offset="60%" stop-color="#0b1322" stop-opacity="0.85" />
      <stop offset="100%" stop-color="#060912" stop-opacity="0.90" />
    </linearGradient>

    <!-- Inner Radial Glow for Glass Shimmer -->
    <radialGradient id="innerGlassShimmer" cx="20%" cy="20%" r="80%">
      <stop offset="0%" stop-color="{accent_color}" stop-opacity="0.20" />
      <stop offset="50%" stop-color="{accent_color}" stop-opacity="0.04" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <!-- Hairline Luminous Border Reflection -->
    <linearGradient id="borderGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.55" />
      <stop offset="35%" stop-color="{accent_color}" stop-opacity="0.75" />
      <stop offset="100%" stop-color="{accent_color}" stop-opacity="0.20" />
    </linearGradient>

    <!-- Icon Neon Glow -->
    <filter id="iconGlow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- Main Translucent Frosted Glass Card Body -->
  <rect x="16" y="16" width="{width - 32}" height="{height - 32}" rx="28" ry="28" 
        fill="url(#glassGradient)" 
        filter="url(#cardShadow)" />

  <!-- Inner Ambient Shimmer Layer -->
  <rect x="16" y="16" width="{width - 32}" height="{height - 32}" rx="28" ry="28" 
        fill="url(#innerGlassShimmer)" />

  <!-- Crisp Luminous Glass Border Stroke -->
  <rect x="16" y="16" width="{width - 32}" height="{height - 32}" rx="28" ry="28" 
        fill="none" 
        stroke="url(#borderGradient)" 
        stroke-width="1.6" />

  <!-- Top Pill Badge (Apple / Vercel Notification Style) -->
  <g transform="translate(42, 40)">
    <!-- Pill Container -->
    <rect x="0" y="0" width="138" height="32" rx="16" ry="16" 
          fill="{pill_bg}" fill-opacity="0.90" 
          stroke="{pill_border}" stroke-width="1.2" />

    <!-- Sparkle Icon Circle (✦) -->
    <circle cx="16" cy="16" r="9" fill="{accent_color}" filter="url(#iconGlow)" />
    <!-- 4-Point Sparkle Star inside circle -->
    <path d="M 16 10 L 17 14.5 L 21.5 16 L 17 17.5 L 16 22 L 15 17.5 L 10.5 16 L 15 14.5 Z" fill="#040810" />

    <!-- Category Label Text -->
    <text x="34" y="21" font-family="'Montserrat', 'Inter', 'Arial', sans-serif" 
          font-size="12" font-weight="700" fill="{accent_color}" letter-spacing="1.5">
      {category}
    </text>
  </g>

  <!-- Title Text (Proportional, Bold, Crisp White) -->
  <text x="42" y="124" font-family="'Montserrat', 'Inter', 'Arial', sans-serif" 
        font-size="28" font-weight="800" fill="#ffffff" letter-spacing="0.5">
    {title}
  </text>

  <!-- Subtitle Text (Subtle Secondary Gray Text) -->
  <text x="42" y="164" font-family="'Inter', 'Arial', sans-serif" 
        font-size="16" font-weight="400" fill="#a0aec0" letter-spacing="0.3">
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
