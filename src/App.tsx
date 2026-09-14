import React, { useState } from 'react';
import { Header } from './components/Header';
import { ScriptStudio } from './components/ScriptStudio';
import { IdeasExplorer } from './components/IdeasExplorer';
import { NasaDiscoveries } from './components/NasaDiscoveries';
import { VideoLibrary } from './components/VideoLibrary';
import { RenderProgressModal } from './components/RenderProgressModal';

export default function App() {
  const [activeTab, setActiveTab] = useState<'studio' | 'ideas' | 'discover' | 'library'>('studio');
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [selectedVideoFolder, setSelectedVideoFolder] = useState<string | undefined>(undefined);

  const handleStartRender = async (config: any) => {
    try {
      const res = await fetch('/api/render-video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });

      const data = await res.json();
      if (res.ok && data.jobId) {
        setActiveJobId(data.jobId);
      } else {
        alert(data.error || 'Error al iniciar la renderización');
      }
    } catch (err: any) {
      alert('Error de conexión: ' + err.message);
    }
  };

  const handleSelectTopicFromIdeas = (topic: string) => {
    setActiveTab('studio');
  };

  const handleViewVideoFromJob = (folderName: string) => {
    setSelectedVideoFolder(folderName);
    setActiveJobId(null);
    setActiveTab('library');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-purple-500 selection:text-white pb-16">
      {/* Top Header */}
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 pt-6">
        {activeTab === 'studio' && (
          <ScriptStudio onStartRender={handleStartRender} />
        )}

        {activeTab === 'ideas' && (
          <IdeasExplorer
            onSelectIdea={(topic) => {
              setActiveTab('studio');
            }}
          />
        )}

        {activeTab === 'discover' && (
          <NasaDiscoveries
            onSelectDiscovery={(title) => {
              setActiveTab('studio');
            }}
          />
        )}

        {activeTab === 'library' && (
          <VideoLibrary selectedVideoFolder={selectedVideoFolder} />
        )}
      </main>

      {/* Render Progress & Terminal Stream Modal */}
      {activeJobId && (
        <RenderProgressModal
          jobId={activeJobId}
          onClose={() => setActiveJobId(null)}
          onViewVideo={handleViewVideoFromJob}
        />
      )}
    </div>
  );
}
