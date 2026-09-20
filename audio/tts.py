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
from core.hosts import HostRegistry
from utils.files import get_media_duration


# Cosmic Entity Voice Profiles (Populated dynamically from Core OOP Host Registry)
COSMIC_VOICE_PROFILES = HostRegistry.all_voice_profiles()



def detect_speech_impact_intensity(text: str) -> Tuple[bool, float, str]:
    """
    Analyzes text to detect questions, exclamations, and high-impact cosmic concepts.
    Returns:
      - is_impact: bool (True for emphasis/questions/hooks/revelations)
      - intensity: float (0.0 for subtle narration up to 1.0 for high impact)
      - reason: str description of triggered pattern
    """
    clean = text.strip()
    
    # 1. Direct Questions & Inquiries (Highest cosmic impact: "¿Qué pasaría si...?", "¿Cómo es posible...?")
    if "¿" in clean or "?" in clean:
        return True, 0.85, "cosmic_question"
    
    # 2. Exclamations, Greetings & Direct Audience Hooks ("¡Hola!", "¡Increíble!", "¡Atención!")
    if "¡" in clean or "!" in clean:
        return True, 0.90, "cosmic_exclamation"
        
    # 3. High Impact Turning Points & Climax Concepts (Requires strong cosmic disruption words)
    high_impact_tokens = [
        "paradoja", "singularidad", "colapso", "destrucción", 
        "agujero negro", "horizonte de sucesos", "big bang", "antimateria",
        "multiverso", "apocalipsis", "cataclismo", "imposible", "revelación"
    ]
    lower = clean.lower()
    matched_high = [kw for kw in high_impact_tokens if kw in lower]
    if matched_high:
        return True, 0.80, f"climax_concept:{matched_high[0]}"
        
    # 4. Standard measured narration (e.g. explanations, descriptions, neutral sentences)
    # The double voice stays active permanently as a subtle, organic acoustic presence (-13.5dB)
    return False, 0.15, "standard_narration"


def build_cell_double_tracking_filter(
    entity: str,
    delay_ms: Optional[int] = None,
    double_vol_db: Optional[float] = None,
    detune_semitones: Optional[float] = None,
    is_impact: bool = False,
    impact_intensity: float = 0.5
) -> str:
    """
    Generates an adaptive, artifact-free FFmpeg filtergraph for DBZ Cell-style Double Tracking.
    
    Adaptive Architecture:
      - SUTILEZA NARRATIVA: Durante la narración continua, la voz secundaria permanece en
        -13.0 a -14.0 dB con micro-retardo de 10-14ms, percibida como una textura orgánica íntima.
      - IMPACTO / PREGUNTAS: Cuando se detectan signos de interrogación/exclamación o conceptos
        clave, sube de manera controlada a -8.0 a -9.5 dB con micro-retardo de 16-22ms (Efecto Haas 3D),
        desplegando una resonancia estéreo omnipotente sin generar eco discreto.
      - 3D HAAS STEREO EXPANSION: La voz secundaria se abre binauralmente (L/R desfasados),
        mientras la voz líder se mantiene centrada al 100% para máxima nitidez y comprensión.
    """
    tag = "q" if "quantum" in entity.lower() else "s"
    
    # Adaptive parameter resolution based on impact intensity
    if "quantum" in entity.lower():
        # Quantum: Sub-armónicos, misterio del vacío, pitch descendente
        default_delay_l = int(12 + (18 - 12) * impact_intensity) if delay_ms is None else delay_ms
        default_delay_r = int(16 + (24 - 16) * impact_intensity) if delay_ms is None else int(delay_ms * 1.3)
        default_vol_db = (-13.5 + (5.5 * impact_intensity)) if double_vol_db is None else double_vol_db
        default_detune = (-0.30 - (0.25 * impact_intensity)) if detune_semitones is None else detune_semitones
        
        pitch_scale = 2.0 ** (default_detune / 12.0)
        vol_factor = 10.0 ** (default_vol_db / 20.0)
        
        filter_graph = (
            f"[0:a]aformat=channel_layouts=stereo[lead_{tag}];"
            f"[0:a]asplit=2[c_l_{tag}][c_r_{tag}];"
            f"[c_l_{tag}]adelay={default_delay_l}|0,rubberband=pitch={pitch_scale:.4f},"
            f"equalizer=f=180:width_type=h:width=80:g=2.5,lowpass=f=2800[clone_l_{tag}];"
            f"[c_r_{tag}]adelay=0|{default_delay_r},rubberband=pitch={pitch_scale:.4f},"
            f"equalizer=f=180:width_type=h:width=80:g=2.5,lowpass=f=2800[clone_r_{tag}];"
            f"[clone_l_{tag}][clone_r_{tag}]join=inputs=2:channel_layout=stereo,volume={vol_factor:.3f}[clone_stereo_{tag}];"
            f"[lead_{tag}][clone_stereo_{tag}]amix=inputs=2:weights=1.0 1.0:normalize=0:duration=first[mix_{tag}];"
            f"[mix_{tag}]highpass=f=75,equalizer=f=3200:width_type=h:width=1200:g=1.5,volume=1.8[out_{tag}]"
        )
    else:
        # Solar: Plasma armónico estelar, brillo energético, pitch ascendente
        default_delay_l = int(10 + (16 - 10) * impact_intensity) if delay_ms is None else delay_ms
        default_delay_r = int(14 + (22 - 14) * impact_intensity) if delay_ms is None else int(delay_ms * 1.3)
        default_vol_db = (-14.0 + (5.5 * impact_intensity)) if double_vol_db is None else double_vol_db
        default_detune = (0.25 + (0.20 * impact_intensity)) if detune_semitones is None else detune_semitones
        
        pitch_scale = 2.0 ** (default_detune / 12.0)
        vol_factor = 10.0 ** (default_vol_db / 20.0)
        
        filter_graph = (
            f"[0:a]aformat=channel_layouts=stereo[lead_{tag}];"
            f"[0:a]asplit=2[c_l_{tag}][c_r_{tag}];"
            f"[c_l_{tag}]adelay={default_delay_l}|0,rubberband=pitch={pitch_scale:.4f},"
            f"highpass=f=1100,equalizer=f=3800:width_type=h:width=1200:g=2.2[clone_l_{tag}];"
            f"[c_r_{tag}]adelay=0|{default_delay_r},rubberband=pitch={pitch_scale:.4f},"
            f"highpass=f=1100,equalizer=f=3800:width_type=h:width=1200:g=2.2[clone_r_{tag}];"
            f"[clone_l_{tag}][clone_r_{tag}]join=inputs=2:channel_layout=stereo,volume={vol_factor:.3f}[clone_stereo_{tag}];"
            f"[lead_{tag}][clone_stereo_{tag}]amix=inputs=2:weights=1.0 1.0:normalize=0:duration=first[mix_{tag}];"
            f"[mix_{tag}]highpass=f=85,equalizer=f=2600:width_type=h:width=900:g=1.8,volume=1.8[out_{tag}]"
        )
        
    return filter_graph



