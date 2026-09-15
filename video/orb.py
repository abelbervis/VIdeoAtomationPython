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
        "body_center": "#06b6d4",    # Electric Cyan
        "body_mid": "#0284c7",       # Blue
        "body_edge": "#3b82f6",      # Deep Blue
        "body_rim": "#4f46e5",       # Indigo Rim
        "spot_core": "#ffffff",      # White Core
        "spot_glow": "#f472b6",      # Magenta/Pink Glow
        "spot_outer": "#c084fc",     # Purple Glow
        "aura_inner": "#a855f7",     # Neon Purple Aura
        "aura_mid": "#7c3aed",
        "aura_outer": "#3b82f6",
        "ring_stroke": "#c084fc",
    },
    "solar": {
        "name": "Solar Bio-Reactive",
        "description": "Incandescent solar amber sphere, warm flare highlight, golden aura",
        "body_center": "#ffb700",
        "body_mid": "#ff7700",
        "body_edge": "#e65100",
        "body_rim": "#d84315",
        "spot_core": "#ffffff",
        "spot_glow": "#ffe066",
        "spot_outer": "#ff9800",
        "aura_inner": "#ff9800",
        "aura_mid": "#f57c00",
        "aura_outer": "#e65100",
        "ring_stroke": "#ffe066",
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
    r_sphere = int(canvas_size * 0.27)
    r_aura_outer_base = int(canvas_size * 0.48)
    r_aura_inner_base = int(canvas_size * 0.38)

    try:
        for i in range(loop_frames):
            t = i / loop_frames
            tau = 2 * math.pi * t

            # 1. Concentric surrounding ring expands & contracts until touching the sphere body (2x faster speed)
            # At t=0 & t=0.5, ring_r = r_sphere + 4 (touches sphere edge!)
            # At t=0.25 & t=0.75, ring_r = r_sphere + 36 (expands far outward!)
            ring_r = int(r_sphere + 20 - 16 * math.cos(2.0 * tau))
            ring_r_outer_glow = ring_r + 5

            # 2. Rich atmospheric volumetric aura swells (+/- 14px)
            r_aura_outer = int(r_aura_outer_base + 14 * math.sin(tau))
            r_aura_inner = int(r_aura_inner_base + 10 * math.sin(tau))

            # 3. Core light spot breathing (Primary Top-Left Spot)
            spot1_x = int(c - r_sphere * 0.32 + 8 * math.sin(tau))
            spot1_y = int(c - r_sphere * 0.28 + 6 * math.cos(tau))
            spot1_rx = int(r_sphere * 0.52 + 6 * math.sin(2 * tau))
            spot1_ry = int(r_sphere * 0.48 + 5 * math.cos(2 * tau))

            # 4. Secondary Counter-Tone Light Spot (Bottom-Right Cyan/Azure Flare)
            spot2_x = int(c + r_sphere * 0.30 - 8 * math.sin(tau))
            spot2_y = int(c + r_sphere * 0.28 - 6 * math.cos(tau))
            spot2_rx = int(r_sphere * 0.44 + 5 * math.cos(2 * tau))
            spot2_ry = int(r_sphere * 0.40 + 4 * math.sin(2 * tau))

            svg = f"""<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="auraGlowDeep_{i}" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="30" />
    </filter>
    <filter id="auraGlowMid_{i}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="18" />
    </filter>
    <filter id="coreBlur_{i}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="11" />
    </filter>
    <filter id="secondaryBlur_{i}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="14" />
    </filter>
    <filter id="ringGlow_{i}" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="8" />
    </filter>

    <clipPath id="sphereClip_{i}">
      <circle cx="{c}" cy="{c}" r="{r_sphere}" />
    </clipPath>

    <!-- Expansive Multi-Stop Atmospheric Neon Volumetric Aura -->
    <radialGradient id="outerAuraDeep_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['aura_inner']}" stop-opacity="0.95" />
      <stop offset="35%" stop-color="{palette['aura_mid']}" stop-opacity="0.75" />
      <stop offset="68%" stop-color="{palette['aura_outer']}" stop-opacity="0.38" />
      <stop offset="88%" stop-color="#3b82f6" stop-opacity="0.15" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <radialGradient id="innerAuraBright_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#c084fc" stop-opacity="0.90" />
      <stop offset="45%" stop-color="{palette['aura_inner']}" stop-opacity="0.60" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <!-- Multi-Spectral Chromatic Sphere Body Gradient -->
    <radialGradient id="sphereBody_{i}" cx="42%" cy="38%" r="62%">
      <stop offset="0%" stop-color="#00f0ff" />
      <stop offset="22%" stop-color="#0284c7" />
      <stop offset="48%" stop-color="#3b82f6" />
      <stop offset="72%" stop-color="#8a2be2" />
      <stop offset="88%" stop-color="#d946ef" />
      <stop offset="100%" stop-color="#1e0836" />
    </radialGradient>

    <!-- Primary Off-Center Light Spot (White Center to Magenta/Pink Flare) -->
    <radialGradient id="primarySpot_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="1.0" />
      <stop offset="26%" stop-color="#f472b6" stop-opacity="0.95" />
      <stop offset="60%" stop-color="#c084fc" stop-opacity="0.65" />
      <stop offset="100%" stop-color="#8a2be2" stop-opacity="0.0" />
    </radialGradient>

    <!-- Secondary Counter-Tone Light Spot (Cyan/Electric Blue Flare) -->
    <radialGradient id="secondarySpot_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00f0ff" stop-opacity="0.90" />
      <stop offset="40%" stop-color="#0284c7" stop-opacity="0.65" />
      <stop offset="80%" stop-color="#3b82f6" stop-opacity="0.30" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>
  </defs>

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
    <!-- Secondary Cyan/Azure Flare (Bottom-Right) -->
    <ellipse cx="{spot2_x}" cy="{spot2_y}" rx="{spot2_rx}" ry="{spot2_ry}" fill="url(#secondarySpot_{i})" filter="url(#secondaryBlur_{i})" />

    <!-- Primary White/Magenta Flare (Top-Left) -->
    <ellipse cx="{spot1_x}" cy="{spot1_y}" rx="{spot1_rx}" ry="{spot1_ry}" fill="url(#primarySpot_{i})" filter="url(#coreBlur_{i})" />
    <circle cx="{spot1_x}" cy="{spot1_y}" r="{int(spot1_rx * 0.45)}" fill="#ffffff" opacity="0.98" filter="url(#coreBlur_{i})" />

    <!-- Subsurface Magenta Rim Accent -->
    <circle cx="{c}" cy="{c}" r="{r_sphere - 3}" fill="none" stroke="#d946ef" stroke-width="4" opacity="0.55" filter="url(#coreBlur_{i})" />
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
            speech_cadence = f"(max(0,sin(2*PI*t/0.48))*{speech_mask})"

            eq_expr = f"brightness='0.07*{speech_cadence}':contrast='1.0 + 0.14*{speech_mask}'"
            hue_expr = f"h='18*{speech_cadence} + 8*sin(2*PI*t/2.4)':s='1.0 + 0.16*{speech_mask}'"

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
    duration: float = 4.0,
    output_path: Optional[Path] = None,
    width: int = 1080,
    height: int = 1920,
    bg_style: str = "cosmic",
    sample_audio: Optional[Path] = None,
) -> Path:
    """Renders a fast preview video matching the reference bio-reactive orb."""
    if output_path is None:
        out_dir = Path("output") / "orb_previews"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"test_orb_{palette}_presenter.mp4"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n🔮 [AI Presenter Tester] Generando vista previa del Orbe Bio-Reactivo...")
    print(f"   • Paleta: '{palette}' | Opacidad: {opacity}")
    print(f"   • Duración: {duration}s | Resolución: {width}x{height}")

    orb_asset = get_or_create_orb_asset(palette=palette, force_refresh=True)
    temp_test_audio: Optional[Path] = None
    resolved_audio: Optional[Path] = sample_audio

    if not resolved_audio:
        temp_test_audio = output_path.parent / "_temp_test_voice.mp3"
        speech_text = "NEXUS ORBE BIO REACTIVO. El universo se expande a velocidades astronómicas."
        from audio.tts import GoogleTTSProvider
        g_tts = GoogleTTSProvider(language="es")
        synthesized = g_tts.synthesize_text(speech_text, temp_test_audio)
        if synthesized and temp_test_audio.exists():
            resolved_audio = temp_test_audio

    mgr = GradientOrbManager(
        palette=palette,
        position=position,
        size=size,
        opacity=opacity,
        animation=animation,
        audio_path=resolved_audio,
        total_duration=duration,
        intro_duration=max(1.5, duration * 0.35),
    )

    orb_filter = mgr.build_filter_chain(
        input_idx=1,
        output_label="orb_layer",
        video_width=width,
        video_height=height,
        fps=30
    )
    x_coord, y_coord = mgr.get_overlay_coordinates(width, height)
    bg_input = f"color=c=0x0b0d14:s={width}x{height}:r=30:d={duration}"

    filter_complex = [
        orb_filter,
        f"[0:v]eq=brightness=-0.02:contrast=1.05[bg_graded]",
        f"[bg_graded][orb_layer]overlay=eval=frame:x='{x_coord}':y='{y_coord}':shortest=1[v_orb]",
        f"[v_orb]drawtext=text='NEXUS - ORBE BIO REACTIVO':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.65:boxborderw=12:x=(w-text_w)/2:y=180[vout]"
    ]
    filter_str = ";".join(filter_complex)

    audio_input_args = []
    if resolved_audio and resolved_audio.exists():
        audio_input_args = ["-i", str(resolved_audio)]
        audio_map = ["-map", "2:a"]
    else:
        audio_input_args = ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
        audio_map = ["-map", "2:a"]

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", bg_input,
        "-stream_loop", "-1", "-i", str(orb_asset),
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
    except subprocess.CalledProcessError:
        fallback_filter = f"{orb_filter};[0:v]eq=brightness=-0.02:contrast=1.05[bg_graded];[bg_graded][orb_layer]overlay=eval=frame:x='{x_coord}':y='{y_coord}':shortest=1[vout]"
        cmd_fallback = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", bg_input,
            "-stream_loop", "-1", "-i", str(orb_asset),
            *audio_input_args,
            "-filter_complex", fallback_filter,
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
        subprocess.run(cmd_fallback, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    finally:
        if temp_test_audio and temp_test_audio.exists():
            try:
                temp_test_audio.unlink()
            except Exception:
                pass

    print(f"\n✨ ¡Vista previa del Orbe Bio-Reactivo generada con éxito!")
    print(f"🎬 Video listo: {output_path.resolve()}\n")
    return output_path
