import React, { useState, useEffect, useRef } from 'react';
import { OrbPalette, OrbPosition, OrbAnimation } from '../types';
import { Play, Square, Sparkles, Radio, Zap } from 'lucide-react';

interface OrbSimulatorProps {
  palette: OrbPalette;
  position: OrbPosition;
  animation: OrbAnimation;
  entityName: string;
  onPaletteChange: (p: OrbPalette) => void;
  onPositionChange: (p: OrbPosition) => void;
  onAnimationChange: (a: OrbAnimation) => void;
}

const PALETTE_COLORS: Record<OrbPalette, { core: string; mid: string; outer: string; glow: string; label: string }> = {
  cosmic: {
    core: '#A855F7',
    mid: '#3B82F6',
    outer: '#06B6D4',
    glow: 'rgba(168, 85, 247, 0.4)',
    label: 'Cósmico (Púrpura, Azul & Cian)',
  },
  cyberpunk: {
    core: '#EC4899',
    mid: '#8B5CF6',
    outer: '#06B6D4',
    glow: 'rgba(236, 72, 153, 0.4)',
    label: 'Cyberpunk (Neón Rosa, Violeta)',
  },
  solar: {
    core: '#F97316',
    mid: '#EAB308',
    outer: '#EF4444',
    glow: 'rgba(249, 115, 22, 0.4)',
    label: 'Solar (Dorado, Incandescente)',
  },
  aurora: {
    core: '#10B981',
    mid: '#06B6D4',
    outer: '#3B82F6',
    glow: 'rgba(16, 185, 129, 0.4)',
    label: 'Aurora (Verde Esmeralda, Turquesa)',
  },
  nebula: {
    core: '#D946EF',
    mid: '#8B5CF6',
    outer: '#6366F1',
    glow: 'rgba(217, 70, 239, 0.4)',
    label: 'Nebulosa (Índigo, Magenta)',
  },
  monochrome: {
    core: '#F8FAFC',
    mid: '#94A3B8',
    outer: '#475569',
    glow: 'rgba(248, 250, 252, 0.4)',
    label: 'Monocromo (Plata Quantum)',
  },
};

