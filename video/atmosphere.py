"""
Global Ambient Foreground Atmosphere Generator.
Generates an ultra-lightweight, seamless looping transparent MOV (QuickTime qtrle / yuva420p)
containing floating, out-of-focus cosmic dust, slow celestial embers, and subtle lens motes
that drift across the entire screen IN FRONT of the orbs to submerge them into a single living universe.
"""

import math
import subprocess
from pathlib import Path
from typing import Optional, Tuple


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


def generate_global_foreground_atmosphere_loop(
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
    loop_frames: int = 60,
    color_a: str = "#00f0ff",
    color_b: str = "#ffea00",
    target_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> Path:
    """
    Renders a 2-second (60 frames @ 30fps) seamless looping transparent MOV video
    containing global foreground floating sparks and out-of-focus lens bokeh discs.
    Placed as a top layer in front of the orbs, creating a profound sense of atmosphere.
    """
    dest_dir = target_dir or (Path(__file__).resolve().parent.parent / "assets" / "atmosphere")
    dest_dir.mkdir(parents=True, exist_ok=True)

    slug_a = color_a.replace("#", "").lower()[:6]
    slug_b = color_b.replace("#", "").lower()[:6]
    mov_path = dest_dir / f"foreground_atmosphere_{width}x{height}_{slug_a}_{slug_b}.mov"

    if not force_refresh and mov_path.exists() and mov_path.stat().st_size > 10000:
        return mov_path

    print(f"  🌌 Generando atmósfera cósmica frontal global ({color_a} & {color_b} | {width}x{height})...")

    # Render optimized frame resolution, scaled up by ffmpeg
    render_w = min(width, 540)
    render_h = min(height, 960)
    frames_dir = dest_dir / f"_temp_atmos_{render_w}x{render_h}_{slug_a}_{slug_b}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    rgb_a = _hex_to_rgb(color_a)
    rgb_b = _hex_to_rgb(color_b)

    # 54 calibrated ambient particles distributed with multi-prime chaotic dispersion
    num_particles = 54
    particles = []
    for idx in range(num_particles):
        # Deterministic multi-prime chaotic seed distribution (eliminates any collinear alignments)
        seed_x = ((idx * 0.6180339887 + 0.137) * 1.41421356) % 1.0
        seed_y = ((idx * 0.3819660113 + 0.293) * 1.73205080) % 1.0
        seed_z = ((idx * 2.7182818284 + 0.511) % 1.0)  # 0.0 (near orbs) to 1.0 (near camera lens)

        base_x = seed_x * render_w
        base_y = seed_y * render_h

        # Multi-harmonic organic drift (seamless periodic looping with variable frequencies and phase shifts)
        freq_x = 1 if (idx % 3 == 0) else (2 if (idx % 3 == 1) else 1)
        freq_y = 1 if (idx % 2 == 0) else 2
        amp_x = 22.0 + ((idx * 13) % 38)
        amp_y = 28.0 + ((idx * 17) % 48)
        phase_x = (idx * 2.39996) % (2 * math.pi)
        phase_y = (idx * 1.61803) % (2 * math.pi)

        # Particle type:
        # If seed_z > 0.78: Large, highly-translucent cinematic lens bokeh disk (soft blur)
        # If seed_z <= 0.78: Fine crystalline ember sparkle
        is_lens_bokeh = (seed_z > 0.76)
        if is_lens_bokeh:
            size = 11.0 + ((idx * 3.7) % 14.0)
            opacity = 0.06 + ((idx * 0.02) % 0.08)  # Ultra-subtle, airy and organic
        else:
            size = 1.1 + ((idx * 0.7) % 2.1)
            opacity = 0.20 + ((idx * 0.06) % 0.35)

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
            "is_lens_bokeh": is_lens_bokeh,
            "seed_z": seed_z,
        })

    try:
        for f in range(loop_frames):
            progress = f / loop_frames
            tau = 2 * math.pi * progress

            svg_parts = [
                f'<svg width="{render_w}" height="{render_h}" viewBox="0 0 {render_w} {render_h}" xmlns="http://www.w3.org/2000/svg">',
                '  <defs>',
                '    <filter id="lensBokehBlur" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="10.0" /></filter>',
                '    <filter id="emberGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.0" /></filter>',
                '  </defs>',
            ]

            for p in particles:
                # Calculate seamless periodic drift
                dx = p["amp_x"] * math.sin(tau * p["freq_x"] + p["phase_x"])
                dy = -p["amp_y"] * math.sin(tau * p["freq_y"] + p["phase_y"]) # upward floating drift

                px = (p["base_x"] + dx) % render_w
                py = (p["base_y"] + dy) % render_h

                # Dynamic color blending based on screen X position (inherits Left/Right host palette)
                x_ratio = max(0.0, min(1.0, px / max(1.0, render_w)))
                p_rgb = _lerp_rgb(rgb_a, rgb_b, x_ratio)
                p_hex = _rgb_to_hex(p_rgb)

                if p["is_lens_bokeh"]:
                    # Out of focus foreground disc
                    svg_parts.append(
                        f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{p["size"]:.1f}" fill="{p_hex}" opacity="{p["opacity"]:.2f}" filter="url(#lensBokehBlur)" />'
                    )
                else:
                    # Fine sharp luminous cosmic ember
                    svg_parts.append(
                        f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{p["size"]*2.0:.1f}" fill="{p_hex}" opacity="{p["opacity"]*0.4:.2f}" filter="url(#emberGlow)" />'
                    )
                    svg_parts.append(
                        f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{p["size"]:.1f}" fill="#ffffff" opacity="{p["opacity"]:.2f}" />'
                    )

            svg_parts.append('</svg>')

            frame_svg = "\n".join(svg_parts)
            frame_path = frames_dir / f"frame_{f:04d}.svg"
            frame_path.write_text(frame_svg, encoding="utf-8")

        # Encode transparent MOV loop
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%04d.svg"),
            "-vf", f"scale={width}:{height}:flags=bicubic,format=yuva420p",
            "-c:v", "qtrle",
            str(mov_path)
        ]
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"  ✅ Atmósfera cósmica frontal generada: {mov_path.name}")
        return mov_path

    except Exception as e:
        print(f"  ⚠️ Error generando atmósfera cósmica frontal: {e}")
        return mov_path
    finally:
        if frames_dir.exists():
            import shutil
            shutil.rmtree(frames_dir, ignore_errors=True)
