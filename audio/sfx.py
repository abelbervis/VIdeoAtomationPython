"""
Automatic Sound Effects (SFX) Generator & Mixer for Video Production.
Provides cinematic whoosh transitions and opening hook impacts.
Includes procedural synthesis if external SFX files are not present.
"""

import math
import random
import shutil
import struct
import subprocess
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from config import SFX_DIR, SFX_INTRO_DIR, SFX_SWOOSH_DIR, TEMP_DIR, ENABLE_SFX, SFX_VOLUME

SFX_CACHE_DIR = Path(__file__).resolve().parent.parent / "assets" / "sfx" / "cached"


def synthesize_procedural_whoosh(
    output_path: Path,
    duration: float = 0.55,
    sample_rate: int = 44100,
    center_freq: float = 280.0,
    sweep_range: float = 1600.0,
    sub_freq: float = 85.0
) -> Path:
    """Synthesize a smooth cinematic whoosh transition sound effect with customizable acoustics."""
    output_path = Path(output_path)
    if output_path.exists() and output_path.stat().st_size > 100:
        return output_path

    SFX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = SFX_CACHE_DIR / f"whoosh_{int(duration * 1000)}_{int(center_freq)}_{int(sweep_range)}.wav"
    if cache_file.exists() and cache_file.stat().st_size > 100:
        if output_path.resolve() != cache_file.resolve():
            shutil.copy2(cache_file, output_path)
        return output_path

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

    if output_path.resolve() != cache_file.resolve():
        try:
            shutil.copy2(output_path, cache_file)
        except Exception:
            pass

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
    output_path = Path(output_path)
    if output_path.exists() and output_path.stat().st_size > 100:
        return output_path

    SFX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = SFX_CACHE_DIR / f"boom_{int(duration * 1000)}.wav"
    if cache_file.exists() and cache_file.stat().st_size > 100:
        if output_path.resolve() != cache_file.resolve():
            shutil.copy2(cache_file, output_path)
        return output_path

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

    if output_path.resolve() != cache_file.resolve():
        try:
            shutil.copy2(output_path, cache_file)
        except Exception:
            pass

    return output_path


