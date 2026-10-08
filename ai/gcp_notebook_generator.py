"""
GCP NotebookLM Tutorial & Debate Generator.
Creates two-host conversational deep dives (NotebookLM style) with synchronized technical slides.

Hosts:
  - Alex (Cloud Solutions Architect): Deep GCP architectural knowledge, best practices, clear explanations.
  - Sam (Senior DevOps / Skeptical Engineer): Practical, questions costs, cold starts, security trade-offs, real-world issues.
"""

import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from pathlib import Path

from config import GEMINI_API_KEY, sanitize_env_value

# Curated high-impact GCP lessons covering the most essential topics
CURATED_GCP_LESSONS: Dict[str, Dict[str, Any]] = {
    "cloud_storage": {
        "title": "Google Cloud Storage: Ahorra el 80% y Domina tus Buckets en 3 Minutos",
        "topic": "Google Cloud Storage & Cost Optimization",
        "category": "Google Cloud • Storage & Cost Optimization",
        "summary": "Tutorial práctico en primera persona con la consola real de GCP, analogías cotidianas y optimización de costos.",
        "mode": "console_tutorial",
        "narrator": "Carlos (Ingeniero Cloud Mexicano)",
        "scenes": [
            {
                "scene_id": 1,
                "scene_type": "hook_bill_alert",
                "title": "¿Factura Gigantesca por Guardar Archivos?",
                "keyword": "ALERTA COSTO",
                "dialogue": "¿Te ha llegado una factura gigantesca por guardar archivos en la nube o no sabes dónde guardar tus fotos y respaldos sin arruinarte? Hoy te explico en 3 minutos cómo funcionan los buckets de Google Cloud y cómo pagar solo centavos en lugar de cientos de dólares."
            },
            {
                "scene_id": 2,
                "scene_type": "create_bucket_ui",
                "title": "Creando un Bucket en la Consola Real de GCP",
                "keyword": "CREAR BUCKET",
                "dialogue": "Entramos a la consola de Google Cloud, vamos a Cloud Storage y damos clic al botón azul Crear Bucket. El nombre debe ser único a nivel mundial. Y aquí viene el primer truco: elegimos región única, por ejemplo us-central1, lo que de entrada reduce la tarifa base."
            },
            {
                "scene_id": 3,
                "scene_type": "storage_analogies",
                "title": "Las 4 Clases de Almacenamiento con Metáforas Reales",
                "keyword": "METÁFORAS",
                "dialogue": "Para no pagar de más, piensa en esto con objetos de tu casa. Standard es el cajón de tu escritorio: lo usas todos los días para tu web o fotos activas. Nearline es el armario: lo abres una vez al mes para respaldos periódicos y ahorras el 50 por ciento. Coldline es la bodega o trastero: accedes una vez al año para archivos históricos y ahorras el 75 por ciento. Y Archive es una caja fuerte bajo tierra: solo para auditorías legales, a un costo prácticamente de cero."
            },
            {
                "scene_id": 4,
                "scene_type": "drag_and_drop_upload",
                "title": "Subiendo Archivos con Cifrado Bancario Automático",
                "keyword": "SUBIR ARCHIVOS",
                "dialogue": "Una vez creado tu bucket, subir archivos es tan fácil como arrastrar y soltar tu carpeta o archivo comprimido directamente en el navegador. Lo mejor es que Google Cloud cifra automáticamente toda tu información en reposo con el estándar bancario AES-256 sin que tengas que configurar llaves complejas."
            },
            {
                "scene_id": 5,
                "scene_type": "cli_zoom",
                "title": "Comando Rápido con gcloud storage CLI",
                "keyword": "GCLOUD CLI",
                "dialogue": "Y si prefieres la terminal, con una sola línea de gcloud storage buckets create con la opción default-storage-class igual a Coldline, automatizas tus respaldos en tus scripts de integración continua en menos de 2 segundos."
            },
            {
                "scene_id": 6,
                "scene_type": "golden_rules_summary",
                "title": "Las 3 Reglas de Oro para Ahorrar el 80%",
                "keyword": "AHORRA 80%",
                "dialogue": "En resumen: guarda en Standard solo lo que uses a diario, pasa tus respaldos a Coldline o Archive, y elige una sola región. Con estas tres reglas, tus archivos estarán seguros y tu factura será mínima. Si te sirvió, ponlo en práctica hoy mismo en tu consola de Google Cloud."
            }
        ]
    },
    "cloud_run": {
        "title": "Cloud Run: De Servidores a Serverless sin Perder el Control",
        "topic": "Cloud Run vs Compute Engine & Arquitectura Serverless",
        "category": "Google Cloud • Serverless Compute",
        "summary": "Cómo ejecutar contenedores en producción escalando de 0 a N instancias en milisegundos sin gestionar infraestructura ni pagar cuando no hay tráfico.",
        "slides": [
            {
                "slide_id": 1,
                "layout": "concept_card",
                "badge": "Serverless • Microservicios",
                "title": "¿Qué es realmente Cloud Run?",
                "subtitle": "Contenedores OCI totalmente gestionados con escalado a cero",
                "concept_title": "La revolución del cómputo Serverless",
                "bullet_points": [
                    "Empaqueta tu código en CUALQUIER lenguaje usando Docker / contenedor OCI estándar.",
                    "Escala automáticamente de 0 a cientos de instancias en segundos según el tráfico HTTP.",
                    "Pagas estrictamente por los milisegundos que dura la ejecución de cada petición.",
                    "Sin servidores que parchar, sin gestión de clusters Kubernetes."
                ],
                "callout_box": "💡 Regla de oro: Si tu backend atiende peticiones HTTP, eventos gRPC o webhooks, Cloud Run suele ser el 90% más barato que una máquina virtual 24/7."
            },
            {
                "slide_id": 2,
                "layout": "comparison_table",
                "badge": "Trade-Offs • Decisión Arquitectónica",
                "title": "Cloud Run vs Compute Engine (VMs)",
                "subtitle": "¿Cuándo elegir cada uno en producción?",
                "headers": ["Criterio", "Cloud Run (Serverless)", "Compute Engine (VMs)"],
                "rows": [
                    ["Escalado a cero", "✅ Sí (0€ sin tráfico)", "❌ No (pagas 24/7 encendido)"],
                    ["Mantenimiento SO", "✅ 100% Google Cloud", "⚠️ Tú gestionas parches y Linux"],
                    ["Tiempo de arranque", "⚡ Segundos / Cold start ~1s", "⏳ Minutos para iniciar la VM"],
                    ["Conexión a hardware", "❌ Contenedor efímero", "✅ GPUs dedicadas, discos locales raw"],
                    ["Caso de uso ideal", "APIs REST, Webhooks, Apps web", "Monolitos legacy, ERPs, kernels custom"]
                ]
            },
            {
                "slide_id": 3,
                "layout": "architecture_flow",
                "badge": "Arquitectura de Red • Producción",
                "title": "Flujo Seguro de una Petición",
                "subtitle": "De Internet a base de datos privada sin exponer IPs públicas",
                "steps": [
                    {"name": "Usuario", "type": "client", "desc": "Petición HTTPS :443"},
                    {"name": "Cloud Armor", "type": "security", "desc": "WAF & Mitigación DDoS"},
                    {"name": "Cloud Run", "type": "compute", "desc": "Contenedor auto-scale (0..N)"},
                    {"name": "VPC Connector", "type": "network", "desc": "Túnel privado Serverless"},
                    {"name": "Cloud SQL", "type": "database", "desc": "Postgres (Solo IP Privada)"}
                ]
            },
            {
                "slide_id": 4,
                "layout": "terminal_code",
                "badge": "Google Cloud CLI • Producción",
                "title": "Despliegue con un Solo Comando",
                "subtitle": "Flags clave para optimizar rendimiento y costes en `gcloud`",
                "window_title": "terminal - gcloud run deploy",
                "code_lines": [
                    "# Despliegue en producción con CPU boost activado",
                    "$ gcloud run deploy api-pedidos \\",
                    "    --image gcr.io/empresa-prod/api:v2.1 \\",
                    "    --region europe-west1 \\",
                    "    --min-instances 0 \\",
                    "    --max-instances 25 \\",
                    "    --cpu-boost \\",
                    "    --allow-unauthenticated"
                ],
                "explanation": "⚡ La flag '--cpu-boost' asigna CPU extra durante el inicio para reducir drásticamente el Cold Start a menos de 600ms."
            },
            {
                "slide_id": 5,
                "layout": "concept_card",
                "badge": "Conclusiones • Pro-Tips",
                "title": "El Veredicto del Arquitecto",
                "subtitle": "3 Consejos indispensables antes de ir a producción",
                "concept_title": "Checklist de Despliegue en GCP",
                "bullet_points": [
                    "Concurrencia: Ajusta 'concurrency' (por defecto 80 peticiones por instancia) según tu lenguaje.",
                    "Secretos: Nunca pongas contraseñas en variables de entorno; móntalas desde Secret Manager.",
                    "Bases de Datos: Usa Serverless VPC Access para que tu Cloud SQL no tenga IP pública."
                ],
                "callout_box": "🎯 Conclusión: Adopta Cloud Run como tu estándar predeterminado en GCP a menos que tengas requisitos de kernel o GPUs continuas."
            }
        ],
        "dialogue": [
            {
                "speaker": "Alex",
                "slide_id": 1,
                "text": "Bienvenidos a este deep dive de Google Cloud. Hoy vamos a desmontar uno de los servicios más potentes y versátiles de toda la plataforma: Cloud Run.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 1,
                "text": "Y la pregunta que todo desarrollador se hace al principio: ¿esto es simplemente otro Docker en la nube o de verdad cambia las reglas del juego para un equipo de ingeniería?",
                "expression": "questioning"
            },
            {
                "speaker": "Alex",
                "slide_id": 1,
                "text": "Cambia radicalmente las reglas porque te da lo mejor de dos mundos: la libertad total de empaquetar cualquier código en un contenedor Docker, pero con el modelo serverless donde escala a cero cuando nadie lo usa.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 2,
                "text": "Espera, pero compáralo con una máquina virtual tradicional de Compute Engine. ¿Cuándo tiene sentido pagar por una VM y cuándo deberíamos saltar directo a Cloud Run?",
                "expression": "questioning"
            },
            {
                "speaker": "Alex",
                "slide_id": 2,
                "text": "Fíjate en esta tabla comparativa. En Compute Engine pagas la máquina las veinticuatro horas aunque no tenga visitas a las tres de la madrugada, y además te toca parchear el sistema operativo. En Cloud Run, Google se encarga de todo el mantenimiento y si no hay tráfico, la factura es literalmente cero euros.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 3,
                "text": "Eso suena genial para el presupuesto, pero hablemos de arquitectura real. ¿Cómo protegemos la base de datos si nuestro contenedor vive en el entorno serverless de Google?",
                "expression": "questioning"
            },
            {
                "speaker": "Alex",
                "slide_id": 3,
                "text": "Exactamente con este flujo de red. Colocamos Cloud Armor en el perímetro para frenar ataques DDoS, y luego usamos un Serverless VPC Access Connector. Esto crea un túnel privado directo hacia tu Cloud SQL sin exponer jamás la base de datos a internet.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 4,
                "text": "Vale, ¿y qué tan complicado es llevarlo a producción desde nuestra terminal de desarrollo?",
                "expression": "questioning"
            },
            {
                "speaker": "Alex",
                "slide_id": 4,
                "text": "Es sorprendentemente directo. Con este comando de gcloud especificas la imagen, fijas el límite de instancias y activas cpu-boost para que el arranque en frío sea prácticamente instantáneo.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 5,
                "text": "Increíble. Así que como resumen: Docker estándar, cero servidores que mantener, base de datos en red privada y escalado automático transparente.",
                "expression": "insight"
            },
            {
                "speaker": "Alex",
                "slide_id": 5,
                "text": "Exacto. Si estás construyendo APIs o microservicios en Google Cloud, Cloud Run debe ser tu primera opción arquitectónica.",
                "expression": "explaining"
            }
        ]
    },
    "iam_security": {
        "title": "IAM en Google Cloud: El Principio de Menor Privilegio",
        "topic": "Gestión de Identidades, Service Accounts y Permisos Seguros",
        "category": "Google Cloud • Security & IAM",
        "summary": "Aprende cómo funciona el control de acceso en GCP, por qué nunca debes usar roles primitivos en producción y cómo aislar Service Accounts correctamente.",
        "slides": [
            {
                "slide_id": 1,
                "layout": "concept_card",
                "badge": "Seguridad • Principio Básico",
                "title": "¿Cómo Funciona Cloud IAM?",
                "subtitle": "¿Quién puede hacer qué sobre qué recurso?",
                "concept_title": "La Trinidad de IAM en Google Cloud",
                "bullet_points": [
                    "Miembro (¿Quién?): Usuario humano, grupo de Google o Service Account de aplicación.",
                    "Rol (¿Qué puede hacer?): Conjunto empaquetado de permisos específicos (ej. roles/storage.objectViewer).",
                    "Recurso (¿Sobre qué?): Un Bucket, una instancia Cloud Run, un proyecto o una base de datos.",
                    "Denegación por defecto: En GCP todo acceso está bloqueado hasta que una política lo permite."
                ],
                "callout_box": "🔒 Principio Fundamental: En IAM, cada permiso debe otorgar solo el mínimo acceso estrictamente necesario durante el menor tiempo posible."
            },
            {
                "slide_id": 2,
                "layout": "hierarchy_tree",
                "badge": "Herencia • Jerarquía de Recursos",
                "title": "Jerarquía de Recursos en GCP",
                "subtitle": "Cómo fluyen los permisos desde la raíz hasta el recurso",
                "nodes": [
                    "Organización (empresa.com)",
                    "Carpetas (Producción / Desarrollo)",
                    "Proyectos GCP (api-prod-9823)",
                    "Recursos (Cloud Run, Buckets, Cloud SQL)"
                ],
                "rule": "⚠️ Regla de Examen: Las políticas IAM se heredan SIEMPRE hacia abajo y NUNCA se pueden revocar en un nivel inferior. Si das Owner en la carpeta, es Owner en todos los proyectos de esa carpeta."
            },
            {
                "slide_id": 3,
                "layout": "comparison_table",
                "badge": "Tipos de Roles • Buenas Prácticas",
                "title": "Roles Primitivos vs Roles Predefinidos",
                "subtitle": "El peligro de asignar 'Editor' u 'Owner' en producción",
                "headers": ["Característica", "Roles Primitivos (Antiguos)", "Roles Predefinidos (Recomendados)"],
                "rows": [
                    ["Ejemplos", "Viewer, Editor, Owner", "roles/storage.objectViewer, roles/pubsub.publisher"],
                    ["Alcance de acceso", "Masivo sobre todo el proyecto", "Quirúrgico sobre un servicio concreto"],
                    ["Riesgo de seguridad", "🔴 Crítico (riesgo de borrado accidental)", "🟢 Mínimo (aislamiento por servicio)"],
                    ["Uso en producción", "❌ Prohibido en entornos serios", "✅ Estándar obligatorio de Google Cloud"]
                ]
            },
            {
                "slide_id": 4,
                "layout": "terminal_code",
                "badge": "CLI • Asignación Segura",
                "title": "Creación y Permisos de Service Account",
                "subtitle": "El flujo seguro con comandos `gcloud`",
                "window_title": "bash - gcloud iam service-accounts",
                "code_lines": [
                    "# 1. Crear Service Account dedicada para el microservicio",
                    "$ gcloud iam service-accounts create sa-pedidos-api \\",
                    "    --display-name=\"SA para API de Pedidos\"",
                    "",
                    "# 2. Asignar únicamente el rol granular requerido",
                    "$ gcloud projects add-iam-policy-binding mi-proyecto \\",
                    "    --member=\"serviceAccount:sa-pedidos-api@mi-proyecto.iam.gserviceaccount.com\" \\",
                    "    --role=\"roles/datastore.user\""
                ],
                "explanation": "🔑 Evita descargar archivos JSON de claves de Service Account; usa Workload Identity o adjunta la SA directamente al recurso de Cloud Run."
            },
            {
                "slide_id": 5,
                "layout": "concept_card",
                "badge": "Resumen • Auditoría",
                "title": "Checklist de Seguridad IAM",
                "subtitle": "3 Reglas de oro para no comprometer tu infraestructura",
                "concept_title": "Buenas Prácticas Oficiales",
                "bullet_points": [
                    "Una Service Account por servicio: Nunca reutilices la misma identidad para frontend, backend y cron jobs.",
                    "Elimina claves JSON descargadas: En su lugar, aprovecha el token metadata server de GCP.",
                    "Usa IAM Recommender: Deja que el machine learning de Google te avise de permisos sin usar para revocarlos automáticamente."
                ],
                "callout_box": "🎯 Veredicto: El mejor sistema de seguridad es aquel donde cada contenedor tiene únicamente los permisos indispensables para cumplir su tarea."
            }
        ],
        "dialogue": [
            {
                "speaker": "Alex",
                "slide_id": 1,
                "text": "Hoy nos adentramos en el corazón de la seguridad en Google Cloud: el sistema de Identity and Access Management, conocido como IAM.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 1,
                "text": "Y reconozcámoslo, Alex, al principio IAM intimida un poco con tantos roles y permisos. ¿Cuál es el modelo mental clave para entenderlo sin volverse loco?",
                "expression": "questioning"
            },
            {
                "speaker": "Alex",
                "slide_id": 1,
                "text": "La clave es responder siempre a tres preguntas: ¿Quién intenta acceder?, ¿Qué acción quiere realizar? y ¿Sobre qué recurso específico? En Google Cloud, todo está denegado por defecto hasta que creas una política explícita.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 2,
                "text": "Y ojo con la jerarquía de recursos. He visto a ingenieros dar permisos a nivel de carpeta creyendo que podían restringirlos en un proyecto específico.",
                "expression": "questioning"
            },
            {
                "speaker": "Alex",
                "slide_id": 2,
                "text": "¡Ese es un error clásico de examen y de producción! Las políticas de IAM fluyen estrictamente hacia abajo. Si alguien es Editor a nivel de carpeta, tiene ese poder en todos y cada uno de los proyectos que cuelguen de ella.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 3,
                "text": "Hablemos de los roles primitivos como Viewer, Editor y Owner. ¿Por qué Google insiste tanto en que no los usemos en entornos reales?",
                "expression": "questioning"
            },
            {
                "speaker": "Alex",
                "slide_id": 3,
                "text": "Porque son dinamita pura. Dar 'Editor' significa que si un atacante compromete esa credencial, puede eliminar bases de datos o crear máquinas virtuales masivas. Los roles predefinidos aíslan los permisos quirúrgicamente por servicio.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 4,
                "text": "Y en la práctica, para que una aplicación hable con una base de datos o Cloud Storage, usamos una Service Account dedicada, ¿verdad?",
                "expression": "questioning"
            },
            {
                "speaker": "Alex",
                "slide_id": 4,
                "text": "Exactamente. Creas la identidad de máquina con gcloud, le otorgas el rol justo y necesario, y lo mejor de todo: jamás descargas archivos de clave JSON a tu portátil.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 5,
                "text": "Una identidad por microservicio, permisos mínimos y auditoría continua. Así se duerme tranquilo en la nube.",
                "expression": "insight"
            },
            {
                "speaker": "Alex",
                "slide_id": 5,
                "text": "Así es, Sam. Menor privilegio no es solo una buena práctica; es la base de cualquier arquitectura resiliente en GCP.",
                "expression": "explaining"
            }
        ]
    },
    "vpc_networking": {
        "title": "VPC y Redes en GCP: Conexión Privada sin Exponer Datos",
        "topic": "Virtual Private Cloud, Subnets y Serverless VPC Access",
        "category": "Google Cloud • Networking",
        "summary": "Descubre la red global definida por software de Google Cloud, cómo conectar servicios serverless con bases de datos internas y el uso de Cloud NAT.",
        "slides": [
            {
                "slide_id": 1,
                "layout": "concept_card",
                "badge": "Redes Globales • VPC",
                "title": "¿Por qué la VPC de Google es Diferente?",
                "subtitle": "La red definida por software más avanzada del planeta",
                "concept_title": "La Red Global de Google Cloud",
                "bullet_points": [
                    "VPC Global: A diferencia de otros proveedores donde las VPCs son regionales, en GCP una VPC abarca todo el mundo por defecto.",
                    "Subredes Regionales: Creas subredes en us-central1, europe-west1 o asia-east1 dentro de la misma VPC.",
                    "Enrutamiento por Fibra de Google: El tráfico entre regiones viaja por la red troncal privada de Google, no por la internet pública.",
                    "Latencias ultrabajas y cifrado automático en tránsito."
                ],
                "callout_box": "🌐 Diferenciador Clave: Puedes conectar dos máquinas en continentes distintos usando sus IPs internas privadas sin configurar VPNs complejas."
            },
            {
                "slide_id": 2,
                "layout": "architecture_flow",
                "badge": "Arquitectura Privada • Cloud SQL",
                "title": "Acceso Seguro a Base de Datos",
                "subtitle": "Conexión Serverless VPC Connector a Cloud SQL",
                "steps": [
                    {"name": "Cloud Run", "type": "compute", "desc": "Contenedor Serverless"},
                    {"name": "Serverless VPC Connector", "type": "network", "desc": "Puente a la VPC (/28)"},
                    {"name": "Subred Privada", "type": "network", "desc": "Rango 10.0.1.0/24"},
                    {"name": "Private Service Connect", "type": "security", "desc": "IP Interna sin internet"},
                    {"name": "Cloud SQL", "type": "database", "desc": "Postgres (10.0.1.5)"}
                ]
            },
            {
                "slide_id": 3,
                "layout": "comparison_table",
                "badge": "Salida a Internet • Seguridad",
                "title": "IP Pública Directa vs Cloud NAT",
                "subtitle": "¿Cómo dar internet a servidores privados de forma segura?",
                "headers": ["Criterio", "IP Externa Pública", "Cloud NAT (Recomendado)"],
                "rows": [
                    ["Exposición al exterior", "🔴 Abierta a escaneos y ataques", "🟢 Oculta, solo tráfico de salida"],
                    ["Conexiones entrantes", "⚠️ Permitidas si el firewall falla", "🛡️ Imposibles por diseño"],
                    ["Actualizaciones de paquetes", "✅ Descarga directa", "✅ Descarga a través del gateway NAT"],
                    ["Coste de IPs públicas", "Pagas por cada IP estática", "Pagas por volumen y 1 sola IP de salida"]
                ]
            },
            {
                "slide_id": 4,
                "layout": "terminal_code",
                "badge": "CLI • Creación de Conector",
                "title": "Creando el Serverless VPC Connector",
                "subtitle": "El comando que une tus microservicios a la red privada",
                "window_title": "bash - gcloud compute networks vpc-access",
                "code_lines": [
                    "# Crear conector en la región de tu microservicio",
                    "$ gcloud compute networks vpc-access connectors create conector-prod \\",
                    "    --region europe-west1 \\",
                    "    --range 10.8.0.0/28 \\",
                    "    --network red-produccion \\",
                    "    --min-instances 2 \\",
                    "    --max-instances 10"
                ],
                "explanation": "📌 El rango de IPs debe ser un bloque /28 libre dentro de tu VPC que no colisione con subredes existentes."
            },
            {
                "slide_id": 5,
                "layout": "concept_card",
                "badge": "Resumen • Best Practices",
                "title": "Reglas de Oro en Redes GCP",
                "subtitle": "Asegura el perímetro de tu arquitectura",
                "concept_title": "Checklist de Networking",
                "bullet_points": [
                    "Modo de VPC Personalizado (Custom Mode): Nunca uses la red 'default' en proyectos de producción.",
                    "Reglas de Firewall con Tags: Aplica políticas de firewall usando Service Accounts o etiquetas de red, nunca por IP suelta.",
                    "Cloud NAT para servidores: Mantén tus instancias en subredes privadas sin IP pública y usa NAT para salir a internet."
                ],
                "callout_box": "🎯 Conclusión: Una red bien diseñada en GCP te permite mover datos globalmente con la máxima velocidad y el mínimo riesgo de exposición."
            }
        ],
        "dialogue": [
            {
                "speaker": "Alex",
                "slide_id": 1,
                "text": "Hoy exploramos el sistema circulatorio de Google Cloud: las redes virtuales VPC y por qué la infraestructura global de Google es tan especial.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 1,
                "text": "Eso de que las VPCs de Google sean 'globales' siempre me ha volado la cabeza. En otras nubes tienes que pelearte con VPC Peering interregional desde el minuto uno.",
                "expression": "questioning"
            },
            {
                "speaker": "Alex",
                "slide_id": 1,
                "text": "Así es, Sam. En Google Cloud, tu red virtual abarca todos los centros de datos del planeta de forma nativa. Dos máquinas en distintas regiones se comunican por IPs privadas a través de los cables submarinos de Google con cifrado automático.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 2,
                "text": "Pero cuando mezclas serverless como Cloud Run con una VPC privada, surge el dilema: ¿cómo conectamos el contenedor a una base de datos que no tiene internet?",
                "expression": "questioning"
            },
            {
                "speaker": "Alex",
                "slide_id": 2,
                "text": "Con el Serverless VPC Access Connector. Actúa como un túnel de alto rendimiento que inyecta el tráfico de Cloud Run directamente en tu subred privada, de modo que Cloud SQL nunca necesita abrir una IP pública al mundo.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 3,
                "text": "¿Y si mis servidores en esa red privada necesitan descargar dependencias o llamar a una API externa sin exponerse a internet?",
                "expression": "questioning"
            },
            {
                "speaker": "Alex",
                "slide_id": 3,
                "text": "Ahí entra Cloud NAT. Permite tráfico de salida hacia internet para parches o APIs externas, pero bloquea categóricamente cualquier intento de conexión entrante desde el exterior.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 4,
                "text": "Y la configuración del conector VPC son apenas unas líneas de gcloud definiendo el rango de subred y la capacidad de escalado.",
                "expression": "questioning"
            },
            {
                "speaker": "Alex",
                "slide_id": 4,
                "text": "Exacto. Un bloque barra 28 libre y listo: tus contenedores serverless se convierten en ciudadanos de primera clase dentro de tu red privada corporativa.",
                "expression": "explaining"
            },
            {
                "speaker": "Sam",
                "slide_id": 5,
                "text": "Una red global limpia, componentes aislados en IPs privadas y salida controlada por Cloud NAT. Impecable.",
                "expression": "insight"
            },
            {
                "speaker": "Alex",
                "slide_id": 5,
                "text": "Esa es la elegancia de diseñar sobre la red de Google Cloud.",
                "expression": "explaining"
            }
        ]
    }
}


