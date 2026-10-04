#!/usr/bin/env python3
"""
Ad & UGC Short-Form Video Generator - Dedicated CLI.
Creates high-converting vertical marketing videos (TikTok Ads, Reels, Shorts)
from user-provided photos and videos in a local folder.

Features:
- Scans user folder for images and video clips.
- Multimodal visual inspection & AI sales copywriting (AIDA framework).
- Interactive console review: view, edit or regenerate the prompt and script BEFORE rendering.
- Neural TTS voiceover with scene-level audio synchronization.
- Word-by-word dynamic karaoke subtitles with hook banner overlay.
- Motion camera effects (Ken Burns zoom/pan) on static product images.
- Background music mixing with dynamic auto-ducking.

Usage:
  python ad_generator.py --folder ./mis_fotos/ --prompt "Vende este reloj con batería de 7 días"
  python ad_generator.py --folder ./fotos_producto/ --product "Café Origen" --offer "20% OFF"
  python ad_generator.py --sample  (crea fotos de prueba y ejecuta una demo completa)
"""

import argparse
import json
import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from ai.ad_copywriter import AdCopywriter, AD_SYSTEM_PROMPT
from audio.beat_sync import BeatGrid
from audio.music import MusicManager
from audio.pixabay_music import PixabayMusicEngine, GENRE_PROFILES
from audio.tts import TTSManager
from config import (
    BASE_DIR,
    OUTPUT_DIR,
    TEMP_DIR,
    VIDEO_FPS,
    VIDEO_CRF,
    VIDEO_PRESET,
    TRANSITION_DURATION,
    MUSIC_VOLUME,
    resolve_video_format,
)
from subtitles.generator import SubtitleGenerator
from utils.files import check_ffmpeg, clean_temp_directory, get_media_duration
from video.render import VideoRenderer


SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
SUPPORTED_VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}
ALL_MEDIA_EXTS = SUPPORTED_IMAGE_EXTS | SUPPORTED_VIDEO_EXTS


def scan_media_folder(folder_path: Path) -> List[Path]:
    """Scans directory and returns valid image and video files sorted by name."""
    if not folder_path.exists() or not folder_path.is_dir():
        return []
    
    files = [
        f for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in ALL_MEDIA_EXTS and not f.name.startswith(".")
    ]
    # Sort files naturally
    files.sort(key=lambda x: x.name.lower())
    return files


def create_sample_media(target_dir: Path) -> List[Path]:
    """Generates 4 high-quality sample product images for immediate demonstration."""
    target_dir.mkdir(parents=True, exist_ok=True)
    created_files: List[Path] = []
    
    samples = [
        ("01_producto_frontal.jpg", "0x181c24", "0x00dcff", "PRO AUDIO X1 - CANCELACION DE RUIDO"),
        ("02_detalle_ergonomia.jpg", "0x201428", "0xff64b4", "CONFORT TOTAL - MEMORY FOAM"),
        ("03_bateria_infinita.jpg", "0x0f2419", "0x50ff8c", "40 HORAS BATERIA - CARGA RAPIDA"),
        ("04_oferta_lanzamiento.jpg", "0x28190a", "0xffbe28", "30% DESCUENTO - ENVIO GRATIS HOY"),
    ]

    has_pil = False
    try:
        from PIL import Image, ImageDraw
        has_pil = True
    except ImportError:
        pass

    if has_pil:
        try:
            pil_colors = [
                ("01_producto_frontal.jpg", (24, 28, 36), "PRO AUDIO X1", "Cancelación Activa de Ruido", (0, 220, 255)),
                ("02_detalle_ergonomia.jpg", (30, 20, 40), "CONFORT TOTAL", "Almohadillas Memory Foam", (255, 100, 180)),
                ("03_bateria_infinita.jpg", (15, 35, 25), "40 HORAS BATERÍA", "Carga Rápida USB-C", (80, 255, 140)),
                ("04_oferta_lanzamiento.jpg", (40, 25, 10), "30% DE DESCUENTO", "¡Envío Gratis Hoy!", (255, 190, 40)),
            ]
            for fname, bg_color, title, subtitle, accent_color in pil_colors:
                out_file = target_dir / fname
                if not out_file.exists():
                    img = Image.new("RGB", (1080, 1920), color=bg_color)
                    draw = ImageDraw.Draw(img)
                    cx, cy = 540, 850
                    draw.ellipse([(cx-260, cy-260), (cx+260, cy+260)], outline=accent_color, width=12)
                    draw.rectangle([(140, 260), (940, 380)], fill=(10, 10, 15), outline=accent_color, width=4)
                    draw.text((540, 320), title, fill=(255, 255, 255), anchor="mm")
                    draw.rectangle([(100, 1360), (980, 1540)], fill=(15, 15, 22), outline=(255, 255, 255), width=3)
                    draw.text((540, 1450), subtitle, fill=accent_color, anchor="mm")
                    img.save(out_file, quality=92)
                created_files.append(out_file)
            return created_files
        except Exception:
            created_files = []

    # Pure FFmpeg fallback (zero external Python dependencies required)
    import subprocess
    for fname, bg_hex, accent_hex, label in samples:
        out_file = target_dir / fname
        if not out_file.exists():
            vf_filter = (
                f"drawbox=x=120:y=240:w=840:h=180:color=0x111118:t=fill,"
                f"drawbox=x=120:y=240:w=840:h=180:color={accent_hex}:t=6,"
                f"drawbox=x=240:y=560:w=600:h=600:color={accent_hex}:t=8,"
                f"drawbox=x=300:y=620:w=480:h=480:color=0x222230:t=fill,"
                f"drawbox=x=100:y=1380:w=880:h=200:color=0x0a0a12:t=fill,"
                f"drawbox=x=100:y=1380:w=880:h=200:color={accent_hex}:t=4"
            )
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"color=c={bg_hex}:s=1080x1920:d=1",
                "-vf", vf_filter,
                "-vframes", "1",
                "-q:v", "3",
                str(out_file)
            ]
            try:
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except Exception as e:
                print(f"  ⚠️ Error al generar imagen con FFmpeg: {e}")
        if out_file.exists():
            created_files.append(out_file)

    return created_files


