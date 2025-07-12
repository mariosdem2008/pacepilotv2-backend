import pytesseract
import re

def coros_parser(image):
    # OCR for all text
    text = pytesseract.image_to_string(image, config='--psm 6')
    ocr_text_digits_only = pytesseract.image_to_string(image, config='--psm 11 -c tessedit_char_whitelist=0123456789./km')
    print(f"OCR Text: {text}")
    lines = text.splitlines()
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')

    # Normalize spacing issues
    text = re.sub(r"\s+", " ", text)

    # ===== Distance =====
    distance = "Unknown"
    distance_match = re.search(r"\b(\d{1,2}\.?\d{0,2})\s*km\b", text, re.IGNORECASE)
    if distance_match:
        try:
            val = float(distance_match.group(1))
            if 0.5 < val < 100:
                distance = f"{val:.2f} km"
        except:
            pass

    # ===== Time =====
    time = "Unknown"
    for i, line in enumerate(lines):
        if "Activity Time" in line and i > 0:
            prev_line = lines[i - 1]
            match = re.search(r"([0-2]?\d[:.][0-5]\d)", prev_line)
            if match:
                time = match.group(1).replace(".", ":")
                break
    # fallback for OCR where time and label are on the same line
    if time == "Unknown":
        match = re.search(r"([0-2]?\d[:.][0-5]\d)[^\d]*(Activity Time)", text)
        if match:
            time = match.group(1).replace(".", ":")

    # ===== Pace =====
    pace = "Unknown"
    pace_match = re.search(r"Avg\.?\s*Pace\s*([0-9]{1,2}'[0-9]{2})", text)
    if pace_match:
        pace = pace_match.group(1) + "/km"

    # ===== Best Pace =====
    best_pace = "Unknown"
    best_pace_match = re.search(r"Best km\s*([0-9]{1,2}'[0-9]{2})", text)
    if not best_pace_match:
        best_pace_match = re.search(r"Best.*?([0-9]{1,2}'[0-9]{2})", text)
    if best_pace_match:
        best_pace = best_pace_match.group(1) + "/km"

    # ===== Heart Rate (Average only for now) =====
    avg_hr = None
    hr_match = re.search(r"(\d{2,3})\s*bpm", text)
    if hr_match:
        avg_hr = hr_match.group(1)

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

