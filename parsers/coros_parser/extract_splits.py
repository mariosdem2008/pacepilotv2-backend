import re

def extract_prefix_number(line):
    match = re.match(r"^\s*(\d+)", line)
    return int(match.group(1)) if match else None

def reorder_lines_by_min_prefix(lines):
    # Collect lines with prefix numbers
    lines_with_prefix = [(extract_prefix_number(line), i, line) for i, line in enumerate(lines)]
    lines_with_prefix = [(num, i, line) for num, i, line in lines_with_prefix if num is not None]

    if not lines_with_prefix:
        return lines  # nothing to sort

    # Find line with the lowest prefix number
    min_prefix, min_index, _ = min(lines_with_prefix, key=lambda x: x[0])

    # Reorder: from the line with the lowest prefix onward, then the lines before
    return lines[min_index:] + lines[:min_index]

def extract_splits(lines):
    lines = reorder_lines_by_min_prefix(lines)

    parsed_lines = []
    splits = []
    total_split_distance = 0.0
    split_index = 1

    for line in lines:
        line = line.strip()
        try:
            match = re.match(
                r"^\s*(\d+)?\s*(Run|Rest)\s+([\d.,]+)\s*km\s+([\d:.]+)?\s*(\d{1,2}|--|°°)?['’°]?(?:(\d{2}|--))?(?:\"|”)?(?:\s*/km)?",
                line
            )
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
        except:
            continue

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

        # Start a new split after each Run
        if i + 1 < len(parsed_lines) and parsed_lines[i + 1]["label"] == "Run":
            split_index += 1
            current_split_entries.clear()

    return splits, total_split_distance
