import pytesseract
import re

def extract_workout_data(image):
    text = pytesseract.image_to_string(image, config='--psm 6')

    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Fix OCR typos
    text = text.replace("’", "'").replace("”", '"').replace("“", '"')
    text = text.replace("istance", "Distance")
    text = text.replace("km/h", "km")

    # Extract distance
    distance_match = re.search(r"(\d+(\.\d+)?)\s*Distance", text)

    # Extract average pace
    avg_pace_match = re.search(r"Average\s*([0-9]{1,2}'[0-9]{2})", text)

    # Extract best pace
    best_pace_match = re.search(r"Best\s*km\s*([0-9]{1,2}'[0-9]{2})", text)

    # Extract valid times (with ":" only, not with "'")
    time_matches = re.finditer(r"\b([0-2]?[0-9]:[0-5][0-9])\b", text)
    time = "Unknown"
    for match in time_matches:
        # Check surrounding context
        context = text[max(0, match.start() - 30):match.end() + 30]
        if "'" not in context:  # avoid pace
            time = match.group(1)
            break  # use first valid time

    return {
        "distance": distance_match.group(1) + " km" if distance_match else "Unknown",
        "time": time,
        "pace": avg_pace_match.group(1) + "/km" if avg_pace_match else "Unknown",
        "best_pace": best_pace_match.group(1) + "/km" if best_pace_match else "Unknown"
    }
