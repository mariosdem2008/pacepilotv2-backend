import re

def extract_summary(lines):
    time = "0:00"
    distance = "Unknown"
    pace = "Unknown"
    best_pace = "Unknown"
    avg_hr = None
    max_hr = None

    
    for line in lines:
        line_clean = line.replace("’", "'").replace("", "'")

        if time == "0:00":
            match = re.search(r"\bTime\b.*?(\d{1,2}:\d{2})", line_clean, re.IGNORECASE)
            if match:
                time = match.group(1)

        if distance == "Unknown":
            match = re.search(r"\bDistance\b.*?(\d{1,3}[.,]\d{1,2})\s*km", line_clean, re.IGNORECASE)
            if match:
                distance = f"{float(match.group(1).replace(',', '.')):.2f} km"

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

    # === EXTRA EXTRACTION FOR TIME & DISTANCE WITHOUT LABELS ===
    for line in lines:
        if distance == "Unknown" and "km/h" not in line.lower():
            match = re.search(r"([\d.,]{2,5})\s*[kKmMwW]", line)
            if match:
                value = float(match.group(1).replace(",", "."))
                if 0.5 < value < 100:
                    distance = f"{value:.2f} km"


    # === EXTRA TIME DETECTION — FLOATING FORMATS OR ACTIVITY TIME LABEL ===
    for i, line in enumerate(lines):
        if time != "0:00":
            break  # already found

        line_clean = line.strip()

        # Match things like "32:14"
        match = re.search(r"\b(\d{1,2}):(\d{2})\b", line_clean)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))

            if 5 <= minutes < 300:  # Ignore short rest times or random clock stamps
                # Look ahead one line to check for "Activity Time" reference
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
        "max_hr": max_hr
    }
