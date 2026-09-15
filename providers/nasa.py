"""
NASA Official Media Provider & Trends Engine.
Unified module containing:
  - NASAClient: Low-level network API client
  - NASACandidate & NASAFilterRanker: Scientific filtering & quality scoring
  - NASADownloader: Asset downloading & attribution generator
  - NASATrendsProvider: Real-time APOD & Library trend hunter
  - NASAProvider: High-level provider interface for scene asset collection
"""

import json
import re
import shutil
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config import (
    ASSETS_DIR,
    NASA_API_KEY,
    NASA_IMAGE_API_BASE,
)
from utils.files import download_file, save_json, sanitize_url

USER_AGENT = "NASA-Shorts-Generator/1.0 (Science Education; Educational Fair Use)"

NASA_PUBLIC_LICENSE_NOTE = (
    "Public Domain - NASA Content Policy: NASA material is generally not copyrighted "
    "and may be used for educational or informational purposes without explicit permission."
)

SPANISH_TO_ENGLISH_ASTRONOMY = {
    "nebulosa": "nebula",
    "agujero negro": "black hole",
    "agujeros negros": "black holes",
    "marte": "mars",
    "tierra": "earth",
    "luna": "moon",
    "sol": "sun",
    "estrella": "star",
    "estrellas": "stars",
    "galaxia": "galaxy",
    "galaxias": "galaxies",
    "universo": "universe",
    "jupiter": "jupiter",
    "saturno": "saturn",
    "espacio": "space",
    "astronauta": "astronaut",
    "telescopio": "telescope",
    "cometa": "comet",
    "asteroide": "asteroid",
    "eclipse": "eclipse",
}

# Institutional PR, executive portraits, and administrative non-space photos
BANNED_PR_PATTERNS = (
    "logo", "meatball", "worm logo", "headquarters", "press conference",
    "briefing", "administrator", "signing ceremony", "building", "center director",
    "auditorium", "award", "portrait", "swearing-in", "anniversary logo",
    "exhibit", "podium", "office", "patch", "reception", "panel discussion",
    "crew arrives", "standing at", "pose for a photo", "ribbon cutting",
    "keynote", "hallway", "personnel", "meeting room", "insignia",
    "seal of", "exterior of building", "hq", "conference", "symposium",
    "group photo", "group portrait", "stands with", "shakes hands", "certificate",
    "facility", "presentation ceremony", "speaks to", "speaks at",
    "official seal", "nasa seal", "nasa logo", "director", "ribbon-cutting",
    "signing of", "commemorative", "astronaut candidate class", "swearing in"
)

# Artificial CGI concepts, diagrams, and artistic illustrations
BAD_ART_TERMS = (
    "artist", "illustration", "concept", "rendering", "digital", "simulation",
    "schematic", "diagram", "3d model", "artist's concept", "artist concept",
    "computer model", "artistic rendering", "graphic representation", "cgi"
)

# Tier 1 Scientific Observational Centers
PRIORITY_CENTERS = {
    "STScI": 3.0,   # Space Telescope Science Institute (Hubble, JWST)
    "JPL": 2.5,     # Jet Propulsion Laboratory (Deep Space, Mars Rovers, Voyager)
    "GSFC": 2.0,    # Goddard Space Flight Center (Astrophysics, SDO, James Webb)
    "MSFC": 1.5,    # Marshall Space Flight Center
    "ARC": 1.5,     # Ames Research Center (Kepler, SOFIA)
}


def normalize_search_term(term: str) -> str:
    """Translate basic Spanish astronomy terms if needed for official NASA library queries."""
    term_clean = term.strip().lower()
    return SPANISH_TO_ENGLISH_ASTRONOMY.get(term_clean, term)


