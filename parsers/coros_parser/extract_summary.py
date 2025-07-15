import re

def extract_summary(lines):
    time = "0:00"
    distance = "Unknown"
    pace = "Unknown"
    best_pace = "Unknown"
    avg_hr = None
    max_hr = None

    # 1️⃣ Extract labeled Time / Distance / Pace / Heart Rate / Best Pace
    for line in lines:
        clean_line = line.replace("’", "'").replace("`", "'")

        if time == "0:00":
            match = re.search(r"\bTime\b.*?(\d{1,2}:\d{2})", clean_line, re.IGNORECASE)
            if match:
                time = match.group(1)

        if distance == "Unknown":
            match = re.search(r"\bDistance\b.*?(\d{1,3}[.,]\d{1,2})\s*km", clean_line, re.IGNORECASE)
            if match:
                distance = f"{float(match.group(1).replace(',', '.')):.2f} km"

        if pace == "Unknown":
            match = re.search(r"Average\s+(\d{1,2})'(\d{2})", clean_line)
            if match:
                pace = f"{match.group(1)}'{match.group(2)}"

        if best_pace == "Unknown":
            match = re.search(r"Best\s+(?:km|lap)?\s*(\d{1,2})[^\d]?(\d{2})", clean_line)
            if match:
                best_pace = f"{match.group(1)}'{match.group(2)}"

        if "Heart Rate" in line and avg_hr is None:
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", clean_line)
            if match:
                max_hr = int(match.group(1))
                avg_hr = int(match.group(2))

    # 2️⃣ Fallback distance extraction without label (avoid km/h confusion)
    for line in lines:
        if distance == "Unknown" and "km/h" not in line.lower():
            match = re.search(r"([\d.,]{2,5})\s*[kKmMwW]", line)
            if match:
                value = float(match.group(1).replace(",", "."))
                if 0.5 < value < 100:
                    distance = f"{value:.2f} km"

    # 3️⃣ Floating time detection by context "Activity Time"
    if time == "0:00":
        for i, line in enumerate(lines):
            clean_line = line.strip()
            match = re.search(r"\b(\d{1,2}):(\d{2})\b", clean_line)
            if not match:
                continue
            minutes, seconds = int(match.group(1)), int(match.group(2))
            if 5 <= minutes < 300:  # plausible duration
                prev_line = lines[i - 1].lower() if i - 1 >= 0 else ""
                next_line = lines[i + 1].lower() if i + 1 < len(lines) else ""
                context = f"{prev_line} {clean_line.lower()} {next_line}"
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
