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
    distance = None
    time = None
    avg_pace = None
    best_pace = None

    for line in text:
        line = line.strip()
        if distance is None:
            match = re.search(r"([\d.,]+)\s*km", line, re.IGNORECASE)
            if match:
                distance = f"{match.group(1).replace(',', '.')} km"
        if time is None:
            match = re.search(r"\b(\d{1,2}:\d{2}(?::\d{2})?)\b", line)
            if match:
                time = match.group(1)
        if avg_pace is None:
            match = re.search(r"Avg(?:\.|erage)?\s*[:]?[\s]*([\d]{1,2})[‘'’]?(\d{2})", line)
            if match:
                avg_pace = f"{match.group(1)}'{match.group(2)}"
        if best_pace is None:
            match = re.search(r"Best.*?([\d]{1,2})[‘'’]?(\d{2})", line)
            if match:
                best_pace = f"{match.group(1)}'{match.group(2)}"

    return {
        "distance": distance,
        "time": time,
        "pace": avg_pace or "Unknown",
        "best_pace": best_pace or "Unknown",
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
    is_lap_style = False
    is_run_rest_style = False

    # Pattern 1: Run/Rest style
    run_rest_pattern = re.compile(
        r"^\s*(\d+)?\s*(Run|Rest)\s+([\d.,]+)\s*km\s+([\d:.]+)?\s*(\d{1,2}|--|°°)?['’°]?(?:(\d{2}|--))?(?:\"|”)?(?:\s*/km)?",
        re.IGNORECASE
    )

    # Pattern 2: Lap style (loosened to allow non-standard time values)
    lap_pattern = re.compile(
        r"^\s*(\d+)\s+([\d.,]+)\s*km\s+([^\s]+(?: [^\s]+)?)\s+(\d{1,2})['’](\d{2})",
        re.IGNORECASE
    )

    for line in lines:
        line = line.strip()
        match = run_rest_pattern.match(line)
        if match:
            is_run_rest_style = True
            label = match.group(2)
            km = float(match.group(3).replace(",", ".")) if match.group(3) else 0.0
            time_str = match.group(4) or "0:00"
            pace_min = (match.group(5) or "--").replace("°", "").replace("’", "").replace("'", "")
            pace_sec = (match.group(6) or "--").replace("°", "").replace("’", "").replace("\"", "")
            pace_str = "-- /km" if pace_min == "--" or pace_sec == "--" else f"{pace_min}'{pace_sec}"
        else:
            match = lap_pattern.match(line)
            if not match:
                continue
            is_lap_style = True
            label = "Lap"
            km = float(match.group(2).replace(",", ".")) if match.group(2) else 0.0
            time_str = match.group(3)
            pace_str = f"{match.group(4)}'{match.group(5)}"

        parsed_lines.append({
            "label": label,
            "km": km,
            "time": time_str,
            "pace": pace_str
        })

    current_split_entries = set()

    for entry in parsed_lines:
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

            if is_lap_style:
                split_index += 1
            elif is_run_rest_style and entry["label"].lower() == "run":
                split_index += 1

        total_split_distance += entry["km"]

    return splits, total_split_distance



def parse_coros_ocr(lines):
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
