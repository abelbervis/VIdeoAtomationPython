"""
Futuristic Sci-Fi Glassmorphism Floating Card Generator.
Refactored to match modern Apple / Vercel floating notification & frosted glass aesthetic
(as per reference images).
"""

from pathlib import Path
from typing import Optional


def generate_hologram_card_svg(
    title: str = "FÍSICA CUÁNTICA",
    subtitle: str = "Estado: Superposición |ψ⟩ = α|0⟩ + β|1⟩",
    category: str = "CONCEPTO",
    color_theme: str = "cyan",  # "cyan", "amber", "purple"
    width: int = 560,
    height: int = 180,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Generates a high-end, minimalist floating card based on Apple/Vercel notification UI
    and frosted glassmorphism references.
    """
    if color_theme == "amber":
        accent_color = "#ffaa00"
        pill_bg = "#3d2b00"
        pill_border = "#855800"
        glow_color = "#ffb300"
    elif color_theme == "purple":
        accent_color = "#d500f9"
        pill_bg = "#2b003d"
        pill_border = "#6a0085"
        glow_color = "#e040fb"
    else:  # cyan / default
        accent_color = "#00f0ff"
        pill_bg = "#002b3d"
        pill_border = "#006685"
        glow_color = "#00f0ff"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <!-- Soft Drop Shadow for Floating Card Depth -->
    <filter id="cardShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#000000" flood-opacity="0.65" />
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="{accent_color}" flood-opacity="0.15" />
    </filter>

    <!-- Frosted Glass Gradient -->
    <linearGradient id="glassGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#181c28" stop-opacity="0.92" />
      <stop offset="50%" stop-color="#0e111a" stop-opacity="0.88" />
      <stop offset="100%" stop-color="#080a10" stop-opacity="0.94" />
    </linearGradient>

    <!-- Hairline Border Light Reflection -->
    <linearGradient id="borderGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.30" />
      <stop offset="40%" stop-color="{accent_color}" stop-opacity="0.40" />
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.08" />
    </linearGradient>

    <!-- Icon Glow -->
    <filter id="iconGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- Main Floating Card Container -->
  <rect x="12" y="12" width="{width - 24}" height="{height - 24}" rx="24" ry="24" 
        fill="url(#glassGradient)" 
        stroke="url(#borderGradient)" 
        stroke-width="1.2" 
        filter="url(#cardShadow)" />

  <!-- Top Pill Badge (Apple / Vercel Notification Style) -->
  <g transform="translate(36, 34)">
    <!-- Pill Background -->
    <rect x="0" y="0" width="128" height="28" rx="14" ry="14" 
          fill="{pill_bg}" fill-opacity="0.85" 
          stroke="{pill_border}" stroke-width="1" />

    <!-- Blue Sparkle Icon Circle (✦) -->
    <circle cx="14" cy="14" r="8" fill="{accent_color}" filter="url(#iconGlow)" />
    <!-- 4-Point Sparkle Star inside circle -->
    <path d="M 14 9 L 14.8 12.8 L 18 14 L 14.8 15.2 L 14 19 L 13.2 15.2 L 10 14 L 13.2 12.8 Z" fill="#050a14" />

    <!-- Category Label Text -->
    <text x="30" y="18" font-family="'Montserrat', 'Inter', 'Helvetica', 'Arial', sans-serif" 
          font-size="11" font-weight="700" fill="{accent_color}" letter-spacing="1.2">
      {category}
    </text>
  </g>

  <!-- Title Text (Large, Bold, Clean) -->
  <text x="36" y="104" font-family="'Montserrat', 'Inter', 'Helvetica', 'Arial', sans-serif" 
        font-size="25" font-weight="800" fill="#ffffff" letter-spacing="0.4">
    {title}
  </text>

  <!-- Subtitle Text (Subtle Gray/Tinted Data Description) -->
  <text x="36" y="136" font-family="'Inter', 'Roboto', 'Arial', sans-serif" 
        font-size="14" font-weight="400" fill="#94a3b8" letter-spacing="0.2">
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
