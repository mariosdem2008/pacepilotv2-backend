# parsers/coros_parser.py
import pytesseract
import re

def coros_parser(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    ocr_text_digits_only = pytesseract.image_to_string(image, config='--psm 11 -c tessedit_char_whitelist=0123456789./km')
    
    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Normalize
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

    # More liberal check for 'X.XX km' format
    for line in lines:
        if "km" in line and not any(x in line.lower() for x in ["pace", "'", "/km", "bpm", "%"]):
            match = re.search(r"(\d{1,2})\s*[eE., ]\s*(\d{2})\s*km", line)
            if match:
                try:
                    val = float(match.group(1) + "." + match.group(2))
                    if 0.5 < val < 100:
                        distance_candidates.append((val, "fallback"))
                except: pass

    if distance_candidates:
        sorted_candidates = sorted(distance_candidates, key=lambda x: ("fallback", "label").index(x[1]))
        distance = f"{sorted_candidates[0][0]:.2f} km"

    # === TIME ===
    time = "Unknown"
    # Check for nearby cluster before or after 'Activity Time'
    for i, line in enumerate(lines):
        if "Activity Time" in line:
            # Check previous and same line for mm:ss or hh:mm:ss patterns
            for j in [i-1, i]:
                if j < 0 or j >= len(lines): continue
                match = re.search(r"([0-9]{1,2}[:.][0-9]{2}(?:[:.][0-9]{2})?)", lines[j])
                if match:
                    time = match.group(1).replace(".", ":")
                    break

    # === PACE ===
    pace = "Unknown"
    best_pace = "Unknown"

    avg_pace_match = re.search(r"Average\s+([0-9]{1,2}'[0-9]{2})", text)
    best_pace_match = re.search(r"Best\s*km\s*@?\s*([0-9]{1,2}'[0-9]{2})", text)

    if avg_pace_match:
        pace = avg_pace_match.group(1) + "/km"
    if best_pace_match:
        best_pace = best_pace_match.group(1) + "/km"

    # === HEART RATE ===
    avg_hr = None
    hr_match = re.search(r"([0-9]{2,3})\s*bpm", text)
    if hr_match:
        hr_val = int(hr_match.group(1))
        if hr_val < 60: hr_val += 100
        avg_hr = str(hr_val)

    return {
        "distance": distance,
        "time": time,
        "pace": pace,
        "best_pace": best_pace,
        "splits": [],
        "avg_hr": avg_hr,
        "max_hr": None,
        "cadence_avg": None,
        "cadence_max": None,
        "stride_length_avg": None
    }
