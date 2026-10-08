#!/usr/bin/env python3
"""
GCP NotebookLM Video Tutorial Generator - Dedicated CLI.
Creates 2-host conversational deep dives (NotebookLM style) with synchronized technical slides,
vocal debate, and high-resolution architecture diagrams for Google Cloud Platform.

Usage:
  python gcp_tutorial.py --sample
  python gcp_tutorial.py --topic "Cloud Run"
  python gcp_tutorial.py --topic "IAM Least Privilege" --notes "Solo dar roles predefinidos"
  python gcp_tutorial.py --notes-file mis_apuntes_gcp.md
  python gcp_tutorial.py --slides-only --topic "VPC Networking"
  python gcp_tutorial.py --format vertical --topic "Cloud Run"
  python gcp_tutorial.py --list-topics
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from ai.gcp_notebook_generator import GCPTutorialGenerator, CURATED_GCP_LESSONS
from config import OUTPUT_DIR, TEMP_DIR
from utils.files import check_ffmpeg
from video.gcp_video_builder import GCPVideoBuilder
from video.slide_renderer import GCPSlideRenderer


def parse_args():
    parser = argparse.ArgumentParser(
        description="☁️ GCP NotebookLM Tutorial Generator: Crea video tutoriales con debate entre 2 voces y diapositivas técnicas de Google Cloud.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Tema de Google Cloud (ej. 'Cloud Run', 'IAM', 'VPC', 'BigQuery', 'Cloud Functions')."
    )
    parser.add_argument(
        "--notes",
        type=str,
        default=None,
        help="Tus notas o apuntes tomados mientras estudiaste GCP."
    )
    parser.add_argument(
        "--notes-file",
        type=str,
        default=None,
        help="Ruta a un archivo .txt o .md con tus notas de estudio de GCP."
    )
    parser.add_argument(
        "--sample", "--demo",
        dest="sample",
        action="store_true",
        help="Ejecuta una demostración instantánea completa sobre Cloud Run vs Compute Engine."
    )
    parser.add_argument(
        "--format",
        choices=["horizontal", "vertical"],
        default="horizontal",
        help="Formato de video: 'horizontal' (1920x1080 para YouTube/Clases) o 'vertical' (1080x1920 para Shorts/Reels)."
    )
    parser.add_argument(
        "--slides-only",
        action="store_true",
        help="Exporta únicamente las diapositivas vectoriales en PNG de alta resolución (sin renderizar video ni TTS)."
    )
    parser.add_argument(
        "--list-topics",
        action="store_true",
        help="Muestra la lista de temas oficiales de GCP listos para generar inmediatamente."
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Ruta personalizada para guardar el archivo de video final (.mp4)."
    )
    parser.add_argument(
        "--no-music",
        action="store_true",
        help="Desactiva la música ambiental de fondo."
    )
    parser.add_argument(
        "--no-subtitles",
        action="store_true",
        help="Desactiva los subtítulos sobreimpresos."
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.20,
        help="Velocidad de locución de las voces (por defecto: 1.20x para ritmo ágil sin pausas muertas)."
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=15,
        help="Cuadros por segundo para exportación (por defecto: 15 FPS para reducir el tamaño al mínimo)."
    )
    parser.add_argument(
        "--codec",
        choices=["x264", "x265"],
        default="x264",
        help="Códec de video: 'x264' (universal para todo navegador y móvil) o 'x265' (máxima compresión HEVC)."
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=26,
        help="Factor de tasa constante (por defecto: 26 para alta nitidez de texto y compresión máxima)."
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Modo interactivo: revisa el guion y el esquema de diapositivas en la terminal antes de renderizar."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("\n" + "=" * 70)
    print("☁️  GOOGLE CLOUD PLATFORM • NOTEBOOK LM VIDEO STUDIO  🎙️")
    print("   Debate Técnico Multipersona + Diapositivas Arquitectónicas HD")
    print("=" * 70)

    # 1. Check FFmpeg
    if not check_ffmpeg():
        print("\n❌ Error: FFmpeg es requerido para renderizar diapositivas y video.")
        sys.exit(1)

    generator = GCPTutorialGenerator()

    # 2. Handle --list-topics
    if args.list_topics:
        topics = generator.list_curated_topics()
        print("\n📚 Temas Curados de Google Cloud Disponibles:")
        print("-" * 70)
        for t in topics:
            print(f"  • {t['slug'].upper()}: {t['title']}")
            print(f"    Categoría: {t['category']} | {t['slides_count']} Diapositivas | {t['dialogue_turns']} Intervenciones")
            print(f"    Ejecución: python gcp_tutorial.py --topic \"{t['slug']}\"\n")
        return

    # 3. Resolve notes & topic
    user_notes = args.notes
    if args.notes_file:
        p = Path(args.notes_file)
        if p.exists():
            user_notes = p.read_text(encoding="utf-8")
            print(f"📄 Notas cargadas desde archivo: {p} ({len(user_notes)} caracteres)")
        else:
            print(f"⚠️ Advertencia: No se encontró el archivo de notas {p}.")

    # 4. Resolve topic
    topic = args.topic
    if args.sample:
        topic = "cloud_run"
        print("💡 Modo DEMO activado: Seleccionando lección 'Cloud Run vs Compute Engine'.")
    elif not topic:
        if user_notes:
            topic = "Conceptos de mis Notas de GCP"
        else:
            # Interactive prompt
            print("\nIntroduce el tema de GCP que quieres aprender o debatir:")
            print("  [1] Cloud Run (Microservicios & Serverless)")
            print("  [2] IAM & Service Accounts (Menor Privilegio)")
            print("  [3] VPC & Redes Privadas (Cloud SQL & NAT)")
            print("  [4] Tema personalizado...")
            try:
                choice = input("\nElige una opción (1-4) o escribe el nombre del tema: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nOperación cancelada.")
                sys.exit(0)

            if choice == "1":
                topic = "cloud_run"
            elif choice == "2":
                topic = "iam_security"
            elif choice == "3":
                topic = "vpc_networking"
            elif choice == "4" or not choice:
                topic = input("Nombre del tema de GCP (ej. BigQuery, Pub/Sub, GKE): ").strip() or "cloud_run"
            else:
                topic = choice

    # 5. Generate lesson specification (Slides + Dialogue)
    print(f"\n🧠 [NotebookLM Generator] Diseñando lección para: '{topic}'...")
    lesson = generator.generate_lesson(topic=topic, user_notes=user_notes)

    print(f"\n✨ Lección Estructurada: {lesson.get('title')}")
    print(f"   Categoría: {lesson.get('category')}")
    print(f"   Resumen: {lesson.get('summary')}")
    print(f"   Diapositivas diseñadas: {len(lesson.get('slides', []))}")
    print(f"   Líneas de debate: {len(lesson.get('dialogue', []))}")

    # 6. Interactive review if requested
    if args.interactive:
        print("\n--- ESQUEMA DE DIAPOSITIVAS ---")
        for s in lesson.get("slides", []):
            print(f"  [Slide {s['slide_id']}] ({s['layout']}) {s['title']} — {s.get('subtitle', '')}")
        print("\n--- DIÁLOGO NOTEBOOK LM ---")
        for d in lesson.get("dialogue", []):
            print(f"  🎙️ {d['speaker']}: \"{d['text']}\"")
        try:
            proceed = input("\n¿Deseas proceder con el renderizado? (S/n): ").strip().lower()
            if proceed and proceed != "s" and proceed != "y" and proceed != "si":
                print("Operación cancelada por el usuario.")
                return
        except (EOFError, KeyboardInterrupt):
            return

    # 7. Dimensions setup
    is_vertical = args.format == "vertical"
    width = 1080 if is_vertical else 1920
    height = 1920 if is_vertical else 1080

    # 8. Slides only mode
    if args.slides_only:
        print(f"\n🖼️ Modo Solo Diapositivas: Exportando imágenes PNG...")
        out_slides_dir = OUTPUT_DIR / "gcp_tutorials" / f"{topic.lower().replace(' ', '_')}_slides"
        out_slides_dir.mkdir(parents=True, exist_ok=True)
        renderer = GCPSlideRenderer(width, height)
        slides = lesson.get("slides", [])
        for s in slides:
            svg = renderer.render_slide_svg(
                slide=s,
                active_speaker="Alex",
                current_slide_num=s["slide_id"],
                total_slides=len(slides),
                series_category=lesson.get("category", "Google Cloud")
            )
            out_png = out_slides_dir / f"slide_{s['slide_id']:02d}.png"
            renderer.rasterize_svg_to_png(svg, out_png)
            print(f"   ✅ Diapositiva {s['slide_id']:02d} guardada en: {out_png}")
        print(f"\n🎉 ¡Todas las diapositivas han sido guardadas en: {out_slides_dir}")
        return

    # 9. Build full audiovisual tutorial video
    selected_codec = "libx265" if args.codec == "x265" else "libx264"
    builder = GCPVideoBuilder(
        width=width,
        height=height,
        burn_subtitles=not args.no_subtitles,
        enable_music=not args.no_music,
        speech_speed=args.speed,
        fps=args.fps,
        crf=args.crf,
        codec=selected_codec
    )

    out_file = Path(args.output).name if args.output else None
    video_path = builder.build_tutorial_video(lesson=lesson, output_file_name=out_file)

    print("\n" + "=" * 70)
    print("🎬  ¡VIDEO TUTORIAL DE GOOGLE CLOUD GENERADO CON ÉXITO!  🎉")
    print(f"   📂 Ruta del video: {video_path}")
    print(f"   💡 Formato: {width}x{height} {'(Horizontal 16:9)' if not is_vertical else '(Vertical 9:16)'}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