def resolve_cache_file_path(media_folder: Path, custom_cache: Optional[str] = None) -> Path:
    """Determines the target cache file path for persisting vision & copywriting results."""
    if custom_cache:
        return Path(custom_cache).expanduser().resolve()
    
    target = media_folder / "ad_script_cache.json"
    try:
        # Test if media_folder is writable
        target.touch(exist_ok=True)
        return target
    except Exception:
        # Fallback to TEMP_DIR if folder is mounted read-only
        safe_name = "".join(c if c.isalnum() else "_" for c in media_folder.name)
        return TEMP_DIR / f"ad_cache_{safe_name}.json"


def load_cached_script(cache_file: Path) -> Optional[Tuple[Dict[str, Any], str]]:
    """Loads previously generated ad script and prompt from JSON cache."""
    if not cache_file.exists() or cache_file.stat().st_size == 0:
        return None
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        script = data.get("script")
        prompt = data.get("user_prompt", "")
        if script and isinstance(script, dict) and script.get("scenes"):
            return script, prompt
    except Exception as e:
        print(f"  ⚠️ Error al leer archivo de caché ({e}). Se regenerará.")
    return None


def save_cached_script(
    cache_file: Path,
    script: Dict[str, Any],
    user_prompt: str,
    media_files: List[Path]
) -> None:
    """Saves the vision copywriting results to disk for zero-cost instant reruns."""
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "cached_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "user_prompt": user_prompt,
            "media_files": [f.name for f in media_files],
            "script": script
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"  💾 Guion y visión guardados en caché: {cache_file.name}")
        print(f"     (Las próximas ejecuciones serán instantáneas y no consumirán API de visión)")
    except Exception as e:
        print(f"  ⚠️ No se pudo guardar la caché ({e})")


