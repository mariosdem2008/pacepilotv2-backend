from fastapi import FastAPI, File, UploadFile, Form
from typing import List
from ocr_logic import extract_workout_data, extract_workout_data_combined
from PIL import Image
import io

app = FastAPI()

@app.get("/ping")
def ping():
    print("🏓 PING received")
    return {"status": "alive"}

@app.get("/")
def read_root():
    return {"message": "PacePilot Screenshot OCR Backend"}

@app.post("/analyze-screenshot")  # Single image endpoint
async def analyze_screenshot(
    file: UploadFile = File(...),
    source: str = Form(...)
):
    image = Image.open(io.BytesIO(await file.read()))
    try:
        data = extract_workout_data(image, source)
        return {"status": "ok", "workout": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/analyze-screenshots-batch")  # Multiple images endpoint
async def analyze_screenshots_batch(
    files: List[UploadFile] = File(...),
    source: str = Form(...)
):
    print(f"📥 Received {len(files)} files from source: {source}", flush=True)

    images = [Image.open(io.BytesIO(await f.read())) for f in files]

    try:
        # Use your combined extractor for multiple images
        data = extract_workout_data_combined(images, source)
        return {"status": "ok", "workout": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
