"""
File and payload integrity validation utilities.
"""

import re
from fastapi import UploadFile, HTTPException

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp"
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# Magic byte signatures
MAGIC_NUMBERS = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp"
}

async def validate_image_file(file: UploadFile, max_size_mb: int = 15) -> bytes:
    """Validates uploaded image file type, size, and header signature."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Empty filename provided")
        
    ext = ("." + file.filename.split(".")[-1]).lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
        
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed size of {max_size_mb} MB"
        )
        
    # Check magic bytes
    is_valid_magic = False
    for magic in MAGIC_NUMBERS:
        if content.startswith(magic):
            is_valid_magic = True
            break
            
    if not is_valid_magic:
        raise HTTPException(status_code=400, detail="Corrupted or invalid image byte signature")
        
    return content

def sanitize_filename(filename: str) -> str:
    """Sanitizes filename against path traversal attacks."""
    cleaned = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename)
    return cleaned.strip("._") or "unnamed_sample.jpg"