def clean_tts_spoken_text(text: str) -> str:
    """
    Cleans text for neural TTS engines so that emojis, arrows, HUD bracket tags,
    and visual glyphs are NEVER spoken aloud as words (e.g. 'flecha hacia abajo').
    """
    if not text:
        return ""
    import re
    cleaned = text
    # Replace directional / prompt arrows with natural spoken phrasing
    cleaned = re.sub(r'[⬇️👇↓]', ' en los comentarios', cleaned)
    # Remove bracketed actions or meta tags like [Ambos Orbes...], [Pausa], etc.
    cleaned = re.sub(r'\[.*?\]', '', cleaned)
    # Remove emoji and symbol ranges
    emoji_pattern = re.compile(
        r'[\U00010000-\U0010ffff]|[\u2600-\u27ff]|[\u2300-\u23ff]|[\u2b50-\u2b55]|[\u200d\ufe0f]',
        flags=re.UNICODE
    )
    cleaned = emoji_pattern.sub('', cleaned)
    # Normalize multiple spaces and punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = cleaned.replace("...", ",").replace("..", ".")
    # Clean redundant "en los comentarios en los comentarios"
    cleaned = re.sub(r'(en los comentarios\s*)+', 'en los comentarios', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def prepare_cosmic_pacing_text(text: str) -> str:
    """
    Cleans and normalizes text for natural, authoritative speech cadence without artificial long pauses or spoken emoji artifacts.
    """
    return clean_tts_spoken_text(text)



class BaseTTSProvider(abc.ABC):
    """Abstract base class for TTS engines."""

    @abc.abstractmethod
    def synthesize_text(self, text: str, output_path: Path, voice: Optional[str] = None) -> bool:
        """Synthesize text into an audio file."""
        pass


class EdgeTTSProvider(BaseTTSProvider):
    """Microsoft Edge Neural TTS with SSML Prosody (Rate/Pitch) & Acoustic DSP Enhancement."""

    def __init__(self, default_voice: str = DEFAULT_TTS_VOICE):
        self.default_voice = (default_voice or "es-MX-JorgeNeural").strip().strip("'\"").strip()

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
        selected_voice = (voice or self.default_voice or "es-MX-JorgeNeural").strip().strip("'\"").strip()
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
        apply_dsp: bool = True,
        delay_ms: Optional[int] = None,
        double_vol_db: Optional[float] = None,
        detune_semitones: Optional[float] = None,
        is_impact: Optional[bool] = None,
        impact_intensity: Optional[float] = None
    ) -> bool:
        """
        Synthesize voice for a cosmic entity (quantum or solar) with tuned SSML prosody,
        Adaptive DBZ Cell-style Double Tracking (detuned micro-delay), 3D Haas binaural width, and sub-harmonics.
        Automatically scales presence between subtle narration and high-impact emphasis.
        """
        entity_key = entity.lower().strip()
        profiles = HostRegistry.all_voice_profiles()
        profile = profiles.get(entity_key, profiles.get("quantum", COSMIC_VOICE_PROFILES.get("quantum", {})))

        # Dynamic speech impact detection
        auto_impact, auto_intensity, reason = detect_speech_impact_intensity(text)
        final_is_impact = is_impact if is_impact is not None else auto_impact
        final_intensity = impact_intensity if impact_intensity is not None else auto_intensity

        print(f"  🎙️ [{entity.upper()}] Adaptive Double Voice Mode: {'IMPACT (' + reason + ')' if final_is_impact else 'SUBTLE NARRATION'} (intensity: {final_intensity:.2f})")

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

        # 3. Apply Adaptive Cell Double Tracking + Haas 3D Stereo DSP Filtergraph
        try:
            filter_graph = build_cell_double_tracking_filter(
                entity=entity_key,
                delay_ms=delay_ms,
                double_vol_db=double_vol_db,
                detune_semitones=detune_semitones,
                is_impact=final_is_impact,
                impact_intensity=final_intensity
            )

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
            print(f"  ⚠️ Cosmic Double-Tracking DSP Filter Error: {e}, falling back to raw synthesis.")
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
