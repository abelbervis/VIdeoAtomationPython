import React, { useEffect, useState } from 'react';
import { ViralIdea } from '../types';
import { Sparkles, Bot, Zap, ArrowRight, RefreshCw, Flame, HelpCircle } from 'lucide-react';

interface IdeasExplorerProps {
  onSelectIdea: (topic: string) => void;
}

export const IdeasExplorer: React.FC<IdeasExplorerProps> = ({ onSelectIdea }) => {
  const [ideas, setIdeas] = useState<ViralIdea[]>([]);
  const [categories, setCategories] = useState<Record<string, string>>({});
  const [selectedCategory, setSelectedCategory] = useState<string>('oraculo_ia');
  const [isLoading, setIsLoading] = useState(true);

  const fetchIdeas = async (cat: string) => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/ideas?category=${cat}`);
      if (res.ok) {
        const data = await res.json();
        setIdeas(data.ideas || []);
        setCategories(data.categories || {});
      }
    } catch {
      // Error
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchIdeas(selectedCategory);
  }, [selectedCategory]);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-[11px] font-semibold border border-purple-500/30 uppercase tracking-wider">
              Estrategia de Viralidad Cuántica
            </span>
            <span className="text-xs text-slate-400">• Ganchos de 3 Segundos para Retención</span>
          </div>
          <h2 className="text-xl font-bold text-white">Ideador Viral de Contenido</h2>
          <p className="text-xs text-slate-400">
            Conceptos estructurados para disparar los comentarios y el tiempo de reproducción en Shorts, TikTok & Reels.
          </p>
        </div>

        <button
          onClick={() => fetchIdeas(selectedCategory)}
          className="flex items-center gap-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition-all border border-slate-700"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} /> Regenerar Ideas
        </button>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 custom-scrollbar">
        {Object.entries({
          oraculo_ia: '🔮 Oráculo IA & Simulaciones',
          paradojas_cuanticas: '⚛️ Paradojas Cuánticas',
          misterios: '🌌 Misterios Cósmicos',
          agujeros_negros: '🕳️ Agujeros Negros',
          planetas_extremos: '🪐 Planetas Extremos',
          james_webb: '🔭 James Webb',
          que_pasaria_si: '💥 ¿Qué pasaría si...?',
        }).map(([key, label]) => (
          <button
            key={key}
            onClick={() => setSelectedCategory(key)}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all border ${
              selectedCategory === key
                ? 'bg-purple-600 text-white border-purple-500 shadow-md shadow-purple-600/30'
                : 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Ideas Grid */}
      {isLoading ? (
        <div className="p-12 text-center text-slate-400 text-sm flex flex-col items-center gap-2">
          <RefreshCw className="w-6 h-6 animate-spin text-purple-500" />
          <span>Analizando algoritmos y patrones de alta retención...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {ideas.map((idea, idx) => (
            <div
              key={idx}
              className="bg-slate-900/90 border border-slate-800 hover:border-purple-500/50 rounded-2xl p-5 shadow-xl backdrop-blur-md flex flex-col justify-between space-y-4 group transition-all"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-bold border border-purple-500/30">
                    OPCIÓN #{idx + 1}
                  </span>
                  <span className="text-[10px] text-slate-500 flex items-center gap-1">
                    <Flame className="w-3 h-3 text-orange-400" /> Viral Score: 98%
                  </span>
                </div>

                <h3 className="font-bold text-base text-white group-hover:text-purple-300 transition-colors">
                  {idea.title}
                </h3>

                {/* Hook Box */}
                <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
                  <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider block">
                    🔥 Gancho Inicial de 3 Segundos:
                  </span>
                  <p className="text-xs text-slate-200 font-medium italic">"{idea.hook}"</p>
                </div>

                {/* Retention Note */}
                {idea.retention_note && (
                  <p className="text-xs text-slate-400 leading-relaxed">
                    <b className="text-slate-300">Gatillo Psicológico:</b> {idea.retention_note}
                  </p>
                )}
              </div>

              <button
                onClick={() => onSelectIdea(`${idea.title}: ${idea.hook}`)}
                className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-purple-600/20 hover:bg-purple-600 text-purple-300 hover:text-white font-bold rounded-xl text-xs border border-purple-500/30 transition-all shadow-md"
              >
                Cargar en Studio & Producir <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
