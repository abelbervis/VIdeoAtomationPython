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
        position: str = "top-center",
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

        self.position = position.lower() if position else "top-center"
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
        Optimized for mobile screen safe zones (TikTok, Reels, Shorts).
        """
        if not self.is_enabled:
            return None

        output_path.parent.mkdir(parents=True, exist_ok=True)
        svg_path = output_path.with_suffix(".svg")

        # Format display phone
        display_phone = self.phone or ""
        if display_phone and not display_phone.startswith("+") and len(display_phone) >= 10:
            display_phone = f"{display_phone}"

        # Dynamic dimension calculations
        has_location = bool(self.location)
        max_chars = max(len(display_phone), len(self.location or "") + 3)
        
        # Dynamic pill width based on text length with comfortable breathing padding
        char_width = 16 if not has_location else 14
        badge_width = max(420, min(620, 110 + int(max_chars * char_width)))
        badge_height = 92 if has_location else 78
        rx = badge_height // 2

        # Location text snippet
        loc_escaped = (self.location or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        phone_escaped = display_phone.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        loc_svg_element = ""
        if has_location:
            loc_svg_element = f'''
  <!-- Location Pin & Text -->
  <text x="84" y="68" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="18" font-weight="700" fill="#38BDF8" letter-spacing="0.4">📍 {loc_escaped}</text>
'''

        phone_y = 39 if has_location else (badge_height // 2 + 9)
        phone_font_size = 27 if has_location else 29

        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{badge_width}" height="{badge_height}" viewBox="0 0 {badge_width} {badge_height}">
  <defs>
    <!-- Deep contrast drop shadow for mobile readability -->
    <filter id="badgeShadow" x="-15%" y="-20%" width="135%" height="145%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.85"/>
    </filter>
    <!-- WhatsApp Gradient -->
    <linearGradient id="waGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#25D366"/>
      <stop offset="100%" stop-color="#128C7E"/>
    </linearGradient>
    <!-- Background Pill Gradient -->
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0B0F19" stop-opacity="0.94"/>
      <stop offset="100%" stop-color="#020617" stop-opacity="0.96"/>
    </linearGradient>
  </defs>

  <!-- Background Frosted Glass Pill with emerald border highlight -->
  <rect x="3" y="3" width="{badge_width - 6}" height="{badge_height - 6}" rx="{rx}" ry="{rx}"
        fill="url(#bgGradient)" stroke="#22C55E" stroke-opacity="0.65" stroke-width="2.2" filter="url(#badgeShadow)"/>

  <!-- WhatsApp Icon Circle -->
  <circle cx="42" cy="{badge_height // 2}" r="25" fill="url(#waGradient)"/>
  
  <!-- WhatsApp Phone Handset Icon (Crisp Vector Glyph) -->
  <g transform="translate(26, {badge_height // 2 - 16}) scale(0.68)">
    <path fill="#FFFFFF" d="M24 4C13 4 4 13 4 24C4 27.5 4.9 30.8 6.5 33.7L4 44L14.6 41.5C17.3 43 20.6 44 24 44C35 44 44 35 44 24C44 13 35 4 24 4ZM34.2 30.6C33.8 31.7 32.1 32.8 31.1 33C30.3 33.2 29.3 33.3 25.8 31.8C21.4 29.9 18.5 25.4 18.3 25.1C18.1 24.8 16.5 22.7 16.5 20.5C16.5 18.3 17.6 17.2 18 16.7C18.4 16.2 19 16 19.6 16C19.8 16 20 16 20.2 16C20.7 16 21 16.1 21.3 16.9C21.7 17.9 22.7 20.3 22.8 20.6C22.9 20.9 23 21.3 22.8 21.7C22.6 22.1 22.4 22.3 22.2 22.6C22 22.9 21.7 23.2 21.4 23.5C21.1 23.8 20.8 24.1 21.2 24.8C21.6 25.5 23 27.8 25.1 29.7C27.8 32.1 30 32.9 30.8 33.2C31.6 33.5 32 33.4 32.5 32.9C33 32.4 34.6 30.5 35.1 29.8C35.6 29.1 36.1 29.2 36.7 29.4C37.3 29.6 40.5 31.2 41.1 31.5C41.7 31.8 42.1 32 42.2 32.2C42.3 32.5 42.3 33.7 34.2 30.6Z"/>
  </g>

  <!-- Phone Number Text (High-contrast bold white) -->
  <text x="84" y="{phone_y}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-weight="800" font-size="{phone_font_size}" fill="#FFFFFF" letter-spacing="0.8">{phone_escaped}</text>
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
        Strictly adjusted for TikTok, YouTube Shorts, and Instagram Reels UI Safe Zones:
        - Top Safe Line (below TikTok tabs/search): y = 175px
        - Bottom Safe Line (above caption/subtitles): y = 1380px
        - Horizontal Center: x = (W-w)/2
        """
        top_safe_y = 175
        bottom_safe_y = 1380
        side_margin = 56

        if self.position in ("top-center", "center-top", "default"):
            # Recommended default for TikTok/Shorts: Centered horizontally, below top tabs
            return (f"(W-w)/2", f"{top_safe_y}")
        elif self.position == "top-left":
            return (f"{side_margin}", f"{top_safe_y}")
        elif self.position == "top-right":
            return (f"W-w-{side_margin}", f"{top_safe_y}")
        elif self.position in ("bottom-center", "center-bottom"):
            return (f"(W-w)/2", f"{bottom_safe_y}")
        elif self.position == "bottom-left":
            return (f"{side_margin}", f"{bottom_safe_y}")
        elif self.position == "bottom-right":
            return (f"W-w-{side_margin}", f"{bottom_safe_y}")
        else:
            # Fallback to top-center (optimal safe zone)
            return (f"(W-w)/2", f"{top_safe_y}")
