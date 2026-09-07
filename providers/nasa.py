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
        topic_anchor: Optional[str],
        visual_subject: Optional[str],
        primary_title: Optional[str]
    ) -> List[str]:
        """Constructs prioritized search queries anchored to the celestial subject."""
        # 1. Clean keywords
        banned_words = {
            "nasa", "agency", "space agency", "headquarters", "scientist", "scientists",
            "laboratory", "meeting", "briefing", "logo", "meatball", "hallway", "office",
            "future", "concept", "illustration", "3d"
        }
        clean_kws = [k.strip() for k in keywords if k.strip() and not any(b in k.lower().split() for b in banned_words)]

        # 2. Derive topic anchor
        anchor = None
        if primary_title:
            p_clean = re.sub(r'^(A|An|The)\s+', '', primary_title, flags=re.I)
            p_clean = re.sub(r'\s*\([^)]*\)', '', p_clean)
            p_clean = re.sub(r'\s*-\s*(19|20)\d{2}.*$', '', p_clean)
            anchor = re.split(r'[:\-—]', p_clean)[0].strip()
            if len(anchor) > 28:
                anchor = " ".join(anchor.split()[:4])
        elif visual_subject:
            v_clean = re.sub(r'[^\w\s]', '', visual_subject).strip()
            if v_clean:
                anchor = v_clean
        elif topic_anchor:
            anchor = re.sub(r'[¡!¿?]', '', topic_anchor).strip()

        # Build query priority list
        queries = []
        if anchor:
            for kw in clean_kws[:2]:
                queries.append(f"{anchor} {kw}")
            queries.append(anchor)

        if len(clean_kws) > 1:
            queries.append(" ".join(clean_kws[:2]))
        queries.extend(clean_kws)

        # Cosmic astronomy fallback queries
        queries.extend([
            "deep space galaxy telescope",
            "astronomy nebula telescope",
            "cosmic stars astronomy",
            "earth orbit space night"
        ])
        return queries

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
        primary_asset_meta: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
        """
        Search and download the highest-ranking scientific asset for a scene.
        """
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        primary_title = primary_asset_meta.get("title") if primary_asset_meta else None
        queries = self._build_search_queries(keywords, topic_anchor, visual_subject, primary_title)

        for query in queries:
            print(f"  🔍 Querying NASA library for '{query}'...")

            # 1. Try preferred type (video/image)
            raw_items = self.client.raw_search(query, media_types=[preferred_type], page_size=10)
            candidates = self.ranker.filter_and_rank(raw_items, topic_anchor=topic_anchor or query)

            # 2. If no video found, fallback to high-res images
            if not candidates and preferred_type == "video":
                print(f"    ↳ No video found for '{query}', searching scientific images...")
                raw_items = self.client.raw_search(query, media_types=["image"], page_size=10)
                candidates = self.ranker.filter_and_rank(raw_items, topic_anchor=topic_anchor or query)

            # If candidates were filtered out due to illustration ban, allow fallback only if no items found
            if not candidates and raw_items:
                candidates = self.ranker.filter_and_rank(raw_items, topic_anchor=topic_anchor or query, allow_illustrations=True)

            for cand in candidates:
                dest_file, meta = self.downloader.download_candidate(cand, scene_idx, save_dir)
                if dest_file and meta:
                    return dest_file, meta

        # 3. If all searches fail and we have an authentic primary discovery visual, reuse it
        if primary_asset_file and primary_asset_file.exists() and primary_asset_meta:
            print(f"  ✨ Reusing verified authentic discovery visual for scene {scene_idx}: '{primary_asset_meta.get('title')}'")
            dest_file = save_dir / f"scene_{scene_idx:02d}{primary_asset_file.suffix}"
            shutil.copy2(primary_asset_file, dest_file)
            meta = dict(primary_asset_meta)
            meta["scene_index"] = scene_idx
            meta["local_file"] = str(dest_file.name)
            meta_file = save_dir / f"scene_{scene_idx:02d}.json"
            save_json(meta, meta_file)
            return dest_file, meta

        print(f"  ❌ Could not retrieve NASA asset for scene {scene_idx}.")
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
