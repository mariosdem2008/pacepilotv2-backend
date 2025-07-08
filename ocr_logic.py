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

    # Extract time from line before "Activity Time"
    time = "Unknown"
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "Activity Time" in line:
            if i > 0:
                time_line = lines[i - 1]
                time_match = re.search(r"([0-2]?[0-9]:[0-5][0-9])", time_line)
                if time_match:
                    time = time_match.group(1)
            break

    # Extract splits
    splits = []
    split_pattern = re.findall(
        r"(\d\.\d{2})\s*km\s*[–\-]?\s*([0-9]{1,2}:[0-9]{2})\s*[–\-]?\s*([0-9]{1,2}'[0-9]{2})",
        text
    )
    for dist, split_time, pace in split_pattern:
        splits.append({
            "distance": f"{dist} km",
            "time": split_time,
            "pace": f"{pace}/km"
        })

    return {
        "distance": distance_match.group(1) + " km" if distance_match else "Unknown",
        "time": time,
        "pace": avg_pace_match.group(1) + "/km" if avg_pace_match else "Unknown",
        "best_pace": best_pace_match.group(1) + "/km" if best_pace_match else "Unknown",
        "splits": splits
    }
