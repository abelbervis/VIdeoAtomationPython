"""
Automatic Sound Effects (SFX) Generator & Mixer for Video Production.
Provides cinematic whoosh transitions and opening hook impacts.
Includes procedural synthesis if external SFX files are not present.
"""

import math
import random
import struct
import subprocess
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from config import SFX_DIR, TEMP_DIR, ENABLE_SFX, SFX_VOLUME


def synthesize_procedural_whoosh(
    output_path: Path,
    duration: float = 0.55,
    sample_rate: int = 44100,
    center_freq: float = 280.0,
    sweep_range: float = 1600.0,
    sub_freq: float = 85.0
) -> Path:
    """Synthesize a smooth cinematic whoosh transition sound effect with customizable acoustics."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_samples = int(duration * sample_rate)
    samples = []

    # Bandpass/swept noise whoosh with exponential bell curve
    for i in range(total_samples):
        t = i / total_samples
        # Bell curve peaking slightly past middle (0.52)
        env = math.exp(-((t - 0.52) ** 2) / (2 * (0.15 ** 2)))

        # Sweeping frequencies: low -> high mid -> low
        freq = center_freq + sweep_range * math.sin(t * math.pi)
        raw_noise = random.uniform(-1.0, 1.0)

        # Low-frequency sub-rumble
        sub_rumble = 0.35 * math.sin(2.0 * math.pi * sub_freq * (1.0 - 0.4 * t) * (i / sample_rate))

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


def synthesize_procedural_boom(
    output_path: Path,
    duration: float = 1.1,
    sample_rate: int = 44100,
    start_freq: float = 110.0,
    end_freq: float = 42.0,
    punch_intensity: float = 0.35
) -> Path:
    """Synthesize a cinematic sub-bass impact for the opening hook."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_samples = int(duration * sample_rate)
    samples = []

    for i in range(total_samples):
        t = i / sample_rate
        norm_t = i / total_samples

        # Smooth exponential decay
        env = math.exp(-norm_t * 4.2)

        # Pitch drops quickly from start_freq to end_freq
        freq = end_freq + (start_freq - end_freq) * math.exp(-norm_t * 7.0)
        phase = 2.0 * math.pi * freq * t

        # Sub sine wave with warm 2nd harmonic
        sub = math.sin(phase) + 0.35 * math.sin(phase * 0.5)

        # Short punchy transient click at t=0
        punch = math.exp(-norm_t * 45.0) * random.uniform(-0.5, 0.5)

        val = (sub * 0.78 + punch * punch_intensity) * env
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

    def __init__(
        self,
        sfx_dir: Path = SFX_DIR,
        output_dir: Optional[Path] = None,
        randomize: bool = True
    ):
        self.sfx_dir = Path(sfx_dir)
        self.output_dir = Path(output_dir) if output_dir else TEMP_DIR
        self.randomize = randomize
        self.sfx_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_default_assets()

    def _ensure_default_assets(self) -> None:
        """Ensure procedural whoosh and boom sound effects exist in temp output directory as fallbacks."""
        whoosh_path = self.output_dir / "procedural_whoosh.wav"
        boom_path = self.output_dir / "procedural_boom.wav"

        if not whoosh_path.exists() or whoosh_path.stat().st_size == 0:
            synthesize_procedural_whoosh(whoosh_path)

        if not boom_path.exists() or boom_path.stat().st_size == 0:
            synthesize_procedural_boom(boom_path)

    def _load_audio_samples(self, filepath: Path, target_sr: int = 44100) -> List[Tuple[float, float]]:
        """
        Load audio samples normalized to floats [-1.0, 1.0].
        Supports any audio format: MP3, WAV, M4A, OGG, FLAC, AAC using FFmpeg with wave fallback.
        """
        if not filepath or not filepath.exists() or filepath.stat().st_size == 0:
            return []

        # 1. First attempt: Use FFmpeg to decode any format directly to raw 16-bit PCM stereo stream
        try:
            cmd = [
                "ffmpeg", "-y", "-v", "quiet",
                "-i", str(filepath.resolve()),
                "-f", "s16le",
                "-ac", "2",
                "-ar", str(target_sr),
                "-"
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            raw_bytes = res.stdout
            if raw_bytes and len(raw_bytes) >= 4:
                num_ints = len(raw_bytes) // 2
                fmt = f"<{num_ints}h"
                ints = struct.unpack(fmt, raw_bytes[:num_ints * 2])
                return [(ints[i] / 32768.0, ints[i + 1] / 32768.0) for i in range(0, len(ints) - 1, 2)]
        except Exception:
            pass

        # 2. Fallback attempt for standard PCM WAV files
        try:
            with wave.open(str(filepath), "rb") as w:
                nchannels = w.getnchannels()
                sampwidth = w.getsampwidth()
                nframes = w.getnframes()
                raw_data = w.readframes(nframes)
                if sampwidth == 2:
                    fmt = f"<{nframes * nchannels}h"
                    ints = struct.unpack(fmt, raw_data)
                    if nchannels == 1:
                        return [(v / 32768.0, v / 32768.0) for v in ints]
                    return [(ints[i] / 32768.0, ints[i + 1] / 32768.0) for i in range(0, len(ints), 2)]
        except Exception as e:
            print(f"  ⚠️ Warning loading SFX {filepath.name}: {e}")

        return []

    def _load_wav_samples(self, filepath: Path, target_sr: int = 44100) -> List[Tuple[float, float]]:
        """Backward-compatible alias for _load_audio_samples."""
        return self._load_audio_samples(filepath, target_sr)

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

        # Scan assets/sfx/ for all user audio files (MP3, WAV, M4A, OGG, FLAC, AAC)
        user_sfx_files: List[Path] = []
        if self.sfx_dir.exists():
            for ext in ("*.mp3", "*.wav", "*.m4a", "*.ogg", "*.flac", "*.aac", "*.MP3", "*.WAV"):
                user_sfx_files.extend([f for f in self.sfx_dir.glob(ext) if f.is_file() and f.stat().st_size > 0])
        user_sfx_files.sort()

        # 1. Opening hook impact at t=0.05s
        boom_candidates = [
            f for f in user_sfx_files
            if any(k in f.name.lower() for k in ("boom", "impact", "hit", "bass", "hook", "intro", "start"))
        ]
        boom_samples: List[Tuple[float, float]] = []

        if boom_candidates:
            chosen_boom = random.choice(boom_candidates) if self.randomize else boom_candidates[0]
            boom_samples = self._load_audio_samples(chosen_boom, sample_rate)
            if boom_samples:
                print(f"  🔊 Impacto de gancho inicial personalizado: {chosen_boom.name}")
        
        if not boom_samples:
            procedural_boom = self.output_dir / "procedural_boom.wav"
            if not procedural_boom.exists():
                synthesize_procedural_boom(procedural_boom)
            boom_samples = self._load_audio_samples(procedural_boom, sample_rate)

        if boom_samples:
            start_frame = int(0.05 * sample_rate)
            boom_vol = volume * (random.uniform(0.80, 0.95) if self.randomize else 0.85)
            for idx, (l_val, r_val) in enumerate(boom_samples):
                pos = start_frame + idx
                if pos < total_frames:
                    left_buf[pos] += l_val * boom_vol
                    right_buf[pos] += r_val * boom_vol

        # 2. Collect pool of whoosh transitions (custom files in assets/sfx/ + procedural fallbacks)
        whoosh_pool: List[List[Tuple[float, float]]] = []
        whoosh_candidates = [
            f for f in user_sfx_files
            if any(k in f.name.lower() for k in ("whoosh", "sweep", "cut", "transition", "swish", "swoosh", "pass"))
        ]
        # If user provided generic audio files not matching 'boom', treat them as potential transitions
        if not whoosh_candidates and user_sfx_files:
            whoosh_candidates = [f for f in user_sfx_files if f not in boom_candidates]

        custom_loaded = []
        for wf in whoosh_candidates:
            s = self._load_audio_samples(wf, sample_rate)
            if s:
                whoosh_pool.append(s)
                custom_loaded.append(wf.name)

        if custom_loaded:
            print(f"  🔊 Transiciones cinemáticas personalizadas ({len(custom_loaded)} archivo(s)): {', '.join(custom_loaded)}")

        # Procedural variants if no custom files or to enrich variety
        if self.randomize and len(whoosh_pool) < 3:
            variants = [
                (0.48, 330.0, 1850.0, 95.0),  # Snappy energetic whoosh
                (0.55, 280.0, 1600.0, 85.0),  # Balanced cinematic whoosh
                (0.64, 210.0, 1300.0, 72.0),  # Deep atmospheric cosmic sweep
            ]
            for dur, cf, sr_f, sub_f in variants:
                temp_w = self.output_dir / f"var_whoosh_{int(cf)}.wav"
                synthesize_procedural_whoosh(temp_w, duration=dur, sample_rate=sample_rate, center_freq=cf, sweep_range=sr_f, sub_freq=sub_f)
                s = self._load_audio_samples(temp_w, sample_rate)
                if s:
                    whoosh_pool.append(s)

        if not whoosh_pool:
            default_w = self.output_dir / "procedural_whoosh.wav"
            if not default_w.exists():
                synthesize_procedural_whoosh(default_w)
            s = self._load_audio_samples(default_w, sample_rate)
            if s:
                whoosh_pool.append(s)

        # 3. Whoosh transition for every subsequent scene cut
        if whoosh_pool and len(scene_timings) > 1:
            for scene in scene_timings[1:]:
                chosen_whoosh = random.choice(whoosh_pool) if self.randomize else whoosh_pool[0]
                cut_vol = volume * (random.uniform(0.90, 1.05) if self.randomize else 1.0)
                lead_time = random.uniform(0.20, 0.24) if self.randomize else 0.22

                cut_time = scene.get("start", 0.0)
                sfx_start = max(0.0, cut_time - lead_time)
                start_frame = int(sfx_start * sample_rate)

                for idx, (l_val, r_val) in enumerate(chosen_whoosh):
                    pos = start_frame + idx
                    if pos < total_frames:
                        left_buf[pos] += l_val * cut_vol
                        right_buf[pos] += r_val * cut_vol

        # 4. Write out combined WAV with soft clipping limiter
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
