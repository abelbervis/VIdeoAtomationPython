"""
NASA Official Media Provider.
Coordinates NASA API queries, authentic observational filtering, and media downloads.
Decoupled into:
  - NASAClient: Network and HTTP requests
  - NASAFilterRanker: Content filtering, PR exclusion, and scientific center ranking
  - NASADownloader: Asset downloading and attribution metadata packaging
"""

import re
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config import ASSETS_DIR, NASA_IMAGE_API_BASE
from providers.nasa_client import NASAClient
from providers.nasa_downloader import NASA_PUBLIC_LICENSE_NOTE, NASADownloader
from providers.nasa_filter import NASAFilterRanker
from utils.files import download_file, save_json

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
    "eclipse": "eclipse"
}


def normalize_search_term(term: str) -> str:
    """Translate basic Spanish astronomy terms if needed for official NASA library queries."""
    term_clean = term.strip().lower()
    return SPANISH_TO_ENGLISH_ASTRONOMY.get(term_clean, term)


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
        """
        Query the NASA Library and return filtered, science-ranked candidates as dictionaries.
        Excludes PR, logos, and low-quality concepts.
        """
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
            # Remove punctuation except hyphens
            cleaned = re.sub(r'[^\w\s\-]', '', cleaned).strip()
            # Skip if contains banned keywords
            words_lower = cleaned.lower().split()
            if any(b in words_lower for b in banned_words):
                continue
            # Keep atomic (max 3 words per query)
            if len(words_lower) > 3:
                cleaned = " ".join(words_lower[:3])
            if cleaned and cleaned.lower() not in [c.lower() for c in clean_kws]:
                clean_kws.append(cleaned)

        # If keywords are empty, attempt to translate visual_subject or topic_anchor
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

        # Limit to at most 2 clean, atomic queries per scene
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
        """
        Search and download the highest-ranking scientific asset for a scene.
        Limits queries to 2 atomic terms to prevent API hammering and timeouts.
        """
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        queries = self._build_search_queries(keywords, topic_anchor, visual_subject)
        if not queries:
            return None, None

        # 1. Search for video first across the atomic queries
        for query in queries:
            print(f"  🔍 Querying NASA library for '{query}' ({preferred_type})...")
            raw_items = self.client.raw_search(query, media_types=[preferred_type], page_size=8)
            candidates = self.ranker.filter_and_rank(raw_items, topic_anchor=topic_anchor or query)

            for cand in candidates:
                dest_file, meta = self.downloader.download_candidate(cand, scene_idx, save_dir, filename_suffix=filename_suffix)
                if dest_file and meta:
                    return dest_file, meta

        # 2. If video not found, attempt ONE image query with the top keyword
        if preferred_type == "video" and queries:
            top_query = queries[0]
            print(f"    ↳ No video found in NASA for '{top_query}', trying still image...")
            raw_items = self.client.raw_search(top_query, media_types=["image"], page_size=6)
            candidates = self.ranker.filter_and_rank(raw_items, topic_anchor=topic_anchor or top_query)

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
        """
        Download authentic official media asset from the NASA discovery event for Scene 1.
        """
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

        # Attempt 1: Direct media_url (APOD high-resolution image or direct mp4)
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

        # Attempt 2: Direct NASA Library asset via nasa_id
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

        # Attempt 3: Query NASA Library using discovery title
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
    # Test runner for quick terminal debugging without rendering videos
    query_term = sys.argv[1] if len(sys.argv) > 1 else "nebulosa"
    print(f"\n🔬 Probando búsqueda en NASA para: '{query_term}'")
    provider = NASAProvider()
    results = provider.search(query_term, media_types=["image", "video"], page_size=10)

    print(f"Encontrados {len(results)} candidatos clasificados por calidad científica:")
    for i, r in enumerate(results[:5], 1):
        print(f"  [{i}] {r['title']}")
        print(f"      Centro: {r['center']} | Fecha: {r['date_created'][:10]} | Puntuación: {r.get('quality_score', 0):.1f}")
        print(f"      Tipo: {r['media_type']} | NASA ID: {r['nasa_id']}")
