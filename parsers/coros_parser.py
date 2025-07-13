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

    # === HR ZONES ===
    hr_zones = {}
    zone_patterns = {
        "Recovery": r"Recovery.*?(\d{1,2}:\d{2})",
        "Aerobic Endurance": r"Aerobic Endurance.*?(\d{1,2}:\d{2})",
        "Aerobic Power": r"Aerobic Power.*?(\d{1,2}:\d{2})",
        "Threshold": r"Threshold.*?(\d{1,2}:\d{2})",
        "Anaerobic Endurance": r"Anaerobic Endurance.*?(\d{1,2}:\d{2})",
        "Anaerobic Power": r"Anaerobic Power.*?(\d{1,2}:\d{2})"
    }
    for line in lines:
        for zone, pattern in zone_patterns.items():
            if zone in line:
                match = re.search(pattern, line)
                if match:
                    hr_zones[zone] = match.group(1)

    # === SPLITS ===
    splits = []
    total_split_distance = 0.0
    split_index = 1

    parsed_lines = []

    # Step 1: Parse all lines that resemble Run or Rest entries (flexible parsing)
    for line in lines:
        line = line.strip()
        original_line = line  # Keep for logging
        try:
            match = re.match(
                r"^\s*(\d+)?\s*(Run|Rest)\s+([\d.,]+)\s*km\s+([\d:.]+)?\s*(\d{1,2}|--)?'(\d{2}|--)?(?:\"|”)?(?:\s*/km)?",
                line
            )
            if not match:
                match = re.match(
                    r"^\s*(Run|Rest)\s+([\d.,]+)\s*km\s+([\d:.]+)?\s*(\d{1,2}|--)?'(\d{2}|--)?(?:\"|”)?(?:\s*/km)?",
                    line
                )
                if match:
                    label = match.group(1)
                    km = float(match.group(2).replace(",", ".")) if match.group(2) else 0.0
                    time_str = match.group(3) or "0:00"
                    pace_min = match.group(4) or "--"
                    pace_sec = match.group(5) or "--"
                else:
                    print(f"⏭️ Skipped unrecognized line: {original_line}", flush=True)
                    continue
            else:
                label = match.group(2)
                km = float(match.group(3).replace(",", ".")) if match.group(3) else 0.0
                time_str = match.group(4) or "0:00"
                pace_min = match.group(5) or "--"
                pace_sec = match.group(6) or "--"

            if pace_min == "--" or pace_sec == "--":
                pace_str = "-- /km"
            else:
                pace_str = f"{pace_min}'{pace_sec}"

            parsed_lines.append({
                "label": label,
                "km": km,
                "time": time_str,
                "pace": pace_str
            })

        except Exception as e:
            print(f"⚠️ Error parsing line: {original_line} -> {e}", flush=True)

    # Step 2: Assign split numbers and filter duplicates
    current_split_entries = set()
    for i, entry in enumerate(parsed_lines):
        label = entry["label"]
        km = entry["km"]
        time_str = entry["time"]
        pace_str = entry["pace"]

        entry_key = (label, f"{km:.2f} km", time_str, pace_str)

        if entry_key not in current_split_entries:
            splits.append({
                "split": split_index,
                "label": label,
                "km": f"{km:.2f} km",
                "time": time_str,
                "pace": pace_str
            })
            current_split_entries.add(entry_key)

        total_split_distance += km

        if i + 1 < len(parsed_lines) and parsed_lines[i + 1]["label"] == "Run":
            split_index += 1
            current_split_entries.clear()

    # === DISTANCE ===
    distance = "Unknown"
    ocr_distance = None
    for line in lines:
        clean_line = line.replace("e", ".").replace("O", "0").replace("l", "1").replace("|", "1")
        clean_line = re.sub(r"\s+", "", clean_line)
        match = re.search(r"(\d{1,3}[.,]\d{1,2})km", clean_line, re.IGNORECASE)
        if match:
            ocr_distance = float(match.group(1).replace(",", "."))
            break

    if total_split_distance > 0:
        if not ocr_distance or abs(ocr_distance - total_split_distance) > 0.3:
            distance = f"{total_split_distance:.2f} km"
        else:
            distance = f"{ocr_distance:.2f} km"
    elif ocr_distance:
        distance = f"{ocr_distance:.2f} km"

    # === TIME ===
    def parse_time_to_sec(t):
        try:
            parts = re.split(r"[:.]", t)
            return int(parts[0]) * 60 + float(parts[1])
        except:
            return 0

    total_seconds = sum(parse_time_to_sec(s["time"]) for s in splits)
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    time = f"{minutes}:{seconds:02d}"

    # === PACE ===
    pace = "Unknown"
    best_pace = "Unknown"

    for line in lines:
        avg_match = re.search(r"Average\s+(\d{1,2}'\d{2})", line)
        if avg_match:
            pace = avg_match.group(1)
        best_match = re.search(r"Best km\s+(\d{1,2})[^\d]?(\d{2})", line)
        if best_match:
            best_pace = f"{best_match.group(1)}'{best_match.group(2)}"

    if pace == "Unknown" and total_split_distance > 0:
        pace_sec = int(total_seconds / total_split_distance)
        pace = f"{pace_sec // 60}'{pace_sec % 60:02d}"

    def pace_to_seconds(p):
        try:
            parts = p.replace("’", "'").replace("`", "'").split("'")
            return int(parts[0]) * 60 + int(parts[1])
        except:
            return None

    best_pace_seconds = None
    for s in splits:
        sec = pace_to_seconds(s["pace"])
        if sec is not None:
            if best_pace_seconds is None or sec < best_pace_seconds:
                best_pace_seconds = sec

    if best_pace_seconds:
        best_pace = f"{best_pace_seconds // 60}'{best_pace_seconds % 60:02d}"

    # === HR / Cadence / Stride ===
    avg_hr = max_hr = cadence_avg = cadence_max = stride_length_avg = None

    for line in lines:
        if "Heart Rate" in line:
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if match:
                max_hr = int(match.group(1))
                avg_hr = int(match.group(2))
        if "Cadence" in line:
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if match:
                cadence_max = int(match.group(1))
                cadence_avg = int(match.group(2))
        if "Stride Length" in line and "Average" in line:
            match = re.search(r"Average\s+(\d+)", line)
            if match:
                stride_length_avg = int(match.group(1))

    result = {
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

    print("\n===== FINAL PARSED WORKOUT DATA =====", flush=True)
    print(json.dumps(result, indent=2), flush=True)
    print("======================================\n", flush=True)

    return result
