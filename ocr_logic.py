import pytesseract
import re

def extract_workout_data(image):
    text = pytesseract.image_to_string(image, config='--psm 6')

    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    text = text.replace("’", "'").replace("”", '"').replace("“", '"')
    text = text.replace("istance", "Distance").replace("km/h", "km")

    # Distance
    distance_match = re.search(r"(\d+(\.\d+)?)\s*Distance", text)

    # Avg pace
    avg_pace_match = re.search(r"Average\s*([0-9]{1,2}'[0-9]{2})", text)

    # Best pace
    best_pace_match = re.search(r"Best\s*km\s*([0-9]{1,2}'[0-9]{2})", text)

    # Time extraction logic
    time = "Unknown"
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "Activity Time" in line:
            if i > 0:
                match = re.search(r"([0-2]?[0-9]:[0-5][0-9])", lines[i - 1])
                if match:
                    time = match.group(1)
            break

    # Splits extraction
    splits = []
    for line in lines:
        match = re.match(r"\s*\d+\s+(\d\.\d{2})\s*km\s+(\d{1,2}:\d{2})[\.:]?\d{0,2}?\s+(\d{1,2}'\d{2})", line)
        if match:
            dist, split_time, pace = match.groups()
            splits.append({
                "distance": f"{dist} km",
                "time": split_time,
                "pace": f"{pace}/km"
            })

    # Heart rate
    hr_avg_match = re.search(r"Average\s+(\d{2,3})", text)
    hr_max_match = re.search(r"Max\s+(\d{2,3})", text)

    # Cadence
    cadence_avg_match = re.search(r"Average\s+(\d{2,3})", text)
    cadence_max_match = re.search(r"Max\s+(\d{2,3})", text)

    # Stride Length
    stride_length_avg_match = re.search(r"Stride Length.*?Average\s+(\d{2,3})", text, re.DOTALL)

    return {
        "distance": distance_match.group(1) + " km" if distance_match else "Unknown",
        "time": time,
        "pace": avg_pace_match.group(1) + "/km" if avg_pace_match else "Unknown",
        "best_pace": best_pace_match.group(1) + "/km" if best_pace_match else "Unknown",
        "splits": splits,
        "avg_hr": hr_avg_match.group(1) if hr_avg_match else None,
        "max_hr": hr_max_match.group(1) if hr_max_match else None,
        "cadence_avg": cadence_avg_match.group(1) if cadence_avg_match else None,
        "cadence_max": cadence_max_match.group(1) if cadence_max_match else None,
        "stride_length_avg": stride_length_avg_match.group(1) if stride_length_avg_match else None
    }
