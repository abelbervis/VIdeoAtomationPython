"""
Media Collector & Provider Router.
Orchestrates downloading and allocating visual media assets from NASA and Pexels.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config import ASSETS_DIR
from providers.nasa import NASAProvider
from providers.pexels import PexelsProvider

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
    primary_asset_meta: Optional[Dict[str, Any]] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Collects visual media assets for all scenes according to chosen provider or auto intelligent routing.
    """
    print(f"\n🔭 Fetching media assets (Mode: {chosen_provider.upper()})...")
    scene_assets = []
    assets_metadata = []

    is_space_topic = any(t in topic.lower() for t in SPACE_TRIGGERS)

    for idx, (scene, timing) in enumerate(zip(scenes, scene_timings), start=1):
        nasa_keywords = scene.get("nasa_keywords") or scene.get("keywords") or [topic]
        pexels_keywords = scene.get("pexels_keywords") or scene.get("keywords") or [topic]
        visual_type = scene.get("visual_type", "video")
        asset_file = None
        meta = None

        # Check if Scene 1 was pre-downloaded with authentic NASA discovery media
        if idx == 1 and primary_asset_file and primary_asset_file.exists() and primary_asset_meta:
            print(f"  ✅ Escena 01 asignada con el medio oficial del descubrimiento: {primary_asset_file.name}")
            print(f"     📡 Fuente / Atribución: {primary_asset_meta.get('attribution_text', 'NASA')}")
            asset_file = primary_asset_file
            meta = primary_asset_meta
        elif chosen_provider == "pexels":
            asset_file, meta = pexels.fetch_scene_asset(
                scene_idx=idx,
                keywords=pexels_keywords,
                preferred_type=visual_type,
                orientation=orientation
            )
        elif chosen_provider == "nasa":
            asset_file, meta = nasa.fetch_scene_asset(
                scene_idx=idx,
                keywords=nasa_keywords,
                preferred_type=visual_type,
                orientation=orientation,
                topic_anchor=topic,
                visual_subject=scene.get("visual_subject"),
                primary_asset_file=primary_asset_file,
                primary_asset_meta=primary_asset_meta
            )
        else:
            # Auto mode: route according to topic domain and available keys
            if is_space_topic or not pexels.is_configured():
                asset_file, meta = nasa.fetch_scene_asset(
                    scene_idx=idx,
                    keywords=nasa_keywords,
                    preferred_type=visual_type,
                    orientation=orientation,
                    topic_anchor=topic,
                    visual_subject=scene.get("visual_subject"),
                    primary_asset_file=primary_asset_file,
                    primary_asset_meta=primary_asset_meta
                )
                if not asset_file and pexels.is_configured():
                    print(f"    ↳ NASA visual not found for scene {idx}, querying Pexels with stock keywords...")
                    asset_file, meta = pexels.fetch_scene_asset(
                        scene_idx=idx,
                        keywords=pexels_keywords,
                        preferred_type=visual_type,
                        orientation=orientation
                    )
            else:
                asset_file, meta = pexels.fetch_scene_asset(
                    scene_idx=idx,
                    keywords=pexels_keywords,
                    preferred_type=visual_type,
                    orientation=orientation
                )
                if not asset_file:
                    print(f"    ↳ Pexels visual not found for scene {idx}, querying NASA with scientific keywords...")
                    asset_file, meta = nasa.fetch_scene_asset(
                        scene_idx=idx,
                        keywords=nasa_keywords,
                        preferred_type=visual_type,
                        orientation=orientation,
                        topic_anchor=topic,
                        visual_subject=scene.get("visual_subject"),
                        primary_asset_file=primary_asset_file,
                        primary_asset_meta=primary_asset_meta
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
