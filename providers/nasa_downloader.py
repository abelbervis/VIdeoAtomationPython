"""
NASA Asset Downloader & Metadata Manager.
Handles downloading remote NASA assets and formatting attribution metadata.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from providers.nasa_client import NASAClient
from providers.nasa_filter import NASACandidate
from utils.files import download_file, save_json

NASA_PUBLIC_LICENSE_NOTE = (
    "Public Domain - NASA Content Policy: NASA material is generally not copyrighted "
    "and may be used for educational or informational purposes without explicit permission."
)


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
        """
        Retrieves direct download URLs for a NASACandidate, downloads the optimal resolution,
        and saves complete scene metadata.
        """
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
