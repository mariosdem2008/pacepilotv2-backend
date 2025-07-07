from fastapi import FastAPI, File, UploadFile
from ocr_logic import extract_workout_data
from PIL import Image
import io

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "PacePilot Screenshot OCR Backend"}

app.post("/analyze-screenshot")
async def analyze_screenshot(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}")
    image = Image.open(io.BytesIO(await file.read()))
    print("Image loaded")

    try:
        data = extract_workout_data(image)
        print("Workout extracted")
        return {"status": "ok", "workout": data}
    except Exception as e:
        print("ERROR:", e)
        return {"status": "error", "message": str(e)}
