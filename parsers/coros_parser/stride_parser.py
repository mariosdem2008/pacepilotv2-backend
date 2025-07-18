import re
from typing import Optional, List, Dict

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

    def normalize_ocr(text: str) -> str:
        return (
            text.replace("0", "o")
                .replace("1", "l")
                .replace("5", "s")
                .replace("—", "-")
        )

    for line in lines:
        line = normalize_ocr(line.strip())
        line_lower = line.lower()

        print(f"[DEBUG] LINE: {line}")

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

        # Running Power (handle "P0wer" as "Power")
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

        # Elevation Gain / Loss (OCR "E1evati0n", "L0ss")
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
