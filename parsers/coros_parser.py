# parsers/coros_parser.py
import pytesseract
import re

def coros_parser(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Normalize text
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    lines = text.splitlines()

    # === DISTANCE ===
    distance = "Unknown"
    distance_count = 0
    for line in lines:
        if re.search(r"\b1\.00\s*km\b", line):
            distance_count += 1
    if distance_count:
        distance = f"{distance_count:.2f} km"

    # === TIME (Total) ===
    time = "Unknown"
    for line in lines:
        if re.search(r"\bTotal Time\b", line, re.IGNORECASE):
            match = re.search(r"(\d{1,2}[:.]\d{2})", line)
            if match:
                time = match.group(1).replace(".", ":")
                break

    # Fallback: last line with 41:15-like pattern
    if time == "Unknown":
        for line in reversed(lines):
            match = re.findall(r"(\d{1,2}[:.]\d{2})", line)
            if match:
                time = match[0].replace(".", ":")
                break

    # === SPLITS ===
    splits = []
    for line in lines:
        # Match: "1 1.00 km 4:57.59 4'58" /km"
        match = re.match(r"^\s*(\d+)\s+1\.00\s*km\s+[\d:.]+\s+(\d{1,2}'\d{2})", line)
        if match:
            km = int(match.group(1))
            pace = match.group(2).replace("’", "'").replace("`", "'")
            splits.append({"km": km, "time": pace})

    # === Final output ===
    return {
        "distance": distance,
        "time": time,
        "pace": "Unknown",
        "best_pace": "Unknown",
        "splits": splits,
        "avg_hr": None,
        "max_hr": None,
        "cadence_avg": None,
        "cadence_max": None,
        "stride_length_avg": None
    }
