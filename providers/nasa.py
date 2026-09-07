"""
NASA Official Media Provider.
Queries the official NASA Image and Video Library API (images-api.nasa.gov).
Downloads high-resolution videos and images with complete metadata and license tracking.
"""

import json
import re
import shutil
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
        Returns a list of parsed resource metadata objects, strictly filtering out
        institutional PR, logos, press conferences, and office photos.
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

                # Institutional / Logo / PR filtering
                title_lower = title.lower()
                desc_lower = (description or "").lower()
                if any(p in title_lower for p in BANNED_PR_PATTERNS):
                    continue
                if any(p in desc_lower[:250] for p in ["meatball logo", "worm logo", "press conference", "ribbon cutting", "podium", "signing ceremony"]):
                    continue

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
        save_dir: Path = ASSETS_DIR,
        orientation: Optional[str] = None,
        topic_anchor: Optional[str] = None,
        visual_subject: Optional[str] = None,
        primary_asset_file: Optional[Path] = None,
        primary_asset_meta: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
        """
        Search and download the best matching asset for a scene with strict topic relevance.
        Anchors candidate queries to the core celestial topic and filters out corporate/office assets.
        """
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        # 1. Clean keywords: eliminate corporate/office words
        banned_kws = {
            "nasa", "agency", "space agency", "headquarters", "scientist", "scientists",
            "laboratory", "meeting", "briefing", "logo", "meatball", "hallway", "office",
            "future", "concept", "illustration", "3d"
        }
        clean_kws = [k.strip() for k in keywords if k.strip() and not any(b in k.lower().split() for b in banned_kws)]

        # 2. Derive topic anchor
        anchor = None
        if primary_asset_meta and primary_asset_meta.get("title"):
            p_title = primary_asset_meta.get("title", "")
            p_clean = re.sub(r'^(A|An|The)\s+', '', p_title, flags=re.I)
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
            t_clean = re.sub(r'[¡!¿?]', '', topic_anchor).strip()
            anchor = t_clean

        # Build candidate search queries: anchored queries first, then clean keywords, then deep cosmic fallbacks
        queries = []
        if anchor:
            for kw in clean_kws[:2]:
                queries.append(f"{anchor} {kw}")
            queries.append(anchor)

        if len(clean_kws) > 1:
            queries.append(" ".join(clean_kws[:2]))
        queries.extend(clean_kws)

        # High-impact cosmic astronomy fallbacks (NEVER search bare "nasa" or "solar system nasa")
        queries.extend([
            "deep space galaxy telescope",
            "astronomy nebula telescope",
            "cosmic stars astronomy",
            "earth orbit space night"
        ])

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
                    photographer = candidate.get("photographer") or candidate.get("center") or "NASA"
                    if photographer and len(photographer) <= 24 and photographer.lower() != "nasa":
                        attr_text = f"NASA | {photographer}"
                    elif candidate.get("center") and len(candidate.get("center")) <= 12 and candidate.get("center").lower() != "nasa":
                        attr_text = f"NASA {candidate.get('center')}"
                    else:
                        attr_text = "NASA Library"

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
                        "attribution_text": attr_text,
                        "license": candidate["license"],
                        "local_file": str(dest_file.name)
                    }
                    save_json(meta, meta_file)
                    return dest_file, meta

        # 3. If all searches fail and we have an authentic primary discovery asset, reuse it
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
        Download the authentic official media asset from the NASA discovery/trending event
        at the very beginning of the pipeline.
        Tries:
        1. Direct APOD / NASA media_url if available.
        2. NASA Library manifest via nasa_id if available.
        3. Search NASA Library using exact discovery title or keywords.
        """
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

        title = discovery_meta.get("title", "NASA Discovery")
        media_type = discovery_meta.get("media_type", "image")
        media_url = discovery_meta.get("media_url")
        source = discovery_meta.get("source", "NASA")
        date_str = discovery_meta.get("date", "")
        credit = discovery_meta.get("credit") or discovery_meta.get("photographer") or "NASA"
        nasa_id = discovery_meta.get("nasa_id")

        print(f"\n🛰️  DESCARGANDO MEDIO OFICIAL DEL DESCUBRIMIENTO AL INICIO...")
        print(f"   Título:   '{title}'")
        print(f"   Tipo:     {media_type.upper()}")
        print(f"   Fuente:   {source}")
        if credit:
            print(f"   Crédito:  {credit}")

        # Determine attribution badge text (concise, <= 32 chars for mobile screen overlay)
        if "apod" in source.lower():
            if credit and credit.lower() not in ["nasa", "nasa / apod"] and len(credit) <= 24:
                attribution_text = f"NASA APOD | {credit}"
            else:
                attribution_text = "NASA APOD"
        elif "webb" in title.lower() or "webb" in source.lower():
            attribution_text = "NASA / ESA Webb"
        elif "hubble" in title.lower():
            attribution_text = "NASA / ESA Hubble"
        elif credit and len(credit) <= 24 and credit.lower() != "nasa":
            attribution_text = f"NASA | {credit}"
        else:
            attribution_text = "NASA Oficial"

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
                    "center": discovery_meta.get("center", "NASA"),
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
            direct_urls = self.get_asset_direct_urls(nasa_id)
            best_url = self.select_best_url(direct_urls, media_type)
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
                        "center": discovery_meta.get("center", "NASA"),
                        "photographer_or_credit": credit,
                        "date_created": date_str,
                        "attribution_text": attribution_text,
                        "license": NASA_PUBLIC_LICENSE_NOTE,
                        "local_file": str(dest_file.name)
                    }
                    save_json(meta, meta_file)
                    print(f"  ✅ Recurso oficial descargado con éxito: {dest_file.name} [{attribution_text}]")
                    return dest_file, meta

        # Attempt 3: Query NASA Library using discovery title and keywords
        print(f"  🔍 Buscando en NASA Library por '{title}'...")
        keywords = discovery_meta.get("keywords", [])
        search_queries = [title]
        if keywords:
            search_queries.append(" ".join(keywords[:2]))

        for q in search_queries:
            items = self.search(q, media_types=[media_type], page_size=5)
            if not items and media_type == "video":
                items = self.search(q, media_types=["image"], page_size=5)
            if items:
                cand = items[0]
                c_urls = self.get_asset_direct_urls(cand["nasa_id"])
                best_url = self.select_best_url(c_urls, cand["media_type"])
                if best_url:
                    c_type = cand["media_type"]
                    ext = ".mp4" if c_type == "video" else ".jpg"
                    dest_file = save_dir / f"scene_{scene_idx:02d}{ext}"
                    meta_file = save_dir / f"scene_{scene_idx:02d}.json"

                    print(f"  ⬇️ Descargando recurso oficial encontrado: '{cand['title']}'...")
                    if download_file(best_url, dest_file):
                        meta = {
                            "scene_index": scene_idx,
                            "provider": "nasa_official_discovery",
                            "is_primary_discovery": True,
                            "title": cand["title"],
                            "nasa_id": cand["nasa_id"],
                            "media_type": c_type,
                            "source_url": best_url,
                            "source": source,
                            "description": cand["description"][:300],
                            "center": cand["center"],
                            "photographer_or_credit": cand["photographer"] or credit,
                            "date_created": cand["date_created"] or date_str,
                            "attribution_text": attribution_text,
                            "license": NASA_PUBLIC_LICENSE_NOTE,
                            "local_file": str(dest_file.name)
                        }
                        save_json(meta, meta_file)
                        print(f"  ✅ Recurso oficial descargado con éxito: {dest_file.name} [{attribution_text}]")
                        return dest_file, meta

        print("  ⚠️ No se pudo descargar el medio oficial específico al inicio; se buscará en el paso de escenas.")
        return None, None
