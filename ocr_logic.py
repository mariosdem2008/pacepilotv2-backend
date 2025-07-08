import pytesseract
import re

def extract_workout_data(image):
    text = pytesseract.image_to_string(image, config='--psm 6')

    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Fix OCR artifacts
    text = text.replace("’", "'").replace("”", '"').replace("“", '"')
    text = text.replace("istance", "Distance")
    text = text.replace("km/h", "km")

    # Distance
    distance_match = re.search(r"(\d+(\.\d+)?)\s*Distance", text)

    # Avg pace
    avg_pace_match = re.search(r"Average\s*([0-9]{1,2}'[0-9]{2})", text)

    # Best pace
    best_pace_match = re.search(r"Best\s*km\s*([0-9]{1,2}'[0-9]{2})", text)

    # Time from line before "Activity Time"
    time = "Unknown"
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "Activity Time" in line:
            if i > 0:
                match = re.search(r"([0-2]?[0-9]:[0-5][0-9])", lines[i - 1])
                if match:
                    time = match.group(1)
            break

    # Extract splits
    splits = []
    for line in lines:
        # Match example: "1 1.00 km 3:24.23 3'24" /km"
        match = re.match(r"\s*\d+\s+(\d\.\d{2})\s*km\s+(\d{1,2}:\d{2})[\.:]\d{1,2}\s+(\d{1,2}'\d{2})", line)
        if match:
            dist, split_time, pace = match.groups()
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
