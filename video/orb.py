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
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


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
    canvas_size: int = 800,
    save_path: Optional[Path] = None,
) -> Tuple[Path, str]:
    """
    Generate a high-definition SVG file containing an organic 3D gradient orb.
    Features:
      - 3-stage layered lighting: ambient diffused atmospheric halo + spherical 3D volume + luminous specular highlight.
      - Resolution-independent vector graphics natively parsed by FFmpeg's librsvg.
    """
    palette = ORB_PALETTES.get(palette_key.lower().strip(), ORB_PALETTES["cosmic"])

    c = canvas_size // 2
    r_sphere = int(canvas_size * 0.33)
    r_aura = int(canvas_size * 0.48)
    r_specular = int(r_sphere * 0.45)

    svg_content = f"""<svg width="{canvas_size}" height="{canvas_size}" viewBox="0 0 {canvas_size} {canvas_size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Filter for soft Gaussian glow diffusion -->
    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="36" result="blur" />
    </filter>
    
    <filter id="intenseAura" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="64" result="blur" />
    </filter>

    <!-- Outer Ambient Diffused Aura -->
    <radialGradient id="auraGrad" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{palette['ambient_aura']}" stop-opacity="0.85" />
      <stop offset="38%" stop-color="{palette['ambient_secondary']}" stop-opacity="0.45" />
      <stop offset="75%" stop-color="{palette['outer_gradient']}" stop-opacity="0.15" />
      <stop offset="100%" stop-color="{palette['deep_edge']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- Primary Volumetric 3D Sphere Radial Gradient -->
    <radialGradient id="orbVolumetric" cx="36%" cy="32%" r="68%" fx="32%" fy="28%">
      <stop offset="0%" stop-color="{palette['core_highlight']}" stop-opacity="1.0" />
      <stop offset="12%" stop-color="{palette['inner_glow']}" stop-opacity="0.98" />
      <stop offset="38%" stop-color="{palette['mid_gradient']}" stop-opacity="0.94" />
      <stop offset="70%" stop-color="{palette['outer_gradient']}" stop-opacity="0.88" />
      <stop offset="90%" stop-color="{palette['deep_edge']}" stop-opacity="0.65" />
      <stop offset="100%" stop-color="{palette['deep_edge']}" stop-opacity="0.0" />
    </radialGradient>

    <!-- Specular Flare Accent (Offset Luminous Crown) -->
    <radialGradient id="specularGleam" cx="30%" cy="26%" r="42%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.95" />
      <stop offset="40%" stop-color="{palette['inner_glow']}" stop-opacity="0.4" />
      <stop offset="100%" stop-color="{palette['mid_gradient']}" stop-opacity="0.0" />
    </radialGradient>
  </defs>

  <!-- Layer 1: Wide Ambient Diffused Aura -->
  <circle cx="{c}" cy="{c}" r="{r_aura}" fill="url(#auraGrad)" filter="url(#intenseAura)" />
  <circle cx="{c}" cy="{c}" r="{int(r_aura * 0.85)}" fill="url(#auraGrad)" filter="url(#softGlow)" />

  <!-- Layer 2: Main 3D Volumetric Sphere Body -->
  <circle cx="{c}" cy="{c}" r="{r_sphere}" fill="url(#orbVolumetric)" />

  <!-- Layer 3: Organic Specular Highlight -->
  <ellipse cx="{int(c * 0.82)}" cy="{int(c * 0.78)}" rx="{r_specular}" ry="{int(r_specular * 0.75)}" fill="url(#specularGleam)" transform="rotate(-18 {int(c * 0.82)} {int(c * 0.78)})" />
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

        # Animate hovering motion (float)
        if self.animation in ("float", "hover", "all") or self.position == "floating":
            # Compound harmonic motion (gentle organic drift in 2D space)
            x_anim = f"{base_x} + 26*sin(2*PI*t/3.2)"
            y_anim = f"{base_y} + 38*sin(2*PI*t/2.4)"
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
          - Dynamic scaling / periodic rhythmic breathing pulse
          - Alpha opacity modulation
          - Coordinate positioning & motion
        """
        target_size = self.pixel_size

        if self.position == "ambient":
            # Ambient mode uses larger soft radius with subtle breathing
            target_size = max(target_size, int(video_width * 0.78))
            effective_opacity = min(0.40, self.opacity)
        else:
            effective_opacity = self.opacity

        # Pulsing scale expression (distinct, clearly visible periodic breathing)
        if self.animation in ("pulse", "breathing", "all"):
            # Rhythmic breathing: +/- 15% scale oscillation every 2.0 seconds
            scale_expr = (
                f"eval=frame:"
                f"w='trunc({target_size}*(1.0 + 0.15*sin(2*PI*t/2.0))/2)*2':"
                f"h='-2'"
            )
        else:
            scale_expr = f"{target_size}:-2"

        # Alpha opacity modulation (constant factor across frames for maximum FFmpeg compatibility)
        filters = [
            f"[{input_idx}:v]scale={scale_expr}",
            "format=yuva420p",
            f"colorchannelmixer=aa={effective_opacity:.2f}[{output_label}]"
        ]

        return ",".join(filters)


def get_or_create_orb_asset(
    palette: str = "cosmic",
    target_dir: Optional[Path] = None,
) -> Path:
    """
    Retrieves or generates a high-resolution transparent RGBA PNG asset
    for the specified gradient orb palette.
    """
    import subprocess

    palette_key = palette.lower().strip() if palette else "cosmic"
    if palette_key not in ORB_PALETTES:
        palette_key = "cosmic"

    dest_dir = target_dir or (Path(__file__).resolve().parent.parent / "assets" / "orbs")
    dest_dir.mkdir(parents=True, exist_ok=True)

    png_path = dest_dir / f"orb_{palette_key}.png"
    svg_path = dest_dir / f"orb_{palette_key}.svg"

    if png_path.exists() and png_path.stat().st_size > 1000:
        return png_path

    # Generate vector SVG
    generate_gradient_orb_svg(palette_key=palette_key, canvas_size=800, save_path=svg_path)

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
) -> Path:
    """
    Renders an ultra-fast (2-4 seconds) video preview of the animated gradient orb.
    Avoids running the entire generation pipeline (no script generation, no TTS, no stock downloads).
    Produces a ready-to-view vertical MP4 in seconds.
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

    # Initialize manager
    mgr = GradientOrbManager(
        palette=palette,
        position=position,
        size=size,
        opacity=opacity,
        animation=animation,
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
        f"[v_orb]drawtext=text='ORB TESTER \\: {palette.upper()} ({animation.upper()})':fontcolor=white:fontsize=38:box=1:boxcolor=black@0.65:boxborderw=12:x=(w-text_w)/2:y=180[vout]"
    ]
    filter_str = ";".join(filter_complex)

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c={bg_color}:s={width}x{height}:r=30:d={duration}",
        "-loop", "1", "-i", str(orb_asset),
        "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
        "-filter_complex", filter_str,
        "-map", "[vout]",
        "-map", "2:a",
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
            "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo",
            "-filter_complex", fallback_filter,
            "-map", "[vout]",
            "-map", "2:a",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            "-movflags", "+faststart",
            str(output_path)
        ]
        subprocess.run(cmd_fallback, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(f"\n✨ ¡Vista previa del Orbe generada en tiempo récord!")
    print(f"🎬 Video listo para ver: {output_path.resolve()}")
    print(f"📦 Tamaño: {output_path.stat().st_size / 1024:.1f} KB\n")
    return output_path

