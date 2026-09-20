import React, { useEffect, useRef, useCallback } from 'react';

export interface EntityPalette {
  primary: string;
  glow: string;
  accent: string;
  name?: string;
}

export interface CosmicBackgroundProps {
  entity1?: EntityPalette;
  entity2?: EntityPalette;
  particleDensity?: 'low' | 'medium' | 'high';
  speedMultiplier?: number;
  gravityStrength?: number;
  showOrbits?: boolean;
  interactiveMouse?: boolean;
}

interface Particle {
  x: number;
  y: number;
  z: number; // -1.0 (deep background) to +1.0 (foreground crossing over cores)
  vx: number;
  vy: number;
  radius: number;
  baseRadius: number;
  alpha: number;
  baseAlpha: number;
  mass: number;
  trail: { x: number; y: number }[];
  life: number;
  maxLife: number;
  bias: number; // 0.0 = belongs to Entity 1, 1.0 = belongs to Entity 2
}

interface RGB {
  r: number;
  g: number;
  b: number;
}

function parseColorToRgb(hexOrRgb: string): RGB {
  if (hexOrRgb.startsWith('#')) {
    let hex = hexOrRgb.slice(1);
    if (hex.length === 3) {
      hex = hex.split('').map(c => c + c).join('');
    }
    const num = parseInt(hex, 16);
    return {
      r: (num >> 16) & 255,
      g: (num >> 8) & 255,
      b: num & 255,
    };
  }
  const match = hexOrRgb.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
  if (match) {
    return {
      r: parseInt(match[1], 10),
      g: parseInt(match[2], 10),
      b: parseInt(match[3], 10),
    };
  }
  return { r: 0, g: 240, b: 255 }; // default cyan fallback
}

function lerpRgb(c1: RGB, c2: RGB, t: number): RGB {
  const clamped = Math.max(0, Math.min(1, t));
  return {
    r: Math.round(c1.r + (c2.r - c1.r) * clamped),
    g: Math.round(c1.g + (c2.g - c1.g) * clamped),
    b: Math.round(c1.b + (c2.b - c1.b) * clamped),
  };
}

