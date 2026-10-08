import React, { useState } from 'react';
import {
  Film,
  Sparkles,
  Monitor,
  Cloud,
  Terminal,
  Zap,
  Play,
  Volume2,
  CheckCircle2,
  Layers,
  ChevronRight,
  Database,
  Plus,
  ArrowRight,
  Settings,
  Info,
  ExternalLink,
  Shield,
  Server,
  Cpu,
  HardDrive
} from 'lucide-react';
import { VisualResourceItem } from '../App';

interface HybridTimelineStudioProps {
  currentLesson: any;
  selectedLessonKey: string;
  allLessons: Record<string, any>;
  onSelectLessonKey: (key: string) => void;
  visualResources: VisualResourceItem[];
  sceneOverrides: Record<string, string>;
  onSetSceneResource: (sceneIdx: number, resourceId: string) => void;
  activeSceneIndex: number;
  onSelectScene: (idx: number) => void;
  onRunCommand: (cmd: string) => void;
  onPlayAudio: (text: string, speaker: string) => void;
  isPlayingAudio: boolean;
  onOpenCatalog: () => void;
  onOpenNewResource: () => void;
}

export const HybridTimelineStudio: React.FC<HybridTimelineStudioProps> = ({
  currentLesson,
  selectedLessonKey,
  allLessons,
  onSelectLessonKey,
  visualResources,
  sceneOverrides,
  onSetSceneResource,
  activeSceneIndex,
  onSelectScene,
  onRunCommand,
  onPlayAudio,
  isPlayingAudio,
  onOpenCatalog,
  onOpenNewResource
}) => {
  const [motionAnimationStep, setMotionAnimationStep] = useState(0);

  // Auto-route scene text using local keyword matching (mirrors VisualResourceRouter in Python)
  const resolveSceneResource = (text: string, idx: number): { resource: VisualResourceItem; isOverridden: boolean } => {
    const key = `${selectedLessonKey}_${idx}`;
    const overrideId = sceneOverrides[key];
    if (overrideId) {
      const found = visualResources.find((r) => r.id === overrideId);
      if (found) return { resource: found, isOverridden: true };
    }

    const clean = text.toLowerCase();
    let best = visualResources[0]; // fallback slide
    let bestScore = -1;

    for (const res of visualResources) {
      let score = 0;
      for (const kw of res.intent_keywords) {
        if (clean.includes(kw.toLowerCase())) {
          score += 1.5 * res.priority;
        }
      }
      if (score > bestScore && score >= 1.0) {
        bestScore = score;
        best = res;
      }
    }

    return { resource: best, isOverridden: false };
  };

  const dialogueList: Array<{ speaker: string; text: string; role?: string }> = currentLesson?.dialogue || [];
  const currentTurn = dialogueList[activeSceneIndex] || dialogueList[0] || { speaker: 'Alex', text: 'Bienvenido a Google Cloud' };
  const { resource: activeResource, isOverridden: activeIsOverridden } = resolveSceneResource(currentTurn.text, activeSceneIndex);

  // Resource styling helpers
  const getResourceBadge = (kind: string) => {
    switch (kind) {
      case 'slide':
        return {
          icon: Monitor,
          label: 'Diapositiva HD',
          badgeClass: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
          dotClass: 'bg-blue-400'
        };
      case 'motion':
        return {
          icon: Sparkles,
          label: 'Animación RAG',
          badgeClass: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
          dotClass: 'bg-emerald-400'
        };
      case 'console':
        return {
          icon: Cloud,
          label: 'Consola GCP Real',
          badgeClass: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
          dotClass: 'bg-amber-400'
        };
      case 'terminal':
        return {
          icon: Terminal,
          label: 'Terminal CLI',
          badgeClass: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
          dotClass: 'bg-purple-400'
        };
      default:
        return {
          icon: Zap,
          label: 'Recurso Custom',
          badgeClass: 'bg-pink-500/15 text-pink-400 border-pink-500/30',
          dotClass: 'bg-pink-400'
        };
    }
  };

  return (
    <main className="flex-1 p-6 max-w-7xl mx-auto w-full flex flex-col gap-6">
      {/* Top Architecture Banner */}
      <div className="bg-gradient-to-r from-blue-950/60 via-indigo-950/40 to-slate-900 border border-indigo-500/30 rounded-2xl p-5 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2.5 mb-1.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
                <Film className="w-4 h-4" />
              </div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                Orquestador de Recursos Visuales
                <span className="text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-mono uppercase tracking-wider">
                  VisualResourceRouter • RAG Multi-Recurso
                </span>
              </h2>
            </div>
            <p className="text-xs text-slate-300 max-w-3xl leading-relaxed">
              Resuelve el problema de escalabilidad: cada escena selecciona automáticamente entre{' '}
              <strong className="text-white">Diapositivas</strong>, <strong className="text-emerald-300">Animaciones Vectoriales RAG</strong>,{' '}
              <strong className="text-amber-300">Consola Real</strong> y <strong className="text-purple-300">Terminal CLI</strong> mediante un router semántico local (&lt;1ms). El prompt de IA se mantiene en pocos cientos de bytes sin saturar memoria ni presupuesto.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={onOpenCatalog}
              className="bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 text-slate-200 text-xs px-3.5 py-2 rounded-xl font-medium flex items-center gap-2 transition shadow-sm"
            >
              <Database className="w-3.5 h-3.5 text-indigo-400" />
              Catálogo de Recursos ({visualResources.length})
            </button>
            <button
              onClick={onOpenNewResource}
              className="bg-indigo-950/80 hover:bg-indigo-900 border border-indigo-500/40 text-indigo-200 text-xs px-3.5 py-2 rounded-xl font-medium flex items-center gap-2 transition"
            >
              <Plus className="w-3.5 h-3.5 text-indigo-400" />
              Nuevo Recurso
            </button>
            <button
              onClick={() => onRunCommand(`python gcp_tutorial.py --topic "${selectedLessonKey}" --hybrid`)}
              className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs px-4 py-2 rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              Renderizar Video Híbrido
            </button>
          </div>
        </div>

        {/* Metrics Pill Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 pt-4 border-t border-slate-800/80 text-xs">
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>Decisión Semántica: <strong className="text-white font-mono">&lt; 1 ms</strong></span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-sky-400" />
            <span>Sobrecoste en Prompt: <strong className="text-white font-mono">0 Bytes</strong></span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-indigo-400" />
            <span>Medios Disponibles: <strong className="text-white font-mono">{visualResources.length} Tipos</strong></span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            <span>Pacing Pedagógico: <strong className="text-white font-mono">Alternado</strong></span>
          </div>
        </div>
      </div>

      {/* Preset Topics Bar */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 whitespace-nowrap mr-1">
          Tema de Estudio:
        </span>
        {Object.keys(allLessons).map((key) => {
          const l = allLessons[key];
          const isSelected = selectedLessonKey === key;
          return (
            <button
              key={key}
              onClick={() => {
                onSelectLessonKey(key);
                onSelectScene(0);
              }}
              className={`text-xs px-3 py-1.5 rounded-xl font-medium whitespace-nowrap transition border ${
                isSelected
                  ? 'bg-indigo-600 text-white border-indigo-400 shadow-md shadow-indigo-600/30'
                  : 'bg-slate-900/80 text-slate-300 border-slate-800 hover:border-slate-700 hover:text-white'
              }`}
            >
              {l.title.split(':')[0]}
            </button>
          );
        })}
      </div>

      {/* Main Grid: Left Column Timeline / Right Column Multi-Resource Live Canvas */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Multi-Resource Timeline Dispatcher */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          <div className="bg-[#0D1424] border border-slate-800/80 rounded-2xl p-4 shadow-xl flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  Línea de Tiempo del Tutorial
                  <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-full font-mono">
                    {dialogueList.length} Escenas
                  </span>
                </h3>
                <p className="text-[11px] text-slate-400">
                  Haz clic para previsualizar o cambia el recurso visual de cada escena
                </p>
              </div>
            </div>

            <div className="space-y-2.5 max-h-[620px] overflow-y-auto pr-1">
              {dialogueList.map((turn, idx) => {
                const isSelected = activeSceneIndex === idx;
                const { resource, isOverridden } = resolveSceneResource(turn.text, idx);
                const badge = getResourceBadge(resource.kind);
                const BadgeIcon = badge.icon;

                return (
                  <div
                    key={idx}
                    onClick={() => onSelectScene(idx)}
                    className={`p-3.5 rounded-xl border transition cursor-pointer flex flex-col gap-2.5 ${
                      isSelected
                        ? 'bg-slate-900/90 border-indigo-500 shadow-lg shadow-indigo-500/10'
                        : 'bg-slate-950/60 border-slate-850 hover:border-slate-700 hover:bg-slate-900/40'
                    }`}
                  >
                    {/* Scene Header */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-950/80 border border-indigo-800/60 px-1.5 py-0.5 rounded">
                          #{idx + 1}
                        </span>
                        <span className="text-xs font-bold text-white">{turn.speaker}</span>
                        {turn.role && (
                          <span className="text-[10px] text-slate-400 hidden sm:inline">
                            ({turn.role})
                          </span>
                        )}
                      </div>

                      {/* Resource Badge */}
                      <div className="flex items-center gap-1.5">
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border flex items-center gap-1 ${badge.badgeClass}`}
                        >
                          <BadgeIcon className="w-3 h-3" />
                          {badge.label}
                        </span>
                        {isOverridden && (
                          <span className="text-[9px] bg-amber-500/20 text-amber-300 border border-amber-500/30 px-1.5 py-0.2 rounded font-mono">
                            Manual
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Dialogue Text */}
                    <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                      "{turn.text}"
                    </p>

                    {/* Resource Selector & Controls */}
                    <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-2 text-xs">
                      <div className="flex items-center gap-1.5 flex-1 min-w-0">
                        <span className="text-[10px] text-slate-400 whitespace-nowrap">Recurso:</span>
                        <select
                          value={resource.id}
                          onClick={(e) => e.stopPropagation()}
                          onChange={(e) => {
                            e.stopPropagation();
                            onSetSceneResource(idx, e.target.value);
                          }}
                          className="bg-slate-900 border border-slate-700 text-slate-200 text-[11px] rounded-lg px-2 py-1 focus:outline-none focus:border-indigo-400 truncate flex-1"
                        >
                          {visualResources.map((res) => (
                            <option key={res.id} value={res.id}>
                              [{res.kind.toUpperCase()}] {res.name}
                            </option>
                          ))}
                        </select>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onPlayAudio(turn.text, turn.speaker);
                        }}
                        className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition flex items-center gap-1 text-[11px]"
                        title="Escuchar audio"
                      >
                        <Volume2 className="w-3.5 h-3.5 text-sky-400" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Multi-Resource Live Preview Canvas */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          <div className="bg-[#0B1222] border border-slate-800/90 rounded-2xl p-5 shadow-2xl flex flex-col min-h-[580px]">
            {/* Canvas Header Bar */}
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
              <div className="flex items-center gap-3">
                <span className="text-xs font-mono font-bold text-indigo-300 bg-indigo-950 border border-indigo-800 px-2 py-1 rounded-lg">
                  Escena {activeSceneIndex + 1} de {dialogueList.length}
                </span>
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    {activeResource.name}
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    {activeIsOverridden ? 'Recurso seleccionado manualmente por el usuario' : 'Asignado automáticamente por coincidencia semántica didáctica'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => onPlayAudio(currentTurn.text, currentTurn.speaker)}
                  className={`text-xs px-3 py-1.5 rounded-xl border flex items-center gap-1.5 font-medium transition ${
                    isPlayingAudio
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 animate-pulse'
                      : 'bg-slate-900 border-slate-700 text-slate-300 hover:text-white hover:border-slate-600'
                  }`}
                >
                  <Volume2 className="w-3.5 h-3.5 text-sky-400" />
                  {isPlayingAudio ? 'Reproduciendo...' : 'Voz Neural'}
                </button>
              </div>
            </div>

            {/* Dynamic Visual Canvas Renderer based on activeResource.kind */}
            <div className="flex-1 bg-slate-950 border border-slate-850 rounded-xl overflow-hidden flex flex-col relative min-h-[400px]">
              {/* KIND 1: SLIDE (Architectural Card) */}
              {activeResource.kind === 'slide' && (
                <div className="w-full h-full p-6 flex flex-col justify-between bg-gradient-to-br from-slate-950 via-[#0B1020] to-[#080d19]">
                  {/* Slide Top Badge */}
                  <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-sky-400 bg-sky-950/70 border border-sky-800/50 px-2.5 py-1 rounded-md">
                      DIAPOSITIVA ARQUITECTÓNICA HD
                    </span>
                    <span className="text-[11px] text-slate-500 font-mono">1920 × 1080 • Vector SVG</span>
                  </div>

                  {/* Slide Content */}
                  <div className="my-auto py-4 space-y-4">
                    <div>
                      <h4 className="text-xl font-black text-white tracking-tight">
                        {currentLesson?.title || 'Concepto de Google Cloud Platform'}
                      </h4>
                      <p className="text-xs text-sky-300 mt-1">
                        Punto Clave: {activeResource.name}
                      </p>
                    </div>

                    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-2.5">
                      <div className="text-xs text-slate-200 font-medium leading-relaxed flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                        <span>{currentTurn.text}</span>
                      </div>
                      <div className="text-xs text-slate-400 leading-relaxed flex items-start gap-2 pl-6">
                        <span className="text-sky-400 font-bold">•</span>
                        <span>Optimizado para retención técnica mediante diagramas y micro-conceptos visuales.</span>
                      </div>
                      <div className="text-xs text-slate-400 leading-relaxed flex items-start gap-2 pl-6">
                        <span className="text-sky-400 font-bold">•</span>
                        <span>Cero sobrecoste de almacenamiento gracias a rasterizado vectorial dinámico.</span>
                      </div>
                    </div>
                  </div>

                  {/* Slide Footer */}
                  <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                    <span>Google Cloud NotebookLM Studio</span>
                    <span className="text-indigo-400 font-medium">Locutor: {currentTurn.speaker}</span>
                  </div>
                </div>
              )}

              {/* KIND 2: MOTION (RAG Vector Animation) */}
              {activeResource.kind === 'motion' && (
                <div className="w-full h-full p-5 flex flex-col justify-between bg-[#060a12] relative overflow-hidden">
                  <div className="flex items-center justify-between z-10">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-950/70 border border-emerald-800/50 px-2.5 py-1 rounded-md flex items-center gap-1.5">
                      <Sparkles className="w-3 h-3" /> CLIP VECTORIAL ANIMADO (RAG)
                    </span>
                    <button
                      onClick={() => setMotionAnimationStep((s) => (s + 1) % 4)}
                      className="text-[11px] bg-slate-900 hover:bg-slate-800 border border-slate-700 text-emerald-300 px-2.5 py-1 rounded-md transition"
                    >
                      Paso Siguiente ({motionAnimationStep + 1}/4)
                    </button>
                  </div>

                  {/* Dynamic SVG Canvas */}
                  <div className="my-auto flex items-center justify-center py-6">
                    <svg viewBox="0 0 700 280" className="w-full max-h-[250px] drop-shadow-2xl">
                      <defs>
                        <linearGradient id="ragLine" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#38bdf8" />
                          <stop offset="50%" stopColor="#34d399" />
                          <stop offset="100%" stopColor="#818cf8" />
                        </linearGradient>
                      </defs>

                      {/* Motion Layout: Hierarchy Tree or Elastic Scaling */}
                      {activeResource.id.includes('tree') || activeResource.id.includes('jerarqu') ? (
                        <g>
                          {/* Tree Root: Organization */}
                          <rect x="250" y="20" width="200" height="45" rx="8" fill="#1e293b" stroke="#38bdf8" strokeWidth="2" />
                          <text x="350" y="48" fill="#ffffff" fontSize="13" fontWeight="bold" textAnchor="middle">
                            🏢 ORGANIZACIÓN GCP
                          </text>

                          {/* Branches */}
                          <path d="M 350 65 L 350 95 L 180 95 L 180 120" stroke="url(#ragLine)" strokeWidth="2" fill="none" strokeDasharray="4 4" />
                          <path d="M 350 65 L 350 95 L 520 95 L 520 120" stroke="url(#ragLine)" strokeWidth="2" fill="none" strokeDasharray="4 4" />

                          {/* Folders */}
                          <rect x="90" y="120" width="180" height="42" rx="6" fill="#0f172a" stroke="#34d399" strokeWidth="1.5" />
                          <text x="180" y="146" fill="#a7f3d0" fontSize="11" fontWeight="bold" textAnchor="middle">
                            📁 Carpeta: Producción
                          </text>

                          <rect x="430" y="120" width="180" height="42" rx="6" fill="#0f172a" stroke="#a78bfa" strokeWidth="1.5" />
                          <text x="520" y="146" fill="#ddd6fe" fontSize="11" fontWeight="bold" textAnchor="middle">
                            📁 Carpeta: Desarrollo
                          </text>

                          {/* Projects */}
                          <path d="M 180 162 L 180 195" stroke="#34d399" strokeWidth="1.5" fill="none" />
                          <path d="M 520 162 L 520 195" stroke="#a78bfa" strokeWidth="1.5" fill="none" />

                          <rect x="100" y="195" width="160" height="38" rx="6" fill="#1e293b" stroke="#38bdf8" strokeWidth="1" />
                          <text x="180" y="219" fill="#e2e8f0" fontSize="10" textAnchor="middle">
                            📦 proj-prod-api-01
                          </text>

                          <rect x="440" y="195" width="160" height="38" rx="6" fill="#1e293b" stroke="#38bdf8" strokeWidth="1" />
                          <text x="520" y="219" fill="#e2e8f0" fontSize="10" textAnchor="middle">
                            📦 proj-dev-sandbox
                          </text>
                        </g>
                      ) : (
                        <g>
                          {/* Elastic Scaling / Network flow representation */}
                          <rect x="60" y="90" width="140" height="70" rx="10" fill="#1e293b" stroke="#38bdf8" strokeWidth="2" />
                          <text x="130" y="125" fill="#ffffff" fontSize="12" fontWeight="bold" textAnchor="middle">
                            Trafico Inbound
                          </text>
                          <text x="130" y="145" fill="#94a3b8" fontSize="10" textAnchor="middle">
                            HTTPS Requests
                          </text>

                          <path d="M 200 125 L 280 125" stroke="url(#ragLine)" strokeWidth="3" fill="none" />
                          <circle cx={240 + ((motionAnimationStep * 20) % 40)} cy="125" r="5" fill="#38bdf8" />

                          <rect x="280" y="70" width="160" height="110" rx="12" fill="#0f172a" stroke="#34d399" strokeWidth="2" />
                          <text x="360" y="105" fill="#34d399" fontSize="13" fontWeight="bold" textAnchor="middle">
                            Cloud Run Pods
                          </text>
                          <text x="360" y="130" fill="#ffffff" fontSize="11" textAnchor="middle">
                            {motionAnimationStep === 0 ? '0 Instancias (0 €)' : `${motionAnimationStep * 3} Réplicas Activas`}
                          </text>
                          <text x="360" y="155" fill="#a7f3d0" fontSize="9" textAnchor="middle">
                            Auto-scaling 0..N en &lt;1s
                          </text>

                          <path d="M 440 125 L 510 125" stroke="url(#ragLine)" strokeWidth="3" fill="none" />

                          <rect x="510" y="90" width="130" height="70" rx="10" fill="#1e293b" stroke="#a78bfa" strokeWidth="2" />
                          <text x="575" y="125" fill="#ffffff" fontSize="12" fontWeight="bold" textAnchor="middle">
                            Cloud SQL
                          </text>
                          <text x="575" y="145" fill="#ddd6fe" fontSize="10" textAnchor="middle">
                            Postgres Privado
                          </text>
                        </g>
                      )}
                    </svg>
                  </div>

                  <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                    <span className="text-emerald-400 font-mono">15 FPS • CRF 26 • x264 MP4</span>
                    <span>Generado con plantilla quirúrgica de ~300 bytes</span>
                  </div>
                </div>
              )}

              {/* KIND 3: CONSOLE (Simulated GCP Real Console Walkthrough) */}
              {activeResource.kind === 'console' && (
                <div className="w-full h-full flex flex-col bg-[#1A1F2C] text-slate-200 font-sans text-xs">
                  {/* Google Cloud Header */}
                  <div className="bg-[#2D3344] px-4 py-2 border-b border-slate-700 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-1.5 font-bold text-white">
                        <span className="text-sky-400 text-sm font-black">Google Cloud</span>
                        <span className="text-slate-400 font-normal">|</span>
                        <span>Console</span>
                      </div>
                      <span className="bg-[#1F2432] text-slate-300 px-2 py-0.5 rounded text-[10px] border border-slate-700">
                        📁 mi-empresa-gcp-prod
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                        Cloud Shell Listo
                      </span>
                    </div>
                  </div>

                  {/* Breadcrumb Bar */}
                  <div className="bg-[#202534] px-4 py-2 border-b border-slate-700/80 flex items-center justify-between">
                    <div className="flex items-center gap-1 text-[11px] text-slate-400">
                      <HardDrive className="w-3.5 h-3.5 text-sky-400" />
                      <span>Cloud Storage</span>
                      <span>&gt;</span>
                      <span className="text-white font-medium">Buckets</span>
                    </div>
                    <button className="bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-bold px-3 py-1 rounded transition">
                      + CREAR BUCKET
                    </button>
                  </div>

                  {/* Simulated Console Table */}
                  <div className="p-4 flex-1 overflow-auto">
                    <table className="w-full text-left text-[11px] border-collapse">
                      <thead>
                        <tr className="border-b border-slate-700 text-slate-400">
                          <th className="pb-2 font-medium">Nombre del Bucket</th>
                          <th className="pb-2 font-medium">Ubicación</th>
                          <th className="pb-2 font-medium">Clase por Defecto</th>
                          <th className="pb-2 font-medium">Ahorro Estimado</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        <tr className="hover:bg-slate-800/40">
                          <td className="py-2.5 font-medium text-sky-400 flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full bg-emerald-400" />
                            gs://empresa-fotos-standard
                          </td>
                          <td className="py-2.5 text-slate-300">us-central1</td>
                          <td className="py-2.5 text-slate-200">STANDARD</td>
                          <td className="py-2.5 text-slate-400">Tarifa Base</td>
                        </tr>
                        <tr className="bg-blue-900/20 border-l-2 border-blue-400">
                          <td className="py-2.5 font-medium text-sky-300 flex items-center gap-1.5 pl-2">
                            <span className="w-2 h-2 rounded-full bg-blue-400" />
                            gs://empresa-backups-coldline
                          </td>
                          <td className="py-2.5 text-slate-300">us-central1</td>
                          <td className="py-2.5 text-sky-300 font-bold">COLDLINE</td>
                          <td className="py-2.5 text-emerald-400 font-bold">Ahorras 75%</td>
                        </tr>
                        <tr className="hover:bg-slate-800/40">
                          <td className="py-2.5 font-medium text-purple-400 flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full bg-purple-400" />
                            gs://empresa-legal-archive
                          </td>
                          <td className="py-2.5 text-slate-300">us-central1</td>
                          <td className="py-2.5 text-purple-300">ARCHIVE</td>
                          <td className="py-2.5 text-emerald-400 font-bold">Ahorras 90%</td>
                        </tr>
                      </tbody>
                    </table>

                    {/* Simulated Click Spotlight */}
                    <div className="mt-4 p-3 bg-blue-950/40 border border-blue-500/40 rounded-lg text-[11px] text-blue-200 flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full bg-blue-400 animate-ping shrink-0" />
                      <span>
                        Simulación de puntero interactivo en video: el cursor resalta la clase <strong>COLDLINE</strong> al compilar el tutorial.
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* KIND 4: TERMINAL (Interactive Cloud Shell CLI) */}
              {activeResource.kind === 'terminal' && (
                <div className="w-full h-full p-5 bg-black font-mono text-xs flex flex-col justify-between text-slate-200">
                  <div className="flex items-center justify-between border-b border-zinc-800 pb-2 mb-3">
                    <span className="text-[11px] font-bold text-purple-400 flex items-center gap-1.5">
                      <Terminal className="w-3.5 h-3.5" /> GOOGLE CLOUD SHELL (BASH)
                    </span>
                    <span className="text-[10px] text-zinc-500">gcloud SDK 502.0</span>
                  </div>

                  <div className="space-y-2 my-auto">
                    <div className="text-zinc-500"># Ejecución automatizada para el tutorial:</div>
                    <div className="text-emerald-400 font-bold">
                      user@cloudshell:~$ gcloud storage buckets create gs://mi-empresa-backups-2025 \
                    </div>
                    <div className="text-emerald-400 pl-4">
                      --location=us-central1 \
                    </div>
                    <div className="text-emerald-400 pl-4">
                      --default-storage-class=COLDLINE
                    </div>
                    <div className="text-zinc-400 pt-2 border-t border-zinc-900 leading-relaxed">
                      Creating gs://mi-empresa-backups-2025/...<br />
                      ✓ Success! Bucket gs://mi-empresa-backups-2025/ created with storage class COLDLINE.<br />
                      AES-256 Customer-Managed / Google-Managed Encryption: ACTIVE.
                    </div>
                  </div>

                  <div className="pt-2 border-t border-zinc-900 text-[10px] text-zinc-500 flex justify-between">
                    <span>Salida renderizada directamente en el MP4</span>
                    <span className="text-purple-400">Tiempo de comando: 1.8s</span>
                  </div>
                </div>
              )}

              {/* KIND 5: CUSTOM (User Registered Resource) */}
              {activeResource.kind === 'custom' && (
                <div className="w-full h-full p-6 flex flex-col justify-between bg-gradient-to-br from-slate-950 via-purple-950/30 to-slate-900">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-pink-400 bg-pink-950/70 border border-pink-800/50 px-2.5 py-1 rounded-md flex items-center gap-1.5">
                      <Zap className="w-3 h-3" /> RECURSO PERSONALIZADO REGISTRADO
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">ID: {activeResource.id}</span>
                  </div>

                  <div className="my-auto py-4 space-y-3">
                    <h4 className="text-lg font-bold text-white">{activeResource.name}</h4>
                    <p className="text-xs text-slate-300 leading-relaxed">{activeResource.description}</p>
                    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3">
                      <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400 block mb-1">
                        Palabras clave de activación semántica:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {activeResource.intent_keywords.map((kw, i) => (
                          <span key={i} className="text-[10px] bg-indigo-950 text-indigo-300 border border-indigo-800/60 px-2 py-0.5 rounded font-mono">
                            {kw}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
                    <span>Prioridad de Despacho: {activeResource.priority}/5</span>
                    <span className="text-pink-400">Extensión modular de video</span>
                  </div>
                </div>
              )}
            </div>

            {/* Bottom Scene Inspector */}
            <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2 text-slate-300">
                <span className="text-slate-400">Triggers detectados:</span>
                <div className="flex items-center gap-1">
                  {activeResource.intent_keywords.slice(0, 4).map((kw, idx) => (
                    <span key={idx} className="bg-slate-900 text-sky-300 text-[10px] px-1.5 py-0.5 rounded border border-slate-800 font-mono">
                      {kw}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => onRunCommand(`python gcp_tutorial.py --topic "${selectedLessonKey}" --hybrid`)}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 transition shadow-md shadow-indigo-600/20"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  Renderizar Esta Lección Híbrida
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
};
