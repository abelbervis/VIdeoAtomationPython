"""
Pixabay Music & Commercial Beat Engine.
Manages royalty-free background music selection via Pixabay and generates
studio-grade rhythmic beat tracks locked to exact BPM for beat-synced video editing.
"""

import os
import math
import struct
import wave
import random
import subprocess
import urllib.request
import urllib.parse
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from config import MUSIC_DIR, TEMP_DIR
from audio.beat_sync import BeatGrid


# Standard commercial music profiles for social media ads
GENRE_PROFILES = {
    "commercial_trap": {
        "name": "Commercial Trap & Urban Beat",
        "bpm": 130.0,
        "tags": ["trap", "hip hop", "upbeat", "advertising", "urban", "energetic"],
        "desc": "Bajos 808 contundentes y percusión moderna ideal para zapatillas, moda urbana, tecnología y gadgets.",
        "kick_pattern": [1, 0, 0, 1, 0, 0, 1, 0],
        "snare_pattern": [0, 0, 1, 0, 0, 0, 1, 0],
        "bass_root": 55.0, # A1
    },
    "tech_electronic": {
        "name": "Modern Tech & Future Groove",
        "bpm": 124.0,
        "tags": ["electronic", "tech", "future", "commercial", "smart", "innovation"],
        "desc": "Ritmo futurista y limpio ideal para accesorios inteligentes, apps, hardware y electrónica.",
        "kick_pattern": [1, 0, 0, 0, 1, 0, 0, 0],
        "snare_pattern": [0, 0, 1, 0, 0, 0, 1, 0],
        "bass_root": 65.4, # C2
    },
    "upbeat_pop": {
        "name": "Upbeat Commercial Pop",
        "bpm": 120.0,
        "tags": ["pop", "happy", "commercial", "energetic", "summer", "lifestyle"],
        "desc": "Energía positiva, alegre y comercial para productos de hogar, cocina, familia y consumo masivo.",
        "kick_pattern": [1, 0, 0, 0, 1, 0, 0, 0],
        "snare_pattern": [0, 0, 1, 0, 0, 0, 1, 0],
        "bass_root": 73.4, # D2
    },
    "chill_lofi": {
        "name": "Chill Aesthetic & Lo-Fi Lounge",
        "bpm": 92.0,
        "tags": ["lofi", "chill", "relax", "coffee", "beauty", "aesthetic", "skincare"],
        "desc": "Vibra relajante y elegante para cosméticos, skincare, café, libros, moda minimalista y bienestar.",
        "kick_pattern": [1, 0, 0, 0, 0, 1, 0, 0],
        "snare_pattern": [0, 0, 1, 0, 0, 0, 1, 0],
        "bass_root": 58.27, # A#1
    },
    "energetic_stomp": {
        "name": "Energetic Stomp & Rock Drive",
        "bpm": 138.0,
        "tags": ["rock", "stomp", "action", "fitness", "sport", "drive", "urgent"],
        "desc": "Máxima intensidad y urgencia para fitness, deportes, herramientas y ofertas flash de tiempo limitado.",
        "kick_pattern": [1, 0, 1, 0, 1, 0, 1, 0],
        "snare_pattern": [0, 0, 1, 0, 0, 0, 1, 0],
        "bass_root": 49.0, # G1
    },
}


