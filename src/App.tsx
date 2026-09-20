import React, { useState } from 'react';
import { CosmicBackground, FocusMode } from './components/CosmicBackground';

export default function App() {
  const [focusMode, setFocusMode] = useState<FocusMode>('dual');

  return (
    <main id="app-root" className="relative min-h-screen w-full bg-[#06070B] overflow-hidden select-none">
      {/* Pure Cosmic Entities & Dual Gravity Particle Background with Interactive Focus Transition */}
      <CosmicBackground 
        focusMode={focusMode}
        onSelectFocus={setFocusMode}
        particleDensity="medium"
        speedMultiplier={1}
        gravityStrength={1}
        showOrbits={true}
        interactiveMouse={true}
      />
    </main>
  );
}
