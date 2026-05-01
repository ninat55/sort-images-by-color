from pathlib import Path
from urllib.parse import urlparse
import json

from fastapi import FastAPI
from fastapi import UploadFile, File
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

import requests
from io import BytesIO

from typing import TypedDict
from PIL import Image
import numpy as np

class URLRequest(BaseModel):
    url: str

class ImageRequest(BaseModel):
    type: str
    src: str
    angle: int

class ImageAngle(TypedDict):
    type: str
    src: str
    angle: int

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Ensure uploads folder exists!
# Create if not, and mount

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

URL_FILE = Path(f"{UPLOAD_DIR}/hosted_urls.txt")
CACHE_FILE = UPLOAD_DIR / "angle_cache.json"

def load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def save_cache(cache: dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def cache_key(type: str, src: str) -> str:
    return f"{type}:{src}"

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Allow cross-origin requests

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    validate_file(file)
    await save(file)

    path = UPLOAD_DIR / file.filename

    try:
        angle = avg_rgb(load_image_file(path))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image: {e}")

    cache = load_cache()
    cache[cache_key("file", file.filename)] = angle
    save_cache(cache)

    return {"type": "file", "src": file.filename, "angle": angle}

def validate_file(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG/PNG/WEBP/GIF images are supported.")

async def save(file: UploadFile):
    filename = file.filename
    contents = await file.read()
    path = UPLOAD_DIR / filename
    with open(path, "wb") as f:
        f.write(contents)

def validate_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise HTTPException(status_code=400, detail="URL must be a valid http or https address.")

@app.post("/save-url")
async def save_url(data: URLRequest):
    validate_url(data.url)

    if data.url in load_hosted_urls():
        raise HTTPException(status_code=409, detail="URL already exists.")

    try:
        angle = avg_rgb(load_image_url(data.url))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load image from URL: {e}")

    with open(URL_FILE, "a") as f:
        f.write(data.url + "\n")

    cache = load_cache()
    cache[cache_key("url", data.url)] = angle
    save_cache(cache)

    return {"type": "url", "src": data.url, "angle": angle}

# TODO: REVIEW
@app.post("/delete-image")
async def delete_image(data: ImageRequest):
    if data.type == "file":
        filename = Path(data.src).name
        path = UPLOAD_DIR / filename

        if not path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        path.unlink()
        cache = load_cache()
        cache.pop(cache_key("file", filename), None)
        save_cache(cache)
        return {"ok": True}

    elif data.type == "url":
        urls = load_hosted_urls()

        if data.src not in urls:
            raise HTTPException(status_code=404, detail="URL not found")

        urls.remove(data.src)

        with open(URL_FILE, "w") as f:
            if urls:
                f.write("\n".join(urls) + "\n")
            else:
                f.write("")

        cache = load_cache()
        cache.pop(cache_key("url", data.src), None)
        save_cache(cache)
        return {"ok": True}

    raise HTTPException(status_code=400, detail="Invalid image type")

@app.get("/uploads-list")
async def uploads_list():
    cache = load_cache()
    images: list[ImageAngle] = []

    for f in UPLOAD_DIR.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        try:
            key = cache_key("file", f.name)
            if key in cache:
                angle = cache[key]
            else:
                angle = avg_rgb(load_image_file(f))
                cache[key] = angle
                save_cache(cache)

            images.append({"type": "file", "src": f.name, "angle": angle})
        except Exception as e:
            print(f"Failed to load image {f.name}: {e}")
            continue

    for url in load_hosted_urls():
        try:
            key = cache_key("url", url)
            if key in cache:
                angle = cache[key]
            else:
                angle = avg_rgb(load_image_url(url))
                cache[key] = angle
                save_cache(cache)

            images.append({"type": "url", "src": url, "angle": angle})
        except Exception as e:
            print(f"Failed to load image from URL {url}: {e}")
            continue

    images.sort(key=lambda img: img["angle"])
    files = [{"type": img["type"], "angle": img["angle"], "src": img["src"]} for img in images]
    return {"files": files}

def load_hosted_urls():
    if not URL_FILE.exists():
        return []
    with open(URL_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

# Image processing

# TODO: revise error handling for image loading functions

def load_image_file(file: Path):
    try:
        return Image.open(file)
    except Exception as e:
        raise ValueError(f"Failed to load image: {e}")

def load_image_url(url: str):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "image/*,*/*;q=0.8",
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            raise ValueError("URL does not point to an image")

        return Image.open(BytesIO(response.content))
    except Exception as e:
        raise ValueError(f"Failed to load image from URL: {e}")

def avg_rgb(img: Image.Image):
    img = img.convert("RGB").resize((64, 64))
    arr = np.array(img)

    brightness = arr.mean(axis=2)

    mask = (brightness > 20) & (brightness < 235)
    filtered = arr[mask]

    if len(filtered) == 0:
        filtered = arr.reshape(-1, 3)

    avg = filtered.mean(axis=0)
    return hue_angle(tuple(avg.astype(int)))

def hue_angle(rgb: tuple[int, int, int]):
    r = rgb[0]/255
    g = rgb[1]/255
    b = rgb[2]/255

    c_max = max(r, g, b)
    c_min = min(r, g, b)

    delta = c_max - c_min

    if delta == 0:
        h = 0
    elif c_max == r:
        h = 60 * (((g - b)/delta) % 6)
    elif c_max == g:
        h = 60 * (((b - r)/delta) + 2)
    elif c_max == b:
        h = 60 * (((r - g)/delta) + 4)
    else:
        h = 0

    if h < 0:
        h += 360
    
    return int(h)