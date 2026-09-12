"""
NASA API Client.
Handles low-level HTTP network calls to the official NASA Image and Video Library (images-api.nasa.gov).
"""

import json
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from config import NASA_IMAGE_API_BASE

USER_AGENT = "NASA-Shorts-Generator/1.0 (Science Education; Educational Fair Use)"


class NASAClient:
    """Handles raw HTTP queries to the official NASA media library with resilient DNS retry and fallback."""

    def __init__(self, base_url: str = NASA_IMAGE_API_BASE):
        self.base_url = base_url.rstrip("/")
        self._search_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._consecutive_dns_failures: int = 0
        self._offline_mode: bool = False

    def raw_search(
        self,
        query: str,
        media_types: Optional[List[str]] = None,
        page_size: int = 15,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Execute raw search against NASA Image and Video Library API.
        Returns the raw items list from collection.items.
        Includes automatic retry for transient DNS/connection resolution errors.
        """
        if self._offline_mode:
            return []

        if not media_types:
            media_types = ["video", "image"]

        cache_key = f"{query.strip().lower()}:{','.join(sorted(media_types))}:{page_size}:{page}"
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]

        params = {
            "q": query.strip(),
            "media_type": ",".join(media_types),
            "page": page,
            "page_size": page_size
        }
        url = f"{self.base_url}/search?{urllib.parse.urlencode(params)}"

        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=12) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                items = payload.get("collection", {}).get("items", [])
                self._search_cache[cache_key] = items
                self._consecutive_dns_failures = 0
                return items
            except Exception as e:
                err_str = str(e).lower()
                is_dns = (
                    "name resolution" in err_str
                    or "errno -3" in err_str
                    or "errno -2" in err_str
                    or "not known" in err_str
                    or "gaierror" in str(type(e)).lower()
                )

                if attempt < max_retries and is_dns:
                    time.sleep(1.0 * (attempt + 1))
                    continue

                if is_dns:
                    self._consecutive_dns_failures += 1
                    if self._consecutive_dns_failures >= 2:
                        if not self._offline_mode:
                            print("  ℹ️ Conexión DNS con NASA API no disponible temporalmente. Conmutando automáticamente a proveedores alternativos (Pexels / Pixabay / IA FLUX)...")
                            self._offline_mode = True
                    else:
                        print(f"  ⚠️ Error de resolución DNS con NASA API para '{query}'. Reintentando o usando alternativas...")
                else:
                    print(f"  ⚠️ Error de conexión con NASA API para '{query}': {e}")
                return []

        return []

    def get_asset_manifest_urls(self, nasa_id: str) -> List[str]:
        """Fetch all direct media URLs from the asset manifest (collection.json) with retries."""
        if self._offline_mode:
            return []

        clean_id = urllib.parse.quote(str(nasa_id).strip(), safe="")
        url = f"{self.base_url}/asset/{clean_id}"

        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=12) as response:
                    payload = json.loads(response.read().decode("utf-8"))

                items = payload.get("collection", {}).get("items", [])
                urls = [item.get("href") for item in items if item.get("href")]
                # Ensure HTTPS and sanitized percent-encoded URLs (e.g. spaces in paths)
                from utils.files import sanitize_url
                self._consecutive_dns_failures = 0
                return [sanitize_url(u.replace("http://", "https://")) for u in urls]
            except Exception as e:
                err_str = str(e).lower()
                is_dns = (
                    "name resolution" in err_str
                    or "errno -3" in err_str
                    or "errno -2" in err_str
                    or "not known" in err_str
                    or "gaierror" in str(type(e)).lower()
                )

                if attempt < max_retries and is_dns:
                    time.sleep(1.0 * (attempt + 1))
                    continue

                if is_dns:
                    self._consecutive_dns_failures += 1
                    if self._consecutive_dns_failures >= 2:
                        self._offline_mode = True
                else:
                    print(f"  ⚠️ Error obteniendo URLs para '{nasa_id}': {e}")
                return []

        return []

    def select_best_resolution_url(self, urls: List[str], media_type: str) -> Optional[str]:
        """
        Picks optimal resolution for vertical video rendering (1080p/720p MP4 or high-res JPG/PNG).
        """
        if not urls:
            return None

        if media_type == "video":
            mp4_urls = [u for u in urls if u.lower().endswith(".mp4")]
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
