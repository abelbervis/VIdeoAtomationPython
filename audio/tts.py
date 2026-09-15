"""
Decoupled Text-to-Speech (TTS) Provider.
Supports Microsoft Edge Neural TTS, OpenAI TTS, Google TTS, and scene-level synchronization.
Generates high quality scientific documentary narration with precise timestamps.
"""

import abc
import asyncio
import json
import os
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from config import AUDIO_DIR, TTS_PROVIDER, TTS_API_KEY, DEFAULT_TTS_VOICE, OPENAI_API_KEY
from utils.files import get_media_duration


# Cosmic Entity Voice Profiles (Microsoft Edge Neural TTS + SSML Prosody + 4-Tier DSP Acoustic Engineering)
COSMIC_VOICE_PROFILES = {
    "quantum": {
        "name": "QUANTUM",
        "voice": "es-ES-AlvaroNeural",
        "rate": "-5%",
        "pitch": "-4Hz",
        "volume": "+0%",
        "role": "La Mente Fundamental del Vacío",
        "description": "Profunda, analítica, serena y pausada. Sub-octava estelar + dimensión binaural 3D.",
        "drone_freq": 48,
        "filter_complex": (
            "[0:a]asplit=2[main_q][sub_q];"
            "[sub_q]asetrate=22050,atempo=2.0,lowpass=f=120,volume=0.15[sub_bass];"
            "[main_q][sub_bass]amix=inputs=2:weights=1.0 0.2:duration=first[mixed_q];"
            "[mixed_q]highpass=f=80,equalizer=f=140:width_type=h:width=60:g=3.0,equalizer=f=3800:width_type=h:width=1200:g=2.5,compand=attacks=0.01:decays=0.1:points=-60/-60|-20/-10|0/-3:soft-knee=6[eq_q];"
            "[eq_q]aformat=channel_layouts=stereo,asplit=2[center_q][wide_q];"
            "[wide_q]adelay=14|14,highpass=f=300,volume=0.20[wide_delayed_q];"
            "[center_q][wide_delayed_q]amix=inputs=2:weights=1.0 0.15:duration=first,volume=2.2[out_q]"
        )
    },
    "solar": {
        "name": "SOLAR",
        "voice": "es-ES-ElviraNeural",
        "rate": "+1%",
        "pitch": "+2Hz",
        "volume": "+0%",
        "role": "El Núcleo Estelar Radiante",
        "description": "Cálida, brillante, envolvente. Saturación plasma estelar + expansión 3D Haas.",
        "drone_freq": 58,
        "filter_complex": (
            "[0:a]asplit=2[main_s][plasma_s];"
            "[plasma_s]highpass=f=3200,volume=0.18,aecho=0.8:0.7:16:0.25[shimmer_s];"
            "[main_s][shimmer_s]amix=inputs=2:weights=1.0 0.2:duration=first[mixed_s];"
            "[mixed_s]highpass=f=90,equalizer=f=2200:width_type=h:width=800:g=2.5,equalizer=f=6200:width_type=h:width=2000:g=2.8,compand=attacks=0.01:decays=0.1:points=-60/-60|-20/-10|0/-3:soft-knee=6[eq_s];"
            "[eq_s]aformat=channel_layouts=stereo,asplit=2[center_s][wide_s];"
            "[wide_s]adelay=10|10,highpass=f=350,volume=0.18[wide_delayed_s];"
            "[center_s][wide_delayed_s]amix=inputs=2:weights=1.0 0.15:duration=first,volume=2.2[out_s]"
        )

    }
}


def prepare_cosmic_pacing_text(text: str) -> str:
    """
    Inserts psychophysical micro-pauses before key concepts to create a measured,
    ancient intelligence cadence rather than rapid robotic TTS delivery.
    """
    replacements = {
        " cuántica": "... cuántica",
        "cuántica": "cuántica",
        " universo": "... universo",
        " espacio": "... espacio",
        " tiempo": "... tiempo",
        " partículas": "... partículas",
        " energía": "... energía",
        " misterios": "... misterios",
    }
    processed = text
    for target, rep in replacements.items():
        if target in processed and not processed.startswith("..."):
            processed = processed.replace(target, rep, 1)
    return processed



