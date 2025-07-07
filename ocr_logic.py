import pytesseract
import re
import sys

def extract_workout_data(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    
    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Cleanups
    text = text.replace("’", "'").replace("”", '"').replace("“", '"')

    # Distance
    distance_match = re.search(r"(\d+\.\d+)\s*km", text)

    # Time
    time_match = re.search(r"([0-9]{1,2}:[0-9]{2})", text)

    # Pace
    pace_match = re.search(r"([0-9]{1,2}'[0-9]{1,2})", text)

    # Splits
    split_pattern = re.findall(r"(\d\.\d{2})\s+km.*?(\d{1,2}:\d{2}).*?(\d{1,2}'\d{2})", text)

    splits = []
    for dist, time, pace in split_pattern:
        splits.append({
            "distance": dist + " km",
            "time": time,
            "pace": pace + "/km"
        })

    return {
        "distance": distance_match.group(1) + " km" if distance_match else "Unknown",
        "time": time_match.group(1) if time_match else "Unknown",
        "pace": pace_match.group(1) + "/km" if pace_match else "Unknown",
        "splits": splits
    }
