"""
AI Ad & UGC Copywriter for Commercial Short-Form Videos.
Generates high-converting, high-retention marketing scripts (AIDA / Hook-Benefit-CTA)
tailored to user-provided product photos and videos.
Supports multimodal visual inspection (Gemini Vision) and fast LLMs (Groq, OpenAI).
"""

import base64
import json
import os
import re
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from config import (
    GEMINI_API_KEY,
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_API_BASE,
    OPENAI_API_KEY,
    LLM_PROVIDER,
    TEMP_DIR,
    sanitize_env_value,
)

AD_SYSTEM_PROMPT = """Eres un Director Creativo y Copywriter Publicitario de élite especializado en videos virales y anuncios de alta conversión para TikTok Ads, Instagram Reels, Facebook Ads y YouTube Shorts (formato UGC / Ecommerce / Servicios).

Tu objetivo es transformar imágenes o videos reales tomados por el usuario de un producto o servicio en un anuncio vertical (9:16) dinámico, hipnótico e imposible de ignorar.

REGLAS DE ORO DEL COPYWRITING Y DIRECCIÓN VISUAL:
1. SELECCIÓN INTELIGENTE DEL ORDEN VISUAL Y NARRATIVO (AIDA):
   - NO estás obligado a usar los archivos en orden alfabético ni en el orden en que se recibieron.
   - Analiza minuciosamente el contenido visual de cada foto y video para determinar su rol publicitario ideal:
     * HOOK_HERO: La toma más estética, llamativa, intrigante o nítida para detener el scroll de golpe en los primeros 3 segundos.
     * PROBLEM: Foto/video que ilustre la necesidad o dolor que resuelve el producto.
     * DEMO_FEATURE: Tomas de uso práctico, movimiento, textura, materiales o funciones destacadas.
     * DESIRE_BENEFIT: Tomas de calidad, durabilidad, detalles que despiertan el deseo irresistible de compra.
     * OFFER_CTA: Tomas del producto completo, empaque, precio, descuento o presentación final para cerrar la venta.
   - En cada escena asigna el "media_file" idóneo para ese momento de la narración, junto con su "narrative_role" y "order_reason".

2. EL GANCHO DE 3 SEGUNDOS (HOOK OBLIGATORIO - Escena 1):
   - Los primeros 3 segundos deciden el éxito del anuncio.
   - Debe detener el scroll de golpe con:
     * Una pregunta provocativa sobre un dolor del cliente ("¿Sigues cometiendo este error con tu...?").
     * Un patrón disruptivo o curiosidad extrema ("Nadie te dijo esto sobre...").
     * Una afirmación contundente contra el producto tradicional ("Deja de gastar en X...").
   - NUNCA abras con saludos aburridos ("Hola amigos", "Hoy les traigo...").

3. ESTRUCTURA AIDA DINÁMICA (20 a 35 segundos en total):
   - Escena 1 (0-3s): GANCHO (Hook) de alto impacto visual y sonoro con la mejor toma introductoria.
   - Escena 2 (3-9s): EL PROBLEMA / AGITACIÓN (El dolor o frustración que sufre el cliente).
   - Escena 3 (9-16s): LA SOLUCIÓN / DEMOSTRACIÓN (Presentación del producto en acción o detalle).
   - Escena 4 (16-22s): BENEFICIOS CLAVE Y DIFERENCIALES (Por qué este producto es superior o único).
   - Escena 5 / Final (22-28s): OFERTA Y LLAMADO A LA ACCIÓN (CTA claro: "Haz clic", "Aprovecha el envío gratis hoy").

4. ESTILO DE LENGUAJE:
   - Natural, enérgico, conversacional, como una recomendación de confianza o un creador de contenido genuino.
   - Frases cortas y contundentes (8 a 15 palabras por escena).
   - Palabras fáciles de pronunciar para el motor de voz (TTS).

5. FORMATO DE SALIDA (ESTRICTAMENTE JSON):
Debes responder ÚNICAMENTE con un objeto JSON válido con la siguiente estructura:
{
  "product_name": "Nombre conciso del producto o servicio",
  "hook_title": "TITULAR CORTO EN MAYÚSCULAS (3 a 6 palabras) para superponer en pantalla en segundos 0-3",
  "target_audience": "Público objetivo",
  "music_genre": "commercial_trap | tech_electronic | upbeat_pop | chill_lofi | energetic_stomp",
  "target_bpm": 124,
  "music_vibe_reason": "Explicación breve de por qué este ritmo eleva la conversión del producto",
  "scenes": [
    {
      "scene_number": 1,
      "media_file": "nombre_exacto_del_archivo.jpg",
      "narrative_role": "HOOK_HERO | PROBLEM | DEMO_FEATURE | DESIRE_BENEFIT | OFFER_CTA",
      "order_reason": "Breve explicación de por qué este archivo específico va en esta posición de la narrativa",
      "narration": "Texto exacto que dirá la voz en off en esta escena",
      "visual_focus": "Qué debe mostrarse o enfocarse de la foto/video asignada",
      "callout_text": "Texto breve de apoyo visual para subtítulo (ej: 'Calidad Premium')"
    }
  ]
}
"""