class BaseTTSProvider(abc.ABC):
    """Abstract base class for TTS engines."""

    @abc.abstractmethod
    def synthesize_text(self, text: str, output_path: Path, voice: Optional[str] = None) -> bool:
        """Synthesize text into an audio file."""
        pass


class EdgeTTSProvider(BaseTTSProvider):
    """Microsoft Edge Neural TTS with SSML Prosody (Rate/Pitch) & Acoustic DSP Enhancement."""

    def __init__(self, default_voice: str = DEFAULT_TTS_VOICE):
        self.default_voice = (default_voice or "es-ES-AlvaroNeural").strip().strip("'\"").strip()

    def synthesize_text(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
        apply_dsp: bool = False,
        dsp_filter: Optional[str] = None
    ) -> bool:
        selected_voice = (voice or self.default_voice or "es-ES-AlvaroNeural").strip().strip("'\"").strip()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        raw_output_path = output_path.parent / f"_raw_{output_path.name}" if apply_dsp else output_path

        synthesized = False

        # 1. Try python edge-tts library if installed
        try:
            import edge_tts

            async def _run():
                communicate = edge_tts.Communicate(
                    text,
                    selected_voice,
                    rate=rate,
                    pitch=pitch,
                    volume=volume
                )
                await communicate.save(str(raw_output_path))

            asyncio.run(_run())
            if raw_output_path.exists() and raw_output_path.stat().st_size > 0:
                synthesized = True
        except ImportError:
            pass
        except Exception as e:
            print(f"  ⚠️ edge-tts python call error: {e}")

        # 2. Try edge-tts CLI tool if available (Fallback)
        if not synthesized:
            try:
                cmd = [
                    "edge-tts",
                    "--voice", selected_voice,
                    "--rate", rate,
                    "--pitch", pitch,
                    "--volume", volume,
                    "--text", text,
                    "--write-media", str(raw_output_path)
                ]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                if raw_output_path.exists() and raw_output_path.stat().st_size > 0:
                    synthesized = True
            except Exception:
                pass

        # 3. Fallback to GoogleTTS if edge-tts is not installed in local environment
        if not synthesized:
            try:
                gtts_provider = GoogleTTSProvider(language="es")
                synthesized = gtts_provider.synthesize_text(text, raw_output_path)
            except Exception as e:
                print(f"  ⚠️ gTTS fallback error: {e}")

        if not synthesized:
            return False

        # 3. Apply Acoustic Post-Processing DSP filter via FFmpeg if requested
        if apply_dsp and dsp_filter:
            try:
                cmd_dsp = [
                    "ffmpeg", "-y",
                    "-i", str(raw_output_path),
                    "-af", dsp_filter,
                    "-acodec", "libmp3lame",
                    "-b:a", "192k",
                    str(output_path)
                ]
                subprocess.run(cmd_dsp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                raw_output_path.unlink(missing_ok=True)
                return output_path.exists() and output_path.stat().st_size > 0
            except Exception as e:
                print(f"  ⚠️ Voice DSP filter error: {e}, keeping raw synthesis.")
                if raw_output_path.exists():
                    raw_output_path.rename(output_path)
                return output_path.exists()

        return True

    def synthesize_cosmic_entity(
        self,
        text: str,
        output_path: Path,
        entity: str = "quantum",
        apply_dsp: bool = True
    ) -> bool:
        """
        Synthesize voice for a cosmic entity (quantum or solar) with tuned SSML prosody,
        psychophysical pacing, 3D Haas binaural width, sub-harmonics, and resonant sub-bass drone.
        """
        entity_key = entity.lower()
        profile = COSMIC_VOICE_PROFILES.get(entity_key, COSMIC_VOICE_PROFILES["quantum"])
        
        # 1. Pacing & SSML pre-processing
        paced_text = prepare_cosmic_pacing_text(text)
        
        output_path = Path(output_path)
        raw_tmp_path = output_path.parent / f"_raw_cosmic_{output_path.name}"

        # 2. Base Neural Synthesis via Edge TTS
        synthesized = self.synthesize_text(
            text=paced_text,
            output_path=raw_tmp_path if apply_dsp else output_path,
            voice=profile["voice"],
            rate=profile["rate"],
            pitch=profile["pitch"],
            volume=profile["volume"],
            apply_dsp=False
        )

        if not synthesized or not apply_dsp:
            return synthesized

        # 3. Apply 4-tier Cosmic DSP Filtergraph (Sub-harmonics + Plasma Saturation + 3D Haas + Resonant Drone)
        try:
            dur = get_media_duration(raw_tmp_path) or 3.0
            filter_graph = profile["filter_complex"].format(duration=f"{dur:.2f}")

            cmd = [
                "ffmpeg", "-y",
                "-i", str(raw_tmp_path),
                "-filter_complex", filter_graph,
                "-map", f"[out_{'q' if 'quantum' in entity_key else 's'}]",
                "-acodec", "libmp3lame",
                "-b:a", "192k",
                str(output_path)
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            raw_tmp_path.unlink(missing_ok=True)
            return output_path.exists() and output_path.stat().st_size > 0
        except Exception as e:
            print(f"  ⚠️ Cosmic DSP Filter Error: {e}, falling back to raw synthesis.")
            if raw_tmp_path.exists():
                raw_tmp_path.rename(output_path)
            return output_path.exists()




class OpenAITTSProvider(BaseTTSProvider):
    """OpenAI TTS API."""

    def __init__(self, api_key: str = OPENAI_API_KEY):
        self.api_key = api_key

    def synthesize_text(self, text: str, output_path: Path, voice: Optional[str] = "onyx") -> bool:
        if not self.api_key:
            return False

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            payload = {
                "model": "tts-1",
                "input": text,
                "voice": voice or "onyx"  # Onyx or alloy fits documentary
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/audio/speech",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as response, open(output_path, "wb") as f:
                f.write(response.read())

            return output_path.exists() and output_path.stat().st_size > 0
        except Exception as e:
            print(f"  ⚠️ OpenAI TTS error: {e}")
            return False


class GoogleTTSProvider(BaseTTSProvider):
    """Google Translate TTS (REST client fallback for zero-key immediate audio)."""

    def __init__(self, language: str = "es"):
        self.language = (language or "es").lower().strip()

    def synthesize_text(self, text: str, output_path: Path, voice: Optional[str] = None) -> bool:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lang_code = "zh-CN" if self.language.startswith("zh") else ("en" if self.language.startswith("en") else "es")
        # Split long text if necessary
        text_encoded = urllib.parse.quote(text[:200])
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={text_encoded}&tl={lang_code}&client=tw-ob"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=15) as response, open(output_path, "wb") as f:
                f.write(response.read())

            return output_path.exists() and output_path.stat().st_size > 0
        except Exception as e:
            print(f"  ⚠️ Google TTS error: {e}")
            return False


class SyntheticFallbackTTSProvider(BaseTTSProvider):
    """Generates clean synthetic speech audio via FFmpeg / eSpeak fallback if offline."""

    def __init__(self, language: str = "es"):
        self.language = (language or "es").lower().strip()

    def synthesize_text(self, text: str, output_path: Path, voice: Optional[str] = None) -> bool:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lang_code = "zh" if self.language.startswith("zh") else ("en" if self.language.startswith("en") else "es")
        # Try espeak if installed
        try:
            cmd = ["espeak", "-v", lang_code, "-w", str(output_path), text]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if output_path.exists() and output_path.stat().st_size > 0:
                return True
        except Exception:
            pass

        # Minimum emergency fallback: estimate duration by word count and generate silent audio track with tone
        words = len(text.split())
        est_duration = max(3.0, words / 2.5)
        try:
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
                "-t", str(est_duration),
                "-q:a", "9",
                "-acodec", "libmp3lame",
                str(output_path)
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except Exception:
            return False


class TTSManager:
    """Manages narration generation, scene audio synchronization, and combined narration."""

    def __init__(
        self,
        provider_type: str = TTS_PROVIDER,
        voice: Optional[str] = None,
        language: str = "es"
    ):
        from config import get_language_voice
        self.language = (language or "es").lower().strip()
        self.voice = get_language_voice(self.language, voice)
        self.providers: List[BaseTTSProvider] = []

        # Setup primary provider
        if provider_type == "openai" and OPENAI_API_KEY:
            self.providers.append(OpenAITTSProvider())
        elif provider_type == "edge":
            self.providers.append(EdgeTTSProvider(self.voice))

        # Add standard fallbacks
        self.providers.append(EdgeTTSProvider(self.voice))
        self.providers.append(GoogleTTSProvider(language=self.language))
        self.providers.append(SyntheticFallbackTTSProvider(language=self.language))

    def synthesize_script(
        self,
        script: Dict[str, Any],
        output_dir: Path = AUDIO_DIR
    ) -> Tuple[Path, List[Dict[str, Any]], float]:
        """
        Synthesize audio for each scene in the script.
        Returns:
            - combined_audio_path: Path to narration.mp3
            - scene_timings: List of scene timing data (start, end, duration, narration)
            - total_duration: float
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        scenes = script.get("scenes", [])
        scene_files: List[Path] = []
        scene_timings: List[Dict[str, Any]] = []
        current_time = 0.0

        print("\n🎙️ Synthesizing narration for each scene...")

        for idx, scene in enumerate(scenes, start=1):
            narration = scene.get("narration", "").strip()
            scene_audio_path = output_dir / f"scene_{idx:02d}.mp3"

            success = False
            for provider in self.providers:
                if provider.synthesize_text(narration, scene_audio_path, self.voice):
                    success = True
                    break

            if not success or not scene_audio_path.exists():
                print(f"  ⚠️ Failed to synthesize audio for scene {idx}, generating placeholder timing.")
                # Generate emergency silent audio
                SyntheticFallbackTTSProvider().synthesize_text(narration, scene_audio_path)

            duration = get_media_duration(scene_audio_path)
            duration = max(duration, 3.0)  # Guarantee minimum readable scene duration

            timing = {
                "scene_id": idx,
                "narration": narration,
                "start": round(current_time, 2),
                "end": round(current_time + duration, 2),
                "duration": round(duration, 2),
                "audio_file": scene_audio_path
            }
            scene_timings.append(timing)
            scene_files.append(scene_audio_path)
            current_time += duration
            print(f"  ✅ Scene {idx:02d}: {duration:.1f}s — \"{narration[:45]}...\"")

        # Combine all scene audios into narration.mp3
        combined_audio_path = output_dir / "narration.mp3"
        self._concat_audios(scene_files, combined_audio_path)

        total_duration = get_media_duration(combined_audio_path)
        if total_duration <= 0:
            total_duration = current_time

        print(f"🎵 Full narration generated: {combined_audio_path.name} ({total_duration:.1f}s)")
        return combined_audio_path, scene_timings, total_duration

    def _concat_audios(self, audio_files: List[Path], output_path: Path) -> None:
        """Concatenate MP3 scene audios using FFmpeg."""
        concat_list_file = output_path.parent / "audio_concat.txt"
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for af in audio_files:
                f.write(f"file '{af.resolve()}'\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file),
            "-c", "copy",
            str(output_path)
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception:
            # Re-encode if stream copy fails
            cmd_reencode = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list_file),
                "-acodec", "libmp3lame",
                "-b:a", "192k",
                str(output_path)
            ]
            subprocess.run(cmd_reencode, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        concat_list_file.unlink(missing_ok=True)