@dataclass
class NASACandidate:
    """Strongly typed model representing a candidate asset from the NASA API."""
    nasa_id: str
    media_type: str
    title: str
    description: str
    center: str
    photographer: str
    date_created: str
    manifest_url: Optional[str] = None
    thumb_url: Optional[str] = None
    quality_score: float = 0.0
    is_illustration: bool = False
    is_pr_photo: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for backward compatibility with existing components."""
        return {
            "nasa_id": self.nasa_id,
            "media_type": self.media_type,
            "title": self.title,
            "description": self.description,
            "center": self.center,
            "photographer": self.photographer,
            "date_created": self.date_created,
            "manifest_url": self.manifest_url,
            "thumb_url": self.thumb_url,
            "quality_score": self.quality_score,
            "is_illustration": self.is_illustration
        }


class NASAClient:
    """Handles raw HTTP queries to the official NASA media library."""

    def __init__(self, base_url: str = NASA_IMAGE_API_BASE):
        self.base_url = base_url.rstrip("/")
        self._search_cache: Dict[str, List[Dict[str, Any]]] = {}

    def raw_search(
        self,
        query: str,
        media_types: Optional[List[str]] = None,
        page_size: int = 15,
        page: int = 1
    ) -> List[Dict[str, Any]]:
        """Execute raw search against NASA Image and Video Library API."""
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

        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=12) as response:
                payload = json.loads(response.read().decode("utf-8"))
            items = payload.get("collection", {}).get("items", [])
            self._search_cache[cache_key] = items
            return items
        except Exception as e:
            print(f"  ⚠️ Error de conexión con NASA API para '{query}': {e}")
            return []

    def get_asset_manifest_urls(self, nasa_id: str) -> List[str]:
        """Fetch all direct media URLs from the asset manifest (collection.json)."""
        clean_id = urllib.parse.quote(str(nasa_id).strip(), safe="")
        url = f"{self.base_url}/asset/{clean_id}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=12) as response:
                payload = json.loads(response.read().decode("utf-8"))

            items = payload.get("collection", {}).get("items", [])
            urls = [item.get("href") for item in items if item.get("href")]
            return [sanitize_url(u.replace("http://", "https://")) for u in urls]
        except Exception as e:
            print(f"  ⚠️ Error obteniendo URLs para '{nasa_id}': {e}")
            return []

    def select_best_resolution_url(self, urls: List[str], media_type: str) -> Optional[str]:
        """Picks optimal resolution for vertical video rendering."""
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


class NASAFilterRanker:
    """Filters low-quality / PR assets and ranks candidates by scientific authenticity."""

    @staticmethod
    def parse_raw_item(raw_item: Dict[str, Any]) -> Optional[NASACandidate]:
        """Extracts structured NASACandidate from a raw NASA collection item."""
        data_list = raw_item.get("data", [])
        if not data_list:
            return None

        data = data_list[0]
        nasa_id = data.get("nasa_id", "")
        if not nasa_id:
            return None

        media_type = data.get("media_type", "image")
        title = data.get("title", "NASA Space Visual")
        description = data.get("description", "")
        center = data.get("center", "NASA")
        date_created = data.get("date_created", "")
        photographer = data.get("photographer") or data.get("secondary_creator") or center

        thumb_url = None
        for link in raw_item.get("links", []):
            if link.get("rel") == "preview":
                thumb_url = link.get("href")
                break

        title_lower = title.lower()
        desc_lower = (description or "").lower()

        is_pr = False
        if any(p in title_lower for p in BANNED_PR_PATTERNS):
            is_pr = True
        elif any(p in desc_lower[:250] for p in ["meatball logo", "worm logo", "press conference", "ribbon cutting", "podium", "signing ceremony"]):
            is_pr = True

        is_illustration = False
        if any(bad in title_lower for bad in BAD_ART_TERMS):
            is_illustration = True
        elif any(bad in desc_lower[:250] for bad in ["artist's concept", "artist concept", "artistic rendering", "3d model"]):
            is_illustration = True

        return NASACandidate(
            nasa_id=nasa_id,
            media_type=media_type,
            title=title,
            description=description[:350],
            center=center,
            photographer=photographer,
            date_created=date_created,
            manifest_url=raw_item.get("href"),
            thumb_url=thumb_url,
            is_pr_photo=is_pr,
            is_illustration=is_illustration
        )

    @classmethod
    def score_candidate(cls, candidate: NASACandidate, topic_anchor: Optional[str] = None) -> float:
        """Calculates an authenticity and relevance score."""
        score = 5.0
        score += PRIORITY_CENTERS.get(candidate.center, 0.0)

        year = candidate.date_created[:4] if len(candidate.date_created) >= 4 else "1900"
        if year.isdigit():
            y_int = int(year)
            if y_int >= 2022:
                score += 2.0
            elif y_int >= 2015:
                score += 1.0
            elif y_int < 1980:
                score -= 0.5

        if topic_anchor:
            anchor_words = [w.lower() for w in topic_anchor.split() if len(w) > 2]
            title_lower = candidate.title.lower()
            if any(w in title_lower for w in anchor_words):
                score += 2.5

        if candidate.is_illustration:
            score -= 4.0

        return score

    @classmethod
    def filter_and_rank(
        cls,
        raw_items: List[Dict[str, Any]],
        topic_anchor: Optional[str] = None,
        allow_illustrations: bool = False
    ) -> List[NASACandidate]:
        """Parses, filters, scores, and orders candidates from highest to lowest scientific quality."""
        candidates: List[NASACandidate] = []

        for item in raw_items:
            cand = cls.parse_raw_item(item)
            if not cand:
                continue

            if cand.is_pr_photo:
                continue

            if cand.is_illustration and not allow_illustrations:
                continue

            cand.quality_score = cls.score_candidate(cand, topic_anchor=topic_anchor)
            candidates.append(cand)

        candidates.sort(
            key=lambda c: (c.quality_score, c.date_created or "1900-01-01"),
            reverse=True
        )

        return candidates


class NASADownloader:
    """Manages downloading NASA media files and formatting standard attribution metadata."""

    def __init__(self, client: NASAClient):
        self.client = client

    @staticmethod
    def format_attribution(
        candidate_or_credit: str,
        center: Optional[str] = None,
        source: Optional[str] = None
    ) -> str:
        """Constructs a clean, compact attribution badge text (<= 30 characters)."""
        source_clean = (source or "NASA").lower()

        if "apod" in source_clean:
            if candidate_or_credit and candidate_or_credit.lower() not in ["nasa", "nasa / apod"] and len(candidate_or_credit) <= 24:
                return f"NASA APOD | {candidate_or_credit}"
            return "NASA APOD"

        if "webb" in source_clean or (center and "stsci" in center.lower()):
            return "NASA / ESA Webb"

        if center and center.upper() in ["JPL", "GSFC", "MSFC", "ARC"]:
            return f"NASA {center.upper()}"

        if candidate_or_credit and len(candidate_or_credit) <= 20 and candidate_or_credit.lower() != "nasa":
            return f"NASA | {candidate_or_credit}"

        return "NASA Library"

    def download_candidate(
        self,
        candidate: NASACandidate,
        scene_idx: int,
        save_dir: Path,
        filename_suffix: str = ""
    ) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
        """Retrieves direct download URLs, downloads optimal resolution, and saves metadata."""
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        direct_urls = self.client.get_asset_manifest_urls(candidate.nasa_id)
        best_url = self.client.select_best_resolution_url(direct_urls, candidate.media_type)

        if not best_url:
            return None, None

        ext = ".mp4" if candidate.media_type == "video" else ".jpg"
        dest_file = save_dir / f"scene_{scene_idx:02d}{filename_suffix}{ext}"
        meta_file = save_dir / f"scene_{scene_idx:02d}{filename_suffix}.json"

        print(f"  ⬇️ Descargando NASA {candidate.media_type} [{candidate.center}]: '{candidate.title}'...")
        success = download_file(best_url, dest_file)

        if success:
            attr_text = self.format_attribution(candidate.photographer, center=candidate.center)
            meta = {
                "scene_index": scene_idx,
                "provider": "nasa",
                "title": candidate.title,
                "nasa_id": candidate.nasa_id,
                "media_type": candidate.media_type,
                "source_url": best_url,
                "description": candidate.description,
                "center": candidate.center,
                "photographer_or_credit": candidate.photographer,
                "date_created": candidate.date_created,
                "attribution_text": attr_text,
                "quality_score": candidate.quality_score,
                "license": NASA_PUBLIC_LICENSE_NOTE,
                "local_file": str(dest_file.name)
            }
            save_json(meta, meta_file)
            return dest_file, meta

        return None, None


class NASATrendsProvider:
    """Client for fetching real-time astronomy news and discoveries from official NASA APIs."""

    def __init__(self, api_key: str = NASA_API_KEY, image_base_url: str = NASA_IMAGE_API_BASE):
        self.api_key = api_key if api_key and api_key != "DEMO_KEY" else "DEMO_KEY"
        self.image_base_url = image_base_url.rstrip("/")

    def fetch_apod_archive(
        self,
        target_date: Optional[str] = None,
        days_back: Optional[int] = None,
        random_archive: bool = False,
        count: int = 8
    ) -> List[Dict[str, Any]]:
        """Fetch Astronomy Picture of the Day (APOD) entries from NASA's archives."""
        candidates: List[Dict[str, Any]] = []
        data = None
        min_nasa_date = datetime(1995, 6, 16).date()
        today = datetime.utcnow().date()

        if target_date:
            try:
                clean_date = target_date.strip()[:10]
                parsed_dt = datetime.strptime(clean_date, "%Y-%m-%d").date()
                parsed_dt = max(min_nasa_date, min(today, parsed_dt))

                start_w = max(min_nasa_date, parsed_dt - timedelta(days=3))
                end_w = min(today, parsed_dt + timedelta(days=3))
                url = f"https://api.nasa.gov/planetary/apod?api_key={self.api_key}&start_date={start_w}&end_date={end_w}"
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": USER_AGENT}
                )
                with urllib.request.urlopen(req, timeout=7) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except Exception:
                try:
                    url = f"https://api.nasa.gov/planetary/apod?api_key={self.api_key}&date={target_date.strip()[:10]}"
                    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                    with urllib.request.urlopen(req, timeout=6) as resp:
                        res = json.loads(resp.read().decode("utf-8"))
                        data = [res] if isinstance(res, dict) else res
                except Exception as e:
                    print(f"  ⚠️ Error consultando fecha {target_date} en APOD ({e})")
                    data = None

        elif days_back and days_back > 0:
            try:
                end_date = max(min_nasa_date, today - timedelta(days=days_back))
                start_date = max(min_nasa_date, end_date - timedelta(days=7))
                url = f"https://api.nasa.gov/planetary/apod?api_key={self.api_key}&start_date={start_date}&end_date={end_date}"
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": USER_AGENT}
                )
                with urllib.request.urlopen(req, timeout=7) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                print(f"  ⚠️ Error consultando días pasados ({days_back}) en APOD ({e})")
                data = None

        elif random_archive:
            try:
                url = f"https://api.nasa.gov/planetary/apod?api_key={self.api_key}&count={count}"
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": USER_AGENT}
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                print(f"  ⚠️ Error consultando archivo histórico aleatorio ({e})")
                data = None

        if data is None or not isinstance(data, list):
            try:
                start_date = today - timedelta(days=7)
                url = f"https://api.nasa.gov/planetary/apod?api_key={self.api_key}&start_date={start_date}&end_date={today}"
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": USER_AGENT}
                )
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except Exception:
                data = None

        if not data or not isinstance(data, list):
            try:
                url = f"https://api.nasa.gov/planetary/apod?api_key={self.api_key}&count={count}"
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": USER_AGENT}
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
                if not title or len(explanation) < 35:
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

    def fetch_apod_recent(self, count: int = 8) -> List[Dict[str, Any]]:
        """Fetch recent Astronomy Picture of the Day (APOD) entries."""
        return self.fetch_apod_archive(count=count)

    def fetch_library_discoveries(
        self,
        query: str = "webb discovery",
        limit: int = 6,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query NASA Image and Video Library for high-impact cosmic discoveries."""
        candidates: List[Dict[str, Any]] = []
        try:
            params: Dict[str, Any] = {
                "q": query,
                "media_type": "video,image",
                "page": 1,
                "page_size": limit
            }
            if year_start:
                params["year_start"] = str(year_start)
            if year_end:
                params["year_end"] = str(year_end)

            url = f"{self.image_base_url}/search?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": USER_AGENT}
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

    def get_trending_candidates(
        self,
        limit: int = 8,
        target_date: Optional[str] = None,
        days_back: Optional[int] = None,
        random_archive: bool = False
    ) -> List[Dict[str, Any]]:
        """Combine multiple NASA feeds (APOD + latest or historical missions)."""
        all_candidates: List[Dict[str, Any]] = []
        seen_titles = set()

        apod_items = self.fetch_apod_archive(
            target_date=target_date,
            days_back=days_back,
            random_archive=random_archive,
            count=min(limit, 8)
        )
        for item in apod_items:
            key = item["title"].lower()
            if key not in seen_titles:
                seen_titles.add(key)
                all_candidates.append(item)

        target_year = None
        if target_date:
            try:
                target_year = int(target_date.strip()[:4])
            except Exception:
                target_year = None

        if random_archive:
            queries = [
                "Apollo 11 moon landing",
                "Hubble deep field original",
                "Voyager golden record interstellar",
                "Cassini Saturn rings closeup",
                "Pluto New Horizons flyby"
            ]
        elif target_year and target_year < 2020:
            queries = [
                f"space exploration discovery {target_year}",
                "Hubble Space Telescope discovery",
                "Mars rover mission space"
            ]
        else:
            queries = [
                "James Webb telescope discovery",
                "solar flare storm aurora",
                "black hole event horizon"
            ]

        for q in queries:
            if len(all_candidates) >= limit:
                break
            lib_items = self.fetch_library_discoveries(
                query=q,
                limit=3,
                year_start=target_year,
                year_end=target_year
            )
            for item in lib_items:
                key = item["title"].lower()
                if key not in seen_titles:
                    seen_titles.add(key)
                    all_candidates.append(item)

        if not all_candidates:
            all_candidates = [
                {
                    "id": "nasa_curated_cme",
                    "title": "Solar Storm and Earth's Magnetic Shield",
                    "source": "NASA Heliophysics Division",
                    "date": "2024-05-10",
                    "scientific_text": "Coronal mass ejections (CMEs) are massive clouds of solar plasma drenched with magnetic field lines that are ejected from the Sun into interplanetary space.",
                    "media_type": "video",
                    "keywords": ["solar storm", "coronal mass ejection", "aurora", "earth magnetosphere"]
                },
                {
                    "id": "nasa_curated_jwst",
                    "title": "James Webb Deep Field Cosmic Dawn",
                    "source": "NASA James Webb Space Telescope",
                    "date": "2023-11-15",
                    "scientific_text": "Webb's powerful infrared gaze pierced through cosmic dust clouds to reveal galaxies formed just a few hundred million years after the Big Bang.",
                    "media_type": "image",
                    "keywords": ["james webb", "first galaxies", "infrared astronomy", "deep space"]
                },
                {
                    "id": "nasa_curated_europa",
                    "title": "Ocean Under Europa's Frozen Crust",
                    "source": "NASA Planetary Science",
                    "date": "2024-03-22",
                    "scientific_text": "Jupiter's moon Europa hides a global salty ocean beneath an icy crust kilometers thick.",
                    "media_type": "image",
                    "keywords": ["europa", "jupiter moon", "alien ocean", "extraterrestrial life"]
                }
            ]

        return all_candidates[:limit]


class NASAProvider:
    """Official NASA Image & Video Library Service."""

    def __init__(self, base_url: str = NASA_IMAGE_API_BASE):
        self.client = NASAClient(base_url=base_url)
        self.ranker = NASAFilterRanker()
        self.downloader = NASADownloader(client=self.client)

    def search(
        self,
        query: str,
        media_types: Optional[List[str]] = None,
        page_size: int = 15
    ) -> List[Dict[str, Any]]:
        """Query the NASA Library and return filtered, science-ranked candidates as dictionaries."""
        effective_query = normalize_search_term(query)
        raw_items = self.client.raw_search(effective_query, media_types=media_types, page_size=page_size)
        candidates = self.ranker.filter_and_rank(raw_items, topic_anchor=effective_query)
        return [c.to_dict() for c in candidates]

    def get_asset_direct_urls(self, nasa_id: str) -> List[str]:
        """Fetch direct download links for an asset via manifest URL."""
        return self.client.get_asset_manifest_urls(nasa_id)

    def select_best_url(self, urls: List[str], media_type: str) -> Optional[str]:
        """Pick optimal resolution file for video rendering."""
        return self.client.select_best_resolution_url(urls, media_type)

    def _build_search_queries(
        self,
        keywords: List[str],
        topic_anchor: Optional[str] = None,
        visual_subject: Optional[str] = None,
        primary_title: Optional[str] = None
    ) -> List[str]:
        """Constructs concise, atomic search queries (maximum 2-3) anchored to visual keywords."""
        banned_words = {
            "nasa", "agency", "space agency", "headquarters", "scientist", "scientists",
            "laboratory", "meeting", "briefing", "logo", "meatball", "hallway", "office",
            "future", "concept", "illustration", "3d", "software", "photometry", "light curve",
            "data", "citizen", "astronomy software", "analysis"
        }
        clean_kws: List[str] = []
        for k in keywords:
            if not k or not str(k).strip():
                continue
            cleaned = str(k).strip()
            cleaned = re.sub(r'[^\w\s\-]', '', cleaned).strip()
            words_lower = cleaned.lower().split()
            if any(b in words_lower for b in banned_words):
                continue
            if len(words_lower) > 3:
                cleaned = " ".join(words_lower[:3])
            if cleaned and cleaned.lower() not in [c.lower() for c in clean_kws]:
                clean_kws.append(cleaned)

        if not clean_kws:
            subject_candidate = visual_subject or topic_anchor
            if subject_candidate:
                sub_clean = re.sub(r'[^\w\s\-]', '', str(subject_candidate)).strip().lower()
                for es, en in SPANISH_TO_ENGLISH_ASTRONOMY.items():
                    if es in sub_clean:
                        sub_clean = en
                        break
                words = sub_clean.split()
                if words and not any(b in words for b in banned_words):
                    clean_kws.append(" ".join(words[:2]))

        return clean_kws[:2]

    def fetch_scene_asset(
        self,
        scene_idx: int,
        keywords: List[str],
        preferred_type: str = "video",
        save_dir: Path = ASSETS_DIR,
        orientation: Optional[str] = None,
        topic_anchor: Optional[str] = None,
        visual_subject: Optional[str] = None,
        primary_asset_file: Optional[Path] = None,
        primary_asset_meta: Optional[Dict[str, Any]] = None,
        filename_suffix: str = ""
    ) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
        """Search and download the highest-ranking scientific asset for a scene."""
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        queries = self._build_search_queries(keywords, topic_anchor, visual_subject)
        if not queries:
            return None, None

        for query in queries:
            print(f"  🔍 Querying NASA library for '{query}' ({preferred_type})...")
            raw_items = self.client.raw_search(query, media_types=[preferred_type], page_size=8)
            candidates = self.ranker.filter_and_rank(raw_items, topic_anchor=topic_anchor or query)

            for cand in candidates:
                dest_file, meta = self.downloader.download_candidate(cand, scene_idx, save_dir, filename_suffix=filename_suffix)
                if dest_file and meta:
                    return dest_file, meta

        if preferred_type == "video" and queries:
            top_query = queries[0]
            print(f"    ↳ No video found in NASA for '{top_query}', trying still image...")
            raw_items = self.client.raw_search(top_query, media_types=["image"], page_size=6)
            candidates = self.ranker.filter_and_rank(raw_items, topic_anchor=top_query)

            for cand in candidates:
                dest_file, meta = self.downloader.download_candidate(cand, scene_idx, save_dir, filename_suffix=filename_suffix)
                if dest_file and meta:
                    return dest_file, meta

        print(f"  ❌ No relevant NASA visual found for scene {scene_idx}.")
        return None, None

    def fetch_primary_discovery_asset(
        self,
        discovery_meta: Dict[str, Any],
        scene_idx: int = 1,
        save_dir: Path = ASSETS_DIR,
        orientation: Optional[str] = None
    ) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
        """Download authentic official media asset from the NASA discovery event for Scene 1."""
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        title = discovery_meta.get("title", "NASA Discovery")
        media_type = discovery_meta.get("media_type", "image")
        media_url = discovery_meta.get("media_url")
        source = discovery_meta.get("source", "NASA")
        date_str = discovery_meta.get("date", "")
        credit = discovery_meta.get("credit") or discovery_meta.get("photographer") or "NASA"
        center = discovery_meta.get("center", "NASA")
        nasa_id = discovery_meta.get("nasa_id")

        print(f"\n🛰️  DESCARGANDO MEDIO OFICIAL DEL DESCUBRIMIENTO AL INICIO...")
        print(f"   Título:   '{title}'")
        print(f"   Tipo:     {media_type.upper()}")
        print(f"   Fuente:   {source}")
        if credit:
            print(f"   Crédito:  {credit}")

        attribution_text = self.downloader.format_attribution(credit, center=center, source=source)

        if media_url and not any(embed in media_url.lower() for embed in ["youtube.com", "youtu.be", "vimeo.com"]):
            ext = ".mp4" if media_type == "video" else ".jpg"
            dest_file = save_dir / f"scene_{scene_idx:02d}{ext}"
            meta_file = save_dir / f"scene_{scene_idx:02d}.json"

            print(f"  ⬇️ Descargando archivo multimedia original: {media_url[:75]}...")
            if download_file(media_url, dest_file):
                meta = {
                    "scene_index": scene_idx,
                    "provider": "nasa_official_discovery",
                    "is_primary_discovery": True,
                    "title": title,
                    "nasa_id": nasa_id or f"apod_{date_str}",
                    "media_type": media_type,
                    "source_url": media_url,
                    "source": source,
                    "description": discovery_meta.get("scientific_text", "")[:300],
                    "center": center,
                    "photographer_or_credit": credit,
                    "date_created": date_str,
                    "attribution_text": attribution_text,
                    "license": NASA_PUBLIC_LICENSE_NOTE,
                    "local_file": str(dest_file.name)
                }
                save_json(meta, meta_file)
                print(f"  ✅ Recurso oficial descargado con éxito: {dest_file.name} [{attribution_text}]")
                return dest_file, meta

        if nasa_id:
            direct_urls = self.client.get_asset_manifest_urls(nasa_id)
            best_url = self.client.select_best_resolution_url(direct_urls, media_type)
            if best_url:
                ext = ".mp4" if media_type == "video" else ".jpg"
                dest_file = save_dir / f"scene_{scene_idx:02d}{ext}"
                meta_file = save_dir / f"scene_{scene_idx:02d}.json"

                print(f"  ⬇️ Descargando activo oficial desde NASA Library (ID: {nasa_id})...")
                if download_file(best_url, dest_file):
                    meta = {
                        "scene_index": scene_idx,
                        "provider": "nasa_official_discovery",
                        "is_primary_discovery": True,
                        "title": title,
                        "nasa_id": nasa_id,
                        "media_type": media_type,
                        "source_url": best_url,
                        "source": source,
                        "description": discovery_meta.get("scientific_text", "")[:300],
                        "center": center,
                        "photographer_or_credit": credit,
                        "date_created": date_str,
                        "attribution_text": attribution_text,
                        "license": NASA_PUBLIC_LICENSE_NOTE,
                        "local_file": str(dest_file.name)
                    }
                    save_json(meta, meta_file)
                    print(f"  ✅ Recurso oficial descargado con éxito: {dest_file.name} [{attribution_text}]")
                    return dest_file, meta

        print(f"  🔍 Buscando en NASA Library por '{title}'...")
        raw_items = self.client.raw_search(title, media_types=[media_type], page_size=6)
        candidates = self.ranker.filter_and_rank(raw_items, topic_anchor=title)

        if not candidates and media_type == "video":
            raw_items = self.client.raw_search(title, media_types=["image"], page_size=6)
            candidates = self.ranker.filter_and_rank(raw_items, topic_anchor=title)

        if candidates:
            cand = candidates[0]
            dest_file, meta = self.downloader.download_candidate(cand, scene_idx, save_dir)
            if dest_file and meta:
                meta["provider"] = "nasa_official_discovery"
                meta["is_primary_discovery"] = True
                meta["source"] = source
                meta_file = save_dir / f"scene_{scene_idx:02d}.json"
                save_json(meta, meta_file)
                print(f"  ✅ Recurso oficial descargado con éxito: {dest_file.name} [{attribution_text}]")
                return dest_file, meta

        print("  ⚠️ No se pudo descargar el medio oficial específico al inicio; se buscará en el paso de escenas.")
        return None, None


if __name__ == "__main__":
    query_term = sys.argv[1] if len(sys.argv) > 1 else "nebulosa"
    print(f"\n🔬 Probando búsqueda en NASA para: '{query_term}'")
    provider = NASAProvider()
    results = provider.search(query_term, media_types=["image", "video"], page_size=10)

    print(f"Encontrados {len(results)} candidatos clasificados por calidad científica:")
    for i, r in enumerate(results[:5], 1):
        print(f"  [{i}] {r['title']}")
        print(f"      Centro: {r['center']} | Fecha: {r['date_created'][:10]} | Puntuación: {r.get('quality_score', 0):.1f}")
        print(f"      Tipo: {r['media_type']} | NASA ID: {r['nasa_id']}")
