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
    canvas_size: int = 600,
    fps: int = 30,
    loop_frames: int = 60,
    target_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> Path:
    """
    Generates a 60-frame (2.0s @ 30FPS) seamless, transparent QuickTime MOV loop (qtrle codec)
    containing an ultra-clean bio-reactive bioluminescent sphere matching the user's reference image.
    """
    palette_key = palette_key.lower().strip()
    if palette_key not in ORB_PALETTES:
        palette_key = "quantum"
    palette = ORB_PALETTES[palette_key]

    dest_dir = target_dir or (Path(__file__).resolve().parent.parent / "assets" / "orbs")
    dest_dir.mkdir(parents=True, exist_ok=True)
    mov_path = dest_dir / f"orb_loop_{palette_key}.mov"

    if not force_refresh and mov_path.exists() and mov_path.stat().st_size > 10000:
        return mov_path

    print(f"  🔮 Generando orbe bio-reactivo 3D ('{palette_key}')...")

    frames_dir = dest_dir / f"_temp_frames_{palette_key}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    c = canvas_size // 2
    r_sphere_base = int(canvas_size * 0.27)
    r_aura_outer_base = int(canvas_size * 0.48)
    r_aura_inner_base = int(canvas_size * 0.38)

    try:
        for i in range(loop_frames):
            t = i / loop_frames
            tau = 2 * math.pi * t

            # 1. Subtle Organic Breathing Scale Animation (Sphere swells and shrinks like a living organism)
            r_sphere = int(r_sphere_base + 10 * math.sin(tau))

            # 2. Concentric surrounding ring expands & contracts in sync with breathing
            ring_r = int(r_sphere + 22 - 16 * math.cos(2.0 * tau))
            ring_r_outer_glow = ring_r + 5

            # 3. Rich atmospheric volumetric aura swells dynamically (+/- 18px)
            r_aura_outer = int(r_aura_outer_base + 18 * math.sin(tau))
            r_aura_inner = int(r_aura_inner_base + 14 * math.sin(tau))
            r_ambient_spill = int((canvas_size * 0.46) + 22 * math.sin(tau))

            # 4. Core light spot breathing (Primary Top-Left Spot)
            spot1_x = int(c - r_sphere * 0.32 + 8 * math.sin(tau))
            spot1_y = int(c - r_sphere * 0.28 + 6 * math.cos(tau))
            spot1_rx = int(r_sphere * 0.52 + 6 * math.sin(2 * tau))
            spot1_ry = int(r_sphere * 0.48 + 5 * math.cos(2 * tau))

            # 5. Secondary Counter-Tone Light Spot (Bottom-Right Flare)
            spot2_x = int(c + r_sphere * 0.30 - 8 * math.sin(tau))
            spot2_y = int(c + r_sphere * 0.28 - 6 * math.cos(tau))
            spot2_rx = int(r_sphere * 0.44 + 5 * math.cos(2 * tau))
            spot2_ry = int(r_sphere * 0.40 + 4 * math.sin(2 * tau))

            svg = f"""<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Enhanced Ultra-Wide Environmental Ambient Illumination Filter -->
    <filter id="ambientSpillBlur_{i}" x="-90%" y="-90%" width="280%" height="280%">
      <feGaussianBlur stdDeviation="70" />
    </filter>
    <filter id="auraGlowDeep_{i}" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="34" />
    </filter>
    <filter id="auraGlowMid_{i}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="20" />
    </filter>
    <filter id="coreBlur_{i}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="11" />
    </filter>
    <filter id="secondaryBlur_{i}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="14" />
    </filter>
    <filter id="ringGlow_{i}" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="9" />
    </filter>

    <clipPath id="sphereClip_{i}">
      <circle cx="{c}" cy="{c}" r="{r_sphere}" />
    </clipPath>

    <!-- Environmental Ambient Light Spill (High-Intensity Radial Wash) -->
    <radialGradient id="ambientSpill_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['spot1_glow']}" stop-opacity="0.95" />
      <stop offset="25%" stop-color="{palette['aura_inner']}" stop-opacity="0.75" />
      <stop offset="55%" stop-color="{palette['aura_outer']}" stop-opacity="0.45" />
      <stop offset="82%" stop-color="{palette['body_c3']}" stop-opacity="0.20" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <!-- Expansive Multi-Stop Atmospheric Neon Volumetric Aura -->
    <radialGradient id="outerAuraDeep_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['aura_inner']}" stop-opacity="0.95" />
      <stop offset="35%" stop-color="{palette['aura_mid']}" stop-opacity="0.75" />
      <stop offset="68%" stop-color="{palette['aura_outer']}" stop-opacity="0.38" />
      <stop offset="88%" stop-color="{palette['body_c3']}" stop-opacity="0.15" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <radialGradient id="innerAuraBright_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['aura_bright']}" stop-opacity="0.90" />
      <stop offset="45%" stop-color="{palette['aura_inner']}" stop-opacity="0.60" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <!-- Multi-Spectral Chromatic Sphere Body Gradient -->
    <radialGradient id="sphereBody_{i}" cx="42%" cy="38%" r="62%">
      <stop offset="0%" stop-color="{palette['body_c0']}" />
      <stop offset="22%" stop-color="{palette['body_c1']}" />
      <stop offset="48%" stop-color="{palette['body_c2']}" />
      <stop offset="72%" stop-color="{palette['body_c3']}" />
      <stop offset="88%" stop-color="{palette['body_c4']}" />
      <stop offset="100%" stop-color="{palette['body_c5']}" />
    </radialGradient>

    <!-- Primary Off-Center Light Spot (White Center to Primary Flare) -->
    <radialGradient id="primarySpot_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['spot1_core']}" stop-opacity="1.0" />
      <stop offset="26%" stop-color="{palette['spot1_glow']}" stop-opacity="0.95" />
      <stop offset="60%" stop-color="{palette['spot1_outer']}" stop-opacity="0.65" />
      <stop offset="100%" stop-color="{palette['body_c3']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- Secondary Counter-Tone Light Spot (Secondary Flare) -->
    <radialGradient id="secondarySpot_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['spot2_core']}" stop-opacity="0.90" />
      <stop offset="40%" stop-color="{palette['spot2_mid']}" stop-opacity="0.65" />
      <stop offset="80%" stop-color="{palette['spot2_outer']}" stop-opacity="0.30" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>
  </defs>

  <!-- 0. Environmental Ambient Illumination (Radiates soft ambient light into surrounding space) -->
  <circle cx="{c}" cy="{c}" r="{canvas_size // 2 - 10}" fill="url(#ambientSpill_{i})" filter="url(#ambientSpillBlur_{i})" />

  <!-- 1. Rich Atmospheric Neon Bloom (Deep + Mid Layered Aura) -->
  <circle cx="{c}" cy="{c}" r="{r_aura_outer}" fill="url(#outerAuraDeep_{i})" filter="url(#auraGlowDeep_{i})" />
  <circle cx="{c}" cy="{c}" r="{r_aura_inner}" fill="url(#innerAuraBright_{i})" filter="url(#auraGlowMid_{i})" />

  <!-- 2. Concentric Surrounding Ring (Expanding & Contracting Fast until touching sphere edge) -->
  <circle cx="{c}" cy="{c}" r="{ring_r_outer_glow}" fill="none" stroke="{palette['aura_inner']}" stroke-width="7" opacity="0.85" filter="url(#ringGlow_{i})" />
  <circle cx="{c}" cy="{c}" r="{ring_r}" fill="none" stroke="{palette['ring_stroke']}" stroke-width="2.8" opacity="0.95" />

  <!-- 3. Sphere Body -->
  <circle cx="{c}" cy="{c}" r="{r_sphere}" fill="url(#sphereBody_{i})" />

  <!-- 4. Multi-Spectral Interior Light Layers -->
  <g clip-path="url(#sphereClip_{i})">
    <!-- Secondary Counter-Tone Flare (Bottom-Right) -->
    <ellipse cx="{spot2_x}" cy="{spot2_y}" rx="{spot2_rx}" ry="{spot2_ry}" fill="url(#secondarySpot_{i})" filter="url(#secondaryBlur_{i})" />

    <!-- Primary Incandescent Flare (Top-Left) -->
    <ellipse cx="{spot1_x}" cy="{spot1_y}" rx="{spot1_rx}" ry="{spot1_ry}" fill="url(#primarySpot_{i})" filter="url(#coreBlur_{i})" />
    <circle cx="{spot1_x}" cy="{spot1_y}" r="{int(spot1_rx * 0.45)}" fill="{palette['spot1_core']}" opacity="0.98" filter="url(#coreBlur_{i})" />

    <!-- Subsurface Rim Accent -->
    <circle cx="{c}" cy="{c}" r="{r_sphere - 3}" fill="none" stroke="{palette['rim_stroke']}" stroke-width="4" opacity="0.55" filter="url(#coreBlur_{i})" />
  </g>

  <!-- 5. Inner Concentric Rim Light -->
  <circle cx="{c}" cy="{c}" r="{r_sphere - 2}" fill="none" stroke="{palette['aura_inner']}" stroke-width="3" opacity="0.75" />
</svg>"""
            (frames_dir / f"frame_{i:03d}.svg").write_text(svg, encoding="utf-8")

        subprocess.run([
            "ffmpeg", "-y", "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%03d.svg"),
            "-c:v", "qtrle",
            str(mov_path)
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return mov_path
    finally:
        if frames_dir.exists():
            shutil.rmtree(frames_dir, ignore_errors=True)


def get_or_create_orb_asset(
    palette: str = "quantum",
    target_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> Path:
    """Retrieves or generates a transparent QuickTime MOV loop for the AI Presenter entity."""
    return generate_animated_orb_loop(
        palette_key=palette,
        canvas_size=600,
        fps=30,
        loop_frames=60,
        target_dir=target_dir,
        force_refresh=force_refresh
    )


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
        """Calculates 2D organic floating drift coordinates for the AI Presenter entity."""
        base_x = f"(W-w)/2"
        base_y = f"(H-h)/2 - {int(video_height * 0.05)}"
        x_anim = f"{base_x} + 18*sin(2*PI*t/3.6)"
        y_anim = f"{base_y} + 24*sin(2*PI*t/2.4)"
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
        Builds the FFmpeg filter chain that applies speech-envelope audio reactivity
        on top of the continuously breathing transparent MOV loop stream.
        """
        target_size = self.pixel_size
        effective_opacity = self.opacity
        speech_intervals: List[Tuple[float, float]] = []

        if self.audio_path and self.audio_path.exists():
            speech_intervals = extract_audio_speech_envelope(self.audio_path)

        filters = []
        scale_expr = f"{target_size}:{target_size}"

        if speech_intervals:
            conds = [f"between(t,{start:.2f},{end:.2f})" for start, end in speech_intervals]
            speech_mask = f"min(1,{'+'.join(conds)})"
            # Active voice ripple (small micro-modulation of speaking intensity)
            voice_ripple = f"(0.5 + 0.5 * sin(2*PI*t/0.38))"

            # Dynamic Speech Reactivity (Highly Luminous Active State & Dimmed Rest State):
            # - Silence Pause (speech_mask = 0): Dims down gracefully (brightness -0.12, contrast 0.80, sat 0.75)
            # - Active Speech (speech_mask = 1): Maintains a bright glowing baseline (+0.16) with subtle voice ripples (up to +0.24)
            eq_expr = f"brightness='-0.12 + (0.28 + 0.08*{voice_ripple})*{speech_mask}':contrast='0.80 + (0.35 + 0.15*{voice_ripple})*{speech_mask}'"
            hue_expr = f"h='(12 + 4*{voice_ripple})*{speech_mask} + 6*sin(2*PI*t/2.4)':s='0.75 + (0.45 + 0.20*{voice_ripple})*{speech_mask}'"

            filters.append(f"[{input_idx}:v]scale={scale_expr}")
            filters.append(f"eq={eq_expr}")
            filters.append(f"hue={hue_expr}")
            filters.append("format=yuva420p")
            filters.append(f"colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]")
        else:
            hue_expr = "h='10*sin(2*PI*t/2.5)':s='1.0 + 0.08*sin(2*PI*t/2.5)'"

            filters.append(f"[{input_idx}:v]scale={scale_expr}")
            filters.append(f"hue={hue_expr}")
            filters.append("format=yuva420p")
            filters.append(f"colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]")

        return ",".join(filters)


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
    headline_hook: str = "⚡ PARADOJA CUÁNTICA VS FÍSICA SOLAR ⚡",
    topic: Optional[str] = None,
    debate_script: Optional[Dict[str, Any]] = None,
    llm_provider: str = "groq",
    gemini_key: Optional[str] = None,
    groq_key: Optional[str] = None,
    openai_key: Optional[str] = None,
    enable_review: bool = True,
) -> Optional[Path]:
    """Renders a stunning co-host conversation video with two bio-reactive orbs and dynamic camera cuts."""
    # 1. If topic is provided and debate_script is not provided, generate with AI
    if not debate_script and topic:
        from ai.debate_generator import DebateScriptGenerator
        gen = DebateScriptGenerator(
            preferred_provider=llm_provider,
            gemini_key=gemini_key,
            groq_key=groq_key,
            openai_key=openai_key,
            enable_review=enable_review
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
                {"speaker": "Quantum", "entity": "quantum", "text": "Bienvenido al canal cósmico.", "shot": "wide"},
                {"speaker": "Solar", "entity": "solar", "text": "Explorando los misterios del cosmos.", "shot": "close_solar"},
                {"speaker": "Quantum", "entity": "quantum", "text": "Cada átomo cuenta una historia infinita.", "shot": "close_quantum"},
                {"speaker": "Ambos", "entity": "both", "text": "El universo continúa expandiéndose.", "shot": "both"}
            ]

        script_json_path = output_path.parent / "script.json"
        script_json_path.write_text(json.dumps(debate_script, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        scenes = [
            {"speaker": "Quantum", "entity": "quantum", "text": q_part1, "shot": "wide"},
            {"speaker": "Quantum", "entity": "quantum", "text": q_part2, "shot": "close_quantum"},
            {"speaker": "Solar", "entity": "solar", "text": s_part3, "shot": "close_solar"},
            {"speaker": "Ambos", "entity": "both", "text": both_part4, "shot": "both"}
        ]

    print(f"\n🔮 [AI Co-Host Debate Express] Renderizando video dinámico ({len(scenes)} escenas) con Doble Orbe y Multi-Cámara...")
    print(f"   • Orbe 1: QUANTUM (Azul Eléctrico / Cyan) | Orbe 2: SOLAR (Ámbar / Oro)")
    print(f"   • Hook: {headline_hook}")
    if has_holo_q:
        print(f"   • HUD Holográfico Q: [{holo_q_cat}] {holo_q_title} -> {holo_q_sub}")
    if has_holo_s:
        print(f"   • HUD Holográfico S: [{holo_s_cat}] {holo_s_title} -> {holo_s_sub}")

    # Generate both orb visual assets
    orb_quantum = get_or_create_orb_asset(palette="quantum", force_refresh=True)
    orb_solar = get_or_create_orb_asset(palette="solar", force_refresh=True)

    # Generate Holographic Floating Reference Cards (Only if required by script)
    from video.hologram import generate_hologram_card_svg, generate_presenter_badge_svg
    holo_q_path = output_path.parent / "_holo_q.svg"
    holo_s_path = output_path.parent / "_holo_s.svg"
    badge_q_path = output_path.parent / "_badge_q.svg"
    badge_s_path = output_path.parent / "_badge_s.svg"

    if has_holo_q:
        generate_hologram_card_svg(
            title=holo_q_title,
            subtitle=holo_q_sub,
            category=holo_q_cat,
            color_theme="cyan",
            width=620,
            height=240,
            output_path=holo_q_path
        )
    if has_holo_s:
        generate_hologram_card_svg(
            title=holo_s_title,
            subtitle=holo_s_sub,
            category=holo_s_cat,
            color_theme="amber",
            width=620,
            height=240,
            output_path=holo_s_path
        )

    generate_presenter_badge_svg(
        name="QUANTUM",
        role="IA Física Cuántica",
        color_theme="cyan",
        width=380,
        height=110,
        output_path=badge_q_path
    )
    generate_presenter_badge_svg(
        name="SOLAR",
        role="IA Astrofísica Solar",
        color_theme="amber",
        width=380,
        height=110,
        output_path=badge_s_path
    )

    temp_test_audio: Optional[Path] = output_path.parent / "_temp_cohost_debate.mp3"
    resolved_audio: Optional[Path] = sample_audio

    scene_records = []
    temp_audio_files_to_clean = []

    if not resolved_audio:
        from audio.tts import EdgeTTSProvider, GoogleTTSProvider
        from audio.sfx import synthesize_camera_servo_sfx, synthesize_space_ambient_pad
        from audio.music import MusicManager

        tts_edge = EdgeTTSProvider()
        test_file = output_path.parent / "_test_probe.mp3"
        use_cosmic_edge = tts_edge.synthesize_text("Hola", test_file)
        if test_file.exists():
            test_file.unlink()

        tts_fallback = GoogleTTSProvider(language="es") if not use_cosmic_edge else None

        current_audio_time = 0.0
        pause_between_scenes = 0.18

        for idx, sc in enumerate(scenes):
            spk_raw = str(sc.get("speaker", "Quantum")).strip()
            ent_raw = str(sc.get("entity", "quantum")).strip().lower()
            text = str(sc.get("text", "")).strip()
            shot = str(sc.get("shot", "wide")).strip().lower()

            if "solar" in ent_raw or "solar" in spk_raw.lower():
                ent = "solar"
                spk = "Solar"
            elif "ambos" in ent_raw or "both" in ent_raw or "ambos" in spk_raw.lower() or "dual" in spk_raw.lower():
                ent = "both"
                spk = "Ambos"
            else:
                ent = "quantum"
                spk = "Quantum"

            # Auto-align shot if missing or mismatch
            if shot not in ["wide", "close_quantum", "close_solar", "both"]:
                if ent == "solar":
                    shot = "close_solar"
                elif ent == "both":
                    shot = "both"
                elif idx == 0:
                    shot = "wide"
                else:
                    shot = "close_quantum"

            scene_audio_paths = []

            if ent == "both":
                p_q = output_path.parent / f"_temp_sc_{idx}_both_q.mp3"
                p_s = output_path.parent / f"_temp_sc_{idx}_both_s.mp3"
                temp_audio_files_to_clean.extend([p_q, p_s])
                if use_cosmic_edge:
                    tts_edge.synthesize_cosmic_entity(text, p_q, entity="quantum")
                    tts_edge.synthesize_cosmic_entity(text, p_s, entity="solar")
                else:
                    tts_fallback.synthesize_text(text, p_q)
                    tts_fallback.synthesize_text(text, p_s)
                dur = max(_get_audio_duration_secs(p_q, 2.5), _get_audio_duration_secs(p_s, 2.5))
                scene_audio_paths = [p_q, p_s]
            else:
                p_sc = output_path.parent / f"_temp_sc_{idx}_{ent}.mp3"
                temp_audio_files_to_clean.append(p_sc)
                if use_cosmic_edge:
                    tts_edge.synthesize_cosmic_entity(text, p_sc, entity=ent)
                else:
                    tts_fallback.synthesize_text(text, p_sc)
                dur = _get_audio_duration_secs(p_sc, 3.0)
                scene_audio_paths = [p_sc]

            s_start = round(current_audio_time, 2)
            s_end = round(s_start + dur, 2)
            current_audio_time = round(s_end + pause_between_scenes, 2)

            scene_records.append({
                "index": idx,
                "speaker": spk,
                "entity": ent,
                "text": text,
                "shot": shot,
                "start": s_start,
                "end": s_end,
                "audio_paths": scene_audio_paths
            })

        total_duration = round(max(current_audio_time + 0.6, 8.0), 2)
        print(f"   • Línea de Tiempo Dialéctica Multi-Escena ({len(scene_records)} escenas):")
        for sc in scene_records:
            print(f"     - Escena {sc['index']+1} [{sc['speaker']}] ({sc['shot']}): {sc['start']}s -> {sc['end']}s | \"{sc['text'][:45]}...\"")
        print(f"     - Duración Total: {total_duration}s")

        # Synthesize camera transition SFX & entity stingers
        sfx_intro_path = output_path.parent / "_temp_sfx_intro.wav"
        sfx_zoom_path = output_path.parent / "_temp_sfx_zoom.wav"
        sfx_pan_path = output_path.parent / "_temp_sfx_pan.wav"
        sfx_res_path = output_path.parent / "_temp_sfx_res.wav"
        music_bg_path = output_path.parent / "_temp_music_ambient.wav"
        temp_audio_files_to_clean.extend([sfx_intro_path, sfx_zoom_path, sfx_pan_path, sfx_res_path])

        synthesize_camera_servo_sfx(sfx_intro_path, duration=1.1, sfx_type="intro")
        synthesize_camera_servo_sfx(sfx_zoom_path, duration=0.52, sfx_type="whoosh_quantum")
        synthesize_camera_servo_sfx(sfx_pan_path, duration=0.52, sfx_type="whoosh_solar")
        synthesize_camera_servo_sfx(sfx_res_path, duration=2.5, sfx_type="cosmic_resonance")

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

        # Add SFX
        audio_inputs.extend(["-i", str(sfx_intro_path)])
        audio_filter_lines.append(f"[{stream_idx}:a]adelay=20|20,volume=0.40[sfx_intro]")
        mix_inputs.append("[sfx_intro]")
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
    speech_mask_q = " + ".join(speech_q_conditions) if speech_q_conditions else "0"

    speech_s_conditions = [f"between(t,{sc['start']},{sc['end']})" for sc in scene_records if sc["entity"] in ["solar", "both"]]
    speech_mask_s = " + ".join(speech_s_conditions) if speech_s_conditions else "0"

    voice_pulse_q = "(0.5 + 0.35*sin(2*PI*t/0.16) + 0.15*cos(2*PI*t/0.28))"
    eq_q = f"brightness='-0.18 + (0.36 + 0.12*{voice_pulse_q})*({speech_mask_q})':contrast='0.70 + (0.60 + 0.22*{voice_pulse_q})*({speech_mask_q})'"
    hue_q = f"h='(14 + 6*{voice_pulse_q})*({speech_mask_q}) + 6*sin(2*PI*t/2.4)':s='0.60 + (0.70 + 0.25*{voice_pulse_q})*({speech_mask_q})'"

    voice_pulse_s = "(0.5 + 0.35*sin(2*PI*t/0.14) + 0.15*cos(2*PI*t/0.26))"
    eq_s = f"brightness='-0.04 + (0.22 + 0.10*{voice_pulse_s})*({speech_mask_s})':contrast='0.92 + (0.28 + 0.14*{voice_pulse_s})*({speech_mask_s})'"
    hue_s = f"h='(14 + 6*{voice_pulse_s})*({speech_mask_s}) + 6*sin(2*PI*t/2.4)':s='0.85 + (0.50 + 0.20*{voice_pulse_s})*({speech_mask_s})'"

    drift_q_active_x = "14.0*sin(2*PI*t/3.6)"
    drift_q_active_y = "18.0*sin(2*PI*t/2.4)"
    drift_q_resting_x = "4.0*sin(2*PI*t/3.6)"
    drift_q_resting_y = "5.0*sin(2*PI*t/2.4)"

    drift_s_active_x = "14.0*sin(2*PI*t/3.2)"
    drift_s_active_y = "18.0*sin(2*PI*t/2.8)"
    drift_s_resting_x = "4.0*sin(2*PI*t/3.2)"
    drift_s_resting_y = "5.0*sin(2*PI*t/2.8)"

    drift_intro_x = "30.0*exp(-7.0*t)*cos(16.0*t)"
    drift_intro_y = "35.0*exp(-7.0*t)*sin(16.0*t)"

    from utils.fonts import resolve_best_font_path
    font_param, _ = resolve_best_font_path()

    escaped_headline_hook = headline_hook.replace(":", "\\:").replace("'", "\\'")

    # High-Performance Futuristic ASS Karaoke Subtitles (Using ALL dynamic scenes)
    from subtitles.generator import generate_cosmic_debate_karaoke_ass
    ass_sub_path = output_path.parent / "_temp_debate_karaoke.ass"
    generate_cosmic_debate_karaoke_ass(scene_records, ass_sub_path, width=width, height=height)
    escaped_ass_path = str(ass_sub_path.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")

    bg_input = f"color=c=0x08090f:s={width}x{height}:r=30:d={total_duration}"

    # Build FFmpeg command inputs
    cmd_inputs = [
        "-f", "lavfi", "-i", bg_input,
        "-stream_loop", "-1", "-i", str(orb_quantum),
        "-stream_loop", "-1", "-i", str(orb_solar),
    ]
    curr_input_idx = 3

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

    cmd_inputs.extend(["-stream_loop", "-1", "-i", str(badge_q_path)])
    badge_q_idx = curr_input_idx
    curr_input_idx += 1

    cmd_inputs.extend(["-stream_loop", "-1", "-i", str(badge_s_path)])
    badge_s_idx = curr_input_idx
    curr_input_idx += 1

    audio_idx = curr_input_idx
    if resolved_audio and resolved_audio.exists():
        cmd_inputs.extend(["-i", str(resolved_audio)])
    else:
        cmd_inputs.extend(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"])

    pre_scale_lines = []
    if has_holo_q and holo_q_idx is not None:
        pre_scale_lines.append(f"[{holo_q_idx}:v]scale=540:-2,format=yuva420p[holo_q]")
    if has_holo_s and holo_s_idx is not None:
        pre_scale_lines.append(f"[{holo_s_idx}:v]scale=540:-2,format=yuva420p[holo_s]")
    pre_scale_lines.append(f"[{badge_q_idx}:v]scale=340:-2,format=yuva420p[badge_q]")
    pre_scale_lines.append(f"[{badge_s_idx}:v]scale=340:-2,format=yuva420p[badge_s]")

    # Calculate exact number of split pads needed for Quantum and Solar
    q_uses = 1 + sum(1 for sc in scene_records if sc["shot"] in ["wide", "both", "close_quantum"])
    s_uses = 1 + sum(1 for sc in scene_records if sc["shot"] in ["wide", "both", "close_solar"])

    filter_complex = [
        *pre_scale_lines,
        f"[1:v]split={q_uses}" + "".join(f"[q_in_{k}]" for k in range(q_uses)),
        f"[2:v]split={s_uses}" + "".join(f"[s_in_{k}]" for k in range(s_uses)),

        # Background Ambient Luminescence
        f"[q_in_0]scale=120:120,eq={eq_q},hue={hue_q},boxblur=24:3,scale=1080:1920,format=yuva420p,colorchannelmixer=aa=0.25[bg_glow_q]",
        f"[s_in_0]scale=120:120,eq={eq_s},hue={hue_s},boxblur=24:3,scale=1080:1920,format=yuva420p,colorchannelmixer=aa=0.25[bg_glow_s]",

        f"[0:v]eq=brightness=-0.01:contrast=1.05[bg_graded]",
        f"[bg_graded][bg_glow_q]overlay=eval=frame:enable='{speech_mask_q}'[bg_glowed_1]",
        f"[bg_glowed_1][bg_glow_s]overlay=eval=frame:enable='{speech_mask_s}'[bg_ambient]"
    ]

    cur_v = "bg_ambient"
    q_cur = 1
    s_cur = 1
    holo_q_used = False
    holo_s_used = False

    for idx, sc in enumerate(scene_records):
        st = sc["start"]
        et = sc["end"]
        ent = sc["entity"]
        shot = sc["shot"]

        intro_dx = f" + {drift_intro_x}" if idx == 0 else ""
        intro_dy = f" + {drift_intro_y}" if idx == 0 else ""

        if shot == "wide":
            is_q_active = (ent in ["quantum", "both"])
            dq_x = drift_q_active_x if is_q_active else drift_q_resting_x
            dq_y = drift_q_active_y if is_q_active else drift_q_resting_y
            q_alpha = 0.95 if is_q_active else 0.65

            is_s_active = (ent in ["solar", "both"])
            ds_x = drift_s_active_x if is_s_active else drift_s_resting_x
            ds_y = drift_s_active_y if is_s_active else drift_s_resting_y
            s_alpha = 0.95 if is_s_active else 0.65

            filter_complex.append(f"[q_in_{q_cur}]scale=355:355,eq={eq_q},hue={hue_q},format=yuva420p,colorchannelmixer=aa={q_alpha}[q_sc_{idx}]")
            filter_complex.append(f"[{cur_v}][q_sc_{idx}]overlay=eval=frame:x='W*0.25-w/2 + {dq_x}{intro_dx}':y='H*0.38-h/2 + {dq_y}{intro_dy}':enable='between(t,{st},{et})'[v_sc_{idx}_q]")
            cur_v = f"v_sc_{idx}_q"
            q_cur += 1

            filter_complex.append(f"[s_in_{s_cur}]scale=310:310,eq={eq_s},hue={hue_s},format=yuva420p,colorchannelmixer=aa={s_alpha}[s_sc_{idx}]")
            filter_complex.append(f"[{cur_v}][s_sc_{idx}]overlay=eval=frame:x='W*0.75-w/2 - 28 + {ds_x}{intro_dx}':y='H*0.39-h/2 + {ds_y}{intro_dy}':enable='between(t,{st},{et})'[v_sc_{idx}_s]")
            cur_v = f"v_sc_{idx}_s"
            s_cur += 1

            if idx == 0:
                bdg_end = min(round(et - 0.2, 2), 2.8)
                filter_complex.append(f"[{cur_v}][badge_q]overlay=eval=frame:x='W*0.25-w/2 + 5.0*sin(2*PI*(t-0.4)/2.2)':y='H*0.52-h/2 + 4.0*cos(2*PI*(t-0.4)/2.2)':enable='between(t,0.3,{bdg_end})'[v_sc_{idx}_bq]")
                filter_complex.append(f"[v_sc_{idx}_bq][badge_s]overlay=eval=frame:x='W*0.75-w/2 - 28 + 5.0*cos(2*PI*(t-0.4)/2.4)':y='H*0.52-h/2 + 4.0*sin(2*PI*(t-0.4)/2.4)':enable='between(t,0.3,{bdg_end})'[v_sc_{idx}_bs]")
                cur_v = f"v_sc_{idx}_bs"

        elif shot == "close_quantum":
            filter_complex.append(f"[q_in_{q_cur}]scale=550:550,eq={eq_q},hue={hue_q},format=yuva420p,colorchannelmixer=aa=0.98[q_sc_{idx}]")
            filter_complex.append(f"[{cur_v}][q_sc_{idx}]overlay=eval=frame:x='W/2-w/2 + {drift_q_active_x} + 25.0*exp(-6.5*(t-{st}))*cos(16.0*(t-{st}))':y='H*0.38-h/2 + {drift_q_active_y} + 30.0*exp(-6.5*(t-{st}))*sin(16.0*(t-{st}))':enable='between(t,{st},{et})'[v_sc_{idx}_q]")
            cur_v = f"v_sc_{idx}_q"
            q_cur += 1

            if has_holo_q and not holo_q_used:
                holo_q_used = True
                filter_complex.append(f"[{cur_v}][holo_q]overlay=eval=frame:x='(W-w)/2':y='H*0.12-h/2 + 6.0*sin(2*PI*(t-{round(st+0.1, 2)})/2.4)':enable='between(t,{round(st+0.1, 2)},{max(round(st+0.2, 2), round(et-0.2, 2))})'[v_sc_{idx}_hq]")
                cur_v = f"v_sc_{idx}_hq"

        elif shot == "close_solar":
            filter_complex.append(f"[s_in_{s_cur}]scale=550:550,eq={eq_s},hue={hue_s},format=yuva420p,colorchannelmixer=aa=0.98[s_sc_{idx}]")
            filter_complex.append(f"[{cur_v}][s_sc_{idx}]overlay=eval=frame:x='W/2-w/2 + {drift_s_active_x} + 25.0*exp(-6.5*(t-{st}))*cos(16.0*(t-{st}))':y='H*0.38-h/2 + {drift_s_active_y} + 30.0*exp(-6.5*(t-{st}))*sin(16.0*(t-{st}))':enable='between(t,{st},{et})'[v_sc_{idx}_s]")
            cur_v = f"v_sc_{idx}_s"
            s_cur += 1

            if has_holo_s and not holo_s_used:
                holo_s_used = True
                filter_complex.append(f"[{cur_v}][holo_s]overlay=eval=frame:x='(W-w)/2':y='H*0.12-h/2 + 6.0*cos(2*PI*(t-{round(st+0.1, 2)})/2.6)':enable='between(t,{round(st+0.1, 2)},{max(round(st+0.2, 2), round(et-0.2, 2))})'[v_sc_{idx}_hs]")
                cur_v = f"v_sc_{idx}_hs"

        elif shot == "both":
            filter_complex.append(f"[q_in_{q_cur}]scale=355:355,eq={eq_q},hue={hue_q},format=yuva420p,colorchannelmixer=aa=0.98[q_sc_{idx}]")
            filter_complex.append(f"[{cur_v}][q_sc_{idx}]overlay=eval=frame:x='W*0.25-w/2 + {drift_q_active_x} + 15.0*exp(-6.5*(t-{st}))*cos(16.0*(t-{st}))':y='H*0.38-h/2 + {drift_q_active_y} + 18.0*exp(-6.5*(t-{st}))*sin(16.0*(t-{st}))':enable='between(t,{st},{et})'[v_sc_{idx}_q]")
            cur_v = f"v_sc_{idx}_q"
            q_cur += 1

            filter_complex.append(f"[s_in_{s_cur}]scale=355:355,eq={eq_s},hue={hue_s},format=yuva420p,colorchannelmixer=aa=0.98[s_sc_{idx}]")
            filter_complex.append(f"[{cur_v}][s_sc_{idx}]overlay=eval=frame:x='W*0.75-w/2 - 28 + {drift_s_active_x} + 15.0*exp(-6.5*(t-{st}))*cos(16.0*(t-{st}))':y='H*0.39-h/2 + {drift_s_active_y} + 18.0*exp(-6.5*(t-{st}))*sin(16.0*(t-{st}))':enable='between(t,{st},{et})'[v_sc_{idx}_s]")
            cur_v = f"v_sc_{idx}_s"
            s_cur += 1

    # Headline Hook Badge (Top Center during first scene)
    first_sc_end = min(scene_records[0]["end"] if scene_records else 2.8, 2.8)
    filter_complex.append(f"[{cur_v}]drawtext=text='{escaped_headline_hook}':{font_param}:fontcolor=white:fontsize=34:box=1:boxcolor=0x08101e@0.92:boxborderw=20:borderw=2:bordercolor=0x00f0ff:x=(w-text_w)/2:y=140:enable='between(t,0,{first_sc_end})'[v_hook]")
    cur_v = "v_hook"

    # Outro Verdict Badge (during last scene)
    last_sc_st = scene_records[-1]["start"] if len(scene_records) > 1 else total_duration * 0.75
    filter_complex.append(f"[{cur_v}]drawtext=text='⚡ VEREDICTO CÓSMICO ⚡':{font_param}:fontcolor=white:fontsize=34:box=1:boxcolor=0x08101e@0.92:boxborderw=20:borderw=2:bordercolor=0xffb300:x=(w-text_w)/2:y=140:enable='between(t,{last_sc_st},{total_duration})'[v_outro_badge]")
    cur_v = "v_outro_badge"

    # Subtitles overlay
    filter_complex.append(f"[{cur_v}]ass='{escaped_ass_path}'[vout]")

    filter_str = ";".join(filter_complex)

    cmd = [
        "ffmpeg", "-y",
        *cmd_inputs,
        "-filter_complex", filter_str,
        "-map", "[vout]",
        "-map", f"{audio_idx}:a",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
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
        for p in [temp_test_audio, ass_sub_path]:
            if p and p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass

    print(f"\n✨ ¡Vista previa del Orbe Bio-Reactivo generada con éxito!")
    print(f"🎬 Video listo: {output_path.resolve()}\n")

    # Generate companion studio-grade thumbnail
    try:
        from ai.thumbnail_generator import ThumbnailGenerator
        thumb_gen = ThumbnailGenerator()
        thumb_path = output_path.parent / "thumbnail.jpg"
        thumb_gen.render_studio_poster(
            hook=headline_hook,
            topic=topic or "Física Cuántica vs Astrofísica Solar",
            output_path=thumb_path
        )
    except Exception as te:
        print(f"  ⚠️ Error secundario generando portada automática: {te}")

    return output_path


# Alias for explicit AI debate generation calls
render_cohost_debate_video = render_orb_test_preview
