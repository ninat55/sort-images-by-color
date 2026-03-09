from pathlib import Path

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
    validate(file)
    await save(file)    
    return {"filename": file.filename, "content_type": file.content_type}

def validate(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG/PNG/WEBP images are supported.")

async def save(file: UploadFile):
    filename = file.filename
    contents = await file.read()
    path = UPLOAD_DIR / filename
    with open(path, "wb") as f:
        f.write(contents)

@app.post("/save-url")
async def save_url(data: URLRequest):
    # TODO: Validate URL!
    with open(URL_FILE, "a") as f:
        f.write(data.url + "\n")
    return {"url": data.url}

@app.get("/uploads-list")
async def uploads_list():
    images: list[ImageAngle] = []

    for f in UPLOAD_DIR.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        try:
            angle = avg_rgb(load_image_file(f))

            image: ImageAngle = {
                "type": "file",
                "src": f.name,
                "angle": angle,
            }

            images.append(image)
        except Exception as e:
            print(f"Failed to load image {f.name}: {e}")
            continue

    for url in load_hosted_urls():
        try:
            angle = avg_rgb(load_image_url(url))

            image: ImageAngle = {
                "type": "url",
                "src": url,
                "angle": angle,
            }
        
            images.append(image)
        except Exception as e:
            print(f"Failed to load image from URL {url}: {e}")
            continue

    images.sort(key=lambda img: img["angle"])
    files = [{"type": img["type"], "src": img["src"]} for img in images]
    return {"files": files}

def load_hosted_urls():
    if not URL_FILE.exists():
        return []

    with open(URL_FILE, "r") as f:
        urls = f.read().splitlines()
    return urls

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
    # TODO: handle else (raise exception?)

    if h < 0:
        h += 360
    
    return int(h)