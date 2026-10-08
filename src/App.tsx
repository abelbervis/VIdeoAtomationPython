import React, { useState, useRef, useEffect } from 'react';
import { Terminal, Cloud, Sparkles, Play, CheckCircle2, Copy, Monitor, Cpu, Shield, Network, HardDrive, ChevronRight, Layers, Volume2, ArrowRight, Database, FolderTree, GitBranch, Zap, X, Search, Film, Sliders, Plus, Check, Eye, Video } from 'lucide-react';
import { HybridTimelineStudio } from './components/HybridTimelineStudio';

export interface VisualResourceItem {
  id: string;
  kind: 'slide' | 'motion' | 'console' | 'terminal' | 'custom';
  name: string;
  description: string;
  intent_keywords: string[];
  priority: number;
}

export const DEFAULT_VISUAL_RESOURCES: VisualResourceItem[] = [
  {
    id: "slide_concept_card",
    kind: "slide",
    name: "Diapositiva: Tarjeta Conceptual Clave",
    description: "Ideal para definiciones, problemas fundamentales y reglas de oro con bullets.",
    intent_keywords: ["concepto", "definicion", "que es", "regla de oro", "importante", "resumen", "fundamento", "alerta"],
    priority: 1
  },
  {
    id: "slide_comparison_table",
    kind: "slide",
    name: "Diapositiva: Matriz Comparativa de Servicios",
    description: "Ideal para comparar 2 o más servicios, pros, contras, tarifas y casos de uso.",
    intent_keywords: ["vs", "comparativa", "diferencia", "frente a", "tabla", "pros", "contras", "cual elegir", "ventajas"],
    priority: 3
  },
  {
    id: "slide_checklist",
    kind: "slide",
    name: "Diapositiva: Checklist de Buenas Prácticas",
    description: "Ideal para pasos numerados, requisitos previos y listas de verificación.",
    intent_keywords: ["checklist", "requisitos", "pasos", "mejores practicas", "verificacion", "paso a paso"],
    priority: 2
  },
  {
    id: "motion_hierarchy_tree",
    kind: "motion",
    name: "Animación RAG: Árbol Jerárquico de Recursos",
    description: "Visualiza la jerarquía de gobierno: Organización > Carpetas > Proyectos con herencia de políticas.",
    intent_keywords: ["jerarquia", "arbol", "organizacion", "carpetas", "proyectos", "herencia", "estructura", "gobierno"],
    priority: 4
  },
  {
    id: "motion_elastic_scale",
    kind: "motion",
    name: "Animación RAG: Escalado Serverless Elástico",
    description: "Visualiza contenedores multiplicándose de 0 a N réplicas bajo demanda y retorno a 0 coste.",
    intent_keywords: ["escala", "escalado", "serverless", "instancias", "pods", "concurrencia", "cold start", "auto-scaling", "multiplica"],
    priority: 4
  },
  {
    id: "motion_packet_flow",
    kind: "motion",
    name: "Animación RAG: Flujo de Paquetes en Red",
    description: "Visualiza paquetes y eventos viajando entre componentes en tiempo real (VPC, Pub/Sub).",
    intent_keywords: ["flujo", "viajan", "paquetes", "pubsub", "cola", "mensajes", "red", "vpc", "fan-out", "latencia"],
    priority: 4
  },
  {
    id: "motion_storage_lifecycle",
    kind: "motion",
    name: "Animación RAG: Ciclo de Vida y Transición de Datos",
    description: "Visualiza objetos transitando automáticamente a clases frías (Coldline) con cifrado AES-256.",
    intent_keywords: ["ciclo de vida", "transicion", "coldline", "archive", "cifrado", "objetos", "retencion", "aes-256"],
    priority: 4
  },
  {
    id: "console_walkthrough",
    kind: "console",
    name: "Consola Real de GCP: Simulación de Interfaz y Clics",
    description: "Demostración visual de la interfaz gráfica real de Google Cloud Console con cursor y menús.",
    intent_keywords: ["consola", "interfaz", "clic", "boton", "pantalla", "menu", "navegador", "ui", "abrimos la consola"],
    priority: 3
  },
  {
    id: "terminal_cli",
    kind: "terminal",
    name: "Terminal en Vivo: Comandos gcloud CLI",
    description: "Simulación de terminal tecleándose en vivo con comandos bash / gcloud y salida de ejecución.",
    intent_keywords: ["terminal", "comando", "gcloud", "bash", "cli", "tecleamos", "linea de comandos", "flags"],
    priority: 3
  }
];

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
  cloud_storage: {
    key: 'cloud_storage',
    title: 'Google Cloud Storage: Ahorra el 80% en tus Buckets',
    category: 'Google Cloud • Storage & Cost Optimization',
    summary: 'Consola real de GCP, las 4 metáforas cotidianas (Cajón, Armario, Bodega, Caja fuerte) y locución de hombre mexicano en primera persona.',
    icon: HardDrive,
    slides: [
      {
        id: 1,
        layout: 'concept_card' as const,
        badge: 'Alerta de Costos vs Solución',
        title: '¿Factura Gigantesca por Guardar Archivos?',
        subtitle: 'El error de pagar por servidores cuando solo necesitas guardar archivos',
        conceptTitle: 'Cero Servidores • Solo Centavos',
        bullets: [
          'Dejar discos SSD 24/7 sin usar te cuesta hasta $1,100 USD/mes por error.',
          'Con Cloud Storage solo pagas por los gigabytes que realmente ocupas.',
          'Escalabilidad infinita: sube 1 foto o 10 millones de backups sin crear particiones.',
          'Cifrado bancario automático AES-256 gestionado por Google.'
        ],
        callout: '💡 Regla de Oro: En lugar de tener un servidor encendido solo para servir archivos, usa Buckets y reduce tu factura hasta un 90%.'
      },
      {
        id: 2,
        layout: 'comparison_table' as const,
        badge: 'Las 4 Metáforas Cotidianas',
        title: 'Las 4 Clases de Almacenamiento con Metáforas Reales',
        subtitle: 'Asocia cada clase a un objeto de tu vida diaria para no pagar de más',
        headers: ['Clase', 'Metáfora Cotidiana', 'Frecuencia de Uso', 'Ahorro'],
        rows: [
          ['STANDARD', '📦 El cajón de tu escritorio', 'Diario (Web, fotos, APIs)', 'Tarifa base'],
          ['NEARLINE', '🗄️ El armario de tu casa', '1 vez al mes (Backups)', 'Ahorras 50%'],
          ['COLDLINE', '🏚️ La bodega o trastero', '1 vez al año (Históricos)', 'Ahorras 75%'],
          ['ARCHIVE', '🔒 Caja fuerte bajo tierra', 'Solo auditorías legales', 'Ahorras 90%']
        ]
      },
      {
        id: 3,
        layout: 'terminal_code' as const,
        badge: 'Consola de GCP en Vivo',
        title: 'Creación Rápida con gcloud storage CLI',
        subtitle: 'Una sola línea para automatizar tus respaldos a bajo costo',
        codeLines: [
          '# Crear bucket con región única y clase COLDLINE para ahorrar 75%',
          '$ gcloud storage buckets create gs://mi-empresa-backups-2025 \\',
          '    --location=us-central1 \\',
          '    --default-storage-class=COLDLINE',
          '',
          '# Subir archivos con cifrado automático',
          '$ gcloud storage cp -r ./mis-fotos gs://mi-empresa-backups-2025/'
        ],
        explanation: '✓ Bucket creado en 1.8 segundos con cifrado automático AES-256 en us-central1.'
      }
    ],
    dialogue: [
      { speaker: 'Alex' as const, role: 'Carlos (Ingeniero Cloud Mexicano)', slideId: 1, text: '¿Te ha llegado una factura gigantesca por guardar archivos en la nube o no sabes dónde guardar tus fotos y respaldos sin arruinarte? Hoy te explico en 3 minutos cómo funcionan los buckets de Google Cloud y cómo pagar solo centavos en lugar de cientos de dólares.' },
      { speaker: 'Alex' as const, role: 'Carlos (Ingeniero Cloud Mexicano)', slideId: 2, text: 'Para no pagar de más, piensa en esto con objetos de tu casa. Standard es el cajón de tu escritorio para el día a día. Nearline es el armario para una vez al mes. Coldline es la bodega para una vez al año. Y Archive es una caja fuerte bajo tierra a costo casi cero.' },
      { speaker: 'Alex' as const, role: 'Carlos (Ingeniero Cloud Mexicano)', slideId: 3, text: 'En resumen: guarda en Standard solo lo que uses a diario, pasa tus respaldos a Coldline o Archive, y elige una sola región. Con estas tres reglas, tus archivos estarán seguros y tu factura será mínima.' }
    ]
  },
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
  const [activeTab, setActiveTab] = useState<'hybrid_studio' | 'gcp_studio' | 'ai_motion' | 'terminal'>('hybrid_studio');
  const [selectedLessonKey, setSelectedLessonKey] = useState<keyof typeof GCP_PRESET_LESSONS>('cloud_storage');
  const [activeSlideIndex, setActiveSlideIndex] = useState(0);
  const [activeDialogueIndex, setActiveDialogueIndex] = useState(0);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [copiedCmd, setCopiedCmd] = useState(false);
  const [motionTopic, setMotionTopic] = useState('Estructura Organizacional en GCP');
  const [motionStage, setMotionStage] = useState(0);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [customMotionTopic, setCustomMotionTopic] = useState('');

  // LLM Provider & Failover state
  const [groqApiKey, setGroqApiKey] = useState<string>(() => localStorage.getItem('gcp_groq_key') || '');
  const [llmProvider, setLlmProvider] = useState<'auto' | 'gemini' | 'groq'>('auto');
  const [showApiKeysModal, setShowApiKeysModal] = useState(false);

  // Multi-Resource Hybrid Timeline state
  const [visualResources, setVisualResources] = useState<VisualResourceItem[]>(DEFAULT_VISUAL_RESOURCES);
  const [sceneResourceOverrides, setSceneResourceOverrides] = useState<Record<string, string>>({});
  const [activeHybridSceneIndex, setActiveHybridSceneIndex] = useState(0);
  const [showResourceCatalogModal, setShowResourceCatalogModal] = useState(false);
  const [showNewResourceModal, setShowNewResourceModal] = useState(false);
  const [newResourceForm, setNewResourceForm] = useState<{
    id: string;
    kind: 'slide' | 'motion' | 'console' | 'terminal' | 'custom';
    name: string;
    description: string;
    keywords: string;
    priority: number;
  }>({
    id: '',
    kind: 'custom',
    name: '',
    description: '',
    keywords: '',
    priority: 3
  });

  const handleSetSceneResource = (sceneIdx: number, resourceId: string) => {
    const key = `${selectedLessonKey}_${sceneIdx}`;
    setSceneResourceOverrides((prev) => ({
      ...prev,
      [key]: resourceId
    }));
  };

  const handleAddNewResource = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newResourceForm.name || !newResourceForm.id) return;
    const item: VisualResourceItem = {
      id: newResourceForm.id.toLowerCase().replace(/[^a-z0-9_]/g, '_'),
      kind: newResourceForm.kind,
      name: newResourceForm.name,
      description: newResourceForm.description,
      intent_keywords: newResourceForm.keywords
        .split(',')
        .map((s) => s.trim().toLowerCase())
        .filter(Boolean),
      priority: Number(newResourceForm.priority) || 2
    };
    setVisualResources((prev) => [...prev, item]);
    setShowNewResourceModal(false);
    setNewResourceForm({
      id: '',
      kind: 'custom',
      name: '',
      description: '',
      keywords: '',
      priority: 3
    });
  };

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
        '  --speed 1.2             Velocidad de locución de voces (por defecto 1.20x para ritmo ágil)',
        '  --fps 15                Cuadros por segundo (15 FPS para reducir el tamaño al mínimo)',
        '  --codec {x264, x265}    Códec de video (x264 universal o x265 HEVC de alta compresión)',
        '  --format TIPO           horizontal (1920x1080) o vertical (1080x1920 Shorts)',
        '  --slides-only           Exporta únicamente las diapositivas HD a output/gcp_tutorials/',
        '  --llm {auto,gemini,groq} Proveedor de IA: auto (Gemini con fallback a Groq), groq o gemini',
        '  --groq-key CLAVE        API Key de Groq para conmutar sin esperas si Gemini devuelve error 429',
        '  --strict                Modo estricto: detiene la ejecución si la IA falla (evita contenido no oficial)',
        '  --no-subtitles          Desactiva subtítulos',
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
    } else if (cmd.includes('--motion-templates') || cmd.includes('--list-templates')) {
      newLogs.push(
        '🗄️  CATÁLOGO DE PLANTILLAS DE ANIMACIÓN (RAG DE COMPONENTES):',
        '   Base de datos ligera SQLite con clasificación semántica y prompt quirúrgico.',
        '--------------------------------------------------------------',
        '  • ID: plantilla_arbol_jerarquico [Curada de Fábrica]',
        '    Nombre: Estructura Jerárquica y Organización en Árbol (Layout: hierarchy_tree)',
        '    Tags: estructura, organizacion, carpetas, jerarquia, proyectos, recursos...',
        '  • ID: plantilla_escalado_elastico [Curada de Fábrica]',
        '    Nombre: Escalado Elástico Serverless de Cero a Infinito (Layout: scaling_elastic)',
        '    Tags: cloud run, serverless, escalado, contenedores, instancias, cold start...',
        '  • ID: plantilla_flujo_red_paquetes [Curada de Fábrica]',
        '    Nombre: Flujo de Red y Mensajería con Tráfico de Paquetes (Layout: network_flow)',
        '    Tags: redes, vpc, paquetes, latencia, pubsub, mensajeria, cola...',
        '  • ID: plantilla_ciclo_vida_almacenamiento [Curada de Fábrica]',
        '    Nombre: Ciclo de Vida de Objetos y Cifrado en Cloud Storage (Layout: storage_lifecycle)',
        '    Tags: storage, buckets, almacenamiento, ciclo de vida, coldline, archive...',
        '  • ID: plantilla_menor_privilegio_iam [Curada de Fábrica]',
        '    Nombre: Seguridad IAM: Principio de Menor Privilegio (Layout: iam_security)',
        '    Tags: iam, permisos, roles, politicas, service accounts, least privilege...',
        'Total registradas: 5 plantillas principales + indexación orgánica activa.'
      );
    } else if (cmd.includes('--visual-resources') || cmd.includes('--list-resources')) {
      newLogs.push(
        '🎨  CATÁLOGO DE RECURSOS VISUALES REGISTRADOS (ROUTER SEMÁNTICO):',
        '   Evita la saturación del prompt clasificando localmente (<1ms) cada escena.',
        '--------------------------------------------------------------',
        '  • ID: slide_concept_card [Tipo: SLIDE] (Prioridad: 1)',
        '    Nombre: Diapositiva: Tarjeta Conceptual Clave',
        '  • ID: slide_comparison_table [Tipo: SLIDE] (Prioridad: 3)',
        '    Nombre: Diapositiva: Matriz Comparativa de Servicios',
        '  • ID: slide_checklist [Tipo: SLIDE] (Prioridad: 2)',
        '    Nombre: Diapositiva: Checklist de Buenas Prácticas',
        '  • ID: motion_hierarchy_tree [Tipo: MOTION] (Prioridad: 4)',
        '    Nombre: Animación RAG: Árbol Jerárquico de Recursos',
        '  • ID: motion_elastic_scale [Tipo: MOTION] (Prioridad: 4)',
        '    Nombre: Animación RAG: Escalado Serverless Elástico',
        '  • ID: motion_packet_flow [Tipo: MOTION] (Prioridad: 4)',
        '    Nombre: Animación RAG: Flujo de Paquetes en Red',
        '  • ID: motion_storage_lifecycle [Tipo: MOTION] (Prioridad: 4)',
        '    Nombre: Animación RAG: Ciclo de Vida y Transición de Datos',
        '  • ID: console_walkthrough [Tipo: CONSOLE] (Prioridad: 3)',
        '    Nombre: Consola Real de GCP: Simulación de Interfaz y Clics',
        '  • ID: terminal_cli [Tipo: TERMINAL] (Prioridad: 3)',
        '    Nombre: Terminal en Vivo: Comandos gcloud CLI',
        `Total recursos registrados: ${visualResources.length} (+ personalizables en UI).`
      );
    } else if (cmd.includes('--motion')) {
      const topicMatch = cmd.match(/--motion\s+["']?([^"']+)["']?/);
      const parsedTopic = topicMatch ? topicMatch[1] : 'Concepto GCP';
      const hasGroq = Boolean(cmd.includes('--groq-key') || groqApiKey);

      newLogs.push(
        `🧠 [AI Motion Generator • RAG] Analizando concepto: '${parsedTopic}'...`,
        '   🔍 [Clasificador Semántico] Coincidencia: >95% detectada en SQLite local',
        '   🎯 [Prompt Quirúrgico] Inyección mínima de ~300 bytes...'
      );

      if (hasGroq) {
        newLogs.push(
          '   ⚠️ Gemini API saturado (HTTP Error 429: Too Many Requests / Quota).',
          '   ⚡ Conmutando automáticamente a Groq LPU (llama-3.3-70b-versatile)...',
          `   ⚡ Groq LPU pobló con éxito la plantilla para '${parsedTopic}' en 0.8s (sin límites).`,
          '   🎬 [Renderizado Vectorial] Compilando keyframes SVG a 10 FPS...',
          '   ✅ Video animado Full HD generado con precisión: ~55 KB (Ultra ligero y contextual)'
        );
      } else {
        newLogs.push(
          '   ⚠️ Gemini API saturado (HTTP Error 429: Too Many Requests / Quota).',
          '   💡 Groq LPU no está configurado (falta GROQ_API_KEY o --groq-key) para conmutar sin esperas.',
          '======================================================================',
          '❌ [GENERACIÓN DETENIDA - ERROR EN LLAMADA A IA]',
          `No se pudo generar la animación para '${parsedTopic}' porque Gemini API devolvió 429 y Groq no está configurado.`,
          '🛑 Operación cancelada para evitar mostrar diagramas o animaciones inexactas que no corresponden al tema.',
          '💡 Solución: Haz clic en el botón "LLM & Cuota" en la barra superior o añade --groq-key <CLAVE> para continuar con Groq.',
          '======================================================================'
        );
      }
    } else if (cmd.includes('--topic') && !cmd.includes('--list-topics')) {
      const topicMatch = cmd.match(/--topic\s+["']?([^"']+)["']?/);
      const parsedTopic = topicMatch ? topicMatch[1] : 'Tema';
      const hasGroq = Boolean(cmd.includes('--groq-key') || groqApiKey);

      newLogs.push(
        `🧠 [NotebookLM Generator] Diseñando lección para: '${parsedTopic}'...`,
        '  🤖 [Gemini LLM] Generando guion técnico y diapositivas...'
      );

      if (hasGroq) {
        newLogs.push(
          '  ⚠️ Gemini API saturado (HTTP Error 429: Too Many Requests / Quota).',
          '  ⚡ Conmutando automáticamente a Groq LPU (llama-3.3-70b-versatile)...',
          `  ✨ Lección Estructurada con Éxito con Groq: ${parsedTopic}`,
          '  🎙️ Voces en Español Latinoamericano Neutro (Alex: es-US / Sam: es-MX)...',
          '  🎬 Codificando video ultraligero a 15 FPS...',
          '✅ ¡Tutorial completado! Video optimizado guardado en output/gcp_tutorials/'
        );
      } else {
        newLogs.push(
          '  ⚠️ Gemini API saturado (HTTP Error 429: Too Many Requests / Quota).',
          '  💡 Groq LPU no está configurado (falta GROQ_API_KEY o --groq-key) para conmutar sin esperas.',
          '======================================================================',
          '❌ [GENERACIÓN DETENIDA - ERROR EN LLAMADA A IA]',
          `No se pudo generar la lección para '${parsedTopic}' porque Gemini API devolvió error 429 y Groq no está configurado.`,
          '🛑 Operación cancelada para evitar mostrar diapositivas inexactas o datos inventados.',
          '💡 Solución inmediata: Obtén tu API Key de Groq gratuita en https://console.groq.com/keys y pásala con --groq-key o en la UI.',
          '======================================================================'
        );
      }
    } else if (cmd.includes('--hybrid')) {
      newLogs.push(
        '🎬 [Orquestador de Recursos Visuales • Router Semántico]',
        '   • Línea de tiempo multi-recurso activa (<1ms de decisión local)',
        '   • Escena 01: [DIAPOSITIVA] Tarjeta conceptual y reglas de oro',
        '   • Escena 02: [ANIMACIÓN RAG] Clip vectorial en tiempo real (Escalado/Flujo)',
        '   • Escena 03: [CONSOLA GCP] Simulación interactiva de UI con clics',
        '   • Escena 04: [DIAPOSITIVA] Matriz comparativa con resaltado dinámico',
        '   • Concatena micro-clips MP4 con audio neural es-MX-JorgeNeural (+8%)',
        '   • Banda sonora ambiental mezclada con auto-ducking (volume=0.04)',
        '✅ ¡Tutorial HÍBRIDO completado exitosamente! Video optimizado en 1080p.'
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
        '   🎙️ Voces en Español Latinoamericano Neutro (Alex: es-US / Sam: es-MX)...',
        '   ⚡ Ritmo ágil a 1.20x sin pausas muertas (duración reducida ~25%)...',
        '   🖼️ Ensamblando diapositivas vectoriales con resaltado dinámico...',
        '   🎬 Codificando video ultraligero a 15 FPS (CRF 26, peso reducido ~90%)...',
        '   🎶 Mezclando audio AAC a 96 kbps con auto-ducking...',
        '✅ ¡Tutorial completado! Video optimizado guardado en output/gcp_tutorials/ (1080p, 15fps)'
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
        <div className="flex items-center bg-slate-900/80 p-1 rounded-xl border border-slate-800 gap-1">
          <button
            onClick={() => setActiveTab('hybrid_studio')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'hybrid_studio'
                ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-indigo-300 hover:text-white'
            }`}
          >
            <Film className="w-3.5 h-3.5" />
            Línea de Tiempo Híbrida
            <span className="text-[9px] bg-indigo-950 text-indigo-300 border border-indigo-500/30 px-1.5 py-0.2 rounded font-bold uppercase">Multi-Recurso</span>
          </button>
          <button
            onClick={() => setActiveTab('gcp_studio')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'gcp_studio'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Diapositivas y Consola
          </button>
          <button
            onClick={() => setActiveTab('ai_motion')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'ai_motion'
                ? 'bg-gradient-to-r from-sky-500 to-emerald-500 text-white shadow-md shadow-sky-500/20'
                : 'text-sky-400 hover:text-white'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Animaciones IA en Vivo
            <span className="text-[9px] bg-sky-900/80 text-sky-200 px-1.5 py-0.2 rounded font-bold uppercase">Ligero</span>
          </button>
          <button
            onClick={() => setActiveTab('terminal')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'terminal'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            Consola CLI
          </button>
        </div>

        {/* LLM Provider & Quota failover button */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowApiKeysModal(true)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium border transition-all ${
              groqApiKey
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20'
                : 'bg-amber-500/10 border-amber-500/30 text-amber-400 hover:bg-amber-500/20'
            }`}
            title="Configuración de IA y Conmutación por Cuota 429"
          >
            <Zap className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">IA:</span>
            <span className="font-semibold">{llmProvider === 'auto' ? 'Auto (Gemini ↔ Groq)' : llmProvider.toUpperCase()}</span>
            <span
              className={`w-2 h-2 rounded-full ${
                groqApiKey ? 'bg-emerald-400 shadow-sm shadow-emerald-400 animate-pulse' : 'bg-amber-400'
              }`}
            />
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      {activeTab === 'hybrid_studio' ? (
        <HybridTimelineStudio
          currentLesson={currentLesson}
          selectedLessonKey={selectedLessonKey}
          allLessons={GCP_PRESET_LESSONS}
          onSelectLessonKey={(key) => {
            setSelectedLessonKey(key as keyof typeof GCP_PRESET_LESSONS);
            setActiveSlideIndex(0);
          }}
          visualResources={visualResources}
          sceneOverrides={sceneResourceOverrides}
          onSetSceneResource={handleSetSceneResource}
          activeSceneIndex={activeHybridSceneIndex}
          onSelectScene={(idx) => setActiveHybridSceneIndex(idx)}
          onRunCommand={(cmd) => {
            runTerminalCommand(cmd);
            setActiveTab('terminal');
          }}
          onPlayAudio={simulateAudioPlay}
          isPlayingAudio={isPlayingAudio}
          onOpenCatalog={() => setShowResourceCatalogModal(true)}
          onOpenNewResource={() => setShowNewResourceModal(true)}
        />
      ) : activeTab === 'gcp_studio' ? (
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
                    <div className="m-3 bg-emerald-950/30 border border-emerald-500/40 rounded-lg p-3 font-mono text-xs space-y-1">
                      <div className="flex items-center justify-between text-emerald-400 font-bold mb-1">
                        <span>✓ [CLOUD SHELL SIMULATOR] Ejecutado</span>
                        <span className="text-[10px] bg-emerald-500/20 px-2 py-0.5 rounded text-emerald-300">Exit Code: 0</span>
                      </div>
                      <p className="text-slate-300 text-[11px]">Creating revision & setting routing 100%... [OK]</p>
                      <p className="text-slate-300 text-[11px]">Setting IAM policy bindings (member: allUsers)... [OK]</p>
                      <p className="text-emerald-300 font-semibold text-[11px]">STATUS 200 OK: Servicio desplegado con éxito en europe-west1</p>
                    </div>
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
      ) : activeTab === 'ai_motion' ? (
        /* AI Motion Studio View with RAG Component Architecture */
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full flex flex-col gap-6">
          {/* Modal Catálogo RAG SQLite */}
          {showTemplateModal && (
            <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
              <div className="bg-[#0B1222] border border-slate-700/80 rounded-2xl max-w-3xl w-full p-6 shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">
                <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                  <div className="flex items-center gap-2.5">
                    <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                      <Database className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        Catálogo de Plantillas RAG (SQLite)
                        <span className="text-[10px] bg-sky-500/20 text-sky-300 border border-sky-500/30 px-2 py-0.5 rounded-full font-mono">
                          motion_templates.sqlite
                        </span>
                      </h3>
                      <p className="text-xs text-slate-400">
                        Base de datos de metadatos y schemas compactos. Zero desperdicio de contexto en prompts.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowTemplateModal(false)}
                    className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="flex-1 overflow-y-auto my-4 space-y-3 pr-1">
                  {[
                    {
                      id: 'plantilla_arbol_jerarquico',
                      name: 'Estructura Jerárquica y Organización en Árbol',
                      layout: 'hierarchy_tree',
                      tags: ['estructura', 'organizacion', 'carpetas', 'jerarquia', 'proyectos', 'gobierno'],
                      desc: 'Visualiza la jerarquía de gobierno en Google Cloud: Organización, Carpetas, Proyectos y Recursos con herencia de políticas.',
                      topicPreset: 'Estructura Organizacional en GCP'
                    },
                    {
                      id: 'plantilla_escalado_elastico',
                      name: 'Escalado Elástico Serverless de Cero a Infinito',
                      layout: 'scaling_elastic',
                      tags: ['cloud run', 'serverless', 'escalado', 'contenedores', 'instancias', 'cold start'],
                      desc: 'Elasticidad de contenedores serverless: reposo a coste 0, arranque en frío ultrarrápido y réplicas elásticas bajo demanda.',
                      topicPreset: 'Cloud Run Serverless Elastic'
                    },
                    {
                      id: 'plantilla_flujo_red_paquetes',
                      name: 'Flujo de Red y Mensajería con Tráfico de Paquetes',
                      layout: 'network_flow',
                      tags: ['redes', 'vpc', 'paquetes', 'latencia', 'pubsub', 'mensajeria', 'cola'],
                      desc: 'Simula el flujo secuencial de paquetes de datos y mensajes entre componentes conectados en tiempo real.',
                      topicPreset: 'Google Cloud Pub/Sub Fan-Out'
                    },
                    {
                      id: 'plantilla_ciclo_vida_almacenamiento',
                      name: 'Ciclo de Vida de Objetos y Cifrado en Cloud Storage',
                      layout: 'storage_lifecycle',
                      tags: ['storage', 'buckets', 'almacenamiento', 'ciclo de vida', 'coldline', 'aes-256'],
                      desc: 'Transición automática de archivos entre clases de almacenamiento con cifrado AES-256 bancario y ahorro del 80%.',
                      topicPreset: 'Cloud Storage Cifrado y Ciclo de Vida'
                    },
                    {
                      id: 'plantilla_menor_privilegio_iam',
                      name: 'Seguridad IAM: Principio de Menor Privilegio',
                      layout: 'iam_security',
                      tags: ['iam', 'permisos', 'roles', 'politicas', 'service accounts', 'least privilege'],
                      desc: 'Validación rigurosa de identidades de Service Accounts, verificación de roles granulares y auditoría en Cloud Logging.',
                      topicPreset: 'IAM Least Privilege & Roles'
                    }
                  ].map((tpl) => (
                    <div key={tpl.id} className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono font-bold text-sky-400">{tpl.id}</span>
                          <span className="text-[10px] bg-blue-900/40 text-blue-300 border border-blue-500/30 px-2 py-0.5 rounded font-mono">
                            {tpl.layout}
                          </span>
                        </div>
                        <button
                          onClick={() => {
                            setMotionTopic(tpl.topicPreset);
                            setMotionStage(0);
                            setShowTemplateModal(false);
                          }}
                          className="text-xs bg-sky-600/30 hover:bg-sky-600 text-sky-200 px-2.5 py-1 rounded-lg border border-sky-500/40 transition"
                        >
                          Probar Plantilla
                        </button>
                      </div>
                      <div className="text-sm font-semibold text-white mt-1">{tpl.name}</div>
                      <p className="text-xs text-slate-400 mt-1">{tpl.desc}</p>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {tpl.tags.map((t) => (
                          <span key={t} className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded font-mono">
                            #{t}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                  <span>💡 Los temas no catalogados se auto-indexan automáticamente en esta base de datos.</span>
                  <button
                    onClick={() => {
                      setShowTemplateModal(false);
                      runTerminalCommand('python gcp_tutorial.py --motion-templates');
                      setActiveTab('terminal');
                    }}
                    className="text-xs text-sky-400 hover:text-sky-300 underline font-mono"
                  >
                    Ver en CLI (--motion-templates)
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="bg-[#0D1424] border border-slate-800 rounded-2xl p-6 shadow-xl">
            {/* Header & Architecture Description */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-bold text-sky-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-sky-400" /> RAG de Componentes & Generador de Video Vectorial
                  </span>
                  <span className="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-full font-bold font-mono">
                    ~75 KB / MP4 1080p
                  </span>
                  <span className="text-[10px] bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2 py-0.5 rounded-full font-bold font-mono">
                    Búsqueda Vectorial &lt;2ms
                  </span>
                </div>
                <h2 className="text-xl font-bold text-white mt-1">Estudio de Animación Técnica al Vuelo con Gemini</h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  La búsqueda semántica selecciona la plantilla en SQLite y solo inyecta su schema (~300 bytes) a Gemini, eliminando la saturación de memoria.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowTemplateModal(true)}
                  className="text-xs bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 px-3.5 py-2 rounded-xl flex items-center gap-2 transition"
                >
                  <Database className="w-3.5 h-3.5 text-sky-400" />
                  Ver Catálogo SQLite (RAG)
                </button>
              </div>
            </div>

            {/* Quick Topic Chips & Custom Input */}
            <div className="flex flex-col gap-3 mb-6 p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs text-slate-400 font-medium mr-1">Temas Curados:</span>
                {[
                  { label: '🏛️ Estructura Organizacional', topic: 'Estructura Organizacional en GCP' },
                  { label: '🚀 Cloud Run Serverless', topic: 'Cloud Run Serverless Elastic' },
                  { label: '⚡ Pub/Sub Fan-Out', topic: 'Google Cloud Pub/Sub Fan-Out' },
                  { label: '📦 Cloud Storage Buckets', topic: 'Cloud Storage Cifrado y Ciclo de Vida' },
                  { label: '🛡️ IAM Menor Privilegio', topic: 'IAM Least Privilege & Roles' }
                ].map((item) => (
                  <button
                    key={item.topic}
                    onClick={() => {
                      setMotionTopic(item.topic);
                      setMotionStage(0);
                    }}
                    className={`text-xs px-3 py-1.5 rounded-lg border transition ${
                      motionTopic === item.topic
                        ? 'bg-blue-600/30 border-sky-400 text-sky-200 font-bold'
                        : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>

              {/* Custom Topic Input */}
              <div className="flex items-center gap-2 pt-2 border-t border-slate-800/60">
                <span className="text-xs text-slate-400">O escribe cualquier tema:</span>
                <input
                  type="text"
                  placeholder="ej. BigQuery particionamiento, Cloud Spanner réplicas, VPC Peering..."
                  value={customMotionTopic}
                  onChange={(e) => setCustomMotionTopic(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && customMotionTopic.trim()) {
                      setMotionTopic(customMotionTopic.trim());
                      setMotionStage(0);
                      setCustomMotionTopic('');
                    }
                  }}
                  className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
                />
                <button
                  onClick={() => {
                    if (customMotionTopic.trim()) {
                      setMotionTopic(customMotionTopic.trim());
                      setMotionStage(0);
                      setCustomMotionTopic('');
                    }
                  }}
                  className="text-xs bg-blue-600 hover:bg-blue-500 text-white px-3 py-1 rounded-lg font-semibold transition"
                >
                  Analizar con RAG
                </button>
              </div>
            </div>

            {/* RAG Classifier HUD (Active Match Telemetry) */}
            {(() => {
              const isTree = motionTopic.toLowerCase().includes('estructura') || motionTopic.toLowerCase().includes('organiz') || motionTopic.toLowerCase().includes('arbol') || motionTopic.toLowerCase().includes('jerarquia');
              const isElastic = motionTopic.toLowerCase().includes('cloud run') || motionTopic.toLowerCase().includes('serverless') || motionTopic.toLowerCase().includes('elastic');
              const isStorage = motionTopic.toLowerCase().includes('storage') || motionTopic.toLowerCase().includes('bucket') || motionTopic.toLowerCase().includes('almacen');
              const isIAM = motionTopic.toLowerCase().includes('iam') || motionTopic.toLowerCase().includes('seguridad') || motionTopic.toLowerCase().includes('privileg');
              
              const currentTplId = isTree
                ? 'plantilla_arbol_jerarquico'
                : isElastic
                ? 'plantilla_escalado_elastico'
                : isStorage
                ? 'plantilla_ciclo_vida_almacenamiento'
                : isIAM
                ? 'plantilla_menor_privilegio_iam'
                : 'plantilla_flujo_red_paquetes';

              const layoutType = isTree ? 'hierarchy_tree' : isElastic ? 'scaling_elastic' : 'network_flow';

              return (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 p-3 rounded-xl bg-slate-900/40 border border-slate-800">
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-400 font-bold uppercase">Plantilla RAG Detectada</span>
                    <span className="text-xs font-mono font-bold text-sky-300 mt-0.5 truncate">{currentTplId}</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-400 font-bold uppercase">Similitud Semántica</span>
                    <span className="text-xs font-mono font-bold text-emerald-400 mt-0.5">100.0% (Coincidencia exacta)</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-400 font-bold uppercase">Prompt Quirúrgico</span>
                    <span className="text-xs font-mono font-bold text-amber-300 mt-0.5">~320 bytes (0 saturación)</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-[10px] text-slate-400 font-bold uppercase">Motor de Render</span>
                    <span className="text-xs font-mono font-bold text-purple-300 mt-0.5">{layoutType}</span>
                  </div>
                </div>
              );
            })()}

            {/* Stage Selector Tabs */}
            {(() => {
              const isTree = motionTopic.toLowerCase().includes('estructura') || motionTopic.toLowerCase().includes('organiz') || motionTopic.toLowerCase().includes('arbol') || motionTopic.toLowerCase().includes('jerarquia');
              const isElastic = motionTopic.toLowerCase().includes('cloud run') || motionTopic.toLowerCase().includes('serverless') || motionTopic.toLowerCase().includes('elastic');

              const stageData = isTree
                ? [
                    { stage: 0, title: 'Fase 1: Organización (Raíz)', badge: 'GOBIERNO CENTRAL', metric: 'Políticas Globales' },
                    { stage: 1, title: 'Fase 2: Carpetas de Entorno', badge: 'HERENCIA', metric: 'Prod vs Sandbox' },
                    { stage: 2, title: 'Fase 3: Proyectos & Facturación', badge: 'AISLAMIENTO', metric: 'Frontera de Recursos' }
                  ]
                : isElastic
                ? [
                    { stage: 0, title: 'Fase 1: Reposo a Cero Costo', badge: 'ESCALADO A CERO', metric: '0€ sin tráfico' },
                    { stage: 1, title: 'Fase 2: Petición HTTP Entrante', badge: 'COLD START', metric: '~300 ms de inicio' },
                    { stage: 2, title: 'Fase 3: Escalado Elástico Paralelo', badge: 'ALTA DEMANDA', metric: '3 pods paralelos' }
                  ]
                : [
                    { stage: 0, title: 'Fase 1: Publicación de Eventos', badge: 'INGESTA', metric: '10k msgs / seg' },
                    { stage: 1, title: 'Fase 2: Buffer en Topic Global', badge: 'RETENCIÓN', metric: 'Multi-región 99.99%' },
                    { stage: 2, title: 'Fase 3: Distribución Fan-Out', badge: 'PARALELO', metric: 'Push/Pull elástico' }
                  ];

              return (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
                  {stageData.map((item) => (
                    <button
                      key={item.stage}
                      onClick={() => setMotionStage(item.stage)}
                      className={`p-3 rounded-xl border text-left transition ${
                        motionStage === item.stage
                          ? 'bg-sky-950/40 border-sky-400 text-white shadow-lg shadow-sky-500/10'
                          : 'bg-slate-900/60 border-slate-800/80 text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold text-sky-400">{item.badge}</span>
                        <span className="text-[10px] text-emerald-400 font-mono">{item.metric}</span>
                      </div>
                      <div className="text-sm font-semibold mt-1">{item.title}</div>
                    </button>
                  ))}
                </div>
              );
            })()}

            {/* Interactive Visual Animated Canvas Simulation (Adapts to Selected Layout) */}
            {(() => {
              const isTree = motionTopic.toLowerCase().includes('estructura') || motionTopic.toLowerCase().includes('organiz') || motionTopic.toLowerCase().includes('arbol') || motionTopic.toLowerCase().includes('jerarquia');
              const isElastic = motionTopic.toLowerCase().includes('cloud run') || motionTopic.toLowerCase().includes('serverless') || motionTopic.toLowerCase().includes('elastic');

              return (
                <div className="relative bg-[#070b14] border border-slate-800 rounded-xl p-8 min-h-[380px] flex flex-col justify-between overflow-hidden shadow-inner">
                  {/* Background Glow */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

                  {/* Canvas Header */}
                  <div className="flex items-center justify-between z-10">
                    <div>
                      <span className="text-[11px] font-bold uppercase tracking-wider text-sky-400">
                        ⚡ SIMULACIÓN VISUAL EN VIVO • {isTree ? 'ARQUITECTURA JERÁRQUICA' : isElastic ? 'ESCALADO SERVERLESS' : 'FLUJO DE PAQUETES'}
                      </span>
                      <h3 className="text-lg font-bold text-white">{motionTopic}</h3>
                    </div>
                    <div className="flex items-center gap-2 bg-slate-900/80 border border-slate-800 px-3 py-1 rounded-full text-xs text-slate-300">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                      1080p @ 10 FPS • ~75 KB
                    </div>
                  </div>

                  {/* Canvas Body (Hierarchy Tree or Elastic Pods or Network Flow) */}
                  {isTree ? (
                    /* HIERARCHY TREE LAYOUT */
                    <div className="flex flex-col items-center gap-4 my-6 z-10">
                      {/* Level 0: Organization */}
                      <div
                        className={`w-72 p-3 rounded-xl border text-center transition-all ${
                          motionStage === 0
                            ? 'bg-blue-900/60 border-amber-400 shadow-lg shadow-amber-500/20 scale-105'
                            : 'bg-slate-900/70 border-slate-800 opacity-70'
                        }`}
                      >
                        <span className="text-[9px] font-bold uppercase bg-amber-500/30 text-amber-300 px-2 py-0.5 rounded">
                          🏢 ORGANIZACIÓN RAÍZ
                        </span>
                        <div className="text-sm font-bold text-white mt-1">MiEmpresa.com</div>
                        <div className="text-[11px] text-slate-400">Políticas globales y cuenta de facturación</div>
                      </div>

                      {/* Branches down */}
                      <div className="w-96 flex items-center justify-between px-16 relative">
                        <div className="w-0.5 h-6 bg-slate-700 mx-auto" />
                      </div>

                      {/* Level 1: Folders */}
                      <div className="grid grid-cols-2 gap-8 w-full max-w-xl">
                        <div
                          className={`p-3 rounded-xl border text-center transition-all ${
                            motionStage === 1
                              ? 'bg-blue-950/70 border-sky-400 shadow-lg shadow-sky-500/20 scale-105'
                              : 'bg-slate-900/70 border-slate-800 opacity-70'
                          }`}
                        >
                          <span className="text-[9px] font-bold uppercase bg-sky-500/30 text-sky-300 px-2 py-0.5 rounded">
                            📁 CARPETA PRODUCCIÓN
                          </span>
                          <div className="text-sm font-bold text-white mt-1">Entorno Prod</div>
                          <div className="text-[11px] text-slate-400">Reglas restrictivas heredadas</div>
                        </div>

                        <div className="p-3 rounded-xl border text-center bg-slate-900/70 border-slate-800 opacity-70">
                          <span className="text-[9px] font-bold uppercase bg-sky-500/30 text-sky-300 px-2 py-0.5 rounded">
                            📁 CARPETA DESARROLLO
                          </span>
                          <div className="text-sm font-bold text-white mt-1">Entorno Sandbox</div>
                          <div className="text-[11px] text-slate-400">Permisos ágiles para pruebas</div>
                        </div>
                      </div>

                      {/* Level 2: Projects */}
                      <div className="grid grid-cols-3 gap-4 w-full max-w-2xl mt-1">
                        <div
                          className={`p-2.5 rounded-xl border text-center transition-all ${
                            motionStage === 2
                              ? 'bg-emerald-950/60 border-emerald-400 shadow-lg shadow-emerald-500/20 scale-105'
                              : 'bg-slate-900/60 border-slate-800 opacity-60'
                          }`}
                        >
                          <span className="text-[9px] font-bold uppercase bg-emerald-500/30 text-emerald-300 px-1.5 py-0.5 rounded">
                            📦 PROYECTO BACKEND
                          </span>
                          <div className="text-xs font-bold text-white mt-0.5">Core APIs & DB</div>
                        </div>
                        <div className="p-2.5 rounded-xl border text-center bg-slate-900/60 border-slate-800 opacity-60">
                          <span className="text-[9px] font-bold uppercase bg-emerald-500/30 text-emerald-300 px-1.5 py-0.5 rounded">
                            📦 PROYECTO FRONTEND
                          </span>
                          <div className="text-xs font-bold text-white mt-0.5">CDN & Hosting</div>
                        </div>
                        <div className="p-2.5 rounded-xl border text-center bg-slate-900/60 border-slate-800 opacity-60">
                          <span className="text-[9px] font-bold uppercase bg-emerald-500/30 text-emerald-300 px-1.5 py-0.5 rounded">
                            📦 PROYECTO QA
                          </span>
                          <div className="text-xs font-bold text-white mt-0.5">Recursos efímeros</div>
                        </div>
                      </div>
                    </div>
                  ) : isElastic ? (
                    /* SCALING ELASTIC LAYOUT */
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center my-6 z-10">
                      {[0, 1, 2].map((podIdx) => {
                        const isActive = motionStage === 2 ? true : motionStage === 1 ? podIdx === 0 : false;
                        return (
                          <div
                            key={podIdx}
                            className={`p-5 rounded-xl border transition-all ${
                              isActive
                                ? 'bg-blue-950/70 border-sky-400 shadow-lg shadow-sky-500/20 scale-105'
                                : 'bg-slate-900/60 border-slate-800 opacity-50'
                            }`}
                          >
                            <span className="text-[10px] font-bold uppercase bg-sky-500/30 text-sky-300 px-2 py-0.5 rounded">
                              CONTENEDOR #{podIdx + 1}
                            </span>
                            <div className="text-base font-bold text-white mt-2">
                              {isActive ? '🟢 ACTIVO (HTTP 200)' : '⚪ APAGADO (0€ Coste)'}
                            </div>
                            <div className="text-xs text-slate-400 mt-1">
                              {isActive ? '80 Concurrencia • 300ms' : 'En reposo evitando gastos'}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    /* NETWORK FLOW LAYOUT */
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center my-6 z-10">
                      <div
                        className={`p-4 rounded-xl border transition-all ${
                          motionStage === 0
                            ? 'bg-blue-950/60 border-sky-400 shadow-lg shadow-sky-500/20 scale-105'
                            : 'bg-slate-900/70 border-slate-800 opacity-60'
                        }`}
                      >
                        <div className="text-[10px] font-bold uppercase text-sky-400 mb-1">CLIENTE / ENTRADA</div>
                        <div className="text-base font-bold text-white">Productores / Tráfico</div>
                        <div className="text-xs text-slate-400 mt-1">Eventos IoT / Solicitudes REST</div>
                      </div>

                      <div
                        className={`p-4 rounded-xl border transition-all ${
                          motionStage === 1
                            ? 'bg-blue-950/60 border-sky-400 shadow-lg shadow-sky-500/20 scale-105'
                            : 'bg-slate-900/70 border-slate-800 opacity-60'
                        }`}
                      >
                        <div className="text-[10px] font-bold uppercase text-amber-400 mb-1">SERVICIO CENTRAL</div>
                        <div className="text-base font-bold text-white">Topic / Procesador</div>
                        <div className="text-xs text-slate-400 mt-1">Buffer persistente multi-región</div>
                      </div>

                      <div
                        className={`p-4 rounded-xl border transition-all ${
                          motionStage === 2
                            ? 'bg-blue-950/60 border-emerald-400 shadow-lg shadow-emerald-500/20 scale-105'
                            : 'bg-slate-900/70 border-slate-800 opacity-60'
                        }`}
                      >
                        <div className="text-[10px] font-bold uppercase text-emerald-400 mb-1">DESTINO / SUSCRIPCIÓN</div>
                        <div className="text-base font-bold text-white">Consumo Fan-Out</div>
                        <div className="text-xs text-slate-400 mt-1">Procesamiento paralelo sin colisiones</div>
                      </div>
                    </div>
                  )}

                  {/* HUD Bottom Bar */}
                  <div className="bg-slate-900/90 border border-slate-800/80 rounded-lg p-3 flex flex-col md:flex-row items-center justify-between gap-3 z-10">
                    <div className="text-xs text-slate-300">
                      <span className="text-sky-400 font-bold">Fase {motionStage + 1}: </span>
                      {isTree ? (
                        motionStage === 0
                          ? 'El nodo Organización centraliza la facturación y gobierna las políticas de cumplimiento para toda la compañía.'
                          : motionStage === 1
                          ? 'Las carpetas agrupan proyectos por entorno (Prod vs Sandbox) y heredan automáticamente las directivas de seguridad.'
                          : 'Cada proyecto actúa como barrera de aislamiento para APIs habilitadas, cuentas de facturación y cuotas de cómputo.'
                      ) : isElastic ? (
                        motionStage === 0
                          ? 'Sin peticiones activas, el servicio permanece apagado a cero para ahorrar el 100% del presupuesto de servidores.'
                          : motionStage === 1
                          ? 'Llega la primera solicitud y el motor de Google Cloud levanta el contenedor en milisegundos (Cold start ultra ágil).'
                          : 'Si entran miles de peticiones simultáneas, Cloud Run multiplica pods en paralelo sin configurar nada manual.'
                      ) : (
                        motionStage === 0
                          ? 'Los productores envían eventos al Topic sin conocer ni saturar la capacidad de los receptores.'
                          : motionStage === 1
                          ? 'El Topic retiene los mensajes de forma síncrona en múltiples zonas garantizando durabilidad extrema.'
                          : 'Múltiples suscriptores consumen el mismo mensaje de forma independiente a su propio ritmo sin colisiones.'
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setMotionStage((prev) => (prev + 1) % 3)}
                        className="text-xs bg-slate-800 hover:bg-slate-700 text-white px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition"
                      >
                        Avanzar Fase <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })()}

            {/* Render & CLI Execution Trigger */}
            <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800/80">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                  <Terminal className="w-5 h-5" />
                </div>
                <div>
                  <div className="text-xs text-slate-400">Comando CLI con RAG semántico:</div>
                  <code className="text-xs text-emerald-400 font-mono font-bold">
                    python gcp_tutorial.py --motion "{motionTopic}"
                  </code>
                </div>
              </div>

              <div className="flex items-center gap-3 w-full sm:w-auto">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(`python gcp_tutorial.py --motion "${motionTopic}"`);
                    setCopiedCmd(true);
                    setTimeout(() => setCopiedCmd(false), 2000);
                  }}
                  className="bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 px-4 py-2.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition"
                >
                  <Copy className="w-3.5 h-3.5" />
                  {copiedCmd ? '¡Copiado!' : 'Copiar Comando'}
                </button>
                <button
                  onClick={() => {
                    runTerminalCommand(`python gcp_tutorial.py --motion "${motionTopic}"`);
                    setActiveTab('terminal');
                  }}
                  className="bg-gradient-to-r from-blue-600 to-sky-500 hover:from-blue-500 hover:to-sky-400 text-white px-5 py-2.5 rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-sky-500/20 transition"
                >
                  <Play className="w-4 h-4 fill-current" />
                  Renderizar Video con IA Ahora
                </button>
              </div>
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
              'python gcp_tutorial.py --topic "cloud_run" --hybrid',
              'python gcp_tutorial.py --motion-templates',
              'python gcp_tutorial.py --list-topics',
              'python gcp_tutorial.py --slides-only --topic "cloud_run"',
              'python gcp_tutorial.py --help',
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

      {/* MODAL 1: Catálogo de Recursos Visuales Registrados */}
      {showResourceCatalogModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0B1222] border border-slate-700/80 rounded-2xl max-w-4xl w-full p-6 shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    Catálogo de Recursos Visuales (Router Semántico)
                    <span className="text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded-full font-mono">
                      {visualResources.length} Registrados
                    </span>
                  </h3>
                  <p className="text-xs text-slate-400">
                    Clasificación semántica local &lt;1ms. Evita la saturación del prompt al delegar el medio ideal por escena.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setShowResourceCatalogModal(false);
                    setShowNewResourceModal(true);
                  }}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-3 py-1.5 rounded-lg font-bold flex items-center gap-1.5 transition"
                >
                  <Plus className="w-3.5 h-3.5" />
                  + Nuevo Recurso
                </button>
                <button
                  onClick={() => setShowResourceCatalogModal(false)}
                  className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="overflow-y-auto my-4 space-y-3 pr-2">
              {visualResources.map((res) => (
                <div
                  key={res.id}
                  className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-start justify-between gap-3 hover:border-slate-700 transition"
                >
                  <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-950/80 px-2 py-0.5 rounded border border-indigo-800/50">
                        {res.id}
                      </span>
                      <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                        Tipo: {res.kind.toUpperCase()}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        Prioridad: {res.priority}/5
                      </span>
                    </div>
                    <h4 className="text-sm font-bold text-white">{res.name}</h4>
                    <p className="text-xs text-slate-300">{res.description}</p>
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <span className="text-[10px] text-slate-500 font-mono">Triggers:</span>
                      {res.intent_keywords.map((kw, i) => (
                        <span key={i} className="text-[10px] bg-slate-950 text-sky-300 border border-slate-850 px-1.5 py-0.2 rounded font-mono">
                          {kw}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
              <span>El catálogo se puede inspeccionar por CLI con: <code className="text-sky-300 font-mono">python gcp_tutorial.py --visual-resources</code></span>
              <button
                onClick={() => setShowResourceCatalogModal(false)}
                className="bg-slate-800 hover:bg-slate-700 text-white px-3 py-1.5 rounded-lg transition"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: Registrar Nuevo Recurso Visual */}
      {showNewResourceModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0B1222] border border-slate-700/80 rounded-2xl max-w-xl w-full p-6 shadow-2xl flex flex-col overflow-hidden">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                  <Plus className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">Registrar Nuevo Recurso Visual</h3>
                  <p className="text-xs text-slate-400">
                    Añade un medio visual al Router Semántico para que esté disponible en la línea de tiempo.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowNewResourceModal(false)}
                className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddNewResource} className="my-4 space-y-3.5 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">ID Único (Snake_case)</label>
                <input
                  type="text"
                  required
                  placeholder="ej. custom_diagrama_3d"
                  value={newResourceForm.id}
                  onChange={(e) => setNewResourceForm({ ...newResourceForm, id: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white font-mono focus:outline-none focus:border-indigo-400"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Tipo de Recurso</label>
                  <select
                    value={newResourceForm.kind}
                    onChange={(e) => setNewResourceForm({ ...newResourceForm, kind: e.target.value as any })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-indigo-400"
                  >
                    <option value="slide">Diapositiva (Slide)</option>
                    <option value="motion">Animación Vectorial (Motion)</option>
                    <option value="console">Consola Simulada (Console)</option>
                    <option value="terminal">Terminal CLI (Terminal)</option>
                    <option value="custom">Recurso Personalizado (Custom)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Prioridad (1-5)</label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={newResourceForm.priority}
                    onChange={(e) => setNewResourceForm({ ...newResourceForm, priority: Number(e.target.value) })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-indigo-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Nombre Descriptivo</label>
                <input
                  type="text"
                  required
                  placeholder="ej. Diagrama 3D de Topología de Red"
                  value={newResourceForm.name}
                  onChange={(e) => setNewResourceForm({ ...newResourceForm, name: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-indigo-400"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Descripción Didáctica</label>
                <textarea
                  rows={2}
                  placeholder="¿Para qué tipo de explicaciones técnicas es óptimo este recurso?"
                  value={newResourceForm.description}
                  onChange={(e) => setNewResourceForm({ ...newResourceForm, description: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-indigo-400"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Palabras Clave de Activación (Separadas por comas)</label>
                <input
                  type="text"
                  required
                  placeholder="ej. topologia, cluster, 3d, malla, latencia, nodos"
                  value={newResourceForm.keywords}
                  onChange={(e) => setNewResourceForm({ ...newResourceForm, keywords: e.target.value })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-indigo-400"
                />
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowNewResourceModal(false)}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-3.5 py-1.5 rounded-lg transition"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-4 py-1.5 rounded-lg transition shadow-md shadow-indigo-600/30"
                >
                  Guardar Recurso
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {/* Modal: Configuración de LLM & Conmutación por Error 429 */}
      {showApiKeysModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0B101D] border border-indigo-500/30 rounded-2xl max-w-xl w-full p-6 shadow-2xl relative">
            <button
              onClick={() => setShowApiKeysModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2.5 mb-4">
              <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Configuración de IA & Tolerancia a Cuota 429</h3>
                <p className="text-xs text-slate-400">Conmutación automática de Gemini a Groq LPU (Llama 3.3)</p>
              </div>
            </div>

            <div className="space-y-4 text-xs text-slate-300">
              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-200">¿Por qué ocurre el Error 429 en Gemini?</span>
                  <span className="text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded-full font-bold">
                    Cuota / Rate Limit
                  </span>
                </div>
                <p className="text-slate-400 leading-relaxed text-[11px]">
                  La capa gratuita de Gemini tiene un límite de peticiones por minuto. Cuando se agota, devuelve <code className="text-amber-300">HTTP 429 Too Many Requests</code>.
                </p>
                <div className="pt-2 border-t border-slate-800/80 flex items-start gap-2 text-slate-300 text-[11px]">
                  <span className="text-emerald-400 font-bold">🛡️ Política de Veracidad:</span>
                  <span>Si la IA falla, la ejecución se <strong>detiene de inmediato</strong> para evitar mostrar diagramas o diapositivas inventadas que no corresponden al tema.</span>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1.5">Proveedor Preferido</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: 'auto', label: 'Auto (Failover)', desc: 'Gemini → Groq si hay 429' },
                    { id: 'groq', label: 'Groq LPU', desc: 'Ultra rápido (Llama 3.3)' },
                    { id: 'gemini', label: 'Gemini Flash', desc: 'Google Multimodal' },
                  ].map((p) => (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => setLlmProvider(p.id as any)}
                      className={`p-2.5 rounded-xl border text-left transition-all ${
                        llmProvider === p.id
                          ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-sm'
                          : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white'
                      }`}
                    >
                      <div className="font-semibold text-xs text-slate-200">{p.label}</div>
                      <div className="text-[10px] text-slate-400">{p.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-slate-300 font-medium">API Key de Groq (LPU Llama 3.3)</label>
                  <a
                    href="https://console.groq.com/keys"
                    target="_blank"
                    rel="noreferrer"
                    className="text-[11px] text-sky-400 hover:underline flex items-center gap-1"
                  >
                    Obtener clave gratis en console.groq.com <ChevronRight className="w-3 h-3" />
                  </a>
                </div>
                <input
                  type="password"
                  placeholder="gsk_..."
                  value={groqApiKey}
                  onChange={(e) => {
                    setGroqApiKey(e.target.value);
                    localStorage.setItem('gcp_groq_key', e.target.value);
                  }}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white font-mono text-xs focus:outline-none focus:border-indigo-400 placeholder:text-slate-600"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  Se guarda localmente en tu navegador. Al ejecutar en terminal puedes pasar <code className="text-indigo-300">--groq-key &lt;CLAVE&gt;</code> o definir <code className="text-indigo-300">export GROQ_API_KEY=...</code>
                </p>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <span className={`text-[11px] font-semibold flex items-center gap-1.5 ${groqApiKey ? 'text-emerald-400' : 'text-amber-400'}`}>
                  <span className={`w-2 h-2 rounded-full ${groqApiKey ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                  {groqApiKey ? 'Groq LPU listo para conmutar sin esperas' : 'Groq no configurado (solo Gemini activo)'}
                </span>
                <button
                  onClick={() => setShowApiKeysModal(false)}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-4 py-2 rounded-xl text-xs transition shadow-md shadow-indigo-600/30"
                >
                  Guardar y Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
