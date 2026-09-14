import express from 'express';
import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';
import { createServer as createViteServer } from 'vite';

const app = express();
const PORT = 3000;

app.use(express.json({ limit: '10mb' }));

// Paths
const ROOT_DIR = process.cwd();
const OUTPUT_DIR = path.join(ROOT_DIR, 'output');
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Serve output files for video player streaming
app.use('/output-files', express.static(OUTPUT_DIR));

// In-memory Job Tracker for Video Rendering
interface RenderJob {
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

const renderJobs: Record<string, RenderJob> = {};

// Helper to run python commands
function runPythonCommand(args: string[]): Promise<{ stdout: string; stderr: string; code: number }> {
  return new Promise((resolve) => {
    const pyProcess = spawn('python3', args, { cwd: ROOT_DIR });
    let stdout = '';
    let stderr = '';

    pyProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pyProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    pyProcess.on('close', (code) => {
      resolve({ stdout, stderr, code: code || 0 });
    });
  });
}

// 1. API: Environment / API Key Connection Status
app.get('/api/env-status', (req, res) => {
  const envFile = path.join(ROOT_DIR, '.env');
  let envVars: Record<string, string> = {};
  if (fs.existsSync(envFile)) {
    const lines = fs.readFileSync(envFile, 'utf-8').split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
        const [k, ...v] = trimmed.split('=');
        envVars[k.trim()] = v.join('=').trim().replace(/^['"]|['"]$/g, '');
      }
    }
  }

  const checkKey = (key: string) => {
    const val = process.env[key] || envVars[key] || '';
    return val.length > 3 && !val.includes('tu_clave') && !val.includes('YOUR_API_KEY');
  };

  res.json({
    gemini: checkKey('GEMINI_API_KEY'),
    openai: checkKey('OPENAI_API_KEY'),
    groq: checkKey('GROQ_API_KEY'),
    pexels: checkKey('PEXELS_API_KEY'),
    pixabay: checkKey('PIXABAY_API_KEY'),
    nasaKey: (process.env.NASA_API_KEY || envVars.NASA_API_KEY || 'DEMO_KEY') !== 'DEMO_KEY',
    defaultLanguage: process.env.DEFAULT_LANGUAGE || envVars.DEFAULT_LANGUAGE || 'es',
    defaultPersona: process.env.SCRIPT_PERSONA || envVars.SCRIPT_PERSONA || 'oracle',
    entityName: process.env.ENTITY_NAME || envVars.ENTITY_NAME || 'Nexus',
  });
});

// 2. API: Content Ideas Discovery
app.get('/api/ideas', async (req, res) => {
  const category = (req.query.category as string) || '';
  const args = ['-c', `from ai.idea_discovery import CURATED_VIRAL_IDEAS, CATEGORY_LABELS; import json; cat = '${category}'; ideas = [i for i in CURATED_VIRAL_IDEAS if not cat or cat == 'all' or i.get('category') == cat or (cat == 'oraculo_ia' and i.get('category') in ('oraculo_ia', 'paradojas_cuanticas'))]; print(json.dumps({'ideas': ideas, 'categories': CATEGORY_LABELS}))` ];
  
  const result = await runPythonCommand(args);
  try {
    const data = JSON.parse(result.stdout);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch ideas', raw: result.stdout || result.stderr });
  }
});

// 3. API: Trending NASA Discoveries
app.get('/api/discover', async (req, res) => {
  const refresh = req.query.refresh === 'true';
  const category = (req.query.category as string) || '';
  const date = (req.query.date as string) || '';
  const daysBack = (req.query.daysBack as string) || '';

  const pythonArgs = ['main.py', '--discover'];
  if (refresh) pythonArgs.push('--refresh');
  if (category) pythonArgs.push('--ideas-category', category);
  if (date) pythonArgs.push('--date', date);
  if (daysBack) pythonArgs.push('--days-back', daysBack);

  const result = await runPythonCommand(pythonArgs);
  
  // Read .trending_cache.json if available
  const cacheFile = path.join(OUTPUT_DIR, '.trending_cache.json');
  if (fs.existsSync(cacheFile)) {
    try {
      const cacheContent = fs.readFileSync(cacheFile, 'utf-8');
      const parsed = JSON.parse(cacheContent);
      return res.json({ items: parsed, stdout: result.stdout });
    } catch {
      // Fallback
    }
  }

  res.json({ stdout: result.stdout, stderr: result.stderr });
});

// 4. API: AI Script Generator Preview
app.post('/api/generate-script', async (req, res) => {
  const { topic, persona = 'oracle', entityName = 'Nexus', language = 'es', duration = 35 } = req.body;

  if (!topic) {
    return res.status(400).json({ error: 'Topic is required' });
  }

  const scriptPy = `
import json
from ai.script_generator import ScriptGenerator

gen = ScriptGenerator(persona="${persona}", entity_name="${entityName}")
script = gen.generate(topic="""${topic.replace(/"/g, '\\"')}""", target_duration=${duration}, language="${language}")
print("JSON_START")
print(json.dumps(script))
print("JSON_END")
`;

  const result = await runPythonCommand(['-c', scriptPy]);
  try {
    const stdout = result.stdout;
    const jsonStart = stdout.indexOf('JSON_START') + 10;
    const jsonEnd = stdout.indexOf('JSON_END');
    if (jsonStart !== -1 && jsonEnd !== -1) {
      const jsonStr = stdout.substring(jsonStart, jsonEnd).trim();
      const scriptData = JSON.parse(jsonStr);
      return res.json({ script: scriptData });
    }
    res.status(500).json({ error: 'Could not parse script output', logs: result.stdout + '\n' + result.stderr });
  } catch (err: any) {
    res.status(500).json({ error: err.message, logs: result.stdout + '\n' + result.stderr });
  }
});

// 5. API: Render Video Async Job
app.post('/api/render-video', (req, res) => {
  const {
    topic,
    persona = 'oracle',
    entityName = 'Nexus',
    duration = 35,
    provider = 'auto',
    format = 'vertical',
    orb = true,
    orbPalette = 'cosmic',
    orbPosition = 'presenter',
    orbAnimation = 'speaking',
    transition = 'fade',
    subtitleColor = 'yellow',
    subtitleAnimation = 'pop',
    subtitleWords = 3,
    customScript,
    enableSfx = true,
    enableAutoDucking = true,
    enableHookTitle = true,
    hookTitle,
  } = req.body;

  if (!topic) {
    return res.status(400).json({ error: 'Topic is required' });
  }

  const jobId = `job_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
  const job: RenderJob = {
    id: jobId,
    topic,
    persona,
    status: 'queued',
    progress: 5,
    logs: [`🚀 Initializing Video Production Job [${jobId}]...`],
    startTime: Date.now(),
  };

  renderJobs[jobId] = job;

  // Build python main.py command line flags
  const pyArgs = ['main.py', '--topic', topic];
  pyArgs.push('--persona', persona);
  pyArgs.push('--entity-name', entityName);
  pyArgs.push('--duration', duration.toString());
  pyArgs.push('--provider', provider);
  pyArgs.push('--format', format);

  if (orb) {
    pyArgs.push('--orb');
    pyArgs.push('--orb-palette', orbPalette);
    pyArgs.push('--orb-position', orbPosition);
    pyArgs.push('--orb-animation', orbAnimation);
  } else {
    pyArgs.push('--no-orb');
  }

  pyArgs.push('--transition', transition);
  pyArgs.push('--subtitle-color', subtitleColor);
  pyArgs.push('--subtitle-animation', subtitleAnimation);
  pyArgs.push('--subtitle-words', subtitleWords.toString());

  if (!enableSfx) pyArgs.push('--no-sfx');
  if (!enableAutoDucking) pyArgs.push('--no-auto-ducking');
  if (!enableHookTitle) pyArgs.push('--no-hook-title');
  if (hookTitle) pyArgs.push('--hook-title', hookTitle);

  if (customScript) {
    pyArgs.push('--script', JSON.stringify(customScript));
  }

  job.status = 'running';
  job.logs.push(`⚙️ Command: python3 ${pyArgs.join(' ')}`);

  const process = spawn('python3', pyArgs, { cwd: ROOT_DIR });

  process.stdout.on('data', (data) => {
    const chunk = data.toString();
    const lines = chunk.split('\n').filter(Boolean);
    for (const line of lines) {
      job.logs.push(line);
      // Update progress heuristics based on log lines
      if (line.includes('Generating structured AI script')) job.progress = 15;
      else if (line.includes('Fetching media clips')) job.progress = 30;
      else if (line.includes('Generating narration TTS')) job.progress = 45;
      else if (line.includes('Generating dynamic subtitles')) job.progress = 60;
      else if (line.includes('Rendering FFmpeg video')) job.progress = 75;
      else if (line.includes('Blending audio tracks')) job.progress = 85;
      else if (line.includes('Applying Reactive Orb')) job.progress = 90;
      else if (line.includes('Render completed successfully') || line.includes('Final video saved')) {
        job.progress = 100;
        // Parse folder name
        const match = line.match(/output\/([^/]+)/);
        if (match) job.folderName = match[1];
      }
    }
  });

  process.stderr.on('data', (data) => {
    job.logs.push(`[STDERR] ${data.toString()}`);
  });

  process.on('close', (code) => {
    job.endTime = Date.now();
    if (code === 0) {
      job.status = 'completed';
      job.progress = 100;
      job.logs.push(`✅ Video render completed successfully in ${((job.endTime - job.startTime) / 1000).toFixed(1)}s!`);
      // Try to find folder name if not captured yet
      if (!job.folderName) {
        const folders = fs.readdirSync(OUTPUT_DIR).filter((f) => {
          const stat = fs.statSync(path.join(OUTPUT_DIR, f));
          return stat.isDirectory() && f !== 'orb_previews';
        });
        if (folders.length > 0) {
          // pick latest directory
          folders.sort((a, b) => {
            return fs.statSync(path.join(OUTPUT_DIR, b)).mtimeMs - fs.statSync(path.join(OUTPUT_DIR, a)).mtimeMs;
          });
          job.folderName = folders[0];
        }
      }
    } else {
      job.status = 'error';
      job.error = `Process exited with code ${code}`;
      job.logs.push(`❌ Render failed with exit code ${code}`);
    }
  });

  res.json({ jobId, message: 'Video production job started', job });
});

// 6. API: Get Job Status
app.get('/api/jobs/:id', (req, res) => {
  const job = renderJobs[req.params.id];
  if (!job) {
    return res.status(404).json({ error: 'Job not found' });
  }
  res.json(job);
});

// 7. API: List Generated Videos Library
app.get('/api/videos', (req, res) => {
  if (!fs.existsSync(OUTPUT_DIR)) {
    return res.json([]);
  }

  const items = fs.readdirSync(OUTPUT_DIR);
  const videos = [];

  for (const item of items) {
    const dirPath = path.join(OUTPUT_DIR, item);
    if (fs.statSync(dirPath).isDirectory() && item !== 'orb_previews') {
      const files = fs.readdirSync(dirPath);
      const mp4File = files.find((f) => f.endsWith('.mp4'));
      const scriptFile = files.find((f) => f === 'script.json');
      const metaFile = files.find((f) => f === 'metadata.json');
      const narrationFile = files.find((f) => f === 'narration.mp3');

      let scriptData = null;
      let metaData = null;

      if (scriptFile) {
        try {
          scriptData = JSON.parse(fs.readFileSync(path.join(dirPath, scriptFile), 'utf-8'));
        } catch {}
      }

      if (metaFile) {
        try {
          metaData = JSON.parse(fs.readFileSync(path.join(dirPath, metaFile), 'utf-8'));
        } catch {}
      }

      const stats = fs.statSync(dirPath);

      if (mp4File) {
        videos.push({
          id: item,
          folderName: item,
          title: scriptData?.title || item.replace(/_/g, ' '),
          hook: scriptData?.hook || '',
          mp4Path: `/output-files/${item}/${mp4File}`,
          narrationPath: narrationFile ? `/output-files/${item}/${narrationFile}` : null,
          createdAt: stats.mtime,
          script: scriptData,
          metadata: metaData,
        });
      }
    }
  }

  // Sort newest first
  videos.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

  res.json(videos);
});

// Start Server with Vite Middleware in Dev or Static in Production
async function startServer() {
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(ROOT_DIR, 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`🌌 NASA Shorts & Oracle AI Studio running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
