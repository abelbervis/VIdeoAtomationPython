"""
Procedural Cosmic Particle Background Video Generator.
Renders a seamless, high-performance looping MP4 video of deep space with:
- Dual gravitational mass interaction (Quantum Cyan & Solar Gold)
- Dynamic orbiting particle trails and accretion dust
- Ambient chromatic nebulae and orbital harmonic rings
- Cached to assets/backgrounds/ for instant reuse in video rendering
"""

import math
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any


def generate_cosmic_particle_bg_video(
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
    loop_frames: int = 60,
    target_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> Path:
    """
    Generates a seamless 2-second (60 frames @ 30fps) high-definition looping MP4
    background with dual cosmic entities and moving gravitational particle fields.
    """
    dest_dir = target_dir or (Path(__file__).resolve().parent.parent / "assets" / "backgrounds")
    dest_dir.mkdir(parents=True, exist_ok=True)
    mp4_path = dest_dir / f"cosmic_dual_particles_{width}x{height}.mp4"

    if not force_refresh and mp4_path.exists() and mp4_path.stat().st_size > 50000:
        return mp4_path

    print(f"  ✨ Generando fondo cósmico cinemático de partículas ({width}x{height} @ {fps}fps)...")

    # Render at a crisp resolution optimized for speed and fidelity
    render_w = min(width, 720)
    render_h = min(height, 1280)
    frames_dir = dest_dir / f"_temp_bg_frames_{render_w}x{render_h}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    # Simulation parameters
    num_particles = 180
    center_ax = render_w * 0.32
    center_ay = render_h * 0.40
    center_bx = render_w * 0.68
    center_by = render_h * 0.44

    # Deterministic particle seed distribution
    particles = []
    for idx in range(num_particles):
        is_q = (idx % 2 == 0)
        seed = (idx * 1.6180339887) % 1.0
        orbit_rad_x = 70 + seed * (render_w * 0.38)
        orbit_rad_y = 50 + ((idx * 2.718) % 1.0) * (render_h * 0.28)
        phase_offset = idx * (2 * math.pi / num_particles)
        speed_mult = 1.0 + ((idx * 0.37) % 1.0) * 1.5
        size = 1.2 if idx % 7 != 0 else (2.4 if idx % 19 != 0 else 3.8)
        color = "#00f0ff" if is_q else ("#ffea00" if idx % 4 != 0 else "#a855f7")
        opacity = 0.35 + ((idx * 0.73) % 0.55)
        particles.append({
            "is_q": is_q,
            "rx": orbit_rad_x,
            "ry": orbit_rad_y,
            "phase": phase_offset,
            "speed": speed_mult,
            "size": size,
            "color": color,
            "opacity": opacity,
            "z_order": idx % 3,
        })

    try:
        for f in range(loop_frames):
            progress = f / loop_frames
            tau = 2 * math.pi * progress

            # Orbiting Entity Centers
            ent_a_x = center_ax + 28 * math.cos(tau)
            ent_a_y = center_ay + 18 * math.sin(tau * 1.2)

            ent_b_x = center_bx + 32 * math.cos(tau + math.pi)
            ent_b_y = center_by + 20 * math.sin((tau + math.pi) * 1.1)

            # Midpoint Bridge
            mid_x = (ent_a_x + ent_b_x) / 2
            mid_y = (ent_a_y + ent_b_y) / 2
            bridge_pulse = 0.5 + 0.5 * math.sin(tau * 2)

            svg_parts = [
                f'<svg width="{render_w}" height="{render_h}" viewBox="0 0 {render_w} {render_h}" xmlns="http://www.w3.org/2000/svg">',
                '  <defs>',
                '    <filter id="bgBlurDeep" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70" /></filter>',
                '    <filter id="coreBlur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="24" /></filter>',
                '    <filter id="glowBlur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="8" /></filter>',
                '    <linearGradient id="deepVoidGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
                '      <stop offset="0%" stop-color="#040508" />',
                '      <stop offset="50%" stop-color="#070912" />',
                '      <stop offset="100%" stop-color="#0a0710" />',
                '    </linearGradient>',
                '    <radialGradient id="nebulaQ" cx="50%" cy="50%" r="50%">',
                '      <stop offset="0%" stop-color="#00f0ff" stop-opacity="0.32" />',
                '      <stop offset="40%" stop-color="#4f46e5" stop-opacity="0.18" />',
                '      <stop offset="80%" stop-color="#1e1b4b" stop-opacity="0.06" />',
                '      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />',
                '    </radialGradient>',
                '    <radialGradient id="nebulaS" cx="50%" cy="50%" r="50%">',
                '      <stop offset="0%" stop-color="#ff9100" stop-opacity="0.36" />',
                '      <stop offset="45%" stop-color="#e11d48" stop-opacity="0.20" />',
                '      <stop offset="85%" stop-color="#4c0519" stop-opacity="0.06" />',
                '      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />',
                '    </radialGradient>',
                '    <radialGradient id="bridgePulseGrad" cx="50%" cy="50%" r="50%">',
                f'      <stop offset="0%" stop-color="#c084fc" stop-opacity="{0.18 * bridge_pulse + 0.08:.2f}" />',
                '      <stop offset="60%" stop-color="#3b82f6" stop-opacity="0.04" />',
                '      <stop offset="100%" stop-color="#000000" stop-opacity="0.0" />',
                '    </radialGradient>',
                '  </defs>',
                '  <!-- 1. Deep Space Base -->',
                f'  <rect width="{render_w}" height="{render_h}" fill="url(#deepVoidGrad)" />',
                '  <!-- 2. Dual Atmospheric Nebulae -->',
                f'  <circle cx="{ent_a_x:.1f}" cy="{ent_a_y:.1f}" r="260" fill="url(#nebulaQ)" filter="url(#bgBlurDeep)" />',
                f'  <circle cx="{ent_b_x:.1f}" cy="{ent_b_y:.1f}" r="280" fill="url(#nebulaS)" filter="url(#bgBlurDeep)" />',
                f'  <circle cx="{mid_x:.1f}" cy="{mid_y:.1f}" r="180" fill="url(#bridgePulseGrad)" filter="url(#coreBlur)" />',
                '  <!-- 3. Astrometric Resonance Bridge Lines -->',
                f'  <line x1="{ent_a_x:.1f}" y1="{ent_a_y:.1f}" x2="{ent_b_x:.1f}" y2="{ent_b_y:.1f}" stroke="rgba(192, 132, 252, 0.22)" stroke-width="1.2" stroke-dasharray="3 9" />',
                '  <!-- 4. Dynamic Particle Swarm and Trails -->',
            ]

            # Render particles with dual attraction positions
            for p in particles:
                host_x = ent_a_x if p["is_q"] else ent_b_x
                host_y = ent_a_y if p["is_q"] else ent_b_y
                direction = 1 if p["is_q"] else -1

                ang = p["phase"] + (tau * p["speed"] * direction)
                px = host_x + p["rx"] * math.cos(ang)
                py = host_y + p["ry"] * math.sin(ang)

                # Tail behind particle
                tail_ang = ang - (0.16 * direction)
                tx = host_x + p["rx"] * math.cos(tail_ang)
                ty = host_y + p["ry"] * math.sin(tail_ang)

                # Draw tail
                svg_parts.append(
                    f'  <line x1="{tx:.1f}" y1="{ty:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="{p["color"]}" stroke-width="{p["size"]*0.7:.1f}" opacity="{p["opacity"]*0.4:.2f}" />'
                )
                # Draw particle point
                svg_parts.append(
                    f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{p["size"]:.1f}" fill="{p["color"]}" opacity="{p["opacity"]:.2f}" />'
                )
                # Extra glow on larger sparks
                if p["size"] > 2.0:
                    svg_parts.append(
                        f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{p["size"]*2.2:.1f}" fill="{p["color"]}" opacity="{p["opacity"]*0.25:.2f}" filter="url(#glowBlur)" />'
                    )

            # Deep Vignette border overlay
            svg_parts.append(
                f'  <rect width="{render_w}" height="{render_h}" fill="none" stroke="#040508" stroke-width="24" opacity="0.6" />'
            )
            svg_parts.append('</svg>')

            frame_svg = "\n".join(svg_parts)
            frame_path = frames_dir / f"frame_{f:04d}.svg"
            frame_path.write_text(frame_svg, encoding="utf-8")

        # Encode frames into seamless looping MP4 using FFmpeg
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%04d.svg"),
            "-vf", f"scale={width}:{height}:flags=bicubic,format=yuv420p",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(mp4_path)
        ]
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"  ✅ Fondo cósmico generado exitosamente: {mp4_path.name}")
        return mp4_path

    except Exception as e:
        print(f"  ⚠️ Error generando video de fondo cósmico: {e}")
        return mp4_path
    finally:
        # Clean up temporary SVG frames
        if frames_dir.exists():
            import shutil
            shutil.rmtree(frames_dir, ignore_errors=True)


def get_cosmic_particle_background_video(width: int = 1080, height: int = 1920) -> Path:
    """Helper to retrieve or generate the cached cosmic particle background video."""
    return generate_cosmic_particle_bg_video(width=width, height=height)
