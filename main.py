from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from ocr_logic import extract_workout_data_combined
from PIL import Image
import io
from typing import List

app = FastAPI()

@app.get("/ping")
def ping():
    print("🏓 PING received")
    return {"status": "alive"}

print("✅ Backend started: This file is running.")

@app.get("/")
def read_root():
    return {"message": "PacePilot Screenshot OCR Backend"}

# NEW: Combine multiple screenshots into a single workout
@app.post("/analyze-screenshots")
async def analyze_screenshots(
    files: List[UploadFile] = File(...),
    source: str = Form(...)
):
    try:
        images = [Image.open(io.BytesIO(await f.read())) for f in files]
        data = extract_workout_data_combined(images, source)
        return {"status": "ok", "workout": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# OLD: Analyze one screenshot (still supported)
@app.post("/analyze-screenshot")
async def analyze_screenshot(
    file: UploadFile = File(...),
    source: str = Form(...)
):
    try:
        image = Image.open(io.BytesIO(await file.read()))
        from ocr_logic import extract_workout_data
        data = extract_workout_data(image, source)
        return {"status": "ok", "workout": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
