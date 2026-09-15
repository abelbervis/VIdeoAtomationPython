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
) -> Optional[Path]:
    """Renders a stunning co-host conversation video with two bio-reactive orbs and dynamic camera cuts."""
    # 1. If topic is provided and debate_script is not provided, generate with AI
    if not debate_script and topic:
        from ai.debate_generator import DebateScriptGenerator
        gen = DebateScriptGenerator(
            preferred_provider=llm_provider,
            gemini_key=gemini_key,
            groq_key=groq_key,
            openai_key=openai_key
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

    if debate_script:
        if debate_script.get("headline_hook"):
            headline_hook = debate_script["headline_hook"]
        holograms = debate_script.get("holograms", {})
        if "quantum" in holograms:
            hq = holograms["quantum"]
            holo_q_title = str(hq.get("title", holo_q_title)).upper()
            holo_q_sub = str(hq.get("subtitle", holo_q_sub))
            holo_q_cat = str(hq.get("category", holo_q_cat))
        if "solar" in holograms:
            hs = holograms["solar"]
            holo_s_title = str(hs.get("title", holo_s_title)).upper()
            holo_s_sub = str(hs.get("subtitle", holo_s_sub))
            holo_s_cat = str(hs.get("category", holo_s_cat))

        scenes = debate_script.get("scenes", [])
        if len(scenes) > 0 and scenes[0].get("text"):
            q_part1 = scenes[0]["text"]
        if len(scenes) > 1 and scenes[1].get("text"):
            q_part2 = scenes[1]["text"]
        if len(scenes) > 2 and scenes[2].get("text"):
            s_part3 = scenes[2]["text"]
        if len(scenes) > 3 and scenes[3].get("text"):
            both_part4 = scenes[3]["text"]

        script_json_path = output_path.parent / "script.json"
        script_json_path.write_text(json.dumps(debate_script, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n🔮 [AI Co-Host Debate Express] Renderizando video con Doble Orbe y Multi-Cámara...")
    print(f"   • Orbe 1: QUANTUM (Azul Eléctrico / Cyan) | Orbe 2: SOLAR (Ámbar / Oro)")
    print(f"   • Hook: {headline_hook}")
    print(f"   • HUD Holográfico Q: [{holo_q_cat}] {holo_q_title} -> {holo_q_sub}")
    print(f"   • HUD Holográfico S: [{holo_s_cat}] {holo_s_title} -> {holo_s_sub}")
    print(f"   • Outro CTA Resonancia: {both_part4}")

    # Generate both assets
    orb_quantum = get_or_create_orb_asset(palette="quantum", force_refresh=True)
    orb_solar = get_or_create_orb_asset(palette="solar", force_refresh=True)

    # Generate Holographic Floating Reference Cards (Modern Apple/Vercel Frosted Glass)
    from video.hologram import generate_hologram_card_svg, generate_presenter_badge_svg
    holo_q_path = output_path.parent / "_holo_q.svg"
    holo_s_path = output_path.parent / "_holo_s.svg"
    badge_q_path = output_path.parent / "_badge_q.svg"
    badge_s_path = output_path.parent / "_badge_s.svg"

    generate_hologram_card_svg(
        title=holo_q_title,
        subtitle=holo_q_sub,
        category=holo_q_cat,
        color_theme="cyan",
        width=620,
        height=240,
        output_path=holo_q_path
    )
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

    # Dynamic timeline variables
    t0 = 0.0
    t1 = 3.2
    t2 = 6.4
    t3 = 9.8
    total_duration = 12.0

    if not resolved_audio:
        part1_path = output_path.parent / "_temp_q_part1.mp3"
        part2_path = output_path.parent / "_temp_q_part2.mp3"
        part3_path = output_path.parent / "_temp_s_part3.mp3"
        part4_q_path = output_path.parent / "_temp_both_q.mp3"
        part4_s_path = output_path.parent / "_temp_both_s.mp3"
        sfx_intro_path = output_path.parent / "_temp_sfx_intro.wav"
        sfx_zoom_path = output_path.parent / "_temp_sfx_zoom.wav"
        sfx_pan_path = output_path.parent / "_temp_sfx_pan.wav"
        sfx_wide_path = output_path.parent / "_temp_sfx_wide.wav"
        sfx_res_path = output_path.parent / "_temp_sfx_res.wav"
        music_bg_path = output_path.parent / "_temp_music_ambient.wav"
        
        from audio.tts import EdgeTTSProvider, GoogleTTSProvider
        from audio.sfx import synthesize_camera_servo_sfx, synthesize_space_ambient_pad
        from audio.music import MusicManager

        tts_edge = EdgeTTSProvider()
        
        # Test a brief call to see if edge neural is online, else fallback
        test_file = output_path.parent / "_test_probe.mp3"
        use_cosmic_edge = tts_edge.synthesize_text("Hola", test_file)
        if test_file.exists():
            test_file.unlink()

        if use_cosmic_edge:
            syn1 = tts_edge.synthesize_cosmic_entity(q_part1, part1_path, entity="quantum")
            syn2 = tts_edge.synthesize_cosmic_entity(q_part2, part2_path, entity="quantum")
            syn3 = tts_edge.synthesize_cosmic_entity(s_part3, part3_path, entity="solar")
            syn4_q = tts_edge.synthesize_cosmic_entity(both_part4, part4_q_path, entity="quantum")
            syn4_s = tts_edge.synthesize_cosmic_entity(both_part4, part4_s_path, entity="solar")
        else:
            tts_fallback = GoogleTTSProvider(language="es")
            syn1 = tts_fallback.synthesize_text(q_part1, part1_path)
            syn2 = tts_fallback.synthesize_text(q_part2, part2_path)
            syn3 = tts_fallback.synthesize_text(s_part3, part3_path)
            syn4_q = tts_fallback.synthesize_text(both_part4, part4_q_path)
            syn4_s = tts_fallback.synthesize_text(both_part4, part4_s_path)

        # Accurately measure each speech part duration to PREVENT ANY AUDIO OVERLAP
        dur1 = _get_audio_duration_secs(part1_path, 3.0)
        dur2 = _get_audio_duration_secs(part2_path, 3.0)
        dur3 = _get_audio_duration_secs(part3_path, 3.2)
        dur4_q = _get_audio_duration_secs(part4_q_path, 2.5)
        dur4_s = _get_audio_duration_secs(part4_s_path, 2.5)
        dur4 = max(dur4_q, dur4_s)

        pause = 0.18  # Natural speech boundary pause in seconds
        t0 = 0.0
        t1 = round(dur1 + pause, 2)
        t2 = round(t1 + dur2 + pause, 2)
        t3 = round(t2 + dur3 + pause, 2)
        total_duration = round(max(t3 + dur4 + 0.9, 12.0), 2)

        print(f"   • Línea de Tiempo Dialéctica: T1={t1}s | T2={t2}s | T3={t3}s | Dur4={dur4}s | Total={total_duration}s")

        # Synthesize camera transition SFX & entity stingers
        sfx_q_hum_path = output_path.parent / "_temp_sfx_q_hum.wav"
        sfx_s_flare_path = output_path.parent / "_temp_sfx_s_flare.wav"
        
        synthesize_camera_servo_sfx(sfx_intro_path, duration=1.1, sfx_type="intro")
        synthesize_camera_servo_sfx(sfx_zoom_path, duration=0.52, sfx_type="whoosh_quantum")
        synthesize_camera_servo_sfx(sfx_pan_path, duration=0.52, sfx_type="whoosh_solar")
        synthesize_camera_servo_sfx(sfx_wide_path, duration=0.60, sfx_type="pull_back")
        synthesize_camera_servo_sfx(sfx_res_path, duration=2.5, sfx_type="cosmic_resonance")
        synthesize_camera_servo_sfx(sfx_q_hum_path, duration=1.2, sfx_type="quantum_hum")
        synthesize_camera_servo_sfx(sfx_s_flare_path, duration=0.9, sfx_type="solar_flare")

        # Prepare background soundtrack
        music_mgr = MusicManager()
        bg_track = music_mgr.get_background_track()
        if bg_track and bg_track.exists():
            music_bg_path = bg_track
        else:
            synthesize_space_ambient_pad(music_bg_path, duration=total_duration)
        
        if syn1 and syn2 and syn3 and part1_path.exists() and part2_path.exists() and part3_path.exists():
            v1_delay = 0
            v2_delay = int(t1 * 1000)
            v3_delay = int(t2 * 1000)
            v4_delay = int(t3 * 1000)
            sfx0_delay = 20
            sfx1_delay = int(max(0.0, t1 - 0.08) * 1000)
            sfx2_delay = int(max(0.0, t2 - 0.08) * 1000)
            sfx3_delay = int(max(0.0, t3 - 0.08) * 1000)
            sfx_res_delay = int(t3 * 1000)
            sfx_q_hum_delay = int(t1 * 1000)
            sfx_s_flare_delay = int(t2 * 1000)

            concat_cmd = [
                "ffmpeg", "-y",
                "-i", str(part1_path),
                "-i", str(part2_path),
                "-i", str(part3_path),
                "-i", str(part4_q_path),
                "-i", str(part4_s_path),
                "-i", str(sfx_intro_path),
                "-i", str(sfx_zoom_path),
                "-i", str(sfx_pan_path),
                "-i", str(sfx_wide_path),
                "-i", str(sfx_res_path),
                "-i", str(sfx_q_hum_path),
                "-i", str(sfx_s_flare_path),
                "-stream_loop", "-1", "-i", str(music_bg_path),
                "-filter_complex",
                f"[0:a]adelay={v1_delay}|{v1_delay},volume=1.0[v1];"
                f"[1:a]adelay={v2_delay}|{v2_delay},volume=1.0[v2];"
                f"[2:a]adelay={v3_delay}|{v3_delay},volume=1.0[v3];"
                f"[3:a]adelay={v4_delay}|{v4_delay},volume=0.90[v4_q];"
                f"[4:a]adelay={v4_delay}|{v4_delay},volume=0.90[v4_s];"
                f"[5:a]adelay={sfx0_delay}|{sfx0_delay},volume=0.42[sfx0];"
                f"[6:a]adelay={sfx1_delay}|{sfx1_delay},volume=0.38[sfx1];"
                f"[7:a]adelay={sfx2_delay}|{sfx2_delay},volume=0.38[sfx2];"
                f"[8:a]adelay={sfx3_delay}|{sfx3_delay},volume=0.42[sfx3];"
                f"[9:a]adelay={sfx_res_delay}|{sfx_res_delay},volume=0.45[sfx_res];"
                f"[10:a]adelay={sfx_q_hum_delay}|{sfx_q_hum_delay},volume=0.32[sfx_q_hum];"
                f"[11:a]adelay={sfx_s_flare_delay}|{sfx_s_flare_delay},volume=0.28[sfx_s_flare];"
                f"[12:a]volume=0.16,afade=t=in:st=0:d=1.0,afade=t=out:st={round(total_duration - 1.4, 2)}:d=1.4[bgm];"
                "[v1][v2][v3][v4_q][v4_s][sfx0][sfx1][sfx2][sfx3][sfx_res][sfx_q_hum][sfx_s_flare][bgm]amix=inputs=13:dropout_transition=0:normalize=0[aout]",
                "-map", "[aout]",
                "-t", str(total_duration),
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
            
            for p in [part1_path, part2_path, part3_path, part4_q_path, part4_s_path, sfx_intro_path, sfx_zoom_path, sfx_pan_path, sfx_wide_path, sfx_res_path, sfx_q_hum_path, sfx_s_flare_path]:
                if p.exists():
                    try:
                        p.unlink()
                    except Exception:
                        pass
                    except Exception:
                        pass
            if music_bg_path.name == "_temp_music_ambient.wav" and music_bg_path.exists():
                try:
                    music_bg_path.unlink()
                except Exception:
                    pass
    else:
        total_duration = _get_audio_duration_secs(resolved_audio, 12.0)
        t1 = round(total_duration * 0.27, 2)
        t2 = round(total_duration * 0.54, 2)
        t3 = round(total_duration * 0.80, 2)

    # Build advanced video filter chains for double overlays & scale changes (Virtual Camera)
    # Audio-reactive speech cadence ripple (Dynamic pulsing & physical expansion on speech peaks)
    voice_pulse_q = "(0.5 + 0.35*sin(2*PI*t/0.16) + 0.15*cos(2*PI*t/0.28))"
    speech_mask_q = f"(between(t,0,{t2}) + between(t,{t3},{total_duration}))"
    eq_q = f"brightness='-0.18 + (0.36 + 0.12*{voice_pulse_q})*{speech_mask_q}':contrast='0.70 + (0.60 + 0.22*{voice_pulse_q})*{speech_mask_q}'"
    hue_q = f"h='(14 + 6*{voice_pulse_q})*{speech_mask_q} + 6*sin(2*PI*t/2.4)':s='0.60 + (0.70 + 0.25*{voice_pulse_q})*{speech_mask_q}'"
    
    voice_pulse_s = "(0.5 + 0.35*sin(2*PI*t/0.14) + 0.15*cos(2*PI*t/0.26))"
    speech_mask_s = f"between(t,{t2},{total_duration})"
    eq_s = f"brightness='-0.04 + (0.22 + 0.10*{voice_pulse_s})*{speech_mask_s}':contrast='0.92 + (0.28 + 0.14*{voice_pulse_s})*{speech_mask_s}'"
    hue_s = f"h='(14 + 6*{voice_pulse_s})*{speech_mask_s} + 6*sin(2*PI*t/2.4)':s='0.85 + (0.50 + 0.20*{voice_pulse_s})*{speech_mask_s}'"

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

    from utils.fonts import resolve_best_font_path
    font_param, _ = resolve_best_font_path()

    escaped_headline_hook = headline_hook.replace(":", "\\:").replace("'", "\\'")

    # High-Performance Futuristic ASS Karaoke Subtitles (Entity Palettes, Pop-In Animation & Word Glow)
    from subtitles.generator import generate_cosmic_debate_karaoke_ass
    ass_sub_path = output_path.parent / "_temp_debate_karaoke.ass"
    scenes_sub_data = [
        {"speaker": "Quantum", "entity": "quantum", "text": q_part1, "start": 0.0, "end": t1},
        {"speaker": "Quantum", "entity": "quantum", "text": q_part2, "start": t1, "end": t2},
        {"speaker": "Solar", "entity": "solar", "text": s_part3, "start": t2, "end": t3},
        {"speaker": "Ambos", "entity": "both", "text": both_part4, "start": t3, "end": total_duration},
    ]
    generate_cosmic_debate_karaoke_ass(scenes_sub_data, ass_sub_path, width=width, height=height)
    escaped_ass_path = str(ass_sub_path.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")

    bg_input = f"color=c=0x08090f:s={width}x{height}:r=30:d={total_duration}"

    filter_complex = [
        # 0. Hologram Reference Card & Presenter Badge Pre-scaling
        "[3:v]scale=540:-2,format=yuva420p[holo_q]",
        "[4:v]scale=540:-2,format=yuva420p[holo_s]",
        "[5:v]scale=340:-2,format=yuva420p[badge_q]",
        "[6:v]scale=340:-2,format=yuva420p[badge_s]",

        # 1. Split streams to apply physical static transparency to separate active/resting layers
        "[1:v]split=4[q_t1][q_t2][q_t4][q_glow]",
        "[2:v]split=4[s_t1][s_t3][s_t4][s_glow]",
        
        # 2. Render each state independently with speech-reactive color surges, contrast flares and luminescence
        f"[q_t1]scale=355:355,eq={eq_q},hue={hue_q},format=yuva420p,colorchannelmixer=aa=0.95[orb_q_wide_t1]",
        f"[q_t2]scale=550:550,eq={eq_q},hue={hue_q},format=yuva420p,colorchannelmixer=aa=0.95[orb_q_close_t2]",
        f"[q_t4]scale=355:355,eq={eq_q},hue={hue_q},format=yuva420p,colorchannelmixer=aa=0.98[orb_q_wide_t4]",
        
        f"[s_t1]scale=310:310,eq={eq_s},hue={hue_s},format=yuva420p,colorchannelmixer=aa=0.52[orb_s_wide_t1]",
        f"[s_t3]scale=550:550,eq={eq_s},hue={hue_s},format=yuva420p,colorchannelmixer=aa=0.95[orb_s_close_t3]",
        f"[s_t4]scale=355:355,eq={eq_s},hue={hue_s},format=yuva420p,colorchannelmixer=aa=0.98[orb_s_wide_t4]",
        
        # 3. Render dynamic ambient glow backplates using ultra-fast pre-scaled blur with audio-reactive intensity
        f"[q_glow]scale=120:120,eq={eq_q},hue={hue_q},boxblur=24:3,scale=1080:1920,format=yuva420p,colorchannelmixer=aa=0.25[bg_glow_q]",
        f"[s_glow]scale=120:120,eq={eq_s},hue={hue_s},boxblur=24:3,scale=1080:1920,format=yuva420p,colorchannelmixer=aa=0.25[bg_glow_s]",
        
        # 4. Apply background grading and overlay dynamic glows first to make the ambient background
        f"[0:v]eq=brightness=-0.01:contrast=1.05[bg_graded]",
        f"[bg_graded][bg_glow_q]overlay=eval=frame:enable='between(t,0,{t2}) + between(t,{t3},{total_duration})'[bg_glowed_1]",
        f"[bg_glowed_1][bg_glow_s]overlay=eval=frame:enable='between(t,{t2},{total_duration})'[bg_ambient]",
        
        # 5. Sequentially overlay the foreground orbs with power ignition snap on frame 0 and matching drifts
        # Toma 1 (0 -> t1): Wide Shot. Power ignition snap + Presenter Badges Floating below each orb
        f"[bg_ambient][orb_q_wide_t1]overlay=eval=frame:x='W*0.25-w/2 + {drift_q_active_x} + {drift_intro_x}':y='H*0.38-h/2 + {drift_q_active_y} + {drift_intro_y}':enable='between(t,0,{t1})'[v1]",
        f"[v1][orb_s_wide_t1]overlay=eval=frame:x='W*0.75-w/2 - 28 + {drift_s_resting_x} + {drift_intro_x}':y='H*0.39-h/2 + {drift_s_resting_y} + {drift_intro_y}':enable='between(t,0,{t1})'[v1_orbs]",
        f"[v1_orbs][badge_q]overlay=eval=frame:x='W*0.25-w/2 + 5.0*sin(2*PI*(t-0.4)/2.2)':y='H*0.52-h/2 + 4.0*cos(2*PI*(t-0.4)/2.2)':enable='between(t,0.3,{max(0.4, round(t1-0.2, 2))})'[v1_bdg_q]",
        f"[v1_bdg_q][badge_s]overlay=eval=frame:x='W*0.75-w/2 - 28 + 5.0*cos(2*PI*(t-0.4)/2.4)':y='H*0.52-h/2 + 4.0*sin(2*PI*(t-0.4)/2.4)':enable='between(t,0.3,{max(0.4, round(t1-0.2, 2))})'[v2]",
        
        # Toma 2 (t1 -> t2): Close Up Quantum active + Floating Sci-Fi Hologram Card 1
        f"[v2][orb_q_close_t2]overlay=eval=frame:x='W/2-w/2 + {drift_q_active_x} + 25.0*exp(-6.5*(t-{t1}))*cos(16.0*(t-{t1}))':y='H*0.38-h/2 + {drift_q_active_y} + 30.0*exp(-6.5*(t-{t1}))*sin(16.0*(t-{t1}))':enable='between(t,{t1},{t2})'[v3]",
        f"[v3][holo_q]overlay=eval=frame:x='(W-w)/2':y='H*0.12-h/2 + 6.0*sin(2*PI*(t-{round(t1+0.1, 2)})/2.4)':enable='between(t,{round(t1+0.1, 2)},{max(round(t1+0.2, 2), round(t2-0.2, 2))})'[v3_holo]",
        
        # Toma 3 (t2 -> t3): Close Up Solar active + Floating Sci-Fi Hologram Card 2
        f"[v3_holo][orb_s_close_t3]overlay=eval=frame:x='W/2-w/2 + {drift_s_active_x} + 25.0*exp(-6.5*(t-{t2}))*cos(16.0*(t-{t2}))':y='H*0.38-h/2 + {drift_s_active_y} + 30.0*exp(-6.5*(t-{t2}))*sin(16.0*(t-{t2}))':enable='between(t,{t2},{t3})'[v4]",
        f"[v4][holo_s]overlay=eval=frame:x='(W-w)/2':y='H*0.12-h/2 + 6.0*cos(2*PI*(t-{round(t2+0.1, 2)})/2.6)':enable='between(t,{round(t2+0.1, 2)},{max(round(t2+0.2, 2), round(t3-0.2, 2))})'[v4_holo]",
        
        # Toma 4 (t3 -> total_duration): Wide Shot Harmonic Resonance Outro (Both Orbs Glow in Resonance)
        f"[v4_holo][orb_q_wide_t4]overlay=eval=frame:x='W*0.25-w/2 + {drift_q_active_x} + 15.0*exp(-6.5*(t-{t3}))*cos(16.0*(t-{t3}))':y='H*0.38-h/2 + {drift_q_active_y} + 18.0*exp(-6.5*(t-{t3}))*sin(16.0*(t-{t3}))':enable='between(t,{t3},{total_duration})'[v5]",
        f"[v5][orb_s_wide_t4]overlay=eval=frame:x='W*0.75-w/2 - 28 + {drift_s_active_x} + 15.0*exp(-6.5*(t-{t3}))*cos(16.0*(t-{t3}))':y='H*0.39-h/2 + {drift_s_active_y} + 18.0*exp(-6.5*(t-{t3}))*sin(16.0*(t-{t3}))':enable='between(t,{t3},{total_duration})'[v6]",
        
        # 6. Headline Hook Badge Overlay (Top Center 0.0s -> min(t1, 2.8s))
        f"[v6]drawtext=text='{escaped_headline_hook}':{font_param}:fontcolor=white:fontsize=34:box=1:boxcolor=0x08101e@0.92:boxborderw=20:borderw=2:bordercolor=0x00f0ff:x=(w-text_w)/2:y=140:enable='between(t,0,{min(round(t1, 2), 2.8)})'[v_hook]",

        # 7. Outro Verdict Header Badge Overlay (Top Center t3 -> total_duration)
        f"[v_hook]drawtext=text='⚡ VEREDICTO CÓSMICO ⚡':{font_param}:fontcolor=white:fontsize=34:box=1:boxcolor=0x08101e@0.92:boxborderw=20:borderw=2:bordercolor=0xffb300:x=(w-text_w)/2:y=140:enable='between(t,{t3},{total_duration})'[v_outro_badge]",

        # 8. High-Performance Futuristic ASS Karaoke Subtitles (Word-by-word glow active highlights & speaker palettes)
        f"[v_outro_badge]ass='{escaped_ass_path}'[vout]"
    ]
    filter_str = ";".join(filter_complex)

    audio_input_args = []
    if resolved_audio and resolved_audio.exists():
        audio_input_args = ["-i", str(resolved_audio)]
        audio_map = ["-map", "7:a"]
    else:
        audio_input_args = ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
        audio_map = ["-map", "7:a"]

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", bg_input,
        "-stream_loop", "-1", "-i", str(orb_quantum),
        "-stream_loop", "-1", "-i", str(orb_solar),
        "-stream_loop", "-1", "-i", str(holo_q_path),
        "-stream_loop", "-1", "-i", str(holo_s_path),
        "-stream_loop", "-1", "-i", str(badge_q_path),
        "-stream_loop", "-1", "-i", str(badge_s_path),
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
        for p in [temp_test_audio, ass_sub_path]:
            if p and p.exists():
                try:
                    p.unlink()
                except Exception:
                    pass

    print(f"\n✨ ¡Vista previa del Orbe Bio-Reactivo generada con éxito!")
    print(f"🎬 Video listo: {output_path.resolve()}\n")
    return output_path


# Alias for explicit AI debate generation calls
render_cohost_debate_video = render_orb_test_preview

