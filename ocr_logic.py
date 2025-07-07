import pytesseract
import re

def extract_workout_data(image):
    text = pytesseract.image_to_string(image, config='--psm 6')

    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Fix some common OCR errors
    text = text.replace("’", "'").replace("”", '"').replace("“", '"')
    text = text.replace("istance", "Distance")
    text = text.replace("km/h", "km")  # sometimes OCR adds /h incorrectly

    # Distance (look for number before the word "Distance")
    distance_match = re.search(r"(\d+(\.\d+)?)\s*Distance", text)

    # Time: find something like 17:10
    time_match = re.search(r"([0-2]?[0-9]:[0-5][0-9])", text)

    # Average Pace: something like "Average 3'28"
    avg_pace_match = re.search(r"Average\s*([0-9]{1,2}'[0-9]{2})", text)

    # Best Pace: something like "Best km 3'19"
    best_pace_match = re.search(r"Best\s*km\s*([0-9]{1,2}'[0-9]{2})", text)

    return {
        "distance": distance_match.group(1) + " km" if distance_match else "Unknown",
        "time": time_match.group(1) if time_match else "Unknown",
        "pace": avg_pace_match.group(1) + "/km" if avg_pace_match else "Unknown",
        "best_pace": best_pace_match.group(1) + "/km" if best_pace_match else "Unknown"
    }
