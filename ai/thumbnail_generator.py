"""
AI Video Thumbnail & Cover Generator for COSMIC DEBATE EXPRESS.
Automatically generates stunning, high-CTR cinematic thumbnail covers for existing or new video outputs using Pollinations FLUX AI.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from providers.pollinations import PollinationsProvider


class ThumbnailGenerator:
    """Generates high-retention cinematic video thumbnail covers."""

    def __init__(self, api_key: Optional[str] = None):
        self.provider = PollinationsProvider(api_key=api_key)

    def generate_thumbnail_for_script(self, script_path: Path, output_image_path: Optional[Path] = None) -> Optional[Path]:
        """
        Generates a 9:16 cinematic vertical thumbnail for a given script.json file.
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

        topic = data.get("topic", "Cosmic Debate")
        hook = data.get("headline_hook", topic)
        
        # Determine output image path
        if output_image_path is None:
            output_image_path = script_path.parent / "thumbnail.jpg"
        else:
            output_image_path = Path(output_image_path)

        print(f"\n🖼️ [Thumbnail AI] Generando portada cinematográfica para: '{topic}'...")
        print(f"   • Gancho visual: {hook}")

        # Construct a rich cinematic prompt for thumbnail generation
        prompt = (
            f"Cinematic vertical 9:16 YouTube Shorts thumbnail about {topic}. "
            f"Featuring glowing electric cyan quantum energy orb versus radiant amber solar energy orb in epic cosmic battle. "
            f"Deep space background, supernovas, particle matrix, hyper-detailed 8k resolution, dramatic lighting, viral clickbait aesthetic."
        )

        # 9:16 vertical resolution optimal for shorts/reels/tiktok covers
        success = self.provider.generate_image(
            prompt=prompt,
            out_path=output_image_path,
            width=768,
            height=1344,
            model="flux"
        )

        if success and output_image_path.exists():
            print(f"  ✨ ¡Portada generada con éxito en: {output_image_path}!")
            return output_image_path
        else:
            print(f"  ⚠️ No se pudo generar la portada con Pollinations.")
            return None

    def batch_generate_thumbnails(self, base_output_dir: Path = Path("output") / "orb_previews") -> int:
        """
        Scans all video folders in base_output_dir, finds script.json files missing a thumbnail, and generates them.
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
            if not thumb_f.exists():
                print(f"\n📁 Procesando proyecto: {script_f.parent.name}")
                res = self.generate_thumbnail_for_script(script_f, thumb_f)
                if res:
                    count += 1
            else:
                print(f"  ✓ {script_f.parent.name} ya tiene portada (thumbnail.jpg).")

        print(f"\n✨ [Thumbnail Batch] Proceso completado. Se generaron {count} nuevas portadas.")
        return count
