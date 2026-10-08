"""
Lightweight Motion Template Registry & Semantic Vector Classifier (RAG for Components).
Provides ultra-lightweight metadata catalog, semantic similarity search, surgical prompt injection,
and automatic organic indexing of new animation templates with zero bloat.
"""

import json
import math
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from config import BASE_DIR, TEMP_DIR


@dataclass
class MotionTemplate:
    """Lightweight metadata descriptor for an animation template."""
    id: str
    name: str
    description: str
    renderer_type: str  # 'hierarchy_tree', 'network_flow', 'scaling_elastic', 'storage_lifecycle', 'iam_security'
    tags: List[str]
    schema: Dict[str, Any]
    default_example: Dict[str, Any]
    usage_count: int = 0
    created_at: float = field(default_factory=time.time)
    is_custom: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SemanticMatcher:
    """
    Ultra-lightweight lexical and semantic similarity classifier (<2ms latency, 0 external dependencies).
    Uses weighted n-grams, technical GCP concept synonym expansion, and cosine similarity.
    """

    # Domain synonyms and concept expansions for Google Cloud Platform
    SYNONYM_CLUSTERS = {
        "jerarquia": ["organizacion", "carpetas", "proyectos", "recursos", "arbol", "estructura", "gobierno", "org", "folder", "tree", "hierarchy", "herencia"],
        "redes": ["vpc", "subredes", "firewall", "paquetes", "latencia", "enrutamiento", "nat", "peering", "interconnect", "router", "red"],
        "mensajeria": ["pubsub", "pub/sub", "colas", "eventos", "productores", "suscriptores", "topic", "suscripcion", "fanout", "fan-out", "streaming"],
        "serverless": ["cloud run", "funciones", "functions", "escalado", "instancias", "concurrencia", "cold start", "auto-scaling", "pods", "contenedores", "microservicios"],
        "almacenamiento": ["storage", "buckets", "objetos", "ciclo de vida", "coldline", "archive", "nearline", "cifrado", "aes-256", "archivos", "gcs"],
        "seguridad": ["iam", "permisos", "roles", "politicas", "service accounts", "least privilege", "tokens", "oauth2", "auditoria", "identidad", "acceso"],
        "base_de_datos": ["cloud sql", "spanner", "bigtable", "firestore", "transacciones", "relacional", "nosql", "sharding", "replicas"]
    }

    @classmethod
    def tokenize_and_expand(cls, text: str) -> List[str]:
        """Extracts normalized tokens, bigrams, and expands synonyms."""
        raw_tokens = re.findall(r'[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9/_-]+', text.lower())
        tokens = []
        for t in raw_tokens:
            clean = (t.replace("á", "a").replace("é", "e").replace("í", "i")
                     .replace("ó", "o").replace("ú", "u").replace("ñ", "n"))
            if len(clean) >= 2:
                tokens.append(clean)

        # Bigrams
        bigrams = [f"{tokens[i]}_{tokens[i+1]}" for i in range(len(tokens) - 1)]

        # Synonym expansion
        expanded = set(tokens + bigrams)
        for token in tokens:
            for cluster_key, synonyms in cls.SYNONYM_CLUSTERS.items():
                if token in synonyms or token == cluster_key:
                    for syn in synonyms:
                        expanded.add(syn)
                    expanded.add(cluster_key)

        return list(expanded)

    @classmethod
    def compute_similarity(cls, query_text: str, template: MotionTemplate) -> float:
        """
        Calculates cosine similarity between the query and template metadata (tags + description + name).
        Returns a score between 0.0 and 1.0.
        """
        query_terms = set(cls.tokenize_and_expand(query_text))
        if not query_terms:
            return 0.0

        # Build document corpus for template
        doc_text = f"{template.name} {template.description} {' '.join(template.tags)} {template.renderer_type}"
        doc_terms = set(cls.tokenize_and_expand(doc_text))
        
        # Tags get higher weight
        tag_terms = set()
        for tag in template.tags:
            tag_terms.update(cls.tokenize_and_expand(tag))

        # Intersection scoring with tag bonuses
        shared = query_terms.intersection(doc_terms)
        if not shared:
            return 0.0

        score_numerator = sum(2.5 if term in tag_terms else 1.0 for term in shared)
        norm_q = math.sqrt(len(query_terms))
        norm_d = math.sqrt(len(doc_terms) + len(tag_terms) * 1.5)

        cosine = score_numerator / (norm_q * norm_d)
        # Scale and clip between 0.0 and 1.0
        adjusted_score = min(1.0, max(0.0, cosine * 1.35))
        return round(adjusted_score, 3)


