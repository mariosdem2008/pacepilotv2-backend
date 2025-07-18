import re
from typing import Optional, Tuple, List, Dict

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
        if "Cadence" in line:
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if match:
                data["cadence_max"] = int(match.group(1))
                data["cadence_avg"] = int(match.group(2))

        if "Stride Length" in line and "Average" in line:
            match = re.search(r"Average\s+(\d+)", line)
            if match:
                data["stride_length_avg"] = int(match.group(1))

        if "Running Power" in line:
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if match:
                data["running_power_max"] = int(match.group(1))
                data["running_power_avg"] = int(match.group(2))

        if "Elevation" in line and ("Gain" in line or "Loss" in line):
            match = re.search(r"Gain\s+(\d+).*Loss\s+(\d+)", line)
            if match:
                data["elevation_gain"] = int(match.group(1))
                data["elevation_loss"] = int(match.group(2))

        if "Max" in line and "Min" in line and "Average" in line and "Elevation" not in line:
            match = re.search(r"Max\s+(\d+)\s+Min\s+(\d+)\s+Average\s+(\d+)", line)
            if match:
                data["elevation_max"] = int(match.group(1))
                data["elevation_min"] = int(match.group(2))
                data["elevation_avg"] = int(match.group(3))

    return data
