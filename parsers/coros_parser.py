import pytesseract
import re

def coros_parser(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    lines = text.splitlines()

    # === HR ZONES INIT EARLY ===
    hr_zones = {}

    # === DISTANCE ===
    distance = "Unknown"
    for line in lines:
        clean_line = line.replace("e", ".").replace("O", "0").replace("l", "1").replace("|", "1")
        clean_line = re.sub(r"\s+", "", clean_line)  # remove all spaces

        # Match formats like 8.00km, 10.5km, etc.
        match = re.search(r"(\d{1,3}[.,]\d{1,2})km", clean_line, re.IGNORECASE)
        if match:
            distance = match.group(1).replace(",", ".")
            distance = f"{float(distance):.2f} km"
            break

        # Try matching broken forms like '8 e 0 0 km'
        match2 = re.findall(r"(\d)\s*e\s*0\s*0\s*km", line, re.IGNORECASE)
        if match2:
            distance = f"{match2[0]}.00 km"
            break

    # === TIME ADDER HELPER ===
    def add_times(times):
        total_minutes = 0
        total_seconds = 0
        for t in times:
            if t:
                parts = t.split(":")
                if len(parts) == 2:
                    minutes, seconds = int(parts[0]), int(parts[1])
                    total_minutes += minutes
                    total_seconds += seconds
        total_minutes += total_seconds // 60
        total_seconds %= 60
        return f"{total_minutes}:{total_seconds:02d}"

    # === TOTAL TIME ===
    time = "Unknown"

    # Try finding time on the same line as "Activity Time"
    for line in lines:
        if "Activity Time" in line:
            match = re.search(r"(\d{1,2}[:.]\d{2})", line)
            if match:
                time = match.group(1).replace(".", ":")
                break

    # If not found, try next few lines after "Activity Time"
    if time == "Unknown":
        for i, line in enumerate(lines):
            if "Activity Time" in line:
                for offset in range(1, 4):
                    if i + offset < len(lines):
                        next_line = lines[i + offset]
                        match = re.search(r"(\d{1,2}[:.]\d{2})", next_line)
                        if match:
                            time = match.group(1).replace(".", ":")
                            break
                if time != "Unknown":
                    break

    # Still no time? Check "Total Time"
    if time == "Unknown":
        for line in lines:
            if "Total Time" in line:
                match = re.search(r"(\d{1,2}[:.]\d{2})", line)
                if match:
                    time = match.group(1).replace(".", ":")
                    break

    # Still unknown? Use HR zones sum
    if time == "Unknown" and hr_zones:
        total_time = add_times(hr_zones.values())
        if total_time != "0:00":
            time = total_time

    # Final fallback: any time found scanning backwards
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
        avg_match = re.search(r"Average\s+(\d{1,2}'\d{2})", line)
        if avg_match:
            pace = avg_match.group(1)

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
        if "Heart Rate" in line and "Max" in line and "Average" in line:
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if match:
                max_hr = int(match.group(1))
                avg_hr = int(match.group(2))
                break
        if "Heart Rate" in line and "Average" in line:
            match = re.search(r"Average\s+(\d+)", line)
            if match:
                avg_hr = int(match.group(1))
        if "Heart Rate" in line and "Max" in line:
            match = re.search(r"Max\s+(\d+)", line)
            if match:
                max_hr = int(match.group(1))

    # === CADENCE ===
    cadence_avg = None
    cadence_max = None
    for line in lines:
        if "Cadence" in line and "Max" in line and "Average" in line:
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if match:
                cadence_max = int(match.group(1))
                cadence_avg = int(match.group(2))
                break
        if "Cadence" in line and "Average" in line:
            match = re.search(r"Average\s+(\d+)", line)
            if match:
                cadence_avg = int(match.group(1))
        if "Cadence" in line and "Max" in line:
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

    # === HR ZONES ===
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

    return {
        "distance": distance,
        "time": time if time != "Unknown" else "0:00",
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
