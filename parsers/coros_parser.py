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

    for line in lines:
        try:
            line = line.strip()

            match = re.match(r"^\s*(\d+)\s+(\d+\.\d+)\s*km\s+([\d:.]+)\s+(\d{1,2}'\d{2})", line)
            if match:
                split_num = int(match.group(1))
                km = float(match.group(2))
                time_str = match.group(3)
                pace_str = match.group(4)

                if km < 0.05:
                    continue

                total_split_distance += km
                splits.append({
                    "split": split_index,
                    "label": "Split",
                    "km": f"{km:.2f} km",
                    "time": time_str,
                    "pace": pace_str
                })
                split_index += 1
                continue

            match = re.match(r"^\s*(\d+)?\s*(Run|Rest)\s+(\d+\.\d+)\s*km\s+([\d:.]+)\s+(\d{1,2})'(\d{2})", line)
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
                continue

            match_fallback = re.match(r"^\s*(Run|Rest)\s+(\d+\.\d+)\s*km\s+([\d:.]+)\s+(\d{1,2})'(\d{2})", line)
            if match_fallback:
                label = match_fallback.group(1)
                km = float(match_fallback.group(2))
                time_str = match_fallback.group(3)
                pace_str = f"{match_fallback.group(4)}'{match_fallback.group(5)}"

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

        except Exception as e:
            print(f"⚠️ Split parsing error: {e} on line: {line}", flush=True)

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
    def parse_time_to_sec(t):
        try:
            if ':' in t:
                parts = t.split(':')
            elif '.' in t:
                parts = t.split('.')
            else:
                return 0
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

    # Pretty-print result to terminal/log
    print("\n===== FINAL PARSED WORKOUT DATA =====", flush=True)
    print(json.dumps(result, indent=2), flush=True)
    print("======================================\n", flush=True)

    return result

