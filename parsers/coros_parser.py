import pytesseract
import re

def coros_parser(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    lines = text.splitlines()

    # === HR ZONES PARSED EARLY ===
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

    for line in lines:
        # Match simple numeric splits (original layout)
        match = re.match(r"^\s*(\d+)\s+(\d+\.\d+)\s*km\s+([\d:.]+)\s+(\d{1,2}'\d{2})", line)
        if match:
            split_num = int(match.group(1))
            km = float(match.group(2))
            time_str = match.group(3)
            pace_str = match.group(4).replace("’", "'").replace("`", "'")

            if km < 0.05:
                continue

            total_split_distance += km
            splits.append({
                "split": split_num,
                "label": "Split",
                "km": f"{km:.2f} km",
                "time": time_str,
                "pace": pace_str
            })
            continue

        # Match "Run"/"Rest" format: optional index, label, km, time, pace
        match = re.match(r"^\s*(\d+)?\s*(Run|Rest)\s+(\d+\.\d+)\s*km\s+([\d:.]+)\s+(\d{1,2})[°'](\d{2})", line)
        if match:
            label = match.group(2)
            km = float(match.group(3))
            time_str = match.group(4)
            pace_str = f"{match.group(5)}'{match.group(6)}"

            if km < 0.05:
                continue

            total_split_distance += km
            splits.append({
                "split": split_index,
                "label": label,
                "km": f"{km:.2f} km",
                "time": time_str,
                "pace": pace_str
            })
            split_index += 1

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
        match2 = re.findall(r"(\d)\s*e\s*0\s*0\s*km", line, re.IGNORECASE)
        if match2:
            ocr_distance = float(match2[0])
            break

    if total_split_distance > 0:
        if not ocr_distance or abs(ocr_distance - total_split_distance) > 0.3:
            distance = f"{total_split_distance:.2f} km"
        else:
            distance = f"{ocr_distance:.2f} km"
    elif ocr_distance:
        distance = f"{ocr_distance:.2f} km"

    # === TIME ===
    time = "Unknown"
    total_time = None
    activity_time = None

    for line in lines:
        if "Total Time" in line or "Activity Time" in line:
            times = re.findall(r"(\d{1,2})[:.](\d{2})", line)
            if "Total Time" in line and len(times) >= 1:
                total_time = f"{times[0][0]}:{times[0][1]}"
            if "Activity Time" in line and len(times) >= 2:
                activity_time = f"{times[1][0]}:{times[1][1]}"
        elif re.search(r"Total Time\s*", line) or re.search(r"Activity Time\s*", line):
            match = re.findall(r"(\d{1,2})[:.](\d{2})", line)
            if match:
                if "Activity Time" in line and len(match) > 0:
                    activity_time = f"{match[0][0]}:{match[0][1]}"
                elif "Total Time" in line and len(match) > 0:
                    total_time = f"{match[0][0]}:{match[0][1]}"

    if activity_time:
        time = activity_time
    elif total_time:
        time = total_time
    elif hr_zones:
        nonzero_times = [t for t in hr_zones.values() if t != "0:00"]
        if nonzero_times:
            total_time_calc = 0
            for t in nonzero_times:
                parts = t.split(":")
                if len(parts) == 2:
                    total_time_calc += int(parts[0]) * 60 + int(parts[1])
            minutes = total_time_calc // 60
            seconds = total_time_calc % 60
            time = f"{minutes}:{seconds:02d}"
    else:
        for line in reversed(lines):
            match = re.findall(r"(\d{1,2})[:.](\d{2})", line)
            if match:
                time = f"{match[0][0]}:{match[0][1]}"
                break

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

    if pace == "Unknown" and time != "Unknown" and total_split_distance > 0:
        time_parts = time.split(":")
        if len(time_parts) == 2:
            total_seconds = int(time_parts[0]) * 60 + int(time_parts[1])
            pace_sec = int(total_seconds / total_split_distance)
            pace = f"{pace_sec // 60}'{pace_sec % 60:02d}"

    # === HEART RATE ===
    avg_hr = None
    max_hr = None
    for line in lines:
        if "Heart Rate" in line:
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if match:
                max_hr = int(match.group(1))
                avg_hr = int(match.group(2))
            match = re.search(r"Average\s+(\d+)", line)
            if match:
                avg_hr = int(match.group(1))
            match = re.search(r"Max\s+(\d+)", line)
            if match:
                max_hr = int(match.group(1))

    # === CADENCE ===
    cadence_avg = None
    cadence_max = None
    for line in lines:
        if "Cadence" in line:
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if match:
                cadence_max = int(match.group(1))
                cadence_avg = int(match.group(2))
            match = re.search(r"Average\s+(\d+)", line)
            if match:
                cadence_avg = int(match.group(1))
            match = re.search(r"Max\s+(\d+)", line)
            if match:
                cadence_max = int(match.group(1))

    # === STRIDE LENGTH ===
    stride_length_avg = None
    for line in lines:
        if "Stride Length" in line and "Average" in line:
            match = re.search(r"Average\s+(\d+)", line)
            if match:
                stride_length_avg = int(match.group(1))
                break

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
