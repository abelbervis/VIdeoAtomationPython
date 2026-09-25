import React from 'react';
import { ActiveTab } from '../types';
import { Sparkles, Clapperboard, MessageSquareQuote, Radio, Orbit, Terminal, Volume2, VolumeX } from 'lucide-react';

interface HeaderProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  isDronePlaying: boolean;
  toggleDrone: () => void;
  onNewScript: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  isDronePlaying,
  toggleDrone,
  onNewScript,
}) => {
  const tabs: { id: ActiveTab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: 'studio', label: 'Shorts Studio', icon: Clapperboard },
    { id: 'debate', label: 'Co-Host Debates', icon: MessageSquareQuote },
    { id: 'nasa', label: 'NASA Media', icon: Radio },
    { id: 'observatory', label: 'Cosmic HUD', icon: Orbit },
    { id: 'export', label: 'CLI & Export', icon: Terminal },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-cyan-500/20 bg-[#06070B]/90 backdrop-blur-md px-4 py-3 sm:px-6">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-500/20 via-blue-600/20 to-purple-600/20 border border-cyan-500/40 shadow-[0_0_15px_rgba(0,240,255,0.25)]">
            <Orbit className="h-5 w-5 text-cyan-400 animate-spin" style={{ animationDuration: '14s' }} />
            <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-cyan-400 animate-ping" />
            <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-cyan-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-bold tracking-wider text-slate-100 uppercase">NASA Shorts</span>
              <span className="rounded bg-cyan-500/10 px-1.5 py-0.5 text-[10px] font-mono font-medium text-cyan-400 border border-cyan-500/30">
                PRO 2026
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono hidden sm:block">Astrometric AI Video Generator & Co-Host Debates</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1 rounded-xl bg-slate-900/60 p-1 border border-slate-800">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                id={`tab-nav-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_12px_rgba(0,240,255,0.18)]'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                }`}
              >
                <Icon className={`h-3.5 w-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {/* Drone sound toggle */}
          <button
            id="btn-drone-toggle"
            onClick={toggleDrone}
            title={isDronePlaying ? 'Mute Cosmic Ambient Drone' : 'Play Binaural Cosmic Drone (48Hz/58Hz)'}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-mono border transition-all ${
              isDronePlaying
                ? 'bg-cyan-950/40 border-cyan-500/40 text-cyan-300 shadow-[0_0_10px_rgba(0,240,255,0.2)]'
                : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            {isDronePlaying ? <Volume2 className="h-3.5 w-3.5 text-cyan-400 animate-pulse" /> : <VolumeX className="h-3.5 w-3.5" />}
            <span className="hidden sm:inline">{isDronePlaying ? 'Drone ON' : 'Drone OFF'}</span>
          </button>

          {/* Quick Create button */}
          <button
            id="btn-quick-create"
            onClick={onNewScript}
            className="flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-[0_0_16px_rgba(0,240,255,0.3)] hover:brightness-110 active:scale-95 transition-all"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Nuevo Guión</span>
          </button>
        </div>
      </div>

      {/* Mobile Sub-Nav */}
      <div className="mt-2 flex md:hidden items-center justify-between gap-1 overflow-x-auto py-1 scrollbar-none">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex shrink-0 items-center gap-1.5 rounded-lg px-2.5 py-1 text-[11px] font-medium transition-all ${
                isActive
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className="h-3 w-3" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
};
