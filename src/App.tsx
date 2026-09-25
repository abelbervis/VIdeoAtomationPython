import React, { useState } from 'react';
import { ActiveTab, VideoScript, SimulatorConfig, EntityId, NASAMediaItem } from './types';
import { SAMPLE_SCRIPTS } from './data/sampleScripts';
import { ENTITY_CHARACTERS } from './data/characters';
import { CosmicBackground } from './components/CosmicBackground';
import { Header } from './components/Header';
import { ShortsStudio } from './components/ShortsStudio';
import { DebateLab } from './components/DebateLab';
import { NASAMediaExplorer } from './components/NASAMediaExplorer';
import { CosmicHUD } from './components/CosmicHUD';
import { ExportModal } from './components/ExportModal';
import { soundEngine } from './utils/audioSynth';

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('studio');
  const [currentScript, setCurrentScript] = useState<VideoScript>(SAMPLE_SCRIPTS[0]);
  const [targetSceneIndexForMedia, setTargetSceneIndexForMedia] = useState<number | null>(null);

  const [simConfig, setSimConfig] = useState<SimulatorConfig>({
    particleDensity: 'medium',
    speedMultiplier: 1.0,
    gravityStrength: 1.0,
    showOrbits: true,
    interactiveMouse: true,
    activeEntityA: 'quantum',
    activeEntityB: 'solar',
    enableDroneSound: false,
    enableSfx: true,
  });

  const charA = ENTITY_CHARACTERS[simConfig.activeEntityA];
  const charB = ENTITY_CHARACTERS[simConfig.activeEntityB];

  // Toggle ambient harmonic drone (binaural sound generator)
  const toggleDrone = () => {
    if (!simConfig.enableDroneSound) {
      soundEngine.startDrone(charA.drone_freq, charB.drone_freq, 0.12);
      setSimConfig((prev) => ({ ...prev, enableDroneSound: true }));
    } else {
      soundEngine.stopDrone();
      setSimConfig((prev) => ({ ...prev, enableDroneSound: false }));
    }
  };

  // Generate new AI script from topic
  const handleGenerateAIScript = (topic: string) => {
    const newScript: VideoScript = {
      id: `script-${Date.now()}`,
      title: topic,
      hookTitle: `¿Y SI ${topic.toUpperCase()}?`,
      topic,
      category: 'Exploración Astronómica',
      duration: 32,
      targetEntities: [simConfig.activeEntityA, simConfig.activeEntityB],
      createdAt: new Date().toISOString().slice(0, 10),
      scenes: [
        {
          id: `s1-${Date.now()}`,
          sceneNumber: 1,
          presenter: 'narrator',
          narration: `Un nuevo enigma cósmico desafía las leyes de la astrofísica: ${topic}.`,
          visualKeywords: ['deep space anomaly', 'cosmic discovery', 'astrophysics'],
          visualPrompt: `Spectacular hyperrealistic cosmic view of ${topic}`,
          camera: 'wide',
          duration: 5,
          mediaTitle: `Observación Astronómica: ${topic}`,
          mediaSource: 'NASA Science Mission',
          mediaDate: '2026',
          mediaUrl: 'https://images-assets.nasa.gov/image/PIA25686/PIA25686~orig.jpg',
          sfx: 'boom',
        },
        {
          id: `s2-${Date.now()}`,
          sceneNumber: 2,
          presenter: simConfig.activeEntityA,
          narration: `A nivel fundamental, los patrones revelan una estructura que no encaja con los modelos convencionales.`,
          visualKeywords: ['quantum lattice', 'energy spectra', 'cosmic microwave'],
          visualPrompt: 'Glowing mathematical cosmic field lines',
          camera: 'close_entity_a',
          duration: 7,
          mediaTitle: 'Espectrometría Espacial NASA',
          mediaSource: 'NASA / JPL',
          mediaDate: '2026',
          mediaUrl: 'https://images-assets.nasa.gov/image/PIA19048/PIA19048~orig.jpg',
          sfx: 'whoosh',
        },
        {
          id: `s3-${Date.now()}`,
          sceneNumber: 3,
          presenter: simConfig.activeEntityB,
          narration: `Las magnitudes térmicas y de masa son colosales. La radiación emitida supera todo lo registrado en nuestra galaxia.`,
          visualKeywords: ['stellar flare', 'supernova energy', 'plasma filaments'],
          visualPrompt: 'Violent plasma storm in deep cosmos',
          camera: 'close_entity_b',
          duration: 7,
          mediaTitle: 'Radiación de Alta Energía',
          mediaSource: 'NASA Chandra Observatory',
          mediaDate: '2025',
          mediaUrl: 'https://images-assets.nasa.gov/image/PIA13123/PIA13123~orig.jpg',
          sfx: 'whoosh',
        },
        {
          id: `s4-${Date.now()}`,
          sceneNumber: 4,
          presenter: simConfig.activeEntityA,
          narration: `Esto sugiere que el horizonte del espacio-tiempo alberga dimensiones y procesos que apenas comenzamos a vislumbrar.`,
          visualKeywords: ['gravitational lens', 'space time curvature'],
          visualPrompt: 'Curved spacetime fabric with warped background galaxies',
          camera: 'close_entity_a',
          duration: 7,
          mediaTitle: 'Deformación del Espacio-Tiempo',
          mediaSource: 'NASA / ESA / Hubble',
          mediaDate: '2026',
          mediaUrl: 'https://images-assets.nasa.gov/image/GSFC_20190925_m13437_BlackHole/GSFC_20190925_m13437_BlackHole~orig.jpg',
          sfx: 'whoosh',
        },
        {
          id: `s5-${Date.now()}`,
          sceneNumber: 5,
          presenter: 'narrator',
          narration: `¿Estamos ante una anomalía pasajera o el inicio de una nueva era en la física cósmica?`,
          visualKeywords: ['cosmic web', 'multiverse'],
          visualPrompt: 'Infinite cosmic filaments glowing in deep space',
          camera: 'wide',
          duration: 6,
          mediaTitle: 'Red Cósmica Profunda',
          mediaSource: 'NASA STScI',
          mediaDate: '2026',
          mediaUrl: 'https://images-assets.nasa.gov/image/PIA23865/PIA23865~orig.jpg',
          sfx: 'boom',
        },
      ],
    };

    setCurrentScript(newScript);
    setActiveTab('studio');
  };

  // Convert Debate turns into a full Video Short Script
  const handleLoadDebateIntoStudio = (
    turns: Array<{ presenter: EntityId; dialogue: string; camera: any; duration: number }>,
    topic: string,
    entA: EntityId,
    entB: EntityId
  ) => {
    const scenes = turns.map((turn, i) => ({
      id: `debate-scene-${i}`,
      sceneNumber: i + 1,
      presenter: turn.presenter,
      narration: turn.dialogue,
      visualKeywords: [turn.presenter, 'space debate', 'singularity'],
      visualPrompt: `Cosmic visual for ${turn.presenter}`,
      camera: turn.camera,
      duration: turn.duration,
      mediaTitle: `Observatorio Astrométrico NASA: Debate Turno ${i + 1}`,
      mediaSource: 'NASA Science Library',
      mediaDate: '2026',
      mediaUrl:
        i % 2 === 0
          ? 'https://images-assets.nasa.gov/image/GSFC_20190925_m13437_BlackHole/GSFC_20190925_m13437_BlackHole~orig.jpg'
          : 'https://images-assets.nasa.gov/image/PIA25686/PIA25686~orig.jpg',
      sfx: (i === 0 ? 'boom' : 'whoosh') as any,
    }));

    const totalDur = scenes.reduce((acc, s) => acc + s.duration, 0);

    const newScript: VideoScript = {
      id: `script-debate-${Date.now()}`,
      title: topic,
      hookTitle: `¿QUIÉN TIENE LA RAZÓN EN EL COSMOS?`,
      topic,
      category: 'Debate de Entidades',
      duration: totalDur,
      targetEntities: [entA, entB],
      createdAt: new Date().toISOString().slice(0, 10),
      scenes,
    };

    setCurrentScript(newScript);
    setSimConfig((prev) => ({ ...prev, activeEntityA: entA, activeEntityB: entB }));
    setActiveTab('studio');
  };

  // Assign selected NASA media item to specific scene
  const handleSelectNASAMediaForScene = (media: NASAMediaItem) => {
    const targetIdx = targetSceneIndexForMedia !== null ? targetSceneIndexForMedia : 0;
    const updatedScenes = [...currentScript.scenes];
    if (updatedScenes[targetIdx]) {
      updatedScenes[targetIdx] = {
        ...updatedScenes[targetIdx],
        mediaUrl: media.fullUrl || media.thumbUrl,
        mediaTitle: media.title,
        mediaSource: `${media.center || 'NASA'} · ${media.nasa_id}`,
        mediaDate: media.date_created,
      };
      setCurrentScript({ ...currentScript, scenes: updatedScenes });
    }
    setTargetSceneIndexForMedia(null);
    setActiveTab('studio');
  };

  return (
    <main id="app-root" className="relative min-h-screen w-full bg-[#06070B] text-slate-100 overflow-x-hidden select-none font-sans">
      {/* 1. DUAL GRAVITY PARTICLE SIMULATION BACKGROUND */}
      <CosmicBackground
        entity1={{
          primary: charA.primary_color,
          glow: charA.glow_color,
          accent: charA.accent_color,
          name: charA.name,
        }}
        entity2={{
          primary: charB.primary_color,
          glow: charB.glow_color,
          accent: charB.accent_color,
          name: charB.name,
        }}
        particleDensity={simConfig.particleDensity}
        speedMultiplier={simConfig.speedMultiplier}
        gravityStrength={simConfig.gravityStrength}
        showOrbits={simConfig.showOrbits}
        interactiveMouse={simConfig.interactiveMouse}
      />

      {/* 2. FOREGROUND INTERACTIVE STUDIO APP */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Navigation Header */}
        <Header
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          isDronePlaying={simConfig.enableDroneSound}
          toggleDrone={toggleDrone}
          onNewScript={() => handleGenerateAIScript('El Misterio de la Materia Oscura')}
        />

        {/* Main Content Area */}
        <div className="flex-1 w-full max-w-7xl mx-auto px-4 py-6 sm:px-6">
          {activeTab === 'studio' && (
            <ShortsStudio
              currentScript={currentScript}
              onUpdateScript={setCurrentScript}
              onSelectNASAMediaForScene={(sceneIdx) => {
                setTargetSceneIndexForMedia(sceneIdx);
                setActiveTab('nasa');
              }}
              onGenerateAIScript={handleGenerateAIScript}
            />
          )}

          {activeTab === 'debate' && (
            <DebateLab
              onLoadDebateIntoStudio={handleLoadDebateIntoStudio}
              onActiveEntitiesChange={(entA, entB) => {
                setSimConfig((prev) => ({ ...prev, activeEntityA: entA, activeEntityB: entB }));
              }}
            />
          )}

          {activeTab === 'nasa' && (
            <NASAMediaExplorer
              onSelectMediaForScene={handleSelectNASAMediaForScene}
              onCreateShortFromMedia={(media) => {
                handleGenerateAIScript(media.title);
              }}
            />
          )}

          {activeTab === 'observatory' && (
            <CosmicHUD config={simConfig} onUpdateConfig={setSimConfig} />
          )}

          {activeTab === 'export' && (
            <ExportModal currentScript={currentScript} config={simConfig} />
          )}
        </div>

        {/* Footer info bar */}
        <footer className="w-full border-t border-slate-900 bg-[#06070B]/80 backdrop-blur-md px-4 py-2.5 text-center text-[11px] font-mono text-slate-500">
          <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
            <span>🚀 NASA Shorts Generator · Entidades Activas: {charA.name} & {charB.name}</span>
            <span>Audio Sub-Bass: {charA.drone_freq}Hz / {charB.drone_freq}Hz · 30 FPS Vertical 9:16</span>
          </div>
        </footer>
      </div>
    </main>
  );
}
