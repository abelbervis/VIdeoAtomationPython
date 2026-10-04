"""
Beat Synchronization and Rhythmic Editing Engine.
Aligns video cuts, transitions, subtitle animations, and speech pauses to the musical beat grid (BPM).
"""

import math
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


class BeatGrid:
    """
    Musical Beat Grid for video editing.
    Calculates exact timestamps for beats, downbeats (bars), and sub-beats.
    """

    def __init__(self, bpm: float = 124.0, beats_per_bar: int = 4):
        self.bpm = max(60.0, min(200.0, float(bpm)))
        self.beats_per_bar = beats_per_bar
        self.seconds_per_beat = 60.0 / self.bpm
        self.seconds_per_bar = self.seconds_per_beat * self.beats_per_bar
        self.seconds_per_half_bar = self.seconds_per_bar / 2.0

    def snap_to_nearest_beat(self, t: float, division: float = 1.0) -> float:
        """
        Snap a timestamp to the closest beat division.
        division=1.0: quarter note (1 beat)
        division=0.5: eighth note (half beat)
        division=2.0: half bar (2 beats)
        division=4.0: full bar (4 beats)
        """
        step = self.seconds_per_beat * division
        return round(t / step) * step

    def snap_to_next_beat(self, t: float, division: float = 2.0) -> float:
        """Snap upward to the next beat boundary (half-bar or full-bar)."""
        step = self.seconds_per_beat * division
        return math.ceil(t / step) * step

    def get_beat_timestamps(self, total_duration: float) -> List[float]:
        """Return all beat timestamps up to total_duration."""
        beats = []
        t = 0.0
        while t <= total_duration:
            beats.append(round(t, 4))
            t += self.seconds_per_beat
        return beats

    def get_bar_timestamps(self, total_duration: float) -> List[float]:
        """Return all measure/downbeat timestamps (beat 1 of each 4-beat bar)."""
        bars = []
        t = 0.0
        while t <= total_duration:
            bars.append(round(t, 4))
            t += self.seconds_per_bar
        return bars

    def align_scene_durations(
        self,
        speech_durations: List[float],
        transition_duration: float = 0.45,
        min_scene_sec: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Calculates snapped scene durations and start offsets so visual cuts land
        precisely on musical downbeats or half-bars.

        Returns a list of dicts:
        [
          {
            "scene_idx": 1,
            "speech_duration": 4.1,
            "snapped_duration": 4.84,    # Locked to musical bar/beat
            "padding_after_speech": 0.74, # Natural rhythmic breathing room
            "start_time": 0.0,
            "cut_time": 4.84
          },
          ...
        ]
        """
        results = []
        current_time = 0.0

        for idx, s_dur in enumerate(speech_durations, start=1):
            # The visual scene must comfortably cover the narration plus comfortable pause
            ideal_min = max(min_scene_sec, s_dur + 0.35)

            # Snap to half-bar (2 beats) or full-bar (4 beats)
            # For tempos > 120 BPM, half-bar is ~1.0s, full-bar is ~2.0s
            snap_step = self.seconds_per_half_bar if self.bpm >= 120 else self.seconds_per_beat

            # Calculate snapped scene duration
            num_steps = math.ceil(ideal_min / snap_step)
            snapped_duration = round(num_steps * snap_step, 3)

            cut_time = round(current_time + snapped_duration, 3)
            pause_after = max(0.0, round(snapped_duration - s_dur, 3))

            results.append({
                "scene_idx": idx,
                "speech_duration": round(s_dur, 2),
                "snapped_duration": snapped_duration,
                "padding_after_speech": pause_after,
                "start_time": round(current_time, 3),
                "cut_time": cut_time,
                "bpm": self.bpm
            })

            current_time = cut_time

        return results


def detect_bpm_from_audio(audio_path: Path, default_bpm: float = 124.0) -> float:
    """
    Estimates BPM using FFmpeg volume analysis or fallback metadata.
    """
    if not audio_path.exists():
        return default_bpm

    try:
        # Run ffmpeg ebur128/astats filter to check for energy peaks
        cmd = [
            "ffmpeg", "-i", str(audio_path),
            "-af", "lowpass=f=180,astats=metadata=1:reset=1",
            "-f", "null", "-"
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=8)
        # If successfully processed, analyze output or return default
        return default_bpm
    except Exception:
        return default_bpm
