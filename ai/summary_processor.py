"""
Summary Processor for Viral Topic Videos.
Transforms user-provided summaries, notes, articles, or transcripts into structured
high-retention video scripts and visual search tags.
"""

import os
import re
import sys
import json
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

from config import GEMINI_API_KEY, GROQ_API_BASE, GROQ_API_KEY, GROQ_MODEL, OPENAI_API_KEY, sanitize_env_value


def read_summary_from_input(prompt_text: Optional[str] = None) -> str:
    """Prompt the user interactively in the terminal to paste their summary or notes."""
    print("\n" + "=" * 65)
    print("📝 GENERADOR DE VIDEO A PARTIR DE UN RESUMEN O TEMA VIRAL")
    print("=" * 65)
    print("Pega a continuación el resumen, notas o transcripción del tema.")
    print("(Presiona Enter dos veces, o escribe 'FIN' en una línea nueva para terminar):\n" + "-" * 65)
    
    lines = []
    try:
        empty_count = 0
        while True:
            line = input()
            if line.strip().upper() == "FIN":
                break
            if not line.strip():
                empty_count += 1
                if empty_count >= 2 and lines:
                    break
            else:
                empty_count = 0
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass

    summary = "\n".join(lines).strip()
    return summary


def extract_topic_title_from_summary(
    summary_text: str,
    language: str = "es",
    gemini_key: Optional[str] = None,
    groq_key: Optional[str] = None,
    openai_key: Optional[str] = None
) -> str:
    """
    Extract a concise, viral, 2-to-5 word topic title from the summary text.
    Uses LLM if available, with a regex fallback.
    """
    cleaned_summary = summary_text.strip()
    if not cleaned_summary:
        return "Tema Viral"

    # Quick heuristic fallback if summary starts with a clear title line
    first_line = cleaned_summary.split("\n")[0].strip().strip("#*-_ ")
    if 3 <= len(first_line.split()) <= 6 and len(first_line) <= 45 and not first_line.endswith((".", "?", "!")):
        return first_line

    # Try Gemini API if key is available
    g_key = sanitize_env_value(gemini_key or GEMINI_API_KEY)
    if g_key and len(g_key) > 15:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={g_key}"
            prompt = (
                f"Extract a short, captivating 2-to-4 word video title in language '{language}' "
                f"for a YouTube Short based on this summary:\n\"\"\"\n{cleaned_summary[:600]}\n\"\"\"\n"
                f"Respond ONLY with the exact title in quotes, nothing else."
            )
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 60,
                    "thinkingConfig": {"thinkingBudget": 0}
                }
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "NASA-Shorts-Generator/1.0"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                title = data["candidates"][0]["content"]["parts"][0]["text"].strip().strip('"\' \n#*')
                if title and len(title) <= 50:
                    return title
        except Exception:
            pass

    # Heuristic fallback: clean the first sentence and extract a meaningful phrase
    # Replace numeric dots (10.000 -> 10000) so we don't break on numbers
    normalized = re.sub(r"(\d+)\.(\d+)", r"\1\2", cleaned_summary)
    sentences = re.split(r"[.!?\n]+", normalized)
    for s in sentences:
        s_clean = re.sub(r"[#*_\"'()]+", "", s).strip()
        words = s_clean.split()
        if len(words) >= 2:
            candidate_words = words[:6]
            stop_words = {"de", "la", "el", "en", "las", "los", "un", "una", "y", "a", "of", "the", "in", "and", "to"}
            while len(candidate_words) > 2 and candidate_words[-1].lower() in stop_words:
                candidate_words.pop()
            return " ".join(candidate_words)
            return " ".join(words[:5])

    return "Descubrimiento Viral"


def process_summary_mode(args) -> Tuple[str, str, None]:
    """
    Resolves summary text from --summary, --notes, or --summary-file,
    infers the topic if not specified, and constructs the grounded prompt context.
    Returns:
        (topic, grounded_context, trending_metadata=None)
    """
    summary_text = ""

    # 1. Load from file if --summary-file is provided
    if getattr(args, "summary_file", None):
        s_path = Path(args.summary_file).expanduser().resolve()
        if not s_path.exists() or not s_path.is_file():
            print(f"\n❌ Error: El archivo de resumen no existe: {s_path}")
            sys.exit(1)
        try:
            summary_text = s_path.read_text(encoding="utf-8").strip()
            print(f"\n📂 Resumen cargado exitosamente desde archivo: {s_path.name}")
        except Exception as e:
            print(f"\n❌ Error al leer el archivo de resumen: {e}")
            sys.exit(1)

    # 2. Or load from CLI text argument if --summary / --notes is provided
    elif getattr(args, "summary", None) is not None:
        raw_val = args.summary.strip() if isinstance(args.summary, str) else ""
        if raw_val:
            summary_text = raw_val
        else:
            summary_text = read_summary_from_input()

    if not summary_text:
        print("\n❌ Error: No se proporcionó ningún texto de resumen.")
        print("Uso: python main.py --summary \"Tu resumen aquí...\" o python main.py --summary-file notas.txt")
        sys.exit(1)

    # 3. Resolve or infer the topic
    if args.topic and args.topic.strip():
        topic = args.topic.strip()
    else:
        print("\n🔍 Detectando título y concepto principal a partir del resumen...")
        topic = extract_topic_title_from_summary(
            summary_text=summary_text,
            language=getattr(args, "language", "es"),
            gemini_key=getattr(args, "gemini_key", None),
            groq_key=getattr(args, "groq_key", None),
            openai_key=getattr(args, "openai_key", None)
        )

    # 4. Build high-retention grounded prompt context
    grounded_context = (
        f"RESUMEN Y NOTAS DEL TEMA VIRAL SUMINISTRADOS POR EL USUARIO:\n"
        f"\"\"\"\n{summary_text.strip()}\n\"\"\"\n\n"
        f"DIRECTIVAS ESTRICTAS DE ADAPTACIÓN A PARTIR DEL RESUMEN:\n"
        f"1. ADHERENCIA ESTRICTA A LOS HECHOS: El guión del video DEBE basarse 100% en la información, hechos y revelaciones de este resumen.\n"
        f"2. GANCHO VIRAL INMEDIATO (Escena 1): Formula una pregunta intrigante o una afirmación impactante que capture la esencia del resumen en los primeros 3 segundos.\n"
        f"3. ESTRUCTURA NARRATIVA: Desarrolla el tema a través de 4 o 5 escenas dinámicas, manteniendo al espectador inmerso hasta el desenlace.\n"
        f"4. PALABRAS CLAVE VISUALES (keywords): Proporciona términos de búsqueda en inglés directos, tangibles y visuales que coincidan con los conceptos clave descritos en el resumen."
    )

    word_count = len(summary_text.split())
    print("\n" + "=" * 65)
    print("📄 MODO RESUMEN ACTIVADO  |  Generador de Video desde Notas")
    print("=" * 65)
    print(f"🎯 Tema detectado: '{topic}'")
    print(f"📝 Longitud:       {len(summary_text)} caracteres (~{word_count} palabras)")
    print("=" * 65)

    return topic, grounded_context, None
