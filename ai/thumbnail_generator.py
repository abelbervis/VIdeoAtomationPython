"""
AI Video Thumbnail & Cover Generator for COSMIC DEBATE EXPRESS.
Generates stunning cinematic 9:16 vertical thumbnails featuring the Quantum (Cyan) and Solar (Amber) orbs,
adds professional bold title typography, and removes any third-party watermarks using Pillow (PIL).
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
from providers.pollinations import PollinationsProvider


class ThumbnailGenerator:
    """Generates high-retention cinematic video thumbnail covers with custom branding and typography."""

    def __init__(self, api_key: Optional[str] = None):
        self.provider = PollinationsProvider(api_key=api_key)

    def generate_thumbnail_for_script(self, script_path: Path, output_image_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generates a 9:16 cinematic vertical thumbnail for a given script.json file,
        compositing a professional title overlay and removing watermarks.
        """
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
        hook = data.get("headline_hook", "⚡ DEBATE CÓSMICO ⚡")
        
        if output_image_path is None:
            output_image_path = script_path.parent / "thumbnail.jpg"
        else:
            output_image_path = Path(output_image_path)

        print(f"\n🖼️ [Thumbnail AI] Generando portada personalizada para: '{topic}'...")
        print(f"   • Título destacado: {hook}")

        # Prompt tailored specifically to the user's Quantum (Cyan) and Solar (Amber) orbs
        prompt = (
            f"Cinematic vertical 9:16 high-end YouTube Shorts thumbnail. "
            f"Two magnificent glowing 3D energy orbs floating in deep space cosmos. "
            f"Left orb is glowing electric cyan blue quantum orb with particle matrix. "
            f"Right orb is radiant amber gold solar orb with thermonuclear flares. "
            f"Epic scientific battle, deep space background, volumetric lighting, 8k resolution, photorealistic."
        )

        temp_img_path = script_path.parent / "_temp_raw_thumb.jpg"
        success = self.provider.generate_image(
            prompt=prompt,
            out_path=temp_img_path,
            width=768,
            height=1344,
            model="flux"
        )

        if not success or not temp_img_path.exists():
            print(f"  ⚠️ No se pudo descargar la imagen base de Pollinations.")
            return None

        try:
            # Open image with Pillow
            img = Image.open(temp_img_path).convert("RGB")
            w, h = img.size

            # Crop bottom 50 pixels to eliminate any watermark
            img = img.crop((0, 0, w, h - 50))
            w, h = img.size

            # Create drawing context for professional overlay & typography
            draw = ImageDraw.Draw(img)

            # Try loading a bold system truetype font
            font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
            title_font = None
            sub_font = None
            if Path(font_path).exists():
                try:
                    title_font = ImageFont.truetype(font_path, 52)
                    sub_font = ImageFont.truetype(font_path, 30)
                except Exception:
                    pass

            if not title_font:
                title_font = ImageFont.load_default()
                sub_font = ImageFont.load_default()

            # Draw top dark gradient / banner background for maximum contrast
            banner_height = 360
            overlay = Image.new("RGBA", (w, banner_height), (8, 14, 28, 220))
            img.paste(Image.alpha_composite(Image.new("RGBA", (w, banner_height), (0,0,0,0)), overlay), (0, 80), overlay)

            # Draw accent glowing line top
            draw.rectangle([40, 75, w - 40, 83], fill=(0, 240, 255))

            # Format and wrap title text nicely
            clean_hook = hook.replace("⚡", "").strip().upper()
            if not clean_hook:
                clean_hook = topic.upper()

            # Word wrap title into max 3 lines
            words = clean_hook.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                test_line = " ".join(current_line)
                bbox = draw.textbbox((0, 0), test_line, font=title_font)
                if bbox[2] > w - 100:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))

            # Draw title text with drop shadow / outline effect
            y_text = 120
            for line in lines[:3]:
                bbox = draw.textbbox((0, 0), line, font=title_font)
                tw = bbox[2] - bbox[0]
                tx = (w - tw) // 2

                # Drop shadow
                draw.text((tx + 3, y_text + 3), line, font=title_font, fill=(0, 0, 0))
                # Main text
                draw.text((tx, y_text), line, font=title_font, fill=(255, 255, 255))
                y_text += 62

            # Draw team badges at the bottom or middle
            badge_text = "TEAM CUÁNTICO  VS  TEAM SOLAR"
            bbox = draw.textbbox((0, 0), badge_text, font=sub_font)
            bw = bbox[2] - bbox[0]
            bx = (w - bw) // 2
            by = h - 160

            # Badge pill background
            draw.rounded_rectangle([bx - 24, by - 12, bx + bw + 24, by + 38], radius=20, fill=(15, 23, 42, 240), outline=(255, 200, 0), width=3)
            draw.text((bx, by), badge_text, font=sub_font, fill=(255, 220, 50))

            # Save final polished thumbnail
            img.save(output_image_path, "JPEG", quality=95)

            # Cleanup temp raw image
            if temp_img_path.exists():
                temp_img_path.unlink()

            print(f"  ✨ ¡Portada profesional generada con éxito en: {output_image_path}!")
            return output_image_path

        except Exception as e:
            print(f"  ⚠️ Error procesando la imagen con Pillow: {e}")
            if temp_img_path.exists():
                temp_img_path.unlink()
            return None

    def batch_generate_thumbnails(self, base_output_dir: Path = Path("output") / "orb_previews") -> int:
        """
        Scans all video folders in base_output_dir, finds script.json files, and generates custom thumbnails.
        """
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
