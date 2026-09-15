"""
Living AI Presenter Orb Generator & Compositor.
Renders a hyper-realistic, bioluminescent 3D Quantum Plasma Entity featuring:
- Living organic energy core with multi-layer volumetric caustics
- Tilted 3D orbital halo rings (sentient energy rings)
- Audio-reactive speech incandescence and dynamic vocal pulsation
- Glass Fresnel specular crown and atmospheric corona halo
- Optimized for functioning as the primary visual AI presenter entity in vertical Shorts
"""

import math
import struct
import subprocess
import wave
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List


def extract_audio_speech_envelope(
    audio_path: Path,
    threshold: float = 0.035,
    min_silence_dur: float = 0.40,
    max_intervals: int = 35,
) -> List[Tuple[float, float]]:
    """
    Extracts high-level continuous speech intervals [(start_sec, end_sec), ...]
    from the narration audio track using lightweight PCM energy analysis.
    """
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


# Streamlined 2 Master Presenter Palettes (Quantum AI Core & Solar Plasma Core)
ORB_PALETTES: Dict[str, Dict[str, Any]] = {
    "quantum": {
        "name": "Quantum AI Presenter",
        "description": "Bioluminescent electric cyan core, deep violet plasma, magenta aura",
        "core_highlight": "#ffffff",
        "inner_glow": "#00f0ff",      # Electric Cyan
        "mid_gradient": "#8a2be2",    # Violet
        "outer_gradient": "#ff007f",  # Neon Magenta
        "deep_edge": "#090314",       # Cosmic Void
        "halo_ring": "#00f0ff",
        "ambient_aura": "#8a2be2",
        "ambient_secondary": "#00f0ff",
    },
    "solar": {
        "name": "Solar Plasma Presenter",
        "description": "Incandescent solar white core, flame amber plasma, radiant orange aura",
        "core_highlight": "#ffffff",
        "inner_glow": "#fff1a8",      # Solar White Flare
        "mid_gradient": "#ffae00",    # Flame Amber
        "outer_gradient": "#ff4500",  # Intense Orange
        "deep_edge": "#1c0400",       # Dark Flare Edge
        "halo_ring": "#ffae00",
        "ambient_aura": "#ff8800",
        "ambient_secondary": "#ff2200",
    }
}


