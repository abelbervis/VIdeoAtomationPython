import React, { useState, useRef, useEffect } from 'react';

export default function App() {
  const [logs, setLogs] = useState<string[]>([
    'NASA Shorts Generator v2.4.0 (CLI)',
    'Sin interfaz gráfica.',
    '',
    'Uso: python main.py [opciones]',
    'Escribe "python main.py --help" para ver la lista de comandos.',
    '------------------------------------------------------------',
    '',
  ]);
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView();
  }, [logs]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      const cmd = input.trim();
      if (!cmd) return;

      const newLogs = [...logs, `$ ${cmd}`];

      if (cmd === 'clear' || cmd === 'cls') {
        setLogs([]);
        setInput('');
        return;
      }

      if (cmd === 'python main.py --help' || cmd === 'help') {
        newLogs.push(
          'Opciones:',
          '  --topic "TEMA"          Tema del video',
          '  --duration SEGUNDOS     Duración en segundos',
          '  --discover              Novedades de la NASA',
          '  --discover-ideas        Ideas de contenido',
          '  --top-choice N          Seleccionar opción',
          '  --orb                   Activar orbe gradiente',
          '  --test-orb              Probar orbe',
          '  ls output/              Listar videos',
          '  clear                   Limpiar la pantalla'
        );
      } else if (cmd.startsWith('python main.py')) {
        newLogs.push(
          'Ejecutando main.py...',
          'Buscando recursos en NASA API...',
          'Generando guion con IA...',
          'Sintetizando audio TTS...',
          'Renderizando con FFmpeg...',
          'Proceso completado. Video guardado en output/'
        );
      } else if (cmd === 'ls output/' || cmd === 'ls output') {
        newLogs.push('orb_previews/', 'agujeros_negros/', 'marte/');
      } else {
        newLogs.push(`Comando no reconocido: ${cmd}`);
      }

      setLogs(newLogs);
      setInput('');
    }
  };

  return (
    <div className="min-h-screen w-full bg-black text-zinc-200 font-mono text-sm p-4 select-text">
      <div className="space-y-1">
        {logs.map((log, index) => (
          <div key={index} className="whitespace-pre-wrap leading-relaxed">
            {log}
          </div>
        ))}
      </div>

      <div className="flex items-center gap-2 mt-2">
        <span className="text-zinc-400 font-bold">$</span>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          className="flex-1 bg-transparent text-white focus:outline-none font-mono"
          autoFocus
        />
      </div>

      <div ref={bottomRef} />
    </div>
  );
}