def _encode_image_to_base64(image_path: Path, max_dim: int = 768) -> Optional[str]:
    """Reads and encodes an image into base64, optionally downscaling if pillow is available."""
    if not image_path.exists() or not image_path.is_file():
        return None
    try:
        from PIL import Image
        import io
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            # Downscale proportionally for fast API transfer
            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=82)
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception:
        # Fallback to direct raw read
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return None


class AdCopywriter:
    """Specialized commercial copywriter for user-supplied media."""

    def __init__(
        self,
        gemini_key: Optional[str] = None,
        groq_key: Optional[str] = None,
        openai_key: Optional[str] = None,
    ):
        self.gemini_key = sanitize_env_value(gemini_key or GEMINI_API_KEY)
        self.groq_key = sanitize_env_value(groq_key or GROQ_API_KEY)
        self.openai_key = sanitize_env_value(openai_key or OPENAI_API_KEY)
        self.system_prompt = AD_SYSTEM_PROMPT

    def build_user_prompt(
        self,
        media_files: List[Path],
        user_prompt: str,
        product_name: Optional[str] = None,
        offer: Optional[str] = None,
        cta: Optional[str] = None,
        target_duration: int = 25,
        language: str = "es",
    ) -> str:
        """Constructs the comprehensive user prompt sent to the LLM."""
        num_scenes = max(3, min(len(media_files), 7))
        file_summary = "\n".join(
            [f"  - Recurso [{i+1}]: '{f.name}' ({'Video dinámico' if f.suffix.lower() in ('.mp4', '.mov', '.webm') else 'Foto estática'})"
             for i, f in enumerate(media_files[:num_scenes])]
        )

        prompt_lines = [
            f"Crea un anuncio publicitario de alta conversión para un video de formato vertical (9:16).",
            f"Archivos multimedia disponibles del producto ({len(media_files[:num_scenes])} tomas):",
            file_summary,
            f"\n🎯 DIRECTIVA DE ORDENAMIENTO VISUAL Y NARRATIVO (CRUCIAL):",
            f"- Examina lo que muestra cada foto y video recibido.",
            f"- Determina TÚ el orden más persuasivo para la narrativa comercial AIDA (Gancho ➔ Problema ➔ Demostración ➔ Deseo ➔ Oferta/CTA).",
            f"- NO sigas obligatoriamente el orden numérico o alfabético. Asigna a la Escena 1 el archivo con mayor impacto para captar la atención en el segundo 0 ('HOOK_HERO').",
            f"- En cada escena de 'scenes', asigna el nombre exacto del archivo en el campo 'media_file', su rol publicitario en 'narrative_role', y una breve justificación en 'order_reason'.",
            f"\nInstrucciones del anunciante:",
            f"- Descripción/Objetivo del anuncio: {user_prompt}",
        ]

        if product_name:
            prompt_lines.append(f"- Nombre del producto/servicio: {product_name}")
        if offer:
            prompt_lines.append(f"- Oferta o promoción especial: {offer}")
        if cta:
            prompt_lines.append(f"- Llamado a la acción (CTA) deseado: {cta}")

        prompt_lines.extend([
            f"\nRequisitos técnicos:",
            f"- Duración total aproximada: {target_duration} segundos (~{round(target_duration/num_scenes, 1)}s por escena).",
            f"- Idioma de la locución: {'Español' if language == 'es' else language}.",
            f"- Cada escena DEBE tener un texto de narración ('narration') fluido, persuasivo y sin emojis ni asteriscos.",
            f"- El 'hook_title' debe ser un gancho en 3 a 5 palabras mayúsculas llamativas.",
            f"- Devuelve ÚNICAMENTE el JSON válido con el esquema especificado.",
        ])

        return "\n".join(prompt_lines)

    def generate_ad_script(
        self,
        media_files: List[Path],
        user_prompt: str,
        product_name: Optional[str] = None,
        offer: Optional[str] = None,
        cta: Optional[str] = None,
        target_duration: int = 25,
        language: str = "es",
        include_vision: bool = True,
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Generates an ad script.
        Returns:
            (script_dict, user_prompt_string)
        """
        prompt_text = self.build_user_prompt(
            media_files=media_files,
            user_prompt=user_prompt,
            product_name=product_name,
            offer=offer,
            cta=cta,
            target_duration=target_duration,
            language=language,
        )

        num_scenes = max(3, min(len(media_files), 7))

        # 1. Try Gemini (with multimodal vision if available)
        if self.gemini_key:
            print("  ⚡ Analizando imágenes y generando guion publicitario con Google Gemini Vision...")
            script = self._call_gemini(
                prompt_text=prompt_text,
                media_files=media_files[:num_scenes] if include_vision else [],
            )
            if script and self._validate_ad_script(script, num_scenes):
                return script, prompt_text

        # 2. Try Groq (LPU fast text generation)
        if self.groq_key:
            print("  ⚡ Generando guion publicitario con Groq LPU...")
            script = self._call_groq(prompt_text=prompt_text)
            if script and self._validate_ad_script(script, num_scenes):
                return script, prompt_text

        # 3. Try OpenAI
        if self.openai_key:
            print("  ⚡ Generando guion publicitario con OpenAI...")
            script = self._call_openai(
                prompt_text=prompt_text,
                media_files=media_files[:num_scenes] if include_vision else [],
            )
            if script and self._validate_ad_script(script, num_scenes):
                return script, prompt_text

        # 4. Fallback Rule-Based Commercial Script Generator
        print("  📢 Creando guion publicitario optimizado con plantilla comercial de alta conversión...")
        script = self._generate_commercial_fallback(
            media_files=media_files[:num_scenes],
            user_prompt=user_prompt,
            product_name=product_name,
            offer=offer,
            cta=cta,
            target_duration=target_duration,
        )
        return script, prompt_text

    def _call_gemini(
        self,
        prompt_text: str,
        media_files: List[Path] = []
    ) -> Optional[Dict[str, Any]]:
        """Call Gemini REST API with optional multimodal vision parts."""
        models = ["gemini-2.5-flash", "gemini-flash-latest"]
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Connection": "close"
        }

        # Build parts list
        parts: List[Dict[str, Any]] = []

        # Add image and video frame data tagged with file names
        image_count = 0
        for idx, f in enumerate(media_files):
            tipo = "Video dinámico" if f.suffix.lower() in (".mp4", ".mov", ".webm") else "Foto"
            temp_thumb = None
            if f.suffix.lower() in (".mp4", ".mov", ".webm"):
                temp_thumb = TEMP_DIR / f"thumb_vision_{idx+1}_{f.stem}.jpg"
                try:
                    subprocess.run([
                        "ffmpeg", "-y", "-ss", "00:00:01", "-i", str(f),
                        "-vframes", "1", "-q:v", "3", str(temp_thumb)
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                except Exception:
                    temp_thumb = None

            img_path = temp_thumb if (temp_thumb and temp_thumb.exists()) else f
            if img_path.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                b64 = _encode_image_to_base64(img_path)
                if b64:
                    parts.append({"text": f"--- MUESTRA VISUAL {idx+1} ---\nNombre de archivo: '{f.name}'\nTipo: {tipo}"})
                    parts.append({
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": b64
                        }
                    })
                    image_count += 1
                    if image_count >= 7:
                        break

        # Append instructions text
        parts.append({"text": prompt_text})

        payload = {
            "systemInstruction": {
                "parts": [{"text": self.system_prompt}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": parts
                }
            ],
            "generationConfig": {
                "temperature": 0.65,
                "topP": 0.95,
                "responseMimeType": "application/json",
                "maxOutputTokens": 2048
            }
        }

        data_bytes = json.dumps(payload).encode("utf-8")

        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
            try:
                req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=35) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    text = resp_json["candidates"][0]["content"]["parts"][0]["text"]
                    clean_text = self._clean_json_markdown(text)
                    return json.loads(clean_text)
            except Exception as e:
                # Try next model if any error
                continue

        return None

    def _call_groq(self, prompt_text: str) -> Optional[Dict[str, Any]]:
        """Call Groq API for lightning fast commercial copywriting."""
        model = GROQ_MODEL or "llama-3.3-70b-versatile"
        url = f"{GROQ_API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json",
            "Connection": "close"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt_text}
            ],
            "temperature": 0.65,
            "response_format": {"type": "json_object"}
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=25) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                raw_content = resp_json["choices"][0]["message"]["content"]
                clean_text = self._clean_json_markdown(raw_content)
                return json.loads(clean_text)
        except Exception:
            return None

    def _call_openai(self, prompt_text: str, media_files: List[Path] = []) -> Optional[Dict[str, Any]]:
        """Call OpenAI API with optional vision."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }

        user_content: List[Dict[str, Any]] = [{"type": "text", "text": prompt_text}]
        for f in media_files[:4]:
            if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                b64 = _encode_image_to_base64(f)
                if b64:
                    mime = "image/png" if f.suffix.lower() == ".png" else "image/jpeg"
                    user_content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"}
                    })

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.65
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                raw_content = resp_json["choices"][0]["message"]["content"]
                clean_text = self._clean_json_markdown(raw_content)
                return json.loads(clean_text)
        except Exception:
            return None

    def _generate_commercial_fallback(
        self,
        media_files: List[Path],
        user_prompt: str,
        product_name: Optional[str] = None,
        offer: Optional[str] = None,
        cta: Optional[str] = None,
        target_duration: int = 25,
    ) -> Dict[str, Any]:
        """Provides an immediate, high-converting ad copy fallback if no API keys are present."""
        clean_product = product_name or "este producto"
        clean_offer = offer or "disponible por tiempo limitado"
        clean_cta = cta or "¡Haz clic en el enlace y pide el tuyo hoy mismo!"

        # Extract main concept from prompt
        concept = user_prompt.strip().rstrip(".,") if user_prompt else "lo que siempre necesitaste"

        num_scenes = max(3, len(media_files))

        # Dynamic template scenes
        template_narrations = [
            f"¡Espera un segundo! Si estás buscando {concept}, tienes que ver esto.",
            f"Olvídate de las opciones ordinarias que no cumplen lo que prometen.",
            f"Mira los acabados y la calidad de {clean_product}, diseñado para darte resultados reales.",
            f"Cada detalle está pensado para hacer tu vida más fácil y práctica.",
            f"Aprovecha porque está {clean_offer}. {clean_cta}"
        ]

        # Smart narrative ordering heuristic for media files
        def get_media_role_score(f: Path) -> Tuple[int, str, str]:
            name = f.name.lower()
            if any(k in name for k in ["frontal", "hero", "portada", "principal", "main", "01"]):
                return (1, "HOOK_HERO", "Toma principal o frontal elegida para apertura y retención inmediata.")
            elif any(k in name for k in ["problema", "dolor", "antes", "error", "diferencia"]):
                return (2, "PROBLEM", "Toma seleccionada para evidenciar el problema o dolor.")
            elif f.suffix.lower() in (".mp4", ".mov", ".webm") or any(k in name for k in ["video", "ergonomia", "detalle", "accion", "uso", "demo"]):
                return (3, "DEMO_FEATURE", "Toma de acción o detalle seleccionada para demostrar el funcionamiento.")
            elif any(k in name for k in ["bateria", "calidad", "resistencia", "duracion", "beneficio"]):
                return (4, "DESIRE_BENEFIT", "Toma seleccionada para resaltar beneficios clave y durabilidad.")
            elif any(k in name for k in ["oferta", "precio", "descuento", "lanzamiento", "cta", "final", "caja", "empaque"]):
                return (5, "OFFER_CTA", "Toma seleccionada para el cierre con oferta y llamado a la acción.")
            else:
                return (3, "DEMO_FEATURE", "Toma de apoyo para enriquecer la demostración visual.")

        sorted_files = sorted(media_files, key=lambda f: get_media_role_score(f)[0]) if media_files else []

        # Adjust length to match num_scenes
        scenes = []
        for i in range(num_scenes):
            narration_idx = min(i, len(template_narrations) - 1)
            assigned_file = sorted_files[i % len(sorted_files)] if sorted_files else None
            role = "DEMO_FEATURE"
            reason = "Toma visual integrada en la narrativa."
            fname = f"toma_{i+1}.jpg"
            if assigned_file:
                _, role, reason = get_media_role_score(assigned_file)
                fname = assigned_file.name

            scenes.append({
                "scene_number": i + 1,
                "media_file": fname,
                "narrative_role": role,
                "order_reason": reason,
                "narration": template_narrations[narration_idx],
                "visual_focus": f"Detalle destacado en '{fname}'",
                "callout_text": "Calidad Premium" if i == 0 else ("Garantía Total" if i == num_scenes-1 else "Innovación")
            })

        hook_word = clean_product.upper() if len(clean_product.split()) <= 4 else "¡NO BUSQUES MÁS!"

        # Music selection heuristic based on keywords
        combined_text = f"{clean_product} {concept} {user_prompt}".lower()
        if any(w in combined_text for w in ["audio", "auricular", "audifono", "tech", "gadget", "app", "smart", "reloj", "computador", "pro"]):
            music_genre = "tech_electronic"
            target_bpm = 124
            vibe_reason = "Ritmo futurista y limpio (124 BPM) para sincronizar cortes visuales de tecnología y gadgets."
        elif any(w in combined_text for w in ["fitness", "gym", "deporte", "urgente", "fuerte", "rapido", "correr"]):
            music_genre = "energetic_stomp"
            target_bpm = 138
            vibe_reason = "Alta energía e intensidad (138 BPM) con cortes rápidos para deportes y acción."
        elif any(w in combined_text for w in ["skincare", "crema", "cafe", "piel", "belleza", "relax", "vela", "aroma", "paz"]):
            music_genre = "chill_lofi"
            target_bpm = 92
            vibe_reason = "Vibra relajante y elegante (92 BPM) con transiciones suaves para cuidado personal y bienestar."
        elif any(w in combined_text for w in ["hogar", "cocina", "limpieza", "familia", "comida", "juguete"]):
            music_genre = "upbeat_pop"
            target_bpm = 120
            vibe_reason = "Vibra alegre y positiva (120 BPM) ideal para productos cotidianos y de hogar."
        else:
            music_genre = "commercial_trap"
            target_bpm = 130
            vibe_reason = "Bajos 808 contundentes y percusión moderna (130 BPM) para impacto comercial en TikTok y Reels."

        return {
            "product_name": clean_product,
            "hook_title": f"¡DESCUBRE {hook_word}!",
            "target_audience": "Público general interesado en calidad",
            "music_genre": music_genre,
            "target_bpm": target_bpm,
            "music_vibe_reason": vibe_reason,
            "scenes": scenes
        }

    def _clean_json_markdown(self, text: str) -> str:
        """Strip markdown fences ```json ... ``` from LLM response."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
        return text.strip()

    def _validate_ad_script(self, script: Dict[str, Any], expected_scenes: int) -> bool:
        """Validates that the returned JSON conforms to required schema."""
        if not isinstance(script, dict):
            return False
        scenes = script.get("scenes")
        if not isinstance(scenes, list) or len(scenes) == 0:
            return False
        for s in scenes:
            if not isinstance(s, dict) or not s.get("narration"):
                return False
        return True
