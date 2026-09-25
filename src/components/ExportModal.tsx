import React, { useState } from 'react';
import { VideoScript, SimulatorConfig } from '../types';
import { ENTITY_CHARACTERS } from '../data/characters';
import {
  Terminal,
  Copy,
  Check,
  Download,
  FileCode,
  FileText,
  Boxes,
  Sparkles,
  Layers,
} from 'lucide-react';

interface ExportModalProps {
  currentScript: VideoScript;
  config: SimulatorConfig;
}

export const ExportModal: React.FC<ExportModalProps> = ({ currentScript, config }) => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const charA = ENTITY_CHARACTERS[config.activeEntityA];

  // Build exact CLI command
  const cliCommand = `python main.py --topic "${currentScript.topic || currentScript.title}" --duration ${currentScript.duration} --orb --orb-palette ${charA.palette_name} --hook-title "${currentScript.hookTitle}" --subtitle-animation pop`;

  // Build Docker Compose command
  const dockerCommand = `docker compose run --rm nasa-shorts --topic "${currentScript.topic || currentScript.title}" --orb --orb-palette ${charA.palette_name}`;

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // Generate SRT Content
  const generateSRT = (): string => {
    let srt = '';
    let currentTime = 0;

    currentScript.scenes.forEach((scene, idx) => {
      const startSec = currentTime;
      const endSec = currentTime + (scene.duration || 5);
      currentTime = endSec;

      const formatTime = (seconds: number) => {
        const hrs = String(Math.floor(seconds / 3600)).padStart(2, '0');
        const mins = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
        const secs = String(Math.floor(seconds % 60)).padStart(2, '0');
        const ms = String(Math.floor((seconds % 1) * 1000)).padStart(3, '0');
        return `${hrs}:${mins}:${secs},${ms}`;
      };

      srt += `${idx + 1}\n${formatTime(startSec)} --> ${formatTime(endSec)}\n${scene.narration}\n\n`;
    });

    return srt;
  };

  // Generate ASS Content
  const generateASS = (): string => {
    return `[Script Info]
Title: ${currentScript.title}
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,72,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,60,60,220,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
${currentScript.scenes
  .map((s, i) => `Dialogue: 0,0:00:0${i * 5}.00,0:00:0${(i + 1) * 5}.00,Default,,0,0,0,,{\\k50}${s.narration}`)
  .join('\n')}
`;
  };

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* HEADER */}
      <div className="rounded-3xl bg-slate-900/80 p-6 border border-cyan-500/20 backdrop-blur-md shadow-2xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                <Terminal className="h-3.5 w-3.5" />
              </span>
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-cyan-400">
                CLI Integration & Deliverables Suite
              </span>
            </div>
            <h2 className="text-2xl font-bold text-slate-100 mt-1">Exportación y Comandos de Terminal</h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Ejecuta el renderizado de alta fidelidad en FFmpeg local o exporta los guiones y subtítulos generados
            </p>
          </div>
        </div>
      </div>

      {/* CLI COMMANDS */}
      <div className="grid grid-cols-1 gap-4">
        {/* Python CLI Command */}
        <div className="rounded-3xl bg-slate-900/70 p-6 border border-slate-800 backdrop-blur-md space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-cyan-400 flex items-center gap-2">
              <Terminal className="h-4 w-4" />
              Comando CLI Python (main.py):
            </span>
            <button
              onClick={() => copyToClipboard(cliCommand, 'cli')}
              className="flex items-center gap-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 px-3 py-1.5 text-xs font-mono transition-all"
            >
              {copiedKey === 'cli' ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
              <span>{copiedKey === 'cli' ? '¡Copiado!' : 'Copiar Comando'}</span>
            </button>
          </div>

          <pre className="rounded-2xl bg-black/90 p-4 font-mono text-xs text-cyan-300 overflow-x-auto border border-slate-800 select-all">
            {cliCommand}
          </pre>
        </div>

        {/* Docker Command */}
        <div className="rounded-3xl bg-slate-900/70 p-6 border border-slate-800 backdrop-blur-md space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-purple-400 flex items-center gap-2">
              <Boxes className="h-4 w-4" />
              Comando Docker Compose (Sin dependencias locales):
            </span>
            <button
              onClick={() => copyToClipboard(dockerCommand, 'docker')}
              className="flex items-center gap-1.5 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 px-3 py-1.5 text-xs font-mono transition-all"
            >
              {copiedKey === 'docker' ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
              <span>{copiedKey === 'docker' ? '¡Copiado!' : 'Copiar Docker'}</span>
            </button>
          </div>

          <pre className="rounded-2xl bg-black/90 p-4 font-mono text-xs text-purple-300 overflow-x-auto border border-slate-800 select-all">
            {dockerCommand}
          </pre>
        </div>
      </div>

      {/* DOWNLOAD DELIVERABLES CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* SCRIPT JSON */}
        <div className="rounded-2xl bg-slate-900/60 p-5 border border-slate-800/80 backdrop-blur-md flex flex-col justify-between space-y-4">
          <div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/20 text-blue-400 border border-blue-500/30 mb-3">
              <FileCode className="h-5 w-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-100">Guión Estructurado (script.json)</h4>
            <p className="text-[11px] text-slate-400 font-mono mt-1">
              Incluye titular gancho, escenas, palabras clave en inglés y metadatos astronómicos.
            </p>
          </div>
          <button
            onClick={() =>
              downloadFile(JSON.stringify(currentScript, null, 2), `${currentScript.id || 'script'}.json`, 'application/json')
            }
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 py-2 text-xs font-mono font-semibold transition-all border border-slate-700"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Descargar script.json</span>
          </button>
        </div>

        {/* SRT SUBTITLES */}
        <div className="rounded-2xl bg-slate-900/60 p-5 border border-slate-800/80 backdrop-blur-md flex flex-col justify-between space-y-4">
          <div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30 mb-3">
              <FileText className="h-5 w-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-100">Subtítulos Universales (subtitles.srt)</h4>
            <p className="text-[11px] text-slate-400 font-mono mt-1">
              Formato estándar compatible con YouTube Shorts, TikTok y reproductores multimedia.
            </p>
          </div>
          <button
            onClick={() => downloadFile(generateSRT(), 'subtitles.srt', 'text/plain')}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 py-2 text-xs font-mono font-semibold transition-all border border-slate-700"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Descargar subtitles.srt</span>
          </button>
        </div>

        {/* ASS SUBTITLES */}
        <div className="rounded-2xl bg-slate-900/60 p-5 border border-slate-800/80 backdrop-blur-md flex flex-col justify-between space-y-4">
          <div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 mb-3">
              <FileText className="h-5 w-5" />
            </div>
            <h4 className="text-sm font-bold text-slate-100">Subtítulos Karaoke (subtitles.ass)</h4>
            <p className="text-[11px] text-slate-400 font-mono mt-1">
              Estilo vertical enriquecido con resaltado dinámico pop-in y tipografía optimizada.
            </p>
          </div>
          <button
            onClick={() => downloadFile(generateASS(), 'subtitles.ass', 'text/plain')}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 py-2 text-xs font-mono font-semibold transition-all border border-slate-700"
          >
            <Download className="h-3.5 w-3.5" />
            <span>Descargar subtitles.ass</span>
          </button>
        </div>
      </div>
    </div>
  );
};
