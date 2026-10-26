from pathlib import Path
from io import BytesIO
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_DIR = Path(os.getenv("EAGLE_INDEX_DIR", BASE_DIR / "image_index")).resolve()
INDEX_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_BYTES = 10 * 1024 * 1024
HASH_SIZE = 8

app = FastAPI(title="Eagle Eye API", version="2.0.0", description="Busca visual aproximada em um índice de imagens fornecidas pelo administrador.")
# GitHub Pages and other static frontends can call the public API. No credentials are used.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])

def load_image(data: bytes) -> Image.Image:
    try:
        image = Image.open(BytesIO(data))
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((1200, 1200))
        return image
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Arquivo inválido ou formato de imagem não suportado.") from exc

def average_hash(image: Image.Image) -> int:
    # Pure-Python average hash: Pillow only, no NumPy/Rust compilation.
    tiny = image.convert("L").resize((HASH_SIZE, HASH_SIZE), Image.Resampling.LANCZOS)
    pixels = list(tiny.getdata())
    mean = sum(pixels) / len(pixels)
    value = 0
    for pixel in pixels:
        value = (value << 1) | int(pixel >= mean)
    return value

def similarity(a: int, b: int) -> float:
    distance = (a ^ b).bit_count()
    return round((1 - distance / (HASH_SIZE * HASH_SIZE)) * 100, 1)

@app.get("/api/health")
def health():
    count = sum(1 for p in INDEX_DIR.rglob("*") if p.is_file() and p.suffix.lower() in ALLOWED)
    return {"ok": True, "service": "Eagle Eye", "indexed_images": count, "mode": "local-image-similarity"}

@app.post("/api/search")
async def search(file: UploadFile = File(...), limit: int = 12):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Envie um arquivo de imagem.")
    raw = await file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="A imagem precisa ter no máximo 10 MB.")
    query_hash = average_hash(load_image(raw))
    limit = max(1, min(limit, 30))
    found = []
    for path in INDEX_DIR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in ALLOWED:
            continue
        try:
            candidate_hash = average_hash(load_image(path.read_bytes()))
            found.append({"filename": path.name, "similarity": similarity(query_hash, candidate_hash), "url": "/image-index/" + path.relative_to(INDEX_DIR).as_posix()})
        except Exception:
            continue
    found.sort(key=lambda x: x["similarity"], reverse=True)
    return {"query": "average-hash-visual-similarity", "indexed_images": len(found), "results": found[:limit], "notice": "Similaridade visual aproximada; não confirma identidade de pessoas."}

app.mount("/image-index", StaticFiles(directory=str(INDEX_DIR)), name="image-index")
app.mount("/", StaticFiles(directory=str(BASE_DIR), html=True), name="frontend")
