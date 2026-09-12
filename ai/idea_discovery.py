"""
Content Ideas Discovery Engine for Science & Viral Shorts.
Generates, ranks, caches, and interactively presents high-retention content ideas
for YouTube Shorts, Instagram Reels, and TikTok.
"""

import json
import random
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config import (
    BASE_DIR,
    GEMINI_API_KEY,
    GROQ_API_BASE,
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OUTPUT_DIR,
    sanitize_env_value,
)
from utils.files import load_json, save_json

# Curated high-retention viral ideas library (guaranteed offline / fallback availability)
CURATED_VIRAL_IDEAS = [
    {
        "title": "El misterio del Gran Atractor",
        "topic": "el misterio del gran atractor",
        "category": "misterios",
        "hook": "¿Hacia dónde se mueve nuestra galaxia a más de 2 millones de kilómetros por hora?",
        "visual_angle": "Simulaciones 3D de cúmulos galácticos, corrientes de materia oscura y mapas cósmicos",
        "why_it_works": "Genera intriga inmediata sobre una fuerza colosal oculta detrás de la Vía Láctea que nadie puede ver directamente.",
        "viral_score": 9.7
    },
    {
        "title": "TON 618: El monstruo que devora galaxias",
        "topic": "agujero negro hipermasivo TON 618",
        "category": "agujeros_negros",
        "hook": "Este objeto es tan colosal que toda nuestra galaxia junta parecería una mota de polvo a su lado.",
        "visual_angle": "Comparativas de escala 3D con el sistema solar y discos de acreción incandescentes",
        "why_it_works": "El choque de escalas extremas e incomprensibles activa de inmediato el asombro y la fascinación.",
        "viral_score": 9.6
    },
    {
        "title": "El planeta donde llueve cristal de lado",
        "topic": "exoplaneta HD 189733b lluvia de cristal",
        "category": "planetas_extremos",
        "hook": "Existe un planeta azul que parece pacífico, pero en su atmósfera llueve vidrio hirviendo a 7.000 km/h.",
        "visual_angle": "Animaciones de tormentas colosales, vientos supersónicos y atmósfera azul cobalto",
        "why_it_works": "Subvierte las expectativas visuales (parece la Tierra pero es un infierno mortal).",
        "viral_score": 9.5
    },
    {
        "title": "¿Qué verías al caer en un agujero negro?",
        "topic": "que verias al caer dentro de un agujero negro",
        "category": "que_pasaria_si",
        "hook": "Si cruzaras el horizonte de sucesos, verías el futuro entero del universo pasar en un instante.",
        "visual_angle": "Distorsión gravitacional, lentes de luz estelar y horizonte de sucesos en primera persona",
        "why_it_works": "La pregunta hipotética en primera persona genera una inmersión psicológica irresistible.",
        "viral_score": 9.8
    },
    {
        "title": "Las galaxias imposibles del James Webb",
        "topic": "galaxias imposibles descubiertas por James Webb",
        "category": "james_webb",
        "hook": "El telescopio James Webb acaba de encontrar algo al inicio del universo que la física no puede explicar.",
        "visual_angle": "Imágenes infrarrojas del campo profundo de Webb y modelos cosmológicos en colapso",
        "why_it_works": "Toca la controversia científica real y la sensación de que los libros de texto deben reescribirse.",
        "viral_score": 9.4
    },
    {
        "title": "El Gran Filtro: ¿Por qué estamos solos?",
        "topic": "paradoja de fermi y teoria del gran filtro",
        "category": "paradojas",
        "hook": "Si el universo tiene billones de mundos habitables... ¿por qué el cosmos guarda un silencio absoluto?",
        "visual_angle": "Cielos nocturnos estrellados, antenas de radio SETI en silencio y civilizaciones en ruinas",
        "why_it_works": "Toca la soledad existencial humana y una de las mayores paradojas sin resolver.",
        "viral_score": 9.6
    },
    {
        "title": "El planeta de diamante: 55 Cancri e",
        "topic": "planeta de diamante 55 Cancri e",
        "category": "planetas_extremos",
        "hook": "A 40 años luz existe un mundo compuesto de puro diamante y grafito que vale billones de dólares.",
        "visual_angle": "Mundos de cristal brillante, ríos de lava de carbono y texturas minerales resplandecientes",
        "why_it_works": "Asocia la riqueza terrenal humana con una escala planetaria inverosímil.",
        "viral_score": 9.3
    },
    {
        "title": "El misterio de la señal Wow!",
        "topic": "la senal wow del espacio exterior",
        "category": "misterios",
        "hook": "En 1977, un radiotelescopio captó un mensaje de 72 segundos que jamás volvió a repetirse.",
        "visual_angle": "Radiotelescopios gigantes, ondas electromagnéticas cruzando el vacío e impresiones de datos",
        "why_it_works": "Misterio histórico auténtico que roza la posibilidad de contacto extraterrestre.",
        "viral_score": 9.5
    },
    {
        "title": "Estrellas de neutrones: Una cucharadita pesa una montaña",
        "topic": "estrellas de neutrones y magnetars densidad extrema",
        "category": "misterios",
        "hook": "Una sola cucharadita de este objeto pesaría más que todas las personas del planeta juntas.",
        "visual_angle": "Púlsares girando a velocidad vertiginosa, campos magnéticos extremos y ondas de choque",
        "why_it_works": "Metáfora tangible (la cucharadita) para un concepto físico de densidad incomprensible.",
        "viral_score": 9.4
    },
    {
        "title": "El día que la Tierra casi muere: Estallidos gamma",
        "topic": "estallidos de rayos gamma peligro para la tierra",
        "category": "apocalipsis",
        "hook": "Un rayo invisible a la velocidad de la luz podría destruir la atmósfera de la Tierra sin aviso previo.",
        "visual_angle": "Supernovas hipermasivas disparando haces de energía pura a través del vacío",
        "why_it_works": "Tensión de alto riesgo y vulnerabilidad planetaria que retiene la atención de principio a fin.",
        "viral_score": 9.5
    },
    {
        "title": "El planeta errante que viaja solo en la oscuridad",
        "topic": "planetas errantes huerfanos sin estrella",
        "category": "planetas_extremos",
        "hook": "Hay miles de millones de planetas congelados vagando por el espacio sin ninguna estrella que los caliente.",
        "visual_angle": "Planetas oscuros iluminados únicamente por auroras boreales y luz estelar lejana",
        "why_it_works": "Evoca misterio sombrío y atmósfera de ciencia ficción cinematográfica.",
        "viral_score": 9.2
    },
    {
        "title": "¿Qué pasaría si la Luna desapareciera mañana?",
        "topic": "que pasaria si la luna desaparece de repente",
        "category": "que_pasaria_si",
        "hook": "Si la Luna se desvaneciera esta noche, los días durarían 6 horas y el eje de la Tierra colapsaría.",
        "visual_angle": "Mareas descontroladas, la Luna fragmentándose y noches en oscuridad total",
        "why_it_works": "Afecta directamente la vida cotidiana del espectador con consecuencias devastadoras.",
        "viral_score": 9.7
    },
    {
        "title": "K2-18b: ¿Se descubrió vida en otro mundo?",
        "topic": "exoplaneta K2-18b posible senal de vida biologica",
        "category": "james_webb",
        "hook": "El telescopio James Webb detectó una molécula en este planeta que en la Tierra solo la producen seres vivos.",
        "visual_angle": "Océanos extraterrestres bajo cielos rojizos y espectros de absorción de luz",
        "why_it_works": "Toca la pregunta definitiva de la humanidad con evidencia científica reciente.",
        "viral_score": 9.7
    },
    {
        "title": "La colisión de la Vía Láctea con Andrómeda",
        "topic": "colision galactica via lactea y andromeda",
        "category": "apocalipsis",
        "hook": "El cielo nocturno del futuro se verá completamente cubierto por una galaxia gigante a punto de chocar.",
        "visual_angle": "Evolución timelapse del cielo nocturno con Andrómeda acercándose y fusionándose",
        "why_it_works": "Visualmente deslumbrante con una perspectiva de tiempo cósmico apabullante.",
        "viral_score": 9.6
    },
    {
        "title": "El vacío de Boötes: El lugar más solitario del universo",
        "topic": "el gran vacio de bootes espacio vacio",
        "category": "misterios",
        "hook": "Existe una región del espacio de 300 millones de años luz donde casi no hay nada. Absolutamente nada.",
        "visual_angle": "Zoom hacia una inmensa oscuridad rodeada de filamentos galácticos brillantes",
        "why_it_works": "Juega con el terror al vacío y las preguntas de qué o quién podría haber vaciado ese sector.",
        "viral_score": 9.4
    }
]

