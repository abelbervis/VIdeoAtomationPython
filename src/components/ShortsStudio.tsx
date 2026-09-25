import React, { useState, useEffect, useRef } from 'react';
import { VideoScript, ScriptScene, EntityId } from '../types';
import { ENTITY_CHARACTERS } from '../data/characters';
import { soundEngine } from '../utils/audioSynth';
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  RotateCcw,
  Sparkles,
  Layers,
  Plus,
  Trash2,
  Image as ImageIcon,
  Volume2,
  VolumeX,
  Clock,
  Sparkle,
  Radio,
  Sliders,
  CheckCircle2,
  Eye,
  Send,
} from 'lucide-react';

interface ShortsStudioProps {
  currentScript: VideoScript;
  onUpdateScript: (script: VideoScript) => void;
  onSelectNASAMediaForScene?: (sceneIndex: number) => void;
  onGenerateAIScript: (topic: string) => void;
}

export const ShortsStudio: React.FC<ShortsStudioProps> = ({
  currentScript,
  onUpdateScript,
  onSelectNASAMediaForScene,
  onGenerateAIScript,
}) => {
  const [activeSceneIndex, setActiveSceneIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [sceneProgress, setSceneProgress] = useState(0); // 0 to 1
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const [isGeneratingAI, setIsGeneratingAI] = useState(false);
  const [customTopicInput, setCustomTopicInput] = useState('');
  const [showAiModal, setShowAiModal] = useState(false);

  const scene = currentScript.scenes[activeSceneIndex] || currentScript.scenes[0];
  const presenter = scene?.presenter !== 'both' && scene?.presenter !== 'narrator'
    ? ENTITY_CHARACTERS[scene.presenter as EntityId]
    : scene?.presenter === 'narrator'
    ? ENTITY_CHARACTERS.narrator
    : ENTITY_CHARACTERS.quantum;

  const currentWords = (scene?.narration || '').split(' ');
  const timerRef = useRef<number | null>(null);
  const progressIntervalRef = useRef<number | null>(null);

  // Play narration via Speech Synthesis & trigger SFX
  const playCurrentSceneNarration = () => {
    if (!scene) return;

    // SFX
    if (scene.sfx === 'boom' || activeSceneIndex === 0) {
      soundEngine.playBoom();
    } else if (scene.sfx === 'whoosh') {
      soundEngine.playWhoosh();
    }

    if (!isVoiceEnabled) return;

    soundEngine.stopSpeaking();
    const duration = scene.duration || 5;

    // Calculate approximate word boundary timing
    let charCounter = 0;
    soundEngine.speak(scene.narration, {
      pitch: presenter?.id === 'solar' ? 1.15 : presenter?.id === 'void' ? 0.75 : 0.95,
      rate: 1.08,
      onBoundary: (charIdx) => {
        // Approximate which word is being spoken
        const textUpToChar = scene.narration.substring(0, charIdx);
        const wIdx = textUpToChar.trim().split(/\s+/).length - 1;
        setCurrentWordIndex(Math.max(0, wIdx));
      },
      onEnd: () => {
        if (isPlaying) {
          handleNextScene();
        }
      },
    });
  };

  const handleNextScene = () => {
    if (activeSceneIndex < currentScript.scenes.length - 1) {
      setActiveSceneIndex((prev) => prev + 1);
      setSceneProgress(0);
      setCurrentWordIndex(0);
    } else {
      // Loop or stop
      setIsPlaying(false);
      soundEngine.stopSpeaking();
      setActiveSceneIndex(0);
      setSceneProgress(0);
      setCurrentWordIndex(0);
    }
  };

  const handlePrevScene = () => {
    if (activeSceneIndex > 0) {
      setActiveSceneIndex((prev) => prev - 1);
      setSceneProgress(0);
      setCurrentWordIndex(0);
    }
  };

  // Trigger playback when active scene changes while playing
  useEffect(() => {
    if (isPlaying) {
      playCurrentSceneNarration();

      // Progress bar animation
      const durationMs = (scene?.duration || 5) * 1000;
      const startTime = performance.now();
      
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = window.setInterval(() => {
        const elapsed = performance.now() - startTime;
        const p = Math.min(1, elapsed / durationMs);
        setSceneProgress(p);
        if (p >= 1 && !isVoiceEnabled) {
          handleNextScene();
        }
      }, 50);
    } else {
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
      soundEngine.stopSpeaking();
    }

    return () => {
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
    };
  }, [isPlaying, activeSceneIndex]);

  const togglePlay = () => {
    if (!isPlaying) {
      setIsPlaying(true);
    } else {
      setIsPlaying(false);
      soundEngine.stopSpeaking();
    }
  };

  const updateSceneField = (index: number, field: keyof ScriptScene, value: any) => {
    const updatedScenes = [...currentScript.scenes];
    updatedScenes[index] = { ...updatedScenes[index], [field]: value };
    onUpdateScript({ ...currentScript, scenes: updatedScenes });
  };

  const handleAddScene = () => {
    const newScene: ScriptScene = {
      id: `scene-${Date.now()}`,
      sceneNumber: currentScript.scenes.length + 1,
      presenter: 'quantum',
      narration: 'Las fluctuaciones en el vacío cósmico revelan nuevos horizontes relativistas.',
      visualKeywords: ['space singularity', 'quantum foam', 'nebula particles'],
      visualPrompt: 'Cinematic glowing cosmic anomaly with quantum particles',
      camera: 'wide',
      duration: 6,
      mediaTitle: 'Observación Infrarroja NASA',
      mediaSource: 'NASA / ESA',
      mediaDate: '2026',
      mediaUrl: 'https://images-assets.nasa.gov/image/GSFC_20190925_m13437_BlackHole/GSFC_20190925_m13437_BlackHole~orig.jpg',
      sfx: 'whoosh',
    };
    onUpdateScript({
      ...currentScript,
      scenes: [...currentScript.scenes, newScene],
      duration: currentScript.duration + newScene.duration,
    });
  };

  const handleDeleteScene = (index: number) => {
    if (currentScript.scenes.length <= 1) return;
    const updatedScenes = currentScript.scenes.filter((_, i) => i !== index);
    onUpdateScript({ ...currentScript, scenes: updatedScenes });
    if (activeSceneIndex >= updatedScenes.length) {
      setActiveSceneIndex(updatedScenes.length - 1);
    }
  };

  const handleGenerateAiTopic = (topic: string) => {
    setIsGeneratingAI(true);
    setTimeout(() => {
      onGenerateAIScript(topic);
      setIsGeneratingAI(false);
      setShowAiModal(false);
      setActiveSceneIndex(0);
      setSceneProgress(0);
    }, 600);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      {/* LEFT COLUMN: 9:16 VERTICAL VIDEO PLAYER PREVIEW */}
      <div className="lg:col-span-5 flex flex-col items-center">
        {/* Phone Frame Mockup (9:16 Aspect Ratio) */}
        <div className="relative w-full max-w-[340px] aspect-[9/16] rounded-3xl overflow-hidden bg-black border-2 border-slate-700/80 shadow-[0_0_35px_rgba(0,0,0,0.8),0_0_15px_rgba(0,240,255,0.15)] flex flex-col justify-between select-none">
          {/* Top Notch / Time Bar */}
          <div className="absolute top-0 inset-x-0 z-30 flex items-center justify-between px-5 pt-3 text-[10px] font-mono text-slate-300 pointer-events-none">
            <span className="flex items-center gap-1.5 font-bold tracking-wider">
              <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
              9:16 REC
            </span>
            <span className="bg-black/60 px-2 py-0.5 rounded-full border border-white/10 text-slate-300">
              {scene?.camera.toUpperCase().replace('_', ' ')}
            </span>
            <span>30 FPS</span>
          </div>

          {/* Background Media with Smooth Ken Burns Drift Effect */}
          <div className="absolute inset-0 z-0 overflow-hidden bg-slate-950">
            {scene?.mediaUrl ? (
              <img
                src={scene.mediaUrl}
                alt={scene.mediaTitle || 'NASA Scene'}
                className="w-full h-full object-cover transition-transform duration-[6000ms] ease-out scale-105 animate-pulse"
                style={{
                  animationDuration: `${(scene.duration || 5) + 2}s`,
                  transform: isPlaying ? 'scale(1.18) translate(-1.5%, 1.5%)' : 'scale(1.04)',
                }}
              />
            ) : (
              <div className="w-full h-full bg-gradient-to-b from-[#06070B] via-[#0D1117] to-[#040508]" />
            )}

            {/* Cinematic Gradient Overlays */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-black/60" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_40%,rgba(0,0,0,0.7)_100%)]" />
          </div>

          {/* TOP THIRD: Dynamic Hook Title Overlay (Scene 1) & Attribution Badge */}
          <div className="relative z-20 pt-10 px-4 space-y-2 pointer-events-none">
            {/* NASA Attribution Badge */}
            <div className="inline-flex items-center gap-1.5 rounded-full bg-black/60 backdrop-blur-md px-3 py-1 border border-white/15 text-[10px] font-mono text-slate-200 shadow-lg">
              <Radio className="h-3 w-3 text-cyan-400 animate-pulse" />
              <span className="font-semibold text-cyan-300">{scene?.mediaSource || 'NASA Official'}</span>
              <span className="text-slate-400">·</span>
              <span className="text-slate-300">{scene?.mediaDate || '2026'}</span>
            </div>

            {/* Hook Headline (Scene 1 only) */}
            {activeSceneIndex === 0 && currentScript.hookTitle && (
              <div className="animate-in fade-in slide-in-from-top-3 duration-500 rounded-xl bg-gradient-to-r from-red-600/90 via-purple-600/90 to-blue-600/90 p-[1px] shadow-2xl">
                <div className="rounded-[11px] bg-black/85 backdrop-blur-md px-3 py-2 text-center">
                  <span className="text-[11px] font-black uppercase tracking-wider text-amber-300 drop-shadow-[0_2px_8px_rgba(255,200,0,0.5)]">
                    {currentScript.hookTitle}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* CENTER: Reactive Floating Orb Entity */}
          <div className="relative z-20 flex flex-col items-center justify-center my-auto pointer-events-none">
            <div className="relative flex items-center justify-center">
              {/* Outer Acoustic Pulse Waves (when speaking) */}
              {isPlaying && (
                <>
                  <div
                    className="absolute h-36 w-36 rounded-full border border-dashed opacity-40 animate-ping"
                    style={{
                      borderColor: presenter.primary_color,
                      animationDuration: '1.4s',
                    }}
                  />
                  <div
                    className="absolute h-28 w-28 rounded-full border opacity-50 animate-pulse"
                    style={{
                      borderColor: presenter.glow_color,
                      boxShadow: `0 0 25px ${presenter.glow_color}`,
                    }}
                  />
                </>
              )}

              {/* Core Singularity Orb */}
              <div
                className="relative h-20 w-20 rounded-full transition-transform duration-300 flex items-center justify-center shadow-2xl"
                style={{
                  background: `radial-gradient(circle at 35% 35%, #FFFFFF 0%, ${presenter.primary_color} 40%, ${presenter.accent_color} 80%, #000000 100%)`,
                  boxShadow: `0 0 35px ${presenter.glow_color}, 0 0 15px ${presenter.primary_color}`,
                  transform: isPlaying ? 'scale(1.12)' : 'scale(1.0)',
                }}
              >
                {/* Rotating astrometric rings */}
                <div
                  className="absolute inset-[-6px] rounded-full border border-dashed opacity-60 animate-spin"
                  style={{
                    borderColor: presenter.primary_color,
                    animationDuration: '8s',
                  }}
                />
              </div>
            </div>

            {/* Presenter Name Badge */}
            <div
              className="mt-3 rounded-full px-3 py-0.5 text-[10px] font-mono font-bold tracking-widest uppercase backdrop-blur-md border shadow-lg"
              style={{
                backgroundColor: 'rgba(0,0,0,0.7)',
                borderColor: presenter.primary_color,
                color: presenter.primary_color,
              }}
            >
              {presenter.name} · {presenter.drone_freq}Hz
            </div>
          </div>

          {/* BOTTOM THIRD: Dynamic Pop-In Karaoke Subtitles */}
          <div className="relative z-20 px-4 pb-8 text-center pointer-events-none">
            <div className="min-h-[85px] flex flex-col justify-end items-center">
              <div className="flex flex-wrap items-center justify-center gap-x-1.5 gap-y-1 bg-black/65 backdrop-blur-md rounded-2xl px-4 py-3 border border-white/10 shadow-2xl">
                {currentWords.map((word, wIdx) => {
                  const isCurrent = isPlaying && wIdx === currentWordIndex;
                  const isPast = isPlaying && wIdx < currentWordIndex;
                  return (
                    <span
                      key={wIdx}
                      className={`text-sm sm:text-base font-black tracking-wide uppercase transition-all duration-150 ${
                        isCurrent
                          ? 'text-yellow-300 scale-110 drop-shadow-[0_0_12px_rgba(255,230,0,0.9)] underline decoration-yellow-400 decoration-2'
                          : isPast
                          ? 'text-white drop-shadow-[0_1px_4px_rgba(0,0,0,0.9)]'
                          : 'text-slate-300/80 drop-shadow-[0_1px_4px_rgba(0,0,0,0.9)]'
                      }`}
                    >
                      {word}
                    </span>
                  );
                })}
              </div>
            </div>

            {/* Scene Index & Total Time */}
            <div className="mt-3 flex items-center justify-between text-[10px] font-mono text-slate-400 px-1">
              <span>
                Escena {activeSceneIndex + 1}/{currentScript.scenes.length}
              </span>
              <span>
                {Math.round(sceneProgress * (scene?.duration || 5))}s / {scene?.duration || 5}s
              </span>
            </div>

            {/* Micro Scene Progress Bar */}
            <div className="mt-1 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-400 to-yellow-400 transition-all duration-100"
                style={{ width: `${sceneProgress * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* PLAYER CONTROLS DOCK */}
        <div className="w-full max-w-[340px] mt-4 flex items-center justify-between gap-2 rounded-2xl bg-slate-900/80 p-2.5 border border-slate-800 shadow-xl backdrop-blur-md">
          <button
            id="btn-prev-scene"
            onClick={handlePrevScene}
            disabled={activeSceneIndex === 0}
            className="p-2 rounded-xl text-slate-400 hover:text-cyan-300 hover:bg-slate-800 disabled:opacity-30 transition-all"
            title="Escena Anterior"
          >
            <SkipBack className="h-4 w-4" />
          </button>

          <button
            id="btn-play-pause-short"
            onClick={togglePlay}
            className="flex items-center justify-center h-10 w-10 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-[0_0_15px_rgba(0,240,255,0.4)] hover:brightness-110 active:scale-95 transition-all"
            title={isPlaying ? 'Pausar' : 'Reproducir Escena & Voz'}
          >
            {isPlaying ? <Pause className="h-5 w-5 fill-current" /> : <Play className="h-5 w-5 fill-current ml-0.5" />}
          </button>

          <button
            id="btn-next-scene"
            onClick={handleNextScene}
            disabled={activeSceneIndex === currentScript.scenes.length - 1}
            className="p-2 rounded-xl text-slate-400 hover:text-cyan-300 hover:bg-slate-800 disabled:opacity-30 transition-all"
            title="Siguiente Escena"
          >
            <SkipForward className="h-4 w-4" />
          </button>

          <div className="h-5 w-[1px] bg-slate-800" />

          {/* Narration voice toggle */}
          <button
            id="btn-voice-toggle"
            onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}
            className={`p-2 rounded-xl transition-all ${
              isVoiceEnabled ? 'text-cyan-400 bg-cyan-950/40 border border-cyan-500/30' : 'text-slate-500 hover:text-slate-300'
            }`}
            title={isVoiceEnabled ? 'Voz TTS activada' : 'Voz TTS silenciada'}
          >
            {isVoiceEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
          </button>

          <button
            id="btn-reset-playback"
            onClick={() => {
              setActiveSceneIndex(0);
              setSceneProgress(0);
              setCurrentWordIndex(0);
              soundEngine.stopSpeaking();
              setIsPlaying(false);
            }}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-all"
            title="Reiniciar desde el inicio"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* RIGHT COLUMN: SCRIPT TIMELINE & SCENE WORKSHOP */}
      <div className="lg:col-span-7 space-y-4">
        {/* SCRIPT HEADER CARD */}
        <div className="rounded-2xl bg-slate-900/60 p-4 border border-slate-800/80 backdrop-blur-md space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <div className="flex items-center gap-2">
                <span className="rounded bg-purple-500/10 px-2 py-0.5 text-[10px] font-mono text-purple-400 border border-purple-500/30">
                  {currentScript.category}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  Duración Total: ~{currentScript.duration}s ({currentScript.scenes.length} escenas)
                </span>
              </div>
              <h2 className="text-lg font-bold text-slate-100 mt-1">{currentScript.title}</h2>
            </div>

            <button
              id="btn-open-ai-generator"
              onClick={() => setShowAiModal(true)}
              className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-lg hover:brightness-110 active:scale-95 transition-all"
            >
              <Sparkles className="h-3.5 w-3.5" />
              <span>Generar con IA</span>
            </button>
          </div>

          {/* Hook Input Field */}
          <div>
            <label className="text-[11px] font-mono text-slate-400 block mb-1">
              ⚡ Gancho Inicial de 3 Segundos (Hook Title Overlay):
            </label>
            <input
              id="input-hook-title"
              type="text"
              value={currentScript.hookTitle}
              onChange={(e) => onUpdateScript({ ...currentScript, hookTitle: e.target.value })}
              className="w-full rounded-xl bg-slate-950/80 border border-slate-800 px-3 py-2 text-xs font-semibold text-yellow-400 focus:outline-none focus:border-cyan-500/50"
              placeholder="E.g. ¿QUÉ PASA SI CAES A UN AGUJERO NEGRO?"
            />
          </div>
        </div>

        {/* SCENES TIMELINE CARDS */}
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Layers className="h-3.5 w-3.5 text-cyan-400" />
              Línea de Tiempo de Escenas
            </span>
            <button
              id="btn-add-scene"
              onClick={handleAddScene}
              className="flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300 font-medium transition-colors"
            >
              <Plus className="h-3.5 w-3.5" />
              <span>Añadir Escena</span>
            </button>
          </div>

          <div className="space-y-3 max-h-[560px] overflow-y-auto pr-1">
            {currentScript.scenes.map((s, idx) => {
              const isActive = activeSceneIndex === idx;
              const scenePresenter = s.presenter !== 'both' && s.presenter !== 'narrator'
                ? ENTITY_CHARACTERS[s.presenter as EntityId]
                : s.presenter === 'narrator'
                ? ENTITY_CHARACTERS.narrator
                : ENTITY_CHARACTERS.quantum;

              return (
                <div
                  key={s.id}
                  onClick={() => {
                    setActiveSceneIndex(idx);
                    setSceneProgress(0);
                    setCurrentWordIndex(0);
                  }}
                  className={`rounded-2xl p-4 transition-all border cursor-pointer ${
                    isActive
                      ? 'bg-slate-900/90 border-cyan-500/50 shadow-[0_0_20px_rgba(0,240,255,0.12)]'
                      : 'bg-slate-900/40 border-slate-800 hover:bg-slate-900/70 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span
                        className="flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-mono font-bold"
                        style={{
                          backgroundColor: `${scenePresenter.primary_color}25`,
                          color: scenePresenter.primary_color,
                          border: `1px solid ${scenePresenter.primary_color}60`,
                        }}
                      >
                        {idx + 1}
                      </span>

                      {/* Presenter Selector */}
                      <select
                        value={s.presenter}
                        onChange={(e) => updateSceneField(idx, 'presenter', e.target.value as EntityId)}
                        onClick={(e) => e.stopPropagation()}
                        className="rounded-lg bg-slate-950 border border-slate-800 px-2 py-1 text-[11px] font-mono font-semibold focus:outline-none focus:border-cyan-500"
                        style={{ color: scenePresenter.primary_color }}
                      >
                        <option value="quantum">QUANTUM (Cian)</option>
                        <option value="solar">SOLAR (Ámbar)</option>
                        <option value="neural">NEURAL (Púrpura)</option>
                        <option value="gaia">GAIA (Esmeralda)</option>
                        <option value="void">VOID (Carmesí)</option>
                        <option value="narrator">NARRADOR (Dorado)</option>
                      </select>

                      {/* Duration */}
                      <div className="flex items-center gap-1 text-[10px] font-mono text-slate-400 bg-slate-950/60 px-2 py-1 rounded-lg border border-slate-800">
                        <Clock className="h-3 w-3" />
                        <input
                          type="number"
                          min={2}
                          max={15}
                          value={s.duration}
                          onChange={(e) => updateSceneField(idx, 'duration', parseInt(e.target.value) || 5)}
                          onClick={(e) => e.stopPropagation()}
                          className="w-8 bg-transparent text-center focus:outline-none text-slate-200"
                        />
                        <span>s</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                      {onSelectNASAMediaForScene && (
                        <button
                          onClick={() => onSelectNASAMediaForScene(idx)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-300 hover:bg-slate-800 transition-all text-[11px] flex items-center gap-1"
                          title="Cambiar imagen de la NASA"
                        >
                          <ImageIcon className="h-3.5 w-3.5" />
                          <span className="hidden sm:inline">NASA Asset</span>
                        </button>
                      )}

                      {currentScript.scenes.length > 1 && (
                        <button
                          onClick={() => handleDeleteScene(idx)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-950/30 transition-all"
                          title="Eliminar escena"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Narration Textarea */}
                  <textarea
                    value={s.narration}
                    onChange={(e) => updateSceneField(idx, 'narration', e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                    rows={2}
                    className="w-full rounded-xl bg-slate-950/70 border border-slate-800/80 p-2.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50 resize-none font-sans"
                    placeholder="Escribe la narración para esta escena..."
                  />

                  {/* Media Info Footer */}
                  <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-[10px] font-mono text-slate-400">
                    <span className="truncate max-w-[260px]">
                      🌌 {s.mediaTitle || 'Simulación Cósmica NASA'} ({s.mediaDate || '2026'})
                    </span>

                    <div className="flex items-center gap-1.5">
                      <span className="text-slate-500">SFX:</span>
                      <select
                        value={s.sfx || 'whoosh'}
                        onChange={(e) => updateSceneField(idx, 'sfx', e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        className="bg-slate-950 rounded px-1.5 py-0.5 border border-slate-800 text-slate-300 text-[10px] focus:outline-none"
                      >
                        <option value="whoosh">Whoosh</option>
                        <option value="boom">Boom</option>
                        <option value="none">Sin SFX</option>
                      </select>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* AI SCRIPT GENERATOR MODAL */}
      {showAiModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in">
          <div className="w-full max-w-lg rounded-3xl bg-slate-900 border border-purple-500/30 p-6 shadow-[0_0_50px_rgba(147,51,234,0.3)] space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  <Sparkles className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-100">Generador de Guiones Cósmicos</h3>
                  <p className="text-xs text-slate-400 font-mono">Escribe un tema astronómico o elige una sugerencia viral</p>
                </div>
              </div>
              <button
                onClick={() => setShowAiModal(false)}
                className="text-slate-400 hover:text-slate-200 text-sm font-mono"
              >
                ✕
              </button>
            </div>

            {/* Custom Prompt Input */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-300">Tema o Pregunta Provocadora:</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={customTopicInput}
                  onChange={(e) => setCustomTopicInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && customTopicInput && handleGenerateAiTopic(customTopicInput)}
                  placeholder="E.g. ¿Qué pasaría si la Tierra deja de girar?"
                  className="flex-1 rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-purple-500"
                />
                <button
                  onClick={() => customTopicInput && handleGenerateAiTopic(customTopicInput)}
                  disabled={!customTopicInput || isGeneratingAI}
                  className="flex items-center gap-1 rounded-xl bg-purple-600 px-4 py-2 text-xs font-semibold text-white hover:bg-purple-500 disabled:opacity-40 transition-all"
                >
                  <Send className="h-3.5 w-3.5" />
                  <span>Generar</span>
                </button>
              </div>
            </div>

            {/* Viral Presets */}
            <div className="space-y-2">
              <span className="text-[11px] font-mono text-slate-400">⚡ Temas Virales Sugeridos:</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {[
                  '¿Y si el Sol se apagara por 8 minutos?',
                  'La Paradoja del Horizonte de Sucesos',
                  'El Océano Oculto de Encélado',
                  'James Webb y las Primeras Galaxias',
                  '¿Podemos viajar más rápido que la luz?',
                  'Materia Oscura y la Mente Cósmica',
                ].map((preset, i) => (
                  <button
                    key={i}
                    onClick={() => handleGenerateAiTopic(preset)}
                    className="flex items-center justify-between rounded-xl bg-slate-950/80 p-2.5 border border-slate-800 text-left text-xs text-slate-300 hover:text-purple-300 hover:border-purple-500/40 hover:bg-purple-950/20 transition-all group"
                  >
                    <span className="truncate mr-2">{preset}</span>
                    <Sparkle className="h-3 w-3 text-purple-400 opacity-0 group-hover:opacity-100 shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
