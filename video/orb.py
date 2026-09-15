"""
Procedural 3D Living AI Presenter Entity Generator & Compositor.
Generates a seamless 60-frame (30 FPS) transparent video loop (QuickTime MOV with ARGB alpha)
containing a dynamic 3D Quantum Energy Organism with:
- Continuously swirling liquid plasma core
- Continuously rotating 3D orbital energy rings
- Orbiting bioluminescent light nodes
- Audio-reactive speech incandescence and dynamic vocal pulsation
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


# 2 Master Signature Palettes
ORB_PALETTES: Dict[str, Dict[str, Any]] = {
    "quantum": {
        "name": "Quantum AI Presenter",
        "description": "Electric cyan core, deep violet plasma, magenta aura",
        "core_highlight": "#ffffff",
        "inner_glow": "#00f0ff",      # Electric Cyan
        "mid_gradient": "#8a2be2",    # Violet
        "outer_gradient": "#ff007f",  # Neon Magenta
        "deep_edge": "#090314",       # Cosmic Void
        "halo_ring": "#00f0ff",
        "halo_ring2": "#ff007f",
    },
    "solar": {
        "name": "Solar Plasma Presenter",
        "description": "Incandescent solar white core, flame amber plasma, radiant orange aura",
        "core_highlight": "#ffffff",
        "inner_glow": "#fff1a8",      # Solar White
        "mid_gradient": "#ffae00",    # Flame Amber
        "outer_gradient": "#ff4500",  # Intense Orange
        "deep_edge": "#1c0400",       # Dark Edge
        "halo_ring": "#ffae00",
        "halo_ring2": "#ff4500",
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
    containing a dynamic 3D Quantum Energy Organism with rotating orbital rings, swirling liquid plasma,
    and orbiting light nodes.
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

    print(f"  🔮 Generando bucle animado 3D para la Entidad Presentador Orbe ('{palette_key}')...")

    frames_dir = dest_dir / f"_temp_frames_{palette_key}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    c = canvas_size // 2
    r_sphere = int(canvas_size * 0.24)
    r_aura = int(canvas_size * 0.42)
    r_specular = int(r_sphere * 0.45)

    try:
        for i in range(loop_frames):
            t = i / loop_frames
            tau = 2 * math.pi * t

            a1 = int(t * 360)
            a2 = int(-t * 360 + 35)

            # Fluid wave control points
            w1_x1 = int(c - r_sphere * 0.70 + 18 * math.sin(tau))
            w1_y1 = int(c + r_sphere * 0.15 + 14 * math.cos(tau))
            w1_cx1 = int(c - r_sphere * 0.30 + 22 * math.cos(tau))
            w1_cy1 = int(c - r_sphere * 0.65 + 18 * math.sin(tau))
            w1_cx2 = int(c + r_sphere * 0.25 + 26 * math.sin(2 * tau))
            w1_cy2 = int(c - r_sphere * 0.45 + 16 * math.cos(2 * tau))
            w1_x2 = int(c + r_sphere * 0.75 + 14 * math.cos(tau))
            w1_y2 = int(c - r_sphere * 0.10 + 18 * math.sin(tau))

            # Orbiting light nodes
            n1_x = int(c + r_sphere * 0.38 * math.cos(tau))
            n1_y = int(c + r_sphere * 0.25 * math.sin(tau))
            n2_x = int(c + r_sphere * 0.32 * math.cos(tau + math.pi / 2))
            n2_y = int(c + r_sphere * 0.35 * math.sin(tau + math.pi / 2))
            n3_x = int(c + r_sphere * 0.42 * math.cos(-tau + math.pi))
            n3_y = int(c + r_sphere * 0.22 * math.sin(-tau + math.pi))

            svg = f"""<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="deepBlur_{i}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="12" />
    </filter>
    <filter id="sharpBlur_{i}" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="5" />
    </filter>
    <filter id="glow_{i}" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" />
    </filter>

    <clipPath id="coreClip_{i}">
      <circle cx="{c}" cy="{c}" r="{r_sphere}" />
    </clipPath>

    <radialGradient id="aura_{i}" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['mid_gradient']}" stop-opacity="0.80" />
      <stop offset="40%" stop-color="{palette['inner_glow']}" stop-opacity="0.40" />
      <stop offset="75%" stop-color="{palette['outer_gradient']}" stop-opacity="0.15" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />
    </radialGradient>

    <radialGradient id="body_{i}" cx="36%" cy="32%" r="68%">
      <stop offset="0%" stop-color="{palette['core_highlight']}" stop-opacity="1.0" />
      <stop offset="18%" stop-color="{palette['inner_glow']}" stop-opacity="0.95" />
      <stop offset="45%" stop-color="{palette['mid_gradient']}" stop-opacity="0.92" />
      <stop offset="80%" stop-color="{palette['outer_gradient']}" stop-opacity="0.95" />
      <stop offset="100%" stop-color="{palette['deep_edge']}" stop-opacity="1.0" />
    </radialGradient>

    <linearGradient id="ringGrad1_{i}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{palette['halo_ring']}" stop-opacity="0.95" />
      <stop offset="50%" stop-color="{palette['core_highlight']}" stop-opacity="1.0" />
      <stop offset="100%" stop-color="{palette['outer_gradient']}" stop-opacity="0.30" />
    </linearGradient>

    <linearGradient id="ringGrad2_{i}" x1="100%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{palette['halo_ring2']}" stop-opacity="0.90" />
      <stop offset="60%" stop-color="{palette['mid_gradient']}" stop-opacity="0.60" />
      <stop offset="100%" stop-color="{palette['inner_glow']}" stop-opacity="0.10" />
    </linearGradient>
  </defs>

  <!-- Atmospheric Corona Aura -->
  <circle cx="{c}" cy="{c}" r="{r_aura}" fill="url(#aura_{i})" />

  <!-- Outer 3D Orbital Energy Ring (Spinning Clockwise) -->
  <g transform="rotate({a1} {c} {c})">
    <ellipse cx="{c}" cy="{c}" rx="{int(r_sphere * 1.62)}" ry="{int(r_sphere * 0.44)}" fill="none" stroke="url(#ringGrad1_{i})" stroke-width="6" filter="url(#glow_{i})" opacity="0.88" />
    <ellipse cx="{c}" cy="{c}" rx="{int(r_sphere * 1.62)}" ry="{int(r_sphere * 0.44)}" fill="none" stroke="#ffffff" stroke-width="2" opacity="0.92" />
  </g>

  <!-- 3D Volumetric Body -->
  <circle cx="{c}" cy="{c}" r="{r_sphere}" fill="url(#body_{i})" />

  <!-- Swirling Fluid Core -->
  <g clip-path="url(#coreClip_{i})">
    <path d="M {w1_x1} {w1_y1} C {w1_cx1} {w1_cy1}, {w1_cx2} {w1_cy2}, {w1_x2} {w1_y2} C {c + int(r_sphere*0.3)} {c + int(r_sphere*0.5)}, {c - int(r_sphere*0.2)} {c + int(r_sphere*0.6)}, {w1_x1} {w1_y1} Z" fill="url(#ringGrad1_{i})" filter="url(#sharpBlur_{i})" opacity="0.85" />
    
    <!-- Orbiting Light Nodes -->
    <circle cx="{n1_x}" cy="{n1_y}" r="14" fill="#ffffff" filter="url(#sharpBlur_{i})" opacity="0.95" />
    <circle cx="{n2_x}" cy="{n2_y}" r="11" fill="{palette['inner_glow']}" filter="url(#sharpBlur_{i})" opacity="0.90" />
    <circle cx="{n3_x}" cy="{n3_y}" r="9" fill="{palette['outer_gradient']}" filter="url(#sharpBlur_{i})" opacity="0.88" />
  </g>

  <!-- Inner 3D Orbital Ring (Counter Spinning) -->
  <g transform="rotate({a2} {c} {c})">
    <ellipse cx="{c}" cy="{c}" rx="{int(r_sphere * 1.35)}" ry="{int(r_sphere * 0.32)}" fill="none" stroke="url(#ringGrad2_{i})" stroke-width="4.5" filter="url(#glow_{i})" opacity="0.80" />
  </g>

  <!-- 3D Glass Specular Crown -->
  <ellipse cx="{int(c - r_sphere*0.28)}" cy="{int(c - r_sphere*0.28)}" rx="{r_specular}" ry="{int(r_specular*0.68)}" fill="#ffffff" transform="rotate(-28 {int(c - r_sphere*0.28)} {int(c - r_sphere*0.28)})" opacity="0.55" filter="url(#sharpBlur_{i})" />

  <!-- Refraction Edge -->
  <circle cx="{c}" cy="{c}" r="{r_sphere}" fill="none" stroke="#000000" stroke-width="2.0" opacity="0.85" />
  <circle cx="{c}" cy="{c}" r="{r_sphere - 1}" fill="none" stroke="{palette['core_highlight']}" stroke-width="0.9" opacity="0.65" />
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
        on top of the continuously swirling/spinning transparent MOV loop stream.
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

            eq_expr = f"brightness='0.06*{speech_cadence}':contrast='1.0 + 0.12*{speech_mask}'"
            hue_expr = f"h='20*{speech_cadence} + 10*sin(2*PI*t/2.4)':s='1.0 + 0.18*{speech_mask}'"

            filters.append(f"[{input_idx}:v]scale={scale_expr}")
            filters.append(f"eq={eq_expr}")
            filters.append(f"hue={hue_expr}")
            filters.append("format=yuva420p")
            filters.append(f"colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]")
        else:
            hue_expr = "h='12*sin(2*PI*t/2.5)':s='1.0 + 0.08*sin(2*PI*t/2.5)'"

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
    """Renders a fast preview video of the dynamic 3D Living Presenter Entity."""
    if output_path is None:
        out_dir = Path("output") / "orb_previews"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"test_orb_{palette}_presenter.mp4"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n🔮 [AI Presenter Tester] Generando vista previa de la Entidad Presentador 3D...")
    print(f"   • Paleta: '{palette}' | Opacidad: {opacity}")
    print(f"   • Duración: {duration}s | Resolución: {width}x{height}")

    orb_asset = get_or_create_orb_asset(palette=palette, force_refresh=True)
    temp_test_audio: Optional[Path] = None
    resolved_audio: Optional[Path] = sample_audio

    if not resolved_audio:
        temp_test_audio = output_path.parent / "_temp_test_voice.mp3"
        speech_text = "El universo se expande a velocidades astronómicas que desafían la imaginación."
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
    bg_input = f"color=c=0x07090e:s={width}x{height}:r=30:d={duration}"

    filter_complex = [
        orb_filter,
        f"[0:v]eq=brightness=-0.03:contrast=1.06:saturation=1.04[bg_graded]",
        f"[bg_graded][orb_layer]overlay=eval=frame:x='{x_coord}':y='{y_coord}':shortest=1[v_orb]",
        f"[v_orb]drawtext=text='LIVING 3D AI ENTITY \\: {palette.upper()}':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.65:boxborderw=12:x=(w-text_w)/2:y=180[vout]"
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
        fallback_filter = f"{orb_filter};[0:v]eq=brightness=-0.03:contrast=1.06:saturation=1.04[bg_graded];[bg_graded][orb_layer]overlay=eval=frame:x='{x_coord}':y='{y_coord}':shortest=1[vout]"
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

    print(f"\n✨ ¡Vista previa de la Entidad 3D en movimiento generada!")
    print(f"🎬 Video listo: {output_path.resolve()}\n")
    return output_path
