export type EntityId = 'quantum' | 'solar' | 'neural' | 'gaia' | 'void' | 'narrator';

export interface EntityCharacter {
  id: EntityId;
  name: string;
  role: string;
  perspective: string;
  color_theme: string;
  palette_name: string;
  primary_color: string;
  glow_color: string;
  border_color: string;
  voice_name: string;
  voice_rate: string;
  voice_pitch: string;
  voice_volume: string;
  drone_freq: number;
  shot_name: 'wide' | 'close_quantum' | 'close_solar';
  accent_color: string;
  tagline: string;
}

export interface ScriptScene {
  id: string;
  sceneNumber: number;
  presenter: EntityId | 'both' | 'narrator';
  narration: string;
  visualKeywords: string[];
  visualPrompt: string;
  camera: 'wide' | 'close_entity_a' | 'close_entity_b' | 'macro_cosmos';
  duration: number; // in seconds
  mediaUrl?: string;
  mediaType?: 'image' | 'video';
  mediaTitle?: string;
  mediaSource?: string;
  mediaDate?: string;
  sfx?: 'boom' | 'whoosh' | 'glitch' | 'none';
}

export interface VideoScript {
  id: string;
  title: string;
  hookTitle: string;
  topic: string;
  category: string;
  duration: number;
  targetEntities: [EntityId, EntityId];
  scenes: ScriptScene[];
  createdAt: string;
}

export interface NASAMediaItem {
  id: string;
  nasa_id: string;
  title: string;
  description: string;
  date_created: string;
  center?: string;
  keywords?: string[];
  thumbUrl: string;
  fullUrl: string;
  media_type: 'image' | 'video';
}

export interface SimulatorConfig {
  particleDensity: 'low' | 'medium' | 'high';
  speedMultiplier: number;
  gravityStrength: number;
  showOrbits: boolean;
  interactiveMouse: boolean;
  activeEntityA: EntityId;
  activeEntityB: EntityId;
  enableDroneSound: boolean;
  enableSfx: boolean;
}

export type ActiveTab = 'studio' | 'debate' | 'nasa' | 'observatory' | 'export';
