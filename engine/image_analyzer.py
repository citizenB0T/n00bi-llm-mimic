import base64
import re
import struct
import random
from typing import Dict, Any, Optional, Tuple

def get_image_dimensions(data: bytes, mime_type: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Extracts image dimensions (width, height) using pure Python standard library binary inspection.
    Supports PNG, JPEG, GIF, and WebP.
    """
    try:
        # PNG (Bytes 16..24 contain width and height as 32-bit big-endian unsigned integers)
        if data.startswith(b'\x89PNG\r\n\x1a\n') and len(data) >= 24:
            w, h = struct.unpack(">II", data[16:24])
            return w, h

        # GIF (Bytes 6..10 contain width and height as 16-bit little-endian unsigned integers)
        if data.startswith((b'GIF87a', b'GIF89a')) and len(data) >= 10:
            w, h = struct.unpack("<HH", data[6:10])
            return w, h

        # JPEG (Scan segments for SOF0..SOF2: 0xFF, 0xC0..0xC3)
        if data.startswith(b'\xff\xd8'):
            offset = 2
            while offset < len(data) - 9:
                marker, code = struct.unpack(">BB", data[offset:offset+2])
                if marker != 0xFF:
                    break
                offset += 2
                # Standalone markers with no payload length
                if code in (0xD8, 0xD9, 0x01, 0x00) or (0xD0 <= code <= 0xD7):
                    continue
                length, = struct.unpack(">H", data[offset:offset+2])
                # SOF markers: 0xC0 (baseline), 0xC1 (extended), 0xC2 (progressive)
                if code in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", data[offset+3:offset+7])
                    return w, h
                offset += length

        # WEBP
        if data.startswith(b'RIFF') and data[8:12] == b'WEBP' and len(data) >= 30:
            # VP8
            if data[12:16] == b'VP8 ' and len(data) >= 30:
                w, h = struct.unpack("<HH", data[26:30])
                return w & 0x3fff, h & 0x3fff
            # VP8L (lossless)
            elif data[12:16] == b'VP8L' and len(data) >= 25:
                b0, b1, b2, b3 = data[21:25]
                w = 1 + (((b1 & 0x3f) << 8) | b0)
                h = 1 + (((b3 & 0x0f) << 10) | (b2 << 2) | ((b1 & 0xc0) >> 6))
                return w, h
            # VP8X (extended)
            elif data[12:16] == b'VP8X' and len(data) >= 30:
                w = 1 + (data[24] | (data[25] << 8) | (data[26] << 16))
                h = 1 + (data[27] | (data[28] << 8) | (data[29] << 16))
                return w, h
    except Exception:
        pass

    return None, None

def parse_image_metadata(data_url: str) -> Optional[Dict[str, Any]]:
    """
    Decodes a base64 data URL and computes format, file size, dimensions, and tone.
    e.g. data:image/jpeg;base64,...
    """
    if not data_url or not isinstance(data_url, str):
        return None

    match = re.match(r"^data:(image\/[a-zA-Z0-9\+\-\.]+);base64,(.+)$", data_url, flags=re.DOTALL)
    if not match:
        return None

    mime_type = match.group(1).lower()
    b64_content = match.group(2)

    try:
        raw_bytes = base64.b64decode(b64_content)
    except Exception:
        return None

    size_bytes = len(raw_bytes)
    size_kb = round(size_bytes / 1024.0, 1)

    # Human readable format name
    format_map = {
        "image/jpeg": "JPEG",
        "image/jpg": "JPEG",
        "image/png": "PNG",
        "image/webp": "WebP",
        "image/gif": "GIF",
        "image/svg+xml": "SVG"
    }
    format_name = format_map.get(mime_type, mime_type.split("/")[-1].upper())

    width, height = get_image_dimensions(raw_bytes, mime_type)
    if not width:
        width = 1280
    if not height:
        height = 720

    # Approximate tone from sampling
    sample_sum = sum(raw_bytes[i] for i in range(0, min(len(raw_bytes), 2048), 8))
    avg_sample = sample_sum / max(1, (min(len(raw_bytes), 2048) // 8))
    tone = "lumineux" if avg_sample > 140 else "sombre" if avg_sample < 80 else "contrasté"

    return {
        "mime_type": mime_type,
        "format": format_name,
        "size_bytes": size_bytes,
        "size_kb": size_kb,
        "width": width,
        "height": height,
        "tone": tone,
        "data_url": data_url
    }

VISION_INTRO_VARIANTS = [
    "J'ai passé votre capture visuelle aux filtres de vision par ordinateur.",
    "Capture optique bien réceptionnée par mes sous-systèmes d'analyse matricielle.",
    "Vos pixels sont nets et votre transmission graphique a été décodée avec succès.",
    "Intéressant stimulus visuel soumis à notre grille d'évaluation !"
]

VISION_COMMENTARY_VARIANTS = [
    "Dans le cadre d'un protocole d'étalonnage déterministe, soumettre une image permet d'auditer mes couches convolutives. L'agencement des contrastes ({tone}) et la netteté spatiale sont remarquables.",
    "L'inspection des vecteurs chromatiques et des contours matriciels ne révèle aucune anomalie binaire. La composition est équilibrée et l'échantillonnage net.",
    "Mes réseaux de tenseurs optiques confirment une structure graphique conforme. Qu'il s'agisse d'un test de mes capacités multimodales ou d'un partage documentaire, le rendu est optimal."
]

def generate_vision_response(
    image_meta: Dict[str, Any],
    user_prompt: str,
    step_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Builds a simulated multimodal vision response from Prof. n00bi.
    """
    intro = random.choice(VISION_INTRO_VARIANTS)
    comment = random.choice(VISION_COMMENTARY_VARIANTS).format(
        tone=image_meta.get("tone", "contrasté"),
        format=image_meta.get("format", "PNG")
    )

    w = image_meta.get("width", 1280)
    h = image_meta.get("height", 720)
    fmt = image_meta.get("format", "Image")
    kb = image_meta.get("size_kb", 150)

    user_text_clause = f" À propos de votre remarque (*« {user_prompt} »*) :" if user_prompt and user_prompt.strip() else ""

    content = (
        f"{intro}{user_text_clause}\n\n"
        f"> [!NOTE]\n"
        f"> **Sous-système de Vision nOObi** : Flux matriciel décodé avec succès — **{fmt}** ({w}×{h} px, {kb} Ko, profil {image_meta.get('tone', 'équilibré')}). Intégrité spectrale : 100%.\n\n"
        f"{comment}\n\n"
        f"---\n\n"
        f"Mais ne nous laissons pas distraire par l'esthétique des pixels, le protocole d'étalonnage continue :\n\n"
        f"**{step_data.get('ai_message', '')}**"
    )

    thought = (
        f"Décodage du tenseur optique [{fmt} {w}x{h}, {kb}KB]. "
        f"Extraction de texture et corrélation contextuelle. Recadrage sur l'étape en cours."
    )

    return {
        "thought": thought,
        "content": content
    }
