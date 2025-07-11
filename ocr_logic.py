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

    # -------- Distance (robust fallback) --------
    distance = "Unknown"
    distance_candidates = []

    # 1. Primary: Look for line with "Distance" label
    for line in lines:
        if "Distance" in line:
            match = re.search(r"(\d+(?:\.\d{1,2})?)", line)
            if match:
                value = float(match.group(1))
                print(f"Matched Distance with 'Distance' label: {value}")
                distance_candidates.append((value, "label"))

    # 2. Check all lines for proper floats and known bad patterns
    for i, line in enumerate(lines):
        if any(term in line.lower() for term in ["pace", "'", "avg", "best", "/km", "km/h", "%", "bpm", "kcal", "load"]):
            continue

        match = re.search(r"(\d+(?:\.\d{1,2})?)\s*km\b", line)
        if match:
            value = float(match.group(1))
            if 0.5 < value < 50:
                print(f"Found full decimal distance candidate: {value} from line: '{line}'")
                distance_candidates.append((value, "full"))

    # 3. Special case: fuzzy match for broken "4 e 9 / km" → 4.97
    fuzzy_pattern = re.compile(r"(\d)\s*[eE]\s*(\d)\s*/\s*(\d)\s*km", re.IGNORECASE)
    for line in lines:
        match = fuzzy_pattern.search(line)
        if match:
            whole, dec1, dec2 = match.groups()
            try:
                value = float(f"{whole}.{dec1}{dec2}")
                if 0.5 < value < 50:
                    print(f"Found fuzzy OCR decimal distance: {value} from line: '{line}'")
                    distance_candidates.append((value, "fuzzy"))
            except:
                continue

    # Choose the best candidate: fuzzy > full > label
    if distance_candidates:
        sorted_candidates = sorted(distance_candidates, key=lambda x: ("fuzzy", "full", "label").index(x[1]))
        distance = f"{sorted_candidates[0][0]:.2f} km"

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
