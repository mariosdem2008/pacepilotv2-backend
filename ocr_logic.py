import pytesseract
import re

def extract_workout_data(image):
    text = pytesseract.image_to_string(image, config='--psm 6')

    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Fix OCR noise
    text = text.replace("’", "'").replace("”", '"').replace("“", '"')
    text = text.replace("istance", "Distance").replace("km/h", "km")

    # -------- Distance logic --------
    km_matches = re.findall(r"(\d+\.\d+|\d+)\s*km", text)
    distance = "Unknown"
    if km_matches:
        distance_context = re.search(r"(\d+\.\d+|\d+)\s*km.*?Distance", text, re.IGNORECASE)
        if distance_context:
            distance = f"{float(distance_context.group(1)):.2f} km"
        else:
            reasonable_kms = [float(km) for km in km_matches if 0 < float(km) < 15]
            if reasonable_kms:
                distance = f"{max(reasonable_kms):.2f} km"

    # -------- Time (Activity Time) --------
    time = "Unknown"
    activity_time_section = re.search(r"([\d:]{4,5}).{0,10}Activity\s*Time", text)
    if activity_time_section:
        time = activity_time_section.group(1)
    else:
        time_candidates = re.finditer(r"\b([0-2]?[0-9]:[0-5][0-9])\b", text)
        for match in time_candidates:
            context = text[max(0, match.start() - 10):match.end() + 10]
            if "'" not in context:
                time = match.group(1)
                break

    # -------- Pace --------
    avg_pace_match = re.search(r"Average\s*([0-9]{1,2}'[0-9]{2})", text)
    best_pace_match = re.search(r"Best\s*km\s*([0-9]{1,2}'[0-9]{2})", text)

    # -------- Splits --------
    splits = []
    split_lines = re.findall(r"(\d\.\d{2}|\d{1,2}\.00)\s*km\s+(\d{1,2}:\d{2})[\.:]?\d*\s+([0-9]{1,2}'[0-9]{2})", text)
    for dist, t, p in split_lines:
        splits.append({
            "distance": f"{dist} km",
            "time": t,
            "pace": f"{p}/km"
        })

    # -------- Heart rate --------
    avg_hr = max_hr = None
    hr_match = re.search(r"Heart\s*Rate.*?Max\s*(\d+)\s*Average\s*(\d+)", text, re.IGNORECASE)
    if hr_match:
        max_hr = hr_match.group(1)
        avg_hr = hr_match.group(2)

    # -------- Cadence --------
    cadence_avg = cadence_max = None
    cadence_match = re.search(r"Cadence.*?Max\s*(\d+)\s*Average\s*(\d+)", text, re.IGNORECASE)
    if cadence_match:
        cadence_max = cadence_match.group(1)
        cadence_avg = cadence_match.group(2)

    # -------- Stride Length --------
    stride_length_avg = None
    stride_match = re.search(r"Stride\s*Length.*?Average\s*(\d+)", text, re.IGNORECASE)
    if stride_match:
        stride_length_avg = stride_match.group(1)

    return {
        "distance": distance,
        "time": time,
        "pace": avg_pace_match.group(1) + "/km" if avg_pace_match else "Unknown",
        "best_pace": best_pace_match.group(1) + "/km" if best_pace_match else "Unknown",
        "splits": splits,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "cadence_avg": cadence_avg,
        "cadence_max": cadence_max,
        "stride_length_avg": stride_length_avg
    }
