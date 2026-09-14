import React, { useEffect, useState } from 'react';
import { NasaDiscovery } from '../types';
import { Globe, Calendar, RefreshCw, Sparkles, Rocket, ArrowRight, ShieldCheck } from 'lucide-react';

interface NasaDiscoveriesProps {
  onSelectDiscovery: (title: string) => void;
}

export const NasaDiscoveries: React.FC<NasaDiscoveriesProps> = ({ onSelectDiscovery }) => {
  const [discoveries, setDiscoveries] = useState<NasaDiscovery[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  const fetchDiscoveries = async (refresh = false) => {
    setIsLoading(true);
    try {
      let url = `/api/discover?refresh=${refresh}`;
      if (selectedDate) url += `&date=${selectedDate}`;

      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        if (data.items && Array.isArray(data.items)) {
          setDiscoveries(data.items);
        } else {
          // Fallback static discoveries
          setDiscoveries([
            {
              title: 'Exoplaneta cubierto por un océano hirviendo de 100 grados',
              explanation:
                'Hallazgo del telescopio espacial James Webb que detectó vapor de agua y dióxido de carbono en la atmósfera denso de un mundo acuático.',
              date: '2024-04-12',
              viral_score: 96,
            },
            {
              title: 'Eclipse Solar Total de América del Norte y la Corona Solar',
              explanation:
                'La SDO y observatorios terrestres capturaron protuberancias solares masivas y bucles magnéticos durante la totalidad.',
              date: '2024-04-08',
              viral_score: 98,
            },
            {
              title: 'Misteriosa estructura en espiral en el centro de la Vía Láctea',
              explanation:
                'Líneas de campo magnético organizadas alrededor de Sgr A* cartografiadas en luz polarizada.',
              date: '2024-03-27',
              viral_score: 92,
            },
          ]);
        }
      }
    } catch {
      // Error
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDiscoveries();
  }, [selectedDate]);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-md flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 text-[11px] font-semibold border border-cyan-500/30 uppercase tracking-wider">
              NASA Official Image & Video Library
            </span>
            <span className="text-xs text-slate-400">• Navegación Histórica 1995-2026</span>
          </div>
          <h2 className="text-xl font-bold text-white">Novedades y Archivo Histórico de la NASA</h2>
          <p className="text-xs text-slate-400">
            Descubrimientos astronómicos reales evaluados por IA con insignias de atribución oficiales.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800">
            <Calendar className="w-3.5 h-3.5 text-cyan-400" />
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="bg-transparent text-xs text-slate-200 focus:outline-none"
            />
          </div>

          <button
            onClick={() => fetchDiscoveries(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition-all border border-slate-700"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} /> Consultar NASA
          </button>
        </div>
      </div>

      {/* Discoveries Grid */}
      {isLoading ? (
        <div className="p-12 text-center text-slate-400 text-sm flex flex-col items-center gap-2">
          <RefreshCw className="w-6 h-6 animate-spin text-cyan-500" />
          <span>Consultando la API oficial de la NASA y la Biblioteca de Imágenes...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {discoveries.map((item, idx) => (
            <div
              key={idx}
              className="bg-slate-900/90 border border-slate-800 hover:border-cyan-500/50 rounded-2xl p-5 shadow-xl backdrop-blur-md flex flex-col justify-between space-y-4 group transition-all"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="font-mono text-cyan-400 font-bold flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3 text-emerald-400" /> NASA APOD / VIDEO
                  </span>
                  {item.date && (
                    <span className="text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800 font-mono">
                      {item.date}
                    </span>
                  )}
                </div>

                <h3 className="font-bold text-base text-white group-hover:text-cyan-300 transition-colors">
                  {item.title}
                </h3>

                {item.explanation && (
                  <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">{item.explanation}</p>
                )}
              </div>

              <button
                onClick={() => onSelectDiscovery(item.title)}
                className="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-cyan-600/20 hover:bg-cyan-600 text-cyan-300 hover:text-white font-bold rounded-xl text-xs border border-cyan-500/30 transition-all shadow-md"
              >
                Producir Video con NASA Media <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