def synthesize_camera_servo_sfx(
    output_path: Path,
    duration: float = 0.50,
    sample_rate: int = 44100,
    sfx_type: str = "zoom_in"
) -> Path:
    """
    Synthesizes next-gen cinematic Sci-Fi sound effects:
      - 'intro' / 'sub_drop': Heavy cinematic 808 sub-bass drop + cosmic shimmer hook
      - 'zoom_in' / 'whoosh_quantum': High-velocity futuristic swish with stereo Haas panning
      - 'pan' / 'whoosh_solar': Radiant plasma swoosh with sizzling harmonic overtone
      - 'pull_back' / 'wide': Deep cosmic suction whoosh with sub-bass tail
      - 'quantum_hum': Ominous sub-quantum resonant hum with phase modulation
      - 'solar_flare': Searing solar energy discharge stinger
    """
    output_path = Path(output_path)
    if output_path.exists() and output_path.stat().st_size > 100:
        return output_path

    SFX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = SFX_CACHE_DIR / f"{sfx_type}_{int(duration * 1000)}ms_{sample_rate}.wav"
    if cache_file.exists() and cache_file.stat().st_size > 100:
        if output_path.resolve() != cache_file.resolve():
            shutil.copy2(cache_file, output_path)
        return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_samples = int(duration * sample_rate)
    samples = []

    for i in range(total_samples):
        t = i / total_samples
        sec = i / sample_rate

        if sfx_type in ("intro", "sub_drop"):
            # Next-Gen Cinematic 808 Sub-Drop + Shimmering Quantum Particle Chime
            env = math.exp(-t * 2.8)
            # Pitch sweep downwards smoothly: 160Hz -> 36Hz
            drop_freq = 36.0 + (160.0 - 36.0) * math.exp(-t * 8.5)
            sub = 0.82 * math.sin(2.0 * math.pi * drop_freq * sec) + 0.35 * math.sin(4.0 * math.pi * drop_freq * sec)
            # Transient acoustic punch
            punch = 0.50 * math.exp(-t * 50.0) * (math.sin(2.0 * math.pi * 95.0 * sec) + random.uniform(-0.6, 0.6))
            # Shimmering high-fidelity celestial overtone chords
            chime_l = (
                0.22 * math.sin(2.0 * math.pi * 587.33 * sec) * math.exp(-t * 2.8) +
                0.16 * math.sin(2.0 * math.pi * 880.00 * sec) * math.exp(-t * 3.6) +
                0.12 * math.sin(2.0 * math.pi * 1760.00 * sec) * math.exp(-t * 4.4)
            )
            chime_r = (
                0.16 * math.sin(2.0 * math.pi * 587.33 * sec) * math.exp(-t * 2.8) +
                0.22 * math.sin(2.0 * math.pi * 1174.66 * sec) * math.exp(-t * 3.6) +
                0.14 * math.sin(2.0 * math.pi * 1760.00 * sec) * math.exp(-t * 4.4)
            )
            l_val = (sub * 0.75 + punch * 0.6 + chime_l) * env
            r_val = (sub * 0.75 + punch * 0.6 + chime_r) * env

        elif sfx_type in ("zoom_in", "whoosh_quantum"):
            # High-velocity Quantum Warp Swish with Haas 3D Spatial Panning (Left -> Center/Right)
            env = math.exp(-((t - 0.46) ** 2) / (2 * (0.12 ** 2)))
            sweep_freq = 240.0 + 1650.0 * (t ** 2.4)
            synth = 0.38 * math.sin(2.0 * math.pi * sweep_freq * sec) + 0.22 * math.sin(3.0 * math.pi * sweep_freq * sec)
            # Crystalline quantum granular texture
            q_grain = 0.45 * random.uniform(-1.0, 1.0) * (0.7 + 0.3 * math.sin(t * math.pi * 4.0))
            sub_tail = 0.32 * math.sin(2.0 * math.pi * 58.0 * sec) * math.exp(-((t - 0.60) ** 2) / 0.04)
            # Laser quantum snap stinger
            snap = 0.35 * math.exp(-((t - 0.70) ** 2) / (2 * (0.012 ** 2))) * math.sin(2.0 * math.pi * 2100.0 * sec)
            raw = (synth + q_grain + sub_tail) * env + snap
            # Binaural 3D Left-to-Right sweep
            l_val = raw * (1.15 - 0.85 * t)
            r_val = raw * (0.20 + 0.90 * t)

        elif sfx_type in ("pan", "whoosh_solar"):
            # Blazing Radiant Plasma Swoosh (Right -> Center/Left Stereo Transition)
            env = math.exp(-((t - 0.48) ** 2) / (2 * (0.13 ** 2)))
            plasma_freq = 1250.0 - 750.0 * (t ** 0.75)
            plasma_osc = 0.42 * math.sin(2.0 * math.pi * plasma_freq * sec) + 0.24 * math.sin(2.0 * math.pi * (plasma_freq * 1.5) * sec)
            # Sizzling stellar prominence noise
            solar_sizzle = 0.45 * random.uniform(-1.0, 1.0) * (0.6 + 0.4 * math.sin(t * math.pi))
            sub_corona = 0.34 * math.sin(2.0 * math.pi * 75.0 * sec)
            raw = (plasma_osc + solar_sizzle + sub_corona) * env
            # Binaural 3D Right-to-Left sweep
            l_val = raw * (0.20 + 0.90 * t)
            r_val = raw * (1.15 - 0.85 * t)

        elif sfx_type in ("pull_back", "wide"):
            # Deep Volumetric Cosmic Suction / Wide Camera Zoom Out
            env = math.exp(-((t - 0.42) ** 2) / (2 * (0.15 ** 2)))
            sub_drone = 0.52 * math.sin(2.0 * math.pi * 88.0 * (1.0 - 0.40 * t) * sec)
            whoosh_air = 0.42 * random.uniform(-1.0, 1.0)
            bass_anchor = 0.40 * math.exp(-((t - 0.75) ** 2) / (2 * (0.022 ** 2))) * math.sin(2.0 * math.pi * 105.0 * sec)
            val = (sub_drone + whoosh_air) * env + bass_anchor
            l_val = val * (0.95 + 0.1 * math.sin(2.0 * math.pi * 1.5 * sec))
            r_val = val * (0.95 - 0.1 * math.sin(2.0 * math.pi * 1.5 * sec))

        elif sfx_type in ("cosmic_resonance", "verdict_chime"):
            # Rich Dual Cosmic Bell Stinger (Sub-bass + Quantum Cyan Chime + Solar Plasma Bell)
            env = min(1.0, sec / 0.05) * math.exp(-t * 1.9)
            sub_base = 0.65 * math.sin(2.0 * math.pi * 52.0 * sec) + 0.30 * math.sin(2.0 * math.pi * 104.0 * sec)
            cyan_crystal = (
                0.32 * math.sin(2.0 * math.pi * 880.0 * sec) * math.exp(-t * 2.8) +
                0.22 * math.sin(2.0 * math.pi * 1320.0 * sec) * math.exp(-t * 3.5) +
                0.14 * math.sin(2.0 * math.pi * 2640.0 * sec) * math.exp(-t * 4.2)
            )
            solar_plasma = (
                0.32 * math.sin(2.0 * math.pi * 440.0 * sec) * math.exp(-t * 2.5) +
                0.20 * math.sin(2.0 * math.pi * 660.0 * sec) * math.exp(-t * 3.2)
            )
            val = (sub_base + cyan_crystal + solar_plasma) * env
            l_val = val * (0.85 + 0.25 * math.sin(2.0 * math.pi * 2.5 * sec))
            r_val = val * (0.85 - 0.25 * math.sin(2.0 * math.pi * 2.5 * sec))

        elif sfx_type == "quantum_hum":
            # Ominous Deep Sub-Bass Quantum Revelation Hum
            env = min(1.0, sec / 0.15) * math.exp(-t * 2.2)
            sub_f = 48.0 + 8.0 * math.sin(2.0 * math.pi * 1.5 * sec)
            sub_osc = 0.75 * math.sin(2.0 * math.pi * sub_f * sec)
            dark_resonance = 0.25 * math.sin(2.0 * math.pi * (sub_f * 2.5) * sec)
            val = (sub_osc + dark_resonance) * env
            l_val, r_val = val, val

        elif sfx_type in ("solar_flare", "flare"):
            # Blazing Solar Flare Stinger
            env = min(1.0, sec / 0.08) * math.exp(-t * 2.6)
            flare_f = 750.0 + 350.0 * math.sin(2.0 * math.pi * 6.0 * sec)
            flare_osc = 0.40 * math.sin(2.0 * math.pi * flare_f * sec)
            heat_noise = 0.35 * random.uniform(-1.0, 1.0)
            val = (flare_osc + heat_noise) * env
            l_val, r_val = val, val

        elif sfx_type in ("cosmic_resonance", "verdict_chime"):
            # Resonant Dual Harmonic Cosmic Bell / Stinger (Sub-bass + Cyan Chime + Solar Brass)
            env = min(1.0, sec / 0.06) * math.exp(-t * 2.1)
            sub_base = 0.55 * math.sin(2.0 * math.pi * 55.0 * sec) + 0.25 * math.sin(2.0 * math.pi * 110.0 * sec)
            cyan_crystal = 0.28 * math.sin(2.0 * math.pi * 880.0 * sec) * math.exp(-t * 3.2) + 0.18 * math.sin(2.0 * math.pi * 1320.0 * sec) * math.exp(-t * 4.0)
            solar_plasma = 0.28 * math.sin(2.0 * math.pi * 440.0 * sec) * math.exp(-t * 2.8) + 0.16 * math.sin(2.0 * math.pi * 660.0 * sec) * math.exp(-t * 3.5)
            harmonic_shimmer = 0.12 * math.sin(2.0 * math.pi * 1760.0 * sec + math.sin(2.0 * math.pi * 8.0 * sec))
            val = (sub_base + cyan_crystal + solar_plasma + harmonic_shimmer) * env
            l_val = val * (0.8 + 0.2 * math.sin(2.0 * math.pi * 2.0 * sec))
            r_val = val * (0.8 - 0.2 * math.sin(2.0 * math.pi * 2.0 * sec))

        else:
            env = math.exp(-t * 3.0)
            val = 0.5 * math.sin(2.0 * math.pi * 440.0 * sec) * env
            l_val, r_val = val, val

        l_val = max(-1.0, min(1.0, l_val * 0.88))
        r_val = max(-1.0, min(1.0, r_val * 0.88))
        samples.append(struct.pack("<hh", int(l_val * 32767), int(r_val * 32767)))

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"".join(samples))

    if output_path.resolve() != cache_file.resolve():
        try:
            shutil.copy2(output_path, cache_file)
        except Exception:
            pass

    return output_path


