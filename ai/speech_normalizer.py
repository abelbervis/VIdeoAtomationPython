"""
Phonetic Text Normalizer for Technical Cloud Spanish Speech.
Cleans and normalizes script text before sending to Text-to-Speech (TTS) engines,
preventing speech artifacts like "acento gcloud...", spelling out acronyms incorrectly,
or stuttering on command flags.
"""

import re
from typing import List


# Technical replacements for spoken Spanish
TECH_SPOKEN_REPLACEMENTS = [
    # Command & CLI syntaxes
    (r"`gcloud\s+([^`]+)`", r"el comando gcloud \1"),
    (r"`gsutil\s+([^`]+)`", r"el comando gsutil \1"),
    (r"`([^`]+)`", r"\1"),  # Remove any remaining backticks
    
    # Flags into spoken words
    (r"--cpu-boost\b", "opción cpu boost"),
    (r"--allow-unauthenticated\b", "opción allow unauthenticated"),
    (r"--min-instances\b", "opción min instances"),
    (r"--max-instances\b", "opción max instances"),
    (r"--location\b", "opción location"),
    (r"--region\b", "opción region"),
    (r"--image\b", "opción image"),
    (r"--range\b", "opción range"),
    (r"--network\b", "opción network"),
    (r"--project\b", "opción project"),
    (r"--member\b", "opción member"),
    (r"--role\b", "opción role"),
    (r"--uniform-bucket-level-access\b", "opción acceso uniforme a nivel de bucket"),
    
    # Acronyms and Technical abbreviations
    (r"\bUBLA\b", "U-B-L-A"),
    (r"\bIAM\b", "I-A-M"),
    (r"\bVPC\b", "V-P-C"),
    (r"\bGCP\b", "Google Cloud"),
    (r"\bSQL\b", "ese-cu-ele"),
    (r"\bCloud SQL\b", "Cloud ese-cu-ele"),
    (r"\bCLI\b", "C-L-I"),
    (r"\bAPI\b", "A-P-I"),
    (r"\bAPIs\b", "A-P-Is"),
    (r"\bVM\b", "máquina virtual"),
    (r"\bVMs\b", "máquinas virtuales"),
    (r"\bSO\b", "sistema operativo"),
    (r"\bWAF\b", "W-A-F"),
    (r"\bDDoS\b", "ataques de denegación de servicio"),
    (r"\bgRPC\b", "G-R-P-C"),
    (r"\bHTTPS\b", "H-T-T-P-S"),
    (r"\bHTTP\b", "H-T-T-P"),
    (r"\bIP\b", "I-P"),
    (r"\bIPs\b", "I-Ps"),
    (r"\bNAT\b", "Nat"),
    (r"\bCloud NAT\b", "Cloud Nat"),
    (r"\bJSON\b", "yei-son"),
    (r"\bDocker\b", "Dóker"),
    (r"\bCold start\b", "arranque en frío"),
    (r"\bcold start\b", "arranque en frío"),
    (r"\bcold starts\b", "arranques en frío"),
    (r"\bColdline\b", "Cold-line"),
    (r"\bNearline\b", "Near-line"),
    (r"\bArchive\b", "Ar-kaiv"),
    (r"\bStandard\b", "estándar"),
    (r"\bAuto-scaling\b", "escalado automático"),
    (r"\bauto-scale\b", "escalado automático"),
    (r"\bServerless\b", "serverless"),
    (r"\bBucket\b", "bucket"),
    (r"\bBuckets\b", "buckets"),
    (r"/28\b", " barra veintiocho"),
    (r"0\.\.N\b", "cero a N"),
    (r"24/7\b", "veinticuatro siete"),
    (r"0€\b", "cero euros"),
    (r"€\b", " euros"),
    (r"\$\s*", ""),  # Strip terminal prompt dollar signs
]


def clean_phonetics_for_speech(text: str) -> str:
    """
    Transforms raw script dialogue into pristine spoken Spanish for TTS:
    - Strips all markdown quotes, backticks, asterisks, hashtags
    - Expands cloud commands, options, and acronyms phonetically
    - Prevents TTS engines from speaking punctuation marks like 'acento', 'barra', etc.
    """
    if not text:
        return ""

    cleaned = text.strip()

    # Apply technical spoken expansions
    for pattern, replacement in TECH_SPOKEN_REPLACEMENTS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    # Strip markdown bold, italics, backticks, hashes, brackets
    cleaned = re.sub(r"[`*#_~]", "", cleaned)
    cleaned = re.sub(r"\[.*?\]", "", cleaned)  # Bracketed stage directions like [Risas]
    
    # Strip straight and smart quotes so they don't produce clicks or pauses
    quote_chars = r"['\"`‘’“”«»„‟‹›]"
    cleaned = re.sub(quote_chars, "", cleaned)

    # Normalize hyphens and dashes into natural pauses
    cleaned = re.sub(r"\s+-\s+", ", ", cleaned)
    cleaned = re.sub(r"--+", " ", cleaned)

    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def split_into_tts_clauses(text: str, max_clause_len: int = 140) -> List[str]:
    """
    Splits long sentences into natural breathing clauses at punctuation boundaries
    to ensure the TTS endpoint never truncates sentences longer than 200 characters.
    """
    clean = clean_phonetics_for_speech(text)
    if len(clean) <= max_clause_len:
        return [clean]

    # Split by major punctuation first
    parts = re.split(r"([.!?;:,])", clean)
    clauses: List[str] = []
    current = ""

    for i in range(0, len(parts), 2):
        chunk = parts[i].strip()
        sep = parts[i + 1] if i + 1 < len(parts) else ""
        candidate = f"{chunk}{sep}".strip()
        if not candidate:
            continue

        if len(current) + len(candidate) + 1 <= max_clause_len:
            current = f"{current} {candidate}".strip()
        else:
            if current:
                clauses.append(current)
            current = candidate

    if current:
        clauses.append(current)

    return clauses if clauses else [clean]
