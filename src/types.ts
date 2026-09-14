export type PersonaType = 'oracle' | 'science' | 'mystery' | 'cyberpunk';
export type ProviderType = 'auto' | 'nasa' | 'pexels' | 'pixabay' | 'pollinations';
export type LLMProviderType = 'auto' | 'gemini' | 'groq' | 'openai';
export type FormatType = 'vertical' | 'horizontal' | 'square';
export type OrbPalette = 'cosmic' | 'cyberpunk' | 'solar' | 'aurora' | 'nebula' | 'monochrome';
export type OrbPosition = 'presenter' | 'host' | 'center' | 'floating' | 'ambient' | 'top-right' | 'bottom-right';
export type OrbAnimation = 'speaking' | 'presenter' | 'reactive' | 'pulse' | 'float' | 'breathing' | 'none';

export interface ScriptScene {
  scene_number: number;
  narration: string;
  duration: number;
  keywords: string[];
  visual_description?: string;
  broll_keywords?: string[];
}

export interface ScriptData {
  title: string;
  hook: string;
  hook_title?: string;
  target_duration?: number;
  scenes: ScriptScene[];
  entity_name?: string;
  persona?: PersonaType;
}

export interface RenderJobStatus {
  id: string;
  topic: string;
  persona: string;
  status: 'queued' | 'running' | 'completed' | 'error';
  progress: number;
  logs: string[];
  outputPath?: string;
  folderName?: string;
  error?: string;
  startTime: number;
  endTime?: number;
}

export interface GeneratedVideo {
  id: string;
  folderName: string;
  title: string;
  hook: string;
  mp4Path: string;
  narrationPath?: string;
  createdAt: string;
  script?: ScriptData;
  metadata?: {
    format?: string;
    width?: number;
    height?: number;
    duration?: number;
    sources?: Array<{
      id?: string;
      title?: string;
      provider?: string;
      date?: string;
    }>;
  };
}

export interface ViralIdea {
  id: string;
  title: string;
  category: string;
  hook: string;
  angle: string;
  retention_note: string;
}

export interface NasaDiscovery {
  title: string;
  explanation?: string;
  date?: string;
  url?: string;
  media_type?: string;
  viral_score?: number;
}
