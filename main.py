from fastapi import FastAPI
from fastapi import UploadFile, File
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pathlib import Path

from typing import TypedDict
from PIL import Image
import numpy as np

class ImageAngle(TypedDict):
    name: str
    angle: int

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Ensure uploads folder exists!
# Create if not, and mount

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

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

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
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

@app.get("/uploads-list")
async def uploads_list():
    images: list[ImageAngle] = []

    for f in UPLOAD_DIR.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        angle = avg_rgb(f)

        image: ImageAngle = {
            "name": f.name,
            "angle": angle,
        }

        images.append(image)
    
    images.sort(key=lambda img: img["angle"])
    
    files = [img["name"] for img in images]
    return {"files": files}
    
# Image processing

def avg_rgb(file: Path):
    img = Image.open(file).convert("RGB").resize((64, 64))
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
    # ELSE RAISE EXCEPTION

    if h < 0:
        h += 360
    
    return int(h)