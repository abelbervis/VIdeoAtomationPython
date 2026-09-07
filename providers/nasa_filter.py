"""
NASA Media Filtering and Quality Ranking Engine.
Filters out public relations/logos and artificial concept illustrations,
and scores authentic scientific observational media from primary space centers.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

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

        # Thumbnail link
        thumb_url = None
        for link in raw_item.get("links", []):
            if link.get("rel") == "preview":
                thumb_url = link.get("href")
                break

        title_lower = title.lower()
        desc_lower = (description or "").lower()

        # Check PR / Institutional patterns
        is_pr = False
        if any(p in title_lower for p in BANNED_PR_PATTERNS):
            is_pr = True
        elif any(p in desc_lower[:250] for p in ["meatball logo", "worm logo", "press conference", "ribbon cutting", "podium", "signing ceremony"]):
            is_pr = True

        # Check Illustration / CGI / Artist concept
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
        """
        Calculates an authenticity and relevance score:
        - Prioritizes top observational science centers (STScI, JPL, GSFC).
        - Rewards recent data captures.
        - Penalizes illustrations unless no observational data exists.
        - Rewards topic relevance matches.
        """
        score = 5.0

        # Scientific center bonus
        score += PRIORITY_CENTERS.get(candidate.center, 0.0)

        # Recency bonus: recent JWST/Hubble/Rover discoveries get higher scores
        year = candidate.date_created[:4] if len(candidate.date_created) >= 4 else "1900"
        if year.isdigit():
            y_int = int(year)
            if y_int >= 2022:
                score += 2.0  # JWST era
            elif y_int >= 2015:
                score += 1.0  # Modern high-def era
            elif y_int < 1980:
                score -= 0.5  # Vintage archive (unless specifically requested)

        # Topic relevance match
        if topic_anchor:
            anchor_words = [w.lower() for w in topic_anchor.split() if len(w) > 2]
            title_lower = candidate.title.lower()
            if any(w in title_lower for w in anchor_words):
                score += 2.5

        # Illustration penalty
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
        """
        Parses, filters, scores, and orders candidates from highest to lowest scientific quality.
        """
        candidates: List[NASACandidate] = []

        for item in raw_items:
            cand = cls.parse_raw_item(item)
            if not cand:
                continue

            # Strict elimination: Always ban administrative PR, podiums, and logos
            if cand.is_pr_photo:
                continue

            # Illustration filter
            if cand.is_illustration and not allow_illustrations:
                continue

            cand.quality_score = cls.score_candidate(cand, topic_anchor=topic_anchor)
            candidates.append(cand)

        # Sort by quality score descending, then by date descending
        candidates.sort(
            key=lambda c: (c.quality_score, c.date_created or "1900-01-01"),
            reverse=True
        )

        return candidates
