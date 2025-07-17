#fallbacks.py
import re
from .utils import parse_time_to_sec, pace_to_seconds
from .utils.ocr_cleaner import recover_distance_from_lines





def apply_fallbacks(summary, splits, total_split_distance, lines, text):
    time = summary["time"]
    distance = summary["distance"]
    pace = summary["pace"]
    best_pace = summary["best_pace"]

    total_seconds = sum(parse_time_to_sec(s.get("time", "0:00")) for s in splits)


    if time == "0:00" and total_seconds > 0:
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        time = f"{minutes}:{seconds:02d}"

    if pace == "Unknown" and total_split_distance > 0:
        pace_sec = int(total_seconds / total_split_distance)
        pace = f"{pace_sec // 60}'{pace_sec % 60:02d}"

    best_pace_seconds = None
    for s in splits:
        sec = pace_to_seconds(s.get("pace", "Unknown"))
        if sec is not None and (best_pace_seconds is None or sec < best_pace_seconds):
            best_pace_seconds = sec

    if best_pace == "Unknown" and best_pace_seconds:
        best_pace = f"{best_pace_seconds // 60}'{best_pace_seconds % 60:02d}"

    # fallback distance detection with your cleaner helper
    ocr_distance_str = recover_distance_from_lines(lines)
    print(f"[DEBUG] Fallback OCR distance: {ocr_distance_str}")


    def parse_km(d):
        try:
            return float(str(d).replace("km", "").strip())
        except:
            return None


    # Try to parse distances
    parsed_summary_distance = parse_km(distance)
    parsed_ocr_distance = parse_km(ocr_distance_str)

    # Use split distance if available and consistent
    if total_split_distance > 0:
        if parsed_summary_distance is None or parsed_summary_distance < total_split_distance - 0.2:
            distance = f"{total_split_distance:.2f} km"
        else:
            distance = f"{parsed_summary_distance:.2f} km"

    # Otherwise, prefer OCR if it's more reasonable
    elif parsed_ocr_distance is not None:
        # Trust OCR if summary distance looks incorrect (e.g. too small)
        if parsed_summary_distance is None or parsed_summary_distance < 0.7 * parsed_ocr_distance:
            distance = f"{parsed_ocr_distance:.2f} km"
        else:
            distance = f"{parsed_summary_distance:.2f} km"


    # Fallback to whatever is available
    elif parsed_summary_distance is not None:
        distance = f"{parsed_summary_distance:.2f} km"

        # Final fallback: try to recover time from lines with strong contextual clues
    if time == "0:00":
        candidate_times = []
        time_pattern = re.compile(r"\b(\d{1,3}):(\d{2})\b")

        for i, line in enumerate(lines):
            matches = time_pattern.findall(line)
            for (m, s) in matches:
                minutes = int(m)
                seconds = int(s)
                # Accept times between 5 minutes and 3 hours (180 min)
                if 5 <= minutes <= 180 and 0 <= seconds < 60:
                    prev_line = lines[i-1].lower() if i-1 >= 0 else ""
                    next_line = lines[i+1].lower() if i+1 < len(lines) else ""
                    line_lower = line.lower()
                    context = f"{prev_line} {line_lower} {next_line}"
                    # Keywords indicating activity time
                    if any(k in context for k in ["activity time", "activity", "duration", "effort", "time"]):
                        candidate_times.append((minutes*60 + seconds, f"{minutes}:{seconds:02d}"))

        if candidate_times:
            candidate_times.sort(reverse=True)  # pick longest time
            time = candidate_times[0][1]
            print(f"[DEBUG] Fallback recovered time: {time}")






    return {
        "distance": distance,
        "time": time,
        "pace": pace,
        "best_pace": best_pace,
        "avg_hr": summary.get("avg_hr"),
        "max_hr": summary.get("max_hr"),
        "cadence_avg": None,
        "cadence_max": None,
        "stride_length_avg": None
    }
