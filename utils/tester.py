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

    total_shots = 0
    num_video_shots = 0
    num_image_shots = 0
    num_broll_splits = 0

    for item in scene_assets:
        s_dur = item.get("duration", 0.0)
        has_split = bool(item.get("secondary_file") or s_dur > 3.5)
        if item.get("is_video"):
            num_video_shots += 1
        else:
            num_image_shots += 1

        if has_split:
            total_shots += 2
            num_broll_splits += 1
            if item.get("secondary_file"):
                if item.get("secondary_is_video"):
                    num_video_shots += 1
                else:
                    num_image_shots += 1
            else:
                # 1.35x focal angle cut of primary
                if item.get("is_video"):
                    num_video_shots += 1
                else:
                    num_image_shots += 1
        else:
            total_shots += 1

    motion_ratio = (num_video_shots / total_shots * 100) if total_shots else 0

    # Calculate relative paths from HTML location
    html_dir = output_html_path.parent.resolve()
    assets_local_dir = html_dir / "assets"

    def get_rel_url(file_path: Optional[Path]) -> str:
        if not file_path:
            return ""
        p = Path(file_path).resolve()
        # If the file also exists in video_folder/assets, prioritize that relative path and sync if needed
        if assets_local_dir.exists():
            candidate = assets_local_dir / p.name
            if candidate.exists() and candidate.resolve() != p:
                try:
                    if p.exists() and p.stat().st_mtime >= candidate.stat().st_mtime:
                        shutil.copy2(p, candidate)
                except Exception:
                    pass
            elif p.exists() and not candidate.exists():
                try:
                    shutil.copy2(p, candidate)
                except Exception:
                    pass
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
        sec_file = asset_item.get("secondary_file")
        sec_is_video = asset_item.get("secondary_is_video", False)
        sec_meta = asset_item.get("secondary_meta") or {}
        has_split = bool(sec_file or s_duration > 3.5)

        start_time = float(timing.get("start", 0.0))
        end_time = float(timing.get("end", start_time + s_duration))

        if has_split:
            d1 = round(s_duration / 2.0, 2)
            d2 = round(s_duration - d1, 2)
            t1_end = start_time + d1
            t2_start = t1_end
        else:
            d1 = s_duration
            d2 = 0.0
            t1_end = end_time
            t2_start = start_time

        rel_media_url = get_rel_url(asset_file) if asset_file else ""
        rel_broll_url = get_rel_url(sec_file) if sec_file else ""
        audio_file = timing.get("audio_file")
        rel_audio_url = get_rel_url(audio_file) if audio_file else ""

        narration = scene.get("narration", "").strip()
        word_count = _count_words(narration)
        word_status_class = "badge-ok" if word_count <= 16 else "badge-warn"
        word_status_text = f"{word_count} palabras" + (" (óptimo)" if word_count <= 16 else " (denso >16)")

        provider_name = (meta.get("provider") or ("NASA" if "nasa" in str(asset_file).lower() else "STOCK")).upper()
        subject = scene.get("visual_subject") or meta.get("title") or f"Escena {s_idx}"

        raw_kws = (
            scene.get("keywords")
            or scene.get("nasa_keywords")
            or scene.get("pexels_keywords")
            or scene.get("stock_keywords")
            or []
        )
        if isinstance(raw_kws, str):
            kws = [k.strip() for k in raw_kws.split(",") if k.strip()]
        elif isinstance(raw_kws, list):
            kws = [str(k).strip() for k in raw_kws if str(k).strip()]
        else:
            kws = []
        image_prompt = scene.get("image_prompt", "")

        punch_badge = '<span class="badge" style="background:#e11d48;color:#fff;">💥 PUNCH-IN (0.4s)</span>' if s_idx == 1 else ''
        if has_split:
            if sec_file:
                broll_badge = '<span class="badge" style="background:#0d9488;color:#fff;">🎬 2 TOMAS (B-ROLL SPLIT 2.5s)</span>'
            else:
                broll_badge = '<span class="badge" style="background:#d97706;color:#fff;">🔍 2 TOMAS (CORTE FOCAL 2.5s)</span>'
        else:
            broll_badge = '<span class="badge" style="background:#4b5563;color:#fff;">🎬 TOMA ÚNICA</span>'

        # --- Shot 1 HTML (Principal) ---
        if asset_file and asset_file.exists():
            if is_video:
                media_shot1 = f"""
                <div class="media-container">
                    <video src="{rel_media_url}" controls muted loop playsinline preload="metadata"></video>
                    <div class="media-overlay-badge">{provider_name}</div>
                </div>
                """
            else:
                media_shot1 = f"""
                <div class="media-container">
                    <img src="{rel_media_url}" alt="{subject}" loading="lazy" />
                    <div class="media-overlay-badge">{provider_name}</div>
                </div>
                """
        else:
            media_shot1 = """
            <div class="media-placeholder">
                <p>⚠️ Sin archivo asignado</p>
            </div>
            """

        shot1_html = f"""
        <div class="shot-card">
            <div class="shot-header">
                <span class="shot-tag">TOMA 1: PRINCIPAL ({start_time:.1f}s - {t1_end:.1f}s)</span>
                <span class="badge {'badge-video' if is_video else 'badge-image'}">{'🎬 VIDEO' if is_video else '📷 FOTO'}</span>
            </div>
            {media_shot1}
            <div class="shot-footer">
                <code>{asset_file.name if asset_file else "None"}</code>
            </div>
        </div>
        """

        # --- Shot 2 HTML (B-Roll o Reencuadre Focal) ---
        if has_split:
            if sec_file:
                broll_p_name = (sec_meta.get("provider") or ("NASA" if "nasa" in str(sec_file).lower() else "B-ROLL")).upper()
                if sec_file.exists():
                    if sec_is_video:
                        media_shot2 = f"""
                        <div class="media-container">
                            <video src="{rel_broll_url}" controls muted loop playsinline preload="metadata"></video>
                            <div class="media-overlay-badge">{broll_p_name}</div>
                        </div>
                        """
                    else:
                        media_shot2 = f"""
                        <div class="media-container">
                            <img src="{rel_broll_url}" alt="{subject} B-Roll" loading="lazy" />
                            <div class="media-overlay-badge">{broll_p_name}</div>
                        </div>
                        """
                else:
                    media_shot2 = """
                    <div class="media-placeholder">
                        <p>⚠️ Archivo B-Roll no encontrado</p>
                    </div>
                    """
                shot2_html = f"""
                <div class="shot-card shot-broll-active">
                    <div class="shot-header">
                        <span class="shot-tag" style="color:#2dd4bf;">TOMA 2: B-ROLL ({t2_start:.1f}s - {end_time:.1f}s)</span>
                        <span class="badge {'badge-video' if sec_is_video else 'badge-image'}">{'🎬 VIDEO' if sec_is_video else '📷 FOTO'}</span>
                    </div>
                    {media_shot2}
                    <div class="shot-footer">
                        <code>{sec_file.name}</code>
                    </div>
                </div>
                """
            else:
                shot2_html = f"""
                <div class="shot-card shot-focal-cut">
                    <div class="shot-header">
                        <span class="shot-tag" style="color:#fbbf24;">TOMA 2: CORTE FOCAL ({t2_start:.1f}s - {end_time:.1f}s)</span>
                        <span class="badge" style="background:#b45309;color:#fff;">🔍 ZOOM 1.35x</span>
                    </div>
                    <div class="focal-cut-preview">
                        <div class="focal-cut-inner">
                            <span class="focal-icon">🔍</span>
                            <strong>Reencuadre Dinámico (Close-Up)</strong>
                            <p>Corte automático a los 2.5s sobre la toma principal para dinamizar el corte.</p>
                            <span class="focal-tip">💡 Puedes asignarle un video/imagen B-Roll independiente en la consola (Opción 3).</span>
                        </div>
                    </div>
                    <div class="shot-footer">
                        <span>Ángulo alternativo automático</span>
                    </div>
                </div>
                """
            shots_block = f"""
            <div class="shots-grid">
                {shot1_html}
                {shot2_html}
            </div>
            """
        else:
            shots_block = f"""
            <div class="shots-grid single-shot">
                {shot1_html}
            </div>
            """

        card = f"""
        <div class="scene-card" id="scene-card-{s_idx}">
            <div class="scene-header">
                <div class="scene-title-group">
                    <span class="scene-number">#{s_idx:02d}</span>
                    <span class="scene-subject">{subject}</span>
                </div>
                <div class="scene-badges">
                    {punch_badge}
                    {broll_badge}
                    <span class="badge badge-provider">{provider_name}</span>
                    <span class="badge badge-time">⏱️ {s_duration:.1f}s ({start_time:.1f}s - {end_time:.1f}s)</span>
                    <span class="badge {word_status_class}">{word_status_text}</span>
                </div>
            </div>

            <div class="scene-body">
                <div class="scene-media-col">
                    {shots_block}
                    {f'<audio controls src="{rel_audio_url}" class="scene-audio-player"></audio>' if rel_audio_url else ''}
                </div>

                <div class="scene-info-col">
                    <div class="info-block">
                        <label>🗣️ GUION / NARRACIÓN NATIVA:</label>
                        <div class="narration-box">"{narration}"</div>
                    </div>

                    <div class="info-block meta-details">
                        <label>🔍 METADATOS Y TOMAS:</label>
                        <ul class="meta-list">
                            <li><strong>Toma 1:</strong> <code>{asset_file.name if asset_file else "None"}</code> ({meta.get("attribution_text", "Dominio Público")})</li>
                            {f'<li><strong>Toma 2 (B-Roll):</strong> <code>{sec_file.name}</code> ({sec_meta.get("attribution_text", "B-Roll complementario")})</li>' if (has_split and sec_file) else ''}
                            {f'<li><strong>Toma 2 (Corte Focal):</strong> <em>Reencuadre 1.35x automático sobre toma 1</em></li>' if (has_split and not sec_file) else ''}
                            {f'<li><strong>Palabras clave:</strong> <code>{", ".join(kws)}</code></li>' if kws else ''}
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
            grid-template-columns: minmax(360px, 1.35fr) 1fr;
            gap: 20px;
            padding: 20px;
        }}
        @media (max-width: 980px) {{
            .scene-body {{ grid-template-columns: 1fr; }}
        }}
        .scene-media-col {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .shots-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }}
        .shots-grid.single-shot {{
            grid-template-columns: 1fr;
        }}
        @media (max-width: 600px) {{
            .shots-grid {{ grid-template-columns: 1fr; }}
        }}
        .shot-card {{
            background: #11161d;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 8px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .shot-card.shot-broll-active {{
            border-color: #0d9488;
            box-shadow: 0 0 10px rgba(13, 148, 136, 0.15);
        }}
        .shot-card.shot-focal-cut {{
            border-color: #d29922;
        }}
        .shot-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.74rem;
            font-weight: 700;
        }}
        .shot-tag {{
            letter-spacing: 0.4px;
        }}
        .shot-footer {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.72rem;
            color: var(--text-muted);
            padding-top: 4px;
            border-top: 1px solid rgba(255,255,255,0.05);
        }}
        .shot-footer code {{
            background: #21262d;
            padding: 2px 6px;
            border-radius: 4px;
            color: #79c0ff;
            word-break: break-all;
            max-width: 100%;
        }}
        .focal-cut-preview {{
            min-height: 180px;
            background: linear-gradient(135deg, #1c2128 0%, #0d1117 100%);
            border: 1px dashed var(--accent-amber);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .focal-cut-inner {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            color: #c9d1d9;
        }}
        .focal-icon {{
            font-size: 2rem;
        }}
        .focal-cut-inner strong {{
            color: #fbbf24;
            font-size: 0.88rem;
        }}
        .focal-cut-inner p {{
            font-size: 0.75rem;
            color: var(--text-muted);
            max-width: 200px;
            line-height: 1.35;
        }}
        .focal-tip {{
            font-size: 0.68rem;
            color: #58a6ff;
            margin-top: 4px;
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
                <div class="stat-item">⏱️ Duración: <strong>{total_duration:.1f}s</strong></div>
                <div class="stat-item">📋 Escenas: <strong>{len(scenes)}</strong></div>
                <div class="stat-item">🎬 Tomas Totales: <strong>{total_shots}</strong> (<strong>{num_broll_splits}</strong> B-Roll Splits)</div>
                <div class="stat-item">🎥 Videos en movimiento: <strong style="color: {'var(--accent-green)' if motion_ratio >= 60 else 'var(--accent-amber)'};">{num_video_shots}/{total_shots} ({motion_ratio:.0f}%)</strong></div>
                <div class="stat-item">📷 Tomas fijas: <strong>{num_image_shots}</strong></div>
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
    """Print an aesthetic, structured audit table in the terminal with B-roll shot visibility."""
    total_duration = sum(item.get("duration", 0.0) for item in scene_assets)

    total_shots = 0
    num_video_shots = 0
    num_image_shots = 0
    num_broll_splits = 0

    for item in scene_assets:
        s_dur = item.get("duration", 0.0)
        has_split = bool(item.get("secondary_file") or s_dur > 3.5)
        if item.get("is_video"):
            num_video_shots += 1
        else:
            num_image_shots += 1

        if has_split:
            total_shots += 2
            num_broll_splits += 1
            if item.get("secondary_file"):
                if item.get("secondary_is_video"):
                    num_video_shots += 1
                else:
                    num_image_shots += 1
            else:
                if item.get("is_video"):
                    num_video_shots += 1
                else:
                    num_image_shots += 1
        else:
            total_shots += 1

    motion_ratio = (num_video_shots / total_shots * 100) if total_shots else 0

    print("\n" + "═" * 74)
    print("🔍  PANEL DE AUDITORÍA & STORYBOARD TESTING (PRE-RENDER)")
    print("═" * 74)
    print(f"🎯 Tema:       '{topic}'")
    print(f"📋 Título:     \"{script.get('title', topic)}\"")
    if script.get("hook"):
        print(f"🪝 Hook:       \"{script.get('hook')}\"")
    print(f"⏱️  Duración:   ~{total_duration:.1f} segundos ({len(scene_assets)} escenas)")
    print(f"🎬 Tomas:      {total_shots} tomas totales ({len(scene_assets)} principales + {num_broll_splits} B-Roll splits)")
    print(f"🎥 Dinamismo:  {num_video_shots} videos / {num_image_shots} fotos ({motion_ratio:.0f}% tomas en movimiento)")
    print("─" * 74)

    warnings = []

    for i, (timing, asset_item, meta) in enumerate(zip(scene_timings, scene_assets, assets_metadata), start=1):
        s_idx = asset_item.get("scene_idx", i)
        s_duration = asset_item.get("duration", timing.get("duration", 0.0))
        is_video = asset_item.get("is_video", False)
        asset_file = asset_item.get("file")
        sec_file = asset_item.get("secondary_file")
        sec_is_video = asset_item.get("secondary_is_video", False)
        sec_meta = asset_item.get("secondary_meta") or {}
        has_split = bool(sec_file or s_duration > 3.5)

        narration = timing.get("narration", "").strip()
        word_count = _count_words(narration)

        if has_split:
            d1 = round(s_duration / 2.0, 2)
            d2 = round(s_duration - d1, 2)
        else:
            d1 = s_duration
            d2 = 0.0

        p1_name = (meta.get("provider") or ("NASA" if "nasa" in str(asset_file).lower() else "STOCK")).upper()
        f1_name = asset_file.name if asset_file else "SIN ARCHIVO"
        m1_icon = "🎬 VIDEO " if is_video else "📷 IMAGEN"

        if not is_video:
            warnings.append(f"Escena {s_idx:02d} (Toma 1): Imagen fija. Puedes reemplazarla por video.")
        if word_count > 16:
            warnings.append(f"Escena {s_idx:02d}: Guion extenso ({word_count} palabras). Puede sonar acelerado.")

        if has_split:
            print(f"[{s_idx:02d}.1] {m1_icon} ({p1_name:<6}) | ⏱️ {d1:4.1f}s | Toma 1: Principal 📁 {f1_name}")
            if sec_file:
                p2_name = (sec_meta.get("provider") or ("NASA" if "nasa" in str(sec_file).lower() else "B-ROLL")).upper()
                m2_icon = "🎬 VIDEO " if sec_is_video else "📷 IMAGEN"
                print(f"[{s_idx:02d}.2] {m2_icon} ({p2_name:<6}) | ⏱️ {d2:4.1f}s | Toma 2: B-Roll    📁 {sec_file.name}")
            else:
                print(f"[{s_idx:02d}.2] 🔍 CORTE FOCAL   | ⏱️ {d2:4.1f}s | Toma 2: Reencuadre dinámico 1.35x (Close-Up)")
        else:
            print(f"[{s_idx:02d}]   {m1_icon} ({p1_name:<6}) | ⏱️ {s_duration:4.1f}s | Toma Única        📁 {f1_name}")

        print(f"     🗣️ \"{narration[:68]}{'...' if len(narration) > 68 else ''}\"")

    print("─" * 74)
    if warnings:
        print("⚠️  AVISOS DE AUDITORÍA DETECTADOS:")
        for w in warnings:
            print(f"   • {w}")
    else:
        print("✨ ¡Todo en orden! Guion conciso y óptimo ritmo visual con B-Roll splits.")
    print("═" * 74 + "\n")


def interactive_audit_menu(
    script: Dict[str, Any],
    scene_assets: List[Dict[str, Any]],
    assets_metadata: List[Dict[str, Any]],
    scene_timings: List[Dict[str, Any]],
    topic: str,
    tts_mgr: Any,
    providers_dict: Dict[str, Any],
    orientation: str = "portrait",
    html_report_path: Optional[Path] = None,
    narration_audio: Optional[Path] = None,
    video_folder: Optional[Path] = None
) -> Tuple[bool, Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Optional[Path]]:
    """
    Interactive CLI loop allowing user to review and tweak script/assets before rendering.
    Returns:
        (proceed_to_render: bool, script, scene_assets, assets_metadata, scene_timings, narration_audio)
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
        output_html_path=html_report_path,
        narration_audio_path=narration_audio
    )

    print_audit_console_summary(script, scene_assets, assets_metadata, scene_timings, topic)
    print(f"🌐 Storyboard visual generado en: {html_report_path.resolve()}\n")

    # Detect completely closed stdin (e.g. background job without piped input)
    is_interactive = sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else False
    if not is_interactive and (not hasattr(sys.stdin, "readable") or not sys.stdin.readable()):
        print("⚠️  Entorno sin entrada estándar interactiva detectado.")
        print("   Se generó el storyboard HTML y los recursos fueron preservados en la carpeta del video.")
        print("   Aprobando automáticamente para proceder al renderizado...")
        return True, script, scene_assets, assets_metadata, scene_timings, narration_audio

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
        except EOFError:
            print("\n⚠️ Fin de archivo (EOF) detectado en la entrada. Aprobando automáticamente...")
            return True, script, scene_assets, assets_metadata, scene_timings, narration_audio
        except KeyboardInterrupt:
            print("\n🛑 Cancelado por el usuario.")
            return False, script, scene_assets, assets_metadata, scene_timings, narration_audio

        if choice in ("", "5"):
            print("\n🚀 ¡Aprobado! Iniciando renderizado de video final...")
            return True, script, scene_assets, assets_metadata, scene_timings, narration_audio

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
                    print(f"\n🎙️ Re-sintetizando audio para la escena {s_idx:02d} y concatenando narración...")
                    new_full_audio, new_timings, _ = tts_mgr.synthesize_script(script)
                    narration_audio = new_full_audio
                    scene_timings = new_timings
                    # Update duration in scene_assets
                    for item, timing in zip(scene_assets, scene_timings):
                        item["duration"] = timing["duration"]

                    # Sync updated audio files directly into video_folder/assets
                    if video_folder:
                        out_assets_dir = Path(video_folder) / "assets"
                        out_assets_dir.mkdir(parents=True, exist_ok=True)
                        for timing in scene_timings:
                            af = timing.get("audio_file")
                            if af and Path(af).exists():
                                dst_a = out_assets_dir / Path(af).name
                                shutil.copy2(af, dst_a)
                        if narration_audio and Path(narration_audio).exists():
                            dst_narr = out_assets_dir / Path(narration_audio).name
                            shutil.copy2(narration_audio, dst_narr)

                    # Refresh HTML
                    generate_audit_html(
                        script=script,
                        scene_assets=scene_assets,
                        assets_metadata=assets_metadata,
                        scene_timings=scene_timings,
                        topic=topic,
                        output_html_path=html_report_path,
                        narration_audio_path=narration_audio
                    )
                    print("✅ Narración, audios y duraciones actualizadas con éxito.")
            except Exception as e:
                print(f"⚠️ Error al editar narración: {e}")

        elif choice == "3":
            # Change / re-search asset (Toma 1 o Toma 2 B-Roll)
            try:
                raw_idx = input(f"¿De qué escena deseas cambiar el visual? (1 a {len(scene_assets)}): ").strip()
                if not raw_idx.isdigit() or not (1 <= int(raw_idx) <= len(scene_assets)):
                    print("⚠️ Número de escena inválido.")
                    continue
                s_idx = int(raw_idx)
                asset_item = scene_assets[s_idx - 1]
                meta_item = assets_metadata[s_idx - 1]
                scene_ref = script["scenes"][s_idx - 1]
                s_duration = asset_item.get("duration", 0.0)
                sec_file = asset_item.get("secondary_file")
                has_split = bool(sec_file or s_duration > 3.5)

                f1_desc = asset_item.get("file").name if asset_item.get("file") else "Sin archivo"
                if sec_file:
                    f2_desc = f"{sec_file.name} (B-Roll complementario)"
                elif has_split:
                    f2_desc = "Ninguno (usando Corte Focal 1.35x dinámico)"
                else:
                    f2_desc = "No aplica (escena corta <= 3.5s)"

                print(f"\nVisuales actuales de la Escena {s_idx:02d}:")
                print(f"  [1] Toma 1 (Principal): {f1_desc}")
                print(f"  [2] Toma 2 (B-Roll):    {f2_desc}")
                print("  [3] Ambas tomas")
                print("  [0] Cancelar")

                shot_target = input("👉 ¿Qué toma deseas editar? [1-3] (0 para cancelar): ").strip()
                if shot_target not in ("1", "2", "3"):
                    continue

                def _edit_target_shot(target: str) -> bool:
                    is_broll = (target == "secondary")
                    label = "Toma 2 (B-Roll)" if is_broll else "Toma 1 (Principal)"
                    cur_f = asset_item.get("secondary_file") if is_broll else asset_item.get("file")
                    suffix = "_broll" if is_broll else ""

                    print(f"\n--- Editando {label} de la Escena {s_idx:02d} ---")
                    print(f"Archivo actual: {cur_f.name if cur_f else 'Ninguno'}")
                    print("  [1] Re-buscar en Pexels (Videos en movimiento)")
                    print("  [2] Re-buscar en Pixabay (Simulaciones 3D / Espacio)")
                    print("  [3] Re-buscar en NASA (Observaciones científicas)")
                    print("  [4] Generar con IA Pollinations (FLUX)")
                    print("  [5] Asignar archivo local propio (video o imagen)")
                    if is_broll:
                        print("  [6] Quitar B-Roll (usar Corte Focal dinámico 1.35x)")
                    print("  [0] Cancelar")

                    sub_choice = input("👉 Elige opción: ").strip()

                    new_file = None
                    new_meta = None

                    if sub_choice == "1" and pexels and pexels.is_configured():
                        default_kw = f"{scene_ref.get('visual_subject', topic)} detail" if is_broll else scene_ref.get("visual_subject", topic)
                        kw_input = input(f"Keywords para Pexels (Enter para '{default_kw}'): ").strip()
                        kw_str = kw_input if kw_input else default_kw
                        kws = [k.strip() for k in kw_str.split(",") if k.strip()]
                        new_file, new_meta = pexels.fetch_scene_asset(
                            scene_idx=s_idx,
                            keywords=kws,
                            preferred_type="video",
                            orientation=orientation,
                            filename_suffix=suffix
                        )
                    elif sub_choice == "2" and pixabay and pixabay.is_configured():
                        default_kw = f"{scene_ref.get('visual_subject', topic)} detail" if is_broll else scene_ref.get("visual_subject", topic)
                        kw_input = input(f"Keywords para Pixabay (Enter para '{default_kw}'): ").strip()
                        kw_str = kw_input if kw_input else default_kw
                        kws = [k.strip() for k in kw_str.split(",") if k.strip()]
                        new_file, new_meta = pixabay.fetch_scene_asset(
                            scene_idx=s_idx,
                            keywords=kws,
                            preferred_type="video",
                            orientation=orientation,
                            filename_suffix=suffix
                        )
                    elif sub_choice == "3" and nasa:
                        default_kw = f"{scene_ref.get('visual_subject', topic)} close up" if is_broll else scene_ref.get("visual_subject", topic)
                        kw_input = input(f"Keywords para NASA (Enter para '{default_kw}'): ").strip()
                        kw_str = kw_input if kw_input else default_kw
                        kws = [k.strip() for k in kw_str.split(",") if k.strip()]
                        new_file, new_meta = nasa.fetch_scene_asset(
                            scene_idx=s_idx,
                            keywords=kws,
                            preferred_type="video",
                            orientation=orientation,
                            topic_anchor=topic,
                            filename_suffix=suffix
                        )
                    elif sub_choice == "4" and pollinations:
                        base_p = scene_ref.get("image_prompt") or f"{topic}, {scene_ref.get('visual_subject', '')}"
                        default_prompt = f"{base_p} cinematic close up detail, alternate camera angle" if is_broll else base_p
                        prompt_input = input(f"Prompt para FLUX (Enter para '{default_prompt[:60]}...'): ").strip()
                        p_str = prompt_input if prompt_input else default_prompt
                        new_file, new_meta = pollinations.fetch_scene_asset(
                            scene_idx=s_idx,
                            prompt=p_str,
                            orientation=orientation,
                            topic=topic,
                            filename_suffix=suffix
                        )
                    elif sub_choice == "5":
                        path_input = input("Ruta absoluta o relativa del archivo (.mp4, .mov, .jpg, .png): ").strip()
                        loc_p = Path(path_input).expanduser().resolve()
                        if loc_p.exists() and loc_p.is_file():
                            ext = loc_p.suffix.lower()
                            dest_file = ASSETS_DIR / f"scene_{s_idx:02d}{suffix}{ext}"
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
                    elif is_broll and sub_choice == "6":
                        asset_item["secondary_file"] = None
                        asset_item["secondary_is_video"] = False
                        asset_item["secondary_meta"] = None
                        print(f"✅ B-Roll removido de la Escena {s_idx:02d}. Se usará Corte Focal dinámico 1.35x.")
                        return True

                    if new_file and new_meta:
                        if is_broll:
                            asset_item["secondary_file"] = new_file
                            asset_item["secondary_is_video"] = (new_meta.get("media_type") == "video")
                            asset_item["secondary_meta"] = new_meta
                            print(f"✅ B-Roll de la Escena {s_idx:02d} actualizado con: {new_file.name}")
                        else:
                            asset_item["file"] = new_file
                            asset_item["is_video"] = (new_meta.get("media_type") == "video")
                            assets_metadata[s_idx - 1] = new_meta
                            print(f"✅ Toma Principal de la Escena {s_idx:02d} actualizada con: {new_file.name}")

                        # Sync newly fetched asset directly into video_folder/assets
                        if video_folder:
                            out_assets_dir = Path(video_folder) / "assets"
                            out_assets_dir.mkdir(parents=True, exist_ok=True)
                            dst_f = out_assets_dir / Path(new_file).name
                            shutil.copy2(new_file, dst_f)
                        return True
                    else:
                        if sub_choice not in ("0", ""):
                            print("⚠️ No se pudo asignar el nuevo asset o no se encontró coincidencia.")
                        return False

                modified = False
                if shot_target == "1":
                    modified = _edit_target_shot("primary")
                elif shot_target == "2":
                    modified = _edit_target_shot("secondary")
                elif shot_target == "3":
                    m1 = _edit_target_shot("primary")
                    m2 = _edit_target_shot("secondary")
                    modified = m1 or m2

                if modified:
                    generate_audit_html(
                        script=script,
                        scene_assets=scene_assets,
                        assets_metadata=assets_metadata,
                        scene_timings=scene_timings,
                        topic=topic,
                        output_html_path=html_report_path,
                        narration_audio_path=narration_audio
                    )
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
            return False, script, scene_assets, assets_metadata, scene_timings, narration_audio

        else:
            print("⚠️ Opción no válida. Ingresa un número del 1 al 6.")
