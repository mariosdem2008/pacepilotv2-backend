import pytesseract
import re
import json

def coros_parser(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    text = text.replace("’", "'").replace("“", '"').replace("”", '"').replace("°", "'").replace("`", "'")
    lines = text.splitlines()

    # === Basic stats ===
    distance = None
    total_time = None
    avg_pace = None
    best_pace = None
    avg_hr = None
    max_hr = None
    cadence_avg = None
    cadence_max = None
    stride_length_avg = None

    for line in lines:
        # Distance
        if not distance and re.search(r"\b[kK][mM]\b", line) and "distance" in line.lower():
            match = re.search(r"([\d\.]+)\s*[kK][mM]", line)
            if match:
                distance = f"{float(match.group(1)):.2f} km"

        # Total Time
        if not total_time:
            match = re.search(r"\b(\d{1,2}:\d{2})\b.*?(Activity Time|Time)", line)
            if match:
                total_time = match.group(1)

        # Avg Pace
        if not avg_pace:
            match = re.search(r"Average Pace.*?(\d+'\d{2})", line)
            if match:
                avg_pace = match.group(1)

        # Best pace
        if not best_pace:
            match = re.search(r"Best Lap.*?(\d+'\d{2})", line)
            if match:
                best_pace = match.group(1)

        # Heart Rate
        if not avg_hr or not max_hr:
            match = re.search(r"Heart Rate.*?Max (\d+).*?Average (\d+)", line)
            if match:
                max_hr = int(match.group(1))
                avg_hr = int(match.group(2))

        # Cadence
        if not cadence_avg or not cadence_max:
            match = re.search(r"Cadence.*?Max (\d+).*?Average (\d+)", line)
            if match:
                cadence_max = int(match.group(1))
                cadence_avg = int(match.group(2))

        # Stride Length
        if not stride_length_avg:
            match = re.search(r"Stride Length.*?Average (\d+)", line)
            if match:
                stride_length_avg = int(match.group(1))

    # === Splits ===
    splits = []
    split_pattern = re.compile(r"(Run|Rest)\s+([\d\.]+)\s*km\s+([\d:.]+)\s+([\d']{1,2}\d{2}|--)\s*/km")
    split_count = 1

    for match in split_pattern.finditer(text):
        label, km, time_str, pace = match.groups()
        splits.append({
            "split": split_count if label == "Run" else split_count,
            "label": label,
            "km": f"{float(km):.2f} km",
            "time": time_str,
            "pace": pace
        })
        if label == "Run":
            split_count += 1

    # === Heart Rate Zones ===
    hr_zones = {}
    zone_patterns = {
        "Recovery": r"Recovery.*?(\d+:\d+)",
        "Aerobic Endurance": r"Aerobic Endurance.*?(\d+:\d+)",
        "Aerobic Power": r"Aerobic Power.*?(\d+:\d+)",
        "Threshold": r"Threshold.*?(\d+:\d+)",
        "Anaerobic Endurance": r"Anaerobic Endurance.*?(\d+:\d+)",
        "Anaerobic Power": r"Anaerobic Power.*?(\d+:\d+)"
    }

    for line in lines:
        for zone, pattern in zone_patterns.items():
            if zone not in hr_zones:
                match = re.search(pattern, line)
                if match:
                    hr_zones[zone] = match.group(1)

    # === Output JSON (safe values only if explicitly extracted) ===
    output = {
        "distance": distance if distance else None,
        "time": total_time if total_time else None,
        "pace": avg_pace if avg_pace else None,
        "best_pace": best_pace,
        "splits": splits,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "cadence_avg": cadence_avg,
        "cadence_max": cadence_max,
        "stride_length_avg": stride_length_avg,
        "hr_zones": hr_zones
    }

    print("===== FINAL PARSED WORKOUT DATA =====", flush=True)
    print(json.dumps(output, indent=2), flush=True)

    return output
