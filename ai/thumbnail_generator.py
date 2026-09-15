"""
AI Video Thumbnail & Cover Generator for COSMIC DEBATE EXPRESS.
Renders studio-grade 1080x1920 (9:16) cinematic posters with:
- Exact 3D bio-reactive Quantum (Cyan) & Solar (Amber) Orbs
- Deep space volumetric starfield & nebula clash
- Electric energy divide with center 'VS' shield
- High-CTR viral headline typography with frosted-glass card, Spanish UTF-8 accents & atmospheric glow
- Zero watermarks, zero blurred blobs, 100% deterministic studio quality
"""

import json
import math
import random
import re
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from video.orb import ORB_PALETTES


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
    # Fallback
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

    def format_title_text(self, hook: str, topic: str) -> Tuple[str, str]:
        """Cleans and extracts the punchiest headline title and scientific subtitle."""
        raw = hook or topic or "DEBATE CÓSMICO"
        # Remove markdown & emojis that break on system font rendering
        clean = re.sub(r"[⚡🔥💥✨🚀👁️⚛️☀️]", "", raw).strip()
        clean = clean.replace("¡", "").replace("!", "").strip().upper()
        if not clean or len(clean) < 5:
            clean = (topic or "DEBATE CÓSMICO").upper()

        sub = (topic or "FÍSICA CUÁNTICA VS ASTROFÍSICA SOLAR").upper()
        sub = re.sub(r"[⚡🔥💥✨🚀👁️⚛️☀️]", "", sub).strip()
        return clean, sub

    def render_studio_poster(self, hook: str, topic: str, output_path: Path) -> Path:
        """
        Renders an ultra-high quality 1080x1920 cinematic YouTube Shorts/TikTok cover.
        """
        W, H = 1080, 1920
        poster = Image.new("RGBA", (W, H), (8, 10, 20, 255))
        pdraw = ImageDraw.Draw(poster)

        # 1. Atmospheric cosmic space gradient
        for y in range(H):
            factor = y / H
            r = int(12 * (1 - factor * 0.45))
            g = int(16 * (1 - factor * 0.45))
            b = int(32 * (1 - factor * 0.45))
            pdraw.line([(0, y), (W, y)], fill=(r, g, b, 255))

        # 2. Rich celestial starfield
        random.seed(99)
        stars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(stars)
        for _ in range(480):
            sx = random.randint(0, W)
            sy = random.randint(0, H)
            sb = random.randint(160, 255)
            sr = random.choice([1, 1, 1, 2, 2, 3])
            sdraw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(sb, sb, 255, random.randint(110, 255)))
        poster = Image.alpha_composite(poster, stars)

        # 3. Volumetric nebula glows (Cyan on Quantum Left, Amber on Solar Right)
        nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ndraw = ImageDraw.Draw(nebula)
        # Quantum Cyan Nebula
        ndraw.ellipse([-160, 700, 680, 1400], fill=(0, 220, 255, 48))
        # Solar Amber Nebula
        ndraw.ellipse([W - 680, 700, W + 160, 1400], fill=(255, 140, 0, 48))
        # Upper Center Soft Cyan Glow
        ndraw.ellipse([W // 2 - 400, 90, W // 2 + 400, 520], fill=(0, 160, 255, 26))
        nebula = nebula.filter(ImageFilter.GaussianBlur(92))
        poster = Image.alpha_composite(poster, nebula)

        # 4. Render and place authentic Quantum and Solar Orbs
        orb_q = render_orb_asset("quantum", size=470)
        orb_s = render_orb_asset("solar", size=470)

        q_pos = (int(W * 0.04), 820)
        s_pos = (int(W * 0.52), 820)
        poster.paste(orb_q, q_pos, orb_q)
        poster.paste(orb_s, s_pos, orb_s)

        # 5. Electric energy divide & Center VS Emblem
        vs_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        vdraw = ImageDraw.Draw(vs_layer)
        vs_cx = W // 2
        vs_cy = 1055

        # Vertical energy divide lines
        vdraw.line([(vs_cx, 750), (vs_cx, 1360)], fill=(255, 255, 255, 75), width=3)
        vdraw.line([(vs_cx - 1, 840), (vs_cx - 1, 1270)], fill=(0, 240, 255, 130), width=2)
        vdraw.line([(vs_cx + 1, 840), (vs_cx + 1, 1270)], fill=(255, 180, 0, 130), width=2)

        # Center VS Metallic Shield
        vdraw.ellipse([vs_cx - 56, vs_cy - 56, vs_cx + 56, vs_cy + 56], fill=(12, 16, 32, 245), outline=(255, 215, 0, 255), width=4)
        vs_font = get_font(46)
        vbbox = vdraw.textbbox((0, 0), "VS", font=vs_font)
        vw = vbbox[2] - vbbox[0]
        vh = vbbox[3] - vbbox[1]
        vdraw.text((vs_cx - vw // 2, vs_cy - vh // 2 - 4), "VS", font=vs_font, fill=(255, 240, 100))
        poster = Image.alpha_composite(poster, vs_layer)

        # 6. Entity Badges below orbs
        badge_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(badge_layer)
        badge_font = get_font(28)

        # Quantum Badge
        bdraw.rounded_rectangle([130, 1310, 390, 1375], radius=18, fill=(10, 25, 45, 235), outline=(0, 240, 255, 255), width=3)
        bdraw.text((155, 1326), "⚛  CUÁNTICO", font=badge_font, fill=(0, 240, 255))

        # Solar Badge
        bdraw.rounded_rectangle([W - 390, 1310, W - 130, 1375], radius=18, fill=(35, 20, 10, 235), outline=(255, 180, 0, 255), width=3)
        bdraw.text((W - 365, 1326), "☀  SOLAR", font=badge_font, fill=(255, 200, 50))
        poster = Image.alpha_composite(poster, badge_layer)

        # 7. Hero Headline Glass Card (Top 30% of screen)
        title_card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        tdraw = ImageDraw.Draw(title_card)

        # Top Eyebrow Tag
        eyebrow_font = get_font(24)
        eb_text = "⚡  DEBATE CÓSMICO EXPRESS  ⚡"
        ebbox = tdraw.textbbox((0, 0), eb_text, font=eyebrow_font)
        ebw = ebbox[2] - ebbox[0]
        eb_x = (W - ebw) // 2
        tdraw.rounded_rectangle([eb_x - 24, 100, eb_x + ebw + 24, 150], radius=16, fill=(10, 18, 38, 220), outline=(0, 240, 255, 210), width=2)
        tdraw.text((eb_x, 113), eb_text, font=eyebrow_font, fill=(0, 240, 255))

        # Main Title Card Glass Box
        card_x1, card_y1, card_x2, card_y2 = 45, 175, W - 45, 590
        tdraw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=28, fill=(10, 15, 30, 230), outline=(0, 240, 255, 180), width=3)
        # Accent gradient top line
        tdraw.line([(card_x1 + 30, card_y1), (card_x2 - 30, card_y1)], fill=(255, 215, 0, 255), width=4)

        # Word-wrapped Title Text
        clean_headline, clean_sub = self.format_title_text(hook, topic)
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

        # Limit to 3 lines
        lines = lines[:3]
        line_y = card_y1 + 45
        for line in lines:
            tb = tdraw.textbbox((0, 0), line, font=title_font)
            tw = tb[2] - tb[0]
            tx = (W - tw) // 2
            # Drop shadow
            tdraw.text((tx + 4, line_y + 4), line, font=title_font, fill=(0, 0, 0, 240))
            tdraw.text((tx + 2, line_y + 2), line, font=title_font, fill=(0, 0, 0, 240))
            # Atmospheric glow
            tdraw.text((tx - 1, line_y), line, font=title_font, fill=(0, 160, 255, 160))
            tdraw.text((tx + 1, line_y), line, font=title_font, fill=(0, 160, 255, 160))
            # Main white text
            tdraw.text((tx, line_y), line, font=title_font, fill=(255, 255, 255, 255))
            line_y += 76

        # Subtitle inside the card
        sub_font = get_font(30)
        stb = tdraw.textbbox((0, 0), clean_sub, font=sub_font)
        stw = stb[2] - stb[0]
        stx = (W - stw) // 2
        tdraw.text((stx + 2, line_y + 16), clean_sub, font=sub_font, fill=(0, 0, 0, 220))
        tdraw.text((stx, line_y + 14), clean_sub, font=sub_font, fill=(255, 215, 0, 255))

        # 8. Bottom Call To Action Badge (Above UI overlay safety zone)
        cta_font = get_font(32)
        cta_text = "⚔  ¿QUIÉN TIENE LA RAZÓN?  ⚔"
        ctb = tdraw.textbbox((0, 0), cta_text, font=cta_font)
        ctw = ctb[2] - ctb[0]
        cx = (W - ctw) // 2
        tdraw.rounded_rectangle([cx - 32, 1460, cx + ctw + 32, 1530], radius=24, fill=(15, 22, 42, 235), outline=(255, 215, 0, 240), width=3)
        tdraw.text((cx, 1478), cta_text, font=cta_font, fill=(255, 230, 80))

        poster = Image.alpha_composite(poster, title_card)

        # 9. Save final thumbnail image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_rgb = poster.convert("RGB")
        final_rgb.save(output_path, "JPEG", quality=96)
        print(f"  ✨ ¡Portada cinematográfica generada con éxito en: {output_path}!")
        return output_path

    def generate_thumbnail_for_script(self, script_path: Path, output_image_path: Optional[Path] = None) -> Optional[Path]:
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
        return self.render_studio_poster(hook, topic, output_image_path)

    def batch_generate_thumbnails(self, base_output_dir: Path = Path("output") / "orb_previews") -> int:
        """Scans all video folders in base_output_dir and regenerates/generates studio thumbnails."""
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
            res = self.generate_thumbnail_for_script(script_f, thumb_f)
            if res:
                count += 1

        print(f"\n✨ [Thumbnail Batch] Proceso completado. Se generaron {count} portadas profesionales.")
        return count
