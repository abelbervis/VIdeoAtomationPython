import React, { useEffect, useRef, useCallback } from 'react';

export interface EntityPalette {
  primary: string;
  glow: string;
  accent: string;
  name?: string;
}

export type FocusMode = 'dual' | 'entity1' | 'entity2';

export interface CosmicBackgroundProps {
  entity1?: EntityPalette;
  entity2?: EntityPalette;
  focusMode?: FocusMode;
  particleDensity?: 'low' | 'medium' | 'high';
  speedMultiplier?: number;
  gravityStrength?: number;
  showOrbits?: boolean;
  interactiveMouse?: boolean;
  onSelectFocus?: (mode: FocusMode) => void;
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
  isCorona?: boolean;
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
  return { r: 0, g: 240, b: 255 };
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
  focusMode = 'dual',
  particleDensity = 'medium',
  speedMultiplier = 1.0,
  gravityStrength = 1.0,
  showOrbits = true,
  interactiveMouse = true,
  onSelectFocus,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mouseRef = useRef<{ x: number; y: number; active: boolean }>({ x: 0, y: 0, active: false });
  const animationFrameId = useRef<number | null>(null);

  // Smooth focus interpolation tracker (0.0 = Dual, -1.0 = Focus Entity 1, 1.0 = Focus Entity 2)
  const currentFocusVal = useRef<number>(0.0);

