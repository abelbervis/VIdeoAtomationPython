import React, { useEffect, useRef, useState, useCallback } from 'react';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  baseRadius: number;
  colorType: 'cyan' | 'violet' | 'amber' | 'neutral';
  alpha: number;
  baseAlpha: number;
  mass: number;
  trail: { x: number; y: number }[];
  life: number;
  maxLife: number;
}

interface CosmicEntity {
  x: number;
  y: number;
  targetX: number;
  targetY: number;
  name: string;
  designation: string;
  type: 'quantum' | 'stellar';
  mass: number;
  radius: number;
  baseColor: string;
  glowColor: string;
  accentColor: string;
  pulsePhase: number;
  orbitAngle: number;
  orbitSpeed: number;
  orbitRadiusX: number;
  orbitRadiusY: number;
}

export interface CosmicBackgroundProps {
  particleDensity?: 'low' | 'medium' | 'high';
  speedMultiplier?: number;
  gravityStrength?: number;
  showTelemetry?: boolean;
  showOrbits?: boolean;
  interactiveMouse?: boolean;
}

export const CosmicBackground: React.FC<CosmicBackgroundProps> = ({
  particleDensity = 'medium',
  speedMultiplier = 1,
  gravityStrength = 1,
  showTelemetry = true,
  showOrbits = true,
  interactiveMouse = true,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mouseRef = useRef<{ x: number; y: number; active: boolean }>({ x: 0, y: 0, active: false });
  const animationFrameId = useRef<number | null>(null);

  // Live telemetry metrics
  const [telemetryData, setTelemetryData] = useState({
    fps: 60,
    activeParticles: 220,
    distanceBetweenEntities: 0,
    quantumFluctuation: 0.98,
    gravitationalFlux: 1.42,
  });

  const getParticleCount = useCallback(() => {
    switch (particleDensity) {
      case 'low':
        return 140;
      case 'high':
        return 340;
      case 'medium':
      default:
        return 220;
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

    // Initial Entity Coordinates
    const entityA: CosmicEntity = {
      x: width * 0.32,
      y: height * 0.45,
      targetX: width * 0.32,
      targetY: height * 0.45,
      name: 'AEON-01',
      designation: 'Singularidad Cuántica / Vórtice Frío',
      type: 'quantum',
      mass: 850 * gravityStrength,
      radius: 42,
      baseColor: '#00F0FF',
      glowColor: 'rgba(0, 240, 255, 0.4)',
      accentColor: '#7000FF',
      pulsePhase: 0,
      orbitAngle: 0,
      orbitSpeed: 0.003 * speedMultiplier,
      orbitRadiusX: Math.min(width * 0.12, 140),
      orbitRadiusY: Math.min(height * 0.1, 90),
    };

    const entityB: CosmicEntity = {
      x: width * 0.68,
      y: height * 0.55,
      targetX: width * 0.68,
      targetY: height * 0.55,
      name: 'SOL-PRIME',
      designation: 'Corona Gravitatoria / Forja Estelar',
      type: 'stellar',
      mass: 920 * gravityStrength,
      radius: 48,
      baseColor: '#FF6B00',
      glowColor: 'rgba(255, 80, 0, 0.45)',
      accentColor: '#FF0055',
      pulsePhase: Math.PI,
      orbitAngle: Math.PI,
      orbitSpeed: -0.0025 * speedMultiplier,
      orbitRadiusX: Math.min(width * 0.14, 160),
      orbitRadiusY: Math.min(height * 0.12, 110),
    };

    const count = getParticleCount();
    const particles: Particle[] = [];

    const createParticle = (customX?: number, customY?: number): Particle => {
      const isEntityA = Math.random() > 0.5;
      const host = isEntityA ? entityA : entityB;
      const angle = Math.random() * Math.PI * 2;
      const dist = 50 + Math.random() * (Math.min(width, height) * 0.45);

      const x = customX ?? (host.x + Math.cos(angle) * dist);
      const y = customY ?? (host.y + Math.sin(angle) * dist);

      // Tangential velocity around nearest host for natural accretion swirl
      const tangentAngle = angle + (isEntityA ? Math.PI / 2 : -Math.PI / 2);
      const orbitalSpeed = (Math.random() * 1.4 + 0.6) * speedMultiplier;

      const colorTypes: Particle['colorType'][] = isEntityA 
        ? ['cyan', 'cyan', 'neutral', 'violet'] 
        : ['amber', 'amber', 'neutral', 'violet'];

      const sizeRoll = Math.random();
      let baseRadius = 1.2;
      if (sizeRoll > 0.94) baseRadius = 3.2; // Foreground bokeh dust
      else if (sizeRoll > 0.8) baseRadius = 2.0;

      return {
        x,
        y,
        vx: Math.cos(tangentAngle) * orbitalSpeed + (Math.random() - 0.5) * 0.4,
        vy: Math.sin(tangentAngle) * orbitalSpeed + (Math.random() - 0.5) * 0.4,
        radius: baseRadius,
        baseRadius,
        colorType: colorTypes[Math.floor(Math.random() * colorTypes.length)],
        alpha: Math.random() * 0.6 + 0.2,
        baseAlpha: Math.random() * 0.7 + 0.3,
        mass: Math.random() * 0.8 + 0.6,
        trail: [],
        life: 0,
        maxLife: Math.random() * 600 + 400,
      };
    };

    for (let i = 0; i < count; i++) {
      particles.push(createParticle());
    }

    // Performance & FPS meter tracking
    let lastFrameTime = performance.now();
    let frameCounter = 0;
    let lastFpsUpdate = performance.now();

    const render = (time: number) => {
      frameCounter++;
      if (time - lastFpsUpdate > 800) {
        const fps = Math.round((frameCounter * 1000) / (time - lastFpsUpdate));
        const dist = Math.hypot(entityA.x - entityB.x, entityA.y - entityB.y);
        setTelemetryData({
          fps,
          activeParticles: particles.length,
          distanceBetweenEntities: Math.round(dist),
          quantumFluctuation: parseFloat((0.95 + Math.sin(time * 0.002) * 0.08).toFixed(3)),
          gravitationalFlux: parseFloat((1.4 + Math.cos(time * 0.0015) * 0.15).toFixed(3)),
        });
        frameCounter = 0;
        lastFpsUpdate = time;
      }
      lastFrameTime = time;

      // Deep space ambient background clear
      ctx.fillStyle = '#06070B';
      ctx.fillRect(0, 0, width, height);

      // Deep celestial gradient wash
      const bgGrad = ctx.createLinearGradient(0, 0, width, height);
      bgGrad.addColorStop(0, '#040609');
      bgGrad.addColorStop(0.5, '#070912');
      bgGrad.addColorStop(1, '#0b080f');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Update Entity orbital positions
      entityA.orbitAngle += entityA.orbitSpeed;
      entityB.orbitAngle += entityB.orbitSpeed;
      entityA.pulsePhase += 0.03 * speedMultiplier;
      entityB.pulsePhase += 0.024 * speedMultiplier;

      const centerX = width * 0.5;
      const centerY = height * 0.5;

      const baseCenterAX = width * 0.34;
      const baseCenterAY = height * 0.48;
      entityA.x = baseCenterAX + Math.cos(entityA.orbitAngle) * entityA.orbitRadiusX;
      entityA.y = baseCenterAY + Math.sin(entityA.orbitAngle * 1.3) * entityA.orbitRadiusY;

      const baseCenterBX = width * 0.66;
      const baseCenterBY = height * 0.52;
      entityB.x = baseCenterBX + Math.cos(entityB.orbitAngle) * entityB.orbitRadiusX;
      entityB.y = baseCenterBY + Math.sin(entityB.orbitAngle * 1.1) * entityB.orbitRadiusY;

      // Mouse influence on singularity center if interactive
      if (interactiveMouse && mouseRef.current.active) {
        entityA.x += (mouseRef.current.x - width * 0.5) * 0.03;
        entityA.y += (mouseRef.current.y - height * 0.5) * 0.03;
        entityB.x += (mouseRef.current.x - width * 0.5) * 0.02;
        entityB.y += (mouseRef.current.y - height * 0.5) * 0.02;
      }

      // Draw Gravitational Bridge & Orbital Lines
      if (showOrbits) {
        ctx.save();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.035)';
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 12]);

        // Orbit paths
        ctx.beginPath();
        ctx.ellipse(baseCenterAX, baseCenterAY, entityA.orbitRadiusX, entityA.orbitRadiusY, 0, 0, Math.PI * 2);
        ctx.stroke();

        ctx.beginPath();
        ctx.ellipse(baseCenterBX, baseCenterBY, entityB.orbitRadiusX, entityB.orbitRadiusY, 0, 0, Math.PI * 2);
        ctx.stroke();

        // Gravitational Bridge Line
        const bridgeGrad = ctx.createLinearGradient(entityA.x, entityA.y, entityB.x, entityB.y);
        bridgeGrad.addColorStop(0, 'rgba(0, 240, 255, 0.15)');
        bridgeGrad.addColorStop(0.5, 'rgba(168, 85, 247, 0.25)');
        bridgeGrad.addColorStop(1, 'rgba(255, 107, 0, 0.15)');
        ctx.strokeStyle = bridgeGrad;
        ctx.lineWidth = 1.5;
        ctx.setLineDash([2, 8]);
        ctx.beginPath();
        ctx.moveTo(entityA.x, entityA.y);
        ctx.lineTo(entityB.x, entityB.y);
        ctx.stroke();
        ctx.restore();
      }

      // Composite Mode for Volumetric Space Radiance
      ctx.save();
      ctx.globalCompositeOperation = 'screen';

      // 1. Render Massive Atmospheric Nebulae for Both Entities
      const drawNebula = (entity: CosmicEntity, colorStops: [number, string][], radiusMultiplier = 4.5) => {
        const pulse = Math.sin(entity.pulsePhase) * 12;
        const rad = (entity.radius * radiusMultiplier) + pulse;
        const grad = ctx.createRadialGradient(entity.x, entity.y, 0, entity.x, entity.y, rad);
        colorStops.forEach(([stop, color]) => grad.addColorStop(stop, color));
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(entity.x, entity.y, rad, 0, Math.PI * 2);
        ctx.fill();
      };

      // Entity A Glow (Cyan/Deep Indigo)
      drawNebula(entityA, [
        [0, 'rgba(0, 240, 255, 0.35)'],
        [0.3, 'rgba(75, 0, 255, 0.2)'],
        [0.7, 'rgba(0, 100, 255, 0.08)'],
        [1, 'rgba(0, 0, 0, 0)'],
      ], 5.2);

      // Entity B Glow (Stellar Amber/Crimson)
      drawNebula(entityB, [
        [0, 'rgba(255, 140, 0, 0.38)'],
        [0.35, 'rgba(255, 0, 90, 0.2)'],
        [0.75, 'rgba(120, 0, 150, 0.08)'],
        [1, 'rgba(0, 0, 0, 0)'],
      ], 5.6);

      // Bridge Singularity Pulse at Midpoint
      const midX = (entityA.x + entityB.x) / 2;
      const midY = (entityA.y + entityB.y) / 2;
      const bridgePulse = Math.sin(time * 0.003) * 0.5 + 0.5;
      const midGrad = ctx.createRadialGradient(midX, midY, 0, midX, midY, 110 + bridgePulse * 30);
      midGrad.addColorStop(0, `rgba(168, 85, 247, ${0.12 * bridgePulse + 0.05})`);
      midGrad.addColorStop(0.5, 'rgba(59, 130, 246, 0.04)');
      midGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = midGrad;
      ctx.beginPath();
      ctx.arc(midX, midY, 140, 0, Math.PI * 2);
      ctx.fill();

      // 2. Update & Render Particles with Dual-Gravity Physics
      const softCore = 60; // Prevents division by zero / slingshot extremes
      const friction = 0.988;

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Gravitational force vector to Entity A
        const dxA = entityA.x - p.x;
        const dyA = entityA.y - p.y;
        const distSqA = dxA * dxA + dyA * dyA + softCore * softCore;
        const distA = Math.sqrt(distSqA);
        const forceA = (entityA.mass * 0.12) / distSqA;

        // Gravitational force vector to Entity B
        const dxB = entityB.x - p.x;
        const dyB = entityB.y - p.y;
        const distSqB = dxB * dxB + dyB * dyB + softCore * softCore;
        const distB = Math.sqrt(distSqB);
        const forceB = (entityB.mass * 0.12) / distSqB;

        // Cumulative acceleration
        let ax = (dxA / distA) * forceA + (dxB / distB) * forceB;
        let ay = (dyA / distA) * forceA + (dyB / distB) * forceB;

        // Interactive mouse gravity disturbance
        if (interactiveMouse && mouseRef.current.active) {
          const dxM = mouseRef.current.x - p.x;
          const dyM = mouseRef.current.y - p.y;
          const distSqM = dxM * dxM + dyM * dyM + 3000;
          const distM = Math.sqrt(distSqM);
          if (distM < 240) {
            // Gentle warp/repulsion
            const forceM = -24 / distM;
            ax += (dxM / distM) * forceM;
            ay += (dyM / distM) * forceM;
          }
        }

        // Velocity integration
        p.vx = (p.vx + ax) * friction;
        p.vy = (p.vy + ay) * friction;

        // Store trail
        p.trail.push({ x: p.x, y: p.y });
        if (p.trail.length > 4) p.trail.shift();

        p.x += p.vx * speedMultiplier;
        p.y += p.vy * speedMultiplier;
        p.life++;

        // Respawn if too far out of bounds or life expired or swallowed by black hole core
        const swallowed = distA < 14 || distB < 14;
        const outOfBounds = p.x < -60 || p.x > width + 60 || p.y < -60 || p.y > height + 60;

        if (p.life > p.maxLife || outOfBounds || swallowed) {
          particles[i] = createParticle();
          continue;
        }

        // Draw particle trail for high-energy motion
        if (p.trail.length > 1) {
          ctx.beginPath();
          ctx.moveTo(p.trail[0].x, p.trail[0].y);
          for (let t = 1; t < p.trail.length; t++) {
            ctx.lineTo(p.trail[t].x, p.trail[t].y);
          }
          let trailColor = 'rgba(140, 200, 255, 0.2)';
          if (p.colorType === 'cyan') trailColor = `rgba(0, 240, 255, ${p.alpha * 0.4})`;
          else if (p.colorType === 'amber') trailColor = `rgba(255, 140, 0, ${p.alpha * 0.4})`;
          else if (p.colorType === 'violet') trailColor = `rgba(190, 80, 255, ${p.alpha * 0.4})`;

          ctx.strokeStyle = trailColor;
          ctx.lineWidth = p.radius * 0.8;
          ctx.stroke();
        }

        // Draw Particle Spark
        let pColor = '#ffffff';
        if (p.colorType === 'cyan') pColor = '#5CF0FF';
        else if (p.colorType === 'amber') pColor = '#FFB042';
        else if (p.colorType === 'violet') pColor = '#D47BFF';

        ctx.fillStyle = pColor;
        ctx.globalAlpha = p.alpha;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();

        // Extra outer glow for bokeh sparks
        if (p.baseRadius > 2.2) {
          const sparkGrad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.radius * 3.5);
          sparkGrad.addColorStop(0, pColor);
          sparkGrad.addColorStop(1, 'rgba(0,0,0,0)');
          ctx.fillStyle = sparkGrad;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius * 3.5, 0, Math.PI * 2);
          ctx.fill();
        }

        ctx.globalAlpha = 1;
      }

      // 3. Render Solid High-Tech Singularities / Cores
      const renderSingularityCore = (entity: CosmicEntity) => {
        const pulse = Math.sin(entity.pulsePhase);
        const coreRad = entity.radius * (0.85 + pulse * 0.06);

        // Core Halo Rings (Futuristic Astrometric Target)
        ctx.lineWidth = 1.2;
        ctx.strokeStyle = entity.baseColor;
        ctx.globalAlpha = 0.45 + pulse * 0.2;

        ctx.beginPath();
        ctx.arc(entity.x, entity.y, coreRad * 1.35, 0, Math.PI * 2);
        ctx.stroke();

        // Inner Dense Optical Singularity
        const coreGrad = ctx.createRadialGradient(entity.x, entity.y, 0, entity.x, entity.y, coreRad);
        coreGrad.addColorStop(0, '#FFFFFF');
        coreGrad.addColorStop(0.3, entity.baseColor);
        coreGrad.addColorStop(0.7, entity.accentColor);
        coreGrad.addColorStop(1, 'rgba(0, 0, 0, 0.8)');

        ctx.fillStyle = coreGrad;
        ctx.globalAlpha = 0.95;
        ctx.beginPath();
        ctx.arc(entity.x, entity.y, coreRad, 0, Math.PI * 2);
        ctx.fill();

        // Singularity Black Hole Shadow Center (for Entity A)
        if (entity.type === 'quantum') {
          ctx.fillStyle = '#020306';
          ctx.globalAlpha = 0.9;
          ctx.beginPath();
          ctx.arc(entity.x, entity.y, coreRad * 0.42, 0, Math.PI * 2);
          ctx.fill();
        }

        // Rotating Orbital Ticks / Telemetry Reticle around Core
        ctx.save();
        ctx.translate(entity.x, entity.y);
        ctx.rotate(time * 0.001 * (entity.type === 'quantum' ? 1 : -1));
        ctx.strokeStyle = entity.baseColor;
        ctx.lineWidth = 1.5;
        ctx.globalAlpha = 0.6;
        for (let a = 0; a < 4; a++) {
          ctx.beginPath();
          ctx.arc(0, 0, coreRad * 1.6, a * (Math.PI / 2) + 0.1, (a + 1) * (Math.PI / 2) - 0.5);
          ctx.stroke();
        }
        ctx.restore();
      };

      renderSingularityCore(entityA);
      renderSingularityCore(entityB);

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
  }, [particleDensity, speedMultiplier, gravityStrength, showOrbits, interactiveMouse, getParticleCount]);

  return (
    <div ref={containerRef} className="fixed inset-0 overflow-hidden pointer-events-none select-none z-0">
      {/* Primary Particle & Gravity Canvas */}
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full block" />

      {/* Subtle Cinematic Film Grain Texture */}
      <div 
        className="absolute inset-0 opacity-[0.035] mix-blend-overlay pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`
        }}
      />

      {/* Deep Vignette Shadow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_40%,rgba(4,5,8,0.7)_100%)] pointer-events-none" />
    </div>
  );
};

export default CosmicBackground;
