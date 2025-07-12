from fastapi import FastAPI, File, UploadFile, Form
from ocr_logic import extract_workout_data
from PIL import Image
import io

app = FastAPI()

@app.post("/")
def read_root():
    return {"message": "PacePilot Screenshot OCR Backend"}

@app.post("/analyze-screenshot")
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
