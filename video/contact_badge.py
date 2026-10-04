"""
Contact & WhatsApp Badge Overlay Manager for Marketing Videos.
Generates crisp, high-contrast, persistent vector badges (WhatsApp Logo + Phone + Location)
and composites them seamlessly onto video renders without blocking captions or product focus.
"""

import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any


class ContactBadgeManager:
    """Generates and manages persistent contact badges for video ads."""

    def __init__(
        self,
        phone: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        location: Optional[str] = None,
        position: str = "top-right",
        video_width: int = 1080,
        video_height: int = 1920,
    ):
        self.phone = phone.strip() if phone else None
        self.city = city.strip() if city else None
        self.country = country.strip() if country else None
        
        # Build composite location string
        if location and location.strip():
            self.location = location.strip()
        elif self.city and self.country:
            self.location = f"{self.city}, {self.country}"
        elif self.city:
            self.location = self.city
        elif self.country:
            self.location = self.country
        else:
            self.location = None

        self.position = position.lower() if position else "top-right"
        self.video_width = video_width
        self.video_height = video_height

    @property
    def is_enabled(self) -> bool:
        """Returns True if there is phone or location information to display."""
        return bool(self.phone or self.location)

    def generate_badge_image(self, output_path: Path) -> Optional[Path]:
        """
        Renders a high-DPI vector SVG badge (WhatsApp icon + phone number + location)
        to a transparent PNG using FFmpeg's built-in SVG engine.
        """
        if not self.is_enabled:
            return None

        output_path.parent.mkdir(parents=True, exist_ok=True)
        svg_path = output_path.with_suffix(".svg")

        # Format display phone
        display_phone = self.phone or ""
        if display_phone and not display_phone.startswith("+") and len(display_phone) >= 10:
            # Clean formatted look
            display_phone = f"{display_phone}"

        # Dynamic dimension calculations
        has_location = bool(self.location)
        max_chars = max(len(display_phone), len(self.location or "") + 3)
        
        # Dynamic pill width based on text length
        char_width = 15 if not has_location else 13
        badge_width = max(380, min(560, 95 + int(max_chars * char_width)))
        badge_height = 84 if has_location else 70
        rx = badge_height // 2

        # Location text snippet
        loc_escaped = (self.location or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        phone_escaped = display_phone.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        loc_svg_element = ""
        if has_location:
            loc_svg_element = f'''
  <!-- Location Pin & Text -->
  <text x="76" y="61" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="16" font-weight="600" fill="#94A3B8" letter-spacing="0.3">📍 {loc_escaped}</text>
'''

        phone_y = 35 if has_location else (badge_height // 2 + 8)
        phone_font_size = 23 if has_location else 25

        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{badge_width}" height="{badge_height}" viewBox="0 0 {badge_width} {badge_height}">
  <defs>
    <!-- Subtle drop shadow filter for pill -->
    <filter id="badgeShadow" x="-10%" y="-15%" width="125%" height="135%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.6"/>
    </filter>
    <!-- WhatsApp Gradient -->
    <linearGradient id="waGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2fe675"/>
      <stop offset="100%" stop-color="#1ea851"/>
    </linearGradient>
    <!-- Background Pill Gradient -->
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0F172A" stop-opacity="0.92"/>
      <stop offset="100%" stop-color="#020617" stop-opacity="0.95"/>
    </linearGradient>
  </defs>

  <!-- Background Frosted Glass Pill -->
  <rect x="3" y="3" width="{badge_width - 6}" height="{badge_height - 6}" rx="{rx}" ry="{rx}"
        fill="url(#bgGradient)" stroke="#38BDF8" stroke-opacity="0.35" stroke-width="1.8" filter="url(#badgeShadow)"/>

  <!-- WhatsApp Icon Circle -->
  <circle cx="38" cy="{badge_height // 2}" r="22" fill="url(#waGradient)"/>
  
  <!-- WhatsApp Phone Handset Icon (Vector Glyph) -->
  <g transform="translate(24, {badge_height // 2 - 14}) scale(0.60)">
    <path fill="#FFFFFF" d="M24 4C13 4 4 13 4 24C4 27.5 4.9 30.8 6.5 33.7L4 44L14.6 41.5C17.3 43 20.6 44 24 44C35 44 44 35 44 24C44 13 35 4 24 4ZM34.2 30.6C33.8 31.7 32.1 32.8 31.1 33C30.3 33.2 29.3 33.3 25.8 31.8C21.4 29.9 18.5 25.4 18.3 25.1C18.1 24.8 16.5 22.7 16.5 20.5C16.5 18.3 17.6 17.2 18 16.7C18.4 16.2 19 16 19.6 16C19.8 16 20 16 20.2 16C20.7 16 21 16.1 21.3 16.9C21.7 17.9 22.7 20.3 22.8 20.6C22.9 20.9 23 21.3 22.8 21.7C22.6 22.1 22.4 22.3 22.2 22.6C22 22.9 21.7 23.2 21.4 23.5C21.1 23.8 20.8 24.1 21.2 24.8C21.6 25.5 23 27.8 25.1 29.7C27.8 32.1 30 32.9 30.8 33.2C31.6 33.5 32 33.4 32.5 32.9C33 32.4 34.6 30.5 35.1 29.8C35.6 29.1 36.1 29.2 36.7 29.4C37.3 29.6 40.5 31.2 41.1 31.5C41.7 31.8 42.1 32 42.2 32.2C42.3 32.5 42.3 33.7 34.2 30.6Z"/>
  </g>

  <!-- Phone Number Text -->
  <text x="76" y="{phone_y}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-weight="bold" font-size="{phone_font_size}" fill="#FFFFFF" letter-spacing="0.6">{phone_escaped}</text>
  {loc_svg_element}
</svg>'''

        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        # Convert SVG to crystal-clear PNG using FFmpeg
        cmd = [
            "ffmpeg", "-y",
            "-i", str(svg_path),
            str(output_path)
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if output_path.exists() and output_path.stat().st_size > 0:
                return output_path
        except subprocess.CalledProcessError:
            pass

        return None

    def get_overlay_coordinates(self, badge_width: int = 440, badge_height: int = 80) -> Tuple[str, str]:
        """
        Returns FFmpeg overlay x and y expressions corresponding to the selected position.
        Ensures safe margins from screen borders and social media UI icons.
        """
        margin_x = 44
        margin_y = 68

        if self.position == "top-left":
            return (f"{margin_x}", f"{margin_y}")
        elif self.position == "top-center":
            return (f"(W-w)/2", f"{margin_y}")
        elif self.position == "bottom-left":
            # Above subtitle / description safe zone
            return (f"{margin_x}", f"H-h-240")
        elif self.position == "bottom-right":
            return (f"W-w-{margin_x}", f"H-h-240")
        else:
            # Default: top-right
            return (f"W-w-{margin_x}", f"{margin_y}")
