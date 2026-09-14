import React, { useEffect, useState } from 'react';
import { GeneratedVideo } from '../types';
import { Video, Play, FileText, Download, Clock, Sparkles, RefreshCw, Eye, ShieldCheck } from 'lucide-react';

interface VideoLibraryProps {
  selectedVideoFolder?: string;
}

export const VideoLibrary: React.FC<VideoLibraryProps> = ({ selectedVideoFolder }) => {
  const [videos, setVideos] = useState<GeneratedVideo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeVideo, setActiveVideo] = useState<GeneratedVideo | null>(null);

  const fetchVideos = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/videos');
      if (res.ok) {
        const data = await res.json();
        setVideos(data);
        if (selectedVideoFolder && data.length > 0) {
          const match = data.find((v: GeneratedVideo) => v.folderName === selectedVideoFolder);
          if (match) setActiveVideo(match);
          else setActiveVideo(data[0]);
        } else if (data.length > 0 && !activeVideo) {
          setActiveVideo(data[0]);
        }
      }
    } catch {
      // Error
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchVideos();
  }, [selectedVideoFolder]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-md flex items-center justify-between">
        <div>
          <span className="text-[10px] uppercase font-bold text-purple-400 tracking-wider">
            Biblioteca de Contenido Renderizado
          </span>
          <h2 className="text-xl font-bold text-white">Videos Generados & Archivos de Producción</h2>
          <p className="text-xs text-slate-400">
            {videos.length} Shorts renderizados en HD (1080x1920 9:16) con subtítulos .srt/.ass y metadatos NASA.
          </p>
        </div>

        <button
          onClick={fetchVideos}
          className="flex items-center gap-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold transition-all border border-slate-700"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} /> Actualizar Biblioteca
        </button>
      </div>

      {isLoading ? (
        <div className="p-12 text-center text-slate-400 text-sm flex flex-col items-center gap-2">
          <RefreshCw className="w-6 h-6 animate-spin text-purple-500" />
          <span>Cargando videos de la carpeta output/...</span>
        </div>
      ) : videos.length === 0 ? (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
          <Video className="w-12 h-12 text-purple-400 mx-auto opacity-50" />
          <h3 className="font-bold text-slate-200 text-base">Aún no has generado ningún video</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Dirígete a la pestaña 🔮 <b>Oráculo & Studio</b> o explora 💡 <b>Ideador Viral</b> para producir tu primer
            video en vertical.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main Video Player & Details */}
          <div className="lg:col-span-7 space-y-4">
            {activeVideo && (
              <div className="bg-slate-900/90 border border-purple-500/30 rounded-2xl p-6 shadow-xl backdrop-blur-md space-y-5">
                {/* Header */}
                <div className="flex items-start justify-between border-b border-slate-800 pb-4">
                  <div>
                    <span className="text-[10px] text-purple-400 font-bold uppercase tracking-wider">
                      {activeVideo.metadata?.format || 'Vertical 9:16'} • {new Date(activeVideo.createdAt).toLocaleString()}
                    </span>
                    <h3 className="text-lg font-bold text-white capitalize">{activeVideo.title}</h3>
                  </div>

                  <a
                    href={activeVideo.mp4Path}
                    download
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded-lg text-xs shadow-md shadow-purple-600/30 transition-all"
                  >
                    <Download className="w-3.5 h-3.5" /> Descargar MP4
                  </a>
                </div>

                {/* Vertical 9:16 Video Player Container */}
                <div className="relative w-full max-w-[320px] mx-auto aspect-[9/16] bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 shadow-2xl">
                  <video
                    src={activeVideo.mp4Path}
                    controls
                    autoPlay
                    loop
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* Script & Metadata tabs */}
                <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
                  <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800/80 pb-2">
                    <span className="font-bold text-purple-300 flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5" /> Guión Generado por IA
                    </span>
                    <span>{activeVideo.script?.scenes?.length || 5} Escenas</span>
                  </div>

                  {activeVideo.script?.hook && (
                    <div className="p-2.5 bg-purple-950/30 border border-purple-500/20 rounded-lg text-xs text-purple-200">
                      <b>Gancho Inicial:</b> {activeVideo.script.hook}
                    </div>
                  )}

                  <div className="space-y-2 max-h-48 overflow-y-auto pr-1 custom-scrollbar text-xs">
                    {activeVideo.script?.scenes?.map((scene, idx) => (
                      <div key={idx} className="p-2 bg-slate-900 rounded-lg space-y-1">
                        <div className="flex justify-between font-mono text-[10px] text-purple-400 font-bold">
                          <span>Escena {scene.scene_number || idx + 1}</span>
                          <span>{scene.duration || 6}s</span>
                        </div>
                        <p className="text-slate-300 text-[11px]">{scene.narration}</p>
                      </div>
                    ))}
                  </div>

                  {/* NASA Atribución */}
                  <div className="pt-2 flex items-center gap-2 text-[10px] text-slate-400 border-t border-slate-800">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span>
                      Atribución Oficial: Imágenes e información registradas en <code>output/{activeVideo.folderName}/metadata.json</code>
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right Column: List of Generated Videos */}
          <div className="lg:col-span-5 space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">
              Videos Disponibles ({videos.length})
            </h3>

            <div className="space-y-3 max-h-[700px] overflow-y-auto pr-1 custom-scrollbar">
              {videos.map((vid) => (
                <button
                  key={vid.id}
                  onClick={() => setActiveVideo(vid)}
                  className={`w-full text-left p-4 rounded-xl border transition-all flex items-start gap-3.5 ${
                    activeVideo?.id === vid.id
                      ? 'bg-purple-950/40 border-purple-500 shadow-md shadow-purple-500/10'
                      : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="w-14 h-24 bg-slate-950 rounded-lg overflow-hidden border border-slate-800 shrink-0 relative flex items-center justify-center">
                    <Video className="w-6 h-6 text-purple-400 opacity-60" />
                    <div className="absolute inset-0 bg-purple-600/10 flex items-center justify-center">
                      <Play className="w-4 h-4 fill-white text-white opacity-80" />
                    </div>
                  </div>

                  <div className="flex-1 min-w-0 space-y-1">
                    <span className="text-[10px] text-purple-400 font-mono font-semibold">
                      {new Date(vid.createdAt).toLocaleDateString()}
                    </span>
                    <h4 className="font-bold text-sm text-slate-100 truncate capitalize">{vid.title}</h4>
                    <p className="text-xs text-slate-400 line-clamp-2">{vid.hook || vid.folderName}</p>
                    <div className="flex items-center gap-2 text-[10px] text-slate-500 pt-1">
                      <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">1080x1920 9:16</span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
