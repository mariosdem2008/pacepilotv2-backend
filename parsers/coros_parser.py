# parsers/coros_parser.py
import pytesseract
import re

def coros_parser(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Normalize text
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

    # === TIME (Total) ===
    time = "Unknown"
    for line in lines:
        if re.search(r"\bTotal Time\b", line, re.IGNORECASE):
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

    # === SPLITS ===
    splits = []
    for line in lines:
        match = re.match(r"^\s*(\d+)\s+(\d+\.\d+)\s*km\s+[\d:.]+\s+(\d{1,2}'\d{2})", line)
        if match:
            km = float(match.group(2))
            pace = match.group(3).replace("’", "'").replace("`", "'")
            splits.append({"km": km, "time": pace})

    # === HEART RATE ===
    avg_hr = max_hr = None
    for line in lines:
        if "Heart Rate" in line and re.search(r"Max\s+(\d+).*Average\s+(\d+)", line):
            match = re.search(r"Max\s+(\d+).*Average\s+(\d+)", line)
            if match:
                max_hr = int(match.group(1))
                avg_hr = int(match.group(2))
                break

    # === CADENCE ===
    cadence_avg = cadence_max = None
    for line in lines:
        if "Cadence" in line and re.search(r"Max\s+(\d+).*Average\s+(\d+)", line):
            match = re.search(r"Max\s+(\d+).*Average\s+(\d+)", line)
            if match:
                cadence_max = int(match.group(1))
                cadence_avg = int(match.group(2))
                break

    # === STRIDE LENGTH ===
    stride_length_avg = None
    for line in lines:
        if "Stride Length" in line:
            match = re.search(r"Average\s+(\d+)", line)
            if match:
                stride_length_avg = int(match.group(1))
                break

    # === HR ZONES ===
    hr_zones = {}
    zone_names = [
        "Recovery", "Aerobic Endurance", "Aerobic Power",
        "Threshold", "Anaerobic Endurance", "Anaerobic Power"
    ]
    for line in lines:
        for zone in zone_names:
            if zone in line:
                match = re.search(r"(\d{1,2}:\d{2})", line)
                if match:
                    hr_zones[zone] = match.group(1)

    return {
        "distance": distance,
        "time": time,
        "pace": "Unknown",
        "best_pace": "Unknown",
        "splits": splits,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "cadence_avg": cadence_avg,
        "cadence_max": cadence_max,
        "stride_length_avg": stride_length_avg,
        "hr_zones": hr_zones if hr_zones else None
    }
