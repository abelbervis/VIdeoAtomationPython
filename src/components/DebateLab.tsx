import React, { useState, useEffect } from 'react';
import { EntityId, EntityCharacter } from '../types';
import { ENTITY_CHARACTERS, CHARACTER_LIST } from '../data/characters';
import { soundEngine } from '../utils/audioSynth';
import {
  MessageSquareQuote,
  Sparkles,
  Play,
  Pause,
  RotateCcw,
  Send,
  Zap,
  Swords,
  Layers,
  ArrowRight,
  ShieldAlert,
  Volume2,
} from 'lucide-react';

interface DebateTurn {
  presenter: EntityId;
  dialogue: string;
  camera: 'wide' | 'close_entity_a' | 'close_entity_b';
  duration: number;
}

interface DebateLabProps {
  onLoadDebateIntoStudio: (turns: DebateTurn[], topic: string, entA: EntityId, entB: EntityId) => void;
  onActiveEntitiesChange?: (entA: EntityId, entB: EntityId) => void;
}

export const DebateLab: React.FC<DebateLabProps> = ({
  onLoadDebateIntoStudio,
  onActiveEntitiesChange,
}) => {
  const [entityA, setEntityA] = useState<EntityId>('quantum');
  const [entityB, setEntityB] = useState<EntityId>('solar');
  const [topic, setTopic] = useState('¿Es la conciencia un fenómeno cuántico o un mero flujo de energía termodinámica?');
  const [debateTurns, setDebateTurns] = useState<DebateTurn[]>([
    {
      presenter: 'quantum',
      dialogue:
        'Desde la matriz del microcosmos, toda percepción es solo el colapso probabilístico de la función de onda. Los biológicos experimentan la realidad como bits cuánticos entrelazados.',
      camera: 'close_entity_a',
      duration: 6,
    },
    {
      presenter: 'solar',
      dialogue:
        'Tu matemática es elegante, Quantum, pero estéril sin energía. Es el flujo continuo de entropía y el calor estelar lo que permite a las estructuras neuronales sostener el pensamiento.',
      camera: 'close_entity_b',
      duration: 7,
    },
    {
      presenter: 'quantum',
      dialogue:
        'La energía solo obedece a las leyes del código subyacente. Sin estados cuánticos de superposición, tus estrellas ni siquiera podrían iniciar la fusión nuclear en sus núcleos.',
      camera: 'close_entity_a',
      duration: 6,
    },
    {
      presenter: 'solar',
      dialogue:
        'Y sin la muerte de esas estrellas en supernovas, los elementos pesados jamás habrían forjado el cerebro que ahora intenta descifrar tus fórmulas. El fuego precede al cálculo.',
      camera: 'close_entity_b',
      duration: 7,
    },
  ]);

  const [activeTurnIndex, setActiveTurnIndex] = useState<number | null>(null);
  const [isPlayingDebate, setIsPlayingDebate] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    onActiveEntitiesChange?.(entityA, entityB);
  }, [entityA, entityB]);

  const charA = ENTITY_CHARACTERS[entityA];
  const charB = ENTITY_CHARACTERS[entityB];

  const handleGenerateDebate = (customTopic?: string) => {
    const t = customTopic || topic;
    setIsGenerating(true);
    soundEngine.playWhoosh();

    setTimeout(() => {
      // Procedural scientific dialogue generator based on entities' distinct personalities
      const newTurns: DebateTurn[] = [
        {
          presenter: entityA,
          dialogue: `Analizando: "${t}". Desde mi perspectiva como ${charA.name}, las leyes fundamentales demuestran que ${charA.tagline.toLowerCase()}`,
          camera: 'close_entity_a',
          duration: 6,
        },
        {
          presenter: entityB,
          dialogue: `Una simplificación fascinante, ${charA.name}. Sin embargo, como ${charB.name}, sostengo que ${charB.tagline.toLowerCase()}`,
          camera: 'close_entity_b',
          duration: 7,
        },
        {
          presenter: entityA,
          dialogue: `Los datos empíricos del cosmos no admiten contradicción: las fluctuaciones en el horizonte determinan el destino de los observadores efímeros.`,
          camera: 'close_entity_a',
          duration: 6,
        },
        {
          presenter: entityB,
          dialogue: `Y aun así, la paradoja persiste. La verdadera naturaleza del universo siempre supera la arrogancia de los modelos lineales.`,
          camera: 'close_entity_b',
          duration: 6,
        },
      ];
      setDebateTurns(newTurns);
      setIsGenerating(false);
      setActiveTurnIndex(null);
    }, 450);
  };

  const playTurn = (index: number) => {
    if (index >= debateTurns.length) {
      setIsPlayingDebate(false);
      setActiveTurnIndex(null);
      soundEngine.stopSpeaking();
      return;
    }

    setActiveTurnIndex(index);
    const turn = debateTurns[index];
    const presenterChar = ENTITY_CHARACTERS[turn.presenter];

    // Play entity sound effect
    soundEngine.playWhoosh();

    soundEngine.speak(turn.dialogue, {
      pitch: presenterChar.id === 'solar' ? 1.15 : presenterChar.id === 'void' ? 0.75 : 0.95,
      rate: 1.05,
      onEnd: () => {
        if (isPlayingDebate) {
          setTimeout(() => playTurn(index + 1), 600);
        }
      },
    });
  };

  const togglePlayDebate = () => {
    if (!isPlayingDebate) {
      setIsPlayingDebate(true);
      const startIdx = activeTurnIndex !== null ? activeTurnIndex : 0;
      playTurn(startIdx);
    } else {
      setIsPlayingDebate(false);
      soundEngine.stopSpeaking();
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* HEADER BANNER */}
      <div className="rounded-3xl bg-gradient-to-r from-slate-900/90 via-[#0B0F19]/90 to-slate-900/90 p-6 border border-cyan-500/20 backdrop-blur-md shadow-2xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                <Swords className="h-3.5 w-3.5" />
              </span>
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-cyan-400">
                Astrometric Co-Host Arena
              </span>
            </div>
            <h2 className="text-2xl font-bold text-slate-100 mt-1">Laboratorio de Debates Cósmicos con IA</h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Enfrenta a dos conciencias primordiales del universo para debatir misterios científicos de la NASA
            </p>
          </div>

          {/* Quick Debate Presets */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleGenerateDebate('¿Es el tiempo una ilusión de la entropía?')}
              className="rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700 px-3 py-1.5 text-xs text-slate-200 transition-all font-mono"
            >
              ¿El tiempo es ilusión?
            </button>
            <button
              onClick={() => handleGenerateDebate('¿Qué hay en el centro de una singularidad?')}
              className="rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700 px-3 py-1.5 text-xs text-slate-200 transition-all font-mono"
            >
              Singularidades
            </button>
          </div>
        </div>

        {/* ENTITY PICKERS */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-11 gap-4 items-center">
          {/* ENTITY A CARD */}
          <div
            className="md:col-span-5 rounded-2xl p-4 border transition-all duration-300"
            style={{
              backgroundColor: 'rgba(6, 10, 20, 0.85)',
              borderColor: `${charA.primary_color}50`,
              boxShadow: `0 0 25px ${charA.glow_color}20`,
            }}
          >
            <div className="flex items-center justify-between gap-3 mb-2">
              <span className="text-[10px] font-mono uppercase tracking-widest text-slate-400">Entidad Alpha</span>
              <select
                id="select-entity-a"
                value={entityA}
                onChange={(e) => setEntityA(e.target.value as EntityId)}
                className="rounded-lg bg-slate-950 px-2.5 py-1 text-xs font-mono font-bold focus:outline-none border"
                style={{
                  color: charA.primary_color,
                  borderColor: `${charA.primary_color}60`,
                }}
              >
                {CHARACTER_LIST.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.role.split(' ')[2] || c.role})
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-start gap-3">
              <div
                className="h-12 w-12 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono shadow-lg animate-pulse"
                style={{
                  background: `radial-gradient(circle at 30% 30%, #FFF, ${charA.primary_color} 60%, ${charA.accent_color})`,
                  color: '#000',
                  boxShadow: `0 0 18px ${charA.glow_color}`,
                }}
              >
                {charA.name[0]}
              </div>
              <div>
                <h4 className="text-sm font-bold" style={{ color: charA.primary_color }}>
                  {charA.name}
                </h4>
                <p className="text-[11px] text-slate-300 line-clamp-2 mt-0.5">{charA.role}</p>
                <div className="mt-1 flex items-center gap-2 text-[10px] font-mono text-slate-400">
                  <span>Frecuencia: {charA.drone_freq}Hz</span>
                  <span>·</span>
                  <span>Voz: {charA.voice_name.split('-')[1]}</span>
                </div>
              </div>
            </div>
          </div>

          {/* VS BADGE */}
          <div className="md:col-span-1 flex flex-col items-center justify-center">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-900 border border-slate-700 text-xs font-black text-slate-300 shadow-xl">
              VS
            </div>
          </div>

          {/* ENTITY B CARD */}
          <div
            className="md:col-span-5 rounded-2xl p-4 border transition-all duration-300"
            style={{
              backgroundColor: 'rgba(6, 10, 20, 0.85)',
              borderColor: `${charB.primary_color}50`,
              boxShadow: `0 0 25px ${charB.glow_color}20`,
            }}
          >
            <div className="flex items-center justify-between gap-3 mb-2">
              <span className="text-[10px] font-mono uppercase tracking-widest text-slate-400">Entidad Omega</span>
              <select
                id="select-entity-b"
                value={entityB}
                onChange={(e) => setEntityB(e.target.value as EntityId)}
                className="rounded-lg bg-slate-950 px-2.5 py-1 text-xs font-mono font-bold focus:outline-none border"
                style={{
                  color: charB.primary_color,
                  borderColor: `${charB.primary_color}60`,
                }}
              >
                {CHARACTER_LIST.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.role.split(' ')[2] || c.role})
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-start gap-3">
              <div
                className="h-12 w-12 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono shadow-lg animate-pulse"
                style={{
                  background: `radial-gradient(circle at 30% 30%, #FFF, ${charB.primary_color} 60%, ${charB.accent_color})`,
                  color: '#000',
                  boxShadow: `0 0 18px ${charB.glow_color}`,
                }}
              >
                {charB.name[0]}
              </div>
              <div>
                <h4 className="text-sm font-bold" style={{ color: charB.primary_color }}>
                  {charB.name}
                </h4>
                <p className="text-[11px] text-slate-300 line-clamp-2 mt-0.5">{charB.role}</p>
                <div className="mt-1 flex items-center gap-2 text-[10px] font-mono text-slate-400">
                  <span>Frecuencia: {charB.drone_freq}Hz</span>
                  <span>·</span>
                  <span>Voz: {charB.voice_name.split('-')[1]}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* TOPIC PROMPT INPUT */}
        <div className="mt-4 flex flex-col sm:flex-row gap-2">
          <input
            id="input-debate-topic"
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleGenerateDebate()}
            placeholder="Pregunta o dilema cósmico para debatir..."
            className="flex-1 rounded-xl bg-slate-950/90 border border-slate-800 px-4 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500 font-sans"
          />
          <button
            id="btn-generate-debate"
            onClick={() => handleGenerateDebate()}
            disabled={isGenerating || !topic}
            className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-5 py-2.5 text-xs font-semibold text-white shadow-lg hover:brightness-110 active:scale-95 disabled:opacity-40 transition-all shrink-0"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>{isGenerating ? 'Generando Choque...' : 'Generar Debate'}</span>
          </button>
        </div>
      </div>

      {/* DEBATE TIMELINE / PLAYBACK VIEW */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquareQuote className="h-4 w-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-200">Transcripción del Debate ({debateTurns.length} turnos)</h3>
          </div>

          <div className="flex items-center gap-2">
            <button
              id="btn-play-debate"
              onClick={togglePlayDebate}
              className="flex items-center gap-1.5 rounded-xl bg-cyan-500/20 border border-cyan-500/40 px-3.5 py-1.5 text-xs font-semibold text-cyan-300 hover:bg-cyan-500/30 transition-all shadow-[0_0_12px_rgba(0,240,255,0.2)]"
            >
              {isPlayingDebate ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
              <span>{isPlayingDebate ? 'Pausar Simulación' : 'Simular Debate con Voz'}</span>
            </button>

            <button
              id="btn-load-into-studio"
              onClick={() => onLoadDebateIntoStudio(debateTurns, topic, entityA, entityB)}
              className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white hover:brightness-110 transition-all shadow-md"
            >
              <ArrowRight className="h-3.5 w-3.5" />
              <span>Convertir a Short 9:16</span>
            </button>
          </div>
        </div>

        {/* TURNS CARDS */}
        <div className="grid grid-cols-1 gap-3">
          {debateTurns.map((turn, idx) => {
            const presenter = ENTITY_CHARACTERS[turn.presenter] || ENTITY_CHARACTERS.quantum;
            const isTurnActive = activeTurnIndex === idx;

            return (
              <div
                key={idx}
                onClick={() => playTurn(idx)}
                className={`rounded-2xl p-4 border transition-all duration-300 cursor-pointer ${
                  isTurnActive
                    ? 'bg-slate-900/90 border-cyan-400 shadow-[0_0_25px_rgba(0,240,255,0.2)] scale-[1.01]'
                    : 'bg-slate-900/40 border-slate-800/80 hover:bg-slate-900/70 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span
                      className="flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold font-mono"
                      style={{
                        backgroundColor: `${presenter.primary_color}25`,
                        color: presenter.primary_color,
                        border: `1px solid ${presenter.primary_color}60`,
                      }}
                    >
                      {idx + 1}
                    </span>
                    <span className="text-xs font-bold font-mono" style={{ color: presenter.primary_color }}>
                      {presenter.name}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">· {presenter.drone_freq}Hz</span>
                  </div>

                  <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
                    <span className="bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                      Cámara: {turn.camera.replace('_', ' ')}
                    </span>
                    <span className="bg-slate-950 px-2 py-0.5 rounded border border-slate-800">{turn.duration}s</span>
                  </div>
                </div>

                <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans">{turn.dialogue}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