class GCPTutorialGenerator:
    """Generates structured NotebookLM deep dive lessons about Google Cloud Platform."""

    def __init__(self, gemini_key: Optional[str] = None):
        raw_key = gemini_key or GEMINI_API_KEY
        self.gemini_key = sanitize_env_value(raw_key)

    def list_curated_topics(self) -> List[Dict[str, str]]:
        """Returns list of curated GCP lessons ready for instant generation."""
        items = []
        for key, lesson in CURATED_GCP_LESSONS.items():
            items.append({
                "slug": key,
                "title": lesson["title"],
                "topic": lesson["topic"],
                "category": lesson["category"],
                "slides_count": str(len(lesson["slides"])),
                "dialogue_turns": str(len(lesson["dialogue"]))
            })
        return items

    def generate_lesson(
        self,
        topic: str,
        user_notes: Optional[str] = None,
        language: str = "es"
    ) -> Dict[str, Any]:
        """
        Generates or matches a full GCP tutorial lesson with slide specifications and 2-host debate dialogue.
        """
        clean_topic = topic.strip().lower()
        
        # 1. Match curated high-fidelity curriculum if matches keywords
        for key, lesson in CURATED_GCP_LESSONS.items():
            if key in clean_topic or clean_topic in key:
                print(f"  📚 [Curated Curriculum] Coincidencia exacta encontrada para '{key}': {lesson['title']}")
                return lesson
            if any(w in clean_topic for w in ["storage", "bucket", "almacenamiento", "archivo", "backup", "s3", "blob", "fotos"]):
                return CURATED_GCP_LESSONS["cloud_storage"]
            if "run" in clean_topic or "serverless" in clean_topic:
                return CURATED_GCP_LESSONS["cloud_run"]
            if "iam" in clean_topic or "permiso" in clean_topic or "seguridad" in clean_topic or "service account" in clean_topic:
                return CURATED_GCP_LESSONS["iam_security"]
            if "vpc" in clean_topic or "red" in clean_topic or "network" in clean_topic or "nat" in clean_topic:
                return CURATED_GCP_LESSONS["vpc_networking"]

        # 2. If Gemini API key is valid, try dynamic LLM generation
        if self._is_valid_key(self.gemini_key):
            try:
                print(f"  🤖 [Gemini LLM] Generando guion técnico y diapositivas personalizadas para: '{topic}'...")
                dynamic_lesson = self._call_gemini_for_lesson(topic, user_notes, language)
                if dynamic_lesson and "slides" in dynamic_lesson and "dialogue" in dynamic_lesson:
                    return dynamic_lesson
            except Exception as e:
                print(f"  ⚠️ Error en generación dinámica con Gemini ({e}), usando fallback inteligente.")

        # 3. Dynamic procedural fallback based on user's notes and topic
        return self._generate_procedural_lesson(topic, user_notes)

    def _is_valid_key(self, key: Optional[str]) -> bool:
        if not key or len(key) < 15:
            return False
        placeholders = ["your_key", "placeholder", "demo", "xxx"]
        return not any(p in key.lower() for p in placeholders)

    def _call_gemini_for_lesson(self, topic: str, user_notes: Optional[str], language: str) -> Optional[Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        
        system_instructions = (
            "Eres un Arquitecto Principal de Google Cloud y un productor de podcasts educativos técnicos estilo NotebookLM. "
            "Debes crear una lección técnica en formato de debate conversacional entre dos presentadores: "
            "Alex (Cloud Solutions Architect, voz explicativa y pedagógica) y Sam (Senior DevOps, voz pragmática que hace preguntas de costes y trade-offs). "
            "Debes devolver ÚNICAMENTE un objeto JSON válido con la estructura solicitada, sin markdown alrededor."
        )

        prompt = f"""
Crea un video tutorial interactivo de Google Cloud Platform (GCP) en formato NotebookLM Deep Dive.
Tema: {topic}
Notas adicionales del estudiante: {user_notes or 'Ninguna específica. Enfócate en conceptos clave, arquitectura y buenas prácticas oficiales de GCP.'}

Requisitos del JSON de salida:
{{
  "title": "Título conciso y atractivo",
  "topic": "{topic}",
  "category": "Google Cloud • [Categoría]",
  "summary": "Resumen en una frase del valor técnico.",
  "slides": [
    {{
      "slide_id": 1,
      "layout": "concept_card",
      "badge": "Concepto Clave",
      "title": "Título de la diapositiva",
      "subtitle": "Subtítulo descriptivo",
      "concept_title": "Idea principal",
      "bullet_points": ["Punto clave 1", "Punto clave 2", "Punto clave 3"],
      "callout_box": "💡 Pro-Tip oficial de GCP"
    }},
    {{
      "slide_id": 2,
      "layout": "comparison_table",
      "badge": "Trade-offs",
      "title": "Comparativa de Soluciones",
      "subtitle": "Cuándo usar cuál",
      "headers": ["Criterio", "Opción A", "Opción B"],
      "rows": [["Coste", "X", "Y"], ["Escalado", "X", "Y"], ["Mantenimiento", "X", "Y"]]
    }},
    {{
      "slide_id": 3,
      "layout": "architecture_flow",
      "badge": "Arquitectura de Red",
      "title": "Diagrama de Flujo del Servicio",
      "subtitle": "Cómo viajan los datos",
      "steps": [
        {{"name": "Cliente", "type": "client", "desc": "HTTPS"}},
        {{"name": "Servicio GCP", "type": "compute", "desc": "Procesamiento"}},
        {{"name": "Base de Datos", "type": "database", "desc": "Almacenamiento privado"}}
      ]
    }},
    {{
      "slide_id": 4,
      "layout": "terminal_code",
      "badge": "Google Cloud CLI",
      "title": "Comandos gcloud Esenciales",
      "subtitle": "Sintaxis para desplegar",
      "window_title": "bash - gcloud deploy",
      "code_lines": ["$ gcloud [comando] --flag1 ..."],
      "explanation": "Explicación breve de las flags."
    }},
    {{
      "slide_id": 5,
      "layout": "concept_card",
      "badge": "Conclusiones",
      "title": "Checklist de Producción",
      "subtitle": "Buenas prácticas recomendadas",
      "concept_title": "Resumen Arquitectónico",
      "bullet_points": ["Regla 1", "Regla 2", "Regla 3"],
      "callout_box": "🎯 Veredicto final del arquitecto"
    }}
  ],
  "dialogue": [
    {{"speaker": "Alex", "slide_id": 1, "text": "Introducción amigable...", "expression": "explaining"}},
    {{"speaker": "Sam", "slide_id": 1, "text": "Pregunta incisiva sobre la dificultad o coste...", "expression": "questioning"}},
    {{"speaker": "Alex", "slide_id": 2, "text": "Explicación comparativa...", "expression": "explaining"}},
    {{"speaker": "Sam", "slide_id": 3, "text": "Duda sobre la arquitectura...", "expression": "questioning"}},
    {{"speaker": "Alex", "slide_id": 3, "text": "Resolución del flujo...", "expression": "explaining"}},
    {{"speaker": "Sam", "slide_id": 4, "text": "Pregunta sobre el despliegue...", "expression": "questioning"}},
    {{"speaker": "Alex", "slide_id": 4, "text": "Detalle del comando gcloud...", "expression": "explaining"}},
    {{"speaker": "Sam", "slide_id": 5, "text": "Conclusión y síntesis...", "expression": "insight"}},
    {{"speaker": "Alex", "slide_id": 5, "text": "Cierre final profesional...", "expression": "explaining"}}
  ]
}}
"""

        payload = {
            "contents": [{"parts": [{"text": f"{system_instructions}\n\n{prompt}"}]}],
            "generationConfig": {
                "temperature": 0.4,
                "responseMimeType": "application/json"
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidate_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(candidate_text)

    def _generate_procedural_lesson(self, topic: str, user_notes: Optional[str]) -> Dict[str, Any]:
        """Constructs a custom technical lesson based on input parameters without hallucinating."""
        clean_title = topic.strip().capitalize()
        notes_snippet = (user_notes or "").strip()
        
        return {
            "title": f"{clean_title}: Conceptos Clave en Google Cloud",
            "topic": clean_title,
            "category": "Google Cloud • Estudio Técnico",
            "summary": f"Explicación técnica en profundidad sobre {clean_title} con arquitectura, casos de uso y buenas prácticas.",
            "slides": [
                {
                    "slide_id": 1,
                    "layout": "concept_card",
                    "badge": "Concepto Fundamental",
                    "title": f"¿Qué es {clean_title}?",
                    "subtitle": "Definición técnica y propósito en la nube de Google",
                    "concept_title": f"Fundamentos de {clean_title}",
                    "bullet_points": [
                        notes_snippet if notes_snippet else f"Componente clave para optimizar cargas de trabajo en Google Cloud Platform.",
                        "Diseñado para integrarse nativamente con el ecosistema de seguridad IAM y VPC.",
                        "Permite escalabilidad elástica y gestión simplificada de infraestructura."
                    ],
                    "callout_box": "💡 Buena Práctica: Comprender la separación de responsabilidades y el modelo de costes antes de implementarlo en producción."
                },
                {
                    "slide_id": 2,
                    "layout": "comparison_table",
                    "badge": "Matriz de Decisión",
                    "title": f"Ventajas de {clean_title}",
                    "subtitle": "Comparativa de arquitectura frente a soluciones tradicionales",
                    "headers": ["Criterio", f"Con {clean_title}", "Enfoque Tradicional"],
                    "rows": [
                        ["Automatización", "Alta integración en GCP", "Configuración manual"],
                        ["Seguridad", "Políticas IAM granulares", "Credenciales estáticas"],
                        ["Escalabilidad", "Gestión automática de picos", "Aprovisionamiento rígido"],
                        ["Monitorización", "Cloud Monitoring integrado", "Agentes de terceros"]
                    ]
                },
                {
                    "slide_id": 3,
                    "layout": "architecture_flow",
                    "badge": "Flujo de Datos",
                    "title": "Arquitectura y Conexiones",
                    "subtitle": "Integración del servicio con el resto de Google Cloud",
                    "steps": [
                        {"name": "Petición / Evento", "type": "client", "desc": "Tráfico o Pub/Sub"},
                        {"name": clean_title, "type": "compute", "desc": "Servicio Principal"},
                        {"name": "Seguridad IAM", "type": "security", "desc": "Validación de Roles"},
                        {"name": "Cloud Storage / DB", "type": "database", "desc": "Persistencia Segura"}
                    ]
                },
                {
                    "slide_id": 4,
                    "layout": "terminal_code",
                    "badge": "Google Cloud CLI",
                    "title": "Comandos de Gestión con `gcloud`",
                    "subtitle": "Operaciones básicas desde la consola de comandos",
                    "window_title": f"bash - gcloud {clean_title.lower().replace(' ', '-')}",
                    "code_lines": [
                        f"# Inspeccionar configuración y recursos activos",
                        f"$ gcloud config set project mi-proyecto-gcp",
                        f"$ gcloud services list --enabled | grep -i '{clean_title[:10]}'",
                        f"$ gcloud info"
                    ],
                    "explanation": "Utiliza siempre gcloud para automatizar tareas repetitivas o integrar en pipelines de CI/CD."
                },
                {
                    "slide_id": 5,
                    "layout": "concept_card",
                    "badge": "Conclusiones",
                    "title": "Resumen y Siguientes Pasos",
                    "subtitle": "Recomendaciones finales para tu examen o proyecto",
                    "concept_title": "Checklist de Arquitectura",
                    "bullet_points": [
                        "Valida las cuotas y límites del servicio en tu región seleccionada.",
                        "Aplica el principio de menor privilegio con Service Accounts dedicadas.",
                        "Configura alertas de presupuesto en Google Cloud Billing."
                    ],
                    "callout_box": "🎯 Veredicto: Dominar este componente es clave para diseñar sistemas resilientes y eficientes en GCP."
                }
            ],
            "dialogue": [
                {
                    "speaker": "Alex",
                    "slide_id": 1,
                    "text": f"Hola a todos. Hoy vamos a analizar a fondo {clean_title} en Google Cloud, un tema fundamental para entender cómo estructurar soluciones modernas.",
                    "expression": "explaining"
                },
                {
                    "speaker": "Sam",
                    "slide_id": 1,
                    "text": f"Y como siempre, Alex, la duda al empezar: ¿qué problema real viene a resolver {clean_title} en nuestro día a día como ingenieros?",
                    "expression": "questioning"
                },
                {
                    "speaker": "Alex",
                    "slide_id": 1,
                    "text": "Resuelve la complejidad de gestionar infraestructuras aisladas, permitiendo que nos concentremos en la lógica de negocio mientras Google se encarga del escalado y la disponibilidad.",
                    "expression": "explaining"
                },
                {
                    "speaker": "Sam",
                    "slide_id": 2,
                    "text": "En esta tabla comparativa se ve muy claro el contraste con las soluciones tradicionales, sobre todo en automatización y control de seguridad.",
                    "expression": "insight"
                },
                {
                    "speaker": "Alex",
                    "slide_id": 2,
                    "text": "Efectivamente. La integración nativa con IAM y la red troncal de Google marca una diferencia enorme tanto en coste operativo como en postura de seguridad.",
                    "expression": "explaining"
                },
                {
                    "speaker": "Sam",
                    "slide_id": 3,
                    "text": "¿Y cómo viajan los datos a través de los diferentes componentes de la arquitectura?",
                    "expression": "questioning"
                },
                {
                    "speaker": "Alex",
                    "slide_id": 3,
                    "text": "Sigue este flujo limpio: la petición entra, se valida la identidad con IAM, el servicio procesa la carga y finalmente persiste en almacenamiento privado sin exponerse a internet.",
                    "expression": "explaining"
                },
                {
                    "speaker": "Sam",
                    "slide_id": 4,
                    "text": "Y para los que amamos la terminal, con gcloud podemos consultar el estado o automatizar el despliegue en un pipeline de GitHub Actions o Cloud Build.",
                    "expression": "insight"
                },
                {
                    "speaker": "Alex",
                    "slide_id": 5,
                    "text": "Para cerrar: revisa siempre las alertas de presupuesto en Cloud Billing, audita permisos con regularidad y aprovecha las ventajas de la nube gestionada.",
                    "expression": "explaining"
                },
                {
                    "speaker": "Sam",
                    "slide_id": 5,
                    "text": "Excelente síntesis. Una base sólida para continuar explorando Google Cloud.",
                    "expression": "insight"
                }
            ]
        }
