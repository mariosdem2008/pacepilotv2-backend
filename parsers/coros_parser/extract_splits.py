import re

def extract_splits(lines):
    splits = []
    total_split_distance = 0.0
    split_index = 1
    parsed_lines = []

    for line in lines:
        line = line.strip()
        original_line = line
        try:
            match = re.match(
                r"^\s*(\d+)?\s*(Run|Rest)\s+([\d.,]+)\s*km\s+([\d:.]+)?\s*(\d{1,2}|--)?'(\d{2}|--)?(?:\"|”)?(?:\s*/km)?",
                line
            )
            if not match:
                match = re.match(
                    r"^\s*(Run|Rest)\s+([\d.,]+)\s*km\s+([\d:.]+)?\s*(\d{1,2}|--)?'(\d{2}|--)?(?:\"|”)?(?:\s*/km)?",
                    line
                )
                if match:
                    label = match.group(1)
                    km = float(match.group(2).replace(",", ".")) if match.group(2) else 0.0
                    time_str = match.group(3) or "0:00"
                    pace_min = match.group(4) or "--"
                    pace_sec = match.group(5) or "--"
                else:
                    print(f"⏭️ Skipped unrecognized line: {original_line}", flush=True)
                    continue
            else:
                label = match.group(2)
                km = float(match.group(3).replace(",", ".")) if match.group(3) else 0.0
                time_str = match.group(4) or "0:00"
                pace_min = match.group(5) or "--"
                pace_sec = match.group(6) or "--"

            pace_str = "-- /km" if pace_min == "--" or pace_sec == "--" else f"{pace_min}'{pace_sec}"

            parsed_lines.append({
                "label": label,
                "km": km,
                "time": time_str,
                "pace": pace_str
            })

        except Exception as e:
            print(f"⚠️ Error parsing line: {original_line} -> {e}", flush=True)

    current_split_entries = set()
    for i, entry in enumerate(parsed_lines):
        label = entry["label"]
        km = entry["km"]
        time_str = entry["time"]
        pace_str = entry["pace"]

        entry_key = (label, f"{km:.2f} km", time_str, pace_str)

        if entry_key not in current_split_entries:
            splits.append({
                "split": split_index,
                "label": label,
                "km": f"{km:.2f} km",
                "time": time_str,
                "pace": pace_str
            })
            current_split_entries.add(entry_key)

        total_split_distance += km

        if i + 1 < len(parsed_lines) and parsed_lines[i + 1]["label"] == "Run":
            split_index += 1
            current_split_entries.clear()

    return splits, total_split_distance
