# parsers/coros_parser.py
import pytesseract
import re

def coros_parser(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Normalize and split lines
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    lines = text.splitlines()

    # === DISTANCE ===
    distance = "Unknown"
    distance_count = 0
    for line in lines:
        if re.search(r"\b1\.00\s*km\b", line):
            distance_count += 1
    if distance_count:
        distance = f"{distance_count:.2f} km"

    # Attempt to extract distance if summary format is used
    if distance == "Unknown":
        for line in lines:
            match = re.search(r"\b(\d{1,3}\.\d{1,2})\s*km\b", line, re.IGNORECASE)
            if match:
                distance = f"{float(match.group(1)):.2f} km"
                break

    # === TOTAL TIME ===
    time = "Unknown"
    for line in lines:
        if "Total Time" in line:
            match = re.search(r"(\d{1,2}[:.]\d{2})", line)
            if match:
                time = match.group(1).replace(".", ":")
                break

    if time == "Unknown":
        for line in reversed(lines):
            match = re.findall(r"(\d{1,2}[:.]\d{2})", line)
            if match:
                time = match[0].replace(".", ":")
                break

    # === PACE & BEST PACE ===
    pace = "Unknown"
    best_pace = "Unknown"
    for line in lines:
        # Avg pace line like "Average 5'01""
        avg_match = re.search(r"Average\s+(\d{1,2}'\d{2})", line)
        if avg_match:
            pace = avg_match.group(1)

        # Best pace line like "Best km 4 48"
        best_match = re.search(r"Best km\s+(\d{1,2})[^\d]?(\d{2})", line)
        if best_match:
            best_pace = f"{best_match.group(1)}'{best_match.group(2)}"

    # === SPLITS ===
    splits = []
    for line in lines:
        match = re.match(r"^\s*(\d+)\s+(\d+\.\d+)\s*km\s+[\d:.]+\s+(\d{1,2}'\d{2})", line)
        if match:
            km = float(match.group(2))
            pace = match.group(3).replace("’", "'").replace("`", "'")
            splits.append({"km": km, "time": pace})

    # === HEART RATE ===
    avg_hr = None
    max_hr = None
    for line in lines:
        if "Heart Rate" in line and "Average" in line and "Max" in line:
            hr_match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if hr_match:
                max_hr = int(hr_match.group(1))
                avg_hr = int(hr_match.group(2))
                break

    # === CADENCE ===
    cadence_avg = None
    cadence_max = None
    for line in lines:
        if "Cadence" in line and "Average" in line and "Max" in line:
            cad_match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if cad_match:
                cadence_max = int(cad_match.group(1))
                cadence_avg = int(cad_match.group(2))
                break

    # === STRIDE LENGTH ===
    stride_length_avg = None
    for line in lines:
        if "Stride Length" in line and "Average" in line:
            stride_match = re.search(r"Average\s+(\d+)", line)
            if stride_match:
                stride_length_avg = int(stride_match.group(1))
                break

    # === HR ZONES ===
    hr_zones = {}
    zone_labels = [
        "Recovery",
        "Aerobic Endurance",
        "Aerobic Power",
        "Threshold",
        "Anaerobic Endurance",
        "Anaerobic Power"
    ]
    for line in lines:
        for zone in zone_labels:
            if zone in line:
                zone_match = re.search(rf"{zone}.*?(\d+:\d{{2}})", line)
                if zone_match:
                    hr_zones[zone] = zone_match.group(1)

    # === Final Output ===
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
        "stride_length_avg": stride_length_avg,
        "hr_zones": hr_zones if hr_zones else None
    }
