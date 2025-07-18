def normalize_ocr_errors(text: str) -> str:
    # Fix common OCR errors (letters to digits)
    replacements = {
        'l': '1',
        'I': '1',
        '|': '1',
        'o': '0',
        'O': '0',
        's': '5',
        'S': '5',
        # Add more if needed
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def parse_workout_metrics(lines: List[str]) -> Dict[str, Optional[int]]:
    data = {
        "cadence_avg": None,
        "cadence_max": None,
        "stride_length_avg": None,
        "running_power_avg": None,
        "running_power_max": None,
        "elevation_gain": None,
        "elevation_loss": None,
        "elevation_min": None,
        "elevation_max": None,
        "elevation_avg": None,
    }

    for line in lines:
        line = line.strip()
        clean_line = normalize_ocr_errors(line)
        line_lower = clean_line.lower()

        print(f"[DEBUG] Normalized LINE: {clean_line}")

        # Cadence
        if "cadence" in line_lower:
            match = re.search(r"max[^0-9]*(\d+)[^0-9]+average[^0-9]*(\d+)", line_lower)
            if match:
                data["cadence_max"] = int(match.group(1))
                data["cadence_avg"] = int(match.group(2))

        # Stride Length
        if "stride length" in line_lower:
            match = re.search(r"average[^0-9]*(\d+)", line_lower)
            if match:
                data["stride_length_avg"] = int(match.group(1))

        # Running Power
        if "running power" in line_lower:
            match = re.search(r"max[^0-9]*(\d+)[^0-9]+average[^0-9]*(\d+)", line_lower)
            if match:
                data["running_power_max"] = int(match.group(1))
                data["running_power_avg"] = int(match.group(2))
            else:
                match = re.search(r"average[^0-9]*(\d+)[^0-9]+max[^0-9]*(\d+)", line_lower)
                if match:
                    data["running_power_avg"] = int(match.group(1))
                    data["running_power_max"] = int(match.group(2))

        # Elevation Gain / Loss
        if "elevation" in line_lower and ("gain" in line_lower or "loss" in line_lower):
            match = re.search(r"gain[^0-9]*(\d+)[^\d]+loss[^0-9]*(\d+)", line_lower)
            if match:
                data["elevation_gain"] = int(match.group(1))
                data["elevation_loss"] = int(match.group(2))

        # Elevation Max / Min / Avg
        if "max" in line_lower and "min" in line_lower and "average" in line_lower:
            match = re.search(r"max[^0-9]*(\d+)[^\d]+min[^0-9]*(\d+)[^\d]+average[^0-9]*(\d+)", line_lower)
            if match:
                data["elevation_max"] = int(match.group(1))
                data["elevation_min"] = int(match.group(2))
                data["elevation_avg"] = int(match.group(3))

    return data
