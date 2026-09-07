"""
Background Music Manager.
Handles background ambient/documentary music mixing with audio ducking and loop trimming.
Does NOT download unverified music from the internet.
"""

import subprocess
from pathlib import Path
from typing import Optional

from config import MUSIC_DIR, TEMP_DIR, MUSIC_VOLUME
from utils.files import get_media_duration


class MusicManager:
    """Manages background audio tracks for science documentary shorts."""

    def __init__(self, default_music_dir: Path = MUSIC_DIR):
        self.music_dir = Path(default_music_dir)

    def get_background_track(self, custom_path: Optional[str] = None) -> Optional[Path]:
        """Check for user-provided background music."""
        if custom_path:
            p = Path(custom_path)
            if p.exists() and p.is_file():
                return p

        # Check default asset music location
        default_file = self.music_dir / "background.mp3"
        if default_file.exists() and default_file.stat().st_size > 0:
            return default_file

        # Check for any .mp3 or .wav in music dir
        if self.music_dir.exists():
            for f in self.music_dir.glob("*.mp3"):
                if f.stat().st_size > 0:
                    return f

        return None

    def prepare_music(
        self,
        music_path: Optional[Path],
        target_duration: float,
        volume: float = MUSIC_VOLUME,
        output_dir: Path = TEMP_DIR
    ) -> Optional[Path]:
        """
        Adjust volume, loop if shorter than video, and apply fade-in / fade-out.
        Returns path to processed music file or None.
        """
        if not music_path or not music_path.exists():
            print("  ℹ️ No background music file found in assets/music/ — proceeding with voice narration only.")
            return None

        output_file = output_dir / "prepared_music.mp3"
        fade_out_start = max(0.0, target_duration - 2.0)

        # Loop and trim to match target duration with low background volume
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", str(music_path),
            "-t", str(target_duration),
            "-filter_complex",
            f"volume={volume},afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out_start:.2f}:d=2.0",
            "-acodec", "libmp3lame",
            "-b:a", "192k",
            str(output_file)
        ]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if output_file.exists() and output_file.stat().st_size > 0:
                print(f"  🎶 Background music mixed: {music_path.name} (volume: {int(volume*100)}%)")
                return output_file
        except Exception as e:
            print(f"  ⚠️ Could not prepare background music ({e}), proceeding without it.")

        return None
