"""
Media Collector & Provider Router.
Orchestrates downloading and allocating visual media assets from NASA, Pexels, and Pixabay.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config import ASSETS_DIR, ENABLE_AI_IMAGE_FALLBACK
from providers.nasa import NASAProvider
from providers.pexels import PexelsProvider
from providers.pixabay import PixabayProvider
from providers.pollinations import PollinationsProvider

# Detect if topic is space-specific for auto mode (Spanish, English, Chinese triggers)
SPACE_TRIGGERS = [
    # Spanish
    "tierra", "marte", "agujero", "nasa", "galaxia", "hubble", "webb", "universo",
    "planeta", "estrella", "espacio", "jupiter", "luna", "saturno", "cosmos",
    "astronauta", "sol", "solar", "orbita", "meteorito", "asteroide", "cometa", "jwst",
    # English
    "earth", "mars", "black hole", "galaxy", "universe", "planet", "star",
    "space", "jupiter", "moon", "saturn", "cosmos", "astronaut", "sun", "solar",
    "orbit", "meteor", "asteroid", "comet",
    # Chinese
    "月球", "火星", "黑洞", "宇宙", "银河", "恒星", "行星", "地球", "太空", "太阳", "韦伯", "航天"
]


def prepare_primary_discovery_asset(
    nasa: NASAProvider,
    trending_metadata: Optional[Dict[str, Any]],
    topic: str,
    orientation: str,
    nasa_grounded_context: Optional[str]
) -> Tuple[Optional[Path], Optional[Dict[str, Any]], Optional[str]]:
    """
    Downloads authentic NASA discovery media for Scene 1 if running from trending metadata,
    and constructs a grounding prompt injection for the AI script generator.
    """
    primary_asset_file = None
    primary_asset_meta = None

    if trending_metadata:
        primary_asset_file, primary_asset_meta = nasa.fetch_primary_discovery_asset(
            discovery_meta=trending_metadata,
            scene_idx=1,
            save_dir=ASSETS_DIR,
            orientation=orientation
        )
        if primary_asset_meta:
            p_type = primary_asset_meta.get("media_type", "visual")
            p_title = primary_asset_meta.get("title", topic)
            p_source = primary_asset_meta.get("source", "NASA")
            grounding_note = (
                f"\n[OFFICIAL NASA DISCOVERY VISUAL]: An authentic NASA {p_type} of '{p_title}' ({p_source}) "
                f"has been obtained and will be displayed in Scene 1. Hook the audience immediately in Scene 1 "
                f"by referencing what they are seeing in this official NASA observation."
            )
            if nasa_grounded_context:
                nasa_grounded_context += grounding_note
            else:
                nasa_grounded_context = grounding_note

    return primary_asset_file, primary_asset_meta, nasa_grounded_context


def collect_scene_assets(
    scenes: List[Dict[str, Any]],
    scene_timings: List[Dict[str, Any]],
    topic: str,
    chosen_provider: str,
    nasa: NASAProvider,
    pexels: PexelsProvider,
    orientation: str,
    primary_asset_file: Optional[Path] = None,
    primary_asset_meta: Optional[Dict[str, Any]] = None,
    pixabay: Optional[PixabayProvider] = None,
    pollinations: Optional[PollinationsProvider] = None,
    enable_ai_fallback: bool = ENABLE_AI_IMAGE_FALLBACK
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Collects visual media assets for all scenes according to chosen provider or auto intelligent routing.
    Supports a resilient cascade across NASA, Pexels, Pixabay, and Pollinations (FLUX AI fallback).
    """
    print(f"\n🔭 Fetching media assets (Mode: {chosen_provider.upper()})...")
    scene_assets = []
    assets_metadata = []

    is_space_topic = any(t in topic.lower() for t in SPACE_TRIGGERS)
    has_pexels = pexels.is_configured()
    has_pixabay = pixabay is not None and pixabay.is_configured()

    for idx, (scene, timing) in enumerate(zip(scenes, scene_timings), start=1):
        raw_kws = (
            scene.get("keywords")
            or scene.get("nasa_keywords")
            or scene.get("pexels_keywords")
            or scene.get("stock_keywords")
            or [topic]
        )
        if isinstance(raw_kws, str):
            keywords = [k.strip() for k in raw_kws.split(",") if k.strip()]
        elif isinstance(raw_kws, list):
            keywords = [str(k).strip() for k in raw_kws if str(k).strip()]
        else:
            keywords = [topic]
        if not keywords:
            keywords = [topic]

        visual_type = scene.get("visual_type", "video")
        asset_file = None
        meta = None

        # Check if Scene 1 was pre-downloaded with authentic NASA discovery media
        if idx == 1 and primary_asset_file and primary_asset_file.exists() and primary_asset_meta:
            print(f"  ✅ Escena 01 asignada con el medio oficial del descubrimiento: {primary_asset_file.name}")
            print(f"     📡 Fuente / Atribución: {primary_asset_meta.get('attribution_text', 'NASA')}")
            asset_file = primary_asset_file
            meta = primary_asset_meta
        elif chosen_provider == "pollinations":
            if pollinations:
                asset_file, meta = pollinations.fetch_scene_asset(
                    scene_idx=idx,
                    prompt=scene.get("image_prompt"),
                    keywords=keywords,
                    orientation=orientation,
                    visual_subject=scene.get("visual_subject"),
                    topic=topic
                )
            else:
                print("  ⚠️ Pollinations provider requested, but provider instance is missing.")
        elif chosen_provider == "pixabay":
            if has_pixabay and pixabay:
                asset_file, meta = pixabay.fetch_scene_asset(
                    scene_idx=idx,
                    keywords=keywords,
                    preferred_type=visual_type,
                    orientation=orientation
                )
            else:
                print("  ⚠️ Pixabay provider requested, but PIXABAY_API_KEY is not configured.")
        elif chosen_provider == "pexels":
            asset_file, meta = pexels.fetch_scene_asset(
                scene_idx=idx,
                keywords=keywords,
                preferred_type=visual_type,
                orientation=orientation
            )
            if not asset_file and has_pixabay and pixabay:
                print(f"    ↳ Pexels visual not found for scene {idx}, falling back to Pixabay...")
                asset_file, meta = pixabay.fetch_scene_asset(
                    scene_idx=idx,
                    keywords=keywords,
                    preferred_type=visual_type,
                    orientation=orientation
                )
        elif chosen_provider == "nasa":
            asset_file, meta = nasa.fetch_scene_asset(
                scene_idx=idx,
                keywords=keywords,
                preferred_type=visual_type,
                orientation=orientation,
                topic_anchor=topic,
                visual_subject=scene.get("visual_subject"),
                primary_asset_file=primary_asset_file,
                primary_asset_meta=primary_asset_meta
            )
            if not asset_file and has_pexels:
                print(f"    ↳ NASA visual not found for scene {idx}, trying Pexels...")
                asset_file, meta = pexels.fetch_scene_asset(
                    scene_idx=idx,
                    keywords=keywords,
                    preferred_type=visual_type,
                    orientation=orientation
                )
            if not asset_file and has_pixabay and pixabay:
                print(f"    ↳ Trying Pixabay as secondary fallback for scene {idx}...")
                asset_file, meta = pixabay.fetch_scene_asset(
                    scene_idx=idx,
                    keywords=keywords,
                    preferred_type=visual_type,
                    orientation=orientation
                )
        else:
            # Auto mode: 3-tier intelligent cascade
            # Space topics: 1. NASA -> 2. Pexels -> 3. Pixabay
            # General topics: 1. Pexels -> 2. Pixabay -> 3. NASA
            if is_space_topic or (not has_pexels and not has_pixabay):
                asset_file, meta = nasa.fetch_scene_asset(
                    scene_idx=idx,
                    keywords=keywords,
                    preferred_type=visual_type,
                    orientation=orientation,
                    topic_anchor=topic,
                    visual_subject=scene.get("visual_subject"),
                    primary_asset_file=primary_asset_file,
                    primary_asset_meta=primary_asset_meta
                )
                if not asset_file and has_pexels:
                    print(f"    ↳ NASA visual not found for scene {idx}, querying Pexels...")
                    asset_file, meta = pexels.fetch_scene_asset(
                        scene_idx=idx,
                        keywords=keywords,
                        preferred_type=visual_type,
                        orientation=orientation
                    )
                if not asset_file and has_pixabay and pixabay:
                    print(f"    ↳ Pexels visual not found for scene {idx}, querying Pixabay...")
                    asset_file, meta = pixabay.fetch_scene_asset(
                        scene_idx=idx,
                        keywords=keywords,
                        preferred_type=visual_type,
                        orientation=orientation
                    )
            else:
                if has_pexels:
                    asset_file, meta = pexels.fetch_scene_asset(
                        scene_idx=idx,
                        keywords=keywords,
                        preferred_type=visual_type,
                        orientation=orientation
                    )
                if not asset_file and has_pixabay and pixabay:
                    print(f"    ↳ Querying Pixabay for scene {idx}...")
                    asset_file, meta = pixabay.fetch_scene_asset(
                        scene_idx=idx,
                        keywords=keywords,
                        preferred_type=visual_type,
                        orientation=orientation
                    )
                if not asset_file:
                    print(f"    ↳ Querying NASA library for scene {idx}...")
                    asset_file, meta = nasa.fetch_scene_asset(
                        scene_idx=idx,
                        keywords=keywords,
                        preferred_type=visual_type,
                        orientation=orientation,
                        topic_anchor=topic,
                        visual_subject=scene.get("visual_subject"),
                        primary_asset_file=primary_asset_file,
                        primary_asset_meta=primary_asset_meta
                    )

        # AI Image Generation Fallback (Zero-cost hyper-specific prompt match)
        if not asset_file and enable_ai_fallback and pollinations:
            print(f"    🎨 Stock visual not found for scene {idx}, generating tailored AI visual with Pollinations ({pollinations.default_model.upper()})...")
            asset_file, meta = pollinations.fetch_scene_asset(
                scene_idx=idx,
                prompt=scene.get("image_prompt"),
                keywords=stock_keywords,
                orientation=orientation,
                visual_subject=scene.get("visual_subject"),
                topic=topic
            )

        if asset_file and meta:
            scene_assets.append({
                "scene_idx": idx,
                "file": asset_file,
                "is_video": (meta["media_type"] == "video"),
                "duration": timing["duration"]
            })
            assets_metadata.append(meta)
        else:
            print(f"  ⚠️ Using fallback background for scene {idx}...")
            scene_assets.append({
                "scene_idx": idx,
                "file": None,
                "is_video": False,
                "duration": timing["duration"]
            })
            assets_metadata.append({
                "scene_index": idx,
                "provider": "synthetic",
                "title": f"Scene {idx}",
                "media_type": "image",
                "attribution_text": "NASA Science Archive" if is_space_topic else "Stock Visual"
            })

    return scene_assets, assets_metadata
