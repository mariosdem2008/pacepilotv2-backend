from fastapi import FastAPI, File, UploadFile
from ocr_logic import extract_workout_data
from PIL import Image
import io
import subprocess

app = FastAPI()

# Install Tesseract at startup (only works if you have root privileges)
@app.on_event("startup")
def install_tesseract():
    try:
        print("Installing Tesseract OCR...")
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "install", "-y", "tesseract-ocr"], check=True)
        print("✅ Tesseract installed successfully")
    except Exception as e:
        print("❌ Failed to install Tesseract:", e)

@app.get("/")
def read_root():
    return {"message": "PacePilot Screenshot OCR Backend"}

@app.post("/analyze-screenshot")
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
