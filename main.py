from fastapi import FastAPI, File, UploadFile, Form
from typing import List
from ocr_logic import extract_workout_data
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

@app.post("/analyze-screenshot")  # 👈 single image
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

@app.post("/analyze-screenshots-batch")  # 👈 multiple images
async def analyze_screenshots_batch(
    files: List[UploadFile] = File(...),
    source: str = Form(...)
):
    from PIL import Image
    import io

    print(f"📥 Received {len(files)} files from source: {source}", flush=True)

    # Combine all images vertically
    images = [Image.open(io.BytesIO(await f.read())) for f in files]
    widths, heights = zip(*(i.size for i in images))

    total_height = sum(heights)
    max_width = max(widths)

    combined_image = Image.new('RGB', (max_width, total_height))
    y_offset = 0
    for im in images:
        combined_image.paste(im, (0, y_offset))
        y_offset += im.size[1]

    # Process combined image
    try:
        data = extract_workout_data(combined_image, source)
        return {"status": "ok", "workout": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}



