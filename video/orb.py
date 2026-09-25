"""
Ultra-Clean Bio-Reactive Presenter Orb Generator & Compositor.
Renders a pristine bioluminescent energy sphere matching the user's reference design:
- Vibrant cyan-to-violet gradient body
- Off-center glowing white/magenta core light spot
- Soft neon purple atmospheric aura & crisp glowing edge ring
- Smooth 60-frame procedural loop (QuickTime MOV with ARGB alpha)
- Speech envelope audio reactivity (brightness, scale, & color surges on speech)
"""

import math
import json

import struct
import subprocess
import wave
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List


def extract_audio_speech_envelope(
    audio_path: Path,
    threshold: float = 0.035,
    min_silence_dur: float = 0.40,
    max_intervals: int = 35,
) -> List[Tuple[float, float]]:
    """Extracts continuous speech intervals [(start_sec, end_sec), ...] from narration audio."""
    audio_path = Path(audio_path)
    if not audio_path.exists() or audio_path.stat().st_size == 0:
        return []

    wav_to_clean: Optional[Path] = None
    read_path = audio_path

    if audio_path.suffix.lower() != ".wav":
        wav_to_clean = audio_path.parent / f"_temp_env_{audio_path.stem}.wav"
        try:
            subprocess.run([
                "ffmpeg", "-y",
                "-i", str(audio_path),
                "-ac", "1",
                "-ar", "16000",
                "-c:a", "pcm_s16le",
                str(wav_to_clean)
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            read_path = wav_to_clean
        except Exception:
            return []

    try:
        with wave.open(str(read_path), "rb") as wf:
            s_rate = wf.getframerate()
            n_frames = wf.getnframes()
            raw_bytes = wf.readframes(n_frames)

        samples_count = len(raw_bytes) // 2
        if samples_count == 0:
            return []

        samples = struct.unpack(f"<{samples_count}h", raw_bytes)
        chunk_size = max(1, s_rate // 10)

        raw_active = []
        for i in range(0, len(samples), chunk_size):
            chunk = samples[i:i + chunk_size]
            if not chunk:
                continue
            rms = math.sqrt(sum(s * s for s in chunk) / len(chunk))
            norm = min(1.0, rms / 8000.0)
            raw_active.append(norm >= threshold)

        raw_intervals: List[Tuple[float, float]] = []
        in_speech = False
        start_idx = 0
        for idx, is_act in enumerate(raw_active):
            if is_act and not in_speech:
                in_speech = True
                start_idx = idx
            elif not is_act and in_speech:
                in_speech = False
                raw_intervals.append((round(start_idx * 0.1, 2), round(idx * 0.1, 2)))
        if in_speech:
            raw_intervals.append((round(start_idx * 0.1, 2), round(len(raw_active) * 0.1, 2)))

        merged: List[Tuple[float, float]] = []
        for start, end in raw_intervals:
            if not merged:
                merged.append((start, end))
            else:
                prev_start, prev_end = merged[-1]
                if start - prev_end <= min_silence_dur:
                    merged[-1] = (prev_start, max(prev_end, end))
                else:
                    merged.append((start, end))

        filtered = [(s, e) for s, e in merged if (e - s) >= 0.18]
        if len(filtered) > max_intervals:
            filtered = filtered[:max_intervals]

        return filtered
    except Exception as e:
        print(f"  ⚠️ Audio envelope extraction notice: {e}")
        return []
    finally:
        if wav_to_clean and wav_to_clean.exists():
            try:
                wav_to_clean.unlink()
            except Exception:
                pass


def extract_real_audio_rms_profile(
    audio_path: Path,
    intervals: List[Tuple[float, float]],
    step_hz: int = 5,
) -> str:
    """
    Extracts high-contrast syllable/speech RMS energy bursts from narration audio,
    returning a compact FFmpeg mathematical expression that surges precisely on spoken syllables.
    """
    audio_path = Path(audio_path)
    if not audio_path.exists() or audio_path.stat().st_size == 0 or not intervals:
        return "(0.5 + 0.3*sin(2*PI*t/0.24))"

    wav_to_clean: Optional[Path] = None
    read_path = audio_path

    if audio_path.suffix.lower() != ".wav":
        wav_to_clean = audio_path.parent / f"_temp_rms_{audio_path.stem}.wav"
        try:
            subprocess.run([
                "ffmpeg", "-y",
                "-i", str(audio_path),
                "-ac", "1",
                "-ar", "16000",
                "-c:a", "pcm_s16le",
                str(wav_to_clean)
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            read_path = wav_to_clean
        except Exception:
            return "(0.5 + 0.3*sin(2*PI*t/0.24))"

    try:
        with wave.open(str(read_path), "rb") as wf:
            s_rate = wf.getframerate()
            n_frames = wf.getnframes()
            raw_bytes = wf.readframes(n_frames)

        samples_count = len(raw_bytes) // 2
        if samples_count == 0:
            return "(0.5 + 0.3*sin(2*PI*t/0.24))"

        samples = struct.unpack(f"<{samples_count}h", raw_bytes)
        chunk_size = max(1, s_rate // step_hz)

        # Merge adjacent energetic segments to keep the expression extremely compact and elegant
        terms: List[str] = []
        n_chunks = len(samples) // chunk_size

        cur_start: Optional[float] = None
        cur_end: Optional[float] = None
        cur_weight_sum = 0.0
        cur_count = 0

        for idx in range(n_chunks):
            t_start = round(idx / step_hz, 2)
            t_end = round((idx + 1) / step_hz, 2)
            in_speech = any(s <= t_start <= e or s <= t_end <= e for s, e in intervals)

            chunk = samples[idx * chunk_size : (idx + 1) * chunk_size]
            rms = math.sqrt(sum(s * s for s in chunk) / len(chunk)) if chunk else 0.0
            norm = max(0.0, min(1.0, (rms - 600.0) / 6800.0)) if in_speech else 0.0

            if norm >= 0.15:
                if cur_start is None:
                    cur_start = t_start
                    cur_end = t_end
                    cur_weight_sum = norm
                    cur_count = 1
                else:
                    cur_end = t_end
                    cur_weight_sum += norm
                    cur_count += 1
            else:
                if cur_start is not None:
                    avg_w = round(min(1.0, max(0.4, cur_weight_sum / max(1, cur_count))), 2)
                    terms.append(f"{avg_w}*between(t,{cur_start},{cur_end})")
                    cur_start = None
                    cur_end = None
                    cur_weight_sum = 0.0
                    cur_count = 0

        if cur_start is not None:
            avg_w = round(min(1.0, max(0.4, cur_weight_sum / max(1, cur_count))), 2)
            terms.append(f"{avg_w}*between(t,{cur_start},{cur_end})")

        if not terms:
            return "(0.5 + 0.3*sin(2*PI*t/0.24))"

        # Cap terms if too large
        if len(terms) > 60:
            terms = terms[:60]

        joined = " + ".join(terms)
        return f"({joined})"
    except Exception as e:
        print(f"  ⚠️ Audio RMS profile notice: {e}")
        return "(0.5 + 0.3*sin(2*PI*t/0.24))"
    finally:
        if wav_to_clean and wav_to_clean.exists():
            try:
                wav_to_clean.unlink()
            except Exception:
                pass


# Palettes matching exact visual references
ORB_PALETTES: Dict[str, Dict[str, Any]] = {
    "quantum": {
        "name": "Quantum Bio-Reactive",
        "description": "Vibrant cyan sphere, white/magenta core highlight, soft neon purple aura",
        "body_c0": "#00f0ff",     # Electric Cyan
        "body_c1": "#0284c7",     # Deep Cyan
        "body_c2": "#3b82f6",     # Royal Blue
        "body_c3": "#8a2be2",     # Deep Violet
        "body_c4": "#d946ef",     # Magenta Rim
        "body_c5": "#1e0836",     # Void Edge
        "spot1_core": "#ffffff",  # Incandescent White
        "spot1_glow": "#f472b6",  # Pink Flare
        "spot1_outer": "#c084fc", # Purple Edge
        "spot2_core": "#00f0ff",  # Secondary Cyan Flare
        "spot2_mid": "#0284c7",
        "spot2_outer": "#3b82f6",
        "aura_inner": "#a855f7",  # Neon Purple Aura
        "aura_mid": "#7c3aed",
        "aura_outer": "#3b82f6",
        "aura_bright": "#c084fc",
        "ring_stroke": "#c084fc",
        "rim_stroke": "#d946ef",
    },
    "solar": {
        "name": "Solar Bio-Reactive",
        "description": "Incandescent solar gold sphere, rose-coral flare highlights, radiant ruby/amber aura",
        "body_c0": "#ffea00",     # Electric Solar Gold
        "body_c1": "#ff9100",     # Amber Flare
        "body_c2": "#ff3d00",     # Fiery Orange-Red
        "body_c3": "#d50000",     # Deep Ruby Crimson
        "body_c4": "#c2185b",     # Magenta Rose Rim
        "body_c5": "#2a0010",     # Deep Cosmic Dark
        "spot1_core": "#ffffff",  # Pure Incandescent Core
        "spot1_glow": "#ff80ab",  # Neon Coral/Rose Flare
        "spot1_outer": "#ff4081", # Hot Pink / Solar Magenta Edge
        "spot2_core": "#ffea00",  # Electric Solar Gold Flare
        "spot2_mid": "#ff9100",   # Amber Mid
        "spot2_outer": "#ff3d00",  # Flame Edge
        "aura_inner": "#ff1744",  # Electric Crimson/Rose Aura
        "aura_mid": "#d50000",   # Ruby Deep Aura
        "aura_outer": "#ff6d00",  # Solar Amber Outer Aura
        "aura_bright": "#ff80ab", # Neon Rose Bright Core
        "ring_stroke": "#ffd54f", # Radiant Gold Ring
        "rim_stroke": "#ff4081",  # Hot Pink/Rose Rim Accent
    },
    "emerald": {
        "name": "Emerald Matrix Bio-Reactive",
        "description": "Cyber mint and neon jade sphere, electric cyan reflections, bio-aurora aura",
        "body_c0": "#00ff9d",     # Neon Mint
        "body_c1": "#00e676",     # Electric Green
        "body_c2": "#00b0ff",     # Cyan Blue
        "body_c3": "#004d40",     # Deep Emerald Teal
        "body_c4": "#1de9b6",     # Aquamarine Rim
        "body_c5": "#00140e",     # Matrix Void
        "spot1_core": "#ffffff",  # Incandescent White Core
        "spot1_glow": "#69f0ae",  # Neon Mint Flare
        "spot1_outer": "#00e5ff", # Cyan Edge
        "spot2_core": "#00ff9d",  # Secondary Mint Flare
        "spot2_mid": "#00b0ff",   # Cyan Mid
        "spot2_outer": "#004d40", # Deep Teal
        "aura_inner": "#00e676",  # Emerald Aura
        "aura_mid": "#00b0ff",   # Cyan Mid Aura
        "aura_outer": "#004d40",  # Teal Outer Aura
        "aura_bright": "#b9f6ca", # Soft Mint Core
        "ring_stroke": "#00ff9d", # Radiant Mint Ring
        "rim_stroke": "#69f0ae",  # Neon Green Rim Accent
    },
    "singularity": {
        "name": "Singularity Violet Bio-Reactive",
        "description": "Deep ultraviolet and void purple sphere, electric magenta flare and cosmic rift aura",
        "body_c0": "#d500f9",     # Electric Violet-Magenta
        "body_c1": "#7c4dff",     # Royal Purple
        "body_c2": "#304ffe",     # Deep Ultramarine
        "body_c3": "#651fff",     # Ultraviolet
        "body_c4": "#ea80fc",     # Neon Lilac Rim
        "body_c5": "#0c0214",     # Event Horizon Void
        "spot1_core": "#ffffff",  # Incandescent White Core
        "spot1_glow": "#e040fb",  # Neon Magenta Flare
        "spot1_outer": "#7c4dff", # Purple Edge
        "spot2_core": "#651fff",  # Secondary Ultraviolet Flare
        "spot2_mid": "#304ffe",   # Ultramarine Mid
        "spot2_outer": "#1a0033", # Void Edge
        "aura_inner": "#d500f9",  # Violet Aura
        "aura_mid": "#7c4dff",   # Purple Deep Aura
        "aura_outer": "#304ffe",  # Blue Outer Aura
        "aura_bright": "#ea80fc", # Lilac Bright Core
        "ring_stroke": "#ea80fc", # Radiant Lilac Ring
        "rim_stroke": "#d500f9",  # Violet Rim Accent
    },
    "supernova": {
        "name": "Supernova Crimson Bio-Reactive",
        "description": "Incandescent magma ruby sphere, molten gold corona, intense thermal explosion aura",
        "body_c0": "#ff1744",     # Electric Crimson
        "body_c1": "#ff5252",     # Plasma Red
        "body_c2": "#ff9100",     # Solar Amber
        "body_c3": "#b71c1c",     # Deep Blood Ruby
        "body_c4": "#ffd600",     # Gold Rim
        "body_c5": "#1f0003",     # Magma Void
        "spot1_core": "#ffffff",  # Pure White Core
        "spot1_glow": "#ffea00",  # Molten Gold Flare
        "spot1_outer": "#ff6d00", # Orange Edge
        "spot2_core": "#ff1744",  # Crimson Flare
        "spot2_mid": "#d50000",   # Ruby Mid
        "spot2_outer": "#3e0007", # Deep Dark Edge
        "aura_inner": "#ff1744",  # Crimson Aura
        "aura_mid": "#ff6d00",   # Amber Mid Aura
        "aura_outer": "#b71c1c",  # Blood Ruby Outer
        "aura_bright": "#ff8a80", # Radiant Coral Core
        "ring_stroke": "#ffd700", # Pure Gold Ring
        "rim_stroke": "#ff5252",  # Flame Rim Accent
    },
    "antimatter": {
        "name": "Antimatter Rift Bio-Reactive",
        "description": "Hyper-saturated fuchsia and electric azure sphere, high energy particle clash aura",
        "body_c0": "#ff007f",     # Neon Fuchsia
        "body_c1": "#e040fb",     # Electric Violet
        "body_c2": "#00e5ff",     # Electric Azure
        "body_c3": "#4a148c",     # Dark Indigo
        "body_c4": "#ff4081",     # Rose Neon Rim
        "body_c5": "#120024",     # Antimatter Void
        "spot1_core": "#ffffff",  # Pure White Core
        "spot1_glow": "#00e5ff",  # Azure Flare
        "spot1_outer": "#ff007f", # Fuchsia Edge
        "spot2_core": "#ff007f",  # Fuchsia Flare
        "spot2_mid": "#7c4dff",   # Purple Mid
        "spot2_outer": "#00e5ff", # Cyan Edge
        "aura_inner": "#ff007f",  # Fuchsia Aura
        "aura_mid": "#7c4dff",   # Purple Aura
        "aura_outer": "#00e5ff",  # Azure Outer Aura
        "aura_bright": "#ff80ab", # Hot Pink Core
        "ring_stroke": "#00e5ff", # Radiant Azure Ring
        "rim_stroke": "#ff007f",  # Fuchsia Rim Accent
    },
}


def generate_animated_orb_loop(
    palette_key: str = "quantum",
    mode: str = "talk",  # "talk", "idle", "close_talk", "close_idle"
    canvas_size: int = 500,
    fps: int = 30,
    loop_frames: int = 45,
    target_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> Path:
    """
    Generates a 45-frame (1.5s @ 30FPS) seamless, lightweight transparent QuickTime MOV loop (qtrle codec)
    containing a conscious bioluminescent sphere with controlled organic eye-gaze and conversational life.
    Modes:
      - 'talk': Side conversational angle (looking between rival and audience) with voice rings.
      - 'idle': Listening side angle (observing interlocutor with subtle ocular breathing).
      - 'close_talk': Direct front camera gaze addressing the audience with deep ocular focus.
      - 'close_idle': Front camera attentive presence.
    """
    palette_key = palette_key.lower().strip()
    if palette_key not in ORB_PALETTES:
        palette_key = "quantum"
    palette = ORB_PALETTES[palette_key]
    
    clean_mode = mode.lower().strip()
    is_close = "close" in clean_mode or "front" in clean_mode
    is_talk = "talk" in clean_mode or "active" in clean_mode or "speaking" in clean_mode
    
    dest_dir = target_dir or (Path(__file__).resolve().parent.parent / "assets" / "orbs")
    dest_dir.mkdir(parents=True, exist_ok=True)
    mode_slug = f"{'close_' if is_close else ''}{'talk' if is_talk else 'idle'}"
    mov_path = dest_dir / f"orb_loop_{palette_key}_{mode_slug}.mov"

    if not force_refresh and mov_path.exists() and mov_path.stat().st_size > 10000:
        return mov_path

    print(f"  🔮 Generando orbe consciente ('{palette_key}' | modo '{mode_slug}' | mirada fluida)...")

    frames_dir = dest_dir / f"_temp_frames_{palette_key}_{mode_slug}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    c = canvas_size // 2
    r_sphere_base = int(canvas_size * 0.27)
    r_aura_outer_base = int(canvas_size * 0.46)
    r_aura_inner_base = int(canvas_size * 0.36)

    # Intelligent Multi-Target Conversational Gaze Geometry:
    # Stable, elegant ocular presence in the loop; spatial shifts occur across the scene timeline in FFmpeg
    if is_close:
        # Frontal Camera Close-up: Center primary gaze focused on viewer
        gaze_primary_x = 0.0
        gaze_primary_y = -0.06
        opp_primary_x = 0.0
        opp_primary_y = 0.16
        body_base_cx = 50
        body_base_cy = 48
    elif "quantum" in palette_key:
        # Quantum (Left host): Attentive gaze oriented towards partner and audience
        gaze_primary_x = 0.12
        gaze_primary_y = -0.08
        opp_primary_x = -0.12
        opp_primary_y = 0.16
        body_base_cx = 52
        body_base_cy = 48
    elif "solar" in palette_key or "cosmic" in palette_key:
        # Solar (Right host): Attentive gaze oriented towards partner and audience
        gaze_primary_x = -0.12
        gaze_primary_y = -0.08
        opp_primary_x = 0.12
        opp_primary_y = 0.16
        body_base_cx = 48
        body_base_cy = 48
    else:
        gaze_primary_x = 0.0
        gaze_primary_y = -0.08
        opp_primary_x = 0.0
        opp_primary_y = 0.16
        body_base_cx = 50
        body_base_cy = 48

    try:
        for i in range(loop_frames):
            t = i / loop_frames
            tau = 2 * math.pi * t

            # Conscious Conversational Gaze Dynamics (Organic Sweet-Spot Harmonic Sweep):
            # Smooth conversational focus sweep between the interlocutor and the audience/camera.
            # Uses harmonic cubic ease (sin(tau) - 0.25*sin(3*tau)) for a natural hesitation at the extremes.
            smooth_sweep = math.sin(tau) - 0.20 * math.sin(3 * tau)
            smooth_vert = math.cos(tau) * 0.7 + math.sin(2 * tau) * 0.3

            if is_talk:
                # Active speaker: broad, confident conversational sweep looking at companion & audience
                gaze_shift_x = 0.085 * smooth_sweep
                gaze_shift_y = 0.040 * smooth_vert
                body_shift_x = 2.4 * math.sin(tau)
                body_shift_y = 1.4 * math.cos(tau)
            else:
                # Attentive listener: subtle, respectful micro-tracking and organic drift
                gaze_shift_x = 0.035 * smooth_sweep
                gaze_shift_y = 0.020 * smooth_vert
                body_shift_x = 1.2 * math.sin(tau)
                body_shift_y = 0.8 * math.cos(tau)

            curr_gaze_x = gaze_primary_x + gaze_shift_x
            curr_gaze_y = gaze_primary_y + gaze_shift_y
            curr_body_cx = body_base_cx + body_shift_x
            curr_body_cy = body_base_cy + body_shift_y

            # ═════════════════════════════════════════════════════════════════════
            # 🎥 VOLUMETRIC 3D PARTICLE & CINEMATIC CAMERA BOKEH SYSTEM:
            # Simulates true 3D orbital perspective with depth of field:
            # - Z < -0.05: Deep cosmic rear particles (behind the orb sphere)
            # - Z in [-0.05, 0.45]: Mid-plane stellar sparkles gliding across foreground
            # - Z > 0.45: Proximate camera bokeh (soft, out-of-focus, highly translucent disks)
            # ═════════════════════════════════════════════════════════════════════
            rear_particles_svg = []
            fore_particles_svg = []
            num_particles = 18 if is_talk else 12
            col_bright = palette["aura_bright"]
            col_core = palette["spot1_core"]
            col_glow = palette["spot1_glow"]

            is_solar = ("solar" in palette_key)

            # Unique pseudo-random deterministic seed offset per palette key
            # Ensures Solar, Quantum and other orbs have completely unique, non-identical organic orbits
            palette_seed_offset = 0.5829 if is_solar else 0.0

            for p_idx in range(num_particles):
                # Pseudo-chaotic phase offset using golden ratio to prevent periodic clustering / repetitive lines
                p_seed = (p_idx * 0.6180339887 + palette_seed_offset) % 1.0
                p_t = (t + (p_idx / num_particles) + 0.15 * math.sin(p_seed * 6.28)) % 1.0
                
                # 3D Depth coordinate z in [-1.0 (far rear), +1.0 (closest to lens)]
                # Non-linear z oscillation with harmonics to avoid pure symmetrical ping-pong
                z = math.cos(2 * math.pi * p_t + p_seed * 1.5)
                
                # 3D Camera Perspective Projection scale factor:
                # Far background: scale ~ 0.45; Near camera: scale ~ 1.25
                persp_scale = 1.0 / (1.55 - 0.70 * z)
                
                # 3D Inclined Spatial Orbital Spiral (Distinct inclination per particle):
                # Varied 3D plane tilts (azimuth & elevation) to break repetitive lines or circles
                tilt_factor = 0.55 + 0.45 * math.sin(p_idx * 1.37 + palette_seed_offset * 4.0)
                p_angle = (p_idx * 2.39996 + palette_seed_offset * 3.14) + 1.15 * math.sin(2 * math.pi * p_t + p_idx)
                orbit_rad_xy = (68.0 + 80.0 * (1.0 - 0.35 * (z ** 2))) * (0.85 + 0.30 * p_seed)
                
                px = c + (orbit_rad_xy * math.cos(p_angle)) * (persp_scale * 1.05)
                py = c + (orbit_rad_xy * math.sin(p_angle) * tilt_factor - 30.0 * z) * persp_scale
                
                # Optical lifecycle curve (bell curve):
                lifecycle = math.sin(math.pi * p_t)

                if z < -0.05:
                    # 🌑 DEEP REAR LAYER (Behind the orb silhouette):
                    p_size = (1.1 + 1.2 * p_t) * persp_scale * 1.4
                    p_alpha = max(0.0, min(0.65, lifecycle * (0.60 if is_talk else 0.40) * (0.5 + 0.5 * (z + 1.0))))
                    rear_particles_svg.append(
                        f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{p_size:.1f}" fill="{col_bright}" opacity="{p_alpha:.2f}" filter="url(#rearParticleBlur_{i})" />'
                    )
                else:
                    # 🌟 FOREGROUND LAYER (Crossing in front of the orb & surrounding atmosphere):
                    if z > 0.45:
                        # 🔮 PROXIMATE CINEMATIC BOKEH DISC (Closest to camera lens):
                        # Expansive, ultra-soft, and ethereal (low opacity) so the orb glows through unobstructed!
                        bokeh_radius = (7.0 + 12.0 * (z - 0.45) * 1.8) * persp_scale
                        bokeh_alpha = max(0.0, min(0.30, lifecycle * (0.28 if is_talk else 0.18) * (1.2 - z * 0.3)))
                        fore_particles_svg.append(
                            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{bokeh_radius:.1f}" fill="{col_glow}" opacity="{bokeh_alpha:.2f}" filter="url(#foreBokehBlur_{i})" />'
                        )
                    else:
                        # ✨ MID-FOREGROUND STELLAR SPARKLE (Crisp core with soft aura flare):
                        p_size = (2.0 + 2.6 * p_t) * persp_scale * 1.15
                        p_alpha = max(0.0, min(0.85, lifecycle * (0.80 if is_talk else 0.50)))
                        fore_particles_svg.append(
                            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{p_size:.1f}" fill="{col_core}" opacity="{p_alpha:.2f}" filter="url(#ringGlow_{i})" />'
                            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{max(0.7, p_size * 0.45):.1f}" fill="#ffffff" opacity="{p_alpha:.2f}" />'
                        )

            rear_particles_str = "\n  ".join(rear_particles_svg)
            fore_particles_str = "\n  ".join(fore_particles_svg)

            is_solar = ("solar" in palette_key)

            if is_solar:
                # ═════════════════════════════════════════════════════════════════════
                # ☀️ SOLAR: LIVING RADIANT STAR WITH STELLAR FLARE VOICE EMISSION
                # ═════════════════════════════════════════════════════════════════════
                if not is_talk:
                    # Solar Listening / Quiescent Solar Rhythm (Calm Fusion Core)
                    r_sphere = int(r_sphere_base + 4.0 * math.sin(tau))
                    r_aura_outer = int(r_aura_outer_base + 8.0 * math.sin(tau))
                    r_aura_inner = int(r_aura_inner_base + 6.0 * math.sin(tau))
                    r_ambient_spill = int((canvas_size * 0.46) + 8.0 * math.sin(tau))

                    # Calibrated Calm Fusion Heart (Centered)
                    mouth_rx = int(r_sphere * (0.34 + 0.04 * math.sin(tau)))
                    mouth_ry = int(r_sphere * (0.34 + 0.04 * math.sin(tau)))
                    mouth_core_r = int(mouth_rx * 0.45)
                    beam_opacity = 0.35

                    # Coronal Loops (Soft Ambient Solar Radiation)
                    corona1_r = int(r_sphere + 18 + 5.0 * math.sin(tau + 0.4))
                    corona1_glow = corona1_r + 6
                    corona2_r = int(r_sphere + 38 + 4.0 * math.cos(tau))

                    rings_svg = f"""
  <!-- Solar Quiescent Coronal Loops -->
  <circle cx="{c}" cy="{c}" r="{corona1_glow}" fill="none" stroke="{palette['aura_inner']}" stroke-width="5.0" opacity="0.45" filter="url(#ringGlow_{i})" />
  <circle cx="{c}" cy="{c}" r="{corona1_r}" fill="none" stroke="{palette['ring_stroke']}" stroke-width="2.2" opacity="0.75" />
  <circle cx="{c}" cy="{c}" r="{corona2_r}" fill="none" stroke="{palette['aura_bright']}" stroke-width="1.6" stroke-dasharray="24 18 36 18" stroke-dashoffset="{int(i * 4)}" opacity="0.50" />
"""
                else:
                    # Solar Active Speaking (Dynamic Thermal Flare "Mouth" & Shockwave Waves)
                    r_sphere = int(r_sphere_base + 8.5 * math.sin(tau) + 3.0 * math.sin(2 * tau))
                    r_aura_outer = int(r_aura_outer_base + 18.0 * math.sin(tau))
                    r_aura_inner = int(r_aura_inner_base + 14.0 * math.sin(tau))
                    r_ambient_spill = int((canvas_size * 0.50) + 16.0 * math.sin(tau))

                    # Dynamic Solar Flare "Mouth" (Vertical & Radial Expansion in Sync with Speech)
                    mouth_rx = int(r_sphere * (0.38 + 0.14 * math.cos(2 * tau) + 0.06 * math.sin(tau)))
                    mouth_ry = int(r_sphere * (0.48 + 0.26 * abs(math.sin(2 * tau)) + 0.10 * math.cos(tau)))
                    mouth_core_r = int(mouth_rx * 0.50 + 2.0 * abs(math.sin(2 * tau)))
                    beam_opacity = min(0.95, 0.45 + 0.50 * abs(math.sin(2 * tau)))

                    # Dynamic Eruptive Coronal Shockwaves & Radiant Arcs
                    flare1_r = int(r_sphere + 18 + 12.0 * math.sin(tau) + 5.0 * math.sin(2 * tau))
                    flare1_glow = flare1_r + 8
                    flare2_r = int(r_sphere + 42 + 16.0 * math.sin(tau + 1.2) + 6.0 * math.cos(2 * tau))
                    flare2_glow = flare2_r + 10
                    flare3_r = int(r_sphere + 66 + 9.0 * math.cos(tau + 2.0))

                    rings_svg = f"""
  <!-- Solar Shockwave Coronal Radiation Waves -->
  <circle cx="{c}" cy="{c}" r="{flare3_r}" fill="none" stroke="{palette['aura_bright']}" stroke-width="2.5" stroke-dasharray="32 16 48 16" stroke-dashoffset="{int(i * 8)}" opacity="0.80" />
  <circle cx="{c}" cy="{c}" r="{flare2_glow}" fill="none" stroke="{palette['aura_inner']}" stroke-width="6.5" opacity="0.65" filter="url(#ringGlow_{i})" />
  <circle cx="{c}" cy="{c}" r="{flare2_r}" fill="none" stroke="{palette['ring_stroke']}" stroke-width="2.2" opacity="0.85" />
  <circle cx="{c}" cy="{c}" r="{flare1_glow}" fill="none" stroke="{palette['aura_inner']}" stroke-width="9.0" opacity="0.90" filter="url(#ringGlow_{i})" />
  <circle cx="{c}" cy="{c}" r="{flare1_r}" fill="none" stroke="{palette['ring_stroke']}" stroke-width="3.2" opacity="0.98" />
  <circle cx="{c}" cy="{c}" r="{flare1_r - 1}" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.85" />
"""

                # Solar SVG Construction: Centered Fusion Plasma Body + Solar Flare Mouth
                beam_w = int(r_sphere * 0.82)
                beam_h = int(r_sphere * 0.24)

                spot1_x = int(c + (r_sphere * curr_gaze_x))
                spot1_y = int(c + (r_sphere * curr_gaze_y))
                body_cx_pct = int(curr_body_cx)
                body_cy_pct = int(curr_body_cy)

                svg = f"""<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="ambientSpillBlur_{i}" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="40" />
    </filter>
    <filter id="auraGlowDeep_{i}" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="22" />
    </filter>
    <filter id="coreBlur_{i}" x="-25%" y="-25%" width="150%" height="150%">
      <feGaussianBlur stdDeviation="8" />
    </filter>
    <filter id="ringGlow_{i}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="7" />
    </filter>
    <filter id="rearParticleBlur_{i}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="1.8" />
    </filter>
    <filter id="foreBokehBlur_{i}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="9.0" />
    </filter>

    <clipPath id="sphereClip_{i}">
      <circle cx="{c}" cy="{c}" r="{r_sphere}" />
    </clipPath>

    <!-- Environmental Thermal Ambient Spill -->
    <radialGradient id="ambientSpill_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['spot1_glow']}" stop-opacity="0.95" />
      <stop offset="35%" stop-color="{palette['aura_inner']}" stop-opacity="0.70" />
      <stop offset="70%" stop-color="{palette['aura_outer']}" stop-opacity="0.30" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <!-- Coronal Outer Neon Aura -->
    <radialGradient id="outerAuraDeep_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['aura_inner']}" stop-opacity="0.95" />
      <stop offset="40%" stop-color="{palette['aura_mid']}" stop-opacity="0.70" />
      <stop offset="75%" stop-color="{palette['aura_outer']}" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <radialGradient id="innerAuraBright_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['aura_bright']}" stop-opacity="0.90" />
      <stop offset="55%" stop-color="{palette['aura_inner']}" stop-opacity="0.55" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <!-- Concentric Star Plasma Body Gradient (Pure Solar Fusion) -->
    <radialGradient id="solarBody_{i}" cx="{body_cx_pct}%" cy="{body_cy_pct}%" r="55%">
      <stop offset="0%" stop-color="{palette['body_c0']}" />
      <stop offset="20%" stop-color="{palette['body_c1']}" />
      <stop offset="45%" stop-color="{palette['body_c2']}" />
      <stop offset="70%" stop-color="{palette['body_c3']}" />
      <stop offset="88%" stop-color="{palette['body_c4']}" />
      <stop offset="100%" stop-color="{palette['body_c5']}" />
    </radialGradient>

    <!-- Solar Flare Mouth Radiant Gradient -->
    <radialGradient id="solarMouth_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['spot1_core']}" stop-opacity="1.0" />
      <stop offset="35%" stop-color="{palette['spot1_glow']}" stop-opacity="0.95" />
      <stop offset="70%" stop-color="{palette['spot1_outer']}" stop-opacity="0.60" />
      <stop offset="100%" stop-color="{palette['body_c3']}" stop-opacity="0.0" />
    </radialGradient>
  </defs>

  <!-- 0. Environmental Ambient Illumination -->
  <circle cx="{c}" cy="{c}" r="{canvas_size // 2 - 10}" fill="url(#ambientSpill_{i})" filter="url(#ambientSpillBlur_{i})" />

  <!-- 1. Coronal Atmospheric Bloom -->
  <circle cx="{c}" cy="{c}" r="{r_aura_outer}" fill="url(#outerAuraDeep_{i})" filter="url(#auraGlowDeep_{i})" />
  <circle cx="{c}" cy="{c}" r="{r_aura_inner}" fill="url(#innerAuraBright_{i})" filter="url(#auraGlowDeep_{i})" />

  <!-- 1.5. Deep Cosmic Rear Particles (Emitted from behind the celestial sphere) -->
  <g id="rear_stellar_stream_{i}">
  {rear_particles_str}
  </g>

  <!-- 2. Coronal Shockwaves & Eruptive Flares -->
  {rings_svg}

  <!-- 3. Living Sun Plasma Sphere -->
  <circle cx="{c}" cy="{c}" r="{r_sphere}" fill="url(#solarBody_{i})" />

  <!-- 4. Solar Flare "Mouth" (Incandescent Fusion Speech Core) -->
  <g clip-path="url(#sphereClip_{i})">
    <!-- Horizontal Solar Ejection Flare Beam -->
    <ellipse cx="{spot1_x}" cy="{spot1_y}" rx="{beam_w}" ry="{beam_h}" fill="{palette['spot1_glow']}" opacity="{beam_opacity}" filter="url(#coreBlur_{i})" />

    <!-- Radiant Solar Mouth Core (Pulsing Acoustic Fusion Center) -->
    <ellipse cx="{spot1_x}" cy="{spot1_y}" rx="{mouth_rx}" ry="{mouth_ry}" fill="url(#solarMouth_{i})" filter="url(#coreBlur_{i})" />
    <circle cx="{spot1_x}" cy="{spot1_y}" r="{mouth_core_r}" fill="{palette['spot1_core']}" opacity="0.98" filter="url(#coreBlur_{i})" />

    <!-- Thermal Subsurface Corona Rim -->
    <circle cx="{c}" cy="{c}" r="{r_sphere - 3}" fill="none" stroke="{palette['rim_stroke']}" stroke-width="3.5" opacity="0.60" filter="url(#coreBlur_{i})" />
  </g>

  <!-- 5. Inner Concentric Rim Light -->
  <circle cx="{c}" cy="{c}" r="{r_sphere - 2}" fill="none" stroke="{palette['aura_inner']}" stroke-width="2.5" opacity="0.75" />

  <!-- 6. Foreground Stellar Bokeh Flares (Dancing around the outer corona, never piercing the core) -->
  <g id="fore_stellar_bokeh_{i}">
  {fore_particles_str}
  </g>
</svg>"""

            else:
                # ═════════════════════════════════════════════════════════════════════
                # 🌌 QUANTUM (AND STANDARD): CONSCIOUS BIO-REACTIVE ORB WITH LIVING GAZE
                # ═════════════════════════════════════════════════════════════════════
                if not is_talk:
                    # LISTENING / ATTENTIVE LIVING PRESENCE
                    # Breathing rhythm with steady attentive focus
                    r_sphere = int(r_sphere_base + 3.5 * math.sin(tau))
                    r_aura_outer = int(r_aura_outer_base + 6.0 * math.sin(tau))
                    r_aura_inner = int(r_aura_inner_base + 4.5 * math.sin(tau))
                    r_ambient_spill = int((canvas_size * 0.44) + 6.0 * math.sin(tau))

                    spot1_x = int(c + (r_sphere * curr_gaze_x))
                    spot1_y = int(c + (r_sphere * curr_gaze_y))
                    spot1_rx = int(r_sphere * 0.48 + 2.0 * math.sin(tau))
                    spot1_ry = int(r_sphere * 0.44 + 1.5 * math.cos(tau))

                    spot2_x = int(c + (r_sphere * opp_primary_x))
                    spot2_y = int(c + (r_sphere * opp_primary_y))
                    spot2_rx = int(r_sphere * 0.40 + 1.5 * math.sin(tau))
                    spot2_ry = int(r_sphere * 0.36 + 1.5 * math.cos(tau))

                    body_cx_pct = int(curr_body_cx)
                    body_cy_pct = int(curr_body_cy)

                    calm_ring_r = int(r_sphere + 18 + 4.0 * math.sin(tau + 0.5))
                    calm_ring_glow = calm_ring_r + 5
                    calm_ring2_r = int(r_sphere + 36 + 3.0 * math.cos(tau))
                    orbit_dash_offset = int(i * 6)

                    rings_svg = f"""
  <!-- Listening Harmonic Ring (Soft Glow Resonance) -->
  <circle cx="{c}" cy="{c}" r="{calm_ring_glow}" fill="none" stroke="{palette['aura_inner']}" stroke-width="4.0" opacity="0.50" filter="url(#ringGlow_{i})" />
  <circle cx="{c}" cy="{c}" r="{calm_ring_r}" fill="none" stroke="{palette['ring_stroke']}" stroke-width="1.8" opacity="0.75" />

  <!-- Outer Orbital Energy Arc -->
  <circle cx="{c}" cy="{c}" r="{calm_ring2_r}" fill="none" stroke="{palette['aura_bright']}" stroke-width="1.4" stroke-dasharray="14 24 36 24" stroke-dashoffset="{orbit_dash_offset}" opacity="0.45" />
"""
                else:
                    # ACTIVE SPEAKING ORB (Dynamic High-Energy Acoustic Resonance Rings)
                    r_sphere = int(r_sphere_base + 7.0 * math.sin(tau) + 2.5 * math.sin(2 * tau))
                    r_aura_outer = int(r_aura_outer_base + 14.0 * math.sin(tau))
                    r_aura_inner = int(r_aura_inner_base + 10.0 * math.sin(tau))
                    r_ambient_spill = int((canvas_size * 0.48) + 12.0 * math.sin(tau))

                    spot1_x = int(c + (r_sphere * curr_gaze_x))
                    spot1_y = int(c + (r_sphere * curr_gaze_y))
                    spot1_rx = int(r_sphere * 0.54 + 3.5 * math.sin(tau))
                    spot1_ry = int(r_sphere * 0.50 + 2.5 * math.cos(tau))

                    spot2_x = int(c + (r_sphere * opp_primary_x))
                    spot2_y = int(c + (r_sphere * opp_primary_y))
                    spot2_rx = int(r_sphere * 0.46 + 2.5 * math.sin(tau))
                    spot2_ry = int(r_sphere * 0.42 + 2.0 * math.cos(tau))

                    body_cx_pct = int(curr_body_cx)
                    body_cy_pct = int(curr_body_cy)

                    # Dynamic Wave 1: Primary Voice Expansion Ring
                    ring1_r = int(r_sphere + 16 + 9.0 * math.sin(tau) + 4.0 * math.sin(2 * tau))
                    ring1_glow = ring1_r + 6

                    # Dynamic Wave 2: Outer Acoustic Resonance Wave
                    ring2_r = int(r_sphere + 36 + 14.0 * math.sin(tau + 1.2) + 5.0 * math.cos(2 * tau))
                    ring2_glow = ring2_r + 8

                    # Dynamic Wave 3: Rotating Orbital Light Arc
                    ring3_r = int(r_sphere + 58 + 8.0 * math.cos(tau + 2.0))
                    orbit_dash_offset = int(i * 12)

                    rings_svg = f"""
  <!-- Ring 3: Rotating Kinetic Energy Halo -->
  <circle cx="{c}" cy="{c}" r="{ring3_r}" fill="none" stroke="{palette['aura_bright']}" stroke-width="2.2" stroke-dasharray="18 22 45 22" stroke-dashoffset="{orbit_dash_offset}" opacity="0.75" />

  <!-- Ring 2: Expanding Outer Resonance Wave -->
  <circle cx="{c}" cy="{c}" r="{ring2_glow}" fill="none" stroke="{palette['aura_inner']}" stroke-width="5.0" opacity="0.60" filter="url(#ringGlow_{i})" />
  <circle cx="{c}" cy="{c}" r="{ring2_r}" fill="none" stroke="{palette['ring_stroke']}" stroke-width="1.8" opacity="0.80" />

  <!-- Ring 1: High-Power Radiant Voice Harmonic Core Ring -->
  <circle cx="{c}" cy="{c}" r="{ring1_glow}" fill="none" stroke="{palette['aura_inner']}" stroke-width="7.5" opacity="0.85" filter="url(#ringGlow_{i})" />
  <circle cx="{c}" cy="{c}" r="{ring1_r}" fill="none" stroke="{palette['ring_stroke']}" stroke-width="2.6" opacity="0.98" />
  <circle cx="{c}" cy="{c}" r="{ring1_r - 1}" fill="none" stroke="#ffffff" stroke-width="1.0" opacity="0.80" />
"""

                svg = f"""<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Streamlined High-Performance Gaussian Filters -->
    <filter id="ambientSpillBlur_{i}" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="40" />
    </filter>
    <filter id="auraGlowDeep_{i}" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="22" />
    </filter>
    <filter id="coreBlur_{i}" x="-25%" y="-25%" width="150%" height="150%">
      <feGaussianBlur stdDeviation="9" />
    </filter>
    <filter id="ringGlow_{i}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="7" />
    </filter>
    <filter id="rearParticleBlur_{i}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="1.8" />
    </filter>
    <filter id="foreBokehBlur_{i}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="9.0" />
    </filter>

    <clipPath id="sphereClip_{i}">
      <circle cx="{c}" cy="{c}" r="{r_sphere}" />
    </clipPath>

    <!-- Environmental Ambient Light Spill -->
    <radialGradient id="ambientSpill_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['spot1_glow']}" stop-opacity="0.90" />
      <stop offset="30%" stop-color="{palette['aura_inner']}" stop-opacity="0.65" />
      <stop offset="65%" stop-color="{palette['aura_outer']}" stop-opacity="0.30" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <!-- Expansive Atmospheric Neon Aura -->
    <radialGradient id="outerAuraDeep_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['aura_inner']}" stop-opacity="0.90" />
      <stop offset="40%" stop-color="{palette['aura_mid']}" stop-opacity="0.65" />
      <stop offset="75%" stop-color="{palette['aura_outer']}" stop-opacity="0.30" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <radialGradient id="innerAuraBright_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['aura_bright']}" stop-opacity="0.85" />
      <stop offset="50%" stop-color="{palette['aura_inner']}" stop-opacity="0.50" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <!-- Multi-Spectral Chromatic Dynamic Plasma Body Gradient -->
    <radialGradient id="sphereBody_{i}" cx="{body_cx_pct}%" cy="{body_cy_pct}%" r="62%">
      <stop offset="0%" stop-color="{palette['body_c0']}" />
      <stop offset="22%" stop-color="{palette['body_c1']}" />
      <stop offset="48%" stop-color="{palette['body_c2']}" />
      <stop offset="72%" stop-color="{palette['body_c3']}" />
      <stop offset="88%" stop-color="{palette['body_c4']}" />
      <stop offset="100%" stop-color="{palette['body_c5']}" />
    </radialGradient>

    <!-- Primary Off-Center Light Spot -->
    <radialGradient id="primarySpot_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['spot1_core']}" stop-opacity="1.0" />
      <stop offset="30%" stop-color="{palette['spot1_glow']}" stop-opacity="0.90" />
      <stop offset="65%" stop-color="{palette['spot1_outer']}" stop-opacity="0.55" />
      <stop offset="100%" stop-color="{palette['body_c3']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- Secondary Counter-Tone Light Spot -->
    <radialGradient id="secondarySpot_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['spot2_core']}" stop-opacity="0.85" />
      <stop offset="45%" stop-color="{palette['spot2_mid']}" stop-opacity="0.55" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>
  </defs>

  <!-- 0. Environmental Ambient Illumination -->
  <circle cx="{c}" cy="{c}" r="{canvas_size // 2 - 10}" fill="url(#ambientSpill_{i})" filter="url(#ambientSpillBlur_{i})" />

  <!-- 1. Atmospheric Neon Bloom -->
  <circle cx="{c}" cy="{c}" r="{r_aura_outer}" fill="url(#outerAuraDeep_{i})" filter="url(#auraGlowDeep_{i})" />
  <circle cx="{c}" cy="{c}" r="{r_aura_inner}" fill="url(#innerAuraBright_{i})" filter="url(#auraGlowDeep_{i})" />

  <!-- 1.5. Deep Cosmic Rear Particles (Emitted from behind the celestial sphere) -->
  <g id="rear_quantum_stream_{i}">
  {rear_particles_str}
  </g>

  <!-- 2. Concentric Surrounding Acoustic Shockwave Rings -->
  {rings_svg}

  <!-- 3. Sphere Body -->
  <circle cx="{c}" cy="{c}" r="{r_sphere}" fill="url(#sphereBody_{i})" />

  <!-- 4. Multi-Spectral Interior Light Layers -->
  <g clip-path="url(#sphereClip_{i})">
    <!-- Secondary Counter-Tone Flare (Bottom-Right) -->
    <ellipse cx="{spot2_x}" cy="{spot2_y}" rx="{spot2_rx}" ry="{spot2_ry}" fill="url(#secondarySpot_{i})" filter="url(#coreBlur_{i})" />

    <!-- Primary Incandescent Flare (Top-Left) -->
    <ellipse cx="{spot1_x}" cy="{spot1_y}" rx="{spot1_rx}" ry="{spot1_ry}" fill="url(#primarySpot_{i})" filter="url(#coreBlur_{i})" />
    <circle cx="{spot1_x}" cy="{spot1_y}" r="{int(spot1_rx * 0.45)}" fill="{palette['spot1_core']}" opacity="0.95" filter="url(#coreBlur_{i})" />

    <!-- Subsurface Rim Accent -->
    <circle cx="{c}" cy="{c}" r="{r_sphere - 3}" fill="none" stroke="{palette['rim_stroke']}" stroke-width="3" opacity="0.50" filter="url(#coreBlur_{i})" />
  </g>

  <!-- 5. Inner Concentric Rim Light -->
  <circle cx="{c}" cy="{c}" r="{r_sphere - 2}" fill="none" stroke="{palette['aura_inner']}" stroke-width="2.5" opacity="0.70" />

  <!-- 6. Foreground Stellar Bokeh Flares (Dancing around the outer corona, never piercing the core) -->
  <g id="fore_quantum_bokeh_{i}">
  {fore_particles_str}
  </g>
</svg>"""
            (frames_dir / f"frame_{i:03d}.svg").write_text(svg, encoding="utf-8")

        temp_mov = frames_dir / f"orb_{palette_key}_{mode}.mov"
        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%03d.svg"),
            "-c:v", "qtrle",
            str(temp_mov)
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        temp_mov.replace(mov_path)

        # Also maintain general loop link if default
        if mode == "talk":
            general_path = dest_dir / f"orb_loop_{palette_key}.mov"
            try:
                shutil.copyfile(mov_path, general_path)
            except Exception:
                pass

        return mov_path
    finally:
        if frames_dir.exists():
            shutil.rmtree(frames_dir, ignore_errors=True)


def get_or_create_orb_asset(
    palette: str = "quantum",
    mode: str = "talk",
    target_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> Path:
    """Retrieves or generates a transparent QuickTime MOV loop for the AI Presenter entity in talk or idle mode."""
    return generate_animated_orb_loop(
        palette_key=palette,
        mode=mode,
        canvas_size=500,
        fps=30,
        loop_frames=45,
        target_dir=target_dir,
        force_refresh=force_refresh
    )


def get_or_create_shockwave_asset(
    color_hex: str = "#00f0ff",
    duration_sec: float = 0.45,
    canvas_size: int = 500,
    fps: int = 30,
    target_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> Path:
    """
    Renders an ephemeral expanding shockwave burst MOV (QuickTime qtrle with alpha).
    Fires at orb singularity ignition with a luminous expanding shockwave ring and incandescent center flare.
    """
    dest_dir = target_dir or (Path(__file__).resolve().parent.parent / "assets" / "orbs")
    dest_dir.mkdir(parents=True, exist_ok=True)
    slug = color_hex.replace("#", "").lower()[:6]
    mov_path = dest_dir / f"shockwave_{slug}_{int(duration_sec * 1000)}ms.mov"

    if not force_refresh and mov_path.exists() and mov_path.stat().st_size > 5000:
        return mov_path

    frames_dir = dest_dir / f"_temp_sw_{slug}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    n_frames = max(10, int(duration_sec * fps))
    c = canvas_size // 2

    try:
        for i in range(n_frames):
            p = i / max(1, n_frames - 1)
            # Cubic ease-out: explosive expansion at start, decelerating gracefully
            r_prog = 1.0 - (1.0 - p) ** 3
            r = 28.0 + r_prog * 210.0
            sw = max(1.0, 7.5 * (1.0 - p * 0.70))
            alpha = max(0.0, ((1.0 - p) ** 1.5) * 0.95)
            core_alpha = max(0.0, (1.0 - p / 0.28) * 0.95) if p < 0.28 else 0.0
            core_r = max(2.0, 26.0 * (1.0 - p / 0.28))

            svg = f"""<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="sw_glow_{i}" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="8" />
    </filter>
  </defs>
  <!-- Incandescent white ignition pinpoint flare -->
  <circle cx="{c}" cy="{c}" r="{core_r:.1f}" fill="#ffffff" opacity="{core_alpha:.2f}" filter="url(#sw_glow_{i})" />
  <!-- Radiant chromatic shockwave glow ring -->
  <circle cx="{c}" cy="{c}" r="{r:.1f}" fill="none" stroke="{color_hex}" stroke-width="{sw * 2.2:.1f}" opacity="{alpha * 0.65:.2f}" filter="url(#sw_glow_{i})" />
  <!-- Crisp inner energy rim -->
  <circle cx="{c}" cy="{c}" r="{r:.1f}" fill="none" stroke="#ffffff" stroke-width="{sw:.1f}" opacity="{alpha * 0.90:.2f}" />
</svg>"""
            (frames_dir / f"sw_{i:03d}.svg").write_text(svg, encoding="utf-8")

        temp_mov = frames_dir / f"_sw_{slug}.mov"
        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(fps),
            "-i", str(frames_dir / "sw_%03d.svg"),
            "-c:v", "qtrle",
            str(temp_mov)
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        temp_mov.replace(mov_path)
        return mov_path
    finally:
        if frames_dir.exists():
            shutil.rmtree(frames_dir, ignore_errors=True)


def synthesize_plasma_arc_sfx(out_path: Path):
    """Generates an elegant, high-frequency ionized cosmic chime/hum stinger for the plasma bridge."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sample_rate = 44100
    duration = 0.75
    n_samples = int(sample_rate * duration)
    frames = bytearray()

    for i in range(n_samples):
        t = i / sample_rate
        # Envelope: 80ms smooth attack, gentle exponential decay
        if t < 0.08:
            env = (t / 0.08) ** 2
        else:
            env = math.exp(-(t - 0.08) * 4.5)

        # Ionized harmonic frequency glide
        f0 = 260.0 + 80.0 * math.sin(math.pi * min(1.0, t / 0.4))
        sig1 = math.sin(2 * math.pi * f0 * t) * 0.40
        sig2 = math.sin(2 * math.pi * f0 * 2.0 * t + 0.5) * 0.22
        sig3 = math.sin(2 * math.pi * f0 * 3.0 * t + 1.0) * 0.12
        shimmer = math.sin(2 * math.pi * 18.0 * t) * 0.10 * sig1

        sample_val = int(32767 * max(-1.0, min(1.0, (sig1 + sig2 + sig3 + shimmer) * env * 0.35)))
        frames.extend(struct.pack('<h', sample_val))

    with wave.open(str(out_path), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(frames)


def get_or_create_plasma_bridge_asset(
    color_a: str = "#00f0ff",
    color_b: str = "#ffea00",
    canvas_w: int = 800,
    canvas_h: int = 360,
    fps: int = 30,
    loop_frames: int = 45,
    target_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> Path:
    """
    Renders an ethereal, high-end quantum-solar magnetic plasma bridge (QuickTime MOV with ARGB alpha).
    Features:
      - Soft atmospheric vacuum glow ribbon bridging Quantum and Solar.
      - Dual braided counter-oscillating harmonic filaments (Lissajous standing waves).
      - Central Lagrange gravitational equilibrium focal node.
      - Luminous bidirectional energy packets (photonic quanta) flowing across the connection.
      - Seamless 45-frame (1.5s @ 30fps) loop for zero overhead.
    """
    dest_dir = target_dir or (Path(__file__).resolve().parent.parent / "assets" / "orbs")
    dest_dir.mkdir(parents=True, exist_ok=True)
    slug_a = color_a.replace("#", "").lower()[:6]
    slug_b = color_b.replace("#", "").lower()[:6]
    mov_path = dest_dir / f"plasma_bridge_{slug_a}_{slug_b}_800x360.mov"

    if not force_refresh and mov_path.exists() and mov_path.stat().st_size > 10000:
        return mov_path

    frames_dir = dest_dir / f"_temp_bridge_{slug_a}_{slug_b}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    w, h = canvas_w, canvas_h
    # Anchor coordinates relative to the 800x360 box (which is overlaid at x=140, y=560)
    x1, y1 = 130, 170
    x2, y2 = 642, 188
    dx = x2 - x1
    n_points = 36

    try:
        for i in range(loop_frames):
            t_norm = i / loop_frames
            tau = 2 * math.pi * t_norm

            pts_main = []
            pts_twin = []
            pts_ribbon_top = []
            pts_ribbon_bot = []

            for k in range(n_points + 1):
                p = k / n_points
                px = x1 + dx * p
                base_y = y1 + (y2 - y1) * p
                env = math.sin(math.pi * p) ** 0.85

                w1 = math.sin(2 * math.pi * p * 1.5 + tau) * 15.0 * env
                w2 = math.cos(2 * math.pi * p * 3.0 - tau * 1.2) * 6.5 * env
                pts_main.append(f"{px:.1f},{base_y + w1 + w2:.1f}")

                tw1 = math.sin(2 * math.pi * p * 2.2 - tau * 1.1 + 2.1) * 12.0 * env
                tw2 = math.cos(2 * math.pi * p * 3.6 + tau * 0.9) * 5.0 * env
                pts_twin.append(f"{px:.1f},{base_y + tw1 + tw2:.1f}")

                rw = (22.0 + 8.0 * math.sin(tau + p * math.pi)) * env
                pts_ribbon_top.append(f"{px:.1f},{base_y - rw:.1f}")
                pts_ribbon_bot.insert(0, f"{px:.1f},{base_y + rw:.1f}")

            path_main = "M " + " L ".join(pts_main)
            path_twin = "M " + " L ".join(pts_twin)
            path_ribbon = "M " + " L ".join(pts_ribbon_top) + " L " + " L ".join(pts_ribbon_bot) + " Z"

            quanta_svg = []
            for q_idx in range(4):
                if q_idx % 2 == 0:
                    q_p = (t_norm * 1.2 + (q_idx / 4.0)) % 1.0
                    q_col = "#ffffff"
                else:
                    q_p = (1.0 - (t_norm * 1.2 + (q_idx / 4.0))) % 1.0
                    q_col = "#fef08a" if q_p > 0.5 else "#a5f3fc"

                q_px = x1 + dx * q_p
                q_env = math.sin(math.pi * q_p) ** 0.85
                q_base_y = y1 + (y2 - y1) * q_p
                q_w = (math.sin(2 * math.pi * q_p * 1.5 + tau) * 15.0 + math.cos(2 * math.pi * q_p * 3.0 - tau * 1.2) * 6.5) * q_env
                q_py = q_base_y + q_w
                q_r = 3.2 + 2.2 * q_env
                q_a = 0.90 * q_env
                quanta_svg.append(f'<circle cx="{q_px:.1f}" cy="{q_py:.1f}" r="{q_r:.1f}" fill="{q_col}" opacity="{q_a:.2f}" filter="url(#pulseGlow_{i})"/>')

            cx_lag = (x1 + x2) // 2
            cy_lag = (y1 + y2) // 2
            lag_pulse = 1.0 + 0.18 * math.sin(tau * 2.0)

            svg = f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="plasmaGrad_{i}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{color_a}" stop-opacity="0.0" />
      <stop offset="10%" stop-color="{color_a}" stop-opacity="0.80" />
      <stop offset="36%" stop-color="#818cf8" stop-opacity="0.85" />
      <stop offset="50%" stop-color="#ffffff" stop-opacity="1.0" />
      <stop offset="64%" stop-color="#f59e0b" stop-opacity="0.85" />
      <stop offset="90%" stop-color="{color_b}" stop-opacity="0.80" />
      <stop offset="100%" stop-color="{color_b}" stop-opacity="0.0" />
    </linearGradient>

    <linearGradient id="ribbonGrad_{i}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{color_a}" stop-opacity="0.0" />
      <stop offset="20%" stop-color="{color_a}" stop-opacity="0.22" />
      <stop offset="50%" stop-color="#e0e7ff" stop-opacity="0.32" />
      <stop offset="80%" stop-color="{color_b}" stop-opacity="0.22" />
      <stop offset="100%" stop-color="{color_b}" stop-opacity="0.0" />
    </linearGradient>

    <radialGradient id="lagrangeCore_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95" />
      <stop offset="35%" stop-color="#c7d2fe" stop-opacity="0.65" />
      <stop offset="70%" stop-color="#818cf8" stop-opacity="0.25" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <filter id="deepBloom_{i}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="14" />
    </filter>
    <filter id="midGlow_{i}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="5.5" />
    </filter>
    <filter id="pulseGlow_{i}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3.5" />
    </filter>
  </defs>

  <!-- 1. Ambient Cosmic Plasma Ribbon (Volumetric atmospheric ionization) -->
  <path d="{path_ribbon}" fill="url(#ribbonGrad_{i})" filter="url(#deepBloom_{i})" />

  <!-- 2. Counter-Oscillating Twin Harmonic Tendril (Braided magnetic streamline) -->
  <path d="{path_twin}" fill="none" stroke="url(#plasmaGrad_{i})" stroke-width="1.8" stroke-dasharray="14 6" opacity="0.72" filter="url(#midGlow_{i})" />

  <!-- 3. Primary Plasma Bridge (High-energy ion stream with bloom) -->
  <path d="{path_main}" fill="none" stroke="url(#plasmaGrad_{i})" stroke-width="6.5" opacity="0.48" filter="url(#midGlow_{i})" />
  <path d="{path_main}" fill="none" stroke="url(#plasmaGrad_{i})" stroke-width="2.6" opacity="0.92" />
  <path d="{path_main}" fill="none" stroke="#ffffff" stroke-width="1.1" opacity="0.95" />

  <!-- 4. Central Lagrange Equilibrium Node (Gravitational nexus) -->
  <circle cx="{cx_lag}" cy="{cy_lag}" r="{14 * lag_pulse:.1f}" fill="url(#lagrangeCore_{i})" filter="url(#pulseGlow_{i})" />
  <circle cx="{cx_lag}" cy="{cy_lag}" r="{3.5 * lag_pulse:.1f}" fill="#ffffff" opacity="0.98" />
  <line x1="{cx_lag - 16 * lag_pulse:.1f}" y1="{cy_lag}" x2="{cx_lag + 16 * lag_pulse:.1f}" y2="{cy_lag}" stroke="#ffffff" stroke-width="0.8" opacity="0.70" filter="url(#pulseGlow_{i})" />

  <!-- 5. Photonic Quanta Pulses (Bidirectional energy packets) -->
  {' '.join(quanta_svg)}
</svg>"""
            (frames_dir / f"frame_{i:03d}.svg").write_text(svg, encoding="utf-8")

        temp_mov = frames_dir / f"_bridge_{slug_a}_{slug_b}.mov"
        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%03d.svg"),
            "-c:v", "qtrle",
            str(temp_mov)
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        temp_mov.replace(mov_path)
        return mov_path
    finally:
        if frames_dir.exists():
            shutil.rmtree(frames_dir, ignore_errors=True)


# Alias for backward compatibility
generate_gradient_orb_svg = generate_animated_orb_loop


class GradientOrbManager:
    """Manages creation, animation, and FFmpeg overlay configurations for the AI Presenter Orb."""

    def __init__(
        self,
        palette: str = "quantum",
        position: str = "presenter",
        size: str = "medium",
        opacity: float = 0.95,
        animation: str = "speaking",
        custom_x: Optional[int] = None,
        custom_y: Optional[int] = None,
        audio_path: Optional[Path] = None,
        total_duration: float = 35.0,
        intro_duration: float = 3.8,
    ):
        self.palette = palette.lower().strip() if palette else "quantum"
        if self.palette not in ORB_PALETTES:
            self.palette = "quantum"

        self.position = "presenter"
        self.pixel_size = 520
        self.opacity = max(0.2, min(1.0, float(opacity)))
        self.animation = "speaking"
        self.audio_path = Path(audio_path) if audio_path else None
        self.total_duration = max(3.0, float(total_duration))
        self.intro_duration = max(1.5, float(intro_duration))

    def get_overlay_coordinates(self, video_width: int, video_height: int) -> Tuple[str, str]:
        """Calculates 2D organic floating drift coordinates with zero-G cushioning entrance."""
        base_x = f"(W-w)/2"
        base_y = f"(H-h)/2 - {int(video_height * 0.05)}"
        # Zero-G cushioning drop: drops 24px into equilibrium position in first 450ms
        dy_intro = "(lt(t,0.45) * -24.0 * (1.0 - (sin(PI/2*t/0.45) + 0.10*sin(PI*t/0.45))))"
        x_anim = f"{base_x} + 18*sin(2*PI*t/3.6)"
        y_anim = f"{base_y} + 24*sin(2*PI*t/2.4) + {dy_intro}"
        return x_anim, y_anim

    def build_filter_chain(
        self,
        input_idx: int,
        output_label: str,
        video_width: int,
        video_height: int,
        fps: int = 30,
    ) -> str:
        """
        Builds the FFmpeg filter chain that applies singularity ignition entrance,
        core flash, and speech-envelope audio reactivity.
        """
        target_size = self.pixel_size
        effective_opacity = self.opacity
        speech_intervals: List[Tuple[float, float]] = []

        if self.audio_path and self.audio_path.exists():
            speech_intervals = extract_audio_speech_envelope(self.audio_path)

        filters = []
        # Singularity Ignition entrance scale curve (0 -> 106% overshoot -> 100% in 450ms)
        intro_scale = "(lt(t\\,0.45) * (0.02 + 0.98*(sin(PI/2*t/0.45) + 0.10*sin(PI*t/0.45))) + gte(t\\,0.45))"
        scale_expr = f"eval=frame:w='trunc({target_size}*({intro_scale})/2)*2':h='trunc({target_size}*({intro_scale})/2)*2'"
        # Core ignition flash: decaying incandescent brightness boost over first 280ms
        flash_expr = "(lt(t\\,0.28) * 0.42 * (1.0 - t/0.28))"

        if speech_intervals:
            conds = [f"between(t\\,{start:.2f}\\,{end:.2f})" for start, end in speech_intervals]
            speech_mask = f"min(1\\,{'+'.join(conds)})"
            voice_ripple = f"(0.5 + 0.5 * sin(2*PI*t/0.38))"

            eq_expr = f"brightness='-0.12 + ({flash_expr}) + (0.28 + 0.08*{voice_ripple})*{speech_mask}':contrast='0.80 + 0.50*({flash_expr}) + (0.35 + 0.15*{voice_ripple})*{speech_mask}'"
            hue_expr = f"h='(12 + 4*{voice_ripple})*{speech_mask} + 6*sin(2*PI*t/2.4)':s='0.75 + 0.30*({flash_expr}) + (0.45 + 0.20*{voice_ripple})*{speech_mask}'"

            return f"[{input_idx}:v]format=yuva420p,scale={scale_expr},eq={eq_expr},hue={hue_expr},colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]"
        else:
            eq_expr = f"brightness='-0.03 + ({flash_expr})':contrast='1.0 + 0.50*({flash_expr})':saturation='1.0 + 0.30*({flash_expr})'"
            hue_expr = "h='10*sin(2*PI*t/2.5)':s='1.0 + 0.08*sin(2*PI*t/2.5)'"

            return f"[{input_idx}:v]format=yuva420p,scale={scale_expr},eq={eq_expr},hue={hue_expr},colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]"


def _get_audio_duration_secs(file_path: Path, default_fallback: float = 3.0) -> float:
    """Accurately measures media duration using ffprobe."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(file_path)
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        val = float(res.stdout.strip())
        return max(0.5, val)
    except Exception:
        return default_fallback


def render_orb_test_preview(
    palette: str = "quantum",
    position: str = "presenter",
    size: str = "medium",
    animation: str = "speaking",
    opacity: float = 0.95,
    duration: float = 12.0,
    output_path: Optional[Path] = None,
    width: int = 1080,
    height: int = 1920,
    bg_style: str = "cosmic",
    sample_audio: Optional[Path] = None,
    headline_hook: str = "PARADOJA CUÁNTICA VS FÍSICA SOLAR",
    topic: Optional[str] = None,
    debate_script: Optional[Dict[str, Any]] = None,
    cohosts: Optional[str] = "quantum,solar",
    llm_provider: str = "groq",
    gemini_key: Optional[str] = None,
    groq_key: Optional[str] = None,
    openai_key: Optional[str] = None,
    enable_review: bool = True,
) -> Optional[Path]:
    """Renders a stunning co-host conversation video with two bio-reactive orbs and dynamic camera cuts."""
    from core.hosts import CosmicDebateShow, HostRegistry, DEFAULT_QUANTUM_HOST, DEFAULT_SOLAR_HOST

    # 0. Resolve co-hosts from parameter, script, or defaults
    target_hosts = cohosts or "quantum,solar"
    if debate_script and "cohosts" in debate_script and isinstance(debate_script["cohosts"], str):
        target_hosts = debate_script["cohosts"]
    
    parts = [p.strip() for p in target_hosts.split(",") if p.strip()]
    resolved_host_a = HostRegistry.get(parts[0]) if len(parts) >= 1 else DEFAULT_QUANTUM_HOST
    resolved_host_b = HostRegistry.get(parts[1]) if len(parts) >= 2 else DEFAULT_SOLAR_HOST
    debate_show = CosmicDebateShow(host_a=resolved_host_a, host_b=resolved_host_b)

    # 1. If topic is provided and debate_script is not provided, generate with AI
    if not debate_script and topic:
        from ai.debate_generator import DebateScriptGenerator
        gen = DebateScriptGenerator(
            preferred_provider=llm_provider,
            gemini_key=gemini_key,
            groq_key=groq_key,
            openai_key=openai_key,
            enable_review=enable_review,
            show=debate_show
        )
        debate_script = gen.generate(topic, language="es", allow_fallback=False)
        if not debate_script:
            print("\n❌ [Debate Express] Generación de guion fallida o cancelada.")
            print("   🚫 Cancelando renderizado para evitar generar un video inconsistente.")
            return None

    if output_path is None:
        out_dir = Path("output") / "orb_previews"
        topic_slug = "debate_express"
        if topic:
            clean_s = "".join(c if c.isalnum() else "_" for c in topic.lower())[:24].strip("_")
            topic_slug = f"debate_{clean_s}"
        video_folder = out_dir / topic_slug
        video_folder.mkdir(parents=True, exist_ok=True)
        output_path = video_folder / "video.mp4"
    else:
        output_path = Path(output_path)
        if output_path.suffix:
            video_folder = output_path.parent / output_path.stem
            video_folder.mkdir(parents=True, exist_ok=True)
            output_path = video_folder / "video.mp4"
        else:
            output_path.mkdir(parents=True, exist_ok=True)
            video_folder = output_path
            output_path = video_folder / "video.mp4"

    # Extract dynamic script values if available
    q_part1 = "El tiempo no existe a escala cuántica: todo ocurre al mismo tiempo."
    q_part2 = "La realidad entera es un cálculo esperando a ser observado."
    s_part3 = "¡Falso! La gravedad de una estrella aplasta cualquier cálculo en cenizas."
    both_part4 = "¿Bando Cuántico o Bando Solar? ¡Defiende tu bando en los comentarios!"

    holo_q_title = "PARADOJA CUÁNTICA"
    holo_q_sub = "Superposición: |ψ⟩ = α|0⟩ + β|1⟩"
    holo_q_cat = "POSTULADO Q"

    holo_s_title = "ENTROPÍA SOLAR"
    holo_s_sub = "Fusión Nuclear: 15,000,000 K"
    holo_s_cat = "POSTULADO S"

    has_holo_q = False
    has_holo_s = False

    if debate_script:
        if debate_script.get("headline_hook"):
            headline_hook = debate_script["headline_hook"]
        holograms = debate_script.get("holograms")
        if isinstance(holograms, dict):
            if "quantum" in holograms and isinstance(holograms["quantum"], dict):
                has_holo_q = True
                hq = holograms["quantum"]
                holo_q_title = str(hq.get("title", holo_q_title)).upper()
                holo_q_sub = str(hq.get("subtitle", holo_q_sub))
                holo_q_cat = str(hq.get("category", holo_q_cat))
            if "solar" in holograms and isinstance(holograms["solar"], dict):
                has_holo_s = True
                hs = holograms["solar"]
                holo_s_title = str(hs.get("title", holo_s_title)).upper()
                holo_s_sub = str(hs.get("subtitle", holo_s_sub))
                holo_s_cat = str(hs.get("category", holo_s_cat))

        scenes = debate_script.get("scenes", [])
        if not scenes:
            scenes = [
                {"speaker": "Narrador", "entity": "narrator", "text": "¿Y si el tiempo no existe y todo ocurre al mismo tiempo?", "shot": "wide"},
                {"speaker": "Quantum", "entity": "quantum", "text": "A escala subatómica el tiempo es solo una ilusión probabilística.", "shot": "close_quantum"},
                {"speaker": "Solar", "entity": "solar", "text": "¡Imposible! La entropía y la fusión estelar demuestran que el tiempo fluye.", "shot": "close_solar"},
                {"speaker": "Narrador", "entity": "narrator", "text": "¿Física cuántica o termodinámica estelar? ¡Elige tu bando en los comentarios!", "shot": "both"}
            ]

        script_json_path = output_path.parent / "script.json"
        script_json_path.write_text(json.dumps(debate_script, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        scenes = [
            {"speaker": "Narrador", "entity": "narrator", "text": "¿Y si el tiempo no existe y todo ocurre al mismo tiempo?", "shot": "wide"},
            {"speaker": "Quantum", "entity": "quantum", "text": q_part1, "shot": "close_quantum"},
            {"speaker": "Quantum", "entity": "quantum", "text": q_part2, "shot": "close_quantum"},
            {"speaker": "Solar", "entity": "solar", "text": s_part3, "shot": "close_solar"},
            {"speaker": "Narrador", "entity": "narrator", "text": both_part4, "shot": "both"}
        ]

    print(f"\n🔮 [AI Co-Host Debate Express] Renderizando video dinámico ({len(scenes)} escenas) con Doble Orbe y Multi-Cámara...")
    print(f"   • Orbe 1: QUANTUM (Azul Eléctrico / Cyan) | Orbe 2: SOLAR (Ámbar / Oro)")
    print(f"   • Hook: {headline_hook}")
    if has_holo_q:
        print(f"   • HUD Holográfico Q: [{holo_q_cat}] {holo_q_title} -> {holo_q_sub}")
    if has_holo_s:
        print(f"   • HUD Holográfico S: [{holo_s_cat}] {holo_s_title} -> {holo_s_sub}")

    # Generate or retrieve cached orb visual assets for all conversational perspectives
    orb_q_talk = get_or_create_orb_asset(palette=debate_show.host_a.palette_name, mode="talk", force_refresh=False)
    orb_q_idle = get_or_create_orb_asset(palette=debate_show.host_a.palette_name, mode="idle", force_refresh=False)
    orb_q_close_talk = get_or_create_orb_asset(palette=debate_show.host_a.palette_name, mode="close_talk", force_refresh=False)
    
    orb_s_talk = get_or_create_orb_asset(palette=debate_show.host_b.palette_name, mode="talk", force_refresh=False)
    orb_s_idle = get_or_create_orb_asset(palette=debate_show.host_b.palette_name, mode="idle", force_refresh=False)
    orb_s_close_talk = get_or_create_orb_asset(palette=debate_show.host_b.palette_name, mode="close_talk", force_refresh=False)

    # Generate Holographic Floating Reference Cards (Only if required by script)
    from video.hologram import generate_hologram_card_svg

    holo_q_path = output_path.parent / "_holo_q.svg"
    holo_s_path = output_path.parent / "_holo_s.svg"

    if has_holo_q:
        generate_hologram_card_svg(
            title=holo_q_title,
            subtitle=holo_q_sub,
            category=holo_q_cat,
            color_theme=debate_show.host_a.color_theme,
            width=620,
            height=240,
            output_path=holo_q_path
        )
    if has_holo_s:
        generate_hologram_card_svg(
            title=holo_s_title,
            subtitle=holo_s_sub,
            category=holo_s_cat,
            color_theme=debate_show.host_b.color_theme,
            width=620,
            height=240,
            output_path=holo_s_path
        )

    # Resolve dynamic roles from AI script generation or infer from topic
    custom_roles = {}
    if debate_script:
        if "roles" in debate_script and isinstance(debate_script["roles"], dict):
            custom_roles = debate_script["roles"]
        elif "hosts" in debate_script and isinstance(debate_script["hosts"], dict):
            for h_k, h_v in debate_script["hosts"].items():
                if isinstance(h_v, dict) and "role" in h_v:
                    custom_roles[h_k] = h_v["role"]
                elif isinstance(h_v, str):
                    custom_roles[h_k] = h_v

    # Fallback to default host roles if custom_roles is incomplete
    default_roles = {
        debate_show.host_a.id: debate_show.host_a.role,
        debate_show.host_b.id: debate_show.host_b.role
    }
    for h_id, h_role in default_roles.items():
        if h_id not in custom_roles:
            custom_roles[h_id] = h_role

    badge_q_path, badge_s_path = debate_show.generate_all_badges(
        output_dir=output_path.parent,
        custom_roles=custom_roles
    )

    temp_test_audio: Optional[Path] = output_path.parent / "_temp_cohost_debate.mp3"
    resolved_audio: Optional[Path] = sample_audio

    scene_records = []
    temp_audio_files_to_clean = []

    if not resolved_audio:
        import concurrent.futures
        import hashlib
        from audio.tts import EdgeTTSProvider, GoogleTTSProvider
        from audio.sfx import synthesize_camera_servo_sfx, synthesize_space_ambient_pad
        from audio.music import MusicManager

        tts_edge = EdgeTTSProvider()
        tts_fallback = GoogleTTSProvider(language="es")

        # Persistent Voice Cache Directory (Instant re-use across test runs & renders)
        voice_cache_dir = Path(__file__).resolve().parent.parent / "assets" / "audio" / "cached_voices"
        voice_cache_dir.mkdir(parents=True, exist_ok=True)

        # Prepare scene specs and parallel TTS tasks (Eliminates redundant roundtrips)
        parsed_scenes = []
        tts_tasks = []

        for idx, sc in enumerate(scenes):
            spk_raw = str(sc.get("speaker", "Quantum")).strip()
            ent_raw = str(sc.get("entity", "quantum")).strip().lower()
            text = str(sc.get("text", "")).strip()
            shot = str(sc.get("shot", "wide")).strip().lower()

            if "narrator" in ent_raw or "narrador" in ent_raw or "narrador" in spk_raw.lower() or "presentador" in spk_raw.lower() or "voz en off" in spk_raw.lower():
                ent = "narrator"
                spk = "Narrador"
            elif "solar" in ent_raw or "solar" in spk_raw.lower():
                ent = "solar"
                spk = "Solar"
            elif "ambos" in ent_raw or "both" in ent_raw or "ambos" in spk_raw.lower() or "dual" in spk_raw.lower():
                ent = "both"
                spk = "Ambos"
            else:
                ent = "quantum"
                spk = "Quantum"

            # Strict speaker-shot alignment: A close-up MUST show the speaker who is actually talking!
            if ent == "narrator":
                if shot not in ["wide", "both"]:
                    shot = "wide" if idx == 0 else "both"
            elif ent == "solar" and shot == "close_quantum":
                shot = "close_solar"
            elif ent == "quantum" and shot == "close_solar":
                shot = "close_quantum"
            elif ent == "both" and shot in ["close_quantum", "close_solar"]:
                shot = "both"
            elif shot not in ["wide", "close_quantum", "close_solar", "both"]:
                if ent == "solar":
                    shot = "close_solar"
                elif ent == "both":
                    shot = "both"
                elif idx == 0:
                    shot = "wide"
                else:
                    shot = "close_quantum"

            # Smart Hashed Audio Cache Check
            text_hash = hashlib.md5(f"{ent}:{text}".encode("utf-8")).hexdigest()[:12]
            cached_voice_file = voice_cache_dir / f"voice_{ent}_{text_hash}.mp3"

            if cached_voice_file.exists() and cached_voice_file.stat().st_size > 500:
                # Already generated and cached: 0ms overhead, 0 API calls!
                scene_audio_paths = [cached_voice_file]
            else:
                tts_tasks.append((text, cached_voice_file, ent))
                scene_audio_paths = [cached_voice_file]

            parsed_scenes.append({
                "index": idx,
                "speaker": spk,
                "entity": ent,
                "text": text,
                "shot": shot,
                "audio_paths": scene_audio_paths
            })

        def _synthesize_voice_worker(task):
            txt, out_p, entity_name = task
            if out_p.exists() and out_p.stat().st_size > 500:
                return
            try:
                ok = tts_edge.synthesize_cosmic_entity(txt, out_p, entity=entity_name)
                if not ok or not out_p.exists() or out_p.stat().st_size == 0:
                    tts_fallback.synthesize_text(txt, out_p)
            except Exception as e:
                print(f"  ⚠️ Edge-TTS failed for {entity_name} ({e}), trying fallback...")
                try:
                    tts_fallback.synthesize_text(txt, out_p)
                except Exception as fb_err:
                    print(f"  ❌ Fallback TTS failed: {fb_err}")

        # Parallelize TTS synthesis across worker threads only for uncached voices
        if tts_tasks:
            print(f"  ⚡ Sintetizando {len(tts_tasks)} pistas vocales nuevas en paralelo...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, len(tts_tasks))) as executor:
                list(executor.map(_synthesize_voice_worker, tts_tasks))
        else:
            print(f"  ⚡ [Caché Instantáneo] Reutilizando {len(parsed_scenes)} pistas vocales ya sintetizadas (0 llamadas a API)")

        # Build chronologically aligned timeline from generated audio files
        current_audio_time = 0.0
        pause_between_scenes = 0.18

        for item in parsed_scenes:
            if item["entity"] == "both" and len(item["audio_paths"]) > 1:
                dur = max(_get_audio_duration_secs(item["audio_paths"][0], 2.5), _get_audio_duration_secs(item["audio_paths"][1], 2.5))
            else:
                dur = _get_audio_duration_secs(item["audio_paths"][0], 3.0)

            s_start = round(current_audio_time, 2)
            s_end = round(s_start + dur, 2)
            current_audio_time = round(s_end + pause_between_scenes, 2)

            scene_records.append({
                "index": item["index"],
                "speaker": item["speaker"],
                "entity": item["entity"],
                "text": item["text"],
                "shot": item["shot"],
                "start": s_start,
                "end": s_end,
                "audio_paths": item["audio_paths"]
            })

        total_duration = round(max(current_audio_time + 0.6, 8.0), 2)
        print(f"   • Línea de Tiempo Dialéctica Multi-Escena ({len(scene_records)} escenas):")
        for sc in scene_records:
            print(f"     - Escena {sc['index']+1} [{sc['speaker']}] ({sc['shot']}): {sc['start']}s -> {sc['end']}s | \"{sc['text'][:45]}...\"")
        print(f"     - Duración Total: {total_duration}s")

        # Camera transition SFX & entity stingers (Checks user assets/sfx/ before procedural fallback)
        from audio.sfx import resolve_sfx_path
        sfx_cache_dir = Path(__file__).resolve().parent.parent / "assets" / "sfx" / "cached"
        sfx_cache_dir.mkdir(parents=True, exist_ok=True)

        sfx_intro_path = resolve_sfx_path("intro", output_dir=sfx_cache_dir, duration=1.1)
        sfx_zoom_path = resolve_sfx_path("whoosh_quantum", output_dir=sfx_cache_dir, duration=0.52)
        sfx_pan_path = resolve_sfx_path("whoosh_solar", output_dir=sfx_cache_dir, duration=0.52)
        sfx_res_path = resolve_sfx_path("cosmic_resonance", output_dir=sfx_cache_dir, duration=2.5)
        music_bg_path = output_path.parent / "_temp_music_ambient.wav"

        sfx_plasma_path = sfx_cache_dir / "sfx_plasma_arc_750.wav"
        if not sfx_plasma_path.exists() or sfx_plasma_path.stat().st_size < 100:
            synthesize_plasma_arc_sfx(sfx_plasma_path)

        # Background soundtrack
        music_mgr = MusicManager()
        bg_track = music_mgr.get_background_track()
        if bg_track and bg_track.exists():
            music_bg_path = bg_track
        else:
            synthesize_space_ambient_pad(music_bg_path, duration=total_duration)
            temp_audio_files_to_clean.append(music_bg_path)

        # Build dynamic audio concat ffmpeg command
        audio_inputs = []
        audio_filter_lines = []
        mix_inputs = []

        stream_idx = 0
        for sc in scene_records:
            delay_ms = int(sc["start"] * 1000)
            for p_path in sc["audio_paths"]:
                audio_inputs.extend(["-i", str(p_path)])
                vol = 0.90 if sc["entity"] == "both" else 1.0
                audio_filter_lines.append(f"[{stream_idx}:a]adelay={delay_ms}|{delay_ms},volume={vol}[a_{stream_idx}]")
                mix_inputs.append(f"[a_{stream_idx}]")
                stream_idx += 1

        # Add SFX - Heavy Sub-Bass Drop Opening Hook Impact (Option 2)
        audio_inputs.extend(["-i", str(sfx_intro_path)])
        audio_filter_lines.append(f"[{stream_idx}:a]adelay=20|20,volume=0.88[sfx_intro]")
        mix_inputs.append("[sfx_intro]")
        stream_idx += 1

        # Add Staggered Solar Singularity Ignition Stinger at 220ms
        audio_inputs.extend(["-i", str(sfx_pan_path)])
        audio_filter_lines.append(f"[{stream_idx}:a]adelay=220|220,volume=0.32[sfx_solar_intro]")
        mix_inputs.append("[sfx_solar_intro]")
        stream_idx += 1

        # Add Ionized Plasma Bridge Resonance Stinger at 380ms
        audio_inputs.extend(["-i", str(sfx_plasma_path)])
        audio_filter_lines.append(f"[{stream_idx}:a]adelay=380|380,volume=0.28[sfx_plasma]")
        mix_inputs.append("[sfx_plasma]")
        stream_idx += 1

        for sc in scene_records[1:]:
            sfx_delay_ms = int(max(0.0, sc["start"] - 0.08) * 1000)
            if sc["shot"] == "close_solar":
                audio_inputs.extend(["-i", str(sfx_pan_path)])
                audio_filter_lines.append(f"[{stream_idx}:a]adelay={sfx_delay_ms}|{sfx_delay_ms},volume=0.35[sfx_{stream_idx}]")
            elif sc["shot"] == "both":
                audio_inputs.extend(["-i", str(sfx_res_path)])
                audio_filter_lines.append(f"[{stream_idx}:a]adelay={sfx_delay_ms}|{sfx_delay_ms},volume=0.42[sfx_{stream_idx}]")
            else:
                audio_inputs.extend(["-i", str(sfx_zoom_path)])
                audio_filter_lines.append(f"[{stream_idx}:a]adelay={sfx_delay_ms}|{sfx_delay_ms},volume=0.35[sfx_{stream_idx}]")
            mix_inputs.append(f"[sfx_{stream_idx}]")
            stream_idx += 1

        # Add Background Music
        audio_inputs.extend(["-stream_loop", "-1", "-i", str(music_bg_path)])
        audio_filter_lines.append(f"[{stream_idx}:a]volume=0.16,afade=t=in:st=0:d=1.0,afade=t=out:st={round(total_duration - 1.4, 2)}:d=1.4[bgm]")
        mix_inputs.append("[bgm]")
        stream_idx += 1

        audio_filter_lines.append(f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:dropout_transition=0:normalize=0[aout]")

        audio_concat_cmd = [
            "ffmpeg", "-y",
            *audio_inputs,
            "-filter_complex", ";".join(audio_filter_lines),
            "-map", "[aout]",
            "-t", str(total_duration),
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(temp_test_audio)
        ]

        try:
            subprocess.run(audio_concat_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if temp_test_audio.exists():
                resolved_audio = temp_test_audio
        except Exception as e:
            print(f"  ⚠️ Multi-scene audio mixing error: {e}")
            if scene_records and scene_records[0]["audio_paths"]:
                resolved_audio = scene_records[0]["audio_paths"][0]

        for p in temp_audio_files_to_clean:
            if p.exists() and p != resolved_audio:
                try:
                    p.unlink()
                except Exception:
                    pass
    else:
        total_duration = _get_audio_duration_secs(resolved_audio, 12.0)
        # Create proportional scene records if using pre-baked audio
        n_sc = max(1, len(scenes))
        slice_dur = total_duration / n_sc
        for idx, sc in enumerate(scenes):
            scene_records.append({
                "index": idx,
                "speaker": sc.get("speaker", "Quantum"),
                "entity": sc.get("entity", "quantum").lower(),
                "text": sc.get("text", ""),
                "shot": sc.get("shot", "wide"),
                "start": round(idx * slice_dur, 2),
                "end": round((idx + 1) * slice_dur, 2),
                "audio_paths": []
            })

    # Build dynamic speech reactive masks
    speech_q_conditions = [f"between(t,{sc['start']},{sc['end']})" for sc in scene_records if sc["entity"] in ["quantum", "both"]]
    speech_mask_q = f"({' + '.join(speech_q_conditions)})" if speech_q_conditions else "0"

    speech_s_conditions = [f"between(t,{sc['start']},{sc['end']})" for sc in scene_records if sc["entity"] in ["solar", "both"]]
    speech_mask_s = f"({' + '.join(speech_s_conditions)})" if speech_s_conditions else "0"

    intervals_q = [(sc["start"], sc["end"]) for sc in scene_records if sc["entity"] in ["quantum", "both"]]
    intervals_s = [(sc["start"], sc["end"]) for sc in scene_records if sc["entity"] in ["solar", "both"]]

    # Real Audio Syllable Energy Modulator (Reacts to voice RMS spikes frame by frame)
    voice_pulse_q = extract_real_audio_rms_profile(resolved_audio, intervals_q) if (resolved_audio and resolved_audio.exists()) else "(0.5 + 0.30*sin(2*PI*t/0.24))"
    voice_pulse_s = extract_real_audio_rms_profile(resolved_audio, intervals_s) if (resolved_audio and resolved_audio.exists()) else "(0.5 + 0.30*sin(2*PI*t/0.24))"

    # Acoustic Respiratory Volume (Physical breathing scale surges +4.5% on active voice syllables)
    scale_expr_q_wide = f"eval=frame:w='trunc(420*(1.0 + 0.045*({voice_pulse_q})*({speech_mask_q}))/2)*2':h='trunc(420*(1.0 + 0.045*({voice_pulse_q})*({speech_mask_q}))/2)*2'"
    scale_expr_s_wide = f"eval=frame:w='trunc(370*(1.0 + 0.045*({voice_pulse_s})*({speech_mask_s}))/2)*2':h='trunc(370*(1.0 + 0.045*({voice_pulse_s})*({speech_mask_s}))/2)*2'"
    scale_expr_q_close = f"eval=frame:w='trunc(820*(1.0 + 0.045*({voice_pulse_q})*({speech_mask_q}))/2)*2':h='trunc(820*(1.0 + 0.045*({voice_pulse_q})*({speech_mask_q}))/2)*2'"
    scale_expr_s_close = f"eval=frame:w='trunc(820*(1.0 + 0.045*({voice_pulse_s})*({speech_mask_s}))/2)*2':h='trunc(820*(1.0 + 0.045*({voice_pulse_s})*({speech_mask_s}))/2)*2'"

    eq_q = f"eval=frame:brightness='-0.03 + (0.18 + 0.22*{voice_pulse_q})*({speech_mask_q})':contrast='1.0 + (0.24 + 0.20*{voice_pulse_q})*({speech_mask_q})':saturation='1.0 + (0.26 + 0.18*{voice_pulse_q})*({speech_mask_q})'"
    hue_q = f"h='(10 + 6*{voice_pulse_q})*({speech_mask_q}) + 4*sin(2*PI*t/3.6)':s='1.0 + (0.22 + 0.15*{voice_pulse_q})*({speech_mask_q})'"

    eq_s = f"eval=frame:brightness='-0.03 + (0.18 + 0.22*{voice_pulse_s})*({speech_mask_s})':contrast='1.0 + (0.24 + 0.20*{voice_pulse_s})*({speech_mask_s})':saturation='1.0 + (0.26 + 0.18*{voice_pulse_s})*({speech_mask_s})'"
    hue_s = f"h='(10 + 6*{voice_pulse_s})*({speech_mask_s}) + 4*sin(2*PI*t/3.6)':s='1.0 + (0.22 + 0.15*{voice_pulse_s})*({speech_mask_s})'"

    # Dynamic Cosmic Vacuum Illumination: Ambient nebula radiance breathes with acoustic intensity
    eq_glow_q = f"eval=frame:brightness='(0.08 + 0.28*{voice_pulse_q})*({speech_mask_q})':contrast='1.0 + 0.35*({speech_mask_q})'"
    eq_glow_s = f"eval=frame:brightness='(0.08 + 0.28*{voice_pulse_s})*({speech_mask_s})':contrast='1.0 + 0.35*({speech_mask_s})'"

    # Organic Celestial Motion Physics:
    # 1. Non-repetitive Lissajous 8-figure orbital float (harmonics with golden ratio periods 5.8s & 8.6s)
    # 2. Conversational Intentionality: Active speaker leans smoothly forward toward interlocutor with acoustic micro-vibration
    # 3. Attentive Listener: Resting entity maintains a smooth, cushioned floating stance
    orbit_lx_q = "(9.0*sin(2*PI*t/5.8) + 3.5*cos(2*PI*t/8.6))"
    orbit_ly_q = "(-11.0*cos(2*PI*t/4.4) - 3.0*sin(2*PI*t/7.2))"

    orbit_lx_s = "(-9.0*sin(2*PI*t/5.6) - 3.5*cos(2*PI*t/8.2))"
    orbit_ly_s = "(-11.0*cos(2*PI*t/4.6) - 3.0*sin(2*PI*t/7.4))"

    # Acoustic micro-resonance (voice vibration on powerful syllables)
    voice_jitter_q = f"(1.8*sin(2*PI*t/0.11)*{voice_pulse_q})"
    voice_jitter_s = f"(-1.8*sin(2*PI*t/0.11)*{voice_pulse_s})"

    from utils.fonts import resolve_best_font_path
    font_param, _ = resolve_best_font_path()

    import re
    clean_hook = re.sub(r'[^\w\s\?¿!¡\-\.,:áéíóúÁÉÍÓÚñÑ]', '', headline_hook).strip()
    escaped_headline_hook = clean_hook.replace(":", "\\:").replace("'", "\\'")

    # High-Performance Futuristic ASS Karaoke Subtitles (Using ALL dynamic scenes)
    from subtitles.generator import generate_cosmic_debate_karaoke_ass
    ass_sub_path = output_path.parent / "_temp_debate_karaoke.ass"
    generate_cosmic_debate_karaoke_ass(scene_records, ass_sub_path, width=width, height=height, roles=custom_roles)
    escaped_ass_path = str(ass_sub_path.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")

    # Dynamic Sci-Fi Cosmic Particle Background Video Loop (Dynamic Palette Inheritance)
    from video.cosmic_bg import get_cosmic_particle_background_video
    from video.atmosphere import generate_global_foreground_atmosphere_loop
    try:
        color_a = getattr(debate_show.host_a, "primary_color", "#00f0ff")
        color_a_glow = getattr(debate_show.host_a, "glow_color", "#0284c7")
        color_b = getattr(debate_show.host_b, "primary_color", "#ffea00")
        color_b_glow = getattr(debate_show.host_b, "glow_color", "#ff5500")

        cosmic_bg_video = get_cosmic_particle_background_video(
            width=width,
            height=height,
            color_a=color_a,
            color_a_glow=color_a_glow,
            color_b=color_b,
            color_b_glow=color_b_glow,
        )
        if cosmic_bg_video.exists() and cosmic_bg_video.stat().st_size > 1000:
            bg_cmd_args = ["-stream_loop", "-1", "-i", str(cosmic_bg_video)]
        else:
            bg_cmd_args = ["-f", "lavfi", "-i", f"color=c=0x08090f:s={width}x{height}:r=30:d={total_duration}"]
    except Exception as bg_err:
        print(f"  ⚠️ Usando fallback de color para fondo: {bg_err}")
        bg_cmd_args = ["-f", "lavfi", "-i", f"color=c=0x08090f:s={width}x{height}:r=30:d={total_duration}"]

    # Global Foreground Atmosphere Loop (Floating sparks & out-of-focus camera lens bokeh)
    try:
        atmos_loop = generate_global_foreground_atmosphere_loop(
            width=width,
            height=height,
            color_a=color_a,
            color_b=color_b,
        )
        has_atmos = atmos_loop.exists() and atmos_loop.stat().st_size > 1000
    except Exception as atmos_err:
        print(f"  ⚠️ Atmósfera frontal no disponible: {atmos_err}")
        has_atmos = False
        atmos_loop = None

    # Build FFmpeg command inputs (wide talk, wide idle, close-up frontal talk for both hosts)
    cmd_inputs = [
        *bg_cmd_args,
        "-stream_loop", "-1", "-i", str(orb_q_talk),
        "-stream_loop", "-1", "-i", str(orb_q_idle),
        "-stream_loop", "-1", "-i", str(orb_q_close_talk),
        "-stream_loop", "-1", "-i", str(orb_s_talk),
        "-stream_loop", "-1", "-i", str(orb_s_idle),
        "-stream_loop", "-1", "-i", str(orb_s_close_talk),
    ]
    curr_input_idx = 7

    # Ephemeral Expanding Singularity Shockwave Bursts
    sw_q_asset = get_or_create_shockwave_asset(color_a, duration_sec=0.45, target_dir=output_path.parent)
    sw_s_asset = get_or_create_shockwave_asset(color_b, duration_sec=0.45, target_dir=output_path.parent)

    cmd_inputs.extend(["-i", str(sw_q_asset)])
    sw_q_idx = curr_input_idx
    curr_input_idx += 1

    cmd_inputs.extend(["-i", str(sw_s_asset)])
    sw_s_idx = curr_input_idx
    curr_input_idx += 1

    # Ethereal Quantum-Solar Magnetic Plasma Bridge (Scene 0 wide hook tension)
    bridge_asset = get_or_create_plasma_bridge_asset(color_a, color_b, target_dir=output_path.parent)
    cmd_inputs.extend(["-stream_loop", "-1", "-i", str(bridge_asset)])
    bridge_idx = curr_input_idx
    curr_input_idx += 1

    atmos_idx = None
    if has_atmos and atmos_loop:
        cmd_inputs.extend(["-stream_loop", "-1", "-i", str(atmos_loop)])
        atmos_idx = curr_input_idx
        curr_input_idx += 1

    holo_q_idx = None
    if has_holo_q:
        cmd_inputs.extend(["-stream_loop", "-1", "-i", str(holo_q_path)])
        holo_q_idx = curr_input_idx
        curr_input_idx += 1

    holo_s_idx = None
    if has_holo_s:
        cmd_inputs.extend(["-stream_loop", "-1", "-i", str(holo_s_path)])
        holo_s_idx = curr_input_idx
        curr_input_idx += 1

    audio_idx = curr_input_idx
    if resolved_audio and resolved_audio.exists():
        cmd_inputs.extend(["-i", str(resolved_audio)])
    else:
        cmd_inputs.extend(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"])

    pre_scale_lines = [
        f"[{sw_q_idx}:v]scale=500:500,format=yuva420p[sw_q]",
        f"[{sw_s_idx}:v]scale=500:500,tpad=start_duration=0.22:color=black@0.0,format=yuva420p[sw_s]",
        f"[{bridge_idx}:v]setpts=N/30/TB,format=yuva420p,fade=t=in:st=0.38:d=0.45:alpha=1,fade=t=out:st=3.75:d=0.75:alpha=1[bridge_faded]",
    ]
    if has_holo_q and holo_q_idx is not None:
        pre_scale_lines.append(f"[{holo_q_idx}:v]scale=540:-2,format=yuva420p[holo_q]")
    if has_holo_s and holo_s_idx is not None:
        pre_scale_lines.append(f"[{holo_s_idx}:v]scale=540:-2,format=yuva420p[holo_s]")

    # Calculate exact number of split pads needed for Quantum and Solar (wide talk, idle, and close frontal talk)
    q_talk_uses = sum(1 for sc in scene_records if (sc["shot"] == "both") or (sc["shot"] == "wide" and sc["entity"] in ["quantum", "both"]))
    q_idle_uses = 1 + sum(1 for sc in scene_records if sc["shot"] == "wide" and sc["entity"] not in ["quantum", "both"])
    q_close_uses = sum(1 for sc in scene_records if sc["shot"] == "close_quantum")

    s_talk_uses = sum(1 for sc in scene_records if (sc["shot"] == "both") or (sc["shot"] == "wide" and sc["entity"] in ["solar", "both"]))
    s_idle_uses = 1 + sum(1 for sc in scene_records if sc["shot"] == "wide" and sc["entity"] not in ["solar", "both"])
    s_close_uses = sum(1 for sc in scene_records if sc["shot"] == "close_solar")

    filter_complex = [
        *pre_scale_lines,
        f"[1:v]setpts=N/30/TB,split={max(1, q_talk_uses)}" + "".join(f"[q_talk_{k}]" for k in range(max(1, q_talk_uses))),
        f"[2:v]setpts=N/30/TB,split={max(1, q_idle_uses)}" + "".join(f"[q_idle_{k}]" for k in range(max(1, q_idle_uses))),
        f"[3:v]setpts=N/30/TB,split={max(1, q_close_uses)}" + "".join(f"[q_close_{k}]" for k in range(max(1, q_close_uses))),
        f"[4:v]setpts=N/30/TB,split={max(1, s_talk_uses)}" + "".join(f"[s_talk_{k}]" for k in range(max(1, s_talk_uses))),
        f"[5:v]setpts=N/30/TB,split={max(1, s_idle_uses)}" + "".join(f"[s_idle_{k}]" for k in range(max(1, s_idle_uses))),
        f"[6:v]setpts=N/30/TB,split={max(1, s_close_uses)}" + "".join(f"[s_close_{k}]" for k in range(max(1, s_close_uses))),

        # Background Ambient Luminescence (Ultra-smooth diffuse glow via 120x120 3-pass boxblur)
        # Deep cosmic illumination breathes in direct sync with speech RMS energy and ignites on entrance
        f"[q_idle_0]scale=120:120,eq={eq_glow_q},hue={hue_q},boxblur=26:3,scale={width}:{height},format=yuva420p,colorchannelmixer=aa=0.30[bg_glow_q]",
        f"[s_idle_0]scale=120:120,eq={eq_glow_s},hue={hue_s},boxblur=26:3,scale={width}:{height},format=yuva420p,colorchannelmixer=aa=0.30[bg_glow_s]",

        f"[0:v]eq=brightness=-0.02:contrast=1.16:saturation=1.12[bg_graded]",
        f"[bg_graded][bg_glow_q]overlay=eval=frame:enable='({speech_mask_q} + between(t,0,0.48))'[bg_glowed_1]",
        f"[bg_glowed_1][bg_glow_s]overlay=eval=frame:enable='({speech_mask_s} + between(t,0.22,0.70))'[bg_glowed_2]",
        f"[bg_glowed_2][sw_q]overlay=eval=frame:x='W*0.25-w/2':y='H*0.38-h/2':enable='between(t,0,0.45)':eof_action=pass[bg_sw_1]",
        f"[bg_sw_1][sw_s]overlay=eval=frame:x='W*0.75-w/2 - 28':y='H*0.39-h/2':enable='between(t,0.22,0.67)':eof_action=pass[bg_ambient]",
        # Ethereal Quantum-Solar Magnetic Plasma Bridge (Scene 0 wide shot: t = 0.38s to 4.55s)
        f"[bg_ambient][bridge_faded]overlay=eval=frame:x=140:y=560:enable='between(t,0.38,4.55)':eof_action=pass[bg_bridged]"
    ]

    cur_v = "bg_bridged"
    q_talk_cur = 0
    q_idle_cur = 1  # 0 used for bg_glow_q
    q_close_cur = 0
    s_talk_cur = 0
    s_idle_cur = 1  # 0 used for bg_glow_s
    s_close_cur = 0
    holo_q_used = False
    holo_s_used = False

    for idx, sc in enumerate(scene_records):
        st = sc["start"]
        # Seamless scene continuity: visual shot stays active until exact start of next scene
        sc_visual_end = scene_records[idx + 1]["start"] if idx + 1 < len(scene_records) else total_duration
        ent = sc["entity"]
        shot = sc["shot"]
        sc_dur = max(0.2, round(sc_visual_end - st, 2))

        # Smooth cinematic ease-in-out dolly progression (Smoothstep S-curve)
        prog_expr = f"(0.5 - 0.5*cos(PI*min(1.0\\,max(0.0\\,(t-{st})/{sc_dur}))))"

        if shot == "wide":
            is_q_active = (ent in ["quantum", "both"])

            if is_q_active:
                q_src = f"q_talk_{q_talk_cur}"
                q_talk_cur += 1
                # Conversational Step-Forward: Active Quantum leans +18px toward center + subtle speech vibration
                dq_x = f"{orbit_lx_q} + 18.0*{prog_expr} + {voice_jitter_q}"
                dq_y = f"{orbit_ly_q} - 10.0*{prog_expr}"
                q_alpha = 1.0
            else:
                q_src = f"q_idle_{q_idle_cur}"
                q_idle_cur += 1
                # Attentive Listening stance: Cushioned celestial orbit with subtle listening tilt
                dq_x = f"{orbit_lx_q} - 6.0"
                dq_y = f"{orbit_ly_q}"
                q_alpha = 0.92

            q_scale_str = scale_expr_q_wide if is_q_active else "410:410"

            # Singularity Ignition & Elastic Zero-G Cushioning for Quantum in Scene 0 (t = 0.0s to 0.45s)
            if idx == 0:
                flash_q = "(lt(t\\,0.35) * 0.45 * (1.0 - t/0.35))"
                q_eq_str = f"eval=frame:brightness='-0.03 + ({flash_q}) + (0.18 + 0.22*{voice_pulse_q})*({speech_mask_q})':contrast='1.0 + 0.45*({flash_q}) + (0.24 + 0.20*{voice_pulse_q})*({speech_mask_q})':saturation='1.0 + 0.35*({flash_q}) + (0.26 + 0.18*{voice_pulse_q})*({speech_mask_q})'"
                dy_intro_q = " + (lt(t\\,0.45) * -28.0 * (1.0 - (sin(PI/2*t/0.45) + 0.10*sin(PI*t/0.45))))"
                dx_intro_q = " + (lt(t\\,0.45) * 16.0 * (1.0 - sin(PI/2*t/0.45)))"
            else:
                q_eq_str = eq_q if is_q_active else "eval=frame:brightness='-0.03':contrast='1.0':saturation='1.0'"
                dy_intro_q = ""
                dx_intro_q = ""

            q_filt = f"format=yuva420p,{q_scale_str if 'scale=' in q_scale_str else f'scale={q_scale_str}'},eq={q_eq_str},hue={hue_q},colorchannelmixer=aa={q_alpha}"
            filter_complex.append(f"[{q_src}]{q_filt}[q_sc_{idx}]")
            filter_complex.append(f"[{cur_v}][q_sc_{idx}]overlay=eval=frame:x='W*0.25-w/2 + {dq_x}{dx_intro_q}':y='H*0.38-h/2 + {dq_y}{dy_intro_q}':enable='between(t,{st},{sc_visual_end})'[v_sc_{idx}_q]")
            cur_v = f"v_sc_{idx}_q"

            is_s_active = (ent in ["solar", "both"])
            if is_s_active:
                s_src = f"s_talk_{s_talk_cur}"
                s_talk_cur += 1
                # Conversational Step-Forward: Active Solar leans -18px toward center + subtle speech vibration
                ds_x = f"{orbit_lx_s} - 18.0*{prog_expr} + {voice_jitter_s}"
                ds_y = f"{orbit_ly_s} - 10.0*{prog_expr}"
                s_alpha = 1.0
            else:
                s_src = f"s_idle_{s_idle_cur}"
                s_idle_cur += 1
                # Attentive Listening stance: Cushioned celestial orbit with subtle listening tilt
                ds_x = f"{orbit_lx_s} + 6.0"
                ds_y = f"{orbit_ly_s}"
                s_alpha = 0.92

            s_scale_str = scale_expr_s_wide if is_s_active else "360:360"

            # Singularity Ignition & Staggered Elastic Zero-G Cushioning for Solar in Scene 0 (t = 0.22s to 0.67s)
            if idx == 0:
                flash_s = "(gte(t\\,0.22)*lt(t\\,0.55) * 0.45 * (1.0 - (t-0.22)/0.33))"
                s_eq_str = f"eval=frame:brightness='-0.03 + ({flash_s}) + (0.18 + 0.22*{voice_pulse_s})*({speech_mask_s})':contrast='1.0 + 0.45*({flash_s}) + (0.24 + 0.20*{voice_pulse_s})*({speech_mask_s})':saturation='1.0 + 0.35*({flash_s}) + (0.26 + 0.18*{voice_pulse_s})*({speech_mask_s})'"
                dy_intro_s = " + (gte(t\\,0.22)*lt(t\\,0.67) * -28.0 * (1.0 - (sin(PI/2*(t-0.22)/0.45) + 0.10*sin(PI*(t-0.22)/0.45))))"
                dx_intro_s = " + (gte(t\\,0.22)*lt(t\\,0.67) * -16.0 * (1.0 - sin(PI/2*(t-0.22)/0.45)))"
                s_enable = f"between(t\\,0.22\\,{sc_visual_end})"
            else:
                s_eq_str = eq_s if is_s_active else "eval=frame:brightness='-0.03':contrast='1.0':saturation='1.0'"
                dy_intro_s = ""
                dx_intro_s = ""
                s_enable = f"between(t,{st},{sc_visual_end})"

            s_filt = f"format=yuva420p,{s_scale_str if 'scale=' in s_scale_str else f'scale={s_scale_str}'},eq={s_eq_str},hue={hue_s},colorchannelmixer=aa={s_alpha}"
            filter_complex.append(f"[{s_src}]{s_filt}[s_sc_{idx}]")
            filter_complex.append(f"[{cur_v}][s_sc_{idx}]overlay=eval=frame:x='W*0.75-w/2 - 28 + {ds_x}{dx_intro_s}':y='H*0.39-h/2 + {ds_y}{dy_intro_s}':enable='{s_enable}'[v_sc_{idx}_s]")
            cur_v = f"v_sc_{idx}_s"

        elif shot == "close_quantum":
            q_src = f"q_close_{q_close_cur}"
            q_close_cur += 1
            # Cinematic Push-In Dolly with Ease-in-Out progression + Lissajous orbital levitation:
            d_cq_x = f"{orbit_lx_q} + {voice_jitter_q}"
            d_cq_y = f"{orbit_ly_q} - 14.0*{prog_expr}"
            sc_close_q = scale_expr_q_close
            if idx == 0:
                flash_q = "(lt(t\\,0.35) * 0.45 * (1.0 - t/0.35))"
                eq_close_q = f"eval=frame:brightness='-0.03 + ({flash_q}) + (0.18 + 0.22*{voice_pulse_q})*({speech_mask_q})':contrast='1.0 + 0.45*({flash_q}) + (0.24 + 0.20*{voice_pulse_q})*({speech_mask_q})':saturation='1.0 + 0.35*({flash_q}) + (0.26 + 0.18*{voice_pulse_q})*({speech_mask_q})'"
                d_cq_y = f"{d_cq_y} + (lt(t\\,0.45) * -28.0 * (1.0 - (sin(PI/2*t/0.45) + 0.10*sin(PI*t/0.45))))"
            else:
                eq_close_q = eq_q

            filter_complex.append(f"[{q_src}]format=yuva420p,scale={sc_close_q},eq={eq_close_q},hue={hue_q},colorchannelmixer=aa=0.98[q_sc_{idx}]")
            filter_complex.append(f"[{cur_v}][q_sc_{idx}]overlay=eval=frame:x='W/2-w/2 + {d_cq_x}':y='H*0.38-h/2 + {d_cq_y}':enable='between(t,{st},{sc_visual_end})'[v_sc_{idx}_q]")
            cur_v = f"v_sc_{idx}_q"

            if has_holo_q and not holo_q_used:
                holo_q_used = True
                filter_complex.append(f"[{cur_v}][holo_q]overlay=eval=frame:x='(W-w)/2':y='H*0.12-h/2 + 6.0*sin(2*PI*(t-{round(st+0.1, 2)})/2.4)':enable='between(t,{round(st+0.1, 2)},{max(round(st+0.2, 2), round(sc_visual_end-0.2, 2))})'[v_sc_{idx}_hq]")
                cur_v = f"v_sc_{idx}_hq"

        elif shot == "close_solar":
            s_src = f"s_close_{s_close_cur}"
            s_close_cur += 1
            # Cinematic Push-In Dolly with Ease-in-Out progression + Lissajous orbital levitation:
            d_cs_x = f"{orbit_lx_s} + {voice_jitter_s}"
            d_cs_y = f"{orbit_ly_s} - 14.0*{prog_expr}"
            sc_close_s = scale_expr_s_close
            if idx == 0:
                flash_s = "(gte(t\\,0.22)*lt(t\\,0.55) * 0.45 * (1.0 - (t-0.22)/0.33))"
                eq_close_s = f"eval=frame:brightness='-0.03 + ({flash_s}) + (0.18 + 0.22*{voice_pulse_s})*({speech_mask_s})':contrast='1.0 + 0.45*({flash_s}) + (0.24 + 0.20*{voice_pulse_s})*({speech_mask_s})':saturation='1.0 + 0.35*({flash_s}) + (0.26 + 0.18*{voice_pulse_s})*({speech_mask_s})'"
                d_cs_y = f"{d_cs_y} + (gte(t\\,0.22)*lt(t\\,0.67) * -28.0 * (1.0 - (sin(PI/2*(t-0.22)/0.45) + 0.10*sin(PI*(t-0.22)/0.45))))"
                s_close_enable = f"between(t\\,0.22\\,{sc_visual_end})"
            else:
                eq_close_s = eq_s
                s_close_enable = f"between(t,{st},{sc_visual_end})"

            filter_complex.append(f"[{s_src}]format=yuva420p,scale={sc_close_s},eq={eq_close_s},hue={hue_s},colorchannelmixer=aa=0.98[s_sc_{idx}]")
            filter_complex.append(f"[{cur_v}][s_sc_{idx}]overlay=eval=frame:x='W/2-w/2 + {d_cs_x}':y='H*0.38-h/2 + {d_cs_y}':enable='{s_close_enable}'[v_sc_{idx}_s]")
            cur_v = f"v_sc_{idx}_s"

        elif shot == "both":
            q_src = f"q_talk_{q_talk_cur}"
            q_talk_cur += 1
            # Cinematic Cosmic Reveal Pull-Back with Smooth Ease-in-out:
            dq_x = f"{orbit_lx_q} + 12.0*(1.0 - {prog_expr}) + {voice_jitter_q}"
            dq_y = f"{orbit_ly_q} + 10.0*{prog_expr}"
            filter_complex.append(f"[{q_src}]format=yuva420p,scale={scale_expr_q_wide},eq={eq_q},hue={hue_q},colorchannelmixer=aa=0.98[q_sc_{idx}]")
            filter_complex.append(f"[{cur_v}][q_sc_{idx}]overlay=eval=frame:x='W*0.25-w/2 + {dq_x}':y='H*0.38-h/2 + {dq_y}':enable='between(t,{st},{sc_visual_end})'[v_sc_{idx}_q]")
            cur_v = f"v_sc_{idx}_q"

            s_src = f"s_talk_{s_talk_cur}"
            s_talk_cur += 1
            ds_x = f"{orbit_lx_s} - 12.0*(1.0 - {prog_expr}) + {voice_jitter_s}"
            ds_y = f"{orbit_ly_s} + 10.0*{prog_expr}"
            filter_complex.append(f"[{s_src}]format=yuva420p,scale={scale_expr_s_wide},eq={eq_s},hue={hue_s},colorchannelmixer=aa=0.98[s_sc_{idx}]")
            filter_complex.append(f"[{cur_v}][s_sc_{idx}]overlay=eval=frame:x='W*0.75-w/2 - 28 + {ds_x}':y='H*0.39-h/2 + {ds_y}':enable='between(t,{st},{sc_visual_end})'[v_sc_{idx}_s]")
            cur_v = f"v_sc_{idx}_s"

    # Global Foreground Particle Atmosphere Overlay (Submerges the orbs in 3D floating space)
    if has_atmos and atmos_idx is not None:
        filter_complex.append(f"[{cur_v}][{atmos_idx}:v]overlay=0:0:enable='between(t,0,{total_duration})'[v_atmos]")
        cur_v = "v_atmos"

    # 3-Second Micro-Dolly Zoom Hook (Cinematic camera push-in 1.0x -> 1.08x during initial 3s retention window)
    filter_complex.append(f"[{cur_v}]zoompan=z='min(1.08\\,1.0+0.08*on/(30*3.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={width}x{height}:fps=30[v_dolly]")
    cur_v = "v_dolly"

    # Option 1: Initial Plasma Shockwave Impulse (Ráfaga Magnética Inicial t = 0.0s -> 0.28s)
    flash_impulse = "(gt(t\\,0)*lt(t\\,0.28) * 0.50 * (1.0 - t/0.28))"
    filter_complex.append(f"[{cur_v}]eq=brightness='({flash_impulse})':contrast='1.0 + ({flash_impulse})':saturation='1.0 + 0.65*({flash_impulse})'[v_shock]")
    cur_v = "v_shock"

    # Headline Hook (Cinematic Floating Title Top Center during first scene - No heavy opaque box)
    first_sc_end = min(scene_records[0]["end"] if scene_records else 2.8, 2.8)
    filter_complex.append(f"[{cur_v}]drawtext=text='{escaped_headline_hook}':{font_param}:fontcolor=0xFFFFFF:fontsize=42:borderw=3:bordercolor=0x000000@0.8:shadowx=2:shadowy=3:shadowcolor=0x00f0ff@0.4:x=(w-text_w)/2:y=140:enable='between(t,0,{first_sc_end})'[v_hook]")
    cur_v = "v_hook"

    # Outro Reflection Badge removed per user request
    # Subtitles overlay
    filter_complex.append(f"[{cur_v}]ass='{escaped_ass_path}'[vout]")

    filter_str = ";".join(filter_complex)
    filter_script_path = output_path.parent / f"_temp_filter_{output_path.stem}.txt"
    with open(filter_script_path, "w", encoding="utf-8") as f_script:
        f_script.write(filter_str)

    cmd = [
        "ffmpeg", "-y",
        *cmd_inputs,
        "-filter_complex_script", str(filter_script_path),
        "-map", "[vout]",
        "-map", f"{audio_idx}:a",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "17",
        "-maxrate", "16M",
        "-bufsize", "32M",
        "-profile:v", "high",
        "-level:v", "4.2",
        "-g", "60",
        "-keyint_min", "30",
        "-sc_threshold", "0",
        "-color_primaries", "bt709",
        "-color_trc", "bt709",
        "-colorspace", "bt709",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "48000",
        "-shortest",
        "-movflags", "+faststart",
        str(output_path)
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"  ❌ FFmpeg render error: {e.stderr.decode('utf-8') if e.stderr else str(e)}")
        raise e
    finally:
        for p in [temp_test_audio, ass_sub_path, filter_script_path]:
            if p and p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass

    print(f"\n✨ ¡Vista previa del Orbe Bio-Reactivo generada con éxito!")
    print(f"🎬 Video listo: {output_path.resolve()}\n")

    # Generate companion studio-grade thumbnail
    thumb_path = output_path.parent / "thumbnail.jpg"
    try:
        from ai.thumbnail_generator import ThumbnailGenerator
        thumb_gen = ThumbnailGenerator()
        thumb_gen.render_studio_poster(
            hook=headline_hook,
            topic=topic or "Física Cuántica vs Astrofísica Solar",
            output_path=thumb_path
        )
    except Exception:
        # Robust zero-dependency fallback: Extract crisp video frame with FFmpeg
        try:
            subprocess.run([
                "ffmpeg", "-y", "-ss", "00:00:02.000",
                "-i", str(output_path),
                "-vframes", "1",
                "-q:v", "2",
                str(thumb_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception:
            pass

    return output_path


# Alias for explicit AI debate generation calls
render_cohost_debate_video = render_orb_test_preview