def generate_gradient_orb_svg(
    palette_key: str = "quantum",
    canvas_size: int = 1000,
    save_path: Optional[Path] = None,
) -> Tuple[Path, str]:
    """
    Generate a high-definition SVG file containing an organic 3D Living AI Presenter Entity
    with orbital energy halos, bioluminescent caustics, volumetric Fresnel core, and glass specular gleam.
    """
    palette_key = palette_key.lower().strip()
    if palette_key not in ORB_PALETTES:
        palette_key = "quantum"
    palette = ORB_PALETTES[palette_key]

    c = canvas_size // 2
    r_sphere = int(canvas_size * 0.23)
    r_corona = int(canvas_size * 0.30)
    r_aura = int(canvas_size * 0.42)
    r_specular = int(r_sphere * 0.45)

    p_x1 = int(c - r_sphere * 0.32)
    p_y1 = int(c - r_sphere * 0.25)
    p_x2 = int(c + r_sphere * 0.30)
    p_y2 = int(c + r_sphere * 0.22)

    svg_content = f"""<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Soft Volumetric Blurs -->
    <filter id="vortexDeepBlur" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="14" result="blurDeep" />
    </filter>

    <filter id="vortexSharpBlur" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="6" result="blurSharp" />
    </filter>

    <filter id="ringGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="glow" />
    </filter>

    <!-- Clip path defining the spherical plasma glass body -->
    <clipPath id="coreClip">
      <circle cx="{c}" cy="{c}" r="{r_sphere}" />
    </clipPath>

    <!-- Layer 0: Radiance Aura -->
    <radialGradient id="outerRadiance" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['ambient_aura']}" stop-opacity="0.82" />
      <stop offset="35%" stop-color="{palette['ambient_secondary']}" stop-opacity="0.45" />
      <stop offset="68%" stop-color="{palette['outer_gradient']}" stop-opacity="0.18" />
      <stop offset="90%" stop-color="{palette['mid_gradient']}" stop-opacity="0.04" />
      <stop offset="100%" stop-color="{palette['mid_gradient']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- Layer 1: Radiant Coronal Plasma Flare -->
    <radialGradient id="coronalHalo" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['core_highlight']}" stop-opacity="0.90" />
      <stop offset="28%" stop-color="{palette['inner_glow']}" stop-opacity="0.70" />
      <stop offset="62%" stop-color="{palette['ambient_aura']}" stop-opacity="0.30" />
      <stop offset="92%" stop-color="{palette['outer_gradient']}" stop-opacity="0.04" />
      <stop offset="100%" stop-color="{palette['outer_gradient']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- Layer 2: 3D Quantum Body -->
    <radialGradient id="orbVolumetric" cx="36%" cy="32%" r="68%" fx="30%" fy="26%">
      <stop offset="0%" stop-color="{palette['core_highlight']}" stop-opacity="1.0" />
      <stop offset="15%" stop-color="{palette['inner_glow']}" stop-opacity="0.96" />
      <stop offset="40%" stop-color="{palette['mid_gradient']}" stop-opacity="0.95" />
      <stop offset="74%" stop-color="{palette['outer_gradient']}" stop-opacity="0.98" />
      <stop offset="94%" stop-color="{palette['deep_edge']}" stop-opacity="1.0" />
      <stop offset="100%" stop-color="#020008" stop-opacity="1.0" />
    </radialGradient>

    <!-- Sentient Orbital Energy Ring Gradients -->
    <linearGradient id="haloRingGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{palette['halo_ring']}" stop-opacity="0.95" />
      <stop offset="50%" stop-color="{palette['core_highlight']}" stop-opacity="1.0" />
      <stop offset="100%" stop-color="{palette['outer_gradient']}" stop-opacity="0.20" />
    </linearGradient>

    <linearGradient id="haloRingGrad2" x1="100%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{palette['inner_glow']}" stop-opacity="0.90" />
      <stop offset="60%" stop-color="{palette['mid_gradient']}" stop-opacity="0.60" />
      <stop offset="100%" stop-color="{palette['deep_edge']}" stop-opacity="0.10" />
    </linearGradient>

    <!-- Internal Caustic Resonance Ribbons -->
    <linearGradient id="ringGrad1" x1="10%" y1="20%" x2="90%" y2="80%">
      <stop offset="0%" stop-color="{palette['core_highlight']}" stop-opacity="0.95" />
      <stop offset="30%" stop-color="{palette['inner_glow']}" stop-opacity="0.82" />
      <stop offset="70%" stop-color="{palette['ambient_aura']}" stop-opacity="0.45" />
      <stop offset="100%" stop-color="{palette['deep_edge']}" stop-opacity="0.0" />
    </linearGradient>

    <!-- Singularity Eye -->
    <radialGradient id="vortexEye" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="1.0" />
      <stop offset="25%" stop-color="{palette['core_highlight']}" stop-opacity="0.98" />
      <stop offset="55%" stop-color="{palette['inner_glow']}" stop-opacity="0.85" />
      <stop offset="85%" stop-color="{palette['ambient_aura']}" stop-opacity="0.30" />
      <stop offset="100%" stop-color="{palette['deep_edge']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- 3D Specular Crown -->
    <radialGradient id="specularGleam" cx="30%" cy="26%" r="48%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="1.0" />
      <stop offset="22%" stop-color="#ffffff" stop-opacity="0.85" />
      <stop offset="50%" stop-color="{palette['inner_glow']}" stop-opacity="0.48" />
      <stop offset="80%" stop-color="{palette['mid_gradient']}" stop-opacity="0.10" />
      <stop offset="100%" stop-color="{palette['mid_gradient']}" stop-opacity="0.0" />
    </radialGradient>
  </defs>

  <!-- Stage 1: Soft Atmospheric Radiance -->
  <circle cx="{c}" cy="{c}" r="{r_aura}" fill="url(#outerRadiance)" />

  <!-- Stage 2: Sentient Orbital Energy Halo Ring (Outer 3D Ellipse) -->
  <g transform="rotate(-22 {c} {c})">
    <ellipse cx="{c}" cy="{c}" rx="{int(r_sphere * 1.65)}" ry="{int(r_sphere * 0.42)}" fill="none" stroke="url(#haloRingGrad1)" stroke-width="6.5" filter="url(#ringGlow)" opacity="0.88" />
    <ellipse cx="{c}" cy="{c}" rx="{int(r_sphere * 1.65)}" ry="{int(r_sphere * 0.42)}" fill="none" stroke="#ffffff" stroke-width="2.5" opacity="0.92" />
  </g>

  <!-- Stage 3: Radiant Corona Ring -->
  <circle cx="{c}" cy="{c}" r="{r_corona}" fill="url(#coronalHalo)" />

  <!-- Stage 4: 3D Volumetric Body -->
  <circle cx="{c}" cy="{c}" r="{r_sphere}" fill="url(#orbVolumetric)" />

  <!-- Stage 5: Living Internal Fluid Core -->
  <g clip-path="url(#coreClip)">
    <ellipse cx="{p_x1}" cy="{p_y1}" rx="{int(r_sphere * 0.88)}" ry="{int(r_sphere * 0.58)}" fill="url(#ringGrad1)" filter="url(#vortexDeepBlur)" transform="rotate(35 {p_x1} {p_y1})" opacity="0.90" />
    <ellipse cx="{p_x2}" cy="{p_y2}" rx="{int(r_sphere * 0.80)}" ry="{int(r_sphere * 0.50)}" fill="url(#haloRingGrad2)" filter="url(#vortexDeepBlur)" transform="rotate(-30 {p_x2} {p_y2})" opacity="0.85" />

    <!-- Interlocking Quantum Ribbons -->
    <path d="M {c - int(r_sphere*0.75)} {c + int(r_sphere*0.12)} C {c - int(r_sphere*0.30)} {c - int(r_sphere*0.70)}, {c + int(r_sphere*0.25)} {c - int(r_sphere*0.50)}, {c + int(r_sphere*0.75)} {c - int(r_sphere*0.08)} C {c + int(r_sphere*0.30)} {c + int(r_sphere*0.60)}, {c - int(r_sphere*0.20)} {c + int(r_sphere*0.70)}, {c - int(r_sphere*0.75)} {c + int(r_sphere*0.12)} Z" fill="url(#ringGrad1)" filter="url(#vortexSharpBlur)" opacity="0.88" />

    <!-- Living Singularity Eye -->
    <circle cx="{c}" cy="{c}" r="{int(r_sphere * 0.34)}" fill="url(#vortexEye)" filter="url(#vortexSharpBlur)" opacity="0.98" />
    <circle cx="{c}" cy="{c}" r="{int(r_sphere * 0.14)}" fill="#ffffff" filter="url(#vortexSharpBlur)" opacity="0.98" />

    <!-- Bioluminescent Nodes -->
    <circle cx="{c - int(r_sphere * 0.30)}" cy="{c - int(r_sphere * 0.16)}" r="{int(r_sphere * 0.04)}" fill="#ffffff" filter="url(#vortexSharpBlur)" opacity="0.92" />
    <circle cx="{c + int(r_sphere * 0.34)}" cy="{c + int(r_sphere * 0.14)}" r="{int(r_sphere * 0.035)}" fill="{palette['inner_glow']}" filter="url(#vortexSharpBlur)" opacity="0.94" />
  </g>

  <!-- Stage 6: Inner Sentient Ring Foreground Overlap -->
  <g transform="rotate(28 {c} {c})">
    <ellipse cx="{c}" cy="{c}" rx="{int(r_sphere * 1.35)}" ry="{int(r_sphere * 0.32)}" fill="none" stroke="url(#haloRingGrad2)" stroke-width="4.5" filter="url(#ringGlow)" opacity="0.78" />
  </g>

  <!-- Stage 7: Fixed 3D Specular Crown -->
  <ellipse cx="{int(c - r_sphere * 0.28)}" cy="{int(c - r_sphere * 0.28)}" rx="{r_specular}" ry="{int(r_specular * 0.68)}" fill="url(#specularGleam)" transform="rotate(-28 {int(c - r_sphere * 0.28)} {int(c - r_sphere * 0.28)})" />

  <!-- Stage 8: Optical Edge Refraction -->
  <circle cx="{c}" cy="{c}" r="{r_sphere}" fill="none" stroke="#000000" stroke-width="2.0" opacity="0.85" />
  <circle cx="{c}" cy="{c}" r="{r_sphere - 1}" fill="none" stroke="{palette['core_highlight']}" stroke-width="0.9" opacity="0.65" />
</svg>"""

    if not save_path:
        save_path = Path("orb.svg")

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(svg_content, encoding="utf-8")

    return save_path, svg_content


