# parsers/coros_parser.py
import pytesseract, re

def coros_parser(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    ocr_text_digits_only = pytesseract.image_to_string(image, config='--psm 11 -c tessedit_char_whitelist=0123456789./km')
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    lines = text.splitlines()

    # Distance
    distance = "Unknown"
    distance_match = re.search(r"\b(\d[\s\.\de]*)\s*km\b", text, re.IGNORECASE)
    if distance_match:
        raw = distance_match.group(1)
        cleaned = re.sub(r"[^\d.]", "", raw)
        try:
            dist_float = float(cleaned)
            if 0.5 < dist_float < 100:
                distance = f"{dist_float:.2f} km"
        except:
            pass

    # Time
    time = "Unknown"
    time_match = re.search(r"\b([0-2]?\d:[0-5]\d(?:[:\.]\d{1,2})?)\b", text)
    if time_match:
        raw_time = time_match.group(1)
        # Normalize 40:11.57 → 40:11
        time = raw_time.split(":")[0] + ":" + raw_time.split(":")[1]

    # Avg pace
    avg_pace_match = re.search(r"Average\s+([0-9]{1,2}'[0-9]{2})", text)
    pace = avg_pace_match.group(1) + "/km" if avg_pace_match else "Unknown"

    # Best pace
    best_pace_match = re.search(r"Best km\s*([0-9]{1,2}'[0-9]{2})", text)
    if not best_pace_match:
        # fallback: try raw match
        best_pace_match = re.search(r"\b([0-9]{1,2}'[0-9]{2})\s*/km\b", text)
    best_pace = best_pace_match.group(1) + "/km" if best_pace_match else "Unknown"

    # HR
    avg_hr = None
    max_hr = None
    hr_match = re.search(r"([0-9]{2,3})\s*bpm", text)
    if hr_match:
        avg_hr = hr_match.group(1)

    return {
        "distance": distance,
        "time": time,
        "pace": pace,
        "best_pace": best_pace,
        "splits": [],
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "cadence_avg": None,
        "cadence_max": None,
        "stride_length_avg": None
    }
