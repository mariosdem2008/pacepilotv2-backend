import pytesseract
import re

def extract_workout_data(image):
    text = pytesseract.image_to_string(image, config='--psm 6')

    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Normalize
    text = text.replace("’", "'").replace("”", '"').replace("“", '"')
    text = text.replace("istance", "Distance").replace("km/h", "km")

    lines = text.splitlines()

    # Distance
    distance_match = re.findall(r"\b(\d+\.\d+|\d+)\s*km\b", text)
    distance = "Unknown"
    if distance_match:
        # Convert all matches to float and get the largest one
        numeric_distances = [float(d) for d in distance_match]
        max_distance = max(numeric_distances)
        distance = f"{max_distance:.2f} km"


    # Time (look for line above "Activity Time")
    time = "Unknown"
    for i, line in enumerate(lines):
        if "Activity Time" in line and i > 0:
            match = re.search(r"([0-2]?[0-9]:[0-5][0-9])", lines[i - 1])
            if match:
                time = match.group(1)
                break

    # Avg pace and best pace
    avg_pace_match = re.search(r"Average\s*([0-9]{1,2}'[0-9]{2})", text)
    best_pace_match = re.search(r"Best\s*km\s*([0-9]{1,2}'[0-9]{2})", text)

    # Splits
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
    avg_hr = None
    max_hr = None
    hr_match = re.search(r"Heart Rate.*?Max\s*(\d{2,3}).*?Average\s*(\d{2,3})", text)
    if hr_match:
        max_hr, avg_hr = hr_match.groups()

    # Cadence
    cadence_match = re.search(r"Cadence.*?Max\s*(\d{2,3}).*?Average\s*(\d{2,3})", text)
    cadence_max = cadence_match.group(1) if cadence_match else None
    cadence_avg = cadence_match.group(2) if cadence_match else None

    # Stride length
    stride_match = re.search(r"Stride Length.*?Average\s*(\d{2,3})", text, re.DOTALL)
    stride_length_avg = stride_match.group(1) if stride_match else None

    return {
        "distance": distance,
        "time": time,
        "pace": avg_pace_match.group(1) + "/km" if avg_pace_match else "Unknown",
        "best_pace": best_pace_match.group(1) + "/km" if best_pace_match else "Unknown",
        "splits": splits,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "cadence_avg": cadence_avg,
        "cadence_max": cadence_max,
        "stride_length_avg": stride_length_avg
    }

