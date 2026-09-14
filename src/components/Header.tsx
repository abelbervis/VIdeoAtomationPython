import React, { useEffect, useState } from 'react';
import { Sparkles, Bot, Video, Radio, Flame, ShieldCheck, CheckCircle2 } from 'lucide-react';

interface HeaderProps {
  activeTab: 'studio' | 'ideas' | 'discover' | 'library';
  onTabChange: (tab: 'studio' | 'ideas' | 'discover' | 'library') => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, onTabChange }) => {
  const [envStatus, setEnvStatus] = useState<any>(null);

  useEffect(() => {
    fetch('/api/env-status')
      .then((res) => res.json())
      .then((data) => setEnvStatus(data))
      .catch(() => {});
  }, []);

  return (
    <header className="bg-slate-900/90 border-b border-slate-800 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Logo & Title */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-purple-600/30">
            <Radio className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-base text-white tracking-tight">NASA Shorts & Cosmic Oracle Studio</h1>
              <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 text-[10px] font-mono font-bold border border-purple-500/30">
                NEXUS 2045 AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Generador Autónomo de Videos Virales con Orbe Reactivo (9:16 Shorts/Reels)
            </p>
          </div>
        </div>

        {/* API Status Badges */}
        <div className="hidden lg:flex items-center gap-2 text-[10px] font-medium text-slate-300 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
          <div className="flex items-center gap-1 text-emerald-400">
            <CheckCircle2 className="w-3 h-3" /> <span>NASA API: OK</span>
          </div>
          <span className="text-slate-700">•</span>
          <div className="flex items-center gap-1 text-purple-400">
            <Sparkles className="w-3 h-3" />
            <span>
              IA LLM:{' '}
              {envStatus?.gemini || envStatus?.groq || envStatus?.openai
                ? [
                    envStatus?.groq ? 'Groq ⚡' : null,
                    envStatus?.gemini ? 'Gemini ✨' : null,
                    envStatus?.openai ? 'OpenAI 🤖' : null,
                  ]
                    .filter(Boolean)
                    .join(' | ')
                : 'Factual Generator (Fallback)'}
            </span>
          </div>
          <span className="text-slate-700">•</span>
          <div className="flex items-center gap-1 text-cyan-400">
            <Video className="w-3 h-3" /> <span>Edge-TTS + FFmpeg: Listo</span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
          {[
            { id: 'studio', label: '🔮 Oráculo & Studio', icon: Bot },
            { id: 'ideas', label: '💡 Ideador Viral', icon: Flame },
            { id: 'discover', label: '🪐 NASA Discoveries', icon: Sparkles },
            { id: 'library', label: '🎬 Biblioteca Videos', icon: Video },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id as any)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === tab.id
                  ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
};