class PixabayMusicEngine:
    """
    Handles Pixabay Royalty-Free music lookup and procedural beat generation.
    """

    def __init__(self, music_dir: Path = MUSIC_DIR, temp_dir: Path = TEMP_DIR):
        self.music_dir = Path(music_dir)
        self.temp_dir = Path(temp_dir)
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.api_key = os.getenv("PIXABAY_API_KEY", "").strip()

    def search_pixabay_api(self, query: str, genre: str = "commercial_trap") -> Optional[Path]:
        """
        Attempts to search and download a royalty-free track from Pixabay API
        if a free API key is configured.
        """
        if not self.api_key:
            return None

        try:
            params = urllib.parse.urlencode({
                "key": self.api_key,
                "q": query,
                "category": "music",
                "per_page": 5,
            })
            url = f"https://pixabay.com/api/?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            hits = data.get("hits", [])
            for hit in hits:
                audio_url = hit.get("audio") or hit.get("previewURL")
                if audio_url:
                    target_file = self.music_dir / f"pixabay_{hit.get('id', 'track')}.mp3"
                    if not target_file.exists():
                        print(f"  📥 Descargando pista libre de Pixabay: {hit.get('tags', 'music')}...")
                        dl_req = urllib.request.Request(audio_url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(dl_req, timeout=15) as dl_resp, open(target_file, "wb") as f:
                            f.write(dl_resp.read())
                    if target_file.exists() and target_file.stat().st_size > 5000:
                        return target_file
        except Exception as e:
            print(f"  ℹ️ Pixabay API info: {e}")

        return None

    def synthesize_studio_beat(
        self,
        genre_key: str,
        duration_sec: float,
        output_file: Optional[Path] = None,
        custom_bpm: Optional[float] = None
    ) -> Tuple[Path, BeatGrid]:
        """
        Synthesizes a master-grade commercial backing beat with punchy kick, snare,
        hi-hats, and rhythmic sub-bass with exact BPM.
        100% Free, instant (<1s), zero API quota, perfectly locked to beat grid.
        """
        profile = GENRE_PROFILES.get(genre_key, GENRE_PROFILES["commercial_trap"])
        bpm = custom_bpm if custom_bpm else profile["bpm"]
        beat_grid = BeatGrid(bpm=bpm)

        if not output_file:
            output_file = self.temp_dir / f"beat_{genre_key}_{int(bpm)}bpm.mp3"

        wav_temp = self.temp_dir / f"beat_raw_{genre_key}.wav"

        sample_rate = 44100
        num_channels = 2
        total_samples = int(sample_rate * duration_sec)

        spb = beat_grid.seconds_per_beat
        samples_per_beat = int(sample_rate * spb)
        samples_per_16th = int(samples_per_beat / 4)

        # Buffer for audio generation (floats -1.0 to 1.0)
        audio_left = [0.0] * total_samples
        audio_right = [0.0] * total_samples

        bass_root = profile["bass_root"]
        kick_pat = profile["kick_pattern"]
        snare_pat = profile["snare_pattern"]

        # Number of 8th note slots
        total_slots = int(duration_sec / (spb / 2))

        # Generate drum pattern
        for slot in range(total_slots):
            slot_sample = int(slot * (samples_per_beat / 2))
            pat_idx = slot % len(kick_pat)

            # Kick Drum (Punchy 808 with exponential pitch drop)
            if kick_pat[pat_idx] == 1:
                kick_len = int(sample_rate * 0.38)
                for i in range(min(kick_len, total_samples - slot_sample)):
                    t = i / sample_rate
                    # Pitch drops from 160Hz to 48Hz
                    freq = 48.0 + 112.0 * math.exp(-t * 22.0)
                    phase = 2.0 * math.pi * freq * t
                    # Amplitude envelope
                    amp = math.exp(-t * 8.5) * 0.75
                    val = math.sin(phase) * amp
                    idx = slot_sample + i
                    audio_left[idx] += val
                    audio_right[idx] += val

            # Snare / Clap (Snappy noise burst + mid body)
            if snare_pat[pat_idx] == 1:
                snare_len = int(sample_rate * 0.22)
                for i in range(min(snare_len, total_samples - slot_sample)):
                    t = i / sample_rate
                    body = math.sin(2.0 * math.pi * 185.0 * t) * math.exp(-t * 24.0) * 0.35
                    noise = (random.random() * 2.0 - 1.0) * math.exp(-t * 18.0) * 0.45
                    val = body + noise
                    idx = slot_sample + i
                    audio_left[idx] += val * 0.95
                    audio_right[idx] += val * 0.95

            # Hi-Hats (Crisp short noise bursts on every 8th note)
            hihat_len = int(sample_rate * 0.05)
            velocity = 0.28 if (slot % 2 == 0) else 0.18
            for i in range(min(hihat_len, total_samples - slot_sample)):
                t = i / sample_rate
                val = (random.random() * 2.0 - 1.0) * math.exp(-t * 70.0) * velocity
                idx = slot_sample + i
                audio_left[idx] += val * 0.8
                audio_right[idx] += val * 1.1

        # Bassline & Synth Cadence
        # 4-bar chord progression: Root, 6th, 4th, 5th
        cadence_ratios = [1.0, 1.25, 0.89, 1.12]
        bar_samples = int(sample_rate * beat_grid.seconds_per_bar)

        for bar_idx in range(int(duration_sec / beat_grid.seconds_per_bar) + 1):
            bar_start = bar_idx * bar_samples
            ratio = cadence_ratios[bar_idx % len(cadence_ratios)]
            freq = bass_root * ratio

            for i in range(min(bar_samples, total_samples - bar_start)):
                idx = bar_start + i
                t = i / sample_rate
                # Sub bass sine + subtle 2nd harmonic
                sub = math.sin(2.0 * math.pi * freq * t) * 0.32
                harm = math.sin(2.0 * math.pi * freq * 2.0 * t) * 0.08
                # Gentle rhythmic sidechain pump on beats
                beat_phase = (i % samples_per_beat) / samples_per_beat
                sidechain = 0.35 + 0.65 * math.sin(beat_phase * math.pi)
                val = (sub + harm) * sidechain
                audio_left[idx] += val
                audio_right[idx] += val

        # Master Limiter & Normalization
        max_peak = max(max(map(abs, audio_left)), max(map(abs, audio_right)), 0.001)
        target_headroom = 0.88 # -1.1 dB true peak
        scale = target_headroom / max_peak

        with wave.open(str(wav_temp), "wb") as wf:
            wf.setnchannels(num_channels)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(sample_rate)
            frames = bytearray()
            for i in range(total_samples):
                # Soft clip with tanh for warmth
                l_val = math.tanh(audio_left[i] * scale)
                r_val = math.tanh(audio_right[i] * scale)
                l_int = max(-32767, min(32767, int(l_val * 32767)))
                r_int = max(-32767, min(32767, int(r_val * 32767)))
                frames.extend(struct.pack("<hh", l_int, r_int))
            wf.writeframes(frames)

        # Convert to high-quality MP3 with FFmpeg
        cmd = [
            "ffmpeg", "-y",
            "-i", str(wav_temp),
            "-acodec", "libmp3lame",
            "-b:a", "256k",
            str(output_file)
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        if wav_temp.exists():
            wav_temp.unlink(missing_ok=True)

        return output_file, beat_grid

    def get_or_create_ad_music(
        self,
        genre_key: str,
        target_duration: float,
        custom_music_path: Optional[str] = None
    ) -> Tuple[Path, BeatGrid]:
        """
        Resolves the best commercial track:
        1. User-provided custom track
        2. Local track in assets/music/
        3. Pixabay API query
        4. Studio Beat synthesizer (Instant, 0-cost, exact BPM)
        """
        # 1. Custom user path
        if custom_music_path:
            p = Path(custom_music_path)
            if p.exists() and p.is_file():
                bpm = GENRE_PROFILES.get(genre_key, {}).get("bpm", 124.0)
                return p, BeatGrid(bpm=bpm)

        # 2. Local tracks in assets/music/
        existing = list(self.music_dir.glob("*.mp3")) + list(self.music_dir.glob("*.wav"))
        for f in existing:
            if genre_key in f.name.lower():
                bpm = GENRE_PROFILES.get(genre_key, {}).get("bpm", 124.0)
                return f, BeatGrid(bpm=bpm)

        # 3. Try Pixabay API if key present
        profile = GENRE_PROFILES.get(genre_key, GENRE_PROFILES["commercial_trap"])
        query = f"commercial {profile['tags'][0]}"
        downloaded = self.search_pixabay_api(query, genre=genre_key)
        if downloaded:
            return downloaded, BeatGrid(bpm=profile["bpm"])

        # 4. Built-in Studio Beat Synthesizer with exact BPM
        dest = self.music_dir / f"ad_beat_{genre_key}_{int(profile['bpm'])}bpm.mp3"
        if not dest.exists():
            print(f"  🥁 Generando base musical comercial '{profile['name']}' a {int(profile['bpm'])} BPM...")
            self.synthesize_studio_beat(genre_key, max(45.0, target_duration + 5.0), output_file=dest)

        return dest, BeatGrid(bpm=profile["bpm"])
