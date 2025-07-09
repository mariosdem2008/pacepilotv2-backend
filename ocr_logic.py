import pytesseract
import re

def extract_workout_data(image):
    text = pytesseract.image_to_string(image, config='--psm 6')

    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Normalize for consistency
    text = (
        text.replace("’", "'")
            .replace("”", '"')
            .replace("“", '"')
            .replace("istance", "Distance")
            .replace("km/h", "km")
    )
    lines = text.splitlines()

    # -------- Distance --------
    distance_match = re.search(r"(\d+(\.\d+)?)\s*Distance", text)
    distance = f"{distance_match.group(1)} km" if distance_match else "Unknown"

    # -------- Time (line above "Activity Time") --------
    time = "Unknown"
    for i, line in enumerate(lines):
        if "Activity Time" in line and i > 0:
            match = re.search(r"([0-2]?[0-9]:[0-5][0-9])", lines[i - 1])
            if match:
                time = match.group(1)
                break

    # -------- Avg Pace & Best Pace --------
    avg_pace_match = re.search(r"Average\s*([0-9]{1,2}'[0-9]{2})", text)
    best_pace_match = re.search(r"Best\s*km\s*([0-9]{1,2}'[0-9]{2})", text)

    pace = avg_pace_match.group(1) + "/km" if avg_pace_match else "Unknown"
    best_pace = best_pace_match.group(1) + "/km" if best_pace_match else "Unknown"

    # -------- Splits --------
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

    # -------- Heart Rate --------
    avg_hr = max_hr = None
    hr_match = re.search(r"Heart Rate.*?Max\s*(\d{2,3}).*?Average\s*(\d{2,3})", text, re.IGNORECASE)
    if hr_match:
        max_hr, avg_hr = hr_match.groups()

    # -------- Cadence --------
    cadence_avg = cadence_max = None
    cadence_match = re.search(r"Cadence.*?Max\s*(\d{2,3}).*?Average\s*(\d{2,3})", text, re.IGNORECASE)
    if cadence_match:
        cadence_max, cadence_avg = cadence_match.groups()

    # -------- Stride Length --------
    stride_length_avg = None
    stride_match = re.search(r"Stride Length.*?Average\s*(\d{2,3})", text, re.IGNORECASE | re.DOTALL)
    if stride_match:
        stride_length_avg = stride_match.group(1)

    return {
        "distance": distance,
        "time": time,
        "pace": pace,
        "best_pace": best_pace,
        "splits": splits,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "cadence_avg": cadence_avg,
        "cadence_max": cadence_max,
        "stride_length_avg": stride_length_avg
    }
