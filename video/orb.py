"""
Gradient Orb Generator & Compositor for Viral Shorts.
Generates an animated, pulsing, multi-stop gradient orb (sphere) with:
- Luminous 3D core and diffused ambient outer glow
- Curated high-retention aesthetic palettes (Cosmic, Cyberpunk, Solar, Aurora, Nebula, Monochrome)
- Smooth harmonic pulsing (breathing scale), floating hover, and rotational shimmer
- Seamless FFmpeg filtergraph integration via vector SVG (rendered with librsvg)
- Configurable positioning (center, floating, ambient background, bottom, top-right)
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
    This creates compact, highly efficient FFmpeg filter graphs that never exceed
    expression parser limits or memory buffers.
    """
    audio_path = Path(audio_path)
    if not audio_path.exists() or audio_path.stat().st_size == 0:
        return []

    wav_to_clean: Optional[Path] = None
    read_path = audio_path

    # Convert a temporary mono PCM WAV if input is compressed (AAC/MP3)
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
        # 100ms window analysis
        chunk_size = max(1, s_rate // 10)

        raw_active = []
        for i in range(0, len(samples), chunk_size):
            chunk = samples[i:i + chunk_size]
            if not chunk:
                continue
            rms = math.sqrt(sum(s * s for s in chunk) / len(chunk))
            norm = min(1.0, rms / 8000.0)
            raw_active.append(norm >= threshold)

        # Detect raw active intervals
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

        # Merge close intervals (inter-word gaps < min_silence_dur) into smooth continuous speech blocks
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

        # Filter out negligible micro-clicks (<0.18s)
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


ORB_PALETTES: Dict[str, Dict[str, Any]] = {
    "cosmic": {
        "name": "Cosmic Void & Violet",
        "description": "Electric cyan core, ultraviolet body, neon magenta rim, deep cosmic void",
        "core_highlight": "#ffffff",
        "inner_glow": "#00f0ff",      # Electric Cyan
        "mid_gradient": "#8a2be2",    # Ultraviolet
        "outer_gradient": "#ff007f",  # Neon Magenta
        "deep_edge": "#120036",       # Deep Void
        "ambient_aura": "#8a2be2",
        "ambient_secondary": "#00f0ff",
        "default_blend": "normal",
    },
    "cyberpunk": {
        "name": "Cyberpunk Neon",
        "description": "Hot neon pink, electric cyan, acid purple, sunset amber",
        "core_highlight": "#ffffff",
        "inner_glow": "#ff007f",      # Hot Pink
        "mid_gradient": "#7b2cbf",    # Acid Purple
        "outer_gradient": "#00d4ff",  # Electric Blue
        "deep_edge": "#ff5400",       # Sunset Amber
        "ambient_aura": "#ff007f",
        "ambient_secondary": "#00d4ff",
        "default_blend": "screen",
    },
    "solar": {
        "name": "Solar Core",
        "description": "Blinding white core, solar flare amber, flame orange, deep crimson",
        "core_highlight": "#ffffff",
        "inner_glow": "#fff1a8",      # Warm Flare
        "mid_gradient": "#ffae00",    # Solar Amber
        "outer_gradient": "#ff4500",  # Flame Orange
        "deep_edge": "#990000",       # Crimson Edge
        "ambient_aura": "#ff8800",
        "ambient_secondary": "#ff2200",
        "default_blend": "screen",
    },
    "aurora": {
        "name": "Aurora Borealis",
        "description": "Mint glow, neon emerald, electric turquoise, deep sea cyan",
        "core_highlight": "#ffffff",
        "inner_glow": "#70ffbd",      # Mint
        "mid_gradient": "#00e599",    # Neon Emerald
        "outer_gradient": "#00d2b4",  # Electric Turquoise
        "deep_edge": "#003847",       # Deep Abyss
        "ambient_aura": "#00e599",
        "ambient_secondary": "#00d2b4",
        "default_blend": "screen",
    },
    "nebula": {
        "name": "Deep Space Nebula",
        "description": "Soft peach highlight, dreamy lavender, deep indigo, pure starlight",
        "core_highlight": "#ffffff",
        "inner_glow": "#ffd1dc",      # Pastel Pink
        "mid_gradient": "#b388ff",    # Lavender
        "outer_gradient": "#4a00e0",  # Indigo
        "deep_edge": "#0d0221",       # Midnight Void
        "ambient_aura": "#b388ff",
        "ambient_secondary": "#4a00e0",
        "default_blend": "normal",
    },
    "monochrome": {
        "name": "Luminous Platinum",
        "description": "Crisp pearlescent white, silver platinum, steel cyan, dark onyx",
        "core_highlight": "#ffffff",
        "inner_glow": "#e6f8ff",      # Ice White
        "mid_gradient": "#9bb8d3",    # Platinum Blue
        "outer_gradient": "#4a6984",  # Steel Slate
        "deep_edge": "#0f172a",       # Onyx
        "ambient_aura": "#9bb8d3",
        "ambient_secondary": "#ffffff",
        "default_blend": "screen",
    }
}

ORB_SIZE_MAP: Dict[str, int] = {
    "small": 240,
    "medium": 440,
    "large": 620,
    "ambient": 840,
}


def generate_gradient_orb_svg(
    palette_key: str = "cosmic",
    canvas_size: int = 1000,
    save_path: Optional[Path] = None,
) -> Tuple[Path, str]:
    """
    Generate a high-definition SVG file containing an organic 3D gradient orb with
    an intense, radiant multi-stage atmospheric glow, realistic volumetric lighting,
    and an internal fluid plasma core with vortex filaments.
    """
    palette = ORB_PALETTES.get(palette_key.lower().strip(), ORB_PALETTES["cosmic"])

    c = canvas_size // 2
    r_sphere = int(canvas_size * 0.26)
    r_corona = int(canvas_size * 0.35)
    r_aura = int(canvas_size * 0.42)
    r_specular = int(r_sphere * 0.45)

    # Coords for internal plasma vortex centers & spiral arms
    p_x1 = int(c - r_sphere * 0.40)
    p_y1 = int(c - r_sphere * 0.32)
    p_x2 = int(c + r_sphere * 0.38)
    p_y2 = int(c + r_sphere * 0.28)
    p_x3 = int(c - r_sphere * 0.25)
    p_y3 = int(c + r_sphere * 0.38)

    svg_content = f"""<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Multi-stage Gaussian Blur filters for radiant volumetric diffusion -->
    <filter id="ultraAura" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="80" result="blur1" />
    </filter>
    
    <filter id="softCorona" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="45" result="blur2" />
    </filter>

    <filter id="intenseGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="22" result="blur3" />
    </filter>

    <filter id="vortexDeepBlur" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="16" result="blurDeep" />
    </filter>

    <filter id="vortexSharpBlur" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blurSharp" />
    </filter>

    <clipPath id="coreClip">
      <circle cx="{c}" cy="{c}" r="{r_sphere}" />
    </clipPath>

    <!-- Layer 0: Ultra-wide diffused ambient radiance -->
    <radialGradient id="outerRadiance" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['ambient_aura']}" stop-opacity="0.95" />
      <stop offset="25%" stop-color="{palette['ambient_secondary']}" stop-opacity="0.70" />
      <stop offset="55%" stop-color="{palette['outer_gradient']}" stop-opacity="0.35" />
      <stop offset="80%" stop-color="{palette['mid_gradient']}" stop-opacity="0.10" />
      <stop offset="100%" stop-color="{palette['deep_edge']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- Layer 1: Radiant Coronal Flare Halo -->
    <radialGradient id="coronalHalo" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['core_highlight']}" stop-opacity="0.80" />
      <stop offset="35%" stop-color="{palette['inner_glow']}" stop-opacity="0.65" />
      <stop offset="70%" stop-color="{palette['ambient_aura']}" stop-opacity="0.30" />
      <stop offset="100%" stop-color="{palette['outer_gradient']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- Layer 2: Primary Volumetric 3D Sphere Radial Gradient -->
    <radialGradient id="orbVolumetric" cx="36%" cy="32%" r="68%" fx="32%" fy="28%">
      <stop offset="0%" stop-color="{palette['core_highlight']}" stop-opacity="1.0" />
      <stop offset="12%" stop-color="{palette['inner_glow']}" stop-opacity="0.98" />
      <stop offset="38%" stop-color="{palette['mid_gradient']}" stop-opacity="0.95" />
      <stop offset="72%" stop-color="{palette['outer_gradient']}" stop-opacity="0.90" />
      <stop offset="92%" stop-color="{palette['deep_edge']}" stop-opacity="0.75" />
      <stop offset="100%" stop-color="{palette['deep_edge']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- Multi-Layer Fluid Plasma Vortex Gradients -->
    <!-- Vortex Core Singularity Eye -->
    <radialGradient id="vortexEye" cx="48%" cy="46%" r="50%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="1.0" />
      <stop offset="20%" stop-color="{palette['core_highlight']}" stop-opacity="0.95" />
      <stop offset="55%" stop-color="{palette['inner_glow']}" stop-opacity="0.80" />
      <stop offset="85%" stop-color="{palette['ambient_aura']}" stop-opacity="0.30" />
      <stop offset="100%" stop-color="{palette['deep_edge']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- Layer 1: Primary Spiral Swirl Gradient -->
    <radialGradient id="plasmaVortex1" cx="42%" cy="38%" r="62%">
      <stop offset="0%" stop-color="{palette['inner_glow']}" stop-opacity="0.92" />
      <stop offset="35%" stop-color="{palette['ambient_aura']}" stop-opacity="0.75" />
      <stop offset="75%" stop-color="{palette['mid_gradient']}" stop-opacity="0.25" />
      <stop offset="100%" stop-color="{palette['deep_edge']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- Layer 2: Counter-Current Fluid Swirl -->
    <radialGradient id="plasmaVortex2" cx="58%" cy="62%" r="58%">
      <stop offset="0%" stop-color="{palette['core_highlight']}" stop-opacity="0.90" />
      <stop offset="30%" stop-color="{palette['ambient_secondary']}" stop-opacity="0.70" />
      <stop offset="70%" stop-color="{palette['outer_gradient']}" stop-opacity="0.20" />
      <stop offset="100%" stop-color="{palette['deep_edge']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- Layer 3: Fluid Spiral Arm Linear Flow -->
    <linearGradient id="spiralArmGrad1" x1="10%" y1="15%" x2="90%" y2="85%">
      <stop offset="0%" stop-color="{palette['core_highlight']}" stop-opacity="0.90" />
      <stop offset="30%" stop-color="{palette['inner_glow']}" stop-opacity="0.80" />
      <stop offset="65%" stop-color="{palette['ambient_aura']}" stop-opacity="0.50" />
      <stop offset="100%" stop-color="{palette['outer_gradient']}" stop-opacity="0.0" />
    </linearGradient>

    <!-- Layer 4: Counter Spiral Arm Linear Flow -->
    <linearGradient id="spiralArmGrad2" x1="85%" y1="20%" x2="15%" y2="80%">
      <stop offset="0%" stop-color="{palette['ambient_secondary']}" stop-opacity="0.85" />
      <stop offset="40%" stop-color="{palette['mid_gradient']}" stop-opacity="0.65" />
      <stop offset="80%" stop-color="{palette['deep_edge']}" stop-opacity="0.20" />
      <stop offset="100%" stop-color="{palette['deep_edge']}" stop-opacity="0.0" />
    </linearGradient>

    <!-- Layer 5: Caustic Equatorial Ring Arc -->
    <linearGradient id="causticRingGrad" x1="0%" y1="50%" x2="100%" y2="50%">
      <stop offset="0%" stop-color="{palette['inner_glow']}" stop-opacity="0.0" />
      <stop offset="25%" stop-color="{palette['core_highlight']}" stop-opacity="0.75" />
      <stop offset="50%" stop-color="{palette['inner_glow']}" stop-opacity="0.90" />
      <stop offset="75%" stop-color="{palette['ambient_secondary']}" stop-opacity="0.65" />
      <stop offset="100%" stop-color="{palette['outer_gradient']}" stop-opacity="0.0" />
    </linearGradient>

    <!-- Layer 6: Organic Specular Highlight Flare -->
    <radialGradient id="specularGleam" cx="30%" cy="26%" r="42%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.98" />
      <stop offset="35%" stop-color="{palette['inner_glow']}" stop-opacity="0.60" />
      <stop offset="80%" stop-color="{palette['mid_gradient']}" stop-opacity="0.10" />
      <stop offset="100%" stop-color="{palette['mid_gradient']}" stop-opacity="0.0" />
    </radialGradient>
  </defs>

  <!-- Stage 1: Ultra-Wide Diffused Atmospheric Radiance (Environmental Illumination) -->
  <circle cx="{c}" cy="{c}" r="{r_aura}" fill="url(#outerRadiance)" filter="url(#ultraAura)" />
  <circle cx="{c}" cy="{c}" r="{int(r_aura * 0.88)}" fill="url(#outerRadiance)" filter="url(#softCorona)" opacity="0.9" />

  <!-- Stage 2: Concentrated Radiant Corona Ring (Intense Edge Glow) -->
  <circle cx="{c}" cy="{c}" r="{r_corona}" fill="url(#coronalHalo)" filter="url(#intenseGlow)" />

  <!-- Stage 3: Main 3D Volumetric Living Core Body -->
  <circle cx="{c}" cy="{c}" r="{r_sphere}" fill="url(#orbVolumetric)" />

  <!-- Stage 4: Layered Fluid Internal Vortex Core (Multi-Stream Plasma Dynamo) -->
  <g clip-path="url(#coreClip)">
    <!-- Layer 4A: Deep Nebula Plasma Bed (Counter-rotating diffuse base) -->
    <ellipse cx="{p_x1}" cy="{p_y1}" rx="{int(r_sphere * 0.90)}" ry="{int(r_sphere * 0.60)}" fill="url(#plasmaVortex1)" filter="url(#vortexDeepBlur)" transform="rotate(45 {p_x1} {p_y1})" opacity="0.90" />
    <ellipse cx="{p_x2}" cy="{p_y2}" rx="{int(r_sphere * 0.80)}" ry="{int(r_sphere * 0.52)}" fill="url(#plasmaVortex2)" filter="url(#vortexDeepBlur)" transform="rotate(-35 {p_x2} {p_y2})" opacity="0.82" />
    <ellipse cx="{p_x3}" cy="{p_y3}" rx="{int(r_sphere * 0.70)}" ry="{int(r_sphere * 0.45)}" fill="url(#plasmaVortex1)" filter="url(#vortexDeepBlur)" transform="rotate(70 {p_x3} {p_y3})" opacity="0.70" />

    <!-- Layer 4B: Primary Fluid Vortex Spiral Arm (Clockwise Energy Stream) -->
    <path d="M {c - int(r_sphere*0.80)} {c + int(r_sphere*0.15)} C {c - int(r_sphere*0.35)} {c - int(r_sphere*0.75)}, {c + int(r_sphere*0.30)} {c - int(r_sphere*0.55)}, {c + int(r_sphere*0.80)} {c - int(r_sphere*0.10)} C {c + int(r_sphere*0.35)} {c + int(r_sphere*0.65)}, {c - int(r_sphere*0.25)} {c + int(r_sphere*0.75)}, {c - int(r_sphere*0.80)} {c + int(r_sphere*0.15)} Z" fill="url(#spiralArmGrad1)" filter="url(#vortexSharpBlur)" opacity="0.75" />

    <!-- Layer 4C: Secondary Counter-Fluid Spiral Arm (Counter-Clockwise Vortex) -->
    <path d="M {c - int(r_sphere*0.55)} {c - int(r_sphere*0.45)} C {c + int(r_sphere*0.05)} {c - int(r_sphere*0.80)}, {c + int(r_sphere*0.70)} {c + int(r_sphere*0.10)}, {c + int(r_sphere*0.45)} {c + int(r_sphere*0.65)} C {c - int(r_sphere*0.15)} {c + int(r_sphere*0.30)}, {c - int(r_sphere*0.45)} {c + int(r_sphere*0.15)}, {c - int(r_sphere*0.55)} {c - int(r_sphere*0.45)} Z" fill="url(#spiralArmGrad2)" filter="url(#vortexSharpBlur)" opacity="0.70" />

    <!-- Layer 4D: Inner Toroidal Caustic Ring (Equatorial Light Ribbon) -->
    <ellipse cx="{c}" cy="{c + int(r_sphere * 0.05)}" rx="{int(r_sphere * 0.72)}" ry="{int(r_sphere * 0.28)}" fill="url(#causticRingGrad)" filter="url(#vortexSharpBlur)" transform="rotate(-18 {c} {c})" opacity="0.80" />

    <!-- Layer 4E: Vortex Core Singularity Eye (Hyper-Bright Focus Center) -->
    <circle cx="{c - int(r_sphere * 0.06)}" cy="{c - int(r_sphere * 0.08)}" r="{int(r_sphere * 0.28)}" fill="url(#vortexEye)" filter="url(#vortexSharpBlur)" opacity="0.95" />
    <circle cx="{c - int(r_sphere * 0.06)}" cy="{c - int(r_sphere * 0.08)}" r="{int(r_sphere * 0.12)}" fill="#ffffff" filter="url(#vortexSharpBlur)" opacity="0.90" />

    <!-- Layer 4F: Quantum Plasma Nodes (Micro Sparkle Points) -->
    <circle cx="{c - int(r_sphere * 0.38)}" cy="{c - int(r_sphere * 0.22)}" r="{int(r_sphere * 0.04)}" fill="#ffffff" filter="url(#vortexSharpBlur)" opacity="0.85" />
    <circle cx="{c + int(r_sphere * 0.42)}" cy="{c + int(r_sphere * 0.18)}" r="{int(r_sphere * 0.035)}" fill="{palette['inner_glow']}" filter="url(#vortexSharpBlur)" opacity="0.90" />
    <circle cx="{c - int(r_sphere * 0.20)}" cy="{c + int(r_sphere * 0.40)}" r="{int(r_sphere * 0.03)}" fill="{palette['core_highlight']}" filter="url(#vortexSharpBlur)" opacity="0.80" />
  </g>

  <!-- Stage 5: High-Luminance Specular Flare Accent (Glassy Light Crown) -->
  <ellipse cx="{int(c * 0.84)}" cy="{int(c * 0.80)}" rx="{r_specular}" ry="{int(r_specular * 0.72)}" fill="url(#specularGleam)" transform="rotate(-20 {int(c * 0.84)} {int(c * 0.80)})" />
</svg>"""

    if not save_path:
        save_path = Path("orb.svg")

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(svg_content, encoding="utf-8")

    return save_path, svg_content


class GradientOrbManager:
    """Manages the creation, animation formulas, and FFmpeg filtergraph strings for gradient orbs."""

    def __init__(
        self,
        palette: str = "cosmic",
        position: str = "center",
        size: str = "medium",
        opacity: float = 0.90,
        animation: str = "pulse",
        custom_x: Optional[int] = None,
        custom_y: Optional[int] = None,
        audio_path: Optional[Path] = None,
    ):
        self.palette = palette.lower().strip() if palette else "cosmic"
        if self.palette not in ORB_PALETTES:
            self.palette = "cosmic"

        self.position = position.lower().strip() if position else "center"
        self.size_name = size.lower().strip() if size else "medium"
        self.pixel_size = ORB_SIZE_MAP.get(self.size_name, 440)
        self.opacity = max(0.1, min(1.0, float(opacity)))
        self.animation = animation.lower().strip() if animation else "pulse"
        self.custom_x = custom_x
        self.custom_y = custom_y
        self.audio_path = Path(audio_path) if audio_path else None

    def get_overlay_coordinates(self, video_width: int, video_height: int) -> Tuple[str, str]:
        """
        Calculates FFmpeg expression strings for X and Y overlay coordinates,
        taking animation (floating hover / bobbing) and positions into account.
        """
        # Base dimensions of scaled orb
        w_expr = "w"
        h_expr = "h"

        if self.custom_x is not None and self.custom_y is not None:
            base_x = str(self.custom_x)
            base_y = str(self.custom_y)
        elif self.position == "ambient":
            # Centered slightly above true center for background lighting ambiance
            base_x = f"(W-{w_expr})/2"
            base_y = f"(H-{h_expr})/2 - {int(video_height * 0.05)}"
        elif self.position in ("top-right", "top_right", "corner"):
            base_x = f"W-{w_expr}-50"
            base_y = "140"
        elif self.position in ("bottom-right", "bottom_right"):
            base_x = f"W-{w_expr}-60"
            base_y = f"H-{h_expr}-240"
        elif self.position == "bottom":
            base_x = f"(W-{w_expr})/2"
            base_y = f"H-{h_expr}-380"
        elif self.position == "floating":
            base_x = f"(W-{w_expr})/2"
            base_y = f"(H-{h_expr})/2 - {int(video_height * 0.04)}"
        else:
            # Default: center, slightly elevated to clear lower third captions
            base_x = f"(W-{w_expr})/2"
            base_y = f"(H-{h_expr})/2 - {int(video_height * 0.04)}"

        # Animate hovering motion (float, speaking or reactive)
        if self.animation in ("float", "hover") or self.position == "floating":
            # Compound harmonic motion (gentle organic drift in 2D space)
            x_anim = f"{base_x} + 26*sin(2*PI*t/3.2)"
            y_anim = f"{base_y} + 38*sin(2*PI*t/2.4)"
            return x_anim, y_anim
        elif self.animation in ("reactive", "speaking", "voice", "alive", "speech"):
            # Living entity: slight micro-wander while speaking plus vertical pulsation
            x_anim = f"{base_x} + 14*sin(2*PI*t/3.6)"
            y_anim = f"{base_y} + 20*sin(2*PI*t/2.2)"
            return x_anim, y_anim
        elif self.animation in ("pulse", "breathing"):
            # Subtle floating offset while pulsing so it feels alive and never static
            x_anim = f"{base_x} + 10*sin(2*PI*t/4.0)"
            y_anim = f"{base_y} + 16*sin(2*PI*t/2.8)"
            return x_anim, y_anim

        return base_x, base_y

    def build_filter_chain(
        self,
        input_idx: int,
        output_label: str,
        video_width: int,
        video_height: int,
        fps: int = 30,
    ) -> str:
        """
        Generate FFmpeg filter chain that animates the orb input (input_idx)
        and prepares it for overlaying onto the main video.
        Features:
          - Audio-reactive speech modulation (speaking / voice / reactive animation):
            dynamically swells in size with voice decibels and shifts color temperature.
          - In speech pauses: settles into gentle idle breathing.
          - Periodic pulse / breathing for fallback modes.
          - Smooth chroma & hue shifts so the orb feels alive.
        """
        target_size = self.pixel_size

        if self.position == "ambient":
            # Ambient mode uses larger soft radius with subtle breathing
            target_size = max(target_size, int(video_width * 0.78))
            effective_opacity = min(0.40, self.opacity)
        else:
            effective_opacity = self.opacity

        # Check if audio-reactive speech animation is requested or active
        is_audio_reactive = self.animation in ("reactive", "speaking", "voice", "alive", "speech")
        speech_intervals: List[Tuple[float, float]] = []

        if is_audio_reactive and self.audio_path and self.audio_path.exists():
            speech_intervals = extract_audio_speech_envelope(self.audio_path)

        filters = []
        if is_audio_reactive and speech_intervals:
            # Build ultra-compact speech activity mask (e.g. 5-25 continuous interval windows)
            conds = [f"between(t,{start:.2f},{end:.2f})" for start, end in speech_intervals]
            speech_mask = f"min(1,{'+'.join(conds)})"

            # Dynamic speech cadence:
            # - While speaking (mask == 1): dynamic expansion (+28% on syllable peaks) + voice shimmer
            # - In silence/pauses (mask == 0): settles into tranquil idle breathing (+- 4%)
            speech_cadence = f"(max(0,sin(2*PI*t/0.45))*{speech_mask})"
            scale_expr = (
                f"eval=frame:"
                f"w='trunc({target_size}*(1.0 + 0.04*sin(2*PI*t/2.5) + 0.28*{speech_cadence})/2)*2':"
                f"h='-2'"
            )

            # Chromatic vitality: shifts saturation and hue dynamically during speech bursts
            hue_expr = (
                f"h='65*{speech_cadence} + 18*sin(2*PI*t/2.0)':"
                f"s='1.0 + 0.28*{speech_mask}'"
            )

            filters.append(f"[{input_idx}:v]scale={scale_expr}")
            filters.append(f"hue={hue_expr}")
            filters.append("format=yuva420p")
            filters.append(f"colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]")
        elif is_audio_reactive and not speech_intervals:
            # Living speaking simulation if audio had no detectable voice or no file was passed:
            simulated_speech = "(max(0,sin(2*PI*t/1.2))*max(0,sin(2*PI*t/0.45)))"
            scale_expr = (
                f"eval=frame:"
                f"w='trunc({target_size}*(1.0 + 0.04*sin(2*PI*t/2.5) + 0.28*{simulated_speech})/2)*2':"
                f"h='-2'"
            )
            hue_expr = f"h='65*{simulated_speech} + 18*sin(2*PI*t/2.0)':s='1.0 + 0.25*{simulated_speech}'"

            filters.append(f"[{input_idx}:v]scale={scale_expr}")
            filters.append(f"hue={hue_expr}")
            filters.append("format=yuva420p")
            filters.append(f"colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]")
        elif self.animation in ("pulse", "breathing", "all"):
            # Rhythmic breathing with live subtle hue modulation: +/- 12% scale oscillation every 2.0s
            scale_expr = (
                f"eval=frame:"
                f"w='trunc({target_size}*(1.0 + 0.12*sin(2*PI*t/2.0))/2)*2':"
                f"h='-2'"
            )
            # Subtle breathing color temperature shift
            hue_expr = "h='24*sin(2*PI*t/2.0)':s='1.0 + 0.12*sin(2*PI*t/2.0)'"

            filters.append(f"[{input_idx}:v]scale={scale_expr}")
            filters.append(f"hue={hue_expr}")
            filters.append("format=yuva420p")
            filters.append(f"colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]")
        elif self.animation in ("float", "hover"):
            # Floating hover with subtle chromatic luminescence
            hue_expr = "h='30*sin(2*PI*t/3.0)':s='1.0 + 0.10*sin(2*PI*t/2.5)'"

            filters.append(f"[{input_idx}:v]scale={target_size}:-2")
            filters.append(f"hue={hue_expr}")
            filters.append("format=yuva420p")
            filters.append(f"colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]")
        else:
            scale_expr = f"{target_size}:-2"
            filters.append(f"[{input_idx}:v]scale={scale_expr}")
            filters.append("format=yuva420p")
            filters.append(f"colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]")

        return ",".join(filters)


def get_or_create_orb_asset(
    palette: str = "cosmic",
    target_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> Path:
    """
    Retrieves or generates a high-resolution transparent RGBA PNG asset
    with multi-stage atmospheric glow for the specified gradient orb palette.
    """
    import subprocess

    palette_key = palette.lower().strip() if palette else "cosmic"
    if palette_key not in ORB_PALETTES:
        palette_key = "cosmic"

    dest_dir = target_dir or (Path(__file__).resolve().parent.parent / "assets" / "orbs")
    dest_dir.mkdir(parents=True, exist_ok=True)

    png_path = dest_dir / f"orb_{palette_key}.png"
    svg_path = dest_dir / f"orb_{palette_key}.svg"

    if not force_refresh and png_path.exists() and png_path.stat().st_size > 1000:
        return png_path

    # Generate vector SVG with enhanced multi-layer radiant glow
    generate_gradient_orb_svg(palette_key=palette_key, canvas_size=1000, save_path=svg_path)

    # Render high-quality transparent RGBA PNG via FFmpeg
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(svg_path), "-pix_fmt", "rgba", str(png_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception:
        # Fallback to SVG directly if PNG render fails
        if svg_path.exists():
            return svg_path

    return png_path if png_path.exists() else svg_path


def render_orb_test_preview(
    palette: str = "cosmic",
    position: str = "center",
    size: str = "medium",
    animation: str = "pulse",
    opacity: float = 0.90,
    duration: float = 4.0,
    output_path: Optional[Path] = None,
    width: int = 1080,
    height: int = 1920,
    bg_style: str = "cosmic",
    sample_audio: Optional[Path] = None,
) -> Path:
    """
    Renders an ultra-fast (2-4 seconds) video preview of the animated gradient orb.
    Avoids running the entire generation pipeline (no script generation, no stock downloads).
    Produces a ready-to-view vertical MP4 in seconds.
    If animation is 'speaking' or 'reactive', generates or accepts sample speech audio
    so you can instantly see the orb modulate its size and color to real spoken words!
    """
    import subprocess
    import shutil

    if output_path is None:
        out_dir = Path("output") / "orb_previews"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / f"test_orb_{palette}_{position}_{animation}.mp4"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n🔮 [Orb Tester] Generando vista previa rápida del Orbe Gradiente...")
    print(f"   • Paleta: '{palette}'")
    print(f"   • Posición: '{position}'")
    print(f"   • Animación: '{animation}'")
    print(f"   • Tamaño: '{size}' | Opacidad: {opacity}")
    print(f"   • Duración: {duration}s | Resolución: {width}x{height}")

    # Generate or get asset
    orb_asset = get_or_create_orb_asset(palette=palette)

    # Handle sample audio for reactive/speaking mode
    temp_test_audio: Optional[Path] = None
    resolved_audio: Optional[Path] = sample_audio
    is_reactive = animation in ("reactive", "speaking", "voice", "alive", "speech")

    if is_reactive and not resolved_audio:
        temp_test_audio = output_path.parent / "_temp_test_voice.mp3"
        # Try synthesize sample speech sentence with GoogleTTSProvider
        speech_text = "El universo se expande a velocidades astronómicas que desafían la imaginación."
        from audio.tts import GoogleTTSProvider
        g_tts = GoogleTTSProvider(language="es")
        synthesized = g_tts.synthesize_text(speech_text, temp_test_audio)
        if synthesized and temp_test_audio.exists():
            resolved_audio = temp_test_audio
            # Update duration to match voice length + padding
            try:
                from utils.files import get_media_duration
                dur = get_media_duration(temp_test_audio)
                if dur and dur > 1.0:
                    duration = min(8.0, dur + 0.5)
            except Exception:
                pass
        else:
            # Fallback synthetic speech tone pulse pattern (1s silence, 2.5s cadence, 1s silence)
            temp_test_wav = output_path.parent / "_temp_test_voice.wav"
            try:
                subprocess.run([
                    "ffmpeg", "-y",
                    "-f", "lavfi", "-i", "sine=f=280:d=1.2",
                    "-f", "lavfi", "-i", "sine=f=420:d=1.4",
                    "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-filter_complex",
                    "[2:a]atrim=end=0.6[sil1];[0:a]volume=0.85[spk1];[2:a]atrim=end=0.4[pause];[1:a]volume=0.9[spk2];[2:a]atrim=end=0.6[sil2];[sil1][spk1][pause][spk2][sil2]concat=n=5:v=0:a=1[aout]",
                    "-map", "[aout]",
                    str(temp_test_wav)
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                resolved_audio = temp_test_wav
                duration = 4.2
            except Exception:
                resolved_audio = None

    # Initialize manager
    mgr = GradientOrbManager(
        palette=palette,
        position=position,
        size=size,
        opacity=opacity,
        animation=animation,
        audio_path=resolved_audio,
    )

    # Construct dynamic filter chains
    orb_filter = mgr.build_filter_chain(
        input_idx=1,
        output_label="orb_layer",
        video_width=width,
        video_height=height,
        fps=30
    )
    x_coord, y_coord = mgr.get_overlay_coordinates(width, height)

    # Background color: subtle dark space gradient simulation with lavfi color
    bg_color = "0x0b0e14" if bg_style == "cosmic" else "0x000000"

    # Filter complex with timer / label overlay so user sees live animation specs
    filter_complex = [
        orb_filter,
        f"[0:v][orb_layer]overlay=eval=frame:x='{x_coord}':y='{y_coord}':shortest=1[v_orb]",
        f"[v_orb]drawtext=text='LIVING ORB TESTER \\: {palette.upper()} ({animation.upper()})':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.65:boxborderw=12:x=(w-text_w)/2:y=180[vout]"
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
        "-f", "lavfi", "-i", f"color=c={bg_color}:s={width}x{height}:r=30:d={duration}",
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
        # Fallback if drawtext fails (e.g. missing font)
        fallback_filter = f"{orb_filter};[0:v][orb_layer]overlay=eval=frame:x='{x_coord}':y='{y_coord}':shortest=1[vout]"
        cmd_fallback = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c={bg_color}:s={width}x{height}:r=30:d={duration}",
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
        # Clean up temporary tester audio files
        for tmp in (temp_test_audio, output_path.parent / "_temp_test_voice.wav"):
            if tmp and tmp.exists():
                try:
                    tmp.unlink()
                except Exception:
                    pass

    print(f"\n✨ ¡Vista previa del Orbe generada en tiempo récord!")
    print(f"🎬 Video listo para ver: {output_path.resolve()}")
    print(f"📦 Tamaño: {output_path.stat().st_size / 1024:.1f} KB\n")
    return output_path

