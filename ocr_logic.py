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
    text = text.replace("km/h", "km")  # sometimes OCR adds /h incorrectly

    # Distance
    distance_match = re.search(r"(\d+(\.\d+)?)\s*Distance", text)

    # Average Pace: e.g. "Average 3'28"
    avg_pace_match = re.search(r"Average\s*([0-9]{1,2}'[0-9]{2})", text)

    # Best Pace: e.g. "Best km 3'19"
    best_pace_match = re.search(r"Best\s*km\s*([0-9]{1,2}'[0-9]{2})", text)

    # Time: find a clean time with ":" that’s not part of a pace (which has "'")
    time = "Unknown"
    time_candidates = list(re.finditer(r"\b([0-2]?[0-9]:[0-5][0-9])\b", text))
    for match in time_candidates:
        context = text[max(0, match.start() - 10):match.end() + 10]
        if "'" not in context:  # not part of a pace
            time = match.group(1)
            break

    return {
        "distance": distance_match.group(1) + " km" if distance_match else "Unknown",
        "time": time,
        "pace": avg_pace_match.group(1) + "/km" if avg_pace_match else "Unknown",
        "best_pace": best_pace_match.group(1) + "/km" if best_pace_match else "Unknown"
    }
