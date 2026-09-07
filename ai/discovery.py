"""
NASA Discovery & Viral Trend Engine.
Handles real-time NASA trends fetching, AI viral scoring, caching, and interactive CLI discovery.
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from ai.trend_evaluator import ViralTrendEvaluator
from config import BASE_DIR, OUTPUT_DIR
from providers.nasa_trends import NASATrendsProvider
from utils.files import format_date_display, load_json, save_json


def resolve_trending_topic(args) -> Tuple[str, Optional[str], Optional[Dict[str, Any]]]:
    """
    Resolves the video topic using NASA APOD archives and viral trend analysis if requested or if no topic was supplied.
    Returns:
        (topic, nasa_grounded_context, trending_metadata)
    """
    # If a manual topic was supplied and trending/discover was not requested, return directly
    if args.topic and not args.trending and not args.discover:
        return args.topic, None, None

    print("\n" + "=" * 65)
    print("🔭 NASA VIRAL TREND HUNTER  |  Discovery & Archive Engine")
    print("=" * 65)

    # Cache file paths: prioritize OUTPUT_DIR for Docker volume persistence across container restarts
    cache_candidates = [
        OUTPUT_DIR / ".trending_cache.json",
        OUTPUT_DIR / "trending_cache.json",
        BASE_DIR / ".trending_cache.json",
    ]
    primary_cache_file = OUTPUT_DIR / ".trending_cache.json"

    ranked_topics = None
    used_cache = False
    has_time_filter = bool(args.date or args.days_back or args.archive)

    # Attempt to load from persistent cache if not forcing refresh
    if not args.refresh_trends:
        for c_file in cache_candidates:
            if c_file.exists():
                cache_data = load_json(c_file)
                if isinstance(cache_data, dict):
                    cache_lang = cache_data.get("language")
                    cache_time = cache_data.get("timestamp", 0)
                    cached_items = cache_data.get("ranked_topics", [])
                    cache_target_date = cache_data.get("target_date")
                    cache_days_back = cache_data.get("days_back")
                    cache_archive = cache_data.get("archive", False)

                    # Validate filter match if specific historical argument was supplied
                    filter_match = True
                    if has_time_filter:
                        if args.date and cache_target_date != args.date:
                            filter_match = False
                        if args.days_back and cache_days_back != args.days_back:
                            filter_match = False
                        if args.archive and not cache_archive:
                            filter_match = False

                    # Cache is valid if same language, filter match, not older than 24h, and non-empty
                    if (
                        filter_match
                        and cache_lang == args.language
                        and (time.time() - cache_time < 86400)
                        and isinstance(cached_items, list)
                        and len(cached_items) > 0
                    ):
                        ranked_topics = cached_items
                        used_cache = True
                        mins_ago = int((time.time() - cache_time) / 60)
                        time_str = f"hace {mins_ago} min" if mins_ago > 0 else "hace un momento"
                        print(f"📦 Usando descubrimientos clasificados en caché ({time_str}, idioma: {args.language}).")
                        if cache_target_date:
                            print(f"   📅 Fecha objetivo archivada: {cache_target_date}")
                        elif cache_days_back:
                            print(f"   📅 Ventana archivada: hace {cache_days_back} días")
                        elif cache_archive:
                            print("   🏛️ Archivo histórico: gemas legendarias (1995-presente)")
                        print(f"   📂 Archivo: {c_file.name} (persistente en Docker)")
                        if args.discover:
                            print("💡 (Usa '--refresh' para forzar una nueva búsqueda en vivo)")
                        break

    # If cache was not used (or forced refresh), fetch fresh from NASA and evaluate with AI
    if not ranked_topics:
        if args.date:
            print(f"📡 Conectando con NASA APOD & Library (Archivo Histórico: fecha {args.date})...")
        elif args.days_back:
            print(f"📡 Conectando con NASA APOD & Library (Archivo Histórico: hace {args.days_back} días)...")
        elif args.archive:
            print("📡 Conectando con el Archivo Histórico de la NASA (1995 - presente: gemas legendarias)...")
        else:
            print("📡 Conectando con las APIs oficiales de la NASA (APOD & Mission Library)...")

        trends_provider = NASATrendsProvider()
        candidates = trends_provider.get_trending_candidates(
            limit=8,
            target_date=args.date,
            days_back=args.days_back,
            random_archive=args.archive
        )
        print(f"✅ Se obtuvieron {len(candidates)} eventos y descubrimientos científicos oficiales.")

        print("🧠 Evaluando potencial viral con IA (Curiosidad, Ganchabilidad, Espectáculo Visual)...")
        evaluator = ViralTrendEvaluator(
            gemini_key=args.gemini_key,
            openai_key=args.openai_key,
            groq_key=args.groq_key,
            preferred_provider=args.llm
        )
        ranked_topics = evaluator.evaluate_candidates(candidates, language=args.language, top_n=5)

    # Always ensure the persistent cache in OUTPUT_DIR is written / kept in sync for Docker
    if ranked_topics:
        cache_payload = {
            "timestamp": time.time(),
            "language": args.language,
            "target_date": getattr(args, "date", None),
            "days_back": getattr(args, "days_back", None),
            "archive": bool(getattr(args, "archive", False)),
            "ranked_topics": ranked_topics
        }
        save_json(cache_payload, primary_cache_file)
        try:
            save_json(cache_payload, BASE_DIR / ".trending_cache.json")
        except Exception:
            pass

    # IF DISCOVER MODE: Show rich CLI table and exit cleanly
    if args.discover:
        print("\n" + "=" * 65)
        header_title = "🌟 DESCUBRIMIENTOS DE LA NASA CLASIFICADOS POR POTENCIAL VIRAL"
        if args.date:
            header_title += f" [Fecha: {args.date}]"
        elif args.days_back:
            header_title += f" [Hace {args.days_back} días]"
        elif args.archive:
            header_title += " [Archivo Histórico 1995-Presente]"
        print(header_title)
        print("=" * 65)
        for i, item in enumerate(ranked_topics or []):
            score = item.get("viral_score", 0.0)
            stars = "🔥" if score >= 9.0 else "⭐"
            formatted_d = format_date_display(item.get("date"), language=args.language) or item.get("date", "Reciente")
            print(f"\n[{i + 1}] {stars} Puntuación Viral: {score:.1f}/10  |  {item.get('adapted_title')}")
            print(f"    📡 Fuente:       {item.get('source')} ({formatted_d})")
            print(f"    🪝 Gancho Viral:  \"{item.get('suggested_hook')}\"")
            print(f"    💡 Razón Viral:   {item.get('viral_reason')}")
            print(f"    📖 Resumen NASA:  {item.get('scientific_summary')}")
        print("\n" + "=" * 65)
        print("💾 Lista de descubrimientos guardada en output/.trending_cache.json")
        print("   (Persistente entre contenedores Docker gracias al volumen ./output)")
        print("💡 Para generar un video de cualquier opción de la lista con total precisión:")
        print("   python main.py --top-choice 1")
        print("   python main.py --top-choice 2")
        print("   (En Docker: docker compose run nasa-shorts --top-choice 2)")
        print("💡 Para explorar otras fechas pasadas del archivo:")
        print("   python main.py --discover --date 2024-04-08")
        print("   python main.py --discover --days-back 30")
        print("   python main.py --discover --archive   (gemas aleatorias de 1995 a hoy)")
        print("   (o usa '--refresh' para forzar una nueva consulta en vivo a la NASA)")
        print("=" * 65 + "\n")
        sys.exit(0)

    if not ranked_topics:
        print("\n❌ No se pudieron evaluar temas de la NASA en este momento.")
        sys.exit(1)

    # IF AUTO-TRENDING: Select winning topic
    choice_idx = max(0, min(args.top_choice - 1, len(ranked_topics) - 1))
    winning = ranked_topics[choice_idx]
    trending_metadata = winning
    selected_topic = winning.get("adapted_title") or winning.get("title")
    nasa_grounded_context = winning.get("scientific_text")

    # Display list of choices with clear pointer to the selected one
    if len(ranked_topics) > 1:
        print(f"\n📋 Opciones disponibles:")
        for i, it in enumerate(ranked_topics):
            mark = "👉 " if i == choice_idx else "   "
            tag = " [SELECCIONADO]" if i == choice_idx else ""
            print(f" {mark}[{i + 1}] {it.get('adapted_title')}{tag} ({it.get('viral_score', 0):.1f}/10)")

    print("\n" + "─" * 65)
    print(f"🏆 TEMA VIRAL SELECCIONADO POR IA (Opción #{choice_idx + 1} de {len(ranked_topics)}):")
    print(f"   Título:    {selected_topic}")
    print(f"   Viralidad: {winning.get('viral_score', 0):.1f}/10  ({winning.get('viral_reason')})")
    print(f"   Gancho:    \"{winning.get('suggested_hook')}\"")
    if winning.get("source"):
        print(f"   Fuente:    {winning.get('source')}")
    if winning.get("credit"):
        print(f"   Crédito:   {winning.get('credit')}")
    if used_cache:
        print(f"   ℹ️  Seleccionado exactamente de la lista guardada en --discover")
        print(f"   💡 (Añade '--refresh' para forzar una nueva consulta en vivo a la NASA)")
    print("─" * 65)

    return selected_topic, nasa_grounded_context, trending_metadata
