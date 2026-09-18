import React, { useState } from 'react';
import {
  Sun,
  Atom,
  Sparkles,
  Volume2,
  Play,
  RotateCcw,
  Layers,
  CircleDot,
  Sliders,
  Download,
  Flame,
  Zap,
  Eye,
  CheckCircle2,
  Info
} from 'lucide-react';
import { SolarOrb } from './components/SolarOrb';
import { QuantumOrb } from './components/QuantumOrb';

export default function App() {
  const [viewMode, setViewMode] = useState<'dual' | 'solar' | 'quantum'>('solar');
  const [orbMode, setOrbMode] = useState<'talk' | 'idle' | 'close'>('talk');
  const [speechEnergy, setSpeechEnergy] = useState<number>(0.75);
  const [isAudioActive, setIsAudioActive] = useState<boolean>(true);
  const [speedMultiplier, setSpeedMultiplier] = useState<number>(1.0);

  // Solar Customizations
  const [showQuantumRing, setShowQuantumRing] = useState<boolean>(true);
  const [showHeliosphericBelts, setShowHeliosphericBelts] = useState<boolean>(true);
  const [showInternalSwirls, setShowInternalSwirls] = useState<boolean>(true);
  const [showProminences, setShowProminences] = useState<boolean>(true);
  const [haloDiffusion, setHaloDiffusion] = useState<'soft' | 'ultra' | 'deep'>('ultra');

  // Interactive Mouse Gaze tracking
  const [mouseGaze, setMouseGaze] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
    setMouseGaze({ x, y });
  };

  const handleResetGaze = () => {
    setMouseGaze({ x: 0, y: 0 });
  };

  const triggerAudioPulse = () => {
    setIsAudioActive(true);
    let energyVal = 1.0;
    setSpeechEnergy(1.0);
    const interval = setInterval(() => {
      energyVal *= 0.85;
      if (energyVal < 0.2) {
        clearInterval(interval);
        setSpeechEnergy(0.75);
      } else {
        setSpeechEnergy(energyVal);
      }
    }, 100);
  };

  const downloadSvg = (type: 'solar' | 'quantum') => {
    const svgElement = document.querySelector(type === 'solar' ? 'svg' : 'svg');
    if (!svgElement) return;
    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svgElement);
    const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `orb_${type}_enhanced.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-[#080612] text-slate-100 font-sans selection:bg-amber-500/30 selection:text-amber-200 flex flex-col">
      {/* Background Subtle Nebula Glows */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -left-40 w-[600px] h-[600px] bg-amber-600/10 rounded-full blur-[140px]" />
        <div className="absolute top-1/2 -right-40 w-[600px] h-[600px] bg-rose-600/10 rounded-full blur-[140px]" />
        <div className="absolute -bottom-40 left-1/3 w-[600px] h-[600px] bg-cyan-600/10 rounded-full blur-[140px]" />
      </div>

      {/* HEADER */}
      <header className="relative z-10 border-b border-white/10 bg-[#0d091f]/80 backdrop-blur-md px-6 py-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-orange-500 to-rose-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
            <Sun className="w-6 h-6 text-white animate-spin-slow" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-amber-200 via-orange-300 to-rose-200 bg-clip-text text-transparent">
              Cosmic Orbs Studio
            </h1>
            <p className="text-xs text-slate-400">
              Enhanced Solar Orb 2.0 & Quantum AI Presenter Visualizer
            </p>
          </div>
        </div>

        {/* View Mode Selector */}
        <div className="flex items-center bg-white/5 p-1 rounded-xl border border-white/10">
          <button
            onClick={() => setViewMode('solar')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'solar'
                ? 'bg-gradient-to-r from-amber-500 to-rose-600 text-white shadow-md shadow-amber-500/25'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Sun className="w-3.5 h-3.5" />
            Solar Orb 2.0
          </button>

          <button
            onClick={() => setViewMode('dual')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'dual'
                ? 'bg-gradient-to-r from-amber-500 via-purple-500 to-cyan-500 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Dual Comparison
          </button>

          <button
            onClick={() => setViewMode('quantum')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              viewMode === 'quantum'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/25'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Atom className="w-3.5 h-3.5" />
            Quantum Orb
          </button>
        </div>
      </header>

      {/* MAIN CONTENT AREA */}
      <main className="relative z-10 flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 max-w-7xl mx-auto w-full">
        {/* LEFT / CENTER: STAGE AREA (8 COLS) */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          {/* TOP CONTROLS CARD */}
          <div className="bg-[#120d2b]/80 border border-white/10 rounded-2xl p-4 backdrop-blur-md flex flex-wrap items-center justify-between gap-4">
            {/* Mode Switcher */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center gap-1">
                <Eye className="w-3.5 h-3.5 text-amber-400" />
                State:
              </span>
              <div className="flex items-center bg-black/40 p-1 rounded-lg border border-white/5">
                <button
                  onClick={() => setOrbMode('talk')}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                    orbMode === 'talk'
                      ? 'bg-amber-500 text-black font-bold shadow'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Speaking
                </button>
                <button
                  onClick={() => setOrbMode('idle')}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                    orbMode === 'idle'
                      ? 'bg-amber-500 text-black font-bold shadow'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Listening
                </button>
                <button
                  onClick={() => setOrbMode('close')}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                    orbMode === 'close'
                      ? 'bg-amber-500 text-black font-bold shadow'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Close-Up
                </button>
              </div>
            </div>

            {/* Audio Pulse Reactivity */}
            <div className="flex items-center gap-3">
              <button
                onClick={triggerAudioPulse}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/30 hover:bg-rose-500/30 transition-all text-xs font-semibold"
              >
                <Volume2 className="w-3.5 h-3.5 animate-pulse" />
                Voice Pulse
              </button>

              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Energy:</span>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.05"
                  value={speechEnergy}
                  onChange={(e) => setSpeechEnergy(parseFloat(e.target.value))}
                  className="w-24 accent-amber-500 h-1.5 bg-slate-700 rounded-lg cursor-pointer"
                />
              </div>
            </div>

            {/* Speed Control */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Speed:</span>
              <select
                value={speedMultiplier}
                onChange={(e) => setSpeedMultiplier(parseFloat(e.target.value))}
                className="bg-black/50 border border-white/10 rounded-lg text-xs text-slate-200 px-2 py-1 outline-none"
              >
                <option value={0.5}>0.5x (Slow)</option>
                <option value={1.0}>1.0x (Normal)</option>
                <option value={1.5}>1.5x (Dynamic)</option>
                <option value={2.0}>2.0x (Hyper)</option>
              </select>
            </div>
          </div>

          {/* ORB RENDER STAGE CANVAS */}
          <div
            onMouseMove={handleMouseMove}
            onMouseLeave={handleResetGaze}
            className="relative bg-gradient-to-b from-[#0e0a24] to-[#080516] border border-white/10 rounded-3xl p-8 min-h-[480px] flex items-center justify-center overflow-hidden shadow-2xl group"
          >
            {/* Subtle Grid Overlay */}
            <div className="absolute inset-0 bg-[radial-gradient(#ffffff_1px,transparent_1px)] [background-size:24px_24px] opacity-5 pointer-events-none" />

            {/* Stage Light Spotlight */}
            <div className="absolute inset-0 bg-radial from-amber-500/5 via-transparent to-transparent pointer-events-none" />

            {/* VIEW MODE: SOLAR 2.0 SPOTLIGHT */}
            {viewMode === 'solar' && (
              <div className="flex flex-col items-center justify-center relative">
                <SolarOrb
                  size={420}
                  mode={orbMode}
                  speechEnergy={speechEnergy}
                  showQuantumRing={showQuantumRing}
                  showHeliosphericBelts={showHeliosphericBelts}
                  showInternalSwirls={showInternalSwirls}
                  showProminences={showProminences}
                  haloDiffusion={haloDiffusion}
                  speedMultiplier={speedMultiplier}
                  interactiveGaze={mouseGaze}
                />

                {/* Badge Label */}
                <div className="mt-4 flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 backdrop-blur-md">
                  <Flame className="w-4 h-4 text-amber-400 animate-bounce" />
                  <span className="text-xs font-bold text-amber-300 uppercase tracking-widest">
                    SOLAR 2.0 • IA ASTROFÍSICA
                  </span>
                </div>
              </div>
            )}

            {/* VIEW MODE: DUAL COMPARISON */}
            {viewMode === 'dual' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full items-center justify-items-center">
                {/* QUANTUM ORB */}
                <div className="flex flex-col items-center group/q">
                  <div className="transition-transform duration-300 group-hover/q:scale-105">
                    <QuantumOrb
                      size={320}
                      mode={orbMode}
                      speechEnergy={speechEnergy}
                      speedMultiplier={speedMultiplier}
                      interactiveGaze={mouseGaze}
                    />
                  </div>
                  <div className="mt-2 flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30">
                    <Atom className="w-3.5 h-3.5 text-cyan-400" />
                    <span className="text-xs font-bold text-cyan-300 tracking-wider">
                      QUANTUM (Left Host)
                    </span>
                  </div>
                </div>

                {/* SOLAR ORB 2.0 */}
                <div className="flex flex-col items-center group/s">
                  <div className="transition-transform duration-300 group-hover/s:scale-105">
                    <SolarOrb
                      size={320}
                      mode={orbMode}
                      speechEnergy={speechEnergy}
                      showQuantumRing={showQuantumRing}
                      showHeliosphericBelts={showHeliosphericBelts}
                      showInternalSwirls={showInternalSwirls}
                      showProminences={showProminences}
                      haloDiffusion={haloDiffusion}
                      speedMultiplier={speedMultiplier}
                      interactiveGaze={mouseGaze}
                    />
                  </div>
                  <div className="mt-2 flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30">
                    <Sun className="w-3.5 h-3.5 text-amber-400" />
                    <span className="text-xs font-bold text-amber-300 tracking-wider">
                      SOLAR 2.0 (Right Host)
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* VIEW MODE: QUANTUM SPOTLIGHT */}
            {viewMode === 'quantum' && (
              <div className="flex flex-col items-center justify-center relative">
                <QuantumOrb
                  size={420}
                  mode={orbMode}
                  speechEnergy={speechEnergy}
                  speedMultiplier={speedMultiplier}
                  interactiveGaze={mouseGaze}
                />
                <div className="mt-4 flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 backdrop-blur-md">
                  <Atom className="w-4 h-4 text-cyan-400 animate-spin-slow" />
                  <span className="text-xs font-bold text-cyan-300 uppercase tracking-widest">
                    QUANTUM • IA CUÁNTICA
                  </span>
                </div>
              </div>
            )}

            {/* Hover Gaze Indicator */}
            <div className="absolute bottom-3 right-4 text-[10px] text-slate-500 font-mono">
              Gaze Position: [{mouseGaze.x.toFixed(2)}, {mouseGaze.y.toFixed(2)}]
            </div>
          </div>

          {/* USER IMPROVEMENTS SUMMARY BADGES (Directly addressing prompt requirements) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-[#120d2b]/60 border border-amber-500/20 rounded-2xl p-4 flex flex-col gap-1.5">
              <div className="flex items-center gap-2 text-amber-400 font-semibold text-sm">
                <Sparkles className="w-4 h-4" />
                Movimiento Interno
              </div>
              <p className="text-xs text-slate-300">
                Granulación de plasma fluido, nodos de erupción giratorios y arcos magnéticos en movimiento dinámico continuo.
              </p>
            </div>

            <div className="bg-[#120d2b]/60 border border-rose-500/20 rounded-2xl p-4 flex flex-col gap-1.5">
              <div className="flex items-center gap-2 text-rose-400 font-semibold text-sm">
                <Layers className="w-4 h-4" />
                Degradados Realistas
              </div>
              <p className="text-xs text-slate-300">
                Halos fotorrealistas con degradados multi-stop (8 paradas de color) y difuminado atmosférico ultra-suave.
              </p>
            </div>

            <div className="bg-[#120d2b]/60 border border-cyan-500/20 rounded-2xl p-4 flex flex-col gap-1.5">
              <div className="flex items-center gap-2 text-cyan-400 font-semibold text-sm">
                <CircleDot className="w-4 h-4" />
                Aro Cuántico Solar
              </div>
              <p className="text-xs text-slate-300">
                Anillo de energía orbital tipo Quantum fusionado en oro solar y ámbar cinético alrededor del cuerpo estelar.
              </p>
            </div>
          </div>
        </div>

        {/* RIGHT: CUSTOMIZATION & FEATURE INSPECTOR PANEL (4 COLS) */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <div className="bg-[#120d2b]/90 border border-white/10 rounded-2xl p-5 flex flex-col gap-5 backdrop-blur-md">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2 uppercase tracking-wide">
                <Sliders className="w-4 h-4 text-amber-400" />
                Detalles del Orbe Solar
              </h2>
              <span className="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-md font-mono border border-amber-500/30">
                v2.0 Enhanced
              </span>
            </div>

            {/* TOGGLE 1: QUANTUM ORBITAL RING */}
            <div className="flex flex-col gap-2 bg-black/30 p-3 rounded-xl border border-white/5">
              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-xs font-semibold text-slate-200 flex items-center gap-2">
                  <Zap className="w-4 h-4 text-amber-400" />
                  Aro Cuántico Orbital
                </span>
                <input
                  type="checkbox"
                  checked={showQuantumRing}
                  onChange={(e) => setShowQuantumRing(e.target.checked)}
                  className="w-4 h-4 accent-amber-500 cursor-pointer rounded"
                />
              </label>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Anillo cinético de energía exterior calcado del orbe Quantum pero armonizado con la paleta estelar.
              </p>
            </div>

            {/* TOGGLE 2: HELIOSPHERIC BELTS */}
            <div className="flex flex-col gap-2 bg-black/30 p-3 rounded-xl border border-white/5">
              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-xs font-semibold text-slate-200 flex items-center gap-2">
                  <CircleDot className="w-4 h-4 text-rose-400" />
                  Cinturones Heliosféricos 3D
                </span>
                <input
                  type="checkbox"
                  checked={showHeliosphericBelts}
                  onChange={(e) => setShowHeliosphericBelts(e.target.checked)}
                  className="w-4 h-4 accent-rose-500 cursor-pointer rounded"
                />
              </label>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Bucles elípticos inclinados (-22° y +32°) que representan el campo magnético del Sol.
              </p>
            </div>

            {/* TOGGLE 3: INTERNAL SWIRL MOTION */}
            <div className="flex flex-col gap-2 bg-black/30 p-3 rounded-xl border border-white/5">
              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-xs font-semibold text-slate-200 flex items-center gap-2">
                  <Flame className="w-4 h-4 text-orange-400" />
                  Movimiento Interno de Plasma
                </span>
                <input
                  type="checkbox"
                  checked={showInternalSwirls}
                  onChange={(e) => setShowInternalSwirls(e.target.checked)}
                  className="w-4 h-4 accent-orange-500 cursor-pointer rounded"
                />
              </label>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Nodos de granulación solar y manchas incandescentes girando en órbita tridimensional fluida.
              </p>
            </div>

            {/* TOGGLE 4: PROMINENCE ARCS */}
            <div className="flex flex-col gap-2 bg-black/30 p-3 rounded-xl border border-white/5">
              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-xs font-semibold text-slate-200 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  Arcos de Prominencia Solar
                </span>
                <input
                  type="checkbox"
                  checked={showProminences}
                  onChange={(e) => setShowProminences(e.target.checked)}
                  className="w-4 h-4 accent-amber-500 cursor-pointer rounded"
                />
              </label>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Filamentos magnéticos curvados que ondean suavemente en el interior del orbe.
              </p>
            </div>

            {/* SELECTOR: HALO DIFFUSION SMOOTHNESS */}
            <div className="flex flex-col gap-2 bg-black/30 p-3 rounded-xl border border-white/5">
              <span className="text-xs font-semibold text-slate-200 flex items-center gap-2">
                <Layers className="w-4 h-4 text-purple-400" />
                Difuminado de Halos
              </span>
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => setHaloDiffusion('soft')}
                  className={`py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    haloDiffusion === 'soft'
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/50'
                      : 'bg-black/40 text-slate-400 border-white/5 hover:bg-white/5'
                  }`}
                >
                  Suave
                </button>
                <button
                  onClick={() => setHaloDiffusion('ultra')}
                  className={`py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    haloDiffusion === 'ultra'
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/50'
                      : 'bg-black/40 text-slate-400 border-white/5 hover:bg-white/5'
                  }`}
                >
                  Ultra Realista
                </button>
                <button
                  onClick={() => setHaloDiffusion('deep')}
                  className={`py-1.5 rounded-lg text-xs font-medium border transition-all ${
                    haloDiffusion === 'deep'
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/50'
                      : 'bg-black/40 text-slate-400 border-white/5 hover:bg-white/5'
                  }`}
                >
                  Profundo
                </button>
              </div>
            </div>

            {/* DOWNLOAD SVG BUTTON */}
            <button
              onClick={() => downloadSvg(viewMode === 'quantum' ? 'quantum' : 'solar')}
              className="mt-2 w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-gradient-to-r from-amber-500 via-orange-500 to-rose-600 text-black font-bold text-xs tracking-wider uppercase hover:brightness-110 transition-all shadow-lg shadow-amber-500/20"
            >
              <Download className="w-4 h-4" />
              Descargar SVG Orbe Solar
            </button>
          </div>

          {/* COLOR PALETTE SPECIFICATION CARD */}
          <div className="bg-[#120d2b]/70 border border-white/10 rounded-2xl p-4 flex flex-col gap-3">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-amber-400" />
              Especificación Paleta Solar Gold 2.0
            </h3>
            <div className="grid grid-cols-6 gap-2">
              <div className="flex flex-col items-center gap-1">
                <div className="w-full h-7 rounded-lg bg-[#ffea00] border border-white/20" />
                <span className="text-[9px] font-mono text-slate-400">#ffea00</span>
              </div>
              <div className="flex flex-col items-center gap-1">
                <div className="w-full h-7 rounded-lg bg-[#ff9100] border border-white/20" />
                <span className="text-[9px] font-mono text-slate-400">#ff9100</span>
              </div>
              <div className="flex flex-col items-center gap-1">
                <div className="w-full h-7 rounded-lg bg-[#ff3d00] border border-white/20" />
                <span className="text-[9px] font-mono text-slate-400">#ff3d00</span>
              </div>
              <div className="flex flex-col items-center gap-1">
                <div className="w-full h-7 rounded-lg bg-[#d50000] border border-white/20" />
                <span className="text-[9px] font-mono text-slate-400">#d50000</span>
              </div>
              <div className="flex flex-col items-center gap-1">
                <div className="w-full h-7 rounded-lg bg-[#c2185b] border border-white/20" />
                <span className="text-[9px] font-mono text-slate-400">#c2185b</span>
              </div>
              <div className="flex flex-col items-center gap-1">
                <div className="w-full h-7 rounded-lg bg-[#ff80ab] border border-white/20" />
                <span className="text-[9px] font-mono text-slate-400">#ff80ab</span>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* FOOTER */}
      <footer className="relative z-10 border-t border-white/10 bg-[#0a0718] py-4 px-6 text-center text-xs text-slate-500">
        Cosmic Orbs Studio • Presentadores Sintéticos IA para Vídeo y Animación
      </footer>
    </div>
  );
}
