import React, { useEffect, useState } from 'react';

interface SolarOrbProps {
  size?: number;
  mode?: 'talk' | 'idle' | 'close';
  speechEnergy?: number;
  showQuantumRing?: boolean;
  showHeliosphericBelts?: boolean;
  showInternalSwirls?: boolean;
  showProminences?: boolean;
  haloDiffusion?: 'soft' | 'ultra' | 'deep';
  speedMultiplier?: number;
  interactiveGaze?: { x: number; y: number };
}

export const SolarOrb: React.FC<SolarOrbProps> = ({
  size = 400,
  mode = 'talk',
  speechEnergy = 0.5,
  showQuantumRing = true,
  showHeliosphericBelts = true,
  showInternalSwirls = true,
  showProminences = true,
  haloDiffusion = 'ultra',
  speedMultiplier = 1.0,
  interactiveGaze = { x: 0, y: 0 },
}) => {
  const [tick, setTick] = useState(0);

  useEffect(() => {
    let animId: number;
    let startTime: number | null = null;

    const animate = (time: number) => {
      if (!startTime) startTime = time;
      const elapsed = (time - startTime) / 1000;
      setTick(elapsed * speedMultiplier);
      animId = requestAnimationFrame(animate);
    };

    animId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animId);
  }, [speedMultiplier]);

  const tau = tick * 2.2;
  const isTalk = mode === 'talk' || mode === 'close';
  const energy = isTalk ? Math.max(0.2, speechEnergy) : 0.05;

  const canvasSize = size;
  const c = canvasSize / 2;
  const rSphereBase = canvasSize * 0.27;
  const rSphere = rSphereBase + (isTalk ? 6 * Math.sin(tau) * energy : 3 * Math.sin(tau));

  // Outer Halos
  const rAuraOuter = canvasSize * 0.46 + (isTalk ? 14 * Math.sin(tau) : 6 * Math.sin(tau));
  const rAuraInner = canvasSize * 0.36 + (isTalk ? 10 * Math.sin(tau) : 4 * Math.sin(tau));

  // Quantum Orbital Ring
  const quantumRingR = rSphere + 38 + 6 * Math.sin(tau * 1.2) * (1 + energy * 0.5);
  const orbitDashOffset = (tick * 120) % 200;

  // Heliospheric Belts
  const belt1Rx = rSphere + 48 + 5 * Math.sin(tau);
  const belt1Ry = (rSphere + 48) * 0.38 + 3 * Math.sin(tau);
  const belt2Rx = rSphere + 72 + 6 * Math.cos(tau);
  const belt2Ry = (rSphere + 72) * 0.32 + 3 * Math.cos(tau);

  // Swirling Internal Motion inside sphere
  const swirl1X = c + rSphere * (0.24 * Math.sin(tau + 0.4) - 0.08 + interactiveGaze.x * 0.15);
  const swirl1Y = c + rSphere * (0.20 * Math.cos(tau + 0.2) - 0.10 + interactiveGaze.y * 0.15);
  const swirl1Rx = rSphere * 0.46 + 4 * Math.sin(tau * 2);
  const swirl1Ry = rSphere * 0.40 + 3 * Math.cos(tau * 2);

  const swirl2X = c + rSphere * (-0.26 * Math.cos(tau * 1.3) + 0.10 + interactiveGaze.x * 0.12);
  const swirl2Y = c + rSphere * (0.22 * Math.sin(tau * 1.3 + 0.8) + 0.08 + interactiveGaze.y * 0.12);
  const swirl2Rx = rSphere * 0.42 + 3 * Math.cos(tau * 1.5);
  const swirl2Ry = rSphere * 0.36 + 2 * Math.sin(tau * 1.5);

  const swirl3X = c + rSphere * (0.30 * Math.cos(tau * 0.9 + 1.8));
  const swirl3Y = c + rSphere * (0.26 * Math.sin(tau * 0.9 + 1.8));
  const swirl3Rx = rSphere * 0.36 + 2 * Math.sin(tau * 1.8);
  const swirl3Ry = rSphere * 0.30 + 2 * Math.cos(tau * 1.8);

  // Internal Prominence Loop Arcs
  const pDx = rSphere * 0.18 * Math.sin(tau);
  const pDy = rSphere * 0.14 * Math.cos(tau);
  const arc1Path = `M ${c - rSphere * 0.42} ${c + rSphere * 0.08} Q ${c + pDx} ${c - rSphere * 0.38 + pDy} ${c + rSphere * 0.42} ${c + rSphere * 0.12}`;
  const arc2Path = `M ${c - rSphere * 0.32} ${c - rSphere * 0.22} Q ${c - pDx} ${c + rSphere * 0.36 - pDy} ${c + rSphere * 0.38} ${c - rSphere * 0.14}`;

  // Voice White Fusion Mouth Aperture
  const mouthW = rSphere * (0.32 + 0.20 * energy + 0.04 * Math.sin(tau));
  const mouthH = rSphere * (0.10 + 0.30 * energy + 0.06 * Math.abs(Math.cos(tau * 2)));
  const mouthGlowW = mouthW * 1.65;
  const mouthGlowH = mouthH * 1.55;

  const stdDevSpill = haloDiffusion === 'deep' ? 64 : haloDiffusion === 'ultra' ? 42 : 28;
  const stdDevDeep = haloDiffusion === 'deep' ? 36 : haloDiffusion === 'ultra' ? 24 : 16;

  return (
    <svg
      width={canvasSize}
      height={canvasSize}
      viewBox={`0 0 ${canvasSize} ${canvasSize}`}
      className="drop-shadow-2xl transition-all duration-300 select-none"
    >
      <defs>
        {/* Halo Diffusion Filters */}
        <filter id="solarHyperSoft" x="-80%" y="-80%" width="260%" height="260%">
          <feGaussianBlur stdDeviation={stdDevSpill} />
        </filter>
        <filter id="solarAuraDeep" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation={stdDevDeep} />
        </filter>
        <filter id="solarAuraSoft" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="12" />
        </filter>
        <filter id="solarCoreBlur" x="-25%" y="-25%" width="150%" height="150%">
          <feGaussianBlur stdDeviation="8" />
        </filter>
        <filter id="solarRingGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="9" />
        </filter>

        <clipPath id="solarSphereClip">
          <circle cx={c} cy={c} r={rSphere} />
        </clipPath>

        {/* Multi-Stop Realistic Halo Gradients */}
        <radialGradient id="solarAmbientSpill" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#ff80ab" stopOpacity="0.95" />
          <stop offset="18%" stopColor="#ffea00" stopOpacity="0.80" />
          <stop offset="42%" stopColor="#ff1744" stopOpacity="0.58" />
          <stop offset="68%" stop-color="#d50000" stopOpacity="0.32" />
          <stop offset="88%" stopColor="#ff6d00" stopOpacity="0.12" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.0" />
        </radialGradient>

        <radialGradient id="solarOuterAura" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#ff1744" stopOpacity="0.95" />
          <stop offset="28%" stopColor="#ff9100" stopOpacity="0.72" />
          <stop offset="55%" stopColor="#d50000" stopOpacity="0.48" />
          <stop offset="80%" stopColor="#ff6d00" stopOpacity="0.22" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.0" />
        </radialGradient>

        <radialGradient id="solarInnerAura" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#ff80ab" stopOpacity="0.95" />
          <stop offset="35%" stopColor="#ffea00" stopOpacity="0.70" />
          <stop offset="70%" stopColor="#ff1744" stopOpacity="0.45" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.0" />
        </radialGradient>

        {/* 8-Stop Volumetric Solar Body Gradient */}
        <radialGradient id="solarSphereBody" cx="50%" cy="50%" r="55%">
          <stop offset="0%" stopColor="#ffffff" />
          <stop offset="10%" stopColor="#ffea00" />
          <stop offset="26%" stopColor="#ff9100" />
          <stop offset="48%" stopColor="#ff3d00" />
          <stop offset="68%" stopColor="#d50000" />
          <stop offset="85%" stopColor="#c2185b" />
          <stop offset="95%" stopColor="#2a0010" />
          <stop offset="100%" stopColor="#120005" />
        </radialGradient>

        {/* Internal Granulation Flares */}
        <radialGradient id="solarSwirl1" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.98" />
          <stop offset="30%" stopColor="#ffea00" stopOpacity="0.85" />
          <stop offset="65%" stopColor="#ff9100" stopOpacity="0.45" />
          <stop offset="100%" stopColor="#ff3d00" stopOpacity="0.0" />
        </radialGradient>

        <radialGradient id="solarSwirl2" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#ffea00" stopOpacity="0.92" />
          <stop offset="40%" stopColor="#ff3d00" stopOpacity="0.65" />
          <stop offset="80%" stopColor="#d50000" stopOpacity="0.25" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.0" />
        </radialGradient>

        <radialGradient id="solarMouthHalo" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="1.0" />
          <stop offset="35%" stopColor="#ff80ab" stopOpacity="0.92" />
          <stop offset="70%" stopColor="#ff4081" stopOpacity="0.55" />
          <stop offset="100%" stopColor="#ff9100" stopOpacity="0.0" />
        </radialGradient>
      </defs>

      {/* 0. Environmental Atmospheric Ambient Illumination */}
      <circle cx={c} cy={c} r={canvasSize * 0.48} fill="url(#solarAmbientSpill)" filter="url(#solarHyperSoft)" opacity="0.85" />
      <circle cx={c} cy={c} r={canvasSize * 0.42} fill="url(#solarAmbientSpill)" filter="url(#solarAuraDeep)" />

      {/* 1. Coronal Atmospheric Multi-Layered Bloom */}
      <circle cx={c} cy={c} r={rAuraOuter} fill="url(#solarOuterAura)" filter="url(#solarAuraDeep)" />
      <circle cx={c} cy={c} r={rAuraInner} fill="url(#solarInnerAura)" filter="url(#solarAuraSoft)" />

      {/* 2. QUANTUM-STYLE OUTER KINETIC ORBITAL RING & TILTED BELTS */}
      {showQuantumRing && (
        <g>
          {/* Glowing Quantum Ring Background Aura */}
          <circle
            cx={c}
            cy={c}
            r={quantumRingR + 6}
            fill="none"
            stroke="#ff1744"
            strokeWidth="6.0"
            opacity="0.60"
            filter="url(#solarRingGlow)"
          />
          {/* Rotating Kinetic Arc */}
          <circle
            cx={c}
            cy={c}
            r={quantumRingR}
            fill="none"
            stroke="#ffd54f"
            strokeWidth="2.8"
            strokeDasharray="28 14 56 14"
            strokeDashoffset={-orbitDashOffset}
            opacity="0.95"
          />
          <circle
            cx={c}
            cy={c}
            r={quantumRingR - 1}
            fill="none"
            stroke="#ffffff"
            strokeWidth="1.2"
            opacity="0.85"
          />
        </g>
      )}

      {showHeliosphericBelts && (
        <g>
          {/* Tilted Heliospheric Belt 1 (-22deg tilt) */}
          <ellipse
            cx={c}
            cy={c}
            rx={belt1Rx}
            ry={belt1Ry}
            transform={`rotate(-22 ${c} ${c})`}
            fill="none"
            stroke="#ff1744"
            strokeWidth="5.0"
            opacity="0.50"
            filter="url(#solarRingGlow)"
          />
          <ellipse
            cx={c}
            cy={c}
            rx={belt1Rx}
            ry={belt1Ry}
            transform={`rotate(-22 ${c} ${c})`}
            fill="none"
            stroke="#ffd54f"
            strokeWidth="2.2"
            strokeDasharray="32 16 48 16"
            strokeDashoffset={orbitDashOffset}
            opacity="0.90"
          />

          {/* Magnetic Coronal Loop 2 (+32deg tilt) */}
          <ellipse
            cx={c}
            cy={c}
            rx={belt2Rx}
            ry={belt2Ry}
            transform={`rotate(32 ${c} ${c})`}
            fill="none"
            stroke="#ff80ab"
            strokeWidth="1.8"
            strokeDasharray="24 20 40 20"
            strokeDashoffset={-orbitDashOffset * 1.3}
            opacity="0.75"
          />
        </g>
      )}

      {/* 3. Living Solar Sphere Body */}
      <circle cx={c} cy={c} r={rSphere} fill="url(#solarSphereBody)" />

      {/* 4. INTERNAL MOTION & VOICE FUSION MOUTH */}
      <g clipPath="url(#solarSphereClip)">
        {showInternalSwirls && (
          <g>
            <ellipse
              cx={swirl1X}
              cy={swirl1Y}
              rx={swirl1Rx}
              ry={swirl1Ry}
              fill="url(#solarSwirl1)"
              filter="url(#solarCoreBlur)"
            />
            <ellipse
              cx={swirl2X}
              cy={swirl2Y}
              rx={swirl2Rx}
              ry={swirl2Ry}
              fill="url(#solarSwirl2)"
              filter="url(#solarCoreBlur)"
            />
            <ellipse
              cx={swirl3X}
              cy={swirl3Y}
              rx={swirl3Rx}
              ry={swirl3Ry}
              fill="url(#solarSwirl1)"
              opacity="0.65"
              filter="url(#solarCoreBlur)"
            />
          </g>
        )}

        {showProminences && (
          <g>
            <path
              d={arc1Path}
              fill="none"
              stroke="#ffea00"
              strokeWidth="3.2"
              opacity="0.60"
              filter="url(#solarCoreBlur)"
            />
            <path
              d={arc2Path}
              fill="none"
              stroke="#ff80ab"
              strokeWidth="2.6"
              opacity="0.55"
              filter="url(#solarCoreBlur)"
            />
          </g>
        )}

        {/* White Fusion Voice Mouth Aperture */}
        <g>
          <ellipse
            cx={c}
            cy={c}
            rx={mouthW * 2.2}
            ry={mouthH * 1.2}
            fill="#ff80ab"
            opacity={0.30 + energy * 0.50}
            filter="url(#solarCoreBlur)"
          />
          <ellipse
            cx={c}
            cy={c}
            rx={mouthGlowW}
            ry={mouthGlowH}
            fill="url(#solarMouthHalo)"
            filter="url(#solarCoreBlur)"
          />
          <ellipse
            cx={c}
            cy={c}
            rx={mouthW}
            ry={mouthH}
            fill="#ffffff"
            opacity="0.98"
            filter="url(#solarCoreBlur)"
          />
          <ellipse
            cx={c}
            cy={c}
            rx={mouthW * 0.65}
            ry={mouthH * 0.55}
            fill="#ffffff"
            opacity="1.0"
          />
        </g>

        {/* Subsurface Corona Rim Accent */}
        <circle
          cx={c}
          cy={c}
          r={rSphere - 3}
          fill="none"
          stroke="#ff4081"
          strokeWidth="3.2"
          opacity="0.55"
          filter="url(#solarCoreBlur)"
        />
      </g>

      {/* 5. Concentric Inner Star Edge Highlight */}
      <circle
        cx={c}
        cy={c}
        r={rSphere - 2}
        fill="none"
        stroke="#ff1744"
        strokeWidth="2.2"
        opacity="0.80"
      />
    </svg>
  );
};
