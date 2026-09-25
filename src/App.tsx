import React, { useRef, useState, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, RotateCcw, Sparkles } from 'lucide-react';

export default function App() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  const videoUrl = '/output/orb_previews/debate_express/video.mp4';

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleRestart = () => {
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      videoRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const cur = videoRef.current.currentTime;
      const dur = videoRef.current.duration || 1;
      setCurrentTime(cur);
      setDuration(dur);
      setProgress((cur / dur) * 100);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const seekTime = (parseFloat(e.target.value) / 100) * duration;
    if (videoRef.current) {
      videoRef.current.currentTime = seekTime;
      setCurrentTime(seekTime);
      setProgress(parseFloat(e.target.value));
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  useEffect(() => {
    // Attempt auto-play with audio if possible
    if (videoRef.current) {
      videoRef.current.play().catch(() => {
        // Fallback to muted autoplay if browser blocks audio autoplay
        if (videoRef.current) {
          videoRef.current.muted = true;
          setIsMuted(true);
          videoRef.current.play();
        }
      });
    }
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-slate-100 p-2 sm:p-6 font-sans select-none overflow-hidden">
      {/* Outer minimalist frame */}
      <div className="relative w-full max-w-[380px] aspect-[9/16] bg-black rounded-3xl overflow-hidden shadow-2xl border border-slate-800/80 flex flex-col group">
        
        {/* Video Element */}
        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-full object-cover cursor-pointer"
          playsInline
          loop
          onTimeUpdate={handleTimeUpdate}
          onClick={togglePlay}
        />

        {/* Top Minimalist Header Overlay */}
        <div className="absolute top-0 inset-x-0 p-4 bg-gradient-to-b from-black/80 via-black/40 to-transparent flex items-center justify-between pointer-events-none z-10">
          <div className="flex items-center gap-2 bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-full border border-slate-700/50 text-xs font-medium text-cyan-400">
            <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
            <span>Co-Host AI • Vista Previa</span>
          </div>
          <button
            onClick={toggleMute}
            className="pointer-events-auto p-2 rounded-full bg-black/50 hover:bg-black/80 backdrop-blur-md text-white/90 hover:text-white transition-all border border-white/10"
            title={isMuted ? 'Activar sonido' : 'Silenciar'}
          >
            {isMuted ? <VolumeX className="w-4 h-4 text-red-400" /> : <Volume2 className="w-4 h-4 text-cyan-400" />}
          </button>
        </div>

        {/* Play/Pause Center Overlay */}
        {!isPlaying && (
          <button
            onClick={togglePlay}
            className="absolute inset-0 m-auto w-16 h-16 rounded-full bg-cyan-500/90 text-slate-950 flex items-center justify-center shadow-lg shadow-cyan-500/30 backdrop-blur-md transition-transform hover:scale-110 active:scale-95 z-20"
          >
            <Play className="w-8 h-8 fill-current translate-x-0.5" />
          </button>
        )}

        {/* Bottom Minimalist Controls Bar */}
        <div className="absolute bottom-0 inset-x-0 p-4 bg-gradient-to-t from-black/90 via-black/50 to-transparent flex flex-col gap-2 transition-opacity duration-300 z-10">
          {/* Timeline Scrub Bar */}
          <div className="flex items-center gap-2">
            <input
              type="range"
              min="0"
              max="100"
              value={progress || 0}
              onChange={handleSeek}
              className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400 focus:outline-none"
            />
          </div>

          {/* Time & Action Buttons */}
          <div className="flex items-center justify-between text-xs text-slate-400 font-mono pt-1">
            <span>{formatTime(currentTime)} / {formatTime(duration)}</span>

            <div className="flex items-center gap-3">
              <button
                onClick={handleRestart}
                className="hover:text-cyan-400 transition-colors p-1"
                title="Reiniciar"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={togglePlay}
                className="hover:text-cyan-400 transition-colors p-1"
                title={isPlaying ? 'Pausar' : 'Reproducir'}
              >
                {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
