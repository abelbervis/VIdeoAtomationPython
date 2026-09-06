"""
NASA Real-time Trending Discoveries & Media Feeds.
Fetches the latest official discoveries from NASA APOD (Astronomy Picture of the Day)
and the NASA Image and Video Library.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from config import NASA_API_KEY, NASA_IMAGE_API_BASE


class NASATrendsProvider:
    """Client for fetching real-time astronomy news and discoveries from official NASA APIs."""

    def __init__(self, api_key: str = NASA_API_KEY, image_base_url: str = NASA_IMAGE_API_BASE):
        self.api_key = api_key if api_key and api_key != "DEMO_KEY" else "DEMO_KEY"
        self.image_base_url = image_base_url.rstrip("/")

    def fetch_apod_recent(self, count: int = 8) -> List[Dict[str, Any]]:
        """
        Fetch recent Astronomy Picture of the Day (APOD) entries.
        Includes high-resolution official imagery/videos and explanations
        written by professional astronomers.
        """
        candidates: List[Dict[str, Any]] = []
        # Attempt 1: Fetch recent date range (last 7 days)
        try:
            today = datetime.utcnow().date()
            start_date = today - timedelta(days=7)
            url = f"https://api.nasa.gov/planetary/apod?api_key={self.api_key}&start_date={start_date}&end_date={today}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "NASA-Shorts-Generator/1.0 (Science Education)"}
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception:
            data = None

        # Attempt 2: Fallback to random count if date range returns empty or fails
        if not data or not isinstance(data, list):
            try:
                url = f"https://api.nasa.gov/planetary/apod?api_key={self.api_key}&count={count}"
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "NASA-Shorts-Generator/1.0 (Science Education)"}
                )
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                print(f"  ⚠️ Error al consultar NASA APOD ({e}). Usando búsqueda en NASA Library...")
                data = []

        if isinstance(data, list):
            for item in reversed(data):
                title = (item.get("title") or "").strip()
                explanation = (item.get("explanation") or "").strip()
                if not title or len(explanation) < 40:
                    continue

                date_str = item.get("date", "")
                media_type = item.get("media_type", "image")
                media_url = item.get("hdurl") or item.get("url")
                copyright_val = (item.get("copyright") or "").strip().replace("\n", " ")
                credit_val = copyright_val if copyright_val else "NASA / APOD"

                candidates.append({
                    "id": f"apod_{date_str or title[:15]}",
                    "title": title,
                    "source": "NASA APOD (Astronomy Picture of the Day)",
                    "date": date_str,
                    "scientific_text": explanation,
                    "media_type": media_type,
                    "media_url": media_url,
                    "credit": credit_val,
                    "keywords": [title.lower(), "space", "astronomy"]
                })

        return candidates

    def fetch_library_discoveries(self, query: str = "webb discovery", limit: int = 6) -> List[Dict[str, Any]]:
        """
        Query NASA Image and Video Library for high-impact cosmic discoveries.
        """
        candidates: List[Dict[str, Any]] = []
        try:
            params = {
                "q": query,
                "media_type": "video,image",
                "page": 1,
                "page_size": limit
            }
            url = f"{self.image_base_url}/search?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "NASA-Shorts-Generator/1.0 (Science Education)"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                payload = json.loads(resp.read().decode("utf-8"))

            items = payload.get("collection", {}).get("items", [])
            for item in items:
                data_list = item.get("data", [])
                if not data_list:
                    continue
                d = data_list[0]
                nasa_id = d.get("nasa_id", "")
                title = (d.get("title") or "").strip()
                desc = (d.get("description") or "").strip()

                if not title or len(desc) < 30:
                    continue

                media_type = d.get("media_type", "image")
                date_created = d.get("date_created", "")[:10]
                center = (d.get("center") or "NASA").strip()
                photographer = (d.get("photographer") or d.get("secondary_creator") or "").strip()
                credit_val = f"NASA / {center}" if center else "NASA"
                if photographer and photographer.lower() != center.lower():
                    credit_val = f"{credit_val} ({photographer})"

                raw_keywords = d.get("keywords") or []
                if isinstance(raw_keywords, str):
                    raw_keywords = [raw_keywords]

                candidates.append({
                    "id": f"nasa_{nasa_id}",
                    "title": title,
                    "source": "NASA Image & Video Library",
                    "date": date_created,
                    "scientific_text": desc,
                    "media_type": media_type,
                    "nasa_id": nasa_id,
                    "center": center,
                    "credit": credit_val,
                    "keywords": [k for k in raw_keywords if isinstance(k, str)][:5]
                })
        except Exception as e:
            print(f"  ⚠️ Error al consultar NASA Image Library ({e})")

        return candidates

    def get_trending_candidates(self, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Combine multiple NASA feeds (APOD + latest missions & telescopes).
        Returns a rich list of official discovery candidates with full scientific summaries.
        """
        all_candidates: List[Dict[str, Any]] = []
        seen_titles = set()

        # 1. Fetch APOD entries (high quality daily astronomy discoveries)
        apod_items = self.fetch_apod_recent(count=min(limit, 8))
        for item in apod_items:
            key = item["title"].lower()
            if key not in seen_titles:
                seen_titles.add(key)
                all_candidates.append(item)

        # 2. Query NASA Library for James Webb & high-impact mission discoveries
        queries = ["James Webb telescope discovery", "solar flare storm aurora", "black hole event horizon"]
        for q in queries:
            if len(all_candidates) >= limit:
                break
            lib_items = self.fetch_library_discoveries(query=q, limit=4)
            for item in lib_items:
                key = item["title"].lower()
                if key not in seen_titles:
                    seen_titles.add(key)
                    all_candidates.append(item)

        # 3. Fail-safe curated NASA discoveries if both APIs were unreachable/rate-limited
        if not all_candidates:
            all_candidates = [
                {
                    "id": "nasa_curated_cme",
                    "title": "Solar Storm and Earth's Magnetic Shield",
                    "source": "NASA Heliophysics Division",
                    "date": "2024-05-10",
                    "scientific_text": "Coronal mass ejections (CMEs) are massive clouds of solar plasma drenched with magnetic field lines that are ejected from the Sun into interplanetary space. When a CME strikes Earth's magnetosphere, it can trigger severe geomagnetic storms, creating auroras down to mid-latitudes and inducing electrical currents that challenge global power grids.",
                    "media_type": "video",
                    "keywords": ["solar storm", "coronal mass ejection", "aurora", "earth magnetosphere"]
                },
                {
                    "id": "nasa_curated_jwst",
                    "title": "James Webb Deep Field Cosmic Dawn",
                    "source": "NASA James Webb Space Telescope",
                    "date": "2023-11-15",
                    "scientific_text": "Webb's powerful infrared gaze pierced through cosmic dust clouds to reveal galaxies formed just a few hundred million years after the Big Bang. These ancient star clusters possess far more mass and maturity than previously predicted by standard cosmological models, challenging our understanding of early galaxy evolution.",
                    "media_type": "image",
                    "keywords": ["james webb", "first galaxies", "infrared astronomy", "deep space"]
                },
                {
                    "id": "nasa_curated_europa",
                    "title": "Ocean Under Europa's Frozen Crust",
                    "source": "NASA Planetary Science",
                    "date": "2024-03-22",
                    "scientific_text": "Jupiter's moon Europa hides a global salty ocean beneath an icy crust kilometers thick. Measurements from NASA spacecraft indicate tidal heating keeps this hidden ocean warm and liquid, potentially hosting volcanic hydrothermal vents and the chemical ingredients necessary for extraterrestrial microbial life.",
                    "media_type": "image",
                    "keywords": ["europa", "jupiter moon", "alien ocean", "extraterrestrial life"]
                }
            ]

        return all_candidates[:limit]
