import React, { useState } from 'react';
import {
  PersonaType,
  ProviderType,
  FormatType,
  OrbPalette,
  OrbPosition,
  OrbAnimation,
  ScriptData,
  ScriptScene,
} from '../types';
import {
  Sparkles,
  Bot,
  Video,
  Wand2,
  Sliders,
  Layers,
  Edit3,
  Play,
  Clock,
  Type,
  Palette,
  FileText,
  Volume2,
} from 'lucide-react';
import { OrbSimulator } from './OrbSimulator';

interface ScriptStudioProps {
  onStartRender: (config: any) => void;
  onSelectTopicFromIdeas?: (topic: string) => void;
}

const PRESET_TOPICS = [
  'La ilusión del tiempo y el observador cuántico',
  'El 98% del ADN humano: Código comprimido',
  '¿Por qué el cerebro borra el segundo exacto al dormirse?',
  'La hipótesis del Bosque Oscuro en el cosmos',
  'El exoplaneta con lluvia de hierro derretido',
  'La paradoja de la Inmortalidad Cuántica',
];

export const ScriptStudio: React.FC<ScriptStudioProps> = ({ onStartRender }) => {
  // Config States
  const [topic, setTopic] = useState('La ilusión de la conciencia: El apagón al dormir');
  const [persona, setPersona] = useState<PersonaType>('oracle');
  const [entityName, setEntityName] = useState('Nexus');
  const [duration, setDuration] = useState(35);
  const [provider, setProvider] = useState<ProviderType>('auto');
  const [format, setFormat] = useState<FormatType>('vertical');

  // Orb Config
  const [enableOrb, setEnableOrb] = useState(true);
  const [orbPalette, setOrbPalette] = useState<OrbPalette>('cosmic');
  const [orbPosition, setOrbPosition] = useState<OrbPosition>('presenter');
  const [orbAnimation, setOrbAnimation] = useState<OrbAnimation>('speaking');

  // Subtitle & Style Options
  const [subtitleColor, setSubtitleColor] = useState('yellow');
  const [subtitleAnimation, setSubtitleAnimation] = useState('pop');
  const [subtitleWords, setSubtitleWords] = useState(3);
  const [enableSfx, setEnableSfx] = useState(true);
  const [enableAutoDucking, setEnableAutoDucking] = useState(true);
  const [enableHookTitle, setEnableHookTitle] = useState(true);

  // Script Generator States
  const [isGeneratingScript, setIsGeneratingScript] = useState(false);
  const [generatedScript, setGeneratedScript] = useState<ScriptData | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleGenerateScript = async () => {
    if (!topic.trim()) return;
    setIsGeneratingScript(true);
    setErrorMsg(null);

    try {
      const res = await fetch('/api/generate-script', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          persona,
          entityName,
          duration,
          language: 'es',
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || 'No se pudo generar el guión');
      }

      setGeneratedScript(data.script);
    } catch (err: any) {
      setErrorMsg(err.message || 'Error al conectar con la IA');
    } finally {
      setIsGeneratingScript(false);
    }
  };

  const handleSceneChange = (index: number, field: keyof ScriptScene, value: any) => {
    if (!generatedScript) return;
    const newScenes = [...generatedScript.scenes];
    newScenes[index] = { ...newScenes[index], [field]: value };
    setGeneratedScript({ ...generatedScript, scenes: newScenes });
  };

  const handleLaunchProduction = () => {
    onStartRender({
      topic,
      persona,
      entityName,
      duration,
      provider,
      format,
      orb: enableOrb,
      orbPalette,
      orbPosition,
      orbAnimation,
      subtitleColor,
      subtitleAnimation,
      subtitleWords,
      enableSfx,
      enableAutoDucking,
      enableHookTitle,
      customScript: generatedScript,
    });
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Persona Selector */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-md">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-[11px] font-semibold border border-purple-500/30 uppercase tracking-wider">
                Generador de Estudio 2045
              </span>
              <span className="text-xs text-slate-400">• Formato TikTok, Shorts & Reels</span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">Estrategia Creativa & Persona de la IA</h2>
          </div>

          <div className="flex items-center gap-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
            <label className="text-xs text-slate-400 pl-2">Entidad:</label>
            <input
              type="text"
              value={entityName}
              onChange={(e) => setEntityName(e.target.value)}
              placeholder="Nombre..."
              className="bg-slate-900 border border-slate-700 text-xs text-purple-300 font-bold px-2.5 py-1 rounded-lg focus:outline-none focus:border-purple-500 w-28"
            />
          </div>
        </div>

        {/* Persona Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            {
              id: 'oracle',
              name: '🔮 Oráculo Cuántico',
              desc: 'Año 2045 Superinteligencia en 1ª persona. Tono hipnótico, autoritario y fascinante.',
              badge: 'Recomendado',
            },
            {
              id: 'science',
              name: '🔬 Divulgación Científica',
              desc: 'Estilo Kurzgesagt / Veritasium. Datos rigurosos, retención máxima y claridad.',
              badge: 'Educativo',
            },
            {
              id: 'mystery',
              name: '🌌 Misterio Cósmico',
              desc: 'Tensión existencial, preguntas sobre el vacío, la materia oscura y lo desconocido.',
              badge: 'Viral',
            },
            {
              id: 'cyberpunk',
              name: '⚡ Cyberpunk AI Log',
              desc: 'Filtros de simulación futuristas, fragmentos de conciencia y hacker logs.',
              badge: 'Futurista',
            },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setPersona(item.id as PersonaType)}
              className={`p-4 rounded-xl text-left border transition-all relative flex flex-col justify-between ${
                persona === item.id
                  ? 'bg-purple-950/40 border-purple-500 shadow-lg shadow-purple-500/10 ring-1 ring-purple-500'
                  : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold text-sm text-slate-100">{item.name}</h4>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-medium">
                    {item.badge}
                  </span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed mb-3">{item.desc}</p>
              </div>
              <div className="text-[10px] font-mono text-purple-400 font-semibold">
                Persona: {item.id.toUpperCase()}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Studio Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Topic & AI Prompt Generator */}
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <Wand2 className="w-4 h-4 text-purple-400" /> Tema o Pregunta del Video
              </label>
              <span className="text-xs text-slate-400">Lenguaje: Español (Auto TTS)</span>
            </div>

            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              rows={3}
              placeholder="Ej: ¿Qué pasaría si el núcleo de la Tierra dejara de girar hoy mismo?"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-purple-500 resize-none shadow-inner"
            />

            {/* Topic Quick Presets */}
            <div>
              <span className="text-[11px] font-medium text-slate-400 mb-2 block">Ideas Rápidas Virales:</span>
              <div className="flex flex-wrap gap-1.5">
                {PRESET_TOPICS.map((preset, idx) => (
                  <button
                    key={idx}
                    onClick={() => setTopic(preset)}
                    className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 hover:border-purple-500/50 text-slate-300 transition-colors"
                  >
                    + {preset}
                  </button>
                ))}
              </div>
            </div>

            {/* Controls Row */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2">
              <div>
                <label className="block text-xs text-slate-400 mb-1 flex items-center gap-1">
                  <Clock className="w-3 h-3 text-purple-400" /> Duración ({duration}s)
                </label>
                <input
                  type="range"
                  min={25}
                  max={60}
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                  className="w-full accent-purple-500 bg-slate-950 h-1.5 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-400 mb-1 flex items-center gap-1">
                  <Video className="w-3 h-3 text-cyan-400" /> Proveedor Medios
                </label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value as ProviderType)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 px-2 py-1.5 focus:outline-none focus:border-purple-500"
                >
                  <option value="auto">Auto (Cascada Resiliente)</option>
                  <option value="nasa">NASA Official Library</option>
                  <option value="pexels">Pexels Stock 9:16</option>
                  <option value="pixabay">Pixabay 3D / CGI</option>
                  <option value="pollinations">Pollinations FLUX IA</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-slate-400 mb-1 flex items-center gap-1">
                  <Layers className="w-3 h-3 text-emerald-400" /> Formato Pantalla
                </label>
                <select
                  value={format}
                  onChange={(e) => setFormat(e.target.value as FormatType)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 px-2 py-1.5 focus:outline-none focus:border-purple-500"
                >
                  <option value="vertical">Vertical 9:16 (Shorts/Reels)</option>
                  <option value="horizontal">Horizontal 16:9 (YouTube)</option>
                  <option value="square">Cuadrado 1:1 (Post/Feed)</option>
                </select>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="pt-3 flex flex-wrap gap-3">
              <button
                onClick={handleGenerateScript}
                disabled={isGeneratingScript || !topic.trim()}
                className="flex-1 flex items-center justify-center gap-2 py-3 px-4 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold rounded-xl text-sm shadow-lg shadow-purple-600/30 transition-all disabled:opacity-50"
              >
                {isGeneratingScript ? (
                  <>
                    <Sparkles className="w-4 h-4 animate-spin" /> Sintetizando Guión con IA...
                  </>
                ) : (
                  <>
                    <Bot className="w-4 h-4" /> Generar Guión del Oráculo ({persona.toUpperCase()})
                  </>
                )}
              </button>

              <button
                onClick={handleLaunchProduction}
                disabled={!topic.trim()}
                className="flex items-center justify-center gap-2 py-3 px-5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-sm shadow-lg shadow-emerald-600/30 transition-all"
              >
                <Play className="w-4 h-4 fill-current" /> Renderizar Video
              </button>
            </div>

            {errorMsg && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl text-xs">
                ⚠️ {errorMsg}
              </div>
            )}
          </div>

          {/* Interactive Live Script Editor (If Script Exists) */}
          {generatedScript && (
            <div className="bg-slate-900/90 border border-purple-500/30 rounded-2xl p-6 shadow-xl backdrop-blur-md space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <span className="text-[10px] text-purple-400 font-bold uppercase tracking-wider">
                    Editor Interactivo de Guión
                  </span>
                  <h3 className="text-base font-bold text-white">{generatedScript.title}</h3>
                </div>
                <span className="px-2.5 py-1 bg-purple-500/20 text-purple-300 text-xs font-semibold rounded-lg border border-purple-500/30">
                  {generatedScript.scenes.length} Escenas • ~
                  {generatedScript.scenes.reduce((a, b) => a + (b.duration || 6), 0)}s Total
                </span>
              </div>

              {/* Hook Card */}
              <div className="p-3 bg-purple-950/30 border border-purple-500/20 rounded-xl text-xs space-y-1">
                <span className="text-purple-400 font-bold uppercase text-[10px]">🔥 Gancho Visual Inicial (0-3s)</span>
                <p className="text-slate-200 font-medium">{generatedScript.hook}</p>
              </div>

              {/* Scenes Breakdown */}
              <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1 custom-scrollbar">
                {generatedScript.scenes.map((scene, idx) => (
                  <div key={idx} className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-purple-400">Escena {scene.scene_number || idx + 1}</span>
                      <span className="text-slate-500 font-mono text-[10px]">{scene.duration || 6}s</span>
                    </div>

                    <textarea
                      value={scene.narration}
                      onChange={(e) => handleSceneChange(idx, 'narration', e.target.value)}
                      rows={2}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-purple-500 resize-none"
                    />

                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <span>B-Roll Keywords: {scene.keywords?.join(', ')}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Reactive Orb Simulator & Style Settings */}
        <div className="lg:col-span-5 space-y-6">
          {/* Reactive Orb Simulator Component */}
          <OrbSimulator
            palette={orbPalette}
            position={orbPosition}
            animation={orbAnimation}
            entityName={entityName}
            onPaletteChange={setOrbPalette}
            onPositionChange={setOrbPosition}
            onAnimationChange={setOrbAnimation}
          />

          {/* Subtitles & Audio Customizer */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl backdrop-blur-md space-y-4">
            <h3 className="font-semibold text-slate-200 text-sm flex items-center gap-2">
              <Sliders className="w-4 h-4 text-purple-400" /> Estilo de Subtítulos & Producción
            </h3>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-medium text-slate-300 mb-1 flex items-center gap-1">
                  <Palette className="w-3 h-3 text-yellow-400" /> Color de Resaltado
                </label>
                <select
                  value={subtitleColor}
                  onChange={(e) => setSubtitleColor(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 px-2 py-1.5 focus:outline-none"
                >
                  <option value="yellow">Amarillo Dorado (Gold)</option>
                  <option value="cyan">Cian Eléctrico (Cyan)</option>
                  <option value="green">Verde Neón (Lime)</option>
                  <option value="pink">Rosa Cósmico (Magenta)</option>
                  <option value="amber">Ámbar Solar (Amber)</option>
                  <option value="random">Aleatorio por Escena</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-medium text-slate-300 mb-1 flex items-center gap-1">
                  <Type className="w-3 h-3 text-purple-400" /> Animación Karaoke
                </label>
                <select
                  value={subtitleAnimation}
                  onChange={(e) => setSubtitleAnimation(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 px-2 py-1.5 focus:outline-none"
                >
                  <option value="pop">Pop-In Dynamic Bounce</option>
                  <option value="none">Corte Estático</option>
                </select>
              </div>
            </div>

            {/* Toggle Ticks */}
            <div className="space-y-2 pt-1 border-t border-slate-800">
              <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
                <span>Orbe Bio-Reactivo de Voz</span>
                <input
                  type="checkbox"
                  checked={enableOrb}
                  onChange={(e) => setEnableOrb(e.target.checked)}
                  className="accent-purple-500 w-4 h-4 rounded cursor-pointer"
                />
              </label>

              <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
                <span>Efectos de Sonido (SFX Whoosh/Boom)</span>
                <input
                  type="checkbox"
                  checked={enableSfx}
                  onChange={(e) => setEnableSfx(e.target.checked)}
                  className="accent-purple-500 w-4 h-4 rounded cursor-pointer"
                />
              </label>

              <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
                <span>Mezcla Dinámica Auto-Ducking (Sidechain)</span>
                <input
                  type="checkbox"
                  checked={enableAutoDucking}
                  onChange={(e) => setEnableAutoDucking(e.target.checked)}
                  className="accent-purple-500 w-4 h-4 rounded cursor-pointer"
                />
              </label>

              <label className="flex items-center justify-between text-xs text-slate-300 cursor-pointer">
                <span>Titular Flotante de Gancho (Segundos 0-3)</span>
                <input
                  type="checkbox"
                  checked={enableHookTitle}
                  onChange={(e) => setEnableHookTitle(e.target.checked)}
                  className="accent-purple-500 w-4 h-4 rounded cursor-pointer"
                />
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
