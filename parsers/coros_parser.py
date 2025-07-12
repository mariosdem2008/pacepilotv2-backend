# parsers/coros_parser.py
import pytesseract
import re

def coros_parser(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    ocr_text_digits_only = pytesseract.image_to_string(image, config='--psm 11 -c tessedit_char_whitelist=0123456789./km')

    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # === Normalize ===
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    text = text.replace("istance", "Distance").replace("km/h", "km")
    lines = text.splitlines()

    # === DISTANCE ===
    distance = "Unknown"
    distance_candidates = []

    for line in lines:
        if "Distance" in line:
            match = re.search(r"(\d+[.,e ]\d{1,2})", line)
            if match:
                raw = match.group(1).replace("e", ".").replace(",", ".").replace(" ", "")
                try:
                    val = float(raw)
                    distance_candidates.append((val, "label"))
                except: pass

    # Add support for "8 e 0 0 km" or "8 e 0 km"
    for line in lines:
        if "km" in line and not any(x in line.lower() for x in ["pace", "'", "/km", "bpm", "%"]):
            # Match things like "8 e 0 0 km"
            mashed = re.findall(r"(\d)\s*[eE., ]\s*(\d)\s*(\d{1,2})\s*km", line)
            if mashed:
                try:
                    val = float(mashed[0][0] + "." + mashed[0][1] + mashed[0][2])
                    if 0.5 < val < 100:
                        distance_candidates.append((val, "mashed"))
                except: pass

    if distance_candidates:
        sorted_candidates = sorted(distance_candidates, key=lambda x: ("mashed", "fallback", "label").index(x[1]))
        distance = f"{sorted_candidates[0][0]:.2f} km"

    # === TIME ===
    time = "Unknown"
    for i, line in enumerate(lines):
        if "Activity Time" in line:
            for j in [i - 1, i]:
                if j < 0 or j >= len(lines): continue

                match = re.search(r"([0-9]{1,2}[:.][0-9]{2}(?:[:.][0-9]{2})?)", lines[j])
                if match:
                    time = match.group(1).replace(".", ":")
                    break

                # Handle mashed timestamp like "4021197"
                digits = re.findall(r"\d{6,8}", lines[j])
                if digits:
                    ts = digits[0]
                    try:
                        minutes = int(ts[:2])
                        seconds = int(ts[2:4])
                        if 0 <= minutes <= 99 and 0 <= seconds < 60:
                            time = f"{minutes}:{seconds:02d}"
                            break
                    except: pass

    # === PACE ===
    pace = "Unknown"
    best_pace = "Unknown"

    avg_pace_match = re.search(r"Average\s+([0-9]{1,2}'[0-9]{2})", text)
    if avg_pace_match:
        pace = avg_pace_match.group(1) + "/km"

    best_pace_match = re.search(r"Best km.*?(\d{1,2})[^\d]?(\d{2})", text)
    if best_pace_match:
        best_pace = f"{best_pace_match.group(1)}'{best_pace_match.group(2)}/km"

    # === HEART RATE ===
    avg_hr = None
    hr_match = re.search(r"([0-9]{2,3})\s*bpm", text)
    if hr_match:
        hr_val = int(hr_match.group(1))
        if hr_val < 60: hr_val += 100
        avg_hr = str(hr_val)


    # === MAX HEART RATE ===
    max_hr_match = re.search(r"Max\s+(\d{2,3})\s+Average\s+(\d{2,3})", text)
    if max_hr_match:
        max_hr = max_hr_match.group(1)
        if not avg_hr:
            avg_hr = max_hr_match.group(2)
    else:
        max_hr = None

    # === CADENCE ===
    cadence_avg = cadence_max = None
    cadence_match = re.search(r"Cadence\s*@\s*Max\s*(\d{2,3})\s+Average\s+(\d{2,3})", text)
    if cadence_match:
        cadence_max = cadence_match.group(1)
        cadence_avg = cadence_match.group(2)

    # === STRIDE LENGTH ===
    stride_length_avg = None
    stride_match = re.search(r"Stride Length.*?Average\s+(\d{2,3})", text)
    if stride_match:
        stride_length_avg = stride_match.group(1)

    return {
        "distance": distance,
        "time": time,
        "pace": pace,
        "best_pace": best_pace,
        "splits": [],
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "cadence_avg": cadence_avg,
        "cadence_max": cadence_max,
        "stride_length_avg": stride_length_avg
    }

