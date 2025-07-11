# parsers/garmin_parser.py
import pytesseract, re

def garmin_parser(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    lines = text.splitlines()

    distance = time = pace = best_pace = "Unknown"
    for line in lines:
        if "Distance" in line or "Dist" in line:
            match = re.search(r"(\d+(?:\.\d{1,2})?)", line)
            if match:
                distance = f"{float(match.group(1)):.2f} km"
        if "Time" in line:
            match = re.search(r"([0-2]?[0-9]:[0-5][0-9])", line)
            if match:
                time = match.group(1)
        if "Pace" in line:
            match = re.search(r"(\d{1,2}'\d{2})", line)
            if match:
                pace = match.group(1) + "/km"

    return {
        "distance": distance,
        "time": time,
        "pace": pace,
        "best_pace": best_pace,
        "splits": [],
        "avg_hr": None,
        "max_hr": None,
        "cadence_avg": None,
        "cadence_max": None,
        "stride_length_avg": None
    }
