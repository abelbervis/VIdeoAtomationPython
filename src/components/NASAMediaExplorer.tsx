import React, { useState, useEffect } from 'react';
import { NASAMediaItem } from '../types';
import { searchNASAMedia, FALLBACK_NASA_MEDIA } from '../utils/nasaApi';
import {
  Search,
  Radio,
  Calendar,
  Layers,
  Sparkles,
  ExternalLink,
  PlusCircle,
  Eye,
  CheckCircle,
} from 'lucide-react';

interface NASAMediaExplorerProps {
  onSelectMediaForScene?: (media: NASAMediaItem) => void;
  onCreateShortFromMedia?: (media: NASAMediaItem) => void;
}

export const NASAMediaExplorer: React.FC<NASAMediaExplorerProps> = ({
  onSelectMediaForScene,
  onCreateShortFromMedia,
}) => {
  const [searchQuery, setSearchQuery] = useState('black hole');
  const [mediaList, setMediaList] = useState<NASAMediaItem[]>(FALLBACK_NASA_MEDIA);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState<NASAMediaItem | null>(null);

  const presets = [
    'black hole',
    'james webb',
    'solar flare',
    'gravitational waves',
    'nebula',
    'enceladus ocean',
    'mars rover',
    'cosmic dawn',
  ];

  const handleSearch = async (queryToUse?: string) => {
    const q = queryToUse !== undefined ? queryToUse : searchQuery;
    setIsLoading(true);
    try {
      const results = await searchNASAMedia(q);
      setMediaList(results);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleSearch('black hole');
  }, []);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* SEARCH AND FILTERS */}
      <div className="rounded-3xl bg-slate-900/80 p-6 border border-slate-800 backdrop-blur-md shadow-2xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                <Radio className="h-3.5 w-3.5 animate-pulse" />
              </span>
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-cyan-400">
                NASA Image & Video Library API
              </span>
            </div>
            <h2 className="text-2xl font-bold text-slate-100 mt-1">Archivo de Medios Oficiales de la NASA</h2>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              Explora imágenes astronómicas reales con metadatos oficiales y fechas para incluir en tus videos
            </p>
          </div>
        </div>

        {/* Search Input Bar */}
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              id="input-nasa-search"
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Buscar en el catálogo de la NASA (ej. James Webb, Supernova, Pulsar)..."
              className="w-full rounded-xl bg-slate-950/90 border border-slate-800 pl-10 pr-4 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500 font-sans"
            />
          </div>
          <button
            id="btn-nasa-search"
            onClick={() => handleSearch()}
            disabled={isLoading}
            className="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-6 py-2.5 text-xs font-semibold text-white shadow-lg hover:brightness-110 active:scale-95 disabled:opacity-40 transition-all shrink-0"
          >
            <Search className="h-3.5 w-3.5" />
            <span>{isLoading ? 'Buscando...' : 'Buscar'}</span>
          </button>
        </div>

        {/* Filter Chips */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          <span className="text-[11px] font-mono text-slate-400 mr-1">Filtros rápidos:</span>
          {presets.map((p) => (
            <button
              key={p}
              onClick={() => {
                setSearchQuery(p);
                handleSearch(p);
              }}
              className={`rounded-lg px-2.5 py-1 text-[11px] font-mono transition-all capitalize ${
                searchQuery.toLowerCase() === p.toLowerCase()
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800/80 hover:bg-slate-800/50'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* MEDIA GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {mediaList.map((item) => (
          <div
            key={item.id}
            className="group relative rounded-2xl bg-slate-900/60 border border-slate-800/80 overflow-hidden hover:border-cyan-500/50 transition-all duration-300 flex flex-col justify-between shadow-lg"
          >
            {/* Thumbnail */}
            <div className="relative aspect-video w-full overflow-hidden bg-slate-950">
              <img
                src={item.thumbUrl}
                alt={item.title}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent opacity-80" />

              {/* Top date badge */}
              <div className="absolute top-2.5 left-2.5 flex items-center gap-1 rounded-full bg-black/70 backdrop-blur-md px-2.5 py-0.5 text-[10px] font-mono text-cyan-300 border border-white/10">
                <Calendar className="h-2.5 w-2.5 text-cyan-400" />
                <span>{item.date_created}</span>
              </div>
            </div>

            {/* Content */}
            <div className="p-4 space-y-2 flex-1 flex flex-col justify-between">
              <div>
                <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">{item.center || 'NASA'}</span>
                <h3 className="text-sm font-bold text-slate-100 line-clamp-2 mt-0.5 group-hover:text-cyan-300 transition-colors">
                  {item.title}
                </h3>
                <p className="text-[11px] text-slate-400 line-clamp-2 mt-1">{item.description}</p>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 flex items-center gap-2 border-t border-slate-800/80">
                <button
                  onClick={() => setSelectedItem(item)}
                  className="flex-1 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 py-1.5 text-xs font-semibold flex items-center justify-center gap-1 transition-all border border-slate-700"
                >
                  <Eye className="h-3.5 w-3.5" />
                  <span>Detalles</span>
                </button>

                {onSelectMediaForScene && (
                  <button
                    onClick={() => onSelectMediaForScene(item)}
                    className="flex-1 rounded-xl bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 py-1.5 text-xs font-semibold flex items-center justify-center gap-1 transition-all"
                  >
                    <PlusCircle className="h-3.5 w-3.5" />
                    <span>Al Short</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* DETAIL MODAL */}
      {selectedItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-in fade-in">
          <div className="w-full max-w-2xl rounded-3xl bg-slate-900 border border-cyan-500/30 p-6 shadow-[0_0_50px_rgba(0,240,255,0.2)] space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-cyan-400 font-bold uppercase tracking-wider">
                ID: {selectedItem.nasa_id}
              </span>
              <button
                onClick={() => setSelectedItem(null)}
                className="text-slate-400 hover:text-slate-200 text-sm font-mono"
              >
                ✕
              </button>
            </div>

            <div className="rounded-2xl overflow-hidden aspect-video bg-black border border-slate-800">
              <img src={selectedItem.fullUrl} alt={selectedItem.title} className="w-full h-full object-contain" />
            </div>

            <div>
              <h3 className="text-lg font-bold text-slate-100">{selectedItem.title}</h3>
              <div className="mt-1 flex items-center gap-3 text-xs font-mono text-slate-400">
                <span>Fecha: {selectedItem.date_created}</span>
                <span>·</span>
                <span>Centro: {selectedItem.center || 'NASA'}</span>
              </div>
              <p className="mt-3 text-xs text-slate-300 leading-relaxed max-h-40 overflow-y-auto bg-slate-950 p-3 rounded-xl border border-slate-800">
                {selectedItem.description}
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setSelectedItem(null)}
                className="rounded-xl bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-700"
              >
                Cerrar
              </button>

              {onSelectMediaForScene && (
                <button
                  onClick={() => {
                    onSelectMediaForScene(selectedItem);
                    setSelectedItem(null);
                  }}
                  className="rounded-xl bg-cyan-500 px-4 py-2 text-xs font-semibold text-black hover:bg-cyan-400 flex items-center gap-1.5 shadow-lg"
                >
                  <PlusCircle className="h-3.5 w-3.5" />
                  <span>Usar en Escena Actual</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
