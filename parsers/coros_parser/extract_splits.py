import re

def extract_splits(lines, distance="Unknown"):
    splits = []
    total_split_distance = 0.0
    split_index = 1
    parsed_lines = []

    for line in lines:
        line = line.strip()
        original_line = line

        # Try to match two possible line formats
        match = re.match(
            r"^\s*(\d+)?\s*(Run|Rest)\s+([\d.,]+)\s*km\s+([\d:.]+)?\s*(\d{1,2}|--)?'(\d{2}|--)?(?:\"|”)?(?:\s*/km)?",
            line
        )
        if not match:
            match = re.match(
                r"^\s*(Run|Rest)\s+([\d.,]+)\s*km\s+([\d:.]+)?\s*(\d{1,2}|--)?'(\d{2}|--)?(?:\"|”)?(?:\s*/km)?",
                line
            )
            if not match:
                print(f"⏭️ Skipped unrecognized line: {original_line}", flush=True)
                continue
            else:
                # Pattern without split number
                label = match.group(1)
                km = float(match.group(2).replace(",", ".")) if match.group(2) else 0.0
                time_str = match.group(3) or "0:00"
                pace_min = match.group(4) or "--"
                pace_sec = match.group(5) or "--"
        else:
            # Pattern with optional split number
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

        # Increment split index on next Run segment
        if i + 1 < len(parsed_lines) and parsed_lines[i + 1]["label"] == "Run":
            split_index += 1
            current_split_entries.clear()

    # === FALLBACK DISTANCE ===
    if distance == "Unknown":
        ocr_distance = None
        for line in lines:
            clean_line = line.replace("e", ".").replace("O", "0").replace("l", "1").replace("|", "1")
            clean_line = re.sub(r"\s+", "", clean_line)
            match = re.search(r"(\d{1,3}[.,]\d{1,2})km", clean_line, re.IGNORECASE)
            if match:
                ocr_distance = float(match.group(1).replace(",", "."))
                break
        if total_split_distance > 0:
            if not ocr_distance or abs(ocr_distance - total_split_distance) > 0.3:
                distance = f"{total_split_distance:.2f} km"
            else:
                distance = f"{ocr_distance:.2f} km"
        elif ocr_distance:
            distance = f"{ocr_distance:.2f} km"

    return splits, distance