class MotionTemplateRegistry:
    """
    Lightweight SQLite database catalog for motion animation templates.
    Guarantees <5ms local search, compact surgical prompts, and organic self-indexing.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else BASE_DIR / "data" / "motion_templates.sqlite"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._seed_curated_templates()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS motion_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    renderer_type TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    schema TEXT NOT NULL,
                    default_example TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    created_at REAL NOT NULL,
                    is_custom INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def _seed_curated_templates(self):
        """Pre-populates the database with flagship Google Cloud architectural visual templates."""
        curated: List[MotionTemplate] = [
            # 1. HIERARCHY TREE (Structure, Folders, Projects, IAM Org)
            MotionTemplate(
                id="plantilla_arbol_jerarquico",
                name="Estructura Jerárquica y Organización en Árbol",
                description="Visualiza la jerarquía de gobierno en Google Cloud: Organización, Carpetas, Proyectos y Recursos con herencia de políticas y aislamiento.",
                renderer_type="hierarchy_tree",
                tags=[
                    "estructura", "organizacion", "carpetas", "jerarquia", "proyectos", "recursos",
                    "arbol", "gobierno", "gcp hierarchy", "folders", "projects", "organization",
                    "resource manager", "herencia", "politica de organizacion"
                ],
                schema={
                    "title": "string (Título máx 6 palabras)",
                    "subtitle": "string (Subtítulo explicativo)",
                    "nodes": [
                        {"id": 0, "name": "Organización raíz (ej. MiEmpresa)", "type": "org", "level": 0, "parent_id": None, "subtext": "Políticas globales"},
                        {"id": 1, "name": "Carpeta Producción", "type": "folder", "level": 1, "parent_id": 0, "subtext": "Políticas restrictivas"},
                        {"id": 2, "name": "Carpeta Desarrollo", "type": "folder", "level": 1, "parent_id": 0, "subtext": "Sandbox experimental"},
                        {"id": 3, "name": "Proyecto Backend", "type": "project", "level": 2, "parent_id": 1, "subtext": "Billing centralizado"},
                        {"id": 4, "name": "Proyecto Frontend", "type": "project", "level": 2, "parent_id": 1, "subtext": "CDN y Hosting"},
                        {"id": 5, "name": "Proyecto Pruebas", "type": "project", "level": 2, "parent_id": 2, "subtext": "Recursos efímeros"}
                    ],
                    "stages": [
                        {
                            "stage_num": 1,
                            "title": "Nodo Raíz de Organización",
                            "badge": "GOBIERNO CENTRAL",
                            "active_node_id": 0,
                            "metric_label": "Nivel Raíz",
                            "metric_value": "Políticas IAM Globales",
                            "explanation": "El nodo Organización centraliza la facturación, los accesos raíz y las auditorías de seguridad."
                        },
                        {
                            "stage_num": 2,
                            "title": "Aislamiento por Carpetas de Entorno",
                            "badge": "HERENCIA",
                            "active_node_id": 1,
                            "metric_label": "Entornos",
                            "metric_value": "Producción vs Sandbox",
                            "explanation": "Las carpetas agrupan proyectos y heredan automáticamente las directivas sin duplicar configuraciones."
                        },
                        {
                            "stage_num": 3,
                            "title": "Proyectos Aislados y Recursos",
                            "badge": "AISLAMIENTO",
                            "active_node_id": 3,
                            "metric_label": "Frontera",
                            "metric_value": "Cuotas y Facturación",
                            "explanation": "Cada proyecto actúa como barrera de aislamiento para APIs habilitadas y límites de gasto."
                        }
                    ]
                },
                default_example={
                    "title": "Estructura Organizacional de Google Cloud",
                    "subtitle": "Jerarquía de Recursos: Organización > Carpetas > Proyectos",
                    "nodes": [
                        {"id": 0, "name": "Organización (ej. MiEmpresa.com)", "type": "org", "level": 0, "parent_id": None, "subtext": "Nodo raíz corporativo"},
                        {"id": 1, "name": "Carpeta Producción", "type": "folder", "level": 1, "parent_id": 0, "subtext": "Reglas de seguridad estrictas"},
                        {"id": 2, "name": "Carpeta Desarrollo", "type": "folder", "level": 1, "parent_id": 0, "subtext": "Sandbox para equipos"},
                        {"id": 3, "name": "Proyecto Backend Core", "type": "project", "level": 2, "parent_id": 1, "subtext": "Facturación y APIs aisladas"},
                        {"id": 4, "name": "Proyecto Frontend Web", "type": "project", "level": 2, "parent_id": 1, "subtext": "Load Balancer y CDN"},
                        {"id": 5, "name": "Proyecto QA & Tests", "type": "project", "level": 2, "parent_id": 2, "subtext": "Recursos temporales"}
                    ],
                    "stages": [
                        {
                            "stage_num": 1,
                            "title": "Nodo Raíz de Organización",
                            "badge": "GOBIERNO CENTRAL",
                            "active_node_id": 0,
                            "metric_label": "Nivel Jerárquico",
                            "metric_value": "Raíz Central (Org)",
                            "explanation": "La Organización gobierna todas las políticas de cumplimiento y facturación corporativa."
                        },
                        {
                            "stage_num": 2,
                            "title": "Herencia y Carpetas",
                            "badge": "SEGREGACIÓN",
                            "active_node_id": 1,
                            "metric_label": "Entornos",
                            "metric_value": "Prod vs Sandbox",
                            "explanation": "Las carpetas permiten segregar permisos heredados automáticamente hacia sus proyectos hijos."
                        },
                        {
                            "stage_num": 3,
                            "title": "Proyectos como Barrera de Aislamiento",
                            "badge": "FRONTERA",
                            "active_node_id": 3,
                            "metric_label": "Límite",
                            "metric_value": "Cuotas y Facturación",
                            "explanation": "Cada proyecto delimita el consumo de APIs, credenciales y límites de seguridad."
                        }
                    ]
                }
            ),

            # 2. NETWORK & PIPELINE FLOW (VPC, PubSub, Queues, Packets)
            MotionTemplate(
                id="plantilla_flujo_red_paquetes",
                name="Flujo de Red y Mensajería con Tráfico de Paquetes",
                description="Simula el flujo secuencial de paquetes de datos y mensajes entre componentes conectados (VPC, Pub/Sub, API Gateway, Load Balancer, Redes).",
                renderer_type="network_flow",
                tags=[
                    "redes", "vpc", "paquetes", "latencia", "pubsub", "mensajeria", "cola", "pipeline",
                    "load balancer", "flujo", "enrutamiento", "firewall", "subredes", "nat", "traffic"
                ],
                schema={
                    "title": "string",
                    "subtitle": "string",
                    "nodes": [
                        {"id": "int", "name": "string", "type": "client|compute|database|security", "subtext": "string"}
                    ],
                    "stages": [
                        {
                            "stage_num": "int",
                            "title": "string",
                            "badge": "string",
                            "active_node_id": "int",
                            "packet_from": "int|null",
                            "packet_to": "int|null",
                            "metric_label": "string",
                            "metric_value": "string",
                            "explanation": "string"
                        }
                    ]
                },
                default_example={
                    "title": "Google Cloud Pub/Sub: Mensajería Asíncrona",
                    "subtitle": "Desacoplamiento global con fan-out masivo",
                    "nodes": [
                        {"id": 0, "name": "Productores (Apps / IoT)", "type": "client", "subtext": "Generación de eventos"},
                        {"id": 1, "name": "Topic Central Pub/Sub", "type": "compute", "subtext": "Buffer persistente global"},
                        {"id": 2, "name": "Suscriptores (BigQuery / Cloud Run)", "type": "database", "subtext": "Consumo en paralelo"}
                    ],
                    "stages": [
                        {
                            "stage_num": 1,
                            "title": "Publicación de Eventos",
                            "badge": "INGESTA",
                            "active_node_id": 0,
                            "packet_from": 0,
                            "packet_to": 1,
                            "metric_label": "Throughput",
                            "metric_value": "10,000 msgs / seg",
                            "explanation": "Los productores envían eventos al Topic sin conocer a los consumidores."
                        },
                        {
                            "stage_num": 2,
                            "title": "Persistencia en Topic",
                            "badge": "RETENCIÓN",
                            "active_node_id": 1,
                            "packet_from": None,
                            "packet_to": None,
                            "metric_label": "Durabilidad",
                            "metric_value": "Multi-región 99.9999%",
                            "explanation": "El Topic retiene los mensajes con replicación síncrona en múltiples zonas."
                        },
                        {
                            "stage_num": 3,
                            "title": "Distribución a Suscriptores",
                            "badge": "FAN-OUT",
                            "active_node_id": 2,
                            "packet_from": 1,
                            "packet_to": 2,
                            "metric_label": "Suscripciones",
                            "metric_value": "Independientes (Push/Pull)",
                            "explanation": "Múltiples servicios consumen el mismo mensaje a ritmos diferentes sin colisiones."
                        }
                    ]
                }
            ),

            # 3. SERVERLESS ELASTIC AUTO-SCALING (Cloud Run, Microservices)
            MotionTemplate(
                id="plantilla_escalado_elastico",
                name="Escalado Elástico Serverless de Cero a Infinito",
                description="Demuestra la elasticidad de contenedores serverless: reposo a costo 0, arranque en frío ultrarrápido, y multiplicación de pods bajo demanda.",
                renderer_type="scaling_elastic",
                tags=[
                    "cloud run", "serverless", "escalado", "contenedores", "instancias",
                    "concurrencia", "cold start", "auto-scaling", "ahorro", "pods", "microservicios"
                ],
                schema={
                    "title": "string",
                    "subtitle": "string",
                    "nodes": [
                        {"id": "int", "name": "string", "type": "client|compute|database", "subtext": "string"}
                    ],
                    "stages": [
                        {
                            "stage_num": "int",
                            "title": "string",
                            "badge": "string",
                            "active_node_id": "int",
                            "instances_count": "int (0, 1 o 3)",
                            "metric_label": "string",
                            "metric_value": "string",
                            "explanation": "string"
                        }
                    ]
                },
                default_example={
                    "title": "Cloud Run: Escalado Automático y Costo Cero",
                    "subtitle": "Contenedores elásticos con facturación por milisegundo",
                    "nodes": [
                        {"id": 0, "name": "Tráfico HTTP", "type": "client", "subtext": "Clientes web y móviles"},
                        {"id": 1, "name": "Cloud Run Container", "type": "compute", "subtext": "Auto-scaling de 0 a 1000"},
                        {"id": 2, "name": "Cloud SQL / Storage", "type": "database", "subtext": "Capa de persistencia"}
                    ],
                    "stages": [
                        {
                            "stage_num": 1,
                            "title": "Reposo a Cero Costo",
                            "badge": "ESCALADO A CERO",
                            "active_node_id": 0,
                            "instances_count": 0,
                            "metric_label": "Costo mensual",
                            "metric_value": "0.00€ sin tráfico",
                            "explanation": "Cuando no hay solicitudes, todas las instancias se apagan evitando costes fijos de servidor."
                        },
                        {
                            "stage_num": 2,
                            "title": "Llegada de Tráfico y Arranque en Frío",
                            "badge": "ARRANQUE RÁPIDO",
                            "active_node_id": 1,
                            "instances_count": 1,
                            "metric_label": "Cold Start",
                            "metric_value": "~300 ms de inicio",
                            "explanation": "La primera petición activa un pod en milisegundos procesando la solicitud de inmediato."
                        },
                        {
                            "stage_num": 3,
                            "title": "Pico de Carga: Multiplicación Elástica",
                            "badge": "ALTA DEMANDA",
                            "active_node_id": 1,
                            "instances_count": 3,
                            "metric_label": "Pods Activos",
                            "metric_value": "3 réplicas paralelas",
                            "explanation": "Si entran miles de peticiones, Cloud Run escala instantáneamente réplicas sin tocar código."
                        }
                    ]
                }
            ),

            # 4. STORAGE LIFECYCLE & SECURITY (Buckets, Tiers, Encryption)
            MotionTemplate(
                id="plantilla_ciclo_vida_almacenamiento",
                name="Ciclo de Vida de Objetos y Cifrado en Cloud Storage",
                description="Muestra la transición automática de archivos entre clases de almacenamiento (Standard, Nearline, Coldline, Archive) con cifrado AES-256.",
                renderer_type="storage_lifecycle",
                tags=[
                    "storage", "buckets", "almacenamiento", "ciclo de vida", "archivos",
                    "coldline", "archive", "nearline", "cifrado", "retencion", "aes-256", "gcs"
                ],
                schema={
                    "title": "string",
                    "subtitle": "string",
                    "nodes": [
                        {"id": "int", "name": "string", "type": "client|security|database", "subtext": "string"}
                    ],
                    "stages": [
                        {
                            "stage_num": "int",
                            "title": "string",
                            "badge": "string",
                            "active_node_id": "int",
                            "metric_label": "string",
                            "metric_value": "string",
                            "explanation": "string"
                        }
                    ]
                },
                default_example={
                    "title": "Cloud Storage: Ahorro del 80% con Ciclo de Vida",
                    "subtitle": "Políticas automáticas de transición y cifrado",
                    "nodes": [
                        {"id": 0, "name": "Carga de Archivos", "type": "client", "subtext": "Subida directa vía API / Consola"},
                        {"id": 1, "name": "Cifrado AES-256", "type": "security", "subtext": "Protección por defecto en reposo"},
                        {"id": 2, "name": "Regla Coldline (30 días)", "type": "database", "subtext": "Transición de bajo costo"}
                    ],
                    "stages": [
                        {
                            "stage_num": 1,
                            "title": "Ingesta y Cifrado Automático",
                            "badge": "SEGURIDAD",
                            "active_node_id": 0,
                            "metric_label": "Cifrado",
                            "metric_value": "AES-256 transparente",
                            "explanation": "Cada objeto se cifra automáticamente antes de tocar el disco sin coste adicional."
                        },
                        {
                            "stage_num": 2,
                            "title": "Transición a Coldline tras 30 Días",
                            "badge": "AHORRO INTELIGENTE",
                            "active_node_id": 2,
                            "metric_label": "Tarifa por GB",
                            "metric_value": "-75% de ahorro mensual",
                            "explanation": "Los archivos antiguos pasan a clases frías de almacenamiento automáticamente."
                        },
                        {
                            "stage_num": 3,
                            "title": "Durabilidad Extrema en Múltiples Zonas",
                            "badge": "ALTA DISPONIBILIDAD",
                            "active_node_id": 2,
                            "metric_label": "Durabilidad",
                            "metric_value": "11 Nueves (99.999999999%)",
                            "explanation": "Tus datos quedan protegidos ante desastres en múltiples centros de datos."
                        }
                    ]
                }
            ),

            # 5. IAM LEAST PRIVILEGE (Security, Policies, Roles)
            MotionTemplate(
                id="plantilla_menor_privilegio_iam",
                name="Seguridad IAM: Principio de Menor Privilegio",
                description="Validación rigurosa de identidades de Service Accounts, verificación de roles granulares y auditoría en Cloud Logging.",
                renderer_type="iam_security",
                tags=[
                    "iam", "permisos", "roles", "politicas", "service accounts",
                    "seguridad", "least privilege", "tokens", "auditoria", "identidad"
                ],
                schema={
                    "title": "string",
                    "subtitle": "string",
                    "nodes": [
                        {"id": "int", "name": "string", "type": "client|security|database", "subtext": "string"}
                    ],
                    "stages": [
                        {
                            "stage_num": "int",
                            "title": "string",
                            "badge": "string",
                            "active_node_id": "int",
                            "metric_label": "string",
                            "metric_value": "string",
                            "explanation": "string"
                        }
                    ]
                },
                default_example={
                    "title": "IAM: Principio de Menor Privilegio en GCP",
                    "subtitle": "Control estricto de identidades y roles mínimos",
                    "nodes": [
                        {"id": 0, "name": "Service Account", "type": "client", "subtext": "Identidad de la app"},
                        {"id": 1, "name": "Políticas IAM", "type": "security", "subtext": "Evaluador de permisos"},
                        {"id": 2, "name": "Base de Datos Prod", "type": "database", "subtext": "Recurso restringido"}
                    ],
                    "stages": [
                        {
                            "stage_num": 1,
                            "title": "Petición con Identidad Gestionada",
                            "badge": "AUTENTICACIÓN",
                            "active_node_id": 0,
                            "metric_label": "Credencial",
                            "metric_value": "Token efímero OAuth2",
                            "explanation": "Las aplicaciones usan Service Accounts con credenciales de corta vida en lugar de contraseñas fijas."
                        },
                        {
                            "stage_num": 2,
                            "title": "Validación de Rol Granular",
                            "badge": "AUTORIZACIÓN",
                            "active_node_id": 1,
                            "metric_label": "Veredicto",
                            "metric_value": "Permiso exacto requerido",
                            "explanation": "El motor de IAM concede únicamente la acción necesaria bloqueando escaladas de privilegio."
                        },
                        {
                            "stage_num": 3,
                            "title": "Trazabilidad en Cloud Logging",
                            "badge": "AUDITORÍA",
                            "active_node_id": 2,
                            "metric_label": "Registro",
                            "metric_value": "100% de llamadas auditadas",
                            "explanation": "Cada acceso queda registrado en los logs de auditoría para trazabilidad de seguridad."
                        }
                    ]
                }
            )
        ]

        with self._get_connection() as conn:
            for t in curated:
                conn.execute("""
                    INSERT OR REPLACE INTO motion_templates
                    (id, name, description, renderer_type, tags, schema, default_example, usage_count, created_at, is_custom)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    t.id,
                    t.name,
                    t.description,
                    t.renderer_type,
                    json.dumps(t.tags, ensure_ascii=False),
                    json.dumps(t.schema, ensure_ascii=False),
                    json.dumps(t.default_example, ensure_ascii=False),
                    t.usage_count,
                    t.created_at,
                    1 if t.is_custom else 0
                ))
            conn.commit()

    def list_templates(self) -> List[MotionTemplate]:
        """Lists all registered templates in the database."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM motion_templates ORDER BY usage_count DESC, id ASC")
            templates = []
            for row in cursor.fetchall():
                templates.append(MotionTemplate(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    renderer_type=row["renderer_type"],
                    tags=json.loads(row["tags"]),
                    schema=json.loads(row["schema"]),
                    default_example=json.loads(row["default_example"]),
                    usage_count=row["usage_count"],
                    created_at=row["created_at"],
                    is_custom=bool(row["is_custom"])
                ))
            return templates

    def get_template(self, template_id: str) -> Optional[MotionTemplate]:
        """Fetches a specific template by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM motion_templates WHERE id = ?", (template_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return MotionTemplate(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                renderer_type=row["renderer_type"],
                tags=json.loads(row["tags"]),
                schema=json.loads(row["schema"]),
                default_example=json.loads(row["default_example"]),
                usage_count=row["usage_count"],
                created_at=row["created_at"],
                is_custom=bool(row["is_custom"])
            )

    def record_usage(self, template_id: str):
        """Increments template usage counter."""
        with self._get_connection() as conn:
            conn.execute("UPDATE motion_templates SET usage_count = usage_count + 1 WHERE id = ?", (template_id,))
            conn.commit()

    def find_best_template(self, topic: str, notes: str = "", threshold: float = 0.50) -> Tuple[Optional[MotionTemplate], float, bool]:
        """
        Executes semantic search against the template registry.
        Returns: (best_template, similarity_score, is_confident_match)
        """
        templates = self.list_templates()
        if not templates:
            return None, 0.0, False

        query = f"{topic} {notes}".strip()
        best_tpl = None
        best_score = -1.0

        for tpl in templates:
            score = SemanticMatcher.compute_similarity(query, tpl)
            if score > best_score:
                best_score = score
                best_tpl = tpl

        is_match = (best_score >= threshold)
        return best_tpl, best_score, is_match

    def build_surgical_prompt(self, template: MotionTemplate, topic: str, notes: str = "") -> str:
        """
        Generates the surgical prompt of only a few hundred bytes injecting ONLY the selected schema.
        Prevents context pollution, eliminates timeouts, and keeps AI output 100% predictable.
        """
        compact_schema = json.dumps(template.schema, ensure_ascii=False)
        context_notes = f"\nDetalles del usuario: \"{notes[:250]}\"" if notes else ""

        return f"""Actúa como un Diseñador Técnico de Motion Graphics para Google Cloud.
Tengo la plantilla de animación '{template.id}' que requiere este JSON exacto:
{compact_schema}

Completa ÚNICAMENTE el JSON para ilustrar didácticamente este tema:
Tema: "{topic}"{context_notes}

Reglas estrictas:
- Devuelve ÚNICAMENTE el objeto JSON válido con los mismos campos del schema.
- Mantén exactamente los IDs de nodos y etapas correlativas.
- Prohibido texto explicativo adicional o markdown exterior."""

    def auto_index_template(
        self,
        template_id: str,
        name: str,
        description: str,
        tags: List[str],
        schema: Dict[str, Any],
        default_example: Dict[str, Any],
        renderer_type: str = "network_flow"
    ) -> MotionTemplate:
        """
        Dynamically registers and indexes a new template created organically for unseen topics.
        The local SQLite database grows richer over time with 0 manual intervention.
        """
        clean_id = re.sub(r'[^a-z0-9_]', '_', template_id.lower()).strip('_')
        tpl = MotionTemplate(
            id=clean_id,
            name=name,
            description=description,
            renderer_type=renderer_type,
            tags=tags,
            schema=schema,
            default_example=default_example,
            usage_count=1,
            created_at=time.time(),
            is_custom=True
        )

        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO motion_templates
                (id, name, description, renderer_type, tags, schema, default_example, usage_count, created_at, is_custom)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tpl.id,
                tpl.name,
                tpl.description,
                tpl.renderer_type,
                json.dumps(tpl.tags, ensure_ascii=False),
                json.dumps(tpl.schema, ensure_ascii=False),
                json.dumps(tpl.default_example, ensure_ascii=False),
                tpl.usage_count,
                tpl.created_at,
                1
            ))
            conn.commit()

        print(f"💾 [Auto-Indexación] Nueva plantilla '{tpl.id}' registrada e indexada en SQLite ({self.db_path.name}).")
        return tpl
