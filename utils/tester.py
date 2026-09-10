"""
Video & Script Auditor / Tester Module.
Allows inspecting, auditing, and interactively refining the script, audio narration,
and visual media assets before committing to expensive video rendering.
Generates an interactive HTML visual storyboard and provides a CLI audit menu.
"""

import json
import os
import re
import shutil
import sys
import webbrowser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config import ASSETS_DIR, AUDIO_DIR, OUTPUT_DIR
from utils.files import get_media_duration, sanitize_filename


def _count_words(text: str) -> int:
    """Count words in a narration string."""
    return len(re.findall(r'\b\w+\b', text or ''))


def generate_audit_html(
    script: Dict[str, Any],
    scene_assets: List[Dict[str, Any]],
    assets_metadata: List[Dict[str, Any]],
    scene_timings: List[Dict[str, Any]],
    topic: str,
    output_html_path: Path,
    narration_audio_path: Optional[Path] = None
) -> Path:
    """
    Generate an interactive, standalone HTML storyboard for visual & script auditing.
    Displays side-by-side previews of media, narration, audio playback, pacing, and keywords.
    """
    output_html_path = Path(output_html_path)
    output_html_path.parent.mkdir(parents=True, exist_ok=True)

    title = script.get("title") or topic or "Video Storyboard Audit"
    hook = script.get("hook") or ""
    scenes = script.get("scenes", [])
    total_duration = sum(item.get("duration", 0.0) for item in scene_assets)

    num_videos = sum(1 for item in scene_assets if item.get("is_video"))
    num_images = len(scene_assets) - num_videos
    motion_ratio = (num_videos / len(scene_assets) * 100) if scene_assets else 0

    # Calculate relative paths from HTML location
    html_dir = output_html_path.parent.resolve()
    assets_local_dir = html_dir / "assets"

    def get_rel_url(file_path: Optional[Path]) -> str:
        if not file_path:
            return ""
        p = Path(file_path).resolve()
        # If the file also exists in video_folder/assets, prioritize that relative path
        if assets_local_dir.exists():
            candidate = assets_local_dir / p.name
            if candidate.exists():
                return f"assets/{candidate.name}"
        try:
            return str(os.path.relpath(p, html_dir)).replace("\\", "/")
        except ValueError:
            return p.as_uri()

    full_audio_rel = get_rel_url(narration_audio_path) if narration_audio_path else ""

    # Build scene cards HTML
    cards_html = []
    for i, (scene, timing, asset_item, meta) in enumerate(
        zip(scenes, scene_timings, scene_assets, assets_metadata),
        start=1
    ):
        s_idx = asset_item.get("scene_idx", i)
        s_duration = asset_item.get("duration", timing.get("duration", 0.0))
        is_video = asset_item.get("is_video", False)
        asset_file = asset_item.get("file")
        rel_media_url = get_rel_url(asset_file) if asset_file else ""

        audio_file = timing.get("audio_file")
        rel_audio_url = get_rel_url(audio_file) if audio_file else ""

        narration = scene.get("narration", "").strip()
        word_count = _count_words(narration)
        word_status_class = "badge-ok" if word_count <= 16 else "badge-warn"
        word_status_text = f"{word_count} palabras" + (" (óptimo)" if word_count <= 16 else " (denso >16)")

        media_badge_class = "badge-video" if is_video else "badge-image"
        media_badge_text = "🎬 VIDEO (MOVIMIENTO)" if is_video else "📷 IMAGEN ESTÁTICA"

        provider_name = (meta.get("provider") or ("NASA" if "nasa" in str(asset_file).lower() else "STOCK")).upper()
        subject = scene.get("visual_subject") or meta.get("title") or f"Escena {s_idx}"

        nasa_kws = scene.get("nasa_keywords", [])
        stock_kws = scene.get("pexels_keywords") or scene.get("stock_keywords", [])
        image_prompt = scene.get("image_prompt", "")

        # Media preview element
        if asset_file and asset_file.exists():
            if is_video:
                media_element = f"""
                <div class="media-container">
                    <video src="{rel_media_url}" controls muted loop playsinline preload="metadata"></video>
                    <div class="media-overlay-badge">{provider_name}</div>
                </div>
                """
            else:
                media_element = f"""
                <div class="media-container">
                    <img src="{rel_media_url}" alt="{subject}" loading="lazy" />
                    <div class="media-overlay-badge">{provider_name}</div>
                </div>
                """
        else:
            media_element = """
            <div class="media-placeholder">
                <p>⚠️ Sin archivo asignado</p>
            </div>
            """

        card = f"""
        <div class="scene-card {'card-warn' if not is_video else ''}" id="scene-card-{s_idx}">
            <div class="scene-header">
                <div class="scene-title-group">
                    <span class="scene-number">#{s_idx:02d}</span>
                    <span class="scene-subject">{subject}</span>
                </div>
                <div class="scene-badges">
                    <span class="badge {media_badge_class}">{media_badge_text}</span>
                    <span class="badge badge-provider">{provider_name}</span>
                    <span class="badge badge-time">⏱️ {s_duration:.1f}s ({timing.get('start', 0):.1f}s - {timing.get('end', 0):.1f}s)</span>
                    <span class="badge {word_status_class}">{word_status_text}</span>
                </div>
            </div>

            <div class="scene-body">
                <div class="scene-media-col">
                    {media_element}
                    {f'<audio controls src="{rel_audio_url}" class="scene-audio-player"></audio>' if rel_audio_url else ''}
                </div>

                <div class="scene-info-col">
                    <div class="info-block">
                        <label>🗣️ GUION / NARRACIÓN NATIVA:</label>
                        <div class="narration-box">"{narration}"</div>
                    </div>

                    <div class="info-block meta-details">
                        <label>🔍 METADATOS Y PALABRAS CLAVE:</label>
                        <ul class="meta-list">
                            {f'<li><strong>NASA keywords:</strong> <code>{", ".join(nasa_kws)}</code></li>' if nasa_kws else ''}
                            {f'<li><strong>Stock keywords:</strong> <code>{", ".join(stock_kws)}</code></li>' if stock_kws else ''}
                            {f'<li><strong>Atribución:</strong> {meta.get("attribution_text", "Dominio Público")}</li>' if meta.get("attribution_text") else ''}
                            {f'<li><strong>Archivo local:</strong> <code>{asset_file.name if asset_file else "None"}</code></li>' if asset_file else ''}
                        </ul>
                    </div>

                    {f'''
                    <div class="info-block prompt-block">
                        <label>🎨 PROMPT DE GENERACIÓN IA (FLUX):</label>
                        <div class="prompt-box">{image_prompt}</div>
                    </div>
                    ''' if image_prompt else ''}
                </div>
            </div>
        </div>
        """
        cards_html.append(card)

    cards_joined = "\n".join(cards_html)

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoría de Video: {title}</title>
    <style>
        :root {{
            --bg-color: #0d1117;
            --card-bg: #161b22;
            --border-color: #30363d;
            --text-main: #f0f6fc;
            --text-muted: #8b949e;
            --accent-cyan: #58a6ff;
            --accent-green: #3fb950;
            --accent-amber: #d29922;
            --accent-red: #f85149;
            --badge-video-bg: #238636;
            --badge-image-bg: #9e6a03;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            padding: 24px;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .header-title {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 8px;
        }}
        .header-hook {{
            font-size: 1.1rem;
            color: var(--accent-cyan);
            margin-bottom: 16px;
            font-style: italic;
        }}
        .stats-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            padding-top: 16px;
            border-top: 1px solid var(--border-color);
        }}
        .stat-item {{
            background: #21262d;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 0.9rem;
        }}
        .full-audio-player {{
            margin-top: 16px;
            width: 100%;
        }}
        .scene-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            margin-bottom: 20px;
            overflow: hidden;
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}
        .scene-card:hover {{
            border-color: var(--accent-cyan);
        }}
        .scene-card.card-warn {{
            border-left: 4px solid var(--accent-amber);
        }}
        .scene-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            padding: 14px 20px;
            background: #1c2128;
            border-bottom: 1px solid var(--border-color);
        }}
        .scene-title-group {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .scene-number {{
            font-size: 1.1rem;
            font-weight: 800;
            color: var(--accent-cyan);
        }}
        .scene-subject {{
            font-size: 1.05rem;
            font-weight: 600;
        }}
        .scene-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .badge {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 6px;
            text-transform: uppercase;
        }}
        .badge-video {{ background: var(--badge-video-bg); color: #fff; }}
        .badge-image {{ background: var(--badge-image-bg); color: #fff; }}
        .badge-provider {{ background: #30363d; color: #c9d1d9; }}
        .badge-time {{ background: #1f6feb; color: #fff; }}
        .badge-ok {{ background: #238636; color: #fff; }}
        .badge-warn {{ background: #d29922; color: #000; }}
        .scene-body {{
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 20px;
            padding: 20px;
        }}
        @media (max-width: 860px) {{
            .scene-body {{ grid-template-columns: 1fr; }}
        }}
        .scene-media-col {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .media-container {{
            position: relative;
            background: #000;
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            max-height: 480px;
        }}
        .media-container video, .media-container img {{
            width: 100%;
            height: auto;
            max-height: 420px;
            object-fit: contain;
            display: block;
        }}
        .media-overlay-badge {{
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(0,0,0,0.75);
            color: #fff;
            font-size: 0.7rem;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
            backdrop-filter: blur(4px);
        }}
        .media-placeholder {{
            background: #21262d;
            border: 2px dashed var(--border-color);
            border-radius: 8px;
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-muted);
        }}
        .scene-audio-player {{
            width: 100%;
            height: 36px;
        }}
        .scene-info-col {{
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}
        .info-block label {{
            display: block;
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-muted);
            margin-bottom: 6px;
            letter-spacing: 0.5px;
        }}
        .narration-box {{
            background: #0d1117;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px;
            font-size: 1.15rem;
            font-weight: 500;
            color: #58a6ff;
            line-height: 1.45;
        }}
        .meta-list {{
            list-style: none;
            font-size: 0.85rem;
            color: var(--text-muted);
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .meta-list code {{
            background: #21262d;
            padding: 2px 6px;
            border-radius: 4px;
            color: #79c0ff;
        }}
        .prompt-box {{
            background: #0d1117;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 10px;
            font-size: 0.8rem;
            color: #8b949e;
            font-family: monospace;
            max-height: 80px;
            overflow-y: auto;
        }}
        .tips-banner {{
            background: #1c2128;
            border: 1px solid var(--accent-cyan);
            border-radius: 8px;
            padding: 16px;
            margin-top: 24px;
            font-size: 0.9rem;
        }}
        .tips-banner h4 {{
            color: var(--accent-cyan);
            margin-bottom: 6px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-title">🌌 {title}</div>
            {f'<div class="header-hook">🪝 "{hook}"</div>' if hook else ''}

            <div class="stats-bar">
                <div class="stat-item">⏱️ Duración Total: <strong>{total_duration:.1f}s</strong></div>
                <div class="stat-item">📋 Escenas: <strong>{len(scenes)}</strong></div>
                <div class="stat-item">🎬 Videos en movimiento: <strong style="color: {'var(--accent-green)' if motion_ratio >= 60 else 'var(--accent-amber)'};">{num_videos}/{len(scene_assets)} ({motion_ratio:.0f}%)</strong></div>
                <div class="stat-item">📷 Imágenes fijas: <strong>{num_images}</strong></div>
            </div>

            {f'''
            <div style="margin-top: 16px;">
                <label style="font-size: 0.8rem; font-weight: 700; color: var(--text-muted);">🎵 NARRACIÓN COMPLETA SINCRONIZADA:</label>
                <audio controls src="{full_audio_rel}" class="full-audio-player"></audio>
            </div>
            ''' if full_audio_rel else ''}
        </header>

        <main>
            {cards_joined}
        </main>

        <div class="tips-banner">
            <h4>💡 Guía de Auditoría de Calidad</h4>
            <ul style="margin-left: 20px; margin-top: 8px; line-height: 1.6;">
                <li><strong>Evitar efecto diapositiva:</strong> Prioriza escenas con el badge verde <code>[VIDEO (MOVIMIENTO)]</code>. Si una escena tiene imagen fija, puedes re-buscarla como video en Pexels o generar un loop 3D.</li>
                <li><strong>Ritmo de narración:</strong> Mantén el texto por debajo de 16 palabras para que el locutor respire con naturalidad y las pausas dramáticas funcionen.</li>
                <li><strong>Concordancia:</strong> Asegúrate de que lo que se ve en la miniatura describa con precisión lo que se lee en la narración.</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""
    output_html_path.write_text(html_content, encoding="utf-8")
    return output_html_path


def print_audit_console_summary(
    script: Dict[str, Any],
    scene_assets: List[Dict[str, Any]],
    assets_metadata: List[Dict[str, Any]],
    scene_timings: List[Dict[str, Any]],
    topic: str
) -> None:
    """Print an aesthetic, structured audit table in the terminal."""
    total_duration = sum(item.get("duration", 0.0) for item in scene_assets)
    num_videos = sum(1 for item in scene_assets if item.get("is_video"))
    num_images = len(scene_assets) - num_videos
    motion_ratio = (num_videos / len(scene_assets) * 100) if scene_assets else 0

    print("\n" + "═" * 70)
    print("🔍  PANEL DE AUDITORÍA & TESTING DE VIDEO (PRE-RENDER)")
    print("═" * 70)
    print(f"🎯 Tema:       '{topic}'")
    print(f"📋 Título:     \"{script.get('title', topic)}\"")
    if script.get("hook"):
        print(f"🪝 Hook:       \"{script.get('hook')}\"")
    print(f"⏱️  Duración:   ~{total_duration:.1f} segundos ({len(scene_assets)} escenas)")
    print(f"🎬 Dinamismo:  {num_videos} videos / {num_images} fotos ({motion_ratio:.0f}% en movimiento)")
    print("─" * 70)

    warnings = []

    for i, (timing, asset_item, meta) in enumerate(zip(scene_timings, scene_assets, assets_metadata), start=1):
        s_idx = asset_item.get("scene_idx", i)
        s_duration = asset_item.get("duration", timing.get("duration", 0.0))
        is_video = asset_item.get("is_video", False)
        asset_file = asset_item.get("file")
        narration = timing.get("narration", "").strip()
        word_count = _count_words(narration)

        media_icon = "🎬 VIDEO " if is_video else "📷 IMAGEN"
        provider = (meta.get("provider") or ("NASA" if "nasa" in str(asset_file).lower() else "STOCK")).upper()
        file_name = asset_file.name if asset_file else "SIN ARCHIVO"

        status_flag = "✅"
        if not is_video:
            status_flag = "⚠️ FOTO"
            warnings.append(f"Escena {s_idx:02d}: Es una imagen fija. Podría percibirse como diapositiva sin movimiento.")
        if word_count > 16:
            warnings.append(f"Escena {s_idx:02d}: Guion extenso ({word_count} palabras). Puede sonar acelerado.")

        print(f"[{s_idx:02d}] {media_icon} ({provider:<6}) | ⏱️ {s_duration:4.1f}s | 📝 {word_count:2d} palabras | {status_flag}")
        print(f"     🗣️ \"{narration[:65]}{'...' if len(narration) > 65 else ''}\"")
        print(f"     📁 {file_name}")

    print("─" * 70)
    if warnings:
        print("⚠️  AVISOS DE AUDITORÍA DETECTADOS:")
        for w in warnings:
            print(f"   • {w}")
    else:
        print("✨ ¡Todo en orden! Guion conciso y óptimo porcentaje de video en movimiento.")
    print("═" * 70 + "\n")


def interactive_audit_menu(
    script: Dict[str, Any],
    scene_assets: List[Dict[str, Any]],
    assets_metadata: List[Dict[str, Any]],
    scene_timings: List[Dict[str, Any]],
    topic: str,
    tts_mgr: Any,
    providers_dict: Dict[str, Any],
    orientation: str = "portrait",
    html_report_path: Optional[Path] = None
) -> Tuple[bool, Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Interactive CLI loop allowing user to review and tweak script/assets before rendering.
    Returns:
        (proceed_to_render: bool, script, scene_assets, assets_metadata, scene_timings)
    """
    nasa = providers_dict.get("nasa")
    pexels = providers_dict.get("pexels")
    pixabay = providers_dict.get("pixabay")
    pollinations = providers_dict.get("pollinations")

    if not html_report_path:
        html_report_path = ASSETS_DIR / "storyboard_audit.html"

    # Generate initial HTML
    generate_audit_html(
        script=script,
        scene_assets=scene_assets,
        assets_metadata=assets_metadata,
        scene_timings=scene_timings,
        topic=topic,
        output_html_path=html_report_path
    )

    print_audit_console_summary(script, scene_assets, assets_metadata, scene_timings, topic)
    print(f"🌐 Storyboard visual generado en: {html_report_path.resolve()}\n")

    # Detect non-interactive environment (e.g. running inside Docker without -it)
    is_interactive = sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else False
    if not is_interactive:
        print("⚠️  Entorno no interactivo detectado (Docker sin flags -it o ejecución en background).")
        print("   Se generó el storyboard HTML y los recursos fueron preservados en la carpeta del video.")
        print("   Para interactuar con este menú en Docker, ejecuta: docker run -it ... o docker compose run ...")
        print("   Aprobando automáticamente para proceder al renderizado...")
        return True, script, scene_assets, assets_metadata, scene_timings

    while True:
        print("\n" + "=" * 55)
        print("🛠️   MENÚ DEL MODO TESTER & AUDITORÍA")
        print("=" * 55)
        print("  [1] 📋 Ver resumen de escenas y guion")
        print("  [2] ✏️  Editar narración de una escena (re-sintetiza audio)")
        print("  [3] 🔄 Cambiar o re-buscar asset visual de una escena")
        print("  [4] 🌐 Abrir / ver Storyboard HTML")
        print("  [5] ✅ APROBAR Y PROCEDER AL RENDER FINAL")
        print("  [6] 🛑 SALIR SIN RENDERIZAR (Conservar guion y archivos)")
        print("=" * 55)

        try:
            choice = input("👉 Selecciona una opción [1-6] (Enter para aprobar): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n🛑 Cancelado por el usuario.")
            return False, script, scene_assets, assets_metadata, scene_timings

        if choice in ("", "5"):
            print("\n🚀 ¡Aprobado! Iniciando renderizado de video final...")
            return True, script, scene_assets, assets_metadata, scene_timings

        elif choice == "1":
            print_audit_console_summary(script, scene_assets, assets_metadata, scene_timings, topic)

        elif choice == "2":
            # Edit narration
            try:
                raw_idx = input(f"¿Qué número de escena deseas editar? (1 a {len(scene_assets)}): ").strip()
                if not raw_idx.isdigit() or not (1 <= int(raw_idx) <= len(scene_assets)):
                    print("⚠️ Número de escena inválido.")
                    continue
                s_idx = int(raw_idx)
                scene_ref = script["scenes"][s_idx - 1]
                print(f"\nTexto actual de la escena {s_idx:02d}:")
                print(f"  \"{scene_ref.get('narration')}\"")
                new_text = input("Escribe la nueva narración (o presiona Enter para cancelar): ").strip()

                if new_text:
                    scene_ref["narration"] = new_text
                    print(f"\n🎙️ Re-sintetizando audio para la escena {s_idx:02d}...")
                    _, new_timings, _ = tts_mgr.synthesize_script(script)
                    scene_timings = new_timings
                    # Update duration in scene_assets
                    for item, timing in zip(scene_assets, scene_timings):
                        item["duration"] = timing["duration"]

                    # Refresh HTML
                    generate_audit_html(
                        script=script,
                        scene_assets=scene_assets,
                        assets_metadata=assets_metadata,
                        scene_timings=scene_timings,
                        topic=topic,
                        output_html_path=html_report_path
                    )
                    print("✅ Narración y duraciones actualizadas con éxito.")
            except Exception as e:
                print(f"⚠️ Error al editar narración: {e}")

        elif choice == "3":
            # Change / re-search asset
            try:
                raw_idx = input(f"¿De qué escena deseas cambiar el visual? (1 a {len(scene_assets)}): ").strip()
                if not raw_idx.isdigit() or not (1 <= int(raw_idx) <= len(scene_assets)):
                    print("⚠️ Número de escena inválido.")
                    continue
                s_idx = int(raw_idx)
                asset_item = scene_assets[s_idx - 1]
                meta_item = assets_metadata[s_idx - 1]

                print(f"\nVisual actual de la escena {s_idx:02d}: {asset_item.get('file')}")
                print("  [1] Re-buscar en Pexels (Videos en movimiento)")
                print("  [2] Re-buscar en Pixabay (Simulaciones 3D / Espacio)")
                print("  [3] Re-buscar en NASA (Observaciones científicas)")
                print("  [4] Generar nueva imagen con IA Pollinations (FLUX)")
                print("  [5] Asignar archivo local propio (video o imagen)")
                print("  [0] Cancelar")

                sub_choice = input("👉 Elige fuente [1-5]: ").strip()

                new_file = None
                new_meta = None

                if sub_choice == "1" and pexels and pexels.is_configured():
                    kw_input = input("Keywords para Pexels (ej: 'space nebula timelapse'): ").strip()
                    kws = [k.strip() for k in kw_input.split(",") if k.strip()] or [topic]
                    new_file, new_meta = pexels.fetch_scene_asset(
                        scene_idx=s_idx,
                        keywords=kws,
                        preferred_type="video",
                        orientation=orientation
                    )
                elif sub_choice == "2" and pixabay and pixabay.is_configured():
                    kw_input = input("Keywords para Pixabay (ej: 'black hole 3d'): ").strip()
                    kws = [k.strip() for k in kw_input.split(",") if k.strip()] or [topic]
                    new_file, new_meta = pixabay.fetch_scene_asset(
                        scene_idx=s_idx,
                        keywords=kws,
                        preferred_type="video",
                        orientation=orientation
                    )
                elif sub_choice == "3" and nasa:
                    kw_input = input("Keywords para NASA (ej: 'solar flare'): ").strip()
                    kws = [k.strip() for k in kw_input.split(",") if k.strip()] or [topic]
                    new_file, new_meta = nasa.fetch_scene_asset(
                        scene_idx=s_idx,
                        keywords=kws,
                        preferred_type="video",
                        orientation=orientation,
                        topic_anchor=topic
                    )
                elif sub_choice == "4" and pollinations:
                    prompt_input = input("Prompt fotográfico para FLUX (en inglés): ").strip()
                    if prompt_input:
                        new_file, new_meta = pollinations.fetch_scene_asset(
                            scene_idx=s_idx,
                            prompt=prompt_input,
                            orientation=orientation,
                            topic=topic
                        )
                elif sub_choice == "5":
                    path_input = input("Ruta absoluta o relativa del archivo (.mp4, .mov, .jpg, .png): ").strip()
                    loc_p = Path(path_input).expanduser().resolve()
                    if loc_p.exists() and loc_p.is_file():
                        ext = loc_p.suffix.lower()
                        dest_file = ASSETS_DIR / f"scene_{s_idx:02d}{ext}"
                        shutil.copy2(loc_p, dest_file)
                        is_vid = ext in [".mp4", ".mov", ".mkv", ".webm"]
                        new_file = dest_file
                        new_meta = {
                            "scene_index": s_idx,
                            "provider": "local",
                            "title": loc_p.name,
                            "media_type": "video" if is_vid else "image",
                            "attribution_text": "Material del usuario"
                        }
                    else:
                        print(f"⚠️ El archivo '{path_input}' no existe.")

                if new_file and new_meta:
                    asset_item["file"] = new_file
                    asset_item["is_video"] = (new_meta.get("media_type") == "video")
                    assets_metadata[s_idx - 1] = new_meta
                    print(f"✅ Escena {s_idx:02d} actualizada con: {new_file.name}")

                    # Refresh HTML
                    generate_audit_html(
                        script=script,
                        scene_assets=scene_assets,
                        assets_metadata=assets_metadata,
                        scene_timings=scene_timings,
                        topic=topic,
                        output_html_path=html_report_path
                    )
                else:
                    if sub_choice not in ("0", ""):
                        print("⚠️ No se pudo asignar el nuevo asset o no se encontró coincidencia.")

            except Exception as e:
                print(f"⚠️ Error al cambiar asset: {e}")

        elif choice == "4":
            print(f"\n🌐 Abriendo storyboard en el navegador: {html_report_path.resolve()}")
            try:
                webbrowser.open(html_report_path.as_uri())
            except Exception:
                print(f"👉 Puedes abrir este archivo localmente: {html_report_path.resolve()}")

        elif choice == "6":
            print("\n🛑 Proceso finalizado sin renderizar. Tus recursos y guion están guardados.")
            return False, script, scene_assets, assets_metadata, scene_timings

        else:
            print("⚠️ Opción no válida. Ingresa un número del 1 al 6.")
