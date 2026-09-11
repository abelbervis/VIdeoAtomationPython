"""
Pollinations.ai Image Generation Provider (Powered by FLUX / Turbo).
Provides zero-cost, hyper-specific text-to-image generation for impossible cosmic scenes,
acting both as a standalone provider and as an intelligent visual fallback when stock
libraries (Pexels, Pixabay, NASA) lack direct semantic match for complex narration.
"""

import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from config import (
    ASSETS_DIR,
    ENABLE_AI_IMAGE_FALLBACK,
    POLLINATIONS_API_KEY,
    POLLINATIONS_MODEL,
)


class PollinationsProvider:
    """
    Client for Pollinations.ai text-to-image API.
    Supports FLUX.1 and Turbo models with smart retry, rate limit recovery,
    and automatic aspect ratio scaling for vertical shorts (9:16) and widescreen (16:9).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        save_dir: Optional[Path] = None,
    ):
        self.api_key = (api_key or POLLINATIONS_API_KEY or "").strip()
        self.default_model = (default_model or POLLINATIONS_MODEL or "flux").lower().strip()
        self.save_dir = Path(save_dir) if save_dir else (ASSETS_DIR / "pollinations")
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def is_configured(self) -> bool:
        """Pollinations is accessible without an API key for public usage."""
        return True

    def _get_dimensions(self, orientation: str) -> Tuple[int, int]:
        """
        Calculate resolution for Pollinations image generation.
        Uses standard aspect ratios with optimal token/speed efficiency.
        """
        norm = (orientation or "vertical").lower().strip()
        if norm in ("vertical", "portrait", "9:16"):
            return 768, 1344  # 9:16 high-res vertical (scaled to 1080x1920 in video renderer)
        elif norm in ("horizontal", "landscape", "16:9", "widescreen"):
            return 1344, 768  # 16:9 widescreen
        else:
            return 1024, 1024  # 1:1 square

    def clean_prompt(self, raw_prompt: str, fallback_topic: str = "deep space") -> str:
        """Sanitize prompt and inject cinematic photographic modifiers for stellar quality."""
        p = (raw_prompt or "").strip()
        if not p or len(p) < 6:
            p = f"cinematic 8k photograph of {fallback_topic}, national geographic, deep space photography"

        # Ensure cinematic photography aesthetic if not already present
        if "photograph" not in p.lower() and "photo" not in p.lower() and "cinematic" not in p.lower():
            p = f"cinematic 8k photograph of {p}, National Geographic photography, sharp focus, 8k"

        return p

    def generate_image(
        self,
        prompt: str,
        out_path: Path,
        width: int = 768,
        height: int = 1344,
        model: Optional[str] = None,
        seed: Optional[int] = None,
        max_retries: int = 3
    ) -> bool:
        """
        Download generated image from Pollinations.ai API with backoff retry.
        Gracefully handles concurrency limits (HTTP 429) by backing off and switching models.
        """
        selected_model = model or self.default_model
        clean_p = self.clean_prompt(prompt)
        encoded_prompt = urllib.parse.quote(clean_p)

        # Base URL construction
        params = {
            "width": str(width),
            "height": str(height),
            "model": selected_model,
            "nologo": "true",
            "enhance": "true"
        }
        if seed is not None:
            params["seed"] = str(seed)
        if self.api_key:
            params["key"] = self.api_key

        models_to_try = [selected_model]
        if selected_model != "turbo":
            models_to_try.append("turbo")
        models_to_try.append("sana")

        for model_candidate in models_to_try:
            params["model"] = model_candidate
            query_str = urllib.parse.urlencode(params)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?{query_str}"

            for attempt in range(max_retries):
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                        "Accept": "image/jpeg,image/png,image/*;q=0.9",
                    }
                    if self.api_key:
                        headers["Authorization"] = f"Bearer {self.api_key}"

                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=25) as resp:
                        content_type = resp.headers.get("Content-Type", "").lower()
                        status = resp.status

                        if status == 200 and ("image" in content_type or not content_type):
                            data = resp.read()
                            # Check that returned payload is indeed an image and not a json error disguised as 200
                            if len(data) > 2048 and (data.startswith(b"\xff\xd8") or data.startswith(b"\x89PNG")):
                                out_path.write_bytes(data)
                                return True
                            elif b"Too Many Requests" in data or b"Queue full" in data:
                                print(f"    ⏳ Pollinations queue busy for model '{model_candidate}', backing off...")
                                time.sleep(2.5 * (attempt + 1))
                                continue

                except urllib.error.HTTPError as he:
                    if he.code == 429:
                        print(f"    ⏳ Pollinations 429 (rate limit) for model '{model_candidate}' (attempt {attempt+1}/{max_retries})...")
                        time.sleep(3.0 * (attempt + 1))
                    else:
                        print(f"    ⚠️ Pollinations HTTP {he.code} for '{model_candidate}': {he.reason}")
                        break
                except Exception as ex:
                    print(f"    ⚠️ Pollinations connection error ({model_candidate}): {ex}")
                    time.sleep(2.0)

        return False

    def fetch_scene_asset(
        self,
        scene_idx: int,
        prompt: Optional[str] = None,
        keywords: Optional[list] = None,
        orientation: str = "vertical",
        visual_subject: Optional[str] = None,
        topic: str = "deep space",
        filename_suffix: str = ""
    ) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
        """
        Fetches an AI-generated photographic visual for a specific scene.
        Returns (filepath, metadata).
        """
        # Determine best prompt: prefer dedicated image_prompt, fallback to visual_subject or keywords
        effective_prompt = ""
        if prompt and str(prompt).strip():
            effective_prompt = str(prompt).strip()
        elif visual_subject and str(visual_subject).strip():
            effective_prompt = f"cinematic photorealistic 8k telescope observation of {visual_subject}, deep space, National Geographic photography"
        elif keywords and len(keywords) > 0:
            effective_prompt = f"cinematic photorealistic 8k space photograph of {', '.join(keywords[:3])}, National Geographic style"
        else:
            effective_prompt = f"cinematic photorealistic 8k space photograph of {topic}, deep cosmos"

        width, height = self._get_dimensions(orientation)
        seed = int(time.time()) % 100000 + (scene_idx * 37)
        filename = f"pollinations_scene_{scene_idx:02d}{filename_suffix}_{seed}.jpg"
        out_path = self.save_dir / filename

        print(f"  🎨 Generating AI visual with Pollinations ({self.default_model.upper()}) for scene {scene_idx}...")
        print(f"     Prompt: \"{effective_prompt[:75]}...\"")

        success = self.generate_image(
            prompt=effective_prompt,
            out_path=out_path,
            width=width,
            height=height,
            seed=seed
        )

        if success and out_path.exists() and out_path.stat().st_size > 2048:
            title = visual_subject or f"AI Vision {scene_idx}"
            meta = {
                "scene_index": scene_idx,
                "provider": "pollinations",
                "title": title,
                "media_type": "image",
                "attribution_text": f"AI Simulation ({self.default_model.upper()})",
                "author": "Pollinations.ai",
                "url": "https://pollinations.ai"
            }
            print(f"  ✅ Escena {scene_idx:02d} generada exitosamente con IA ({self.default_model.upper()}): {filename}")
            return out_path, meta

        print(f"  ❌ Falló la generación con Pollinations para la escena {scene_idx}")
        return None, None
