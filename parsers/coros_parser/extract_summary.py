import re
from .utils.ocr_cleaner import recover_distance_from_lines  # ✅ MOVE TO THE TOP



def extract_summary(lines):
    time = "0:00"
    distance = "Unknown"
    pace = "Unknown"
    best_pace = "Unknown"
    avg_hr = None
    max_hr = None

    for line in lines:
        line_clean = line.replace("’", "'").replace("`", "'")

        if time == "0:00":
            match = re.search(r"\bTime\b.*?(\d{1,2}:\d{2})", line_clean, re.IGNORECASE)
            if match:
                time = match.group(1)

        if distance == "Unknown":
            # Skip obvious speed indicators like km/h or pace
            if "km/h" not in line_clean.lower():
                # First try with keywords
                match = re.search(r"\b(?:distance|istance|stance)\b[^0-9]*?(\d{1,3})[.,](\d{1,2})\s*km", line_clean, re.IGNORECASE)
                if match:
                    try:
                        dist_val = float(f"{match.group(1)}.{match.group(2)}")
                        if 0.5 < dist_val < 100:
                            distance = f"{dist_val:.2f} km"
                    except:
                        pass
                else:
                    # Fallback: look for any floating number + 'km' in safe contexts
                    match = re.search(r"\b(\d{1,3})[.,](\d{1,2})\s*km\b", line_clean)
                    if match:
                        try:
                            dist_val = float(f"{match.group(1)}.{match.group(2)}")
                            # Exclude small values like 0.02, or common pace-like ranges
                            if 0.5 < dist_val < 100:
                                distance = f"{dist_val:.2f} km"
                        except:
                            pass


        if pace == "Unknown":
            match = re.search(r"Average\s+(\d{1,2})'(\d{2})", line_clean)
            if match:
                pace = f"{match.group(1)}'{match.group(2)}"

        if best_pace == "Unknown":
            match = re.search(r"Best\s+(?:km|lap)?\s*(\d{1,2})[^\d]?(\d{2})", line_clean)
            if match:
                best_pace = f"{match.group(1)}'{match.group(2)}"

        if "Heart Rate" in line and avg_hr is None:
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line_clean)
            if match:
                max_hr = int(match.group(1))
                avg_hr = int(match.group(2))

    # === Distance fallback (from joined noisy lines) ===
    if distance == "Unknown":
        recovered = recover_distance_from_lines(lines)
        if recovered:
            distance = recovered

    # === Extra time detection based on context ===
    for i, line in enumerate(lines):
        if time != "0:00":
            break

        line_clean = line.strip()
        match = re.search(r"\b(\d{1,2}):(\d{2})\b", line_clean)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))

            if 5 <= minutes < 300:
                next_line = lines[i+1].lower() if i+1 < len(lines) else ""
                prev_line = lines[i-1].lower() if i-1 >= 0 else ""
                context = f"{prev_line} {line_clean.lower()} {next_line}"
                if "activity time" in context:
                    time = f"{minutes}:{seconds:02d}"
                    break

    return {
        "time": time,
        "distance": distance,
        "pace": pace,
        "best_pace": best_pace,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
    }
