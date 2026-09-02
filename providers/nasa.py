"""
NASA Official Media Provider.
Queries the official NASA Image and Video Library API (images-api.nasa.gov).
Downloads high-resolution videos and images with complete metadata and license tracking.
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from config import NASA_IMAGE_API_BASE, ASSETS_DIR
from utils.files import download_file, save_json

NASA_PUBLIC_LICENSE_NOTE = (
    "Public Domain - NASA Content Policy: NASA material is generally not copyrighted "
    "and may be used for educational or informational purposes without explicit permission."
)


class NASAProvider:
    """Official NASA Image & Video Library Client."""

    def __init__(self, base_url: str = NASA_IMAGE_API_BASE):
        self.base_url = base_url.rstrip("/")

    def search(
        self,
        query: str,
        media_types: List[str] = ["video", "image"],
        page_size: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Query the NASA Image and Video Library.
        Returns a list of parsed resource metadata objects.
        """
        media_type_str = ",".join(media_types)
        params = {
            "q": query,
            "media_type": media_type_str,
            "page": 1,
            "page_size": page_size
        }
        url = f"{self.base_url}/search?{urllib.parse.urlencode(params)}"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "NASA-Shorts-Generator/1.0 (Science Education)"}
            )
            with urllib.request.urlopen(req, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))

            items = payload.get("collection", {}).get("items", [])
            results = []

            for item in items:
                data_list = item.get("data", [])
                if not data_list:
                    continue
                data = data_list[0]

                nasa_id = data.get("nasa_id")
                media_type = data.get("media_type")
                title = data.get("title", "NASA Space Visual")
                description = data.get("description", "")
                center = data.get("center", "NASA")
                date_created = data.get("date_created", "")
                photographer = data.get("photographer") or data.get("secondary_creator") or center

                # Thumbnail link if available
                thumb_url = None
                for link in item.get("links", []):
                    if link.get("rel") == "preview":
                        thumb_url = link.get("href")
                        break

                results.append({
                    "nasa_id": nasa_id,
                    "media_type": media_type,
                    "title": title,
                    "description": description[:300],
                    "center": center,
                    "photographer": photographer,
                    "date_created": date_created,
                    "manifest_url": item.get("href"),
                    "thumb_url": thumb_url,
                    "license": NASA_PUBLIC_LICENSE_NOTE
                })

            return results
        except Exception as e:
            print(f"  ⚠️ Error searching NASA API for '{query}': {e}")
            return []

    def get_asset_direct_urls(self, nasa_id: str) -> List[str]:
        """Fetch direct download links for an asset via manifest URL."""
        url = f"{self.base_url}/asset/{nasa_id}"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "NASA-Shorts-Generator/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))

            items = payload.get("collection", {}).get("items", [])
            urls = [item.get("href") for item in items if item.get("href")]
            return urls
        except Exception as e:
            print(f"  ⚠️ Error fetching asset manifest for '{nasa_id}': {e}")
            return []

    def select_best_url(self, urls: List[str], media_type: str) -> Optional[str]:
        """Pick optimal resolution file (preferring 1080p/720p MP4 or high-res JPG)."""
        if not urls:
            return None

        # Ensure HTTPS urls
        urls = [u.replace("http://", "https://") for u in urls]

        if media_type == "video":
            mp4_urls = [u for u in urls if u.lower().endswith(".mp4")]
            # Priority: medium or large (good balance of quality vs file size for shorts)
            for priority in ["~medium.mp4", "~orig.mp4", "~large.mp4", "~mobile.mp4", ".mp4"]:
                for u in mp4_urls:
                    if priority in u.lower():
                        return u
            return mp4_urls[0] if mp4_urls else None

        else:
            img_urls = [u for u in urls if u.lower().endswith((".jpg", ".jpeg", ".png"))]
            for priority in ["~large.jpg", "~orig.jpg", "~medium.jpg", ".jpg", ".png"]:
                for u in img_urls:
                    if priority in u.lower():
                        return u
            return img_urls[0] if img_urls else None

    def fetch_scene_asset(
        self,
        scene_idx: int,
        keywords: List[str],
        preferred_type: str = "video",
        save_dir: Path = ASSETS_DIR
    ) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
        """
        Search and download the best matching asset for a scene.
        Fallbacks to alternative keywords and image types automatically.
        """
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Build candidate search queries: combinations and individual keywords
        queries = []
        if len(keywords) > 1:
            queries.append(" ".join(keywords[:2]))
        queries.extend(keywords)
        # Broad astronomy fallbacks
        queries.extend(["space universe", "galaxy nebula", "solar system nasa", "earth orbit"])

        for query in queries:
            print(f"  🔍 Querying NASA library for '{query}'...")
            
            # 1. Try preferred type first
            items = self.search(query, media_types=[preferred_type], page_size=8)
            
            # 2. If no preferred type (e.g. video), fallback to image
            if not items and preferred_type == "video":
                print(f"    ↳ No video found for '{query}', falling back to images...")
                items = self.search(query, media_types=["image"], page_size=8)

            for candidate in items:
                nasa_id = candidate["nasa_id"]
                cand_type = candidate["media_type"]
                direct_urls = self.get_asset_direct_urls(nasa_id)
                best_url = self.select_best_url(direct_urls, cand_type)

                if not best_url:
                    continue

                ext = ".mp4" if cand_type == "video" else ".jpg"
                dest_file = save_dir / f"scene_{scene_idx:02d}{ext}"
                meta_file = save_dir / f"scene_{scene_idx:02d}.json"

                print(f"  ⬇️ Downloading NASA {cand_type}: '{candidate['title']}'...")
                success = download_file(best_url, dest_file)

                if success:
                    meta = {
                        "scene_index": scene_idx,
                        "provider": "nasa",
                        "title": candidate["title"],
                        "nasa_id": nasa_id,
                        "media_type": cand_type,
                        "source_url": best_url,
                        "description": candidate["description"],
                        "center": candidate["center"],
                        "photographer_or_credit": candidate["photographer"],
                        "date_created": candidate["date_created"],
                        "license": candidate["license"],
                        "local_file": str(dest_file.name)
                    }
                    save_json(meta, meta_file)
                    return dest_file, meta

        print(f"  ❌ Could not retrieve NASA asset for scene {scene_idx}.")
        return None, None
