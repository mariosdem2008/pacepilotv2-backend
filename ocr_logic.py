import pytesseract
import re

def extract_workout_data(image):
    text = pytesseract.image_to_string(image, config='--psm 6')

    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Fix OCR errors
    text = text.replace("’", "'").replace("”", '"').replace("“", '"')
    text = text.replace("istance", "Distance")
    text = text.replace("km/h", "km")

    # Distance
    distance_match = re.search(r"(\d+(\.\d+)?)\s*Distance", text)

    # Average Pace
    avg_pace_match = re.search(r"Average\s*([0-9]{1,2}'[0-9]{2})", text)

    # Best Pace
    best_pace_match = re.search(r"Best\s*km\s*([0-9]{1,2}'[0-9]{2})", text)

    # Extract time specifically near "Activity Time"
    time = "Unknown"
    activity_time_section = re.search(r"([\d:]{4,5}).{0,10}Activity\s*Time", text)
    if activity_time_section:
        time = activity_time_section.group(1)
    else:
        # fallback: pick the first valid time not surrounded by pace-like characters
        time_candidates = re.finditer(r"\b([0-2]?[0-9]:[0-5][0-9])\b", text)
        for match in time_candidates:
            context = text[max(0, match.start() - 10):match.end() + 10]
            if "'" not in context:  # exclude pace-like strings
                time = match.group(1)
                break

    return {
        "distance": distance_match.group(1) + " km" if distance_match else "Unknown",
        "time": time,
        "pace": avg_pace_match.group(1) + "/km" if avg_pace_match else "Unknown",
        "best_pace": best_pace_match.group(1) + "/km" if best_pace_match else "Unknown"
    }
