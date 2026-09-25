import React from 'react';
import { SimulatorConfig, EntityId } from '../types';
import { ENTITY_CHARACTERS, CHARACTER_LIST } from '../data/characters';
import { soundEngine } from '../utils/audioSynth';
import {
  Orbit,
  Sliders,
  Activity,
  Gauge,
  Zap,
  RotateCcw,
  Sparkles,
  Volume2,
  VolumeX,
  Compass,
} from 'lucide-react';

interface CosmicHUDProps {
  config: SimulatorConfig;
  onUpdateConfig: (newConfig: SimulatorConfig) => void;
}

export const CosmicHUD: React.FC<CosmicHUDProps> = ({ config, onUpdateConfig }) => {
  const charA = ENTITY_CHARACTERS[config.activeEntityA];
  const charB = ENTITY_CHARACTERS[config.activeEntityB];

  const handleUpdate = <K extends keyof SimulatorConfig>(key: K, value: SimulatorConfig[K]) => {
    const updated = { ...config, [key]: value };
    onUpdateConfig(updated);

    if (key === 'activeEntityA' || key === 'activeEntityB') {
      const nextCharA = ENTITY_CHARACTERS[key === 'activeEntityA' ? (value as EntityId) : config.activeEntityA];
      const nextCharB = ENTITY_CHARACTERS[key === 'activeEntityB' ? (value as EntityId) : config.activeEntityB];
      if (config.enableDroneSound) {
        soundEngine.updateDroneFrequencies(nextCharA.drone_freq, nextCharB.drone_freq);
      }
    }
  };

  const handleResetDefaults = () => {
    const resetConfig: SimulatorConfig = {
      particleDensity: 'medium',
      speedMultiplier: 1.0,
      gravityStrength: 1.0,
      showOrbits: true,
      interactiveMouse: true,
      activeEntityA: 'quantum',
      activeEntityB: 'solar',
      enableDroneSound: config.enableDroneSound,
      enableSfx: true,
    };
    onUpdateConfig(resetConfig);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* HEADER */}
      <div className="rounded-3xl bg-slate-900/80 p-6 border border-cyan-500/20 backdrop-blur-md shadow-2xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                <Orbit className="h-3.5 w-3.5 animate-spin" style={{ animationDuration: '10s' }} />
              </span>
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-cyan-400">
                Dual Gravity Observatory
              </span>
            </div>
            <h2 className="text-2xl font-bold text-slate-100 mt-1">Telemetría y Control de Partículas Cósmicas</h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Ajusta la simulación de atracción gravitacional de doble centro y los armónicos binaurales
            </p>
          </div>

          <button
            onClick={handleResetDefaults}
            className="flex items-center gap-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 px-3.5 py-2 text-xs font-mono border border-slate-700 transition-all"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Restablecer Órbitas</span>
          </button>
        </div>
      </div>

      {/* ASTROMETRIC TELEMETRY CARDS */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-2xl bg-slate-900/60 p-4 border border-slate-800/80 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>VEL. BARYCENTRO</span>
            <Activity className="h-3.5 w-3.5 text-cyan-400" />
          </div>
          <div className="mt-2 text-xl font-bold font-mono text-cyan-300">
            {(config.speedMultiplier * 29.78).toFixed(2)} <span className="text-xs font-normal text-slate-400">km/s</span>
          </div>
          <p className="text-[10px] text-slate-500 font-mono mt-1">Velocidad orbital relativa</p>
        </div>

        <div className="rounded-2xl bg-slate-900/60 p-4 border border-slate-800/80 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>CAMPO GRAVITATORIO</span>
            <Gauge className="h-3.5 w-3.5 text-amber-400" />
          </div>
          <div className="mt-2 text-xl font-bold font-mono text-amber-300">
            {(config.gravityStrength * 9.81).toFixed(2)} <span className="text-xs font-normal text-slate-400">G-eff</span>
          </div>
          <p className="text-[10px] text-slate-500 font-mono mt-1">Atracción mutua entre núcleos</p>
        </div>

        <div className="rounded-2xl bg-slate-900/60 p-4 border border-slate-800/80 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>RESONANCIA DRONE</span>
            <Volume2 className="h-3.5 w-3.5 text-purple-400" />
          </div>
          <div className="mt-2 text-xl font-bold font-mono text-purple-300">
            {charA.drone_freq} / {charB.drone_freq} <span className="text-xs font-normal text-slate-400">Hz</span>
          </div>
          <p className="text-[10px] text-slate-500 font-mono mt-1">Ondas armónicas sub-graves</p>
        </div>

        <div className="rounded-2xl bg-slate-900/60 p-4 border border-slate-800/80 backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-400 text-xs font-mono">
            <span>PARTÍCULAS ACTIVAS</span>
            <Sparkles className="h-3.5 w-3.5 text-emerald-400" />
          </div>
          <div className="mt-2 text-xl font-bold font-mono text-emerald-300">
            {config.particleDensity === 'low' ? '150' : config.particleDensity === 'high' ? '380' : '240'}{' '}
            <span className="text-xs font-normal text-slate-400">sparks</span>
          </div>
          <p className="text-[10px] text-slate-500 font-mono mt-1">Renderizado 3D Z-Buffer</p>
        </div>
      </div>

      {/* SIMULATOR CONTROLS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* ENTITY COSMIC PALETTES */}
        <div className="rounded-3xl bg-slate-900/60 p-6 border border-slate-800/80 backdrop-blur-md space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Zap className="h-4 w-4 text-cyan-400" />
            Configuración de Entidades en Órbita
          </h3>

          <div className="space-y-4">
            <div>
              <label className="text-xs font-mono text-slate-400 block mb-1">Núcleo Gravitatorio Primario (A):</label>
              <select
                id="select-sim-entity-a"
                value={config.activeEntityA}
                onChange={(e) => handleUpdate('activeEntityA', e.target.value as EntityId)}
                className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-xs font-mono font-bold focus:outline-none"
                style={{ color: charA.primary_color }}
              >
                {CHARACTER_LIST.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.role}) · {c.drone_freq}Hz
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs font-mono text-slate-400 block mb-1">Núcleo Gravitatorio Secundario (B):</label>
              <select
                id="select-sim-entity-b"
                value={config.activeEntityB}
                onChange={(e) => handleUpdate('activeEntityB', e.target.value as EntityId)}
                className="w-full rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-xs font-mono font-bold focus:outline-none"
                style={{ color: charB.primary_color }}
              >
                {CHARACTER_LIST.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.role}) · {c.drone_freq}Hz
                  </option>
                ))}
              </select>
            </div>

            {/* Density Selector */}
            <div>
              <label className="text-xs font-mono text-slate-400 block mb-1.5">Densidad de Partículas:</label>
              <div className="grid grid-cols-3 gap-2">
                {(['low', 'medium', 'high'] as const).map((d) => (
                  <button
                    key={d}
                    onClick={() => handleUpdate('particleDensity', d)}
                    className={`rounded-xl py-2 text-xs font-mono uppercase font-bold transition-all border ${
                      config.particleDensity === d
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-[0_0_12px_rgba(0,240,255,0.2)]'
                        : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
                    }`}
                  >
                    {d === 'low' ? 'Baja (150)' : d === 'medium' ? 'Media (240)' : 'Alta (380)'}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* PHYSICS MODIFIERS */}
        <div className="rounded-3xl bg-slate-900/60 p-6 border border-slate-800/80 backdrop-blur-md space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Sliders className="h-4 w-4 text-purple-400" />
            Parámetros Físicos de Simulación
          </h3>

          <div className="space-y-4">
            {/* Speed Multiplier */}
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-slate-300 mb-1">
                <span>Velocidad de Órbita:</span>
                <span className="text-cyan-400 font-bold">{config.speedMultiplier.toFixed(1)}x</span>
              </div>
              <input
                type="range"
                min="0.2"
                max="3.0"
                step="0.1"
                value={config.speedMultiplier}
                onChange={(e) => handleUpdate('speedMultiplier', parseFloat(e.target.value))}
                className="w-full accent-cyan-400"
              />
            </div>

            {/* Gravity Strength */}
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-slate-300 mb-1">
                <span>Intensidad Gravitacional:</span>
                <span className="text-amber-400 font-bold">{config.gravityStrength.toFixed(1)}x</span>
              </div>
              <input
                type="range"
                min="0.2"
                max="2.5"
                step="0.1"
                value={config.gravityStrength}
                onChange={(e) => handleUpdate('gravityStrength', parseFloat(e.target.value))}
                className="w-full accent-amber-400"
              />
            </div>

            {/* Toggle Toggles */}
            <div className="pt-2 grid grid-cols-1 sm:grid-cols-2 gap-3">
              <label className="flex items-center gap-2 text-xs font-mono text-slate-300 bg-slate-950/70 p-2.5 rounded-xl border border-slate-800 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.showOrbits}
                  onChange={(e) => handleUpdate('showOrbits', e.target.checked)}
                  className="rounded accent-cyan-400"
                />
                <span>Pistas de Órbitas</span>
              </label>

              <label className="flex items-center gap-2 text-xs font-mono text-slate-300 bg-slate-950/70 p-2.5 rounded-xl border border-slate-800 cursor-pointer">
                <input
                  type="checkbox"
                  checked={config.interactiveMouse}
                  onChange={(e) => handleUpdate('interactiveMouse', e.target.checked)}
                  className="rounded accent-cyan-400"
                />
                <span>Gravedad de Ratón</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
