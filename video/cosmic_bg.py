"""
Procedural Cosmic Particle Background & Foreground Overlay Generator.
Renders seamless looping MP4/MOV videos with:
- Dual or Focused Mode (Wide shot vs Close-up shot with dense corona of the active orb)
- Dynamic Color Palette inheritance from any character or custom hex colors
- Real-time color interpolation (lerp) across gravitational fields
- Dedicated Transparent Foreground Particle Overlay Pass (MOV with alpha) to pass in front of orbs
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
    focus_mode: str = "dual",  # "dual", "host_a", "host_b"
    target_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> Path:
    """
    Generates a seamless 2-second (60 frames @ 30fps) high-definition looping MP4
    background with dual or focused entity gravitation, dense corona, and dynamic colors.
    """
    dest_dir = target_dir or (Path(__file__).resolve().parent.parent / "assets" / "backgrounds")
    dest_dir.mkdir(parents=True, exist_ok=True)

    slug_a = color_a.replace("#", "").lower()[:6]
    slug_b = color_b.replace("#", "").lower()[:6]
    mp4_path = dest_dir / f"cosmic_bg_{width}x{height}_{focus_mode}_{slug_a}_{slug_b}.mp4"

    if not force_refresh and mp4_path.exists() and mp4_path.stat().st_size > 50000:
        return mp4_path

    print(f"  ✨ Generando fondo cósmico [{focus_mode.upper()}] ({color_a} & {color_b} | {width}x{height} @ {fps}fps)...")

    render_w = min(width, 720)
    render_h = min(height, 1280)
    frames_dir = dest_dir / f"_temp_bg_{render_w}x{render_h}_{focus_mode}_{slug_a}_{slug_b}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    rgb_a = _hex_to_rgb(color_a)
    rgb_a_glow = _hex_to_rgb(color_a_glow)
    rgb_b = _hex_to_rgb(color_b)
    rgb_b_glow = _hex_to_rgb(color_b_glow)

    # Simulation parameters depending on focus mode
    num_particles = 240 if focus_mode != "dual" else 200

    if focus_mode == "host_a":
        center_ax, center_ay = render_w * 0.50, render_h * 0.44
        center_bx, center_by = render_w * 0.88, render_h * 0.70
        weight_a = 0.88
    elif focus_mode == "host_b":
        center_ax, center_ay = render_w * 0.12, render_h * 0.70
        center_bx, center_by = render_w * 0.50, render_h * 0.44
        weight_a = 0.12
    else:
        center_ax, center_ay = render_w * 0.33, render_h * 0.42
        center_bx, center_by = render_w * 0.67, render_h * 0.46
        weight_a = 0.50

    particles = []
    for idx in range(num_particles):
        is_a = (idx / num_particles) < weight_a
        seed = (idx * 1.6180339887) % 1.0

        if focus_mode != "dual" and ((is_a and focus_mode == "host_a") or (not is_a and focus_mode == "host_b")):
            # Concentrated accretion corona around focused host
            orbit_rad_x = 35 + seed * (render_w * 0.32)
            orbit_rad_y = 25 + ((idx * 2.718) % 1.0) * (render_h * 0.24)
            speed_mult = 0.6 + ((idx * 0.45) % 1.0) * 1.1
        else:
            orbit_rad_x = 65 + seed * (render_w * 0.42)
            orbit_rad_y = 48 + ((idx * 2.718) % 1.0) * (render_h * 0.32)
            speed_mult = 0.45 + ((idx * 0.37) % 1.0) * 0.7

        phase_offset = idx * (2 * math.pi / num_particles)
        z_depth = ((idx * 3.1415) % 2.0) - 1.0
        base_size = 1.3 + (z_depth + 1.0) * 0.8
        if z_depth > 0.4 and idx % 7 == 0:
            base_size = 4.2 + ((idx * 0.6) % 2.5)

        opacity = 0.4 + ((idx * 0.73) % 0.55)
        particles.append({
            "is_a": is_a,
            "rx": orbit_rad_x,
            "ry": orbit_rad_y,
            "phase": phase_offset,
            "speed": speed_mult,
            "size": base_size,
            "z": z_depth,
            "opacity": opacity,
        })

    try:
        for f in range(loop_frames):
            progress = f / loop_frames
            tau = 2 * math.pi * progress

            if focus_mode == "host_a":
                ent_a_x = center_ax + 12 * math.cos(tau)
                ent_a_y = center_ay + 8 * math.sin(tau * 1.2)
                ent_b_x = center_bx + 18 * math.cos(tau + math.pi)
                ent_b_y = center_by + 14 * math.sin((tau + math.pi))
            elif focus_mode == "host_b":
                ent_a_x = center_ax + 18 * math.cos(tau)
                ent_a_y = center_ay + 14 * math.sin(tau)
                ent_b_x = center_bx + 12 * math.cos(tau + math.pi)
                ent_b_y = center_by + 8 * math.sin((tau + math.pi) * 1.2)
            else:
                ent_a_x = center_ax + 24 * math.cos(tau)
                ent_a_y = center_ay + 16 * math.sin(tau * 1.2)
                ent_b_x = center_bx + 26 * math.cos(tau + math.pi)
                ent_b_y = center_by + 18 * math.sin((tau + math.pi) * 1.1)

            mid_x = (ent_a_x + ent_b_x) / 2
            mid_y = (ent_a_y + ent_b_y) / 2
            bridge_pulse = 0.5 + 0.5 * math.sin(tau * 2)

            mid_color_rgb = _lerp_rgb(rgb_a, rgb_b, 0.5)
            mid_hex = _rgb_to_hex(mid_color_rgb)

            # Dominant aura radius
            rad_neb_a = 360 if focus_mode == "host_a" else (180 if focus_mode == "host_b" else 270)
            rad_neb_b = 360 if focus_mode == "host_b" else (180 if focus_mode == "host_a" else 290)

            # Pre-calculate nebula opacities for clean f-strings
            op_a_0 = "0.38" if focus_mode == "host_a" else "0.28"
            op_a_45 = "0.22" if focus_mode == "host_a" else "0.15"
            op_b_0 = "0.38" if focus_mode == "host_b" else "0.28"
            op_b_45 = "0.22" if focus_mode == "host_b" else "0.15"

            svg_parts = [
                f'<svg width="{render_w}" height="{render_h}" viewBox="0 0 {render_w} {render_h}" xmlns="http://www.w3.org/2000/svg">',
                '  <defs>',
                '    <filter id="bgBlurDeep" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="65" /></filter>',
                '    <filter id="coreBlur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="22" /></filter>',
                '    <filter id="glowBlur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="8" /></filter>',
                '    <linearGradient id="deepVoidGrad" x1="0%" y1="0%" x2="100%" y2="100%">',
                '      <stop offset="0%" stop-color="#040508" />',
                '      <stop offset="50%" stop-color="#070810" />',
                '      <stop offset="100%" stop-color="#09060d" />',
                '    </linearGradient>',
                '    <radialGradient id="nebulaA" cx="50%" cy="50%" r="50%">',
                f'      <stop offset="0%" stop-color="{color_a}" stop-opacity="{op_a_0}" />',
                f'      <stop offset="45%" stop-color="{color_a_glow}" stop-opacity="{op_a_45}" />',
                '      <stop offset="85%" stop-color="#000000" stop-opacity="0.0" />',
                '    </radialGradient>',
                '    <radialGradient id="nebulaB" cx="50%" cy="50%" r="50%">',
                f'      <stop offset="0%" stop-color="{color_b}" stop-opacity="{op_b_0}" />',
                f'      <stop offset="45%" stop-color="{color_b_glow}" stop-opacity="{op_b_45}" />',
                '      <stop offset="85%" stop-color="#000000" stop-opacity="0.0" />',
                '    </radialGradient>',
                '    <radialGradient id="bridgePulseGrad" cx="50%" cy="50%" r="50%">',
                f'      <stop offset="0%" stop-color="{mid_hex}" stop-opacity="{0.18 * bridge_pulse + 0.06:.2f}" />',
                '      <stop offset="70%" stop-color="#000000" stop-opacity="0.0" />',
                '    </radialGradient>',
                '  </defs>',
                '  <!-- 1. Deep Space Base -->',
                f'  <rect width="{render_w}" height="{render_h}" fill="url(#deepVoidGrad)" />',
                '  <!-- 2. Dual/Focused Atmospheric Nebulae -->',
                f'  <circle cx="{ent_a_x:.1f}" cy="{ent_a_y:.1f}" r="{rad_neb_a}" fill="url(#nebulaA)" filter="url(#bgBlurDeep)" />',
                f'  <circle cx="{ent_b_x:.1f}" cy="{ent_b_y:.1f}" r="{rad_neb_b}" fill="url(#nebulaB)" filter="url(#bgBlurDeep)" />',
                f'  <circle cx="{mid_x:.1f}" cy="{mid_y:.1f}" r="170" fill="url(#bridgePulseGrad)" filter="url(#coreBlur)" />',
                '  <!-- 3. Astrometric Resonance Bridge Lines -->',
                f'  <line x1="{ent_a_x:.1f}" y1="{ent_a_y:.1f}" x2="{ent_b_x:.1f}" y2="{ent_b_y:.1f}" stroke="{mid_hex}" stroke-opacity="0.22" stroke-width="1.2" stroke-dasharray="3 9" />',
            ]

            # Particles processing
            for p in particles:
                host_x = ent_a_x if p["is_a"] else ent_b_x
                host_y = ent_a_y if p["is_a"] else ent_b_y
                direction = 1 if p["is_a"] else -1

                ang = p["phase"] + (tau * p["speed"] * direction)
                px = host_x + p["rx"] * math.cos(ang)
                py = host_y + p["ry"] * math.sin(ang)

                dA = math.hypot(px - ent_a_x, py - ent_a_y)
                dB = math.hypot(px - ent_b_x, py - ent_b_y)
                ratio = max(0.0, min(1.0, dA / (dA + dB + 0.001)))
                p_color_rgb = _lerp_rgb(rgb_a, rgb_b, ratio)
                p_hex = _rgb_to_hex(p_color_rgb)

                tail_ang = ang - (0.15 * direction)
                tx = host_x + p["rx"] * math.cos(tail_ang)
                ty = host_y + p["ry"] * math.sin(tail_ang)

                # Draw Particle & Tail
                svg_parts.append(
                    f'  <line x1="{tx:.1f}" y1="{ty:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="{p_hex}" stroke-width="{p["size"]*0.75:.1f}" opacity="{p["opacity"]*0.4:.2f}" />'
                )
                svg_parts.append(
                    f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{p["size"]:.1f}" fill="{p_hex}" opacity="{p["opacity"]:.2f}" />'
                )
                if p["size"] > 2.5:
                    svg_parts.append(
                        f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{p["size"]*2.4:.1f}" fill="{p_hex}" opacity="{p["opacity"]*0.3:.2f}" filter="url(#glowBlur)" />'
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
            "-vf", f"scale={width}:{height}:flags=bicubic,format=yuv420p",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(mp4_path)
        ]
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"  ✅ Fondo cósmico [{focus_mode}] generado: {mp4_path.name}")
        return mp4_path

    except Exception as e:
        print(f"  ⚠️ Error generando video de fondo cósmico: {e}")
        return mp4_path
    finally:
        if frames_dir.exists():
            import shutil
            shutil.rmtree(frames_dir, ignore_errors=True)


def generate_cosmic_foreground_particles_overlay(
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
    Renders a transparent QuickTime MOV (PNG/Alpha or QTRLE) foreground particle pass.
    These particles explicitly pass in front of the orb entities with prominent specular glow and bokeh.
    """
    dest_dir = target_dir or (Path(__file__).resolve().parent.parent / "assets" / "backgrounds")
    dest_dir.mkdir(parents=True, exist_ok=True)

    slug_a = color_a.replace("#", "").lower()[:6]
    slug_b = color_b.replace("#", "").lower()[:6]
    mov_path = dest_dir / f"cosmic_fg_sparks_{width}x{height}_{slug_a}_{slug_b}.mov"

    if not force_refresh and mov_path.exists() and mov_path.stat().st_size > 50000:
        return mov_path

    print(f"  ✨ Generando capa frontal transparente de partículas ({width}x{height} @ {fps}fps)...")

    render_w = min(width, 720)
    render_h = min(height, 1280)
    frames_dir = dest_dir / f"_temp_fg_{render_w}x{render_h}_{slug_a}_{slug_b}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    rgb_a = _hex_to_rgb(color_a)
    rgb_b = _hex_to_rgb(color_b)

    # 45 prominent foreground crossing sparks
    num_sparks = 45
    sparks = []
    for idx in range(num_sparks):
        seed = (idx * 1.618) % 1.0
        is_a = (idx % 2 == 0)
        center_x = (render_w * 0.35) if is_a else (render_w * 0.65)
        center_y = (render_h * 0.44) if is_a else (render_h * 0.48)
        radius = 70 + seed * (render_w * 0.45)
        phase = idx * (2 * math.pi / num_sparks)
        speed = 0.5 + ((idx * 0.42) % 1.0) * 0.8
        size = 3.5 + ((idx * 0.77) % 3.8) # Large 3.5px - 7.3px foreground bokeh
        sparks.append({
            "is_a": is_a,
            "cx": center_x,
            "cy": center_y,
            "r": radius,
            "phase": phase,
            "speed": speed,
            "size": size,
            "opacity": 0.65 + ((idx * 0.5) % 0.35),
        })

    try:
        for f in range(loop_frames):
            progress = f / loop_frames
            tau = 2 * math.pi * progress

            svg_parts = [
                f'<svg width="{render_w}" height="{render_h}" viewBox="0 0 {render_w} {render_h}" xmlns="http://www.w3.org/2000/svg">',
                '  <defs>',
                '    <filter id="fgGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="10" /></filter>',
                '    <filter id="bokehSoft" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="20" /></filter>',
                '  </defs>',
            ]

            for s in sparks:
                direction = 1 if s["is_a"] else -1
                ang = s["phase"] + (tau * s["speed"] * direction)
                
                # 3D inclination tilt so particles cross diagonally across the orb face
                px = s["cx"] + s["r"] * math.cos(ang)
                py = s["cy"] + s["r"] * math.sin(ang) * 0.75 + math.cos(ang * 0.8) * 35

                # Trail
                tang = ang - (0.18 * direction)
                tx = s["cx"] + s["r"] * math.cos(tang)
                ty = s["cy"] + s["r"] * math.sin(tang) * 0.75 + math.cos(tang * 0.8) * 35

                color_rgb = rgb_a if s["is_a"] else rgb_b
                col_hex = _rgb_to_hex(color_rgb)

                # 1. Trail
                svg_parts.append(
                    f'  <line x1="{tx:.1f}" y1="{ty:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="{col_hex}" stroke-width="{s["size"]*1.1:.1f}" opacity="{s["opacity"]*0.6:.2f}" />'
                )
                # 2. Large Outer Bokeh Glow
                svg_parts.append(
                    f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{s["size"]*3.6:.1f}" fill="{col_hex}" opacity="{s["opacity"]*0.45:.2f}" filter="url(#bokehSoft)" />'
                )
                # 3. Chromatic Glow Ring
                svg_parts.append(
                    f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{s["size"]*1.8:.1f}" fill="{col_hex}" opacity="{s["opacity"]*0.85:.2f}" filter="url(#fgGlow)" />'
                )
                # 4. White-Hot Incandescent Specular Spark Core
                svg_parts.append(
                    f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{s["size"]*0.75:.1f}" fill="#FFFFFF" opacity="0.98" />'
                )

            svg_parts.append('</svg>')
            frame_svg = "\n".join(svg_parts)
            frame_path = frames_dir / f"fg_{f:04d}.svg"
            frame_path.write_text(frame_svg, encoding="utf-8")

        # Encode as transparent video with alpha channel (PNG video codec in QuickTime container)
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "fg_%04d.svg"),
            "-vf", f"scale={width}:{height}:flags=bicubic,format=yuva420p",
            "-c:v", "png",
            "-pix_fmt", "yuva420p",
            str(mov_path)
        ]
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"  ✅ Capa frontal transparente generada: {mov_path.name}")
        return mov_path

    except Exception as e:
        print(f"  ⚠️ Error generando capa frontal: {e}")
        return mov_path
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
    focus_mode: str = "dual",
) -> Path:
    """Helper to retrieve or generate the cached cosmic particle background video."""
    return generate_cosmic_particle_bg_video(
        width=width,
        height=height,
        color_a=color_a,
        color_a_glow=color_a_glow,
        color_b=color_b,
        color_b_glow=color_b_glow,
        focus_mode=focus_mode,
    )


def get_cosmic_foreground_overlay(
    width: int = 1080,
    height: int = 1920,
    color_a: str = "#00f0ff",
    color_b: str = "#ffea00",
) -> Path:
    """Helper to retrieve or generate the cached transparent foreground particle video overlay."""
    return generate_cosmic_foreground_particles_overlay(
        width=width,
        height=height,
        color_a=color_a,
        color_b=color_b,
    )
