import React, { useEffect, useState, useRef } from 'react';
import { RenderJobStatus } from '../types';
import { Loader2, CheckCircle2, AlertTriangle, Terminal, Video, X } from 'lucide-react';

interface RenderProgressModalProps {
  jobId: string;
  onClose: () => void;
  onViewVideo: (folderName: string) => void;
}

export const RenderProgressModal: React.FC<RenderProgressModalProps> = ({ jobId, onClose, onViewVideo }) => {
  const [jobStatus, setJobStatus] = useState<RenderJobStatus | null>(null);
  const logContainerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let isMounted = true;
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/jobs/${jobId}`);
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            setJobStatus(data);
            if (data.status === 'completed' || data.status === 'error') {
              clearInterval(interval);
            }
          }
        }
      } catch {
        // Retry
      }
    }, 1000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [jobId]);

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [jobStatus?.logs]);

  if (!jobStatus) {
    return (
      <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
          <p className="text-sm text-slate-300">Conectando con el motor de renderizado FFmpeg...</p>
        </div>
      </div>
    );
  }

  const isCompleted = jobStatus.status === 'completed';
  const isError = jobStatus.status === 'error';

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl relative space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            {isCompleted ? (
              <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-xl">
                <CheckCircle2 className="w-6 h-6" />
              </div>
            ) : isError ? (
              <div className="p-2 bg-rose-500/20 text-rose-400 rounded-xl">
                <AlertTriangle className="w-6 h-6" />
              </div>
            ) : (
              <div className="p-2 bg-purple-500/20 text-purple-400 rounded-xl">
                <Loader2 className="w-6 h-6 animate-spin" />
              </div>
            )}
            <div>
              <h3 className="font-bold text-lg text-white">
                {isCompleted
                  ? '¡Renderizado de Video Completado!'
                  : isError
                  ? 'Error en la Producción del Video'
                  : 'Producción de Video en Proceso...'}
              </h3>
              <p className="text-xs text-slate-400">
                Tema: <span className="text-purple-300 font-semibold">{jobStatus.topic}</span> • Persona:{' '}
                <span className="uppercase text-slate-300 font-mono">{jobStatus.persona}</span>
              </p>
            </div>
          </div>

          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg bg-slate-800/50">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold">
            <span className="text-purple-300">
              {jobStatus.progress < 20
                ? 'Sintetizando guión estructurado...'
                : jobStatus.progress < 40
                ? 'Buscando clips astronómicos y B-Roll...'
                : jobStatus.progress < 60
                ? 'Sintetizando voz en off y subtítulos...'
                : jobStatus.progress < 85
                ? 'Renderizado acelerado FFmpeg y audio ducking...'
                : jobStatus.progress < 100
                ? 'Componiendo Orbe Reactivo y metadatos...'
                : 'Video final optimizado listo para publicación!'}
            </span>
            <span className="text-slate-400 font-mono">{jobStatus.progress}%</span>
          </div>

          <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div
              className="bg-gradient-to-r from-purple-600 via-indigo-500 to-emerald-400 h-full rounded-full transition-all duration-500 shadow-lg shadow-purple-500/50"
              style={{ width: `${jobStatus.progress}%` }}
            />
          </div>
        </div>

        {/* Terminal Live Output Logs */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5 font-mono text-[11px] text-purple-400">
              <Terminal className="w-3.5 h-3.5" /> Terminal Stream Logs
            </span>
            <span className="text-[10px] font-mono text-slate-500">{jobStatus.logs.length} líneas</span>
          </div>

          <div
            ref={logContainerRef}
            className="bg-slate-950 border border-slate-800/80 rounded-xl p-3.5 h-48 overflow-y-auto font-mono text-xs text-slate-300 space-y-1 shadow-inner custom-scrollbar"
          >
            {jobStatus.logs.map((log, idx) => (
              <div
                key={idx}
                className={
                  log.includes('✅')
                    ? 'text-emerald-400 font-semibold'
                    : log.includes('❌') || log.includes('[STDERR]')
                    ? 'text-rose-400'
                    : log.includes('🚀') || log.includes('⚙️')
                    ? 'text-purple-300 font-medium'
                    : 'text-slate-400'
                }
              >
                {log}
              </div>
            ))}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-800">
          <span className="text-xs text-slate-500">Job ID: {jobStatus.id}</span>

          <div className="flex items-center gap-2">
            {isCompleted && jobStatus.folderName && (
              <button
                onClick={() => onViewVideo(jobStatus.folderName!)}
                className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-sm shadow-lg shadow-emerald-600/30 transition-all"
              >
                <Video className="w-4 h-4" /> Reproducir Video Generado
              </button>
            )}

            <button
              onClick={onClose}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium rounded-xl text-xs transition-colors"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
