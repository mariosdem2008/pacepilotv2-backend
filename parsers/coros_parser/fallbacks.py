#fallbacks.py
import re
from .utils import parse_time_to_sec, pace_to_seconds
from .utils.ocr_cleaner import recover_distance_from_lines


def apply_fallbacks(summary, splits, total_split_distance, lines, text):
    time = summary["time"]
    distance = summary["distance"]
    pace = summary["pace"]
    best_pace = summary["best_pace"]

    total_seconds = sum(parse_time_to_sec(s["time"]) for s in splits)

    if time == "0:00" and total_seconds > 0:
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        time = f"{minutes}:{seconds:02d}"

    if pace == "Unknown" and total_split_distance > 0:
        pace_sec = int(total_seconds / total_split_distance)
        pace = f"{pace_sec // 60}'{pace_sec % 60:02d}"

    best_pace_seconds = None
    for s in splits:
        sec = pace_to_seconds(s["pace"])
        if sec is not None and (best_pace_seconds is None or sec < best_pace_seconds):
            best_pace_seconds = sec

    if best_pace == "Unknown" and best_pace_seconds:
        best_pace = f"{best_pace_seconds // 60}'{best_pace_seconds % 60:02d}"

    # fallback distance detection with your cleaner helper
    ocr_distance_str = recover_distance_from_lines(lines)

    def parse_km(d):
        try:
            return float(str(d).replace("km", "").strip())
        except:
            return None

    parsed_summary_distance = parse_km(distance)
    parsed_ocr_distance = parse_km(ocr_distance_str)

    # Use OCR distance if valid
    if parsed_ocr_distance:
        if parsed_summary_distance is None or abs(parsed_summary_distance - parsed_ocr_distance) > 0.3:
            distance = f"{parsed_ocr_distance:.2f} km"

    # Fallback to splits if no good OCR distance
    elif parsed_summary_distance is None and total_split_distance > 0:
        distance = f"{total_split_distance:.2f} km"



    return {
        "distance": distance,
        "time": time,
        "pace": pace,
        "best_pace": best_pace,
        "avg_hr": summary["avg_hr"],
        "max_hr": summary["max_hr"],
        "cadence_avg": None,
        "cadence_max": None,
        "stride_length_avg": None
    }