def display_prompt_and_script_review(
    user_prompt: str,
    script: Dict[str, Any],
    media_files: List[Path],
    product_name: Optional[str] = None,
    offer: Optional[str] = None,
    cta: Optional[str] = None,
) -> None:
    """Formats and prints the advertising prompt and generated scenes for user inspection."""
    terminal_width = min(shutil.get_terminal_size((80, 20)).columns, 82)
    sep_double = "═" * terminal_width
    sep_single = "─" * terminal_width

    scenes = script.get("scenes", [])
    hook_title = script.get("hook_title") or script.get("title", "")
    prod = script.get("product_name") or product_name or "Producto"

    print("\n" + sep_double)
    print("📢  REVISIÓN DEL GUION PUBLICITARIO (ANTES DE RENDERIZAR)")
    print(sep_double)
    print(f"🎯 Prompt del Usuario: \"{user_prompt}\"")
    if offer:
        print(f"🎁 Oferta destacada:  {offer}")
    if cta:
        print(f"🚀 Llamado a la acción: {cta}")
    print(f"🏷️  Producto:         {prod}")
    print(f"💥 Hook en Pantalla:  {hook_title}")
    print(f"🎞️  Total Escenas:     {len(scenes)} escenas ({len(media_files)} archivos multimedia)")
    print(sep_single)
    # Music & Rhythm summary
    genre_key = script.get("music_genre", "commercial_trap")
    genre_info = GENRE_PROFILES.get(genre_key, GENRE_PROFILES["commercial_trap"])
    bpm = float(script.get("target_bpm", genre_info["bpm"]))
    vibe = script.get("music_vibe_reason") or genre_info["desc"]
    bar_sec = (60.0 / bpm) * 4.0
    beat_sec = 60.0 / bpm

    print("🎵 MÚSICA & RITMO (PIXABAY / BEAT-SYNC):")
    print(f"   Pista/Estilo:   {genre_info['name']} ({bpm:.0f} BPM)")
    print(f"   Sincronización: Cortes visuales alineados a golpes de compás (cada {bar_sec:.2f}s | beat: {beat_sec:.2f}s)")
    print(f"   Justificación:  \"{vibe}\"")
    print(sep_single)
    print("📋 CONTENIDO DE CADA ESCENA:")

    for idx, scene in enumerate(scenes):
        media_name = media_files[idx % len(media_files)].name if media_files else "Sin archivo"
        narration = scene.get("narration", "").strip()
        callout = scene.get("callout_text", "")
        focus = scene.get("visual_focus", "")

        callout_str = f" | Badge: [{callout}]" if callout else ""
        print(f"\n  [Escena {idx + 1:02d}] 📁 Recurso: {media_name}{callout_str}")
        if focus:
            print(f"    🔍 Enfoque visual: {focus}")
        print(f"    🗣️  Locución: \"{narration}\"")

    print("\n" + sep_double)


