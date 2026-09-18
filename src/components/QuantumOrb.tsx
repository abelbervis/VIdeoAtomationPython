import React, { useEffect, useState } from 'react';

interface QuantumOrbProps {
  size?: number;
  mode?: 'talk' | 'idle' | 'close';
  speechEnergy?: number;
  speedMultiplier?: number;
  interactiveGaze?: { x: number; y: number };
}

export const QuantumOrb: React.FC<QuantumOrbProps> = ({
  size = 400,
  mode = 'talk',
  speechEnergy = 0.5,
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

  const rAuraOuter = canvasSize * 0.46 + (isTalk ? 12 * Math.sin(tau) : 5 * Math.sin(tau));
  const rAuraInner = canvasSize * 0.36 + (isTalk ? 8 * Math.sin(tau) : 4 * Math.sin(tau));

  // Gaze & Light Spot positions
  const spot1X = c - rSphere * (0.30 - interactiveGaze.x * 0.15);
  const spot1Y = c - rSphere * (0.26 - interactiveGaze.y * 0.15);
  const spot1Rx = rSphere * 0.52 + 3 * Math.sin(tau);
  const spot1Ry = rSphere * 0.48 + 2 * Math.cos(tau);

  const spot2X = c + rSphere * (0.28 + interactiveGaze.x * 0.12);
  const spot2Y = c + rSphere * (0.26 + interactiveGaze.y * 0.12);
  const spot2Rx = rSphere * 0.44 + 2 * Math.sin(tau);
  const spot2Ry = rSphere * 0.40 + 2 * Math.cos(tau);

  // Quantum Energy Rings
  const ring1R = rSphere + 16 + (isTalk ? 8 * Math.sin(tau) * energy : 4 * Math.sin(tau));
  const ring2R = rSphere + 36 + (isTalk ? 12 * Math.sin(tau + 1.2) : 6 * Math.sin(tau));
  const ring3R = rSphere + 58 + 6 * Math.cos(tau + 2.0);
  const orbitDashOffset = (tick * 140) % 200;

  return (
    <svg
      width={canvasSize}
      height={canvasSize}
      viewBox={`0 0 ${canvasSize} ${canvasSize}`}
      className="drop-shadow-2xl transition-all duration-300 select-none"
    >
      <defs>
        <filter id="qSpillBlur" x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="40" />
        </filter>
        <filter id="qAuraDeep" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="22" />
        </filter>
        <filter id="qCoreBlur" x="-25%" y="-25%" width="150%" height="150%">
          <feGaussianBlur stdDeviation="9" />
        </filter>
        <filter id="qRingGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="7" />
        </filter>

        <clipPath id="qSphereClip">
          <circle cx={c} cy={c} r={rSphere} />
        </clipPath>

        <radialGradient id="qAmbientSpill" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#f472b6" stopOpacity="0.90" />
          <stop offset="30%" stopColor="#a855f7" stopOpacity="0.65" />
          <stop offset="65%" stopColor="#3b82f6" stopOpacity="0.30" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.0" />
        </radialGradient>

        <radialGradient id="qOuterAura" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#a855f7" stopOpacity="0.90" />
          <stop offset="40%" stopColor="#7c3aed" stopOpacity="0.65" />
          <stop offset="75%" stopColor="#3b82f6" stopOpacity="0.30" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.0" />
        </radialGradient>

        <radialGradient id="qInnerAura" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#c084fc" stopOpacity="0.85" />
          <stop offset="50%" stopColor="#a855f7" stopOpacity="0.50" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.0" />
        </radialGradient>

        <radialGradient id="qSphereBody" cx="52%" cy="48%" r="62%">
          <stop offset="0%" stopColor="#00f0ff" />
          <stop offset="22%" stopColor="#0284c7" />
          <stop offset="48%" stopColor="#3b82f6" />
          <stop offset="72%" stopColor="#8a2be2" />
          <stop offset="88%" stopColor="#d946ef" />
          <stop offset="100%" stopColor="#1e0836" />
        </radialGradient>

        <radialGradient id="qPrimarySpot" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="1.0" />
          <stop offset="30%" stopColor="#f472b6" stopOpacity="0.90" />
          <stop offset="65%" stopColor="#c084fc" stopOpacity="0.55" />
          <stop offset="100%" stopColor="#8a2be2" stopOpacity="0.0" />
        </radialGradient>

        <radialGradient id="qSecondarySpot" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#00f0ff" stopOpacity="0.85" />
          <stop offset="45%" stopColor="#0284c7" stopOpacity="0.55" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.0" />
        </radialGradient>
      </defs>

      {/* 0. Ambient Illumination */}
      <circle cx={c} cy={c} r={canvasSize * 0.44} fill="url(#qAmbientSpill)" filter="url(#qSpillBlur)" />

      {/* 1. Atmospheric Bloom */}
      <circle cx={c} cy={c} r={rAuraOuter} fill="url(#qOuterAura)" filter="url(#qAuraDeep)" />
      <circle cx={c} cy={c} r={rAuraInner} fill="url(#qInnerAura)" filter="url(#qAuraDeep)" />

      {/* 2. Quantum Acoustic Shockwave Rings */}
      <g>
        {/* Ring 3: Rotating Kinetic Energy Halo */}
        <circle
          cx={c}
          cy={c}
          r={ring3R}
          fill="none"
          stroke="#c084fc"
          strokeWidth="2.2"
          strokeDasharray="18 22 45 22"
          strokeDashoffset={orbitDashOffset}
          opacity="0.75"
        />

        {/* Ring 2: Expanding Outer Resonance Wave */}
        <circle
          cx={c}
          cy={c}
          r={ring2R + 6}
          fill="none"
          stroke="#a855f7"
          strokeWidth="5.0"
          opacity="0.60"
          filter="url(#qRingGlow)"
        />
        <circle
          cx={c}
          cy={c}
          r={ring2R}
          fill="none"
          stroke="#c084fc"
          strokeWidth="1.8"
          opacity="0.80"
        />

        {/* Ring 1: High-Power Radiant Core Ring */}
        <circle
          cx={c}
          cy={c}
          r={ring1R + 6}
          fill="none"
          stroke="#a855f7"
          strokeWidth="7.5"
          opacity="0.85"
          filter="url(#qRingGlow)"
        />
        <circle
          cx={c}
          cy={c}
          r={ring1R}
          fill="none"
          stroke="#c084fc"
          strokeWidth="2.6"
          opacity="0.98"
        />
        <circle
          cx={c}
          cy={c}
          r={ring1R - 1}
          fill="none"
          stroke="#ffffff"
          strokeWidth="1.0"
          opacity="0.80"
        />
      </g>

      {/* 3. Sphere Body */}
      <circle cx={c} cy={c} r={rSphere} fill="url(#qSphereBody)" />

      {/* 4. Multi-Spectral Interior Light Layers */}
      <g clipPath="url(#qSphereClip)">
        <ellipse
          cx={spot2X}
          cy={spot2Y}
          rx={spot2Rx}
          ry={spot2Ry}
          fill="url(#qSecondarySpot)"
          filter="url(#qCoreBlur)"
        />
        <ellipse
          cx={spot1X}
          cy={spot1Y}
          rx={spot1Rx}
          ry={spot1Ry}
          fill="url(#qPrimarySpot)"
          filter="url(#qCoreBlur)"
        />
        <circle
          cx={spot1X}
          cy={spot1Y}
          r={spot1Rx * 0.45}
          fill="#ffffff"
          opacity="0.95"
          filter="url(#qCoreBlur)"
        />
        <circle
          cx={c}
          cy={c}
          r={rSphere - 3}
          fill="none"
          stroke="#d946ef"
          strokeWidth="3.0"
          opacity="0.50"
          filter="url(#qCoreBlur)"
        />
      </g>

      {/* 5. Inner Edge Light */}
      <circle
        cx={c}
        cy={c}
        r={rSphere - 2}
        fill="none"
        stroke="#a855f7"
        strokeWidth="2.5"
        opacity="0.70"
      />
    </svg>
  );
};
