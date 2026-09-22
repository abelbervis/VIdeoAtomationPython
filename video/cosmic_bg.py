"""
Procedural Cosmic Particle Background Video Generator.
Renders a seamless, high-performance looping MP4 video of deep space with:
- Dynamic Color Palette inheritance from any cosmic character or custom hex colors
- Real-time color interpolation (lerp) across gravitational fields
- 3D depth layers with foreground bokeh sparks crossing in front of entities
- Ambient fluid nebulae and orbital harmonic resonance lines
"""

import math
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple


def _hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    clean = hex_str.strip().lstrip("#")
    if len(clean) == 3:
        clean = "".join(c + c for c in clean)
    try:
        val = int(clean, 16)
        return ((val >> 16) & 255, (val >> 8) & 255, val & 255)
    except Exception:
        return (0, 240, 255)


def _lerp_rgb(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    clamped = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * clamped),
        int(c1[1] + (c2[1] - c1[1]) * clamped),
        int(c1[2] + (c2[2] - c1[2]) * clamped),
    )


def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def generate_cosmic_particle_bg_video(
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
    loop_frames: int = 60,
    color_a: str = "#00f0ff",
    color_a_glow: str = "#0284c7",
    color_b: str = "#ffea00",
    color_b_glow: str = "#ff5500",
    target_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> Path:
    """
    Generates a seamless 2-second (60 frames @ 30fps) high-definition looping MP4
    background with dual cosmic entities, dynamic palette inheritance, and 3D depth.
    """
    dest_dir = target_dir or (Path(__file__).resolve().parent.parent / "assets" / "backgrounds")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    slug_a = color_a.replace("#", "").lower()[:6]
    slug_b = color_b.replace("#", "").lower()[:6]
    mp4_path = dest_dir / f"cosmic_bg_{width}x{height}_{slug_a}_{slug_b}.mp4"

    if not force_refresh and mp4_path.exists() and mp4_path.stat().st_size > 50000:
        return mp4_path

    print(f"  ✨ Generando fondo cósmico dinámico ({color_a} & {color_b} | {width}x{height} @ {fps}fps)...")

    # Render at a crisp resolution optimized for speed and fidelity
    render_w = min(width, 720)
    render_h = min(height, 1280)
    frames_dir = dest_dir / f"_temp_bg_{render_w}x{render_h}_{slug_a}_{slug_b}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    rgb_a = _hex_to_rgb(color_a)
    rgb_a_glow = _hex_to_rgb(color_a_glow)
    rgb_b = _hex_to_rgb(color_b)
    rgb_b_glow = _hex_to_rgb(color_b_glow)

    # Simulation parameters - Elegant cinematic celestial field
    num_particles = 68
    particles = []
    for idx in range(num_particles):
        # Deterministic multi-prime chaotic seed distribution
        seed_x = ((idx * 0.6180339887 + 0.173) * 1.41421356) % 1.0
        seed_y = ((idx * 0.3819660113 + 0.317) * 1.73205080) % 1.0
        seed_z = ((idx * 2.7182818284 + 0.643) % 1.0)

        base_x = seed_x * render_w
        base_y = seed_y * render_h

        # Harmonious organic floating drift
        freq_x = 1 if (idx % 3 == 0) else (2 if (idx % 3 == 1) else 1)
        freq_y = 1 if (idx % 2 == 0) else 2
        amp_x = 18.0 + ((idx * 11) % 32)
        amp_y = 22.0 + ((idx * 15) % 40)
        phase_x = (idx * 2.39996) % (2 * math.pi)
        phase_y = (idx * 1.61803) % (2 * math.pi)

        # Particle aesthetic categorization:
        # If seed_z > 0.74: Soft luminous distant bokeh disc
        # If seed_z <= 0.74: Fine sharp crystalline ember sparkle
        is_bokeh = (seed_z > 0.74)
        if is_bokeh:
            size = 9.0 + ((idx * 3.1) % 12.0)
            opacity = 0.08 + ((idx * 0.02) % 0.10)
        else:
            size = 1.2 + ((idx * 0.6) % 1.9)
            opacity = 0.35 + ((idx * 0.06) % 0.45)

        particles.append({
            "idx": idx,
            "base_x": base_x,
            "base_y": base_y,
            "amp_x": amp_x,
            "amp_y": amp_y,
            "freq_x": freq_x,
            "freq_y": freq_y,
            "phase_x": phase_x,
            "phase_y": phase_y,
            "size": size,
            "opacity": opacity,
            "is_bokeh": is_bokeh,
            "seed_z": seed_z,
        })

    try:
        for f in range(loop_frames):
            progress = f / loop_frames
            tau = 2 * math.pi * progress

            svg_parts = [
                f'<svg width="{render_w}" height="{render_h}" viewBox="0 0 {render_w} {render_h}" xmlns="http://www.w3.org/2000/svg">',
                '  <defs>',
                '    <filter id="bokehBlur" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="9.0" /></filter>',
                '    <filter id="emberGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.8" /></filter>',
                '    <linearGradient id="deepVoidGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
                '      <stop offset="0%" stop-color="#040508" />',
                '      <stop offset="50%" stop-color="#06070e" />',
                '      <stop offset="100%" stop-color="#08050c" />',
                '    </linearGradient>',
                '  </defs>',
                '  <!-- 1. Deep Space Void Base -->',
                f'  <rect width="{render_w}" height="{render_h}" fill="url(#deepVoidGrad)" />',
            ]

            # Render particles with harmonious spatial color gradation & depth
            for p in particles:
                # Organic seamless drift
                dx = p["amp_x"] * math.sin(tau * p["freq_x"] + p["phase_x"])
                dy = -p["amp_y"] * math.sin(tau * p["freq_y"] + p["phase_y"])

                px = (p["base_x"] + dx) % render_w
                py = (p["base_y"] + dy) % render_h

                # Dynamic color blending based on screen X position (Left Host -> Right Host)
                x_ratio = max(0.0, min(1.0, px / max(1.0, render_w)))
                p_rgb = _lerp_rgb(rgb_a, rgb_b, x_ratio)
                p_hex = _rgb_to_hex(p_rgb)

                if p["is_bokeh"]:
                    # Soft luminous celestial bokeh disc (no harsh edges)
                    svg_parts.append(
                        f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{p["size"]:.1f}" fill="{p_hex}" opacity="{p["opacity"]:.2f}" filter="url(#bokehBlur)" />'
                    )
                else:
                    # Elegant crystalline ember with glowing colored bloom and brilliant core
                    svg_parts.append(
                        f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{p["size"]*2.2:.1f}" fill="{p_hex}" opacity="{p["opacity"]*0.45:.2f}" filter="url(#emberGlow)" />'
                    )
                    svg_parts.append(
                        f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{p["size"]:.1f}" fill="#ffffff" opacity="{p["opacity"]:.2f}" />'
                    )

            # Deep Vignette border overlay
            svg_parts.append(
                f'  <rect width="{render_w}" height="{render_h}" fill="none" stroke="#040508" stroke-width="20" opacity="0.65" />'
            )
            svg_parts.append('</svg>')

            frame_svg = "\n".join(svg_parts)
            frame_path = frames_dir / f"frame_{f:04d}.svg"
            frame_path.write_text(frame_svg, encoding="utf-8")

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%04d.svg"),
            "-vf", f"scale={width}:{height}:flags=lanczos,format=yuv420p",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "16",
            "-color_primaries", "bt709",
            "-color_trc", "bt709",
            "-colorspace", "bt709",
            "-pix_fmt", "yuv420p",
            str(mp4_path)
        ]
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"  ✅ Fondo cósmico adaptado generado: {mp4_path.name}")
        return mp4_path

    except Exception as e:
        print(f"  ⚠️ Error generando video de fondo cósmico: {e}")
        return mp4_path
    finally:
        if frames_dir.exists():
            import shutil
            shutil.rmtree(frames_dir, ignore_errors=True)


def get_cosmic_particle_background_video(
    width: int = 1080,
    height: int = 1920,
    color_a: str = "#00f0ff",
    color_a_glow: str = "#0284c7",
    color_b: str = "#ffea00",
    color_b_glow: str = "#ff5500",
) -> Path:
    """Helper to retrieve or generate the cached cosmic particle background video with dynamic colors."""
    return generate_cosmic_particle_bg_video(
        width=width,
        height=height,
        color_a=color_a,
        color_a_glow=color_a_glow,
        color_b=color_b,
        color_b_glow=color_b_glow,
    )