def interactive_prompt_review_menu(
    copywriter: AdCopywriter,
    media_files: List[Path],
    user_prompt: str,
    script: Dict[str, Any],
    product_name: Optional[str] = None,
    offer: Optional[str] = None,
    cta: Optional[str] = None,
    target_duration: int = 25,
    language: str = "es",
    cache_file: Optional[Path] = None,
) -> Tuple[bool, Dict[str, Any], str]:
    """
    Interactive CLI loop allowing user to review, edit, or regenerate the prompt and script.
    Returns:
        (proceed_to_render: bool, final_script: dict, active_user_prompt: str)
    """
    current_prompt = user_prompt
    current_script = script

    while True:
        display_prompt_and_script_review(
            user_prompt=current_prompt,
            script=current_script,
            media_files=media_files,
            product_name=product_name,
            offer=offer,
            cta=cta,
        )

        print("\n¿Qué deseas hacer antes del renderizado?")
        print("  [1] ✅ APROBAR Y COMENZAR RENDERIZADO (Presiona Enter)")
        print("  [2] ✏️  MODIFICAR EL PROMPT Y REGENERAR EL GUION CON IA")
        print("  [3] 🎵 CAMBIAR ESTILO MUSICAL O RITMO (BPM)")
        print("  [4] 📝 EDITAR LAS FRASES DEL GUION MANUALMENTE")
        print("  [5] 👁️  VER EL SYSTEM PROMPT COMPLETO DE MARKETING")
        print("  [6] ❌ CANCELAR Y SALIR")
        
        try:
            choice = input("\n👉 Elige una opción [1-6] (por defecto: 1): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada por el usuario.")
            return False, current_script, current_prompt

        if not choice or choice == "1":
            print("\n✅ Guion y música aprobados. Iniciando síntesis de voz y renderizado de video...")
            if cache_file:
                save_cached_script(cache_file, current_script, current_prompt, media_files)
            return True, current_script, current_prompt

        elif choice == "2":
            print("\n" + "─" * 65)
            print(f"Prompt actual: \"{current_prompt}\"")
            print("─" * 65)
            new_prompt = input("Ingresa las nuevas instrucciones o ajustes para el prompt:\n> ").strip()
            if new_prompt:
                current_prompt = new_prompt
                print("\n🔄 Regenerando guion con el nuevo prompt...")
                new_script, _ = copywriter.generate_ad_script(
                    media_files=media_files,
                    user_prompt=current_prompt,
                    product_name=product_name,
                    offer=offer,
                    cta=cta,
                    target_duration=target_duration,
                    language=language,
                )
                if new_script:
                    current_script = new_script
                    print("✅ Nuevo guion generado exitosamente.")
                    if cache_file:
                        save_cached_script(cache_file, current_script, current_prompt, media_files)
                else:
                    print("⚠️ No se pudo regenerar; manteniendo el guion anterior.")
            else:
                print("No se ingresó ningún cambio.")

        elif choice == "3":
            print("\n" + "─" * 65)
            print("🎵 SELECCIÓN DE ESTILO MUSICAL (PIXABAY / BEAT-SYNC)")
            print("─" * 65)
            genre_list = list(GENRE_PROFILES.keys())
            for idx, g_key in enumerate(genre_list, start=1):
                g_info = GENRE_PROFILES[g_key]
                print(f"  [{idx}] {g_info['name']} ({g_info['bpm']:.0f} BPM)")
                print(f"      👉 {g_info['desc']}")
            print(f"  [6] 🎛️  Ingresar BPM personalizado manualmente")

            g_choice = input(f"\nElige un estilo [1-{len(genre_list)+1}] (Enter para mantener actual): ").strip()
            if g_choice.isdigit():
                val = int(g_choice)
                if 1 <= val <= len(genre_list):
                    selected_key = genre_list[val - 1]
                    current_script["music_genre"] = selected_key
                    current_script["target_bpm"] = GENRE_PROFILES[selected_key]["bpm"]
                    current_script["music_vibe_reason"] = GENRE_PROFILES[selected_key]["desc"]
                    print(f"✅ Estilo musical cambiado a: {GENRE_PROFILES[selected_key]['name']}")
                    if cache_file:
                        save_cached_script(cache_file, current_script, current_prompt, media_files)
                elif val == len(genre_list) + 1:
                    custom_bpm_str = input("Ingresa el valor de BPM deseado (ej: 128): ").strip()
                    try:
                        c_bpm = float(custom_bpm_str)
                        current_script["target_bpm"] = c_bpm
                        current_script["music_vibe_reason"] = f"Tempo manual fijado a {c_bpm:.0f} BPM."
                        print(f"✅ BPM actualizado a: {c_bpm:.0f}")
                        if cache_file:
                            save_cached_script(cache_file, current_script, current_prompt, media_files)
                    except ValueError:
                        print("Valor de BPM inválido.")

        elif choice == "4":
            scenes = current_script.get("scenes", [])
            print(f"\nEditar escenas (1 a {len(scenes)}) o 'H' para editar el Hook Title:")
            target_scene = input("Número de escena a modificar [1-N o H] (Enter para volver): ").strip()
            
            if target_scene.lower() == "h":
                cur_hook = current_script.get("hook_title", "")
                print(f"Hook Title actual: \"{cur_hook}\"")
                new_hook = input("Nuevo Hook Title:\n> ").strip()
                if new_hook:
                    current_script["hook_title"] = new_hook.upper()
                    print("✅ Hook Title actualizado.")
                    if cache_file:
                        save_cached_script(cache_file, current_script, current_prompt, media_files)
            elif target_scene.isdigit():
                s_num = int(target_scene)
                if 1 <= s_num <= len(scenes):
                    cur_text = scenes[s_num - 1].get("narration", "")
                    print(f"\nEscena {s_num} actual:")
                    print(f"\"{cur_text}\"")
                    new_text = input("Escribe el nuevo texto para esta escena:\n> ").strip()
                    if new_text:
                        scenes[s_num - 1]["narration"] = new_text
                        print(f"✅ Escena {s_num} actualizada.")
                        if cache_file:
                            save_cached_script(cache_file, current_script, current_prompt, media_files)
                else:
                    print("Número de escena fuera de rango.")

        elif choice == "5":
            print("\n" + "═" * 65)
            print("📜 SYSTEM PROMPT DE COPYWRITING PUBLICITARIO")
            print("═" * 65)
            print(AD_SYSTEM_PROMPT)
            print("═" * 65)
            input("\nPresiona Enter para volver al menú...")

        elif choice == "6":
            print("\n❌ Renderizado cancelado. No se realizaron cambios.")
            return False, current_script, current_prompt

        else:
            print("Opción no válida. Por favor selecciona del 1 al 6.")


