"""
Pixabay Official Media Provider.
Queries the Pixabay API (pixabay.com/api) for high-quality stock videos, 3D CGI animations, and photos.
Ideal for cosmic simulations, space phenomena, and cinematic background loops.
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from config import PIXABAY_API_KEY, ASSETS_DIR
from utils.files import download_file, save_json

PIXABAY_API_BASE = "https://pixabay.com/api"
PIXABAY_LICENSE_NOTE = (
    "Pixabay Content License: Free to use for commercial and non-commercial purposes. "
    "Attribution is not required, but giving credit to the artist or Pixabay is appreciated."
)


class PixabayProvider:
    """Official Pixabay Video & Photo API Client."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = PIXABAY_API_BASE):
        raw_key = api_key if api_key is not None else PIXABAY_API_KEY
        self.api_key = str(raw_key or "").strip().strip("'\"").strip()
        self.base_url = (base_url or PIXABAY_API_BASE).rstrip("/")

    def is_configured(self) -> bool:
        """Check if a valid Pixabay API key is present."""
        if not self.api_key or len(self.api_key) < 15:
            return False
        placeholders = ["tu_clave", "your_key", "demo_key", "placeholder", "xxx", "your_pixabay_api_key"]
        if any(p in self.api_key.lower() for p in placeholders):
            return False
        return True

    @staticmethod
    def _optimize_query_for_pixabay(query: str) -> str:
        """
        Translates and adapts Spanish/general queries into high-match English keywords for Pixabay.
        """
        q = query.lower().strip()
        translations = {
            "agujeros negros": "black hole space",
            "agujero negro": "black hole space",
            "espacio profundo": "deep space nebula",
            "espacio": "space cosmos stars",
            "universo": "universe galaxy space",
            "galaxia": "galaxy space nebula",
            "nebulosa": "nebula stars space",
            "tierra": "planet earth space",
            "marte": "mars planet space",
            "luna": "moon starry sky",
            "sol": "sun solar flare space",
            "estrellas": "stars night sky galaxy",
            "cometa": "comet meteor space",
            "asteroide": "asteroid meteor space",
            "telescopio": "telescope astronomy starry sky"
        }

        for es_term, en_term in translations.items():
            if es_term in q:
                return en_term

        # Strip common Spanish articles
        stop_words = {"el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "en", "para", "por", "y"}
        tokens = [w for w in q.split() if w not in stop_words]
        return " ".join(tokens) if tokens else query

    def search_videos(
        self,
        query: str,
        orientation: Optional[str] = "portrait",
        per_page: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Search for videos on Pixabay.
        Returns a list of standardized video result dictionaries.
        """
        if not self.is_configured():
            return []

        search_q = self._optimize_query_for_pixabay(query)
        # Pixabay query length maximum is 100 characters
        search_q = search_q[:95]

        endpoint = f"{self.base_url}/videos/"
        params = {
            "key": self.api_key,
            "q": search_q,
            "video_type": "all",
            "per_page": min(max(per_page, 3), 50),
            "safesearch": "true"
        }

        url = f"{endpoint}?{urllib.parse.urlencode(params)}"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "NASA-Shorts-Generator/1.0 (Educational Video Creator)"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                hits = data.get("hits", [])
                formatted = []
                for hit in hits:
                    formatted.append({
                        "id": hit.get("id"),
                        "title": hit.get("tags") or search_q,
                        "url": hit.get("pageURL"),
                        "duration": hit.get("duration", 0),
                        "user": hit.get("user") or "Pixabay Contributor",
                        "user_id": hit.get("user_id"),
                        "type": hit.get("type", "film"),
                        "videos": hit.get("videos", {})
                    })
                return formatted
        except Exception as e:
            print(f"  ⚠️ Pixabay video search failed for '{search_q}': {e}")
            return []

    def search_photos(
        self,
        query: str,
        orientation: Optional[str] = "portrait",
        per_page: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Search for photos/images on Pixabay as a fallback.
        """
        if not self.is_configured():
            return []

        search_q = self._optimize_query_for_pixabay(query)[:95]
        endpoint = f"{self.base_url}/"
        params = {
            "key": self.api_key,
            "q": search_q,
            "image_type": "photo",
            "per_page": min(max(per_page, 3), 50),
            "safesearch": "true"
        }
        if orientation == "portrait":
            params["orientation"] = "vertical"
        elif orientation == "landscape":
            params["orientation"] = "horizontal"

        url = f"{endpoint}?{urllib.parse.urlencode(params)}"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "NASA-Shorts-Generator/1.0 (Educational Video Creator)"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                hits = data.get("hits", [])
                formatted = []
                for hit in hits:
                    formatted.append({
                        "id": hit.get("id"),
                        "title": hit.get("tags") or search_q,
                        "url": hit.get("pageURL"),
                        "user": hit.get("user") or "Pixabay Contributor",
                        "large_url": hit.get("largeImageURL") or hit.get("webformatURL"),
                        "width": hit.get("imageWidth", 0),
                        "height": hit.get("imageHeight", 0)
                    })
                return formatted
        except Exception as e:
            print(f"  ⚠️ Pixabay photo search failed for '{search_q}': {e}")
            return []

    def select_best_video_url(
        self,
        videos_dict: Dict[str, Any],
        orientation: Optional[str] = "portrait"
    ) -> Optional[str]:
        """
        Select optimal MP4 download URL from Pixabay video variants.
        Prioritizes 'large' (1080p) or 'medium' (720p).
        """
        if not videos_dict:
            return None

        # Check in quality order: large -> medium -> small
        for quality in ("large", "medium", "small"):
            v_info = videos_dict.get(quality)
            if v_info and isinstance(v_info, dict):
                url = v_info.get("url")
                if url and url.startswith("http"):
                    return url

        # Fallback to tiny if nothing else
        tiny = videos_dict.get("tiny")
        if tiny and isinstance(tiny, dict) and tiny.get("url"):
            return tiny.get("url")

        return None

    def fetch_scene_asset(
        self,
        scene_idx: int,
        keywords: List[str],
        preferred_type: str = "video",
        save_dir: Path = ASSETS_DIR,
        orientation: Optional[str] = "portrait",
        filename_suffix: str = ""
    ) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
        """
        Search and download the best matching Pixabay asset for a scene.
        Seamless drop-in replacement for NASAProvider / PexelsProvider.
        """
        if not self.is_configured():
            print("  ⚠️ PixabayProvider: No PIXABAY_API_KEY configured. Cannot query Pixabay.")
            return None, None

        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        queries: List[str] = []
        for kw in keywords:
            cleaned = str(kw).strip()
            if cleaned and cleaned not in queries:
                queries.append(cleaned)
        if len(keywords) > 1:
            combined = f"{keywords[0].strip()} {keywords[1].strip()}".strip()
            if combined and combined not in queries and len(combined.split()) <= 4:
                queries.append(combined)

        for query in queries:
            print(f"  🔍 Querying Pixabay library for '{query}'...")

            # 1. Try preferred type (video first)
            if preferred_type == "video":
                video_items = self.search_videos(query, orientation=orientation, per_page=8)
                for item in video_items:
                    best_url = self.select_best_video_url(item.get("videos", {}), orientation=orientation)
                    if not best_url:
                        continue

                    dest_file = save_dir / f"scene_{scene_idx:02d}{filename_suffix}.mp4"
                    meta_file = save_dir / f"scene_{scene_idx:02d}{filename_suffix}.json"

                    user_name = (item.get("user") or "").strip()
                    print(f"  ⬇️ Downloading Pixabay video: '{item['title']}' by {user_name}...")
                    success = download_file(best_url, dest_file)
                    if success:
                        attr_text = f"Pixabay | {user_name}" if user_name and len(user_name) <= 22 else "Pixabay"
                        meta = {
                            "scene_index": scene_idx,
                            "provider": "pixabay",
                            "title": item["title"],
                            "asset_id": item["id"],
                            "media_type": "video",
                            "source_url": best_url,
                            "pixabay_page_url": item["url"],
                            "description": f"Video by {user_name} on Pixabay",
                            "photographer_or_credit": user_name,
                            "attribution_text": attr_text,
                            "license": PIXABAY_LICENSE_NOTE,
                            "local_file": str(dest_file.name)
                        }
                        save_json(meta, meta_file)
                        return dest_file, meta

            # 2. Try photos (if preferred_type was image or video search had no hits)
            photo_items = self.search_photos(query, orientation=orientation, per_page=8)
            for item in photo_items:
                best_url = item.get("large_url")
                if not best_url:
                    continue

                dest_file = save_dir / f"scene_{scene_idx:02d}{filename_suffix}.jpg"
                meta_file = save_dir / f"scene_{scene_idx:02d}{filename_suffix}.json"

                user_name = (item.get("user") or "").strip()
                print(f"  ⬇️ Downloading Pixabay photo: '{item['title']}' by {user_name}...")
                success = download_file(best_url, dest_file)
                if success:
                    attr_text = f"Pixabay | {user_name}" if user_name and len(user_name) <= 22 else "Pixabay"
                    meta = {
                        "scene_index": scene_idx,
                        "provider": "pixabay",
                        "title": item["title"],
                        "asset_id": item["id"],
                        "media_type": "image",
                        "source_url": best_url,
                        "pixabay_page_url": item["url"],
                        "description": f"Photo by {user_name} on Pixabay",
                        "photographer_or_credit": user_name,
                        "attribution_text": attr_text,
                        "license": PIXABAY_LICENSE_NOTE,
                        "local_file": str(dest_file.name)
                    }
                    save_json(meta, meta_file)
                    return dest_file, meta

        print(f"  ❌ Could not retrieve Pixabay asset for scene {scene_idx}.")
        return None, None
