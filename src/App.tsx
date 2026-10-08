import React, { useState, useRef, useEffect } from 'react';
import { Terminal, Cloud, Sparkles, Play, CheckCircle2, Copy, Monitor, Cpu, Shield, Network, ChevronRight, Layers, Volume2, ArrowRight } from 'lucide-react';

interface SlideData {
  id: number;
  layout: 'concept_card' | 'comparison_table' | 'architecture_flow' | 'terminal_code' | 'checklist';
  badge: string;
  title: string;
  subtitle: string;
  conceptTitle?: string;
  bullets?: string[];
  callout?: string;
  headers?: string[];
  rows?: string[][];
  steps?: { name: string; type: string; desc: string }[];
  codeLines?: string[];
  explanation?: string;
}

interface DialogueTurn {
  speaker: 'Alex' | 'Sam';
  role: string;
  slideId: number;
  text: string;
}

const GCP_PRESET_LESSONS = {
  cloud_run: {
    key: 'cloud_run',
    title: 'Cloud Run: De Servidores a Serverless',
    category: 'Google Cloud • Serverless Compute',
    summary: 'Ejecución de contenedores con auto-escalado de 0 a N instancias en milisegundos sin gestionar infraestructura.',
    icon: Cpu,
    slides: [
      {
        id: 1,
        layout: 'concept_card' as const,
        badge: 'Serverless Compute',
        title: '¿Qué es realmente Cloud Run?',
        subtitle: 'Contenedores OCI totalmente gestionados con escalado a cero',
        conceptTitle: 'La revolución del cómputo moderno',
        bullets: [
          'Empaqueta cualquier backend en un contenedor Docker estándar.',
          'Escala automáticamente de 0 a cientos de instancias en segundos.',
          'Pagas estrictamente por milisegundo de ejecución.',
          'Sin mantenimiento de SO ni parches de kernel.'
        ],
        callout: '💡 Regla de Oro: Si tu backend atiende peticiones HTTP o webhooks, Cloud Run es ~90% más económico que una VM 24/7.'
      },
      {
        id: 2,
        layout: 'comparison_table' as const,
        badge: 'Trade-offs Arquitectónicos',
        title: 'Cloud Run vs Compute Engine (VMs)',
        subtitle: 'Matriz de decisión para cargas de trabajo en producción',
        headers: ['Criterio', 'Cloud Run (Serverless)', 'Compute Engine (VM)'],
        rows: [
          ['Escalado a cero', '✅ Sí (0€ sin visitas)', '❌ No (Pagas 24/7 encendido)'],
          ['Mantenimiento SO', '✅ 100% Google Cloud', '⚠️ Tú gestionas parches y Linux'],
          ['Tiempo de arranque', '⚡ Segundos (Cold start ~1s)', '⏳ Minutos para boot de VM'],
          ['Caso de uso ideal', 'APIs REST, Webhooks, Apps web', 'Monolitos legacy, ERPs, kernels custom']
        ]
      },
      {
        id: 3,
        layout: 'architecture_flow' as const,
        badge: 'Flujo Seguro de Red',
        title: 'Arquitectura Privada de Extremo a Extremo',
        subtitle: 'De Internet a Cloud SQL sin exponer jamás IPs públicas',
        steps: [
          { name: 'Usuario Final', type: 'client', desc: 'Petición HTTPS :443' },
          { name: 'Cloud Armor', type: 'security', desc: 'WAF & Mitigación DDoS' },
          { name: 'Cloud Run', type: 'compute', desc: 'Contenedor auto-scale (0..N)' },
          { name: 'VPC Connector', type: 'network', desc: 'Túnel privado Serverless' },
          { name: 'Cloud SQL', type: 'database', desc: 'PostgreSQL (Solo IP Privada)' }
        ]
      },
      {
        id: 4,
        layout: 'terminal_code' as const,
        badge: 'Google Cloud CLI',
        title: 'Despliegue con un Solo Comando',
        subtitle: 'Flags indispensables de `gcloud` para producción',
        codeLines: [
          '# Despliegue en producción con CPU boost activado',
          '$ gcloud run deploy api-pedidos \\',
          '    --image gcr.io/empresa-prod/api:v2.1 \\',
          '    --region europe-west1 \\',
          '    --min-instances 0 \\',
          '    --max-instances 25 \\',
          '    --cpu-boost \\',
          '    --allow-unauthenticated'
        ],
        explanation: '⚡ La flag --cpu-boost asigna CPU adicional durante el arranque para reducir el cold start a menos de 600ms.'
      },
      {
        id: 5,
        layout: 'checklist' as const,
        badge: 'Checklist Final',
        title: 'El Veredicto del Arquitecto',
        subtitle: 'Buenas prácticas oficiales antes de ir a producción',
        bullets: [
          'Concurrencia: Calibra el número de peticiones simultáneas por contenedor según tu lenguaje.',
          'Secretos: Nunca incluyas credenciales en variables de entorno; móntalas desde Secret Manager.',
          'Bases de Datos: Utiliza Serverless VPC Access para aislar Cloud SQL en IP privada.'
        ],
        callout: '🎯 Veredicto: Elige Cloud Run como tu estándar predeterminado para microservicios y APIs en GCP.'
      }
    ],
    dialogue: [
      { speaker: 'Alex' as const, role: 'Cloud Architect', slideId: 1, text: 'Bienvenidos a este deep dive de Google Cloud. Hoy vamos a desmontar Cloud Run y entender cómo cambia las reglas del juego.' },
      { speaker: 'Sam' as const, role: 'Senior DevOps', slideId: 1, text: '¿Y esto es simplemente otro contenedor Docker en la nube o realmente resuelve un problema de costes y arquitectura?' },
      { speaker: 'Alex' as const, role: 'Cloud Architect', slideId: 1, text: 'Resuelve lo mejor de dos mundos: la libertad total de un contenedor Docker, pero con escalado a cero para pagar solo por los milisegundos que procesas.' },
      { speaker: 'Sam' as const, role: 'Senior DevOps', slideId: 2, text: 'Frente a una máquina virtual de Compute Engine tradicional, ¿dónde está la verdadera ventaja financiera?' },
      { speaker: 'Alex' as const, role: 'Cloud Architect', slideId: 2, text: 'En una VM pagas las veinticuatro horas aunque no haya tráfico a las tres de la madrugada. En Cloud Run la factura es cero euros cuando no hay visitas.' },
      { speaker: 'Sam' as const, role: 'Senior DevOps', slideId: 3, text: '¿Y cómo protegemos la base de datos si nuestro contenedor vive en el entorno serverless de Google?' },
      { speaker: 'Alex' as const, role: 'Cloud Architect', slideId: 3, text: 'Usamos Cloud Armor en el perímetro y un Serverless VPC Connector para comunicar Cloud Run con Cloud SQL por IP interna privada.' },
      { speaker: 'Sam' as const, role: 'Senior DevOps', slideId: 4, text: 'Y el despliegue con gcloud es directo con apenas unas flags para controlar el cold start y la concurrencia.' },
      { speaker: 'Alex' as const, role: 'Cloud Architect', slideId: 5, text: 'Exacto. Cloud Run te da la máxima velocidad de iteración con el mínimo coste operativo.' }
    ]
  },
  iam_security: {
    key: 'iam_security',
    title: 'IAM: Principio de Menor Privilegio',
    category: 'Google Cloud • Security & IAM',
    summary: 'Gestión de identidades, Service Accounts aisladas y por qué nunca debes usar roles primitivos en producción.',
    icon: Shield,
    slides: [
      {
        id: 1,
        layout: 'concept_card' as const,
        badge: 'Seguridad • Identidad',
        title: 'La Trinidad de Cloud IAM',
        subtitle: '¿Quién puede hacer qué sobre qué recurso?',
        conceptTitle: 'Modelo de Acceso Seguro',
        bullets: [
          'Miembro: Quién accede (Usuario, Grupo o Service Account de máquina).',
          'Rol: Conjunto de permisos específicos (ej. roles/pubsub.publisher).',
          'Recurso: Sobre qué actúa (Bucket, Instancia, Proyecto).',
          'Denegación por defecto: Todo acceso está bloqueado hasta otorgar una política.'
        ],
        callout: '🔒 Principio de Menor Privilegio: Concede solo el mínimo permiso indispensable por el menor tiempo necesario.'
      },
      {
        id: 2,
        layout: 'comparison_table' as const,
        badge: 'Tipos de Roles',
        title: 'Roles Primitivos vs Roles Predefinidos',
        subtitle: 'El riesgo crítico de otorgar Editor u Owner',
        headers: ['Característica', 'Roles Primitivos (Antiguos)', 'Roles Predefinidos (Recomendados)'],
        rows: [
          ['Ejemplos', 'Viewer, Editor, Owner', 'roles/storage.objectViewer, roles/run.developer'],
          ['Alcance', 'Global sobre todo el proyecto', 'Quirúrgico sobre un servicio concreto'],
          ['Riesgo', '🔴 Crítico (Borrado accidental)', '🟢 Mínimo (Permisos estrictos)'],
          ['Uso en producción', '❌ Prohibido', '✅ Estándar oficial de Google Cloud']
        ]
      },
      {
        id: 3,
        layout: 'terminal_code' as const,
        badge: 'CLI • Service Accounts',
        title: 'Creación de Service Account Dedicada',
        subtitle: 'Asignación de roles granulares con gcloud',
        codeLines: [
          '# 1. Crear Service Account dedicada',
          '$ gcloud iam service-accounts create sa-pedidos \\',
          '    --display-name="SA para API de Pedidos"',
          '',
          '# 2. Asignar rol granular sin privilegios excesivos',
          '$ gcloud projects add-iam-policy-binding mi-proyecto \\',
          '    --member="serviceAccount:sa-pedidos@mi-proyecto.iam.gserviceaccount.com" \\',
          '    --role="roles/datastore.user"'
        ],
        explanation: '🔑 Nunca descargues claves JSON a tu máquina; aprovecha Workload Identity o adjunta la SA directamente.'
      },
      {
        id: 4,
        layout: 'checklist' as const,
        badge: 'Auditoría',
        title: 'Reglas de Oro de Seguridad',
        subtitle: 'Prácticas recomendadas por Google Cloud Security',
        bullets: [
          'Una Service Account por microservicio (nunca compartas credenciales entre frontend y backend).',
          'Usa IAM Recommender para revocar permisos que no se hayan usado en 90 días.',
          'Heredabilidad: Las políticas IAM heredadas desde carpetas no pueden revocarse a nivel de proyecto.'
        ],
        callout: '🎯 Veredicto: El mejor sistema es aquel donde el atacante no puede hacer nada incluso si compromete una credencial.'
      }
    ],
    dialogue: [
      { speaker: 'Alex' as const, role: 'Cloud Architect', slideId: 1, text: 'Hoy nos adentramos en IAM, el guardián de todo lo que ocurre dentro de Google Cloud.' },
      { speaker: 'Sam' as const, role: 'Senior DevOps', slideId: 1, text: '¿Por qué la gente comete tantos errores con roles y credenciales al empezar?' },
      { speaker: 'Alex' as const, role: 'Cloud Architect', slideId: 1, text: 'Porque tienden a usar el atajo fácil: dar rol de Editor u Owner a todo el mundo para que las cosas funcionen rápido.' },
      { speaker: 'Sam' as const, role: 'Senior DevOps', slideId: 2, text: 'Y eso es el equivalente a darle las llaves maestras del edificio a un repartidor.' },
      { speaker: 'Alex' as const, role: 'Cloud Architect', slideId: 2, text: 'Tal cual. Los roles predefinidos te permiten otorgar exactamente la acción necesaria sin abrir la puerta a desastres.' },
      { speaker: 'Sam' as const, role: 'Senior DevOps', slideId: 3, text: 'Y para las aplicaciones, una Service Account propia sin claves JSON descargadas.' },
      { speaker: 'Alex' as const, role: 'Cloud Architect', slideId: 4, text: 'Menor privilegio siempre. Así es como se diseña una nube verdaderamente segura.' }
    ]
  },
  vpc_networking: {
    key: 'vpc_networking',
    title: 'VPC y Redes Globales en GCP',
    category: 'Google Cloud • Networking',
    summary: 'Virtual Private Cloud global, subredes interregionales sin VPNs complejas y Cloud NAT para servidores privados.',
    icon: Network,
    slides: [
      {
        id: 1,
        layout: 'concept_card' as const,
        badge: 'Redes Globales',
        title: 'La Singularidad de la VPC de Google',
        subtitle: 'Una sola red que abarca todo el planeta',
        conceptTitle: 'Red Definida por Software',
        bullets: [
          'VPC Global: A diferencia de otras nubes, una VPC en GCP cubre todas las regiones del mundo.',
          'Fibra Privada: El tráfico entre continentes viaja por los cables submarinos de Google con cifrado automático.',
          'Subredes Regionales: Creas subredes en Europa, EE.UU. o Asia conectadas por IPs privadas nativas.',
          'Sin necesidad de VPC Peering interregional costoso.'
        ],
        callout: '🌐 Ventaja Única: Dos servidores en regiones diferentes pueden hablarse por IP privada con latencias mínimas.'
      },
      {
        id: 2,
        layout: 'architecture_flow' as const,
        badge: 'Arquitectura Privada',
        title: 'Cloud NAT: Internet Seguro de Salida',
        subtitle: 'Cómo actualizar paquetes sin recibir ataques externos',
        steps: [
          { name: 'VMs Privadas', type: 'compute', desc: 'Sin IP Pública (10.0.1.0/24)' },
          { name: 'Cloud Router', type: 'network', desc: 'Enrutador BGP interno' },
          { name: 'Cloud NAT', type: 'security', desc: 'Traducción de direcciones' },
          { name: 'Internet', type: 'client', desc: 'Repositorios y APIs externas' }
        ]
      },
      {
        id: 3,
        layout: 'terminal_code' as const,
        badge: 'CLI • Serverless VPC Access',
        title: 'Conector de Red Serverless',
        subtitle: 'El puente entre Cloud Run y tu base de datos',
        codeLines: [
          '# Crear conector /28 en la región de tus microservicios',
          '$ gcloud compute networks vpc-access connectors create conector-prod \\',
          '    --region europe-west1 \\',
          '    --range 10.8.0.0/28 \\',
          '    --network red-produccion \\',
          '    --min-instances 2 \\',
          '    --max-instances 10'
        ],
        explanation: '📌 Requiere un bloque /28 libre dentro de tu VPC que no colisione con otras subredes.'
      }
    ],
    dialogue: [
      { speaker: 'Alex' as const, role: 'Cloud Architect', slideId: 1, text: 'Hoy hablamos del sistema circulatorio de Google Cloud: su red virtual VPC global.' },
      { speaker: 'Sam' as const, role: 'Senior DevOps', slideId: 1, text: 'Eso de que una VPC sea global sin configurar túneles entre continentes siempre me parece magia.' },
      { speaker: 'Alex' as const, role: 'Cloud Architect', slideId: 1, text: 'Es el fruto de la inversión multimillonaria de Google en fibra submarina privada. Todo queda bajo una misma red lógica.' },
      { speaker: 'Sam' as const, role: 'Senior DevOps', slideId: 2, text: '¿Y para dar salida a internet a servidores sin IP pública usamos Cloud NAT?' },
      { speaker: 'Alex' as const, role: 'Cloud Architect', slideId: 2, text: 'Exactamente. Descargas paquetes y llamadas a APIs de forma segura, bloqueando cualquier conexión entrante.' }
    ]
  }
};