CATEGORY_LABELS = {
    "all": "🌟 Todas las categorías virales (Mix)",
    "misterios": "🔭 Misterios Cósmicos & Cosas Inexplicables",
    "agujeros_negros": "🕳️ Agujeros Negros & Singularidades",
    "planetas_extremos": "🪐 Exoplanetas Inquietantes & Mundos Extremos",
    "james_webb": "🛰️ Descubrimientos del Telescopio James Webb",
    "paradojas": "🧠 Paradojas Científicas & Paradoja de Fermi",
    "apocalipsis": "💥 Catástrofes Cósmicas & Fin de los Tiempos",
    "que_pasaria_si": "❓ Escenarios Hipotéticos ('¿Qué pasaría si...?')"
}


class ContentIdeaGenerator:
    """Generates and evaluates high-retention video topic ideas using AI or curated algorithms."""

    def __init__(
        self,
        gemini_key: Optional[str] = None,
        openai_key: Optional[str] = None,
        groq_key: Optional[str] = None,
        preferred_provider: str = LLM_PROVIDER
    ):
        self.gemini_key = sanitize_env_value(gemini_key or GEMINI_API_KEY)
        self.openai_key = sanitize_env_value(openai_key or OPENAI_API_KEY)
        self.groq_key = sanitize_env_value(groq_key or GROQ_API_KEY)
        self.provider = (preferred_provider or LLM_PROVIDER or "auto").lower()

    def _is_valid_key(self, key: Optional[str]) -> bool:
        if not key or len(key) < 15:
            return False
        placeholders = ["demo_key", "tu_clave", "sk-...", "your_key", "xxx", "placeholder"]
        return not any(p in key.lower() for p in placeholders)

    def generate_ideas(
        self,
        category: str = "all",
        language: str = "es",
        count: int = 5,
        avoid_topics: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates structured viral topic ideas.
        Tries configured LLM first; falls back smoothly to the curated catalogue.
        """
        avoid_topics = avoid_topics or []
        ai_ideas = None

        # Try LLM if configured
        if self._is_valid_key(self.groq_key) or self._is_valid_key(self.gemini_key) or self._is_valid_key(self.openai_key):
            try:
                ai_ideas = self._fetch_ai_ideas(category, language, count, avoid_topics)
            except Exception as ex:
                print(f"  ℹ️ Generación por IA no disponible ({ex}), usando catálogo curado de alto impacto...")

        if ai_ideas and len(ai_ideas) >= 3:
            return ai_ideas[:count]

        # Fallback: curated catalogue
        return self._get_curated_ideas(category=category, count=count, avoid_topics=avoid_topics)

    def _get_curated_ideas(
        self,
        category: str = "all",
        count: int = 5,
        avoid_topics: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Selects and randomizes from curated high-retention database."""
        avoid_set = {t.lower() for t in (avoid_topics or [])}
        pool = []

        for item in CURATED_VIRAL_IDEAS:
            if item["topic"].lower() in avoid_set:
                continue
            if category and category != "all":
                if item.get("category") != category:
                    continue
            pool.append(item.copy())

        # If pool is small, relax category filter
        if len(pool) < count:
            for item in CURATED_VIRAL_IDEAS:
                if item not in pool and item["topic"].lower() not in avoid_set:
                    pool.append(item.copy())

        random.shuffle(pool)
        selected = pool[:count]

        # Assign incremental IDs
        for idx, it in enumerate(selected, 1):
            it["id"] = idx

        return selected

    def _build_prompt(self, category: str, language: str, count: int, avoid_topics: List[str]) -> str:
        cat_desc = CATEGORY_LABELS.get(category, f"categoría '{category}'")
        lang_name = "español" if language == "es" else "inglés"
        avoid_clause = ""
        if avoid_topics:
            avoid_clause = f"\nEvita repetir estos temas específicos: {', '.join(avoid_topics[:10])}."

        return f"""Eres un estratega viral jefe y guionista de YouTube Shorts, Instagram Reels y TikTok especializado en divulgación científica, astronomía y el cosmos.

Genera exactamente {count} ideas de contenido altamente virales y magnéticas en {lang_name} dentro de: {cat_desc}.{avoid_clause}

REGLAS DE RETENCIÓN OBLIGATORIAS:
1. "Curiosity Gap": El gancho debe plantear una pregunta o hecho contraintuitivo que active el cerebro reptiliano en los primeros 3 segundos.
2. Viabilidad Visual: El tema DEBE contar con abundantes videos e imágenes de stock espectaculares (agujeros negros, nebulosas, colisiones, 3D, rovers, planetas extremos).
3. Choque de Escalas o Misterio: Cosas que empequeñecen al ser humano o hechos inquietantes de la física moderna.
4. "topic" conciso: Debe ser una frase clave limpia (2 a 5 palabras) adecuada para buscar medios y generar el guión.

Responde ÚNICAMENTE con un JSON válido con esta estructura:
{{
  "ideas": [
    {{
      "title": "Título corto y llamativo",
      "topic": "termino clave de busqueda del tema",
      "category": "{category if category != 'all' else 'misterios'}",
      "hook": "Gancho irresistible hablado para los primeros 3 segundos",
      "visual_angle": "Qué visuales y animaciones 3D se usarán en el video",
      "why_it_works": "Por qué este tema retiene a la audiencia en 1 frase",
      "viral_score": 9.6
    }}
  ]
}}
"""

    def _fetch_ai_ideas(
        self,
        category: str,
        language: str,
        count: int,
        avoid_topics: List[str]
    ) -> Optional[List[Dict[str, Any]]]:
        prompt = self._build_prompt(category, language, count, avoid_topics)

        # 1. Try Groq
        if self._is_valid_key(self.groq_key) and self.provider in ["auto", "groq"]:
            try:
                payload = {
                    "model": GROQ_MODEL or "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.7
                }
                req = urllib.request.Request(
                    f"{GROQ_API_BASE}/chat/completions",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.groq_key}",
                        "User-Agent": "NASA-Shorts-Generator/1.0"
                    },
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    items = parsed.get("ideas", [])
                    if items:
                        return self._sanitize_items(items)
            except Exception:
                pass

        # 2. Try Gemini
        if self._is_valid_key(self.gemini_key) and self.provider in ["auto", "gemini"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.7,
                        "responseMimeType": "application/json",
                        "maxOutputTokens": 2048,
                        "thinkingConfig": {"thinkingBudget": 0}
                    }
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(content)
                    items = parsed.get("ideas", [])
                    if items:
                        return self._sanitize_items(items)
            except Exception:
                pass

        return None

    def _sanitize_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned = []
        for idx, item in enumerate(items, 1):
            cleaned.append({
                "id": idx,
                "title": str(item.get("title", f"Idea {idx}")).strip(),
                "topic": str(item.get("topic") or item.get("title", "")).strip(),
                "category": str(item.get("category", "misterios")).strip(),
                "hook": str(item.get("hook", "")).strip(),
                "visual_angle": str(item.get("visual_angle", "")).strip(),
                "why_it_works": str(item.get("why_it_works", "")).strip(),
                "viral_score": float(item.get("viral_score", 9.0))
            })
        return cleaned