def parse_arguments() -> argparse.Namespace:
    """Configures command line arguments for the ad generator."""
    parser = argparse.ArgumentParser(
        description="Generador de Videos Publicitarios (Ads/UGC) con Fotos y Videos del Usuario.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # 1. Ejecutar con una carpeta de fotos de tu producto:
  python3 ad_generator.py --folder ./mis_fotos/ --prompt "Vende este termo inteligente que mantiene el agua fria por 24h"

  # 2. Agregar oferta especial y llamada a la accion:
  python3 ad_generator.py --folder ./fotos_zapatillas/ --product "Sneakers AirUrban" --offer "30%% OFF por 48 horas" --cta "Pide las tuyas en el link de la bio"

  # 3. Probar inmediatamente con imagenes de muestra generadas automaticamente:
  python3 ad_generator.py --sample
        """
    )

    parser.add_argument(
        "--folder", "-f",
        type=str,
        default="./input_media",
        help="Ruta de la carpeta que contiene las fotos o videos del producto (default: ./input_media)"
    )
    parser.add_argument(
        "--prompt", "-p",
        type=str,
        default="Vende este producto destacando su maxima calidad, innovacion y por que el cliente debe tenerlo hoy.",
        help="Instruccion publicitaria, angulo de ventas o descripcion de lo que se desea transmitir."
    )
    parser.add_argument(
        "--product",
        type=str,
        default=None,
        help="Nombre especifico del producto o marca."
    )
    parser.add_argument(
        "--offer",
        type=str,
        default=None,
        help="Oferta, descuento o beneficio especial (ej: '50%% de descuento', 'Envio gratis hoy')."
    )
    parser.add_argument(
        "--cta",
        type=str,
        default=None,
        help="Llamado a la acción (ej: 'Haz clic en el enlace', 'Compra ahora')."
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=25,
        help="Duración objetivo del anuncio en segundos (default: 25s, rango recomendado 20-35s)."
    )
    parser.add_argument(
        "--voice",
        type=str,
        default=None,
        help="Voz de locución Neural (ej: 'es-MX-JorgeNeural', 'es-ES-AlvaroNeural', 'en-US-ChristopherNeural')."
    )
    parser.add_argument(
        "--language", "-l",
        type=str,
        default="es",
        choices=["es", "en", "zh"],
        help="Idioma de la locución y subtítulos (default: es)."
    )
    parser.add_argument(
        "--music",
        type=str,
        default=None,
        help="Ruta a un archivo de música de fondo personalizado (o 'none' para silenciar)."
    )
    parser.add_argument(
        "--music-genre",
        type=str,
        default="auto",
        choices=["auto", "commercial_trap", "tech_electronic", "upbeat_pop", "chill_lofi", "energetic_stomp"],
        help="Estilo musical libre de derechos de Pixabay (default: auto, seleccionado por IA según el producto)."
    )
    parser.add_argument(
        "--bpm",
        type=float,
        default=None,
        help="Velocidad en Beats Por Minuto (BPM) para sincronizar los cortes de video al ritmo (default: automático según género)."
    )
    parser.add_argument(
        "--no-beat-sync",
        action="store_true",
        help="Desactivar la alineación rítmica Beat-Sync (los cortes se harán sólo según la voz)."
    )
    parser.add_argument(
        "--force-vision", "--force",
        action="store_true",
        help="Forzar un nuevo análisis de visión por API ignorando el archivo de caché existente."
    )
    parser.add_argument(
        "--cache-file",
        type=str,
        default=None,
        help="Ruta personalizada para guardar o leer el guion en caché (default: <carpeta>/ad_script_cache.json)."
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Nombre o carpeta donde guardar el video final renderizado."
    )
    parser.add_argument(
        "--transition",
        type=str,
        default="fade",
        choices=["fade", "dissolve", "wipeleft", "slideleft", "random", "none"],
        help="Efecto de transición visual entre tomas (default: fade)."
    )
    parser.add_argument(
        "--non-interactive", "--yes", "-y",
        action="store_true",
        help="Omitir la pausa de revisión interactiva en consola y renderizar directamente."
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Crea fotos de muestra en './sample_product_media' y corre una prueba publicitaria completa."
    )
    parser.add_argument(
        "--gemini-key",
        type=str,
        default=None,
        help="Clave API de Google Gemini (opcional si ya está en .env)."
    )
    parser.add_argument(
        "--groq-key",
        type=str,
        default=None,
        help="Clave API de Groq (opcional si ya está en .env)."
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    start_time = time.time()

    print("=" * 65)
    print("🎬  GENERADOR DE VIDEOS PUBLICITARIOS Y UGC (MODO CLI)")
    print("=" * 65)

    # 1. Check prerequisites
    if not check_ffmpeg():
        print("\n❌ Error: FFmpeg es obligatorio pero no se encontró en el PATH del sistema.")
        print("Instala FFmpeg para poder generar videos: https://ffmpeg.org/download.html")
        sys.exit(1)

    # 2. Determine target media folder
    if args.sample:
        media_folder = BASE_DIR / "sample_product_media"
        print(f"\n🧪 Modo muestra activado: Creando fotos de producto en '{media_folder}'...")
        media_files = create_sample_media(media_folder)
        if not args.product:
            args.product = "Auriculares Pro Audio X1"
        if not args.offer:
            args.offer = "30% de descuento + Envío Gratis en las próximas 24 horas"
        if not args.cta:
            args.cta = "Toca el botón aquí abajo y consigue los tuyos antes de que se agoten"
    else:
        media_folder = Path(args.folder).expanduser().resolve()
        media_files = scan_media_folder(media_folder)

    # If folder is missing or empty, provide helpful guidance
    if not media_files:
        print(f"\n❌ No se encontraron fotos ni videos válidos en la carpeta:")
        print(f"   📁 {media_folder}")
        print("\n💡 Formatos compatibles: .jpg, .jpeg, .png, .webp, .mp4, .mov, .webm")
        print("\n👉 Para probar inmediatamente con imágenes de muestra automáticas ejecuta:")
        print("   python ad_generator.py --sample")
        print("\n👉 O coloca tus fotos en una carpeta y corre:")
        print(f"   python ad_generator.py --folder {args.folder} --prompt \"Tu mensaje de venta\"")
        sys.exit(1)

    print(f"\n📁 Carpeta de origen: {media_folder.name} ({len(media_files)} archivos multimedia detectados):")
    for idx, f in enumerate(media_files[:6]):
        tipo = "VIDEO" if f.suffix.lower() in SUPPORTED_VIDEO_EXTS else "FOTO"
        print(f"   {idx+1}. [{tipo}] {f.name}")
    if len(media_files) > 6:
        print(f"   ... y {len(media_files) - 6} archivos más.")

    # 3. Initialize AI Copywriter
    copywriter = AdCopywriter(
        gemini_key=args.gemini_key,
        groq_key=args.groq_key,
    )

    # 4. Check Script Cache or Generate with AI Vision
    cache_file = resolve_cache_file_path(media_folder, args.cache_file)
    cached_data = None if args.force_vision else load_cached_script(cache_file)

    if cached_data:
        script, active_prompt = cached_data
        print(f"\n⚡ CACHÉ ACTIVADO: Se cargó el guion y análisis previo desde '{cache_file.name}'")
        print(f"   (0 llamadas a la API de Visión. Para forzar un nuevo análisis usa '--force-vision')")
        # If user provided a specific product/offer/cta flag on this run, update it
        if args.product:
            script["product_name"] = args.product
        if args.prompt and args.prompt != "Vende este producto de forma irresistible":
            active_prompt = args.prompt
    else:
        if args.force_vision and cache_file.exists():
            print(f"\n🔄 Flag '--force-vision' detectado: Reanalizando imágenes con la API e ignorando caché...")
        else:
            print(f"\n🧠 Analizando medios y redactando guion publicitario de alta retención...")

        script, active_prompt = copywriter.generate_ad_script(
            media_files=media_files,
            user_prompt=args.prompt,
            product_name=args.product,
            offer=args.offer,
            cta=args.cta,
            target_duration=args.duration,
            language=args.language,
            include_vision=True,
        )

        if not script or not script.get("scenes"):
            print("\n❌ Error: No fue posible generar el guion publicitario.")
            sys.exit(1)

        # Save to cache file for instant future reruns
        save_cached_script(cache_file, script, active_prompt, media_files)

    # 5. Interactive Review Menu (Requested: "ver el prompt en consola y modificarlo antes de renderizar")
    if not args.non_interactive:
        proceed, script, active_prompt = interactive_prompt_review_menu(
            copywriter=copywriter,
            media_files=media_files,
            user_prompt=active_prompt,
            script=script,
            product_name=args.product,
            offer=args.offer,
            cta=args.cta,
            target_duration=args.duration,
            language=args.language,
            cache_file=cache_file,
        )
        if not proceed:
            sys.exit(0)
    else:
        print("⚡ Modo no interactivo activado: Procediendo directo al renderizado.")

    # 6. Audio Synthesis (TTS)
    tts_mgr = TTSManager(language=args.language, voice=args.voice)
    narration_audio, scene_timings, raw_total_duration = tts_mgr.synthesize_script(
        script=script,
        output_dir=TEMP_DIR / "ad_audio"
    )

    if not narration_audio or not narration_audio.exists():
        print("\n❌ Error: Falló la síntesis de audio para la narración.")
        sys.exit(1)

    # 7. Pixabay Music Engine & Beat-Sync Alignment
    genre_key = args.music_genre if args.music_genre != "auto" else script.get("music_genre", "commercial_trap")
    target_bpm = args.bpm if args.bpm else float(script.get("target_bpm", 124.0))

    music_engine = PixabayMusicEngine()
    bg_track, beat_grid = music_engine.get_or_create_ad_music(
        genre_key=genre_key,
        target_duration=raw_total_duration + 8.0,
        custom_music_path=args.music if (args.music and args.music != "none") else None
    )
    if args.bpm:
        beat_grid = BeatGrid(bpm=args.bpm)

    enable_trans = (args.transition != "none")
    trans_duration = TRANSITION_DURATION if enable_trans else 0.0

    # Rhythmic Beat-Snapping: align scene durations to musical downbeats
    if not args.no_beat_sync:
        speech_durations = [t["duration"] for t in scene_timings]
        aligned_scenes = beat_grid.align_scene_durations(
            speech_durations=speech_durations,
            transition_duration=trans_duration
        )
        print(f"\n🥁 Sincronización Rítmica Beat-Sync activada ({beat_grid.bpm:.0f} BPM):")
        print(f"   Compás de 4 tiempos: {beat_grid.seconds_per_bar:.2f}s | Beat: {beat_grid.seconds_per_beat:.2f}s")
        for s in aligned_scenes:
            print(f"   - Escena {s['scene_idx']:02d}: Voz {s['speech_duration']:.1f}s ➔ Toma visual {s['snapped_duration']:.2f}s (Corte en compás: {s['cut_time']:.2f}s)")

        # Pad individual scene audio files with rhythmic breathing pause before the cut
        padded_files = []
        current_time_acc = 0.0
        for i, s_info in enumerate(aligned_scenes):
            orig_timing = scene_timings[i]
            orig_audio = Path(orig_timing["audio_file"])
            padded_audio = TEMP_DIR / "ad_audio" / f"scene_{s_info['scene_idx']:02d}_padded.mp3"
            pad_needed = s_info["padding_after_speech"]

            if pad_needed > 0.04:
                pad_cmd = [
                    "ffmpeg", "-y",
                    "-i", str(orig_audio),
                    "-af", f"apad=pad_dur={pad_needed:.3f}",
                    "-t", f"{s_info['snapped_duration']:.3f}",
                    "-acodec", "libmp3lame", "-b:a", "192k",
                    str(padded_audio)
                ]
                subprocess.run(pad_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                padded_files.append(padded_audio)
            else:
                padded_files.append(orig_audio)

            orig_timing["start"] = round(current_time_acc, 2)
            orig_timing["duration"] = s_info["snapped_duration"]
            orig_timing["end"] = round(current_time_acc + s_info["snapped_duration"], 2)
            current_time_acc += s_info["snapped_duration"]

        # Recombine audio tracks with beat pauses
        beatsynced_audio = TEMP_DIR / "ad_audio" / "narration_beatsynced.mp3"
        tts_mgr._concat_audios(padded_files, beatsynced_audio)
        if beatsynced_audio.exists() and beatsynced_audio.stat().st_size > 0:
            narration_audio = beatsynced_audio
            total_duration = get_media_duration(narration_audio)
        else:
            total_duration = raw_total_duration
    else:
        total_duration = raw_total_duration

    # 8. Subtitles Generation (Karaoke with High Contrast & Hook Title Banner)
    fmt_cfg = resolve_video_format("vertical")
    hook_banner = script.get("hook_title") or script.get("title") or "¡OFERTA EXCLUSIVA!"
    hook_bar_duration = round(beat_grid.seconds_per_bar * 2, 2) if not args.no_beat_sync else 2.8

    sub_gen = SubtitleGenerator(
        width=fmt_cfg["width"],
        height=fmt_cfg["height"],
        margin_bottom=fmt_cfg["subtitle_margin_bottom"],
        font_size=fmt_cfg["subtitle_font_size"],
        dynamic_highlight=True,
        highlight_color="&H0000FFFF&",  # High-energy vibrant yellow (ASS BGR)
        animation="pop"
    )

    srt_path, ass_path = sub_gen.generate_subtitles(
        scene_timings=scene_timings,
        language=args.language,
        hook_title=hook_banner,
        hook_duration=hook_bar_duration
    )

    # 9. Background Music Preparation (Auto-Ducking)
    prepared_music = None
    if args.music != "none" and bg_track and bg_track.exists():
        music_mgr = MusicManager()
        prepared_music = music_mgr.prepare_music(
            bg_track,
            target_duration=total_duration,
            volume=MUSIC_VOLUME
        )

    # 10. Visual Scene Clips Rendering (Smart vertical framing & Ken Burns motion)
    renderer = VideoRenderer(
        width=fmt_cfg["width"],
        height=fmt_cfg["height"],
        fps=VIDEO_FPS,
        crf=VIDEO_CRF,
        preset=VIDEO_PRESET,
        enable_broll_split=False,  # Keep user's primary photos clean
        enable_punch_in=True
    )

    print(f"\n🎞️  Procesando {len(scene_timings)} tomas visuales en formato vertical 9:16 ({fmt_cfg['width']}x{fmt_cfg['height']})...")
    scene_clips = []
    num_scenes = len(scene_timings)
    enable_trans = (args.transition != "none")
    trans_duration = TRANSITION_DURATION if enable_trans else 0.0

    for i, timing in enumerate(scene_timings):
        s_idx = timing["scene_id"]
        s_dur = timing["duration"]
        # Map scene to media files cyclically
        media_file = media_files[(s_idx - 1) % len(media_files)]
        is_video = media_file.suffix.lower() in SUPPORTED_VIDEO_EXTS
        pad = trans_duration if (enable_trans and i < num_scenes - 1) else 0.0

        clip = renderer.render_scene_clip(
            asset_path=media_file,
            duration=s_dur,
            scene_idx=s_idx,
            is_video=is_video,
            transition_pad=pad
        )
        scene_clips.append(clip)

    # 10. Assemble Final Video Output
    out_dir = Path(args.output) if args.output else (OUTPUT_DIR / "ads")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    sanitized_prod = "".join([c if c.isalnum() else "_" for c in (args.product or "anuncio")])[:20].strip("_")
    out_filename = f"ad_{sanitized_prod}_{timestamp}.mp4"

    final_video_path = renderer.assemble_final_video(
        scene_clips=scene_clips,
        narration_audio=narration_audio,
        subtitles_file=ass_path,
        output_filename=out_filename,
        background_music=prepared_music,
        output_dir=out_dir,
        scene_durations=[t["duration"] for t in scene_timings],
        transition=args.transition,
        transition_duration=trans_duration,
        auto_ducking=True
    )

    elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print("🎉  ¡VIDEO PUBLICITARIO GENERADO CON ÉXITO!")
    print("=" * 65)
    print(f"📦 Archivo final:     {final_video_path.resolve()}")
    print(f"⏱️  Duración:          {total_duration:.1f} segundos")
    print(f"📐 Formato:           {fmt_cfg['width']}x{fmt_cfg['height']} (9:16 Vertical)")
    print(f"⚡ Tiempo de render:  {elapsed:.1f} segundos")
    print(f"💬 Subtítulos:        {ass_path.name} (Animación dinámica Karaoke)")
    print("=" * 65)
    print(f"🚀 Listo para publicar en TikTok Ads, Meta Reels y YouTube Shorts.\n")


if __name__ == "__main__":
    main()
