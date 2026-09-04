"""
Automatic Sound Effects (SFX) Generator & Mixer for Video Production.
Provides cinematic whoosh transitions and opening hook impacts.
Includes procedural synthesis if external SFX files are not present.
"""

import math
import random
import struct
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from config import SFX_DIR, TEMP_DIR, ENABLE_SFX, SFX_VOLUME


def synthesize_procedural_whoosh(output_path: Path, duration: float = 0.55, sample_rate: int = 44100) -> Path:
    """Synthesize a smooth cinematic whoosh transition sound effect."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_samples = int(duration * sample_rate)
    samples = []

    # Bandpass/swept noise whoosh with exponential bell curve
    for i in range(total_samples):
        t = i / total_samples
        # Bell curve peaking slightly past middle (0.52)
        env = math.exp(-((t - 0.52) ** 2) / (2 * (0.15 ** 2)))

        # Sweeping frequencies: low -> high mid -> low
        freq = 280 + 1600 * math.sin(t * math.pi)
        raw_noise = random.uniform(-1.0, 1.0)

        # Low-frequency sub-rumble
        sub_rumble = 0.35 * math.sin(2.0 * math.pi * 85 * (1.0 - 0.4 * t) * (i / sample_rate))

        val = (raw_noise * 0.65 + sub_rumble) * env
        val = max(-1.0, min(1.0, val * 0.85))
        sample_int = int(val * 32767)
        samples.append(struct.pack("<hh", sample_int, sample_int))

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"".join(samples))

    return output_path


def synthesize_procedural_boom(output_path: Path, duration: float = 1.1, sample_rate: int = 44100) -> Path:
    """Synthesize a cinematic sub-bass impact for the opening hook."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_samples = int(duration * sample_rate)
    samples = []

    for i in range(total_samples):
        t = i / sample_rate
        norm_t = i / total_samples

        # Smooth exponential decay
        env = math.exp(-norm_t * 4.2)

        # Pitch drops quickly from 110Hz to 42Hz
        freq = 42.0 + 70.0 * math.exp(-norm_t * 7.0)
        phase = 2.0 * math.pi * freq * t

        # Sub sine wave with warm 2nd harmonic
        sub = math.sin(phase) + 0.35 * math.sin(phase * 0.5)

        # Short punchy transient click at t=0
        punch = math.exp(-norm_t * 45.0) * random.uniform(-0.5, 0.5)

        val = (sub * 0.78 + punch * 0.35) * env
        val = max(-1.0, min(1.0, val * 0.85))
        sample_int = int(val * 32767)
        samples.append(struct.pack("<hh", sample_int, sample_int))

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"".join(samples))

    return output_path


class SFXManager:
    """Manages sound effect assets and timeline synchronization."""

    def __init__(self, sfx_dir: Path = SFX_DIR, output_dir: Optional[Path] = None):
        self.sfx_dir = Path(sfx_dir)
        self.output_dir = Path(output_dir) if output_dir else TEMP_DIR
        self.sfx_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_default_assets()

    def _ensure_default_assets(self) -> None:
        """Ensure standard whoosh and boom sound effects exist on disk."""
        whoosh_path = self.sfx_dir / "whoosh.wav"
        boom_path = self.sfx_dir / "boom.wav"

        if not whoosh_path.exists() or whoosh_path.stat().st_size == 0:
            synthesize_procedural_whoosh(whoosh_path)

        if not boom_path.exists() or boom_path.stat().st_size == 0:
            synthesize_procedural_boom(boom_path)

    def _load_wav_samples(self, filepath: Path, target_sr: int = 44100) -> List[Tuple[float, float]]:
        """Load 16-bit stereo/mono WAV samples normalized to floats [-1.0, 1.0]."""
        samples: List[Tuple[float, float]] = []
        try:
            with wave.open(str(filepath), "rb") as w:
                nchannels = w.getnchannels()
                sampwidth = w.getsampwidth()
                framerate = w.getframerate()
                nframes = w.getnframes()
                raw_data = w.readframes(nframes)

                if sampwidth != 2:
                    return []

                fmt = f"<{nframes * nchannels}h"
                ints = struct.unpack(fmt, raw_data)

                if nchannels == 1:
                    samples = [(v / 32768.0, v / 32768.0) for v in ints]
                else:
                    samples = [(ints[i] / 32768.0, ints[i + 1] / 32768.0) for i in range(0, len(ints), 2)]
        except Exception as e:
            print(f"  ⚠️ Warning loading SFX {filepath.name}: {e}")
        return samples

    def build_sfx_timeline(
        self,
        scene_timings: List[Dict[str, Any]],
        total_duration: float,
        output_path: Optional[Path] = None,
        volume: float = SFX_VOLUME,
        sample_rate: int = 44100
    ) -> Optional[Path]:
        """
        Assemble a single synchronized SFX track matching scene transitions.
        Places:
        - Opening cinematic impact (boom) at t=0.05s
        - Transition whooshes at each scene cut (t = scene['start'] - 0.22s)
        """
        if not scene_timings or total_duration <= 0:
            return None

        dest_file = Path(output_path) if output_path else self.output_dir / "sfx_timeline.wav"
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        total_frames = int(math.ceil(total_duration * sample_rate))
        # Master stereo float buffer
        left_buf = [0.0] * total_frames
        right_buf = [0.0] * total_frames

        whoosh_file = self.sfx_dir / "whoosh.wav"
        boom_file = self.sfx_dir / "boom.wav"

        whoosh_samples = self._load_wav_samples(whoosh_file, sample_rate) if whoosh_file.exists() else []
        boom_samples = self._load_wav_samples(boom_file, sample_rate) if boom_file.exists() else []

        # 1. Opening hook impact at t=0.05s
        if boom_samples:
            start_frame = int(0.05 * sample_rate)
            boom_vol = volume * 0.85
            for idx, (l_val, r_val) in enumerate(boom_samples):
                pos = start_frame + idx
                if pos < total_frames:
                    left_buf[pos] += l_val * boom_vol
                    right_buf[pos] += r_val * boom_vol

        # 2. Whoosh transition for every subsequent scene
        if whoosh_samples and len(scene_timings) > 1:
            whoosh_vol = volume
            for scene in scene_timings[1:]:
                # Lead into the cut by 0.22s (whoosh peaks at 0.27s)
                cut_time = scene.get("start", 0.0)
                sfx_start = max(0.0, cut_time - 0.22)
                start_frame = int(sfx_start * sample_rate)

                for idx, (l_val, r_val) in enumerate(whoosh_samples):
                    pos = start_frame + idx
                    if pos < total_frames:
                        left_buf[pos] += l_val * whoosh_vol
                        right_buf[pos] += r_val * whoosh_vol

        # 3. Write out combined WAV with soft clipping limiter
        packed_frames = []
        for i in range(total_frames):
            l = max(-1.0, min(1.0, left_buf[i]))
            r = max(-1.0, min(1.0, right_buf[i]))
            l_int = int(l * 32767)
            r_int = int(r * 32767)
            packed_frames.append(struct.pack("<hh", l_int, r_int))

        with wave.open(str(dest_file), "wb") as out_wav:
            out_wav.setnchannels(2)
            out_wav.setsampwidth(2)
            out_wav.setframerate(sample_rate)
            out_wav.writeframes(b"".join(packed_frames))

        print(f"  🔊 SFX Timeline generated: {dest_file.name} ({len(scene_timings)} scenes with transition whooshes)")
        return dest_file
