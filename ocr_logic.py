import pytesseract
from PIL import Image

def extract_workout_data(image: Image.Image):
    text = pytesseract.image_to_string(image)
    
    # Dummy logic — improve later!
    lines = text.split("\n")
    data = {}
    for line in lines:
        if "Distance" in line:
            data["distance"] = line.split(":")[-1].strip()
        elif "Pace" in line:
            data["pace"] = line.split(":")[-1].strip()
        elif "Time" in line:
            data["time"] = line.split(":")[-1].strip()
    
    return data
