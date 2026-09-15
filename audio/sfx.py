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

from config import SFX_DIR, SFX_INTRO_DIR, SFX_SWOOSH_DIR, TEMP_DIR, ENABLE_SFX, SFX_VOLUME


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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_samples = int(duration * sample_rate)
    samples = []

    for i in range(total_samples):
        t = i / total_samples
        sec = i / sample_rate

        if sfx_type in ("intro", "sub_drop"):
            # Cinematic Sub-Bass Impact Drop (808 style) + Sci-Fi Ethereal Chime Hook
            env = math.exp(-t * 3.4)
            # Pitch sweep downwards rapidly: 140Hz -> 38Hz
            drop_freq = 38.0 + (140.0 - 38.0) * math.exp(-t * 9.0)
            sub = 0.72 * math.sin(2.0 * math.pi * drop_freq * sec) + 0.22 * math.sin(4.0 * math.pi * drop_freq * sec)
            punch = 0.40 * math.exp(-t * 40.0) * random.uniform(-0.9, 0.9)
            # High crystalline harmonics
            chime = (
                0.25 * math.sin(2.0 * math.pi * 587.33 * sec) * math.exp(-t * 3.2) +
                0.20 * math.sin(2.0 * math.pi * 880.00 * sec) * math.exp(-t * 4.0) +
                0.15 * math.sin(2.0 * math.pi * 1174.66 * sec) * math.exp(-t * 4.8)
            )
            val = (sub + punch + chime) * env
            l_val, r_val = val, val

        elif sfx_type in ("zoom_in", "whoosh_quantum"):
            # High-velocity futuristic Sci-Fi Woosh / Swish (Left-to-Right Haas whip)
            env = math.exp(-((t - 0.48) ** 2) / (2 * (0.13 ** 2)))
            # Frequency acceleration curve
            sweep_freq = 220.0 + 1400.0 * (t ** 2.2)
            synth = 0.35 * math.sin(2.0 * math.pi * sweep_freq * sec) + 0.18 * math.sin(3.0 * math.pi * sweep_freq * sec)
            filtered_noise = 0.55 * random.uniform(-1.0, 1.0) * (0.6 + 0.4 * math.sin(t * math.pi))
            sub_tail = 0.28 * math.sin(2.0 * math.pi * 65.0 * sec) * math.exp(-((t - 0.65) ** 2) / 0.05)
            # High-tech laser lock snap at the end
            snap = 0.30 * math.exp(-((t - 0.72) ** 2) / (2 * (0.015 ** 2))) * math.sin(2.0 * math.pi * 1800.0 * sec)
            raw = (synth + filtered_noise + sub_tail) * env + snap
            # Dynamic stereo pan (Left -> Right sweeping swish)
            l_val = raw * (1.1 - 0.85 * t)
            r_val = raw * (0.25 + 0.85 * t)

        elif sfx_type in ("pan", "whoosh_solar"):
            # Radiant Plasma Swoosh (Right-to-Center blazing transition)
            env = math.exp(-((t - 0.50) ** 2) / (2 * (0.14 ** 2)))
            # Downward solar frequency glide
            plasma_freq = 1100.0 - 650.0 * (t ** 0.8)
            plasma_osc = 0.38 * math.sin(2.0 * math.pi * plasma_freq * sec) + 0.20 * math.sin(2.0 * math.pi * (plasma_freq * 1.5) * sec)
            sizzle = 0.48 * random.uniform(-1.0, 1.0)
            sub_pulse = 0.30 * math.sin(2.0 * math.pi * 82.0 * sec)
            raw = (plasma_osc + sizzle + sub_pulse) * env
            # Dynamic stereo pan (Right -> Center/Left)
            l_val = raw * (0.2 + 0.8 * t)
            r_val = raw * (1.0 - 0.6 * t)

        elif sfx_type in ("pull_back", "wide"):
            # Deep Cosmic Suction / Wide Camera Release
            env = math.exp(-((t - 0.45) ** 2) / (2 * (0.16 ** 2)))
            sub_drone = 0.45 * math.sin(2.0 * math.pi * 95.0 * (1.0 - 0.45 * t) * sec)
            whoosh_air = 0.45 * random.uniform(-1.0, 1.0)
            bass_lock = 0.35 * math.exp(-((t - 0.80) ** 2) / (2 * (0.025 ** 2))) * math.sin(2.0 * math.pi * 120.0 * sec)
            val = (sub_drone + whoosh_air) * env + bass_lock
            l_val, r_val = val, val

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

    return output_path


def synthesize_space_ambient_pad(
    output_path: Path,
    duration: float = 12.0,
    sample_rate: int = 44100
) -> Path:
    """Synthesize a lush, cinematic sci-fi ambient space drone soundtrack."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_samples = int(duration * sample_rate)
    samples = []

    for i in range(total_samples):
        sec = i / sample_rate
        fade_in = min(1.0, sec / 1.2)
        fade_out = min(1.0, (duration - sec) / 2.0) if sec > duration - 2.0 else 1.0
        env = fade_in * fade_out

        f1, f2, f3, f4 = 65.41, 130.81, 196.00, 329.63
        lfo_slow = math.sin(2.0 * math.pi * 0.18 * sec)
        lfo_phase = math.cos(2.0 * math.pi * 0.12 * sec)

        osc1 = 0.35 * math.sin(2.0 * math.pi * f1 * sec)
        osc2 = 0.25 * math.sin(2.0 * math.pi * (f2 + 0.4 * lfo_slow) * sec)
        osc3 = 0.20 * math.sin(2.0 * math.pi * (f3 + 0.6 * lfo_phase) * sec)
        osc4 = 0.12 * math.sin(2.0 * math.pi * f4 * sec)
        space_air = 0.08 * random.uniform(-1.0, 1.0) * (0.7 + 0.3 * lfo_slow)

        val_l = (osc1 + osc2 * 1.1 + osc3 * 0.8 + osc4 + space_air) * env * 0.40
        val_r = (osc1 + osc2 * 0.8 + osc3 * 1.1 + osc4 + space_air) * env * 0.40

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