class GradientOrbManager:
    """Manages the creation, animation formulas, and FFmpeg filtergraph strings for the AI Presenter Orb."""

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
        self.pixel_size = 520  # Prominent presenter size
        self.opacity = max(0.2, min(1.0, float(opacity)))
        self.animation = "speaking"
        self.custom_x = custom_x
        self.custom_y = custom_y
        self.audio_path = Path(audio_path) if audio_path else None
        self.total_duration = max(3.0, float(total_duration))
        self.intro_duration = max(1.5, float(intro_duration))

    def get_overlay_coordinates(self, video_width: int, video_height: int) -> Tuple[str, str]:
        """
        Calculates fluid 2D harmonic drift coordinates for the AI Presenter entity,
        centering it elegantly on screen with living organic micro-wander.
        """
        base_x = f"(W-w)/2"
        base_y = f"(H-h)/2 - {int(video_height * 0.05)}"

        # Living entity 2D organic floating drift
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
        Generates the FFmpeg filter chain for the AI Presenter entity:
        - Vocal speech envelope reactivity: swells +5.5% on speech peaks
        - Voice incandescence: radiant brightness and contrast surge during vocal articulation
        - Organic harmonic breathing drift in speech pauses
        """
        target_size = self.pixel_size
        effective_opacity = self.opacity
        speech_intervals: List[Tuple[float, float]] = []

        if self.audio_path and self.audio_path.exists():
            speech_intervals = extract_audio_speech_envelope(self.audio_path)

        filters = []
        base_s = str(target_size)

        if speech_intervals:
            conds = [f"between(t,{start:.2f},{end:.2f})" for start, end in speech_intervals]
            speech_mask = f"min(1,{'+'.join(conds)})"
            speech_cadence = f"(max(0,sin(2*PI*t/0.48))*{speech_mask})"

            scale_val = f"trunc({base_s}*(1.0 + 0.03*sin(2*PI*t/2.5) + 0.055*{speech_cadence})/2)*2"
            scale_expr = f"eval=frame:w='{scale_val}':h='{scale_val}'"
            eq_expr = f"brightness='0.06*{speech_cadence}':contrast='1.0 + 0.12*{speech_mask}'"
            hue_expr = f"h='20*{speech_cadence} + 10*sin(2*PI*t/2.4)':s='1.0 + 0.18*{speech_mask}'"
            rotate_expr = f"a='0.04*sin(2*PI*t/3.2)':ow='iw':oh='ih':c=none"

            filters.append(f"[{input_idx}:v]scale={scale_expr}")
            filters.append(f"rotate={rotate_expr}")
            filters.append(f"eq={eq_expr}")
            filters.append(f"hue={hue_expr}")
            filters.append("format=yuva420p")
            filters.append(f"colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]")
        else:
            scale_val = f"trunc({base_s}*(1.0 + 0.04*sin(2*PI*t/2.4))/2)*2"
            scale_expr = f"eval=frame:w='{scale_val}':h='{scale_val}'"
            hue_expr = "h='12*sin(2*PI*t/2.5)':s='1.0 + 0.08*sin(2*PI*t/2.5)'"
            rotate_expr = "a='0.03*sin(2*PI*t/3.6)':ow='iw':oh='ih':c=none"

            filters.append(f"[{input_idx}:v]scale={scale_expr}")
            filters.append(f"rotate={rotate_expr}")
            filters.append(f"hue={hue_expr}")
            filters.append("format=yuva420p")
            filters.append(f"colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]")

        return ",".join(filters)


def get_or_create_orb_asset(
    palette: str = "quantum",
    target_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> Path:
    """
    Retrieves or generates a high-resolution transparent RGBA PNG asset
    for the AI Presenter entity.
    """
    palette_key = palette.lower().strip() if palette else "quantum"
    if palette_key not in ORB_PALETTES:
        palette_key = "quantum"

    dest_dir = target_dir or (Path(__file__).resolve().parent.parent / "assets" / "orbs")
    dest_dir.mkdir(parents=True, exist_ok=True)

    png_path = dest_dir / f"orb_{palette_key}.png"
    svg_path = dest_dir / f"orb_{palette_key}.svg"

    if not force_refresh and png_path.exists() and png_path.stat().st_size > 1000:
        return png_path

    generate_gradient_orb_svg(palette_key=palette_key, canvas_size=1000, save_path=svg_path)

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(svg_path), "-pix_fmt", "rgba", str(png_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception:
        if svg_path.exists():
            return svg_path

    return png_path if png_path.exists() else svg_path


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
    """
    Renders an ultra-fast preview video of the AI Presenter Orb.
    """
    if output_path is None:
        out_dir = Path("output") / "orb_previews"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"test_orb_{palette}_presenter.mp4"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n🔮 [AI Presenter Tester] Generando vista previa del Entidad Presentador Orbe...")
    print(f"   • Paleta: '{palette}' | Opacidad: {opacity}")
    print(f"   • Duración: {duration}s | Resolución: {width}x{height}")

    orb_asset = get_or_create_orb_asset(palette=palette)
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
        f"[v_orb]drawtext=text='AI PREENTER ENTITY \\: {palette.upper()}':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.65:boxborderw=12:x=(w-text_w)/2:y=180[vout]"
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
        "-loop", "1", "-i", str(orb_asset),
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
            "-loop", "1", "-i", str(orb_asset),
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

    print(f"\n✨ ¡Vista previa del Presentador IA generada!")
    print(f"🎬 Video listo: {output_path.resolve()}\n")
    return output_path