export default function App() {
  const [activeTab, setActiveTab] = useState<'terminal' | 'gcp_studio'>('gcp_studio');
  const [selectedLessonKey, setSelectedLessonKey] = useState<keyof typeof GCP_PRESET_LESSONS>('cloud_run');
  const [activeSlideIndex, setActiveSlideIndex] = useState(0);
  const [activeDialogueIndex, setActiveDialogueIndex] = useState(0);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [copiedCmd, setCopiedCmd] = useState(false);

  // Terminal state
  const [logs, setLogs] = useState<string[]>([
    '══════════════════════════════════════════════════════════════',
    '☁️  GOOGLE CLOUD PLATFORM • NOTEBOOK LM VIDEO STUDIO  🎙️',
    '   Motor de Video Tutoriales & Shorts Técnicos Automatizados',
    '══════════════════════════════════════════════════════════════',
    '',
    'Comandos principales disponibles:',
    '  python gcp_tutorial.py --sample         (Genera tutorial NotebookLM completo)',
    '  python gcp_tutorial.py --list-topics    (Lista temas oficiales curados de GCP)',
    '  python gcp_tutorial.py --slides-only    (Exporta diapositivas vectoriales HD)',
    '  python main.py --help                  (CLI de shorts científicos de la NASA)',
    '--------------------------------------------------------------',
    ''
  ]);
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  const currentLesson = GCP_PRESET_LESSONS[selectedLessonKey];
  const currentSlide = currentLesson.slides[activeSlideIndex] || currentLesson.slides[0];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const runTerminalCommand = (rawCmd: string) => {
    const cmd = rawCmd.trim();
    if (!cmd) return;

    const newLogs = [...logs, `$ ${cmd}`];

    if (cmd === 'clear' || cmd === 'cls') {
      setLogs([]);
      setInput('');
      return;
    }

    if (cmd === 'python gcp_tutorial.py --help' || cmd === 'gcp --help') {
      newLogs.push(
        'Uso: python gcp_tutorial.py [OPCIONES]',
        '',
        'Opciones principales:',
        '  --topic "TEMA"          Tema de GCP (ej. Cloud Run, IAM, VPC, BigQuery)',
        '  --notes "TUS NOTAS"     Notas o apuntes de estudio para transformar en video',
        '  --notes-file ARCHIVO    Ruta a archivo .md/.txt con tus apuntes',
        '  --sample / --demo       Ejecuta demo completa de Cloud Run vs Compute Engine',
        '  --format TIPO           horizontal (1920x1080) o vertical (1080x1920 Shorts)',
        '  --slides-only           Exporta únicamente las diapositivas HD a output/gcp_tutorials/',
        '  --list-topics           Lista los temas curados con diapositivas predefinidas',
        '  --interactive           Revisa guion y diapositivas en terminal antes de renderizar',
        '  --no-music              Desactiva la pista ambiental de fondo'
      );
    } else if (cmd === 'python gcp_tutorial.py --list-topics') {
      newLogs.push(
        'Temas Curados de Google Cloud Disponibles:',
        '  • CLOUD_RUN: Cloud Run: De Servidores a Serverless sin Perder el Control',
        '    Categoría: Google Cloud • Serverless Compute | 5 Diapositivas | 11 Intervenciones',
        '  • IAM_SECURITY: IAM en Google Cloud: El Principio de Menor Privilegio',
        '    Categoría: Google Cloud • Security & IAM | 5 Diapositivas | 11 Intervenciones',
        '  • VPC_NETWORKING: VPC y Redes en GCP: Conexión Privada sin Exponer Datos',
        '    Categoría: Google Cloud • Networking | 5 Diapositivas | 11 Intervenciones'
      );
    } else if (cmd.includes('gcp_tutorial.py --slides-only')) {
      newLogs.push(
        '🖼️ [GCP Slide Renderer] Generando diapositivas vectoriales SVG...',
        '   • Rasterizando a 1920x1080 PNG con FFmpeg librsvg...',
        '   ✅ Slide 01: Concept Card (Serverless)',
        '   ✅ Slide 02: Matriz Comparativa (Cloud Run vs VM)',
        '   ✅ Slide 03: Arquitectura de Red (VPC Access a Cloud SQL)',
        '   ✅ Slide 04: Terminal gcloud CLI (CPU Boost)',
        '   ✅ Slide 05: Checklist de Producción',
        '🎉 Diapositivas HD listas en: output/gcp_tutorials/cloud_run_slides/'
      );
    } else if (cmd.includes('gcp_tutorial.py')) {
      newLogs.push(
        '🚀 [GCP NotebookLM Studio] Iniciando pipeline de video tutorial...',
        '   • Estructurando lección pedagógica de dos hosts...',
        '   🎙️ Sintetizando voz Alex (Cloud Solutions Architect) con EQ Studio...',
        '   🎙️ Sintetizando voz Sam (Senior DevOps) con pitch dinámico...',
        '   🖼️ Ensamblando 5 diapositivas con avatares de speakers activos...',
        '   🎬 Codificando video sincronizado a 1080p con subtítulos...',
        '   🎶 Mezclando música ambiental lo-fi tech con auto-ducking...',
        '✅ ¡Tutorial completado! Video guardado en output/gcp_tutorials/tutorial_cloud_run.mp4 (1080p)'
      );
    } else if (cmd === 'ls output/' || cmd === 'ls output' || cmd === 'ls output/gcp_tutorials/') {
      newLogs.push(
        'gcp_tutorials/tutorial_cloud_run.mp4',
        'gcp_tutorials/cloud_run_slides/slide_01.png',
        'gcp_tutorials/cloud_run_slides/slide_02.png',
        'gcp_tutorials/cloud_run_slides/slide_03.png',
        'gcp_tutorials/cloud_run_slides/slide_04.png',
        'gcp_tutorials/cloud_run_slides/slide_05.png'
      );
    } else if (cmd === 'python main.py --help') {
      newLogs.push(
        'Uso: python main.py [opciones]',
        '  --topic "TEMA"          Tema del video de la NASA',
        '  --trending              Detector automático de descubrimientos virales',
        '  --gcp-tutorial          Lanza el generador de video tutoriales de GCP (NotebookLM)'
      );
    } else {
      newLogs.push(`Comando ejecutado: ${cmd}`);
    }

    setLogs(newLogs);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      runTerminalCommand(input);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCmd(true);
    setTimeout(() => setCopiedCmd(false), 2000);
  };

  const simulateAudioPlay = (dialogueText: string, speaker: string) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(dialogueText);
      utterance.lang = 'es-ES';
      utterance.pitch = speaker === 'Sam' ? 1.25 : 0.95;
      utterance.rate = speaker === 'Sam' ? 1.05 : 0.95;
      utterance.onstart = () => setIsPlayingAudio(true);
      utterance.onend = () => setIsPlayingAudio(false);
      utterance.onerror = () => setIsPlayingAudio(false);
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col font-sans select-text">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-[#0B0F19]/90 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-sky-400 to-emerald-400 p-0.5 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <div className="w-full h-full bg-[#0B0F19] rounded-[10px] flex items-center justify-center">
              <Cloud className="w-5 h-5 text-sky-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight text-white">GCP NotebookLM Studio</h1>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Nuevo Comando CLI
              </span>
            </div>
            <p className="text-xs text-slate-400">Generador de Video Tutoriales & Debate de 2 Voces con Diapositivas HD</p>
          </div>
        </div>

        {/* Mode Switcher Tabs */}
        <div className="flex items-center bg-slate-900/80 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('gcp_studio')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'gcp_studio'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Estudio Visual de Diapositivas
          </button>
          <button
            onClick={() => setActiveTab('terminal')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'terminal'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            Consola Terminal CLI
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      {activeTab === 'gcp_studio' ? (
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Topic Selector & NotebookLM Debate Transcript */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            {/* Lesson Selector Card */}
            <div className="bg-[#0D1424] border border-slate-800/80 rounded-2xl p-5 shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-sky-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" /> Temas de Estudio Curados
                </span>
                <span className="text-xs text-slate-400">Selecciona para cargar</span>
              </div>

              <div className="space-y-2">
                {(Object.keys(GCP_PRESET_LESSONS) as Array<keyof typeof GCP_PRESET_LESSONS>).map((key) => {
                  const item = GCP_PRESET_LESSONS[key];
                  const Icon = item.icon;
                  const isSelected = selectedLessonKey === key;
                  return (
                    <button
                      key={key}
                      onClick={() => {
                        setSelectedLessonKey(key);
                        setActiveSlideIndex(0);
                        setActiveDialogueIndex(0);
                      }}
                      className={`w-full text-left p-3.5 rounded-xl border transition-all flex items-start gap-3.5 ${
                        isSelected
                          ? 'bg-blue-600/10 border-blue-500/40 text-white shadow-lg shadow-blue-500/5'
                          : 'bg-slate-900/40 border-slate-800/60 text-slate-300 hover:bg-slate-900/80 hover:border-slate-700'
                      }`}
                    >
                      <div className={`p-2 rounded-lg mt-0.5 ${isSelected ? 'bg-blue-500 text-white' : 'bg-slate-800 text-slate-400'}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-semibold truncate">{item.title}</h3>
                          {isSelected && <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>}
                        </div>
                        <p className="text-xs text-slate-400 line-clamp-1 mt-0.5">{item.category}</p>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* CLI Command Shortcut */}
              <div className="mt-4 pt-4 border-t border-slate-800/80">
                <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                  <span>Comando dedicado de terminal:</span>
                  <button
                    onClick={() => copyToClipboard(`python gcp_tutorial.py --topic "${selectedLessonKey}"`)}
                    className="text-sky-400 hover:text-sky-300 flex items-center gap-1 font-medium"
                  >
                    {copiedCmd ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    {copiedCmd ? 'Copiado' : 'Copiar'}
                  </button>
                </div>
                <div className="bg-black/60 rounded-lg p-2.5 font-mono text-xs text-emerald-400 flex items-center justify-between border border-slate-800">
                  <span className="truncate">$ python gcp_tutorial.py --topic "{selectedLessonKey}"</span>
                  <button
                    onClick={() => {
                      runTerminalCommand(`python gcp_tutorial.py --topic "${selectedLessonKey}"`);
                      setActiveTab('terminal');
                    }}
                    className="ml-2 text-xs bg-emerald-500/20 text-emerald-300 px-2.5 py-1 rounded hover:bg-emerald-500/30 transition shrink-0 flex items-center gap-1 font-sans"
                  >
                    <Play className="w-3 h-3 fill-current" /> Ejecutar
                  </button>
                </div>
              </div>
            </div>

            {/* NotebookLM Dialogue Transcript */}
            <div className="bg-[#0D1424] border border-slate-800/80 rounded-2xl p-5 shadow-xl flex-1 flex flex-col min-h-[380px]">
              <div className="flex items-center justify-between mb-3.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                    🎙️ Debate NotebookLM (Alex & Sam)
                  </span>
                </div>
                <span className="text-[11px] text-slate-400">
                  {currentLesson.dialogue.length} intervenciones
                </span>
              </div>

              <div className="space-y-3 overflow-y-auto max-h-[380px] pr-1.5 flex-1">
                {currentLesson.dialogue.map((turn, i) => {
                  const isAlex = turn.speaker === 'Alex';
                  const isActive = activeDialogueIndex === i;
                  return (
                    <div
                      key={i}
                      onClick={() => {
                        setActiveDialogueIndex(i);
                        setActiveSlideIndex(Math.max(0, turn.slideId - 1));
                      }}
                      className={`p-3 rounded-xl border transition-all cursor-pointer ${
                        isActive
                          ? isAlex
                            ? 'bg-blue-950/40 border-blue-500 text-white shadow-md'
                            : 'bg-emerald-950/40 border-emerald-500 text-white shadow-md'
                          : 'bg-slate-900/40 border-slate-800/60 text-slate-300 hover:bg-slate-900'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <span
                            className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                              isAlex ? 'bg-blue-600' : 'bg-emerald-600'
                            }`}
                          >
                            {turn.speaker[0]}
                          </span>
                          <span className="text-xs font-bold">{turn.speaker}</span>
                          <span className="text-[10px] text-slate-400 font-medium">({turn.role})</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-sky-400 font-mono">
                            Slide {turn.slideId}
                          </span>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              simulateAudioPlay(turn.text, turn.speaker);
                            }}
                            className="p-1 rounded text-slate-400 hover:text-white transition"
                            title="Escuchar locución simulada"
                          >
                            <Volume2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                      <p className="text-xs leading-relaxed text-slate-200 pl-8">{turn.text}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Right Column: Visual Slide Canvas Preview */}
          <div className="lg:col-span-7 flex flex-col gap-4">
            {/* Slide Navigation Header */}
            <div className="bg-[#0D1424] border border-slate-800/80 rounded-2xl p-4 flex items-center justify-between shadow-xl">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <Monitor className="w-4 h-4 text-sky-400" /> Diapositiva en Video: {activeSlideIndex + 1} de {currentLesson.slides.length}
                </span>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono">
                  {currentSlide.layout}
                </span>
              </div>

              <div className="flex items-center gap-2">
                {currentLesson.slides.map((s, idx) => (
                  <button
                    key={s.id}
                    onClick={() => setActiveSlideIndex(idx)}
                    className={`w-7 h-7 rounded-lg text-xs font-bold transition-all ${
                      activeSlideIndex === idx
                        ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30'
                        : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {idx + 1}
                  </button>
                ))}
              </div>
            </div>

            {/* The Visual Slide Mockup (Renders layout according to currentSlide) */}
            <div className="bg-[#0A0E17] border border-slate-800 rounded-2xl p-7 shadow-2xl relative overflow-hidden flex flex-col min-h-[520px] justify-between">
              {/* Subtle Rainbow Top Edge like Google Cloud */}
              <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-blue-500 via-emerald-500 via-amber-400 to-rose-500" />

              {/* Slide Top Metadata */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-500/10 text-blue-400 border border-blue-500/30">
                      {currentLesson.category}
                    </span>
                  </div>
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-800/80 text-sky-300 border border-slate-700">
                    {currentSlide.badge}
                  </span>
                </div>

                <h2 className="text-2xl font-extrabold text-white tracking-tight">{currentSlide.title}</h2>
                <p className="text-sm text-slate-400 mt-1">{currentSlide.subtitle}</p>
              </div>

              {/* Slide Body by Layout */}
              <div className="my-6 flex-1 flex flex-col justify-center">
                {currentSlide.layout === 'concept_card' || currentSlide.layout === 'checklist' ? (
                  <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 shadow-lg space-y-4">
                    {currentSlide.conceptTitle && (
                      <h3 className="text-base font-bold text-sky-300">{currentSlide.conceptTitle}</h3>
                    )}
                    <div className="space-y-2.5">
                      {currentSlide.bullets?.map((b, i) => (
                        <div key={i} className="flex items-start gap-2.5 text-xs text-slate-200">
                          <div className="w-5 h-5 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                            ✓
                          </div>
                          <span className="leading-relaxed">{b}</span>
                        </div>
                      ))}
                    </div>
                    {currentSlide.callout && (
                      <div className="bg-amber-950/20 border-l-4 border-amber-500 p-3 rounded-r-lg text-xs text-amber-200 leading-relaxed">
                        {currentSlide.callout}
                      </div>
                    )}
                  </div>
                ) : currentSlide.layout === 'comparison_table' ? (
                  <div className="border border-slate-800 rounded-xl overflow-hidden shadow-lg bg-slate-900/40">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="bg-slate-900 border-b border-slate-800">
                          {currentSlide.headers?.map((h, i) => (
                            <th key={i} className="p-3 font-bold text-slate-300">
                              {h}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 font-sans">
                        {currentSlide.rows?.map((row, rIdx) => (
                          <tr key={rIdx} className={rIdx % 2 === 0 ? 'bg-slate-950/40' : 'bg-slate-900/20'}>
                            {row.map((cell, cIdx) => (
                              <td
                                key={cIdx}
                                className={`p-3 ${
                                  cIdx === 0 ? 'font-semibold text-slate-300' : cIdx === 1 ? 'text-sky-300' : 'text-slate-400'
                                }`}
                              >
                                {cell}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : currentSlide.layout === 'architecture_flow' ? (
                  <div className="flex flex-wrap items-center justify-center gap-3 py-4">
                    {currentSlide.steps?.map((step, idx) => (
                      <React.Fragment key={idx}>
                        <div className="bg-slate-900/80 border border-slate-700/80 rounded-xl p-3.5 w-44 shadow-lg text-center flex flex-col justify-between">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-sky-400 mb-1">
                            {step.type}
                          </span>
                          <h4 className="text-sm font-bold text-white">{step.name}</h4>
                          <span className="text-[11px] text-slate-400 mt-2 bg-slate-950 px-2 py-1 rounded border border-slate-800">
                            {step.desc}
                          </span>
                        </div>
                        {idx < (currentSlide.steps?.length || 0) - 1 && (
                          <div className="flex items-center text-sky-400/80">
                            <ArrowRight className="w-5 h-5 animate-pulse" />
                          </div>
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                ) : currentSlide.layout === 'terminal_code' ? (
                  <div className="bg-[#050811] border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
                    <div className="bg-slate-900/90 px-4 py-2 border-b border-slate-800 flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                        <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                        <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                      </div>
                      <span className="text-[11px] font-mono text-slate-400">bash — gcloud deploy</span>
                      <div className="w-12" />
                    </div>
                    <div className="p-4 font-mono text-xs space-y-1.5 overflow-x-auto">
                      {currentSlide.codeLines?.map((line, idx) => (
                        <div
                          key={idx}
                          className={
                            line.startsWith('$')
                              ? 'text-sky-400 font-bold'
                              : line.startsWith('#')
                              ? 'text-slate-500'
                              : 'text-slate-200'
                          }
                        >
                          {line}
                        </div>
                      ))}
                    </div>
                    {currentSlide.explanation && (
                      <div className="bg-blue-950/30 border-t border-slate-800 p-3 text-xs text-sky-300">
                        {currentSlide.explanation}
                      </div>
                    )}
                  </div>
                ) : null}
              </div>

              {/* Bottom Presenter Overlay (NotebookLM Status) */}
              <div className="bg-slate-950/90 border border-slate-800 rounded-xl p-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center">
                    A
                  </div>
                  <div>
                    <span className="text-xs font-bold text-white block">Alex</span>
                    <span className="text-[10px] text-blue-400">Cloud Solutions Architect</span>
                  </div>
                </div>

                <div className="text-center">
                  <span className="text-[10px] uppercase tracking-widest font-bold text-slate-500">
                    NOTEBOOK LM AUDIO OVERVIEW
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <span className="text-xs font-bold text-white block">Sam</span>
                    <span className="text-[10px] text-emerald-400">Senior DevOps Engineer</span>
                  </div>
                  <div className="w-7 h-7 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center">
                    S
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions Bar */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => {
                  runTerminalCommand(`python gcp_tutorial.py --slides-only --topic "${selectedLessonKey}"`);
                  setActiveTab('terminal');
                }}
                className="bg-slate-900 border border-slate-800 text-slate-200 hover:text-white hover:bg-slate-800/80 p-3 rounded-xl text-xs font-medium flex items-center justify-center gap-2 transition"
              >
                <Monitor className="w-4 h-4 text-sky-400" /> Exportar Diapositivas HD (PNG)
              </button>
              <button
                onClick={() => {
                  runTerminalCommand(`python gcp_tutorial.py --topic "${selectedLessonKey}"`);
                  setActiveTab('terminal');
                }}
                className="bg-blue-600 hover:bg-blue-500 text-white p-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-blue-600/30 transition"
              >
                <Play className="w-4 h-4 fill-current" /> Renderizar Video Tutorial Completo
              </button>
            </div>
          </div>
        </main>
      ) : (
        /* Terminal CLI View */
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full flex flex-col">
          {/* Quick Command Chips */}
          <div className="flex flex-wrap items-center gap-2 mb-4 pb-3 border-b border-slate-800">
            <span className="text-xs text-slate-400 font-medium mr-1">Comandos rápidos:</span>
            {[
              'python gcp_tutorial.py --sample',
              'python gcp_tutorial.py --list-topics',
              'python gcp_tutorial.py --slides-only --topic "cloud_run"',
              'python gcp_tutorial.py --help',
              'python main.py --help',
              'ls output/'
            ].map((cmd) => (
              <button
                key={cmd}
                onClick={() => runTerminalCommand(cmd)}
                className="text-xs font-mono bg-slate-900 border border-slate-800 text-slate-300 hover:text-sky-300 hover:border-slate-700 px-2.5 py-1 rounded-md transition"
              >
                {cmd}
              </button>
            ))}
          </div>

          {/* Terminal Box */}
          <div className="flex-1 bg-black/95 border border-slate-800 rounded-2xl p-5 font-mono text-sm shadow-2xl flex flex-col min-h-[500px]">
            <div className="flex-1 overflow-y-auto space-y-1 pr-2">
              {logs.map((log, index) => (
                <div
                  key={index}
                  className={`whitespace-pre-wrap leading-relaxed ${
                    log.startsWith('$')
                      ? 'text-emerald-400 font-bold'
                      : log.startsWith('✅')
                      ? 'text-emerald-300'
                      : log.startsWith('❌')
                      ? 'text-rose-400'
                      : log.startsWith('☁️') || log.startsWith('🚀')
                      ? 'text-sky-300 font-bold'
                      : 'text-zinc-300'
                  }`}
                >
                  {log}
                </div>
              ))}
              <div ref={bottomRef} />
            </div>

            {/* Input Line */}
            <div className="flex items-center gap-2 mt-4 pt-3 border-t border-zinc-900">
              <span className="text-emerald-400 font-bold">$</span>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Escribe un comando (ej: python gcp_tutorial.py --sample)"
                className="flex-1 bg-transparent text-white focus:outline-none font-mono text-sm placeholder:text-zinc-600"
                autoFocus
              />
            </div>
          </div>
        </main>
      )}
    </div>
  );
}
