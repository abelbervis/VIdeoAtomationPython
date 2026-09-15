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
    }
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
) -> Path:
    """Renders a stunning co-host conversation video with two bio-reactive orbs and dynamic camera cuts."""
    if output_path is None:
        out_dir = Path("output") / "orb_previews"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"test_orb_{palette}_presenter.mp4"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n🔮 [AI Co-Host Debate] Generando demo interactiva de Doble Orbe y Multi-Cámara...")
    print(f"   • Orbe 1: Quantum (Azul Eléctrico) | Orbe 2: Solar (Ámbar Fuego)")
    print(f"   • Hook: {headline_hook}")
    print(f"   • Duración: 12.0s | Resolución: {width}x{height} | 4 Cortes de Cámara")

    # Generate both assets
    orb_quantum = get_or_create_orb_asset(palette="quantum", force_refresh=True)
    orb_solar = get_or_create_orb_asset(palette="solar", force_refresh=True)

    temp_test_audio: Optional[Path] = output_path.parent / "_temp_cohost_debate.mp3"
    resolved_audio: Optional[Path] = sample_audio

    if not resolved_audio:
        part1_path = output_path.parent / "_temp_q_part1.mp3"
        part2_path = output_path.parent / "_temp_q_part2.mp3"
        part3_path = output_path.parent / "_temp_s_part3.mp3"
        sfx_intro_path = output_path.parent / "_temp_sfx_intro.wav"
        sfx_zoom_path = output_path.parent / "_temp_sfx_zoom.wav"
        sfx_pan_path = output_path.parent / "_temp_sfx_pan.wav"
        sfx_wide_path = output_path.parent / "_temp_sfx_wide.wav"
        music_bg_path = output_path.parent / "_temp_music_ambient.wav"
        
        from audio.tts import EdgeTTSProvider, GoogleTTSProvider
        from audio.sfx import synthesize_camera_servo_sfx, synthesize_space_ambient_pad
        from audio.music import MusicManager

        tts_q = EdgeTTSProvider(default_voice="es-ES-AlvaroNeural")
        tts_s = EdgeTTSProvider(default_voice="es-ES-ElviraNeural")
        
        # Test a brief call to see if edge neural is online, else fallback
        test_file = output_path.parent / "_test_probe.mp3"
        if not tts_q.synthesize_text("Hola", test_file):
            tts_q = GoogleTTSProvider(language="es")
            tts_s = GoogleTTSProvider(language="es")
        if test_file.exists():
            test_file.unlink()

        syn1 = tts_q.synthesize_text("¡Hola! Bienvenidos a este nuevo debate espacial.", part1_path)
        syn2 = tts_q.synthesize_text("Hoy exploraremos los límites y misterios de la física cuántica.", part2_path)
        syn3 = tts_s.synthesize_text("¡Excelente! Y yo aportaré los secretos de la física solar.", part3_path)

        # Synthesize camera transition SFX
        synthesize_camera_servo_sfx(sfx_intro_path, duration=0.8, sfx_type="intro")
        synthesize_camera_servo_sfx(sfx_zoom_path, duration=0.45, sfx_type="zoom_in")
        synthesize_camera_servo_sfx(sfx_pan_path, duration=0.45, sfx_type="pan")
        synthesize_camera_servo_sfx(sfx_wide_path, duration=0.55, sfx_type="pull_back")

        # Prepare background soundtrack (custom asset or procedural space ambient pad)
        music_mgr = MusicManager()
        bg_track = music_mgr.get_background_track()
        if bg_track and bg_track.exists():
            music_bg_path = bg_track
        else:
            synthesize_space_ambient_pad(music_bg_path, duration=12.0)
        
        if syn1 and syn2 and syn3 and part1_path.exists() and part2_path.exists() and part3_path.exists():
            # Multitrack Audio Mixing Pipeline:
            # Inputs:
            # 0: Voice Part 1 (Quantum - 0.0s)
            # 1: Voice Part 2 (Quantum - 3.2s)
            # 2: Voice Part 3 (Solar - 6.2s)
            # 3: SFX Intro (0.0s)
            # 4: SFX Zoom (3.2s)
            # 5: SFX Pan (6.2s)
            # 6: SFX Wide Pan Out (9.2s)
            # 7: Sci-Fi Ambient Soundtrack Pad (0.0s - 12.0s)
            concat_cmd = [
                "ffmpeg", "-y",
                "-i", str(part1_path),
                "-i", str(part2_path),
                "-i", str(part3_path),
                "-i", str(sfx_intro_path),
                "-i", str(sfx_zoom_path),
                "-i", str(sfx_pan_path),
                "-i", str(sfx_wide_path),
                "-stream_loop", "-1", "-i", str(music_bg_path),
                "-filter_complex",
                "[0:a]adelay=0|0,volume=1.0[v1];"
                "[1:a]adelay=3200|3200,volume=1.0[v2];"
                "[2:a]adelay=6200|6200,volume=1.0[v3];"
                "[3:a]adelay=50|50,volume=0.35[sfx0];"
                "[4:a]adelay=3180|3180,volume=0.40[sfx1];"
                "[5:a]adelay=6180|6180,volume=0.40[sfx2];"
                "[6:a]adelay=9180|9180,volume=0.45[sfx3];"
                "[7:a]volume=0.18,afade=t=in:st=0:d=1.0,afade=t=out:st=10.2:d=1.8[bgm];"
                "[v1][v2][v3][sfx0][sfx1][sfx2][sfx3][bgm]amix=inputs=8:dropout_transition=0:normalize=0[aout]",
                "-map", "[aout]",
                "-t", "12.0",
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                str(temp_test_audio)
            ]
            try:
                subprocess.run(concat_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if temp_test_audio.exists():
                    resolved_audio = temp_test_audio
            except Exception as e:
                print(f"  ⚠️ Test co-host audio concat error: {e}")
                resolved_audio = part1_path
            
            for p in [part1_path, part2_path, part3_path, sfx_intro_path, sfx_zoom_path, sfx_pan_path, sfx_wide_path]:
                if p.exists():
                    try:
                        p.unlink()
                    except Exception:
                        pass
            if music_bg_path.name == "_temp_music_ambient.wav" and music_bg_path.exists():
                try:
                    music_bg_path.unlink()
                except Exception:
                    pass


    # Build advanced video filter chains for double overlays & scale changes (Virtual Camera)
    # Drift and eq structures with static opacities split by role and shot
    voice_ripple_q = "(0.5 + 0.5 * sin(2*PI*t/0.38))"
    speech_mask_q = "between(t,0,6.2)"
    eq_q = f"brightness='-0.18 + (0.34 + 0.08*{voice_ripple_q})*{speech_mask_q}':contrast='0.70 + (0.55 + 0.15*{voice_ripple_q})*{speech_mask_q}'"
    hue_q = f"h='(12 + 4*{voice_ripple_q})*{speech_mask_q} + 6*sin(2*PI*t/2.4)':s='0.60 + (0.65 + 0.20*{voice_ripple_q})*{speech_mask_q}'"
    
    voice_ripple_s = "(0.5 + 0.5 * sin(2*PI*t/0.36))"
    speech_mask_s = "between(t,6.2,12.0)"
    eq_s = f"brightness='-0.04 + (0.16 + 0.05*{voice_ripple_s})*{speech_mask_s}':contrast='0.92 + (0.22 + 0.08*{voice_ripple_s})*{speech_mask_s}'"
    hue_s = f"h='(12 + 4*{voice_ripple_s})*{speech_mask_s} + 6*sin(2*PI*t/2.4)':s='0.85 + (0.45 + 0.15*{voice_ripple_s})*{speech_mask_s}'"

    # Precise structural drift controls (Calm when passive/resting, full dynamic swing when active)
    drift_q_active_x = "14.0*sin(2*PI*t/3.6)"
    drift_q_active_y = "18.0*sin(2*PI*t/2.4)"
    drift_q_resting_x = "4.0*sin(2*PI*t/3.6)"
    drift_q_resting_y = "5.0*sin(2*PI*t/2.4)"

    drift_s_active_x = "14.0*sin(2*PI*t/3.2)"
    drift_s_active_y = "18.0*sin(2*PI*t/2.8)"
    drift_s_resting_x = "4.0*sin(2*PI*t/3.2)"
    drift_s_resting_y = "5.0*sin(2*PI*t/2.8)"

    # Power ignition spring on intro (0-0.8s)
    drift_intro_x = "30.0*exp(-7.0*t)*cos(16.0*t)"
    drift_intro_y = "35.0*exp(-7.0*t)*sin(16.0*t)"

    bg_input = f"color=c=0x08090f:s={width}x{height}:r=30:d=12.0"

    filter_complex = [
        # 1. Split streams to apply physical static transparency to separate active/resting layers
        "[1:v]split=4[q_wa][q_wp][q_ca][q_glow]",
        "[2:v]split=4[s_wa][s_wp][s_ca][s_glow]",
        
        # 2. Render each state independently with pre-baked alpha levels and size depth differences (Z-Axis)
        f"[q_wa]scale=355:355,eq={eq_q},hue={hue_q},format=yuva420p,colorchannelmixer=aa=0.95[orb_q_wide_active]",
        f"[q_wp]scale=310:310,eq={eq_q},hue={hue_q},format=yuva420p,colorchannelmixer=aa=0.32[orb_q_wide_passive]",
        f"[q_ca]scale=550:550,eq={eq_q},hue={hue_q},format=yuva420p,colorchannelmixer=aa=0.95[orb_q_close_active]",
        
        f"[s_wp]scale=310:310,eq={eq_s},hue={hue_s},format=yuva420p,colorchannelmixer=aa=0.52[orb_s_wide_passive]",
        f"[s_wa]scale=355:355,eq={eq_s},hue={hue_s},format=yuva420p,colorchannelmixer=aa=0.95[orb_s_wide_active]",
        f"[s_ca]scale=550:550,eq={eq_s},hue={hue_s},format=yuva420p,colorchannelmixer=aa=0.95[orb_s_close_active]",
        
        # 3. Render dynamic ambient glow backplates using the ultra-fast pre-scaled blur technique
        f"[q_glow]scale=120:120,eq={eq_q},hue={hue_q},boxblur=24:3,scale=1080:1920,format=yuva420p,colorchannelmixer=aa=0.22[bg_glow_q]",
        f"[s_glow]scale=120:120,eq={eq_s},hue={hue_s},boxblur=24:3,scale=1080:1920,format=yuva420p,colorchannelmixer=aa=0.22[bg_glow_s]",
        
        # 4. Apply background grading and overlay dynamic glows first to make the ambient background
        f"[0:v]eq=brightness=-0.01:contrast=1.05[bg_graded]",
        f"[bg_graded][bg_glow_q]overlay=eval=frame:enable='between(t,0,6.2)'[bg_glowed_1]",
        f"[bg_glowed_1][bg_glow_s]overlay=eval=frame:enable='between(t,6.2,12.0)'[bg_ambient]",
        
        # 5. Sequentially overlay the foreground orbs with power ignition snap on frame 0 and matching drifts
        # Toma 1 (0-3.2s): Wide Shot. Power ignition snap, Quantum active takes stage (Z-forward). Solar passive leans left towards Quantum
        f"[bg_ambient][orb_q_wide_active]overlay=eval=frame:x='W*0.25-w/2 + {drift_q_active_x} + {drift_intro_x}':y='H*0.42-h/2 + {drift_q_active_y} + {drift_intro_y}':enable='between(t,0,3.2)'[v1]",
        f"[v1][orb_s_wide_passive]overlay=eval=frame:x='W*0.75-w/2 - 28 + {drift_s_resting_x} + {drift_intro_x}':y='H*0.43-h/2 + {drift_s_resting_y} + {drift_intro_y}':enable='between(t,0,3.2)'[v2]",
        
        # Toma 2 (3.2s-6.2s): Close Up Quantum active with organic spring camera damping transition
        f"[v2][orb_q_close_active]overlay=eval=frame:x='W/2-w/2 + {drift_q_active_x} + 25.0*exp(-6.5*(t-3.2))*cos(16.0*(t-3.2))':y='H*0.40-h/2 + {drift_q_active_y} + 30.0*exp(-6.5*(t-3.2))*sin(16.0*(t-3.2))':enable='between(t,3.2,6.2)'[v3]",
        
        # Toma 3 (6.2s-9.2s): Close Up Solar active with organic spring camera damping transition
        f"[v3][orb_s_close_active]overlay=eval=frame:x='W/2-w/2 + {drift_s_active_x} + 25.0*exp(-6.5*(t-6.2))*cos(16.0*(t-6.2))':y='H*0.40-h/2 + {drift_s_active_y} + 30.0*exp(-6.5*(t-6.2))*sin(16.0*(t-6.2))':enable='between(t,6.2,9.2)'[v4]",
        
        # Toma 4 (9.2s-12.0s): Wide Shot. Solar active takes stage (Z-forward). Quantum passive leans right towards Solar (Z-back + leaning offset)
        f"[v4][orb_q_wide_passive]overlay=eval=frame:x='W*0.25-w/2 + 28 + {drift_q_resting_x} + 15.0*exp(-6.5*(t-9.2))*cos(16.0*(t-9.2))':y='H*0.43-h/2 + {drift_q_resting_y} + 18.0*exp(-6.5*(t-9.2))*sin(16.0*(t-9.2))':enable='between(t,9.2,12.0)'[v5]",
        f"[v5][orb_s_wide_active]overlay=eval=frame:x='W*0.75-w/2 + {drift_s_active_x} + 15.0*exp(-6.5*(t-9.2))*cos(16.0*(t-9.2))':y='H*0.42-h/2 + {drift_s_active_y} + 18.0*exp(-6.5*(t-9.2))*sin(16.0*(t-9.2))':enable='between(t,9.2,12.0)'[v6]",
        
        # 6. Headline Hook Badge Overlay (Top Center 0.0s - 2.6s)
        f"[v6]drawtext=text='{headline_hook.replace(':', '\\\\:').replace('\'', '\\\\\'')}':fontcolor=white:fontsize=36:fontfile=Arial:box=1:boxcolor=0x08101e@0.85:boxborderw=14:borderw=2:bordercolor=0x00f0ff:x=(w-text_w)/2:y=170:enable='between(t,0,2.6)'[v_hook]",

        # 7. Subtitles dialogue overlays (Bottom)
        f"[v_hook]drawtext=text='Quantum\\: ¡Hola! Bienvenidos a este nuevo debate espacial.':fontcolor=0x00f0ff:fontsize=36:fontfile=Arial:box=1:boxcolor=black@0.75:boxborderw=12:x=(w-text_w)/2:y=h-240:enable='between(t,0,3.2)'[sub1]",
        f"[sub1]drawtext=text='Quantum\\: Hoy exploraremos los limites y misterios de la fisica cuantica.':fontcolor=0x00f0ff:fontsize=36:fontfile=Arial:box=1:boxcolor=black@0.75:boxborderw=12:x=(w-text_w)/2:y=h-240:enable='between(t,3.2,6.2)'[sub2]",
        f"[sub2]drawtext=text='Solar\\: ¡Excelente! Y yo aportare los secretos de la fisica solar.':fontcolor=0xffaa00:fontsize=36:fontfile=Arial:box=1:boxcolor=black@0.75:boxborderw=12:x=(w-text_w)/2:y=h-240:enable='between(t,6.2,9.7)'[sub3]",
        f"[sub3]drawtext=text='[Ambos Orbes en Armonia y Resonancia]':fontcolor=white:fontsize=36:fontfile=Arial:box=1:boxcolor=black@0.75:boxborderw=12:x=(w-text_w)/2:y=h-240:enable='between(t,9.7,12.0)'[vout]"
    ]
    filter_str = ";".join(filter_complex)

    audio_input_args = []
    if resolved_audio and resolved_audio.exists():
        audio_input_args = ["-i", str(resolved_audio)]
        audio_map = ["-map", "3:a"]
    else:
        audio_input_args = ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
        audio_map = ["-map", "3:a"]

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", bg_input,
        "-stream_loop", "-1", "-i", str(orb_quantum),
        "-stream_loop", "-1", "-i", str(orb_solar),
        *audio_input_args,
        "-filter_complex", filter_str,
        "-map", "[vout]",
        *audio_map,
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
        if temp_test_audio and temp_test_audio.exists():
            try:
                temp_test_audio.unlink()
            except Exception:
                pass

    print(f"\n✨ ¡Vista previa del Orbe Bio-Reactivo generada con éxito!")
    print(f"🎬 Video listo: {output_path.resolve()}\n")
    return output_path