def resolve_content_ideas(args) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Main interactive entry point for Content Ideas Discovery.
    Presents curated and AI-generated viral ideas, allowing the user to select one,
    regenerate, change category, or exit.
    Returns:
        (selected_topic, idea_metadata) or (None, None) if exited.
    """
    cache_file = OUTPUT_DIR / ".ideas_cache.json"
    generator = ContentIdeaGenerator(
        gemini_key=getattr(args, "gemini_key", None),
        openai_key=getattr(args, "openai_key", None),
        groq_key=getattr(args, "groq_key", None),
        preferred_provider=getattr(args, "llm", "auto")
    )

    current_category = getattr(args, "ideas_category", None) or "all"
    seen_topics: List[str] = []
    current_ideas: List[Dict[str, Any]] = []

    # Attempt to load cache if not forcing refresh
    if not getattr(args, "refresh_trends", False) and cache_file.exists():
        try:
            cached_data = load_json(cache_file)
            if isinstance(cached_data, dict):
                cached_cat = cached_data.get("category")
                cached_list = cached_data.get("ideas")
                if cached_cat == current_category and isinstance(cached_list, list) and len(cached_list) > 0:
                    current_ideas = cached_list
        except Exception:
            pass

    # If no cached ideas, generate fresh
    if not current_ideas:
        print(f"\n💡 Generando ideas virales de contenido (Categoría: {CATEGORY_LABELS.get(current_category, current_category)})...")
        current_ideas = generator.generate_ideas(
            category=current_category,
            language=getattr(args, "language", "es"),
            count=5,
            avoid_topics=seen_topics
        )

    for item in current_ideas:
        seen_topics.append(item["topic"])

    # If non-interactive mode (--top-choice specified or --list-ideas)
    if getattr(args, "list_ideas", False):
        _print_ideas_table(current_ideas, current_category)
        print("\n💡 Para producir un video de cualquier idea:")
        print("   python main.py --discover-ideas --top-choice 1")
        print("   python main.py --discover-ideas --top-choice 2\n")
        return None, None

    # Interactive Loop
    while True:
        _print_ideas_table(current_ideas, current_category)

        # Save cache for persistence
        save_json({
            "timestamp": time.time(),
            "category": current_category,
            "ideas": current_ideas
        }, cache_file)

        # Check if user passed an explicit --top-choice without interactive prompt
        if hasattr(args, "top_choice") and getattr(args, "top_choice_explicit", False):
            choice_idx = max(0, min(args.top_choice - 1, len(current_ideas) - 1))
            winning = current_ideas[choice_idx]
            print(f"\n👉 Seleccionada automáticamente la Opción #{choice_idx + 1}: '{winning['title']}'")
            return winning["topic"], winning

        # Prompt user for action
        print("\n" + "─" * 65)
        print("⚡ ACCIONES DISPONIBLES:")
        print("   [1-5] Seleccionar esa idea y producir el video completo ahora")
        print("   [R]   Regenerar / Explorar 5 ideas frescas diferentes")
        print("   [C]   Cambiar de categoría / nicho temático")
        print("   [Q]   Salir al menú principal")
        print("─" * 65)

        try:
            choice = input("👉 Elige una opción: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Cancelado por el usuario.")
            return None, None

        if not choice:
            continue

        choice_lower = choice.lower()

        # Selection of an idea [1-5]
        if choice.isdigit():
            val = int(choice)
            if 1 <= val <= len(current_ideas):
                winning = current_ideas[val - 1]
                print("\n" + "═" * 65)
                print(f"🚀 ¡IDEA SELECCIONADA CON ÉXITO! (Opción #{val}):")
                print(f"   Título:   \"{winning['title']}\"")
                print(f"   Tema:     {winning['topic']}")
                print(f"   Gancho:   \"{winning['hook']}\"")
                print("═" * 65)
                return winning["topic"], winning
            else:
                print(f"⚠️ Por favor ingresa un número entre 1 y {len(current_ideas)}.")
                continue

        # Regenerate fresh ideas
        elif choice_lower == "r":
            print(f"\n🔄 Buscando 5 nuevos ángulos virales ({CATEGORY_LABELS.get(current_category, current_category)})...")
            fresh = generator.generate_ideas(
                category=current_category,
                language=getattr(args, "language", "es"),
                count=5,
                avoid_topics=seen_topics
            )
            if fresh:
                current_ideas = fresh
                for item in fresh:
                    seen_topics.append(item["topic"])
            else:
                print("⚠️ No se pudieron obtener más ideas distintas en este momento.")

        # Change category
        elif choice_lower == "c":
            cat_keys = list(CATEGORY_LABELS.keys())
            print("\n📂 SELECCIONA UNA NUEVA CATEGORÍA TEMÁTICA:")
            for i, k in enumerate(cat_keys, 1):
                print(f"   [{i}] {CATEGORY_LABELS[k]}")
            print(f"   [{len(cat_keys) + 1}] ✍️ Escribir categoría personalizada")

            try:
                cat_input = input("\n👉 Selecciona una categoría: ").strip()
            except (EOFError, KeyboardInterrupt):
                continue

            if cat_input.isdigit():
                c_val = int(cat_input)
                if 1 <= c_val <= len(cat_keys):
                    current_category = cat_keys[c_val - 1]
                elif c_val == len(cat_keys) + 1:
                    custom_cat = input("✍️ Escribe el tema o nicho deseado (ej. 'supernovas', 'marte', 'gravedad cuántica'): ").strip()
                    if custom_cat:
                        current_category = custom_cat
            elif cat_input:
                current_category = cat_input

            print(f"\n🔄 Generando ideas para categoría: {CATEGORY_LABELS.get(current_category, current_category)}...")
            current_ideas = generator.generate_ideas(
                category=current_category,
                language=getattr(args, "language", "es"),
                count=5,
                avoid_topics=seen_topics
            )

        # Quit
        elif choice_lower in ["q", "exit", "salir"]:
            print("\n👋 Sesión de lluvia de ideas finalizada. ¡Hasta pronto!")
            return None, None
        else:
            print("⚠️ Opción no reconocida. Escribe un número [1-5], R, C o Q.")


def _print_ideas_table(ideas: List[Dict[str, Any]], category: str):
    """Renders high-contrast, aesthetic CLI cards for discovered content ideas."""
    print("\n" + "═" * 65)
    print("💡 DESCUBRIDOR DE IDEAS VIRALES (CONTENT IDEAS DISCOVERY)")
    print("═" * 65)
    cat_label = CATEGORY_LABELS.get(category, f"Nicho personalizado: '{category}'")
    print(f"📂 Categoría: {cat_label}")
    print(f"⏱️  Formato:   Shorts / Reels / TikTok (Alto dinamismo)")
    print("─" * 65)

    for i, item in enumerate(ideas, 1):
        score = item.get("viral_score", 9.0)
        stars = "🔥" if score >= 9.5 else "⭐"
        cat_badge = item.get("category", category).upper().replace("_", " ")

        print(f"\n[{i}] {stars} {score:.1f}/10  |  \"{item.get('title')}\"")
        print(f"    🏷️  Categoría:      {cat_badge}")
        print(f"    🪝 Gancho (3 seg): \"{item.get('hook')}\"")
        if item.get("visual_angle"):
            print(f"    🎬 Enfoque Visual: {item.get('visual_angle')}")
        if item.get("why_it_works"):
            print(f"    🧠 Por qué sirve:  {item.get('why_it_works')}")
        print(f"    🎯 Tema video:     \"{item.get('topic')}\"")

    print("\n" + "═" * 65)