  const getParticleCount = useCallback(() => {
    switch (particleDensity) {
      case 'low':
        return 160;
      case 'high':
        return 420;
      case 'medium':
      default:
        return 280;
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

    const entA_primary = parseColorToRgb(entity1.primary);
    const entA_glow = parseColorToRgb(entity1.glow);
    const entA_accent = parseColorToRgb(entity1.accent);

    const entB_primary = parseColorToRgb(entity2.primary);
    const entB_glow = parseColorToRgb(entity2.glow);
    const entB_accent = parseColorToRgb(entity2.accent);

    // Entity state objects
    const entityA = {
      x: width * 0.32,
      y: height * 0.46,
      mass: 750 * gravityStrength,
      radius: 44,
      scale: 1.0,
      opacity: 1.0,
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
      scale: 1.0,
      opacity: 1.0,
      pulsePhase: Math.PI,
      orbitAngle: Math.PI,
      orbitSpeed: -0.0012 * speedMultiplier,
      orbitRadiusX: Math.min(width * 0.16, 180),
      orbitRadiusY: Math.min(height * 0.13, 120),
    };

    const count = getParticleCount();
    const particles: Particle[] = [];

    const createParticle = (customX?: number, customY?: number, forceCorona = false): Particle => {
      let isEntityA: boolean;
      if (focusMode === 'entity1') {
        isEntityA = Math.random() < 0.88;
      } else if (focusMode === 'entity2') {
        isEntityA = Math.random() < 0.12;
      } else {
        isEntityA = Math.random() < 0.5;
      }

      const host = isEntityA ? entityA : entityB;
      const angle = Math.random() * Math.PI * 2;

      // Accretion corona vs deep cosmic dust
      const isCorona = forceCorona || Math.random() < (focusMode !== 'dual' ? 0.65 : 0.35);
      const dist = isCorona 
        ? (30 + Math.random() * 110) 
        : (60 + Math.random() * (Math.min(width, height) * 0.45));

      const x = customX ?? (host.x + Math.cos(angle) * dist);
      const y = customY ?? (host.y + Math.sin(angle) * dist);

      // 3D Depth coordinate: -1.0 (behind) to +1.0 (foreground crossing in front of cores)
      const z = (Math.random() * 2) - 1.0;

      const tangentAngle = angle + (isEntityA ? Math.PI / 2 : -Math.PI / 2);
      const orbitalSpeed = (isCorona ? 0.45 + Math.random() * 0.85 : 0.25 + Math.random() * 0.55) * speedMultiplier;

      // Foreground particles have large distinct radius and high specular visibility
      let baseRadius = 1.4 + (z + 1.0) * 0.9;
      if (z > 0.3) {
        baseRadius = 3.8 + Math.random() * 3.4; // 3.8px - 7.2px prominent foreground spark
      }

      return {
        x,
        y,
        z,
        vx: Math.cos(tangentAngle) * orbitalSpeed + (Math.random() - 0.5) * 0.2,
        vy: Math.sin(tangentAngle) * orbitalSpeed + (Math.random() - 0.5) * 0.2,
        radius: baseRadius,
        baseRadius,
        alpha: Math.random() * 0.45 + 0.55,
        baseAlpha: Math.random() * 0.5 + 0.5,
        mass: Math.random() * 0.6 + 0.7,
        trail: [],
        life: 0,
        maxLife: Math.random() * 800 + 600,
        bias: isEntityA ? 0.0 : 1.0,
        isCorona,
      };
    };

    for (let i = 0; i < count; i++) {
      particles.push(createParticle());
    }

    const render = (time: number) => {
      // Smooth focus interpolation
      const targetFocus = focusMode === 'entity1' ? -1.0 : (focusMode === 'entity2' ? 1.0 : 0.0);
      currentFocusVal.current += (targetFocus - currentFocusVal.current) * 0.04;
      const fVal = currentFocusVal.current; // -1 to 1

      // 1. Deep Space Base
      ctx.fillStyle = '#06070B';
      ctx.fillRect(0, 0, width, height);

      const bgGrad = ctx.createLinearGradient(0, 0, width, height);
      bgGrad.addColorStop(0, '#040508');
      bgGrad.addColorStop(0.5, '#070810');
      bgGrad.addColorStop(1, '#09060d');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Update Entity orbital positions based on Focus Mode
      entityA.orbitAngle += entityA.orbitSpeed;
      entityB.orbitAngle += entityB.orbitSpeed;
      entityA.pulsePhase += 0.016 * speedMultiplier;
      entityB.pulsePhase += 0.013 * speedMultiplier;

      // Base barycentric centers smoothly shifting under focus
      const dualCenterAX = width * 0.33 + Math.sin(time * 0.0004) * 30;
      const dualCenterAY = height * 0.46 + Math.cos(time * 0.0003) * 20;
      const focusCenterAX = width * 0.50;
      const focusCenterAY = height * 0.48;

      const dualCenterBX = width * 0.67 - Math.sin(time * 0.0004) * 30;
      const dualCenterBY = height * 0.54 - Math.cos(time * 0.0003) * 20;
      const focusCenterBX = width * 0.50;
      const focusCenterBY = height * 0.48;

      // Entity A position calculation
      if (fVal < 0) {
        // Entity A focused in center
        const tA = -fVal; // 0 to 1
        const curAX = dualCenterAX + (focusCenterAX - dualCenterAX) * tA;
        const curAY = dualCenterAY + (focusCenterAY - dualCenterAY) * tA;
        entityA.x = curAX + Math.cos(entityA.orbitAngle) * (entityA.orbitRadiusX * (1 - tA * 0.7));
        entityA.y = curAY + Math.sin(entityA.orbitAngle * 1.2) * (entityA.orbitRadiusY * (1 - tA * 0.7));
        entityA.scale = 1.0 + tA * 0.28;
        entityA.opacity = 1.0;

        // Entity B peripheral shift
        const curBX = dualCenterBX + (width * 0.92 - dualCenterBX) * tA;
        const curBY = dualCenterBY + (height * 0.75 - dualCenterBY) * tA;
        entityB.x = curBX;
        entityB.y = curBY;
        entityB.scale = 1.0 - tA * 0.45;
        entityB.opacity = 1.0 - tA * 0.65;
      } else if (fVal > 0) {
        // Entity B focused in center
        const tB = fVal; // 0 to 1
        const curBX = dualCenterBX + (focusCenterBX - dualCenterBX) * tB;
        const curBY = dualCenterBY + (focusCenterBY - dualCenterBY) * tB;
        entityB.x = curBX + Math.cos(entityB.orbitAngle) * (entityB.orbitRadiusX * (1 - tB * 0.7));
        entityB.y = curBY + Math.sin(entityB.orbitAngle * 1.2) * (entityB.orbitRadiusY * (1 - tB * 0.7));
        entityB.scale = 1.0 + tB * 0.28;
        entityB.opacity = 1.0;

        // Entity A peripheral shift
        const curAX = dualCenterAX + (width * 0.08 - dualCenterAX) * tB;
        const curAY = dualCenterAY + (height * 0.75 - dualCenterAY) * tB;
        entityA.x = curAX;
        entityA.y = curAY;
        entityA.scale = 1.0 - tB * 0.45;
        entityA.opacity = 1.0 - tB * 0.65;
      } else {
        // Pure dual balance
        entityA.x = dualCenterAX + Math.cos(entityA.orbitAngle) * entityA.orbitRadiusX;
        entityA.y = dualCenterAY + Math.sin(entityA.orbitAngle * 1.25) * entityA.orbitRadiusY;
        entityA.scale = 1.0;
        entityA.opacity = 1.0;

        entityB.x = dualCenterBX + Math.cos(entityB.orbitAngle) * entityB.orbitRadiusX;
        entityB.y = dualCenterBY + Math.sin(entityB.orbitAngle * 1.15) * entityB.orbitRadiusY;
        entityB.scale = 1.0;
        entityB.opacity = 1.0;
      }

      // Mouse interactive tilt
      if (interactiveMouse && mouseRef.current.active) {
        const mx = (mouseRef.current.x - width * 0.5) * 0.015;
        const my = (mouseRef.current.y - height * 0.5) * 0.015;
        entityA.x += mx;
        entityA.y += my;
        entityB.x += mx * 0.8;
        entityB.y += my * 0.8;
      }

      // Orbits & Gravitational Bridge Line
      if (showOrbits && Math.abs(fVal) < 0.8) {
        ctx.save();
        ctx.setLineDash([3, 10]);
        ctx.globalAlpha = Math.max(0, 1 - Math.abs(fVal) * 1.2);

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

      // 2. Volumetric Nebulae & Radiance
      ctx.save();
      ctx.globalCompositeOperation = 'screen';

      const drawNebula = (
        x: number,
        y: number,
        primaryRgb: RGB,
        accentRgb: RGB,
        glowRgb: RGB,
        pulsePhase: number,
        opacity: number,
        radiusMul = 5.2
      ) => {
        if (opacity <= 0.01) return;
        const pulse = Math.sin(pulsePhase) * 10;
        const rad = 46 * radiusMul + pulse;
        const grad = ctx.createRadialGradient(x, y, 0, x, y, rad);
        grad.addColorStop(0, rgbToString(primaryRgb, 0.35 * opacity));
        grad.addColorStop(0.35, rgbToString(glowRgb, 0.20 * opacity));
        grad.addColorStop(0.7, rgbToString(accentRgb, 0.08 * opacity));
        grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(x, y, rad, 0, Math.PI * 2);
        ctx.fill();
      };

      drawNebula(entityA.x, entityA.y, entA_primary, entA_accent, entA_glow, entityA.pulsePhase, entityA.opacity, fVal < -0.3 ? 7.2 : 5.5);
      drawNebula(entityB.x, entityB.y, entB_primary, entB_accent, entB_glow, entityB.pulsePhase, entityB.opacity, fVal > 0.3 ? 7.2 : 5.8);

      // Central Harmonic Maelstrom (in dual mode)
      if (Math.abs(fVal) < 0.7) {
        const midX = (entityA.x + entityB.x) / 2;
        const midY = (entityA.y + entityB.y) / 2;
        const midPulse = Math.sin(time * 0.0018) * 0.5 + 0.5;
        const blendedCoreRgb = lerpRgb(entA_accent, entB_accent, 0.5);
        const midGrad = ctx.createRadialGradient(midX, midY, 0, midX, midY, 150 + midPulse * 40);
        midGrad.addColorStop(0, rgbToString(blendedCoreRgb, (0.15 * midPulse + 0.07) * (1 - Math.abs(fVal))));
        midGrad.addColorStop(0.6, rgbToString(lerpRgb(entA_primary, entB_primary, 0.5), 0.04 * (1 - Math.abs(fVal))));
        midGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = midGrad;
        ctx.beginPath();
        ctx.arc(midX, midY, 190, 0, Math.PI * 2);
        ctx.fill();
      }

      // 3. Physics Simulation & Sorting into 3D Depth
      const softCore = 65;
      const friction = 0.992;

      const bgParticles: Particle[] = [];
      const fgParticles: Particle[] = [];

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Gravitational forces
        const dxA = entityA.x - p.x;
        const dyA = entityA.y - p.y;
        const distSqA = dxA * dxA + dyA * dyA + softCore * softCore;
        const distA = Math.sqrt(distSqA);
        const massMulA = (fVal < -0.3 ? 1.4 : (fVal > 0.3 ? 0.3 : 1.0));
        const forceA = (entityA.mass * massMulA * 0.07) / distSqA;

        const dxB = entityB.x - p.x;
        const dyB = entityB.y - p.y;
        const distSqB = dxB * dxB + dyB * dyB + softCore * softCore;
        const distB = Math.sqrt(distSqB);
        const massMulB = (fVal > 0.3 ? 1.4 : (fVal < -0.3 ? 0.3 : 1.0));
        const forceB = (entityB.mass * massMulB * 0.07) / distSqB;

        let ax = (dxA / distA) * forceA + (dxB / distB) * forceB;
        let ay = (dyA / distA) * forceA + (dyB / distB) * forceB;

        // Mouse gravity influence
        if (interactiveMouse && mouseRef.current.active) {
          const dxM = mouseRef.current.x - p.x;
          const dyM = mouseRef.current.y - p.y;
          const distSqM = dxM * dxM + dyM * dyM + 4000;
          const distM = Math.sqrt(distSqM);
          if (distM < 260) {
            const forceM = -18 / distM;
            ax += (dxM / distM) * forceM;
            ay += (dyM / distM) * forceM;
          }
        }

        p.vx = (p.vx + ax) * friction;
        p.vy = (p.vy + ay) * friction;

        p.trail.push({ x: p.x, y: p.y });
        if (p.trail.length > (p.z > 0 ? 8 : 5)) p.trail.shift();

        p.x += p.vx * speedMultiplier;
        p.y += p.vy * speedMultiplier;
        p.life++;

        // Color interpolation ratio
        const totalDist = distA + distB;
        let ratio = Math.max(0, Math.min(1, distA / (totalDist || 1)));
        if (fVal < -0.4) ratio = Math.max(0, ratio - 0.35);
        if (fVal > 0.4) ratio = Math.min(1, ratio + 0.35);
        p.bias = ratio;

        const outOfBounds = p.x < -120 || p.x > width + 120 || p.y < -120 || p.y > height + 120;
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

      // 3.1. Render Background Particle Pass (Z < 0) Behind Cores
      for (let i = 0; i < bgParticles.length; i++) {
        const p = bgParticles[i];
        const pRgb = lerpRgb(entA_primary, entB_primary, p.bias);

        if (p.trail.length > 1) {
          ctx.beginPath();
          ctx.moveTo(p.trail[0].x, p.trail[0].y);
          for (let t = 1; t < p.trail.length; t++) {
            ctx.lineTo(p.trail[t].x, p.trail[t].y);
          }
          ctx.strokeStyle = rgbToString(pRgb, p.alpha * 0.35);
          ctx.lineWidth = p.radius * 0.7;
          ctx.stroke();
        }

        ctx.fillStyle = rgbToString(pRgb, p.alpha * 0.85);
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();
      }

      // 3.2. Render Entity Cores / Singularities
      const renderSingularityCore = (
        x: number,
        y: number,
        primaryRgb: RGB,
        accentRgb: RGB,
        glowRgb: RGB,
        pulsePhase: number,
        scale: number,
        opacity: number,
        isHole = false
      ) => {
        if (opacity <= 0.01) return;
        const pulse = Math.sin(pulsePhase);
        const coreRad = 44 * scale * (0.86 + pulse * 0.05);

        // Reticle Halo
        ctx.lineWidth = 1.3 * scale;
        ctx.strokeStyle = rgbToString(primaryRgb, (0.45 + pulse * 0.15) * opacity);
        ctx.beginPath();
        ctx.arc(x, y, coreRad * 1.35, 0, Math.PI * 2);
        ctx.stroke();

        // Inner Optical Core
        const coreGrad = ctx.createRadialGradient(x, y, 0, x, y, coreRad);
        coreGrad.addColorStop(0, '#FFFFFF');
        coreGrad.addColorStop(0.35, rgbToString(primaryRgb, 0.95 * opacity));
        coreGrad.addColorStop(0.75, rgbToString(accentRgb, 0.80 * opacity));
        coreGrad.addColorStop(1, `rgba(0, 0, 0, ${0.85 * opacity})`);

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

        // Rotating astrometric orbital arcs
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(time * 0.0008 * (isHole ? 1 : -1));
        ctx.strokeStyle = rgbToString(primaryRgb, 0.55 * opacity);
        ctx.lineWidth = 1.4 * scale;
        for (let a = 0; a < 4; a++) {
          ctx.beginPath();
          ctx.arc(0, 0, coreRad * 1.58, a * (Math.PI / 2) + 0.1, (a + 1) * (Math.PI / 2) - 0.5);
          ctx.stroke();
        }
        ctx.restore();
      };

      renderSingularityCore(entityA.x, entityA.y, entA_primary, entA_accent, entA_glow, entityA.pulsePhase, entityA.scale, entityA.opacity, true);
      renderSingularityCore(entityB.x, entityB.y, entB_primary, entB_accent, entB_glow, entityB.pulsePhase, entityB.scale, entityB.opacity, false);

      // 3.3. Render Prominent Foreground Particle Pass (Z >= 0) IN FRONT OF ENTITY CORES
      for (let i = 0; i < fgParticles.length; i++) {
        const p = fgParticles[i];
        const pRgb = lerpRgb(entA_primary, entB_primary, p.bias);

        // Proximity flare when passing in front of either entity core
        const distToA = Math.hypot(p.x - entityA.x, p.y - entityA.y);
        const distToB = Math.hypot(p.x - entityB.x, p.y - entityB.y);
        const crossingCore = (distToA < entityA.radius * entityA.scale * 1.4 && entityA.opacity > 0.3) ||
                             (distToB < entityB.radius * entityB.scale * 1.4 && entityB.opacity > 0.3);

        const flareBoost = crossingCore ? 1.6 : 1.0;

        // Extended luminous motion trail
        if (p.trail.length > 1) {
          ctx.beginPath();
          ctx.moveTo(p.trail[0].x, p.trail[0].y);
          for (let t = 1; t < p.trail.length; t++) {
            ctx.lineTo(p.trail[t].x, p.trail[t].y);
          }
          ctx.strokeStyle = rgbToString(pRgb, Math.min(1.0, p.alpha * 0.65 * flareBoost));
          ctx.lineWidth = p.radius * 0.9 * flareBoost;
          ctx.stroke();
        }

        // Chromatic outer glow ring / bokeh disc
        const bokehRad = p.radius * (crossingCore ? 5.2 : 3.8);
        const bokehGrad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, bokehRad);
        bokehGrad.addColorStop(0, rgbToString(pRgb, Math.min(1.0, 0.85 * flareBoost)));
        bokehGrad.addColorStop(0.4, rgbToString(pRgb, 0.35 * flareBoost));
        bokehGrad.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = bokehGrad;
        ctx.beginPath();
        ctx.arc(p.x, p.y, bokehRad, 0, Math.PI * 2);
        ctx.fill();

        // White-Hot Incandescent Specular Core (100% visible crossing in front)
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.arc(p.x, p.y, Math.max(1.8, p.radius * 0.75 * flareBoost), 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.restore();

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

    // Clicking anywhere smoothly toggles camera shot (Dual -> Entity 1 Focus -> Entity 2 Focus)
    const handleCanvasClick = (e: MouseEvent) => {
      if (!onSelectFocus) return;
      const clickX = e.clientX;
      if (focusMode === 'dual') {
        if (clickX < width * 0.5) onSelectFocus('entity1');
        else onSelectFocus('entity2');
      } else {
        onSelectFocus('dual');
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseleave', handleMouseLeave);
    canvas.addEventListener('click', handleCanvasClick);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseleave', handleMouseLeave);
      canvas.removeEventListener('click', handleCanvasClick);
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [entity1, entity2, focusMode, particleDensity, speedMultiplier, gravityStrength, showOrbits, interactiveMouse, onSelectFocus, getParticleCount]);

  return (
    <div ref={containerRef} className="fixed inset-0 overflow-hidden pointer-events-none select-none z-0">
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full block pointer-events-auto cursor-pointer" />

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
