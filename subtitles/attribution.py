"""
Attribution Badges & Source Credits Builder.
Extracts and formats media sources, capture dates, and visual subject labels for ASS overlays.
"""

from typing import Any, Dict, List, Optional
from utils.files import clean_visual_subject, format_date_display


def build_source_attributions(
    scenes: List[Dict[str, Any]],
    scene_timings: List[Dict[str, Any]],
    assets_metadata: List[Dict[str, Any]],
    language: str,
    topic: str,
    no_badge_label: bool = False,
    no_badge_date: bool = False
) -> List[Dict[str, Any]]:
    """
    Constructs source attribution badge overlays for each scene.
    """
    source_attributions = []

    for scene, timing, meta in zip(scenes, scene_timings, assets_metadata):
        if meta and meta.get("attribution_text"):
            base_attr = meta.get("attribution_text")
            date_raw = meta.get("date_created") or meta.get("date")
            formatted_date = (
                format_date_display(date_raw, language=language)
                if (not no_badge_date and date_raw)
                else None
            )

            # Determine what is being shown on screen:
            # 1. AI scene visual_subject (in target language)
            # 2. Cleaned official NASA media title
            # 3. Cleaned topic name
            visual_subject_label = None
            if not no_badge_label:
                visual_label_raw = scene.get("visual_subject") or meta.get("title") or topic
                visual_subject_label = clean_visual_subject(visual_label_raw, fallback_topic=topic)

            if formatted_date:
                source_line = f"{base_attr} · {formatted_date}"
            else:
                source_line = base_attr

            scene_start = float(timing.get("start", 0.0))
            scene_dur = float(timing.get("duration", 5.0))
            display_dur = min(2.8, max(1.5, scene_dur - 0.3))

            source_attributions.append({
                "scene_id": timing.get("scene_id"),
                "start": scene_start,
                "end": scene_start + display_dur,
                "duration": scene_dur,
                "subject": visual_subject_label,
                "source": source_line,
                "text": f"{visual_subject_label} | {source_line}" if visual_subject_label else source_line,
                "date": formatted_date,
                "is_primary": meta.get("is_primary_discovery", False)
            })

    return source_attributions
