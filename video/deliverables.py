"""
Video Deliverables & Output Packaging.
Organizes output files (video, script, subtitles, audio, metadata) in a clean dedicated folder.
"""

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config import OUTPUT_DIR
from utils.files import sanitize_filename, save_json


def resolve_video_output_folder(custom_output: Optional[str], topic: str) -> Tuple[Path, str]:
    """
    Resolves the target folder and filename for the final video deliverables.
    Returns:
        (video_folder, output_filename)
    """
    if custom_output:
        out_candidate = Path(custom_output)
        if len(out_candidate.parts) > 1:
            if out_candidate.suffix.lower() == ".mp4":
                video_name = sanitize_filename(out_candidate.stem)
                video_folder = out_candidate.parent / video_name
            else:
                video_name = sanitize_filename(out_candidate.name)
                video_folder = out_candidate
        else:
            video_name = sanitize_filename(out_candidate.stem)
            video_folder = OUTPUT_DIR / video_name
    else:
        video_name = sanitize_filename(topic)
        video_folder = OUTPUT_DIR / video_name

    video_name = video_name or "short_video"
    video_folder.mkdir(parents=True, exist_ok=True)
    output_filename = f"{video_name}.mp4"

    return video_folder, output_filename


def package_deliverables(
    video_folder: Path,
    script: Dict[str, Any],
    srt_path: Optional[str],
    ass_path: Optional[str],
    narration_audio: Optional[Path],
    sfx_track: Optional[Path],
    trending_metadata: Optional[Dict[str, Any]] = None,
    scene_assets: Optional[List[Dict[str, Any]]] = None,
    scene_timings: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Path]:
    """
    Copies and organizes all intermediate assets (script, audio, subs, metadata)
    into the video's dedicated directory.
    """
    deliverables = {}

    # 1. Full AI script
    script_dest = video_folder / "script.json"
    save_json(script, script_dest)
    deliverables["script"] = script_dest

    # 2. Synchronized Subtitles (.srt and .ass)
    srt_dest = video_folder / "subtitles.srt"
    if srt_path and Path(srt_path).exists():
        shutil.copy2(srt_path, srt_dest)
        deliverables["srt"] = srt_dest

    ass_dest = video_folder / "subtitles.ass"
    if ass_path and Path(ass_path).exists():
        shutil.copy2(ass_path, ass_dest)
        deliverables["ass"] = ass_dest

    # 3. Narration audio track (.mp3)
    audio_dest = video_folder / "narration.mp3"
    if narration_audio and Path(narration_audio).exists():
        shutil.copy2(narration_audio, audio_dest)
        deliverables["audio"] = audio_dest

    # 4. Sound effects track (.wav)
    sfx_dest = video_folder / "sfx.wav"
    if sfx_track and Path(sfx_track).exists():
        shutil.copy2(sfx_track, sfx_dest)
        deliverables["sfx"] = sfx_dest

    # 5. NASA Discovery metadata if generated from trending
    if trending_metadata:
        nasa_dest = video_folder / "nasa_discovery.json"
        save_json(trending_metadata, nasa_dest)
        deliverables["nasa_discovery"] = nasa_dest

    # 6. Interactive Visual Storyboard / Audit HTML
    storyboard_file = video_folder / "storyboard_audit.html"
    if storyboard_file.exists():
        deliverables["storyboard"] = storyboard_file

    # 7. Scene Media Assets (videos, images, audio clips)
    if scene_assets:
        assets_dest_dir = video_folder / "assets"
        assets_dest_dir.mkdir(parents=True, exist_ok=True)
        for item in scene_assets:
            src_file = item.get("file")
            if src_file and Path(src_file).exists():
                dest_file = assets_dest_dir / Path(src_file).name
                if dest_file.resolve() != Path(src_file).resolve():
                    shutil.copy2(src_file, dest_file)
        if scene_timings:
            for timing in scene_timings:
                af = timing.get("audio_file")
                if af and Path(af).exists():
                    dest_audio = assets_dest_dir / Path(af).name
                    if dest_audio.resolve() != Path(af).resolve():
                        shutil.copy2(af, dest_audio)
        deliverables["scene_assets"] = assets_dest_dir

    return deliverables


def print_completion_summary(
    video_folder: Path,
    final_video: Path,
    deliverables: Dict[str, Path],
    total_duration: float,
    elapsed_seconds: float
) -> None:
    """Prints a clear summary of all created deliverables."""
    print("\n" + "=" * 65)
    print("🎉 VIDEO CREATION COMPLETED SUCCESSFULLY!")
    print(f"📁 Carpeta del Video:     {video_folder.resolve()}")
    print(f"🎥 Video Final:           {final_video.resolve()}")
    if "storyboard" in deliverables:
        print(f"🌐 Storyboard (.html):    {deliverables['storyboard'].resolve()}")
    if "script" in deliverables:
        print(f"📜 Guión (.json):         {deliverables['script'].resolve()}")
    if "srt" in deliverables:
        print(f"📝 Subtítulos (.srt):     {deliverables['srt'].resolve()}")
    if "audio" in deliverables:
        print(f"🎵 Narración (.mp3):      {deliverables['audio'].resolve()}")
    if "sfx" in deliverables:
        print(f"🔊 Efectos Sonido (.wav): {deliverables['sfx'].resolve()}")
    meta_dest = video_folder / "metadata.json"
    if meta_dest.exists():
        print(f"📊 Metadatos (.json):     {meta_dest.resolve()}")
    print(f"⏱️  Duración Total:        {total_duration:.1f}s")
    print(f"⚡ Tiempo de Proceso:      {elapsed_seconds:.1f}s")
    print("=" * 65)
