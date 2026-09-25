import React from 'react';
import { CosmicBackground } from './components/CosmicBackground';

export default function App() {
  return (
    <main id="app-root" className="relative min-h-screen w-full bg-[#06070B] overflow-hidden select-none">
      {/* Pure Cosmic Entities & Dual Gravity Particle Background */}
      <CosmicBackground 
        particleDensity="medium"
        speedMultiplier={1}
        gravityStrength={1}
        showTelemetry={false}
        showOrbits={true}
        interactiveMouse={true}
      />
    </main>
  );
}