export const OrbSimulator: React.FC<OrbSimulatorProps> = ({
  palette,
  position,
  animation,
  entityName,
  onPaletteChange,
  onPositionChange,
  onAnimationChange,
}) => {
  const [isPlayingTestAudio, setIsPlayingTestAudio] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Simulated speech amplitude level (0 to 1)
  const amplitudeRef = useRef(0.2);

  useEffect(() => {
    let phase = 0;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const render = () => {
      phase += 0.04;
      const width = canvas.width;
      const height = canvas.height;

      ctx.clearRect(0, 0, width, height);

      // Draw background space subtle grid
      ctx.fillStyle = '#090d16';
      ctx.fillRect(0, 0, width, height);

      // Determine simulated amplitude
      if (isPlayingTestAudio) {
        // Dynamic speech modulation simulation
        amplitudeRef.current = 0.3 + Math.sin(phase * 3) * 0.25 + Math.cos(phase * 7) * 0.15 + Math.sin(phase * 12) * 0.1;
      } else {
        // Idle breathing
        amplitudeRef.current = 0.2 + Math.sin(phase * 1.5) * 0.05;
      }

      const amp = Math.max(0.1, amplitudeRef.current);
      const colors = PALETTE_COLORS[palette];

      // Calculate orb center based on position setting
      let cx = width / 2;
      let cy = height / 2;

      if (position === 'presenter' || position === 'host') {
        cx = width / 2;
        cy = height * 0.62;
      } else if (position === 'floating') {
        cx = width / 2 + Math.sin(phase * 0.8) * 15;
        cy = height * 0.48 + Math.cos(phase * 1.1) * 10;
      } else if (position === 'ambient') {
        cx = width / 2;
        cy = height / 2;
      } else if (position === 'top-right') {
        cx = width * 0.82;
        cy = height * 0.22;
      }

      const baseRadius = position === 'ambient' ? 140 : 65;
      const pulseScale = 1 + amp * 0.45;
      const radius = baseRadius * pulseScale;

      // Outer Glow Aura
      const auraGrad = ctx.createRadialGradient(cx, cy, radius * 0.2, cx, cy, radius * 2.2);
      auraGrad.addColorStop(0, colors.glow);
      auraGrad.addColorStop(0.6, colors.glow.replace('0.4', '0.15'));
      auraGrad.addColorStop(1, 'transparent');

      ctx.beginPath();
      ctx.arc(cx, cy, radius * 2.2, 0, Math.PI * 2);
      ctx.fillStyle = auraGrad;
      ctx.fill();

      // Atmospheric Ring / Waves
      ctx.save();
      ctx.lineWidth = 2 + amp * 3;
      ctx.strokeStyle = colors.mid;
      ctx.globalAlpha = 0.5 + amp * 0.3;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * (1.1 + Math.sin(phase * 2) * 0.08), 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();

      // Main Gradient Orb Core
      const coreGrad = ctx.createRadialGradient(
        cx - radius * 0.3,
        cy - radius * 0.3,
        radius * 0.1,
        cx,
        cy,
        radius
      );
      coreGrad.addColorStop(0, '#FFFFFF');
      coreGrad.addColorStop(0.25, colors.core);
      coreGrad.addColorStop(0.65, colors.mid);
      coreGrad.addColorStop(1, colors.outer);

      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fillStyle = coreGrad;
      ctx.shadowColor = colors.core;
      ctx.shadowBlur = 25 * pulseScale;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Specular Highlight
      const specGrad = ctx.createRadialGradient(
        cx - radius * 0.35,
        cy - radius * 0.35,
        0,
        cx - radius * 0.35,
        cy - radius * 0.35,
        radius * 0.4
      );
      specGrad.addColorStop(0, 'rgba(255, 255, 255, 0.85)');
      specGrad.addColorStop(1, 'rgba(255, 255, 255, 0)');

      ctx.beginPath();
      ctx.arc(cx - radius * 0.35, cy - radius * 0.35, radius * 0.4, 0, Math.PI * 2);
      ctx.fillStyle = specGrad;
      ctx.fill();

      // Entity Label overlay
      ctx.fillStyle = '#E2E8F0';
      ctx.font = 'bold 12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`${entityName.toUpperCase()} • ORBE BIO-REACTIVO`, cx, cy + radius + 22);

      animFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [palette, position, animation, isPlayingTestAudio, entityName]);

  const toggleTestSpeech = () => {
    if (isPlayingTestAudio) {
      setIsPlayingTestAudio(false);
      return;
    }

    setIsPlayingTestAudio(true);

    // Play synthetic browser speech for preview
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const text = `Transmisión iniciada. Soy ${entityName}, entidad oráculo del año 2045. Analizando resonancia bio-métrica.`;
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'es-ES';
      utterance.rate = 1.0;
      utterance.pitch = 0.9;

      utterance.onend = () => setIsPlayingTestAudio(false);
      utterance.onerror = () => setIsPlayingTestAudio(false);

      window.speechSynthesis.speak(utterance);
    } else {
      setTimeout(() => setIsPlayingTestAudio(false), 5000);
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-purple-500/20 text-purple-400 rounded-lg">
            <Radio className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100 text-sm">Simulador de Orbe Reactivo (FFmpeg Composite)</h3>
            <p className="text-xs text-slate-400">Entidad de Inteligencia Artificial & Modulación de Voz</p>
          </div>
        </div>

        <button
          onClick={toggleTestSpeech}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
            isPlayingTestAudio
              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30 animate-pulse'
              : 'bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-600/25'
          }`}
        >
          {isPlayingTestAudio ? (
            <>
              <Square className="w-3.5 h-3.5 fill-current" /> Detener Demostración
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" /> Probar Reactividad de Voz
            </>
          )}
        </button>
      </div>

      {/* Canvas Live Simulation */}
      <div className="relative w-full h-[230px] rounded-xl overflow-hidden border border-slate-800 bg-slate-950 flex items-center justify-center">
        <canvas ref={canvasRef} width={420} height={230} className="w-full h-full object-cover" />

        <div className="absolute top-3 left-3 bg-slate-950/80 backdrop-blur-md border border-slate-800 px-2.5 py-1 rounded-full text-[10px] text-purple-300 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>ESTADO: {isPlayingTestAudio ? 'HABLANDO (+45% EXPANSIÓN)' : 'REPOSO (IDLE)'}</span>
        </div>

        <div className="absolute bottom-3 right-3 text-[10px] text-slate-400 bg-slate-950/80 px-2.5 py-1 rounded-md border border-slate-800">
          Paleta: <span className="text-purple-300 font-semibold">{PALETTE_COLORS[palette].label}</span>
        </div>
      </div>

      {/* Control Pickers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
        {/* Palette Selector */}
        <div>
          <label className="block text-[11px] font-medium text-slate-300 mb-1 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-purple-400" /> Paleta de Colores
          </label>
          <select
            value={palette}
            onChange={(e) => onPaletteChange(e.target.value as OrbPalette)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 px-2.5 py-1.5 focus:border-purple-500 focus:outline-none"
          >
            {Object.entries(PALETTE_COLORS).map(([key, val]) => (
              <option key={key} value={key}>
                {val.label}
              </option>
            ))}
          </select>
        </div>

        {/* Position Selector */}
        <div>
          <label className="block text-[11px] font-medium text-slate-300 mb-1 flex items-center gap-1">
            <Zap className="w-3 h-3 text-cyan-400" /> Posición en Video (9:16)
          </label>
          <select
            value={position}
            onChange={(e) => onPositionChange(e.target.value as OrbPosition)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 px-2.5 py-1.5 focus:border-purple-500 focus:outline-none"
          >
            <option value="presenter">Presenter (Inferior Centro - Presentador)</option>
            <option value="floating">Floating (Centro Flotante 2D)</option>
            <option value="ambient">Ambient (Resplandor Gigante)</option>
            <option value="top-right">Top-Right (Watermark / Marca de agua)</option>
          </select>
        </div>

        {/* Animation Mode */}
        <div>
          <label className="block text-[11px] font-medium text-slate-300 mb-1 flex items-center gap-1">
            <Radio className="w-3 h-3 text-emerald-400" /> Modo de Animación
          </label>
          <select
            value={animation}
            onChange={(e) => onAnimationChange(e.target.value as OrbAnimation)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 px-2.5 py-1.5 focus:border-purple-500 focus:outline-none"
          >
            <option value="speaking">Speaking (Escucha locución en tiempo real)</option>
            <option value="pulse">Pulse (Pulsación rítmica armónica)</option>
            <option value="float">Float (Ondulación libre)</option>
            <option value="breathing">Breathing (Respiración suave)</option>
          </select>
        </div>
      </div>
    </div>
  );
};