def synthesize_space_ambient_pad(
    output_path: Path,
    duration: float = 12.0,
    sample_rate: int = 44100
) -> Path:
    """Synthesize a lush, multi-harmonic cinematic sci-fi ambient space drone soundtrack."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_samples = int(duration * sample_rate)
    samples = []

    for i in range(total_samples):
        sec = i / sample_rate
        fade_in = min(1.0, sec / 1.5)
        fade_out = min(1.0, (duration - sec) / 2.2) if sec > duration - 2.2 else 1.0
        env = fade_in * fade_out

        # Celestial modal frequencies (D Dorian / Deep Space Harmonic Spectrum)
        # Fundamental roots: D2 (73.42Hz), A2 (110.00Hz), F3 (174.61Hz), C4 (261.63Hz), E4 (329.63Hz)
        lfo_slow = math.sin(2.0 * math.pi * 0.08 * sec)
        lfo_fast = math.sin(2.0 * math.pi * 0.22 * sec)
        lfo_chorus = math.cos(2.0 * math.pi * 0.14 * sec)

        # Warm deep sub-bass foundation
        sub_d = 0.40 * math.sin(2.0 * math.pi * 36.71 * sec)
        sub_root = 0.35 * math.sin(2.0 * math.pi * 73.42 * sec)

        # Ethereal mid pads with organic analog detune
        pad_fifth = 0.25 * math.sin(2.0 * math.pi * (110.00 + 0.35 * lfo_slow) * sec)
        pad_third = 0.20 * math.sin(2.0 * math.pi * (174.61 + 0.45 * lfo_chorus) * sec)
        pad_seventh = 0.16 * math.sin(2.0 * math.pi * (261.63 + 0.25 * lfo_fast) * sec)
        pad_ninth = 0.12 * math.sin(2.0 * math.pi * (329.63 + 0.50 * lfo_slow) * sec)

        # High crystal shimmer
        shimmer = 0.06 * math.sin(2.0 * math.pi * (1046.50 + math.sin(2.0 * math.pi * 2.0 * sec)) * sec) * (0.6 + 0.4 * lfo_fast)
        cosmic_air = 0.04 * random.uniform(-1.0, 1.0) * (0.8 + 0.2 * lfo_slow)

        # Stereo binaural widening
        val_l = (sub_d + sub_root + pad_fifth * 1.15 + pad_third * 0.85 + pad_seventh * 1.1 + pad_ninth * 0.9 + shimmer + cosmic_air) * env * 0.42
        val_r = (sub_d + sub_root + pad_fifth * 0.85 + pad_third * 1.15 + pad_seventh * 0.9 + pad_ninth * 1.1 + shimmer * 1.1 + cosmic_air) * env * 0.42

        val_l = max(-1.0, min(1.0, val_l))
        val_r = max(-1.0, min(1.0, val_r))
        samples.append(struct.pack("<hh", int(val_l * 32767), int(val_r * 32767)))

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
        intro_dir: Optional[Path] = None,
        swoosh_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        randomize: bool = True
    ):
        self.sfx_dir = Path(sfx_dir)
        self.intro_dir = Path(intro_dir) if intro_dir else (SFX_INTRO_DIR if SFX_INTRO_DIR.parent == self.sfx_dir else self.sfx_dir / "intro")
        self.swoosh_dir = Path(swoosh_dir) if swoosh_dir else (SFX_SWOOSH_DIR if SFX_SWOOSH_DIR.parent == self.sfx_dir else self.sfx_dir / "swoosh")
        self.output_dir = Path(output_dir) if output_dir else TEMP_DIR
        self.randomize = randomize

        self.sfx_dir.mkdir(parents=True, exist_ok=True)
        self.intro_dir.mkdir(parents=True, exist_ok=True)
        self.swoosh_dir.mkdir(parents=True, exist_ok=True)
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

    def _scan_audio_files(self, folder: Path) -> List[Path]:
        """Scan a folder for all supported audio formats (MP3, WAV, M4A, OGG, FLAC, AAC)."""
        if not folder or not folder.exists() or not folder.is_dir():
            return []
        found: List[Path] = []
        for ext in (
            "*.mp3", "*.wav", "*.m4a", "*.ogg", "*.flac", "*.aac", "*.wma",
            "*.MP3", "*.WAV", "*.M4A", "*.OGG", "*.FLAC", "*.AAC"
        ):
            found.extend([f for f in folder.glob(ext) if f.is_file() and f.stat().st_size > 0])
        return sorted(list(set(found)))

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

        # 1. Opening hook impact at t=0.05s
        # First priority: check assets/sfx/intro/ (any audio file, name doesn't matter, picked randomly)
        intro_candidates = self._scan_audio_files(self.intro_dir)
        source_intro_dir = self.intro_dir.name

        # Fallback: scan root sfx_dir for keyword matches
        if not intro_candidates:
            root_sfx = self._scan_audio_files(self.sfx_dir)
            intro_candidates = [
                f for f in root_sfx
                if any(k in f.name.lower() for k in ("boom", "impact", "hit", "bass", "hook", "intro", "start"))
            ]
            source_intro_dir = "sfx"

        boom_samples: List[Tuple[float, float]] = []
        if intro_candidates:
            chosen_boom = random.choice(intro_candidates) if self.randomize else intro_candidates[0]
            boom_samples = self._load_audio_samples(chosen_boom, sample_rate)
            if boom_samples:
                print(f"  🔊 Impacto de gancho inicial: '{chosen_boom.name}' seleccionado aleatoriamente ({len(intro_candidates)} en {source_intro_dir}/)")

        # Procedural fallback if no audio file was found or decoded
        if not boom_samples:
            procedural_boom = self.output_dir / "procedural_boom.wav"
            if not procedural_boom.exists():
                synthesize_procedural_boom(procedural_boom)
            boom_samples = self._load_audio_samples(procedural_boom, sample_rate)

        if boom_samples:
            start_frame = int(0.00 * sample_rate)
            boom_vol = volume * (random.uniform(0.80, 0.95) if self.randomize else 0.85)
            for idx, (l_val, r_val) in enumerate(boom_samples):
                pos = start_frame + idx
                if pos < total_frames:
                    left_buf[pos] += l_val * boom_vol
                    right_buf[pos] += r_val * boom_vol

        # 2. Collect pool of swoosh transitions (any audio in assets/sfx/swoosh/ picked randomly per cut)
        whoosh_pool: List[List[Tuple[float, float]]] = []

        # First priority: check assets/sfx/swoosh/ (or alias assets/sfx/whoosh/)
        swoosh_candidates = self._scan_audio_files(self.swoosh_dir)
        source_swoosh_dir = self.swoosh_dir.name
        if not swoosh_candidates and (self.sfx_dir / "whoosh").is_dir():
            swoosh_candidates = self._scan_audio_files(self.sfx_dir / "whoosh")
            source_swoosh_dir = "whoosh"

        # Fallback: scan root sfx_dir for keyword matches
        if not swoosh_candidates:
            root_sfx = self._scan_audio_files(self.sfx_dir)
            swoosh_candidates = [
                f for f in root_sfx
                if any(k in f.name.lower() for k in ("whoosh", "sweep", "cut", "transition", "swish", "swoosh", "pass"))
            ]
            if not swoosh_candidates and root_sfx:
                swoosh_candidates = [f for f in root_sfx if f not in intro_candidates]
            source_swoosh_dir = "sfx"

        custom_loaded: List[str] = []
        for wf in swoosh_candidates:
            s = self._load_audio_samples(wf, sample_rate)
            if s:
                whoosh_pool.append(s)
                custom_loaded.append(wf.name)

        if custom_loaded:
            print(f"  🔊 Transiciones swoosh: {len(custom_loaded)} efecto(s) cargados desde {source_swoosh_dir}/ (se elegirán aleatoriamente por corte: {', '.join(custom_loaded)})")

        # Procedural variants ONLY if no custom swoosh files exist
        if not whoosh_pool:
            if self.randomize:
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
