"""
Pexels Official Media Provider.
Queries the official Pexels API (api.pexels.com) for high-quality stock videos and photos.
Optimized for vertical 9:16 portrait orientation for YouTube Shorts, Reels, and TikTok.
Includes full photographer credits and license tracking.
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from config import PEXELS_API_KEY, PEXELS_API_BASE, ASSETS_DIR
from utils.files import download_file, save_json

PEXELS_LICENSE_NOTE = (
    "Pexels License: All photos and videos on Pexels are free to use. "
    "Attribution is not required, but giving credit to the photographer or Pexels is appreciated."
)


class PexelsProvider:
    """Official Pexels Video & Photo API Client."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = PEXELS_API_BASE):
        self.api_key = (api_key or PEXELS_API_KEY or "").strip()
        self.base_url = base_url.rstrip("/")

    def is_configured(self) -> bool:
        """Check if a valid Pexels API key is present."""
        return bool(self.api_key and len(self.api_key) > 10)

    def _get_headers(self) -> Dict[str, str]:
        """HTTP headers required for Pexels API authentication."""
        return {
            "Authorization": self.api_key,
            "User-Agent": "NASA-Shorts-Generator/1.0 (Educational Video Creator)"
        }

    def search_videos(
        self,
        query: str,
        orientation: Optional[str] = "portrait",
        per_page: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Search for videos on Pexels.
        Tries portrait orientation first (ideal for 9:16 shorts), falls back to any orientation.
        """
        if not self.is_configured():
            return []

        results = self._query_videos(query, orientation=orientation, per_page=per_page)
        # If no results with portrait, search without orientation constraint
        if not results and orientation:
            results = self._query_videos(query, orientation=None, per_page=per_page)
        return results

    def _query_videos(
        self,
        query: str,
        orientation: Optional[str] = None,
        per_page: int = 15
    ) -> List[Dict[str, Any]]:
        """Execute video search HTTP request."""
        params: Dict[str, Any] = {
            "query": query,
            "per_page": per_page
        }
        if orientation:
            params["orientation"] = orientation

        url = f"{self.base_url}/videos/search?{urllib.parse.urlencode(params)}"

        try:
            req = urllib.request.Request(url, headers=self._get_headers())
            with urllib.request.urlopen(req, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))

            videos = payload.get("videos", [])
            parsed = []
            for v in videos:
                user = v.get("user", {}) or {}
                parsed.append({
                    "id": v.get("id"),
                    "title": f"Pexels Video {v.get('id')}",
                    "media_type": "video",
                    "width": v.get("width", 0),
                    "height": v.get("height", 0),
                    "duration": v.get("duration", 0),
                    "url": v.get("url", ""),
                    "image": v.get("image", ""),
                    "photographer": user.get("name", "Pexels Creator"),
                    "photographer_url": user.get("url", ""),
                    "video_files": v.get("video_files", []),
                    "license": PEXELS_LICENSE_NOTE
                })
            return parsed
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("  ❌ Pexels API Authentication Error (401): Invalid or expired PEXELS_API_KEY.")
            else:
                print(f"  ⚠️ Pexels video search error HTTP {e.code} for '{query}': {e.reason}")
            return []
        except Exception as e:
            print(f"  ⚠️ Error querying Pexels videos for '{query}': {e}")
            return []

    def search_photos(
        self,
        query: str,
        orientation: Optional[str] = "portrait",
        per_page: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Search for photos on Pexels.
        Tries portrait orientation first, falls back to any orientation.
        """
        if not self.is_configured():
            return []

        results = self._query_photos(query, orientation=orientation, per_page=per_page)
        if not results and orientation:
            results = self._query_photos(query, orientation=None, per_page=per_page)
        return results

    def _query_photos(
        self,
        query: str,
        orientation: Optional[str] = None,
        per_page: int = 15
    ) -> List[Dict[str, Any]]:
        """Execute photo search HTTP request."""
        params: Dict[str, Any] = {
            "query": query,
            "per_page": per_page
        }
        if orientation:
            params["orientation"] = orientation

        url = f"{self.base_url}/v1/search?{urllib.parse.urlencode(params)}"

        try:
            req = urllib.request.Request(url, headers=self._get_headers())
            with urllib.request.urlopen(req, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))

            photos = payload.get("photos", [])
            parsed = []
            for p in photos:
                title = p.get("alt") or f"Pexels Photo {p.get('id')}"
                parsed.append({
                    "id": p.get("id"),
                    "title": title,
                    "media_type": "image",
                    "width": p.get("width", 0),
                    "height": p.get("height", 0),
                    "url": p.get("url", ""),
                    "photographer": p.get("photographer", "Pexels Creator"),
                    "photographer_url": p.get("photographer_url", ""),
                    "src": p.get("src", {}),
                    "license": PEXELS_LICENSE_NOTE
                })
            return parsed
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("  ❌ Pexels API Authentication Error (401): Invalid or expired PEXELS_API_KEY.")
            else:
                print(f"  ⚠️ Pexels photo search error HTTP {e.code} for '{query}': {e.reason}")
            return []
        except Exception as e:
            print(f"  ⚠️ Error querying Pexels photos for '{query}': {e}")
            return []

    def select_best_video_file(self, video_files: List[Dict[str, Any]]) -> Optional[str]:
        """
        Choose the best MP4 video stream URL for vertical short format.
        Favors vertical (height >= width) and HD (1080p/720p) quality.
        """
        if not video_files:
            return None

        mp4_candidates = [
            vf for vf in video_files
            if vf.get("file_type") == "video/mp4" or (vf.get("link", "").lower().split("?")[0].endswith(".mp4"))
        ]
        if not mp4_candidates:
            mp4_candidates = video_files

        def score_candidate(vf: Dict[str, Any]) -> int:
            w = vf.get("width") or 0
            h = vf.get("height") or 0
            quality = (vf.get("quality") or "").lower()
            score = 0

            # Strongly prefer portrait vertical videos (9:16)
            if h > w and h >= 1080:
                score += 2000
            elif h > w and h >= 720:
                score += 1500
            elif h > w:
                score += 1000

            # Quality bonus
            if quality == "hd":
                score += 300
            elif quality == "uhd":
                score += 250
            elif quality == "sd":
                score += 100

            # Resolution proximity
            score += min(h, 1920)
            return score

        sorted_candidates = sorted(mp4_candidates, key=score_candidate, reverse=True)
        return sorted_candidates[0].get("link")

    def select_best_photo_url(self, src: Dict[str, str]) -> Optional[str]:
        """Pick optimal resolution image URL (preferring portrait or large2x)."""
        if not src:
            return None
        for key in ["portrait", "large2x", "original", "large", "medium"]:
            if src.get(key):
                return src[key]
        # First available value in dict
        for v in src.values():
            if v:
                return v
        return None

    def fetch_scene_asset(
        self,
        scene_idx: int,
        keywords: List[str],
        preferred_type: str = "video",
        save_dir: Path = ASSETS_DIR
    ) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
        """
        Search and download the best matching Pexels asset for a scene.
        Seamless drop-in replacement for NASAProvider.fetch_scene_asset.
        """
        if not self.is_configured():
            print("  ⚠️ PexelsProvider: No PEXELS_API_KEY configured. Cannot query Pexels.")
            return None, None

        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Build candidate search queries
        queries: List[str] = []
        if len(keywords) > 1:
            queries.append(" ".join(keywords[:2]))
        queries.extend(keywords)

        for query in queries:
            print(f"  🔍 Querying Pexels library for '{query}'...")

            # 1. Try preferred type (video first)
            if preferred_type == "video":
                video_items = self.search_videos(query, orientation="portrait", per_page=8)
                for item in video_items:
                    best_url = self.select_best_video_file(item.get("video_files", []))
                    if not best_url:
                        continue

                    dest_file = save_dir / f"scene_{scene_idx:02d}.mp4"
                    meta_file = save_dir / f"scene_{scene_idx:02d}.json"

                    print(f"  ⬇️ Downloading Pexels video: '{item['title']}' by {item['photographer']}...")
                    success = download_file(best_url, dest_file)
                    if success:
                        meta = {
                            "scene_index": scene_idx,
                            "provider": "pexels",
                            "title": item["title"],
                            "asset_id": item["id"],
                            "media_type": "video",
                            "source_url": best_url,
                            "pexels_page_url": item["url"],
                            "description": f"Video by {item['photographer']} on Pexels",
                            "photographer_or_credit": item["photographer"],
                            "photographer_url": item["photographer_url"],
                            "license": item["license"],
                            "local_file": str(dest_file.name)
                        }
                        save_json(meta, meta_file)
                        return dest_file, meta

            # 2. Try photos (if preferred_type was image or video search had no hits)
            photo_items = self.search_photos(query, orientation="portrait", per_page=8)
            for item in photo_items:
                best_url = self.select_best_photo_url(item.get("src", {}))
                if not best_url:
                    continue

                dest_file = save_dir / f"scene_{scene_idx:02d}.jpg"
                meta_file = save_dir / f"scene_{scene_idx:02d}.json"

                print(f"  ⬇️ Downloading Pexels photo: '{item['title']}' by {item['photographer']}...")
                success = download_file(best_url, dest_file)
                if success:
                    meta = {
                        "scene_index": scene_idx,
                        "provider": "pexels",
                        "title": item["title"],
                        "asset_id": item["id"],
                        "media_type": "image",
                        "source_url": best_url,
                        "pexels_page_url": item["url"],
                        "description": f"Photo by {item['photographer']} on Pexels",
                        "photographer_or_credit": item["photographer"],
                        "photographer_url": item["photographer_url"],
                        "license": item["license"],
                        "local_file": str(dest_file.name)
                    }
                    save_json(meta, meta_file)
                    return dest_file, meta

        print(f"  ❌ Could not retrieve Pexels asset for scene {scene_idx}.")
        return None, None
