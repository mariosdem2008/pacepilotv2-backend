import re

def extract_prefix_number(line):
    match = re.match(r"^\s*(\d+)", line)
    return int(match.group(1)) if match else None

def reorder_lines_by_min_prefix(lines):
    lines_with_prefix = [(extract_prefix_number(line), i, line) for i, line in enumerate(lines)]
    lines_with_prefix = [(num, i, line) for num, i, line in lines_with_prefix if num is not None]

    if not lines_with_prefix:
        return lines

    min_prefix, min_index, _ = min(lines_with_prefix, key=lambda x: x[0])
    return lines[min_index:] + lines[:min_index]

def extract_summary_info(text):
    """
    Extract overall workout info from summary-type OCR.
    """
    distance = None
    time = None
    avg_pace = None
    best_pace = None

    for line in text:
        line = line.strip()
        # Distance
        if distance is None:
            match = re.search(r"([\d.,]+)\s*km", line, re.IGNORECASE)
            if match:
                distance = f"{match.group(1).replace(',', '.')} km"

        # Total Time
        if time is None:
            match = re.search(r"\b(\d{1,2}:\d{2}(?::\d{2})?)\b", line)
            if match:
                time = match.group(1)

        # Avg Pace
        if avg_pace is None:
            match = re.search(r"Avg(?:\.|erage)?\s*[:]?[\s]*([\d]{1,2})[‘'’]?(\d{2})", line)
            if match:
                avg_pace = f"{match.group(1)}'{match.group(2)}"

        # Best Pace
        if best_pace is None:
            match = re.search(r"Best.*?([\d]{1,2})[‘'’]?(\d{2})", line)
            if match:
                best_pace = f"{match.group(1)}'{match.group(2)}"

    return {
        "distance": distance,
        "time": time,
        "pace": avg_pace,
        "best_pace": best_pace,
        "splits": [],
        "avg_hr": None,
        "max_hr": None,
        "cadence_avg": None,
        "cadence_max": None,
        "stride_length_avg": None,
        "hr_zones": None
    }

def extract_splits(lines):
    lines = reorder_lines_by_min_prefix(lines)

    parsed_lines = []
    splits = []
    total_split_distance = 0.0
    split_index = 1

    split_pattern = re.compile(
        r"^\s*(\d+)?\s*(Run|Rest)\s+([\d.,]+)\s*km\s+([\d:.]+)?\s*(\d{1,2}|--|°°)?['’°]?(?:(\d{2}|--))?(?:\"|”)?(?:\s*/km)?",
        re.IGNORECASE
    )

    for line in lines:
        line = line.strip()
        match = split_pattern.match(line)
        if not match:
            continue

        label = match.group(2)
        km = float(match.group(3).replace(",", ".")) if match.group(3) else 0.0
        time_str = match.group(4) or "0:00"
        pace_min = (match.group(5) or "--").replace("°", "").replace("’", "").replace("'", "")
        pace_sec = (match.group(6) or "--").replace("°", "").replace("’", "").replace("\"", "")

        pace_str = "-- /km" if pace_min == "--" or pace_sec == "--" else f"{pace_min}'{pace_sec}"

        parsed_lines.append({
            "label": label,
            "km": km,
            "time": time_str,
            "pace": pace_str
        })

    current_split_entries = set()
    for i, entry in enumerate(parsed_lines):
        entry_key = (entry["label"], f"{entry['km']:.2f} km", entry["time"], entry["pace"])
        if entry_key not in current_split_entries:
            splits.append({
                "split": split_index,
                "label": entry["label"],
                "km": f"{entry['km']:.2f} km",
                "time": entry["time"],
                "pace": entry["pace"]
            })
            current_split_entries.add(entry_key)

        total_split_distance += entry["km"]

        if i + 1 < len(parsed_lines) and parsed_lines[i + 1]["label"] == "Run":
            split_index += 1
            current_split_entries.clear()

    return splits, total_split_distance

def parse_coros_ocr(lines):
    """
    Try to extract structured data from a list of OCR lines (strings).
    Will fall back to summary parsing if split table fails.
    """
    splits, total_split_distance = extract_splits(lines)

    if splits:
        return {
            "distance": f"{total_split_distance:.2f} km",
            "time": None,
            "pace": None,
            "best_pace": None,
            "avg_hr": None,
            "max_hr": None,
            "cadence_avg": None,
            "cadence_max": None,
            "stride_length_avg": None,
            "splits": splits,
            "hr_zones": None
        }
    else:
        return extract_summary_info(lines)