function rgbToString(rgb: RGB, alpha = 1.0): string {
  return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha.toFixed(3)})`;
}

// Preset defaults for seamless out-of-the-box experience
export const DEFAULT_ENTITY_A: EntityPalette = {
  name: 'Quantum Core',
  primary: '#00F0FF',
  glow: '#0284C7',
  accent: '#7000FF',
};

export const DEFAULT_ENTITY_B: EntityPalette = {
  name: 'Solar Forge',
  primary: '#FFAA00',
  glow: '#FF5500',
  accent: '#FF0055',
};

export const CosmicBackground: React.FC<CosmicBackgroundProps> = ({
  entity1 = DEFAULT_ENTITY_A,
  entity2 = DEFAULT_ENTITY_B,
  particleDensity = 'medium',
  speedMultiplier = 1.0,
  gravityStrength = 1.0,
  showOrbits = true,
  interactiveMouse = true,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mouseRef = useRef<{ x: number; y: number; active: boolean }>({ x: 0, y: 0, active: false });
  const animationFrameId = useRef<number | null>(null);

  const getParticleCount = useCallback(() => {
    switch (particleDensity) {
      case 'low':
        return 150;
      case 'high':
        return 380;
      case 'medium':
      default:
      return 240;
    }
  }, [particleDensity]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) return;

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    // Parse dynamic entity colors into RGB for instant fast per-frame lerping
    const entA_primary = parseColorToRgb(entity1.primary);
    const entA_glow = parseColorToRgb(entity1.glow);
    const entA_accent = parseColorToRgb(entity1.accent);

    const entB_primary = parseColorToRgb(entity2.primary);
    const entB_glow = parseColorToRgb(entity2.glow);
    const entB_accent = parseColorToRgb(entity2.accent);

    // Entities with organic barycentric orbital drift
    const entityA = {
      x: width * 0.32,
      y: height * 0.46,
      mass: 750 * gravityStrength,
      radius: 44,
      pulsePhase: 0,
      orbitAngle: 0,
      orbitSpeed: 0.0014 * speedMultiplier,
      orbitRadiusX: Math.min(width * 0.15, 170),
      orbitRadiusY: Math.min(height * 0.12, 110),
    };

    const entityB = {
      x: width * 0.68,
      y: height * 0.54,
      mass: 820 * gravityStrength,
      radius: 46,
      pulsePhase: Math.PI,
      orbitAngle: Math.PI,
      orbitSpeed: -0.0012 * speedMultiplier,
      orbitRadiusX: Math.min(width * 0.16, 180),
      orbitRadiusY: Math.min(height * 0.13, 120),
    };

    const count = getParticleCount();
    const particles: Particle[] = [];

    const createParticle = (customX?: number, customY?: number): Particle => {
      const bias = Math.random(); // 0 = Entity A, 1 = Entity B
      const isEntityA = bias < 0.5;
      const host = isEntityA ? entityA : entityB;
      const angle = Math.random() * Math.PI * 2;
      const dist = 40 + Math.random() * (Math.min(width, height) * 0.48);

      const x = customX ?? (host.x + Math.cos(angle) * dist);
      const y = customY ?? (host.y + Math.sin(angle) * dist);

      // 3D Depth coordinate: -1.0 (behind) to +1.0 (foreground crossing over cores)
      const z = (Math.random() * 2) - 1.0;

      // Tangential velocity around nearest host for natural accretion swirl (calibrated for majestic slow float)
      const tangentAngle = angle + (isEntityA ? Math.PI / 2 : -Math.PI / 2);
      const orbitalSpeed = (0.28 + Math.random() * 0.65) * speedMultiplier;

      // Base radius scaled by 3D depth for natural parallax
      let baseRadius = 1.3 + (z + 1.0) * 0.7;
      if (z > 0.6 && Math.random() > 0.75) {
        baseRadius = 3.5 + Math.random() * 2.2; // Large foreground bokeh spark
      }

      return {
        x,
        y,
        z,
        vx: Math.cos(tangentAngle) * orbitalSpeed + (Math.random() - 0.5) * 0.25,
        vy: Math.sin(tangentAngle) * orbitalSpeed + (Math.random() - 0.5) * 0.25,
        radius: baseRadius,
        baseRadius,
        alpha: Math.random() * 0.5 + 0.35,
        baseAlpha: Math.random() * 0.6 + 0.4,
        mass: Math.random() * 0.6 + 0.7,
        trail: [],
        life: 0,
        maxLife: Math.random() * 800 + 600,
        bias,
      };
    };

    for (let i = 0; i < count; i++) {
      particles.push(createParticle());
    }

    const render = (time: number) => {
      // 1. Deep Space Base Clear with Subtle Fluid Cosmic Wash
      ctx.fillStyle = '#06070B';
      ctx.fillRect(0, 0, width, height);

      const bgGrad = ctx.createLinearGradient(0, 0, width, height);
      bgGrad.addColorStop(0, '#040508');
      bgGrad.addColorStop(0.5, '#070810');
      bgGrad.addColorStop(1, '#09060d');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Update Entity orbital positions (fluid barycentric motion)
      entityA.orbitAngle += entityA.orbitSpeed;
      entityB.orbitAngle += entityB.orbitSpeed;
      entityA.pulsePhase += 0.016 * speedMultiplier;
      entityB.pulsePhase += 0.013 * speedMultiplier;

      const baseCenterAX = width * 0.35 + Math.sin(time * 0.0004) * 35;
      const baseCenterAY = height * 0.48 + Math.cos(time * 0.0003) * 25;
      entityA.x = baseCenterAX + Math.cos(entityA.orbitAngle) * entityA.orbitRadiusX;
      entityA.y = baseCenterAY + Math.sin(entityA.orbitAngle * 1.25) * entityA.orbitRadiusY;

      const baseCenterBX = width * 0.65 - Math.sin(time * 0.0004) * 35;
      const baseCenterBY = height * 0.52 - Math.cos(time * 0.0003) * 25;
      entityB.x = baseCenterBX + Math.cos(entityB.orbitAngle) * entityB.orbitRadiusX;
      entityB.y = baseCenterBY + Math.sin(entityB.orbitAngle * 1.15) * entityB.orbitRadiusY;

      // Mouse gentle parallax influence
      if (interactiveMouse && mouseRef.current.active) {
        const mx = (mouseRef.current.x - width * 0.5) * 0.018;
        const my = (mouseRef.current.y - height * 0.5) * 0.018;
        entityA.x += mx;
        entityA.y += my;
        entityB.x += mx * 0.8;
        entityB.y += my * 0.8;
      }

      // Gravitational Bridge Line (Dynamic Color-Interpolated Flow)
      if (showOrbits) {
        ctx.save();
        ctx.setLineDash([3, 10]);

        // Orbit tracks
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.025)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.ellipse(baseCenterAX, baseCenterAY, entityA.orbitRadiusX, entityA.orbitRadiusY, 0, 0, Math.PI * 2);
        ctx.stroke();

        ctx.beginPath();
        ctx.ellipse(baseCenterBX, baseCenterBY, entityB.orbitRadiusX, entityB.orbitRadiusY, 0, 0, Math.PI * 2);
        ctx.stroke();

        // Color-interpolated dynamic bridge between current entities
        const bridgeGrad = ctx.createLinearGradient(entityA.x, entityA.y, entityB.x, entityB.y);
        bridgeGrad.addColorStop(0, rgbToString(entA_primary, 0.16));
        bridgeGrad.addColorStop(0.5, rgbToString(lerpRgb(entA_accent, entB_accent, 0.5), 0.22));
        bridgeGrad.addColorStop(1, rgbToString(entB_primary, 0.16));
        ctx.strokeStyle = bridgeGrad;
        ctx.lineWidth = 1.4;
        ctx.beginPath();
        ctx.moveTo(entityA.x, entityA.y);
        ctx.lineTo(entityB.x, entityB.y);
        ctx.stroke();
        ctx.restore();
      }

      // Composite Mode for Volumetric Radiance
      ctx.save();
      ctx.globalCompositeOperation = 'screen';

      // 2. Atmospheric Nebulae with Dynamic Entity Colors & Central Tides
      const drawNebula = (
        x: number,
        y: number,
        primaryRgb: RGB,
        accentRgb: RGB,
        glowRgb: RGB,
        pulsePhase: number,
        radiusMul = 5.2
      ) => {
        const pulse = Math.sin(pulsePhase) * 10;
        const rad = 46 * radiusMul + pulse;
        const grad = ctx.createRadialGradient(x, y, 0, x, y, rad);
        grad.addColorStop(0, rgbToString(primaryRgb, 0.32));
        grad.addColorStop(0.35, rgbToString(glowRgb, 0.18));
        grad.addColorStop(0.7, rgbToString(accentRgb, 0.07));
        grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(x, y, rad, 0, Math.PI * 2);
        ctx.fill();
      };

      // Nebulae for both entities adapting to whatever colors are configured
      drawNebula(entityA.x, entityA.y, entA_primary, entA_accent, entA_glow, entityA.pulsePhase, 5.5);
      drawNebula(entityB.x, entityB.y, entB_primary, entB_accent, entB_glow, entityB.pulsePhase, 5.8);

      // Central Harmonic Maelstrom (Blends both entity colors seamlessly in the middle)
      const midX = (entityA.x + entityB.x) / 2;
      const midY = (entityA.y + entityB.y) / 2;
      const midPulse = Math.sin(time * 0.0018) * 0.5 + 0.5;
      const blendedCoreRgb = lerpRgb(entA_accent, entB_accent, 0.5);
      const midGrad = ctx.createRadialGradient(midX, midY, 0, midX, midY, 130 + midPulse * 40);
      midGrad.addColorStop(0, rgbToString(blendedCoreRgb, 0.14 * midPulse + 0.06));
      midGrad.addColorStop(0.6, rgbToString(lerpRgb(entA_primary, entB_primary, 0.5), 0.04));
      midGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = midGrad;
      ctx.beginPath();
      ctx.arc(midX, midY, 170, 0, Math.PI * 2);
      ctx.fill();

      // 3. Physics Simulation & Rendering in 3D Depth Layers
      const softCore = 75; // Smooth gravitational damping
      const friction = 0.991; // Fluid cosmic drift

      // Separate background particles (Z < 0) and foreground particles (Z >= 0)
      const bgParticles: Particle[] = [];
      const fgParticles: Particle[] = [];

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Gravitational force vector to Entity A
        const dxA = entityA.x - p.x;
        const dyA = entityA.y - p.y;
        const distSqA = dxA * dxA + dyA * dyA + softCore * softCore;
        const distA = Math.sqrt(distSqA);
        const forceA = (entityA.mass * 0.065) / distSqA;

        // Gravitational force vector to Entity B
        const dxB = entityB.x - p.x;
        const dyB = entityB.y - p.y;
        const distSqB = dxB * dxB + dyB * dyB + softCore * softCore;
        const distB = Math.sqrt(distSqB);
        const forceB = (entityB.mass * 0.065) / distSqB;

        // Cumulative acceleration
        let ax = (dxA / distA) * forceA + (dxB / distB) * forceB;
        let ay = (dyA / distA) * forceA + (dyB / distB) * forceB;

        // Interactive mouse gravity wave
        if (interactiveMouse && mouseRef.current.active) {
          const dxM = mouseRef.current.x - p.x;
          const dyM = mouseRef.current.y - p.y;
          const distSqM = dxM * dxM + dyM * dyM + 4000;
          const distM = Math.sqrt(distSqM);
          if (distM < 260) {
            const forceM = -16 / distM;
            ax += (dxM / distM) * forceM;
            ay += (dyM / distM) * forceM;
          }
        }

        // Velocity integration with calm cosmic scale
        p.vx = (p.vx + ax) * friction;
        p.vy = (p.vy + ay) * friction;

        // Trail positions
        p.trail.push({ x: p.x, y: p.y });
        if (p.trail.length > 5) p.trail.shift();

        p.x += p.vx * speedMultiplier;
        p.y += p.vy * speedMultiplier;
        p.life++;

        // Smooth color ratio calculated dynamically by relative distance between the two entities
        const totalDist = distA + distB;
        const ratio = Math.max(0, Math.min(1, distA / (totalDist || 1)));
        p.bias = ratio; // 0 = close to A (A's color), 1 = close to B (B's color)

        // Respawn if life expired or out of bounds
        const outOfBounds = p.x < -80 || p.x > width + 80 || p.y < -80 || p.y > height + 80;
        if (p.life > p.maxLife || outOfBounds) {
          particles[i] = createParticle();
          continue;
        }

        if (p.z < 0) {
          bgParticles.push(p);
        } else {
          fgParticles.push(p);
        }
      }

      // Helper to render particle sparks and light trails
      const renderParticleBatch = (batch: Particle[], isForeground = false) => {
        for (let i = 0; i < batch.length; i++) {
          const p = batch[i];

          // Compute exact interpolated color between the two entities
          const pRgb = lerpRgb(entA_primary, entB_primary, p.bias);

          // Render Trail
          if (p.trail.length > 1) {
            ctx.beginPath();
            ctx.moveTo(p.trail[0].x, p.trail[0].y);
            for (let t = 1; t < p.trail.length; t++) {
              ctx.lineTo(p.trail[t].x, p.trail[t].y);
            }
            ctx.strokeStyle = rgbToString(pRgb, p.alpha * (isForeground ? 0.45 : 0.25));
            ctx.lineWidth = p.radius * (isForeground ? 0.9 : 0.7);
            ctx.stroke();
          }

          // Render Spark Core
          ctx.fillStyle = rgbToString(pRgb, p.alpha * (isForeground ? 0.95 : 0.8));
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
          ctx.fill();

          // Foreground Bokeh Glow when crossing near front plane
          if (isForeground && p.radius > 2.2) {
            const glowRad = p.radius * 3.8;
            const sparkGrad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, glowRad);
            sparkGrad.addColorStop(0, rgbToString(pRgb, 0.6));
            sparkGrad.addColorStop(0.5, rgbToString(pRgb, 0.2));
            sparkGrad.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.fillStyle = sparkGrad;
            ctx.beginPath();
            ctx.arc(p.x, p.y, glowRad, 0, Math.PI * 2);
            ctx.fill();
          }
        }
      };

      // 3.1. Render Background Particles (Z < 0) BEHIND Entity Cores
      renderParticleBatch(bgParticles, false);

      // 3.2. Render Dynamic Entity Cores / Singularities
      const renderSingularityCore = (
        x: number,
        y: number,
        primaryRgb: RGB,
        accentRgb: RGB,
        glowRgb: RGB,
        pulsePhase: number,
        isHole = false
      ) => {
        const pulse = Math.sin(pulsePhase);
        const coreRad = 44 * (0.86 + pulse * 0.05);

        // Reticle Halo
        ctx.lineWidth = 1.2;
        ctx.strokeStyle = rgbToString(primaryRgb, 0.45 + pulse * 0.15);
        ctx.beginPath();
        ctx.arc(x, y, coreRad * 1.35, 0, Math.PI * 2);
        ctx.stroke();

        // Inner Optical Core
        const coreGrad = ctx.createRadialGradient(x, y, 0, x, y, coreRad);
        coreGrad.addColorStop(0, '#FFFFFF');
        coreGrad.addColorStop(0.35, rgbToString(primaryRgb, 0.95));
        coreGrad.addColorStop(0.75, rgbToString(accentRgb, 0.8));
        coreGrad.addColorStop(1, 'rgba(0, 0, 0, 0.85)');

        ctx.fillStyle = coreGrad;
        ctx.beginPath();
        ctx.arc(x, y, coreRad, 0, Math.PI * 2);
        ctx.fill();

        if (isHole) {
          ctx.fillStyle = '#020306';
          ctx.beginPath();
          ctx.arc(x, y, coreRad * 0.4, 0, Math.PI * 2);
          ctx.fill();
        }

        // Rotating orbital astrometric arcs
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(time * 0.0008 * (isHole ? 1 : -1));
        ctx.strokeStyle = rgbToString(primaryRgb, 0.55);
        ctx.lineWidth = 1.4;
        for (let a = 0; a < 4; a++) {
          ctx.beginPath();
          ctx.arc(0, 0, coreRad * 1.58, a * (Math.PI / 2) + 0.1, (a + 1) * (Math.PI / 2) - 0.5);
          ctx.stroke();
        }
        ctx.restore();
      };

      renderSingularityCore(entityA.x, entityA.y, entA_primary, entA_accent, entA_glow, entityA.pulsePhase, true);
      renderSingularityCore(entityB.x, entityB.y, entB_primary, entB_accent, entB_glow, entityB.pulsePhase, false);

      // 3.3. Render Foreground Particles (Z >= 0) IN FRONT of Entity Cores (crossing over)
      renderParticleBatch(fgParticles, true);

      ctx.restore(); // Restore globalCompositeOperation

      animationFrameId.current = requestAnimationFrame(render);
    };

    animationFrameId.current = requestAnimationFrame(render);

    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current.x = e.clientX;
      mouseRef.current.y = e.clientY;
      mouseRef.current.active = true;
    };

    const handleMouseLeave = () => {
      mouseRef.current.active = false;
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [entity1, entity2, particleDensity, speedMultiplier, gravityStrength, showOrbits, interactiveMouse, getParticleCount]);

  return (
    <div ref={containerRef} className="fixed inset-0 overflow-hidden pointer-events-none select-none z-0">
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full block" />

      {/* Cinematic Film Grain Texture */}
      <div 
        className="absolute inset-0 opacity-[0.032] mix-blend-overlay pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`
        }}
      />

      {/* Deep Vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_45%,rgba(4,5,8,0.75)_100%)] pointer-events-none" />
    </div>
  );
};

export default CosmicBackground;
