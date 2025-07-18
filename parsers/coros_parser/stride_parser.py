import re
from typing import Optional, List, Dict

def parse_workout_metrics(lines: List[str]) -> Dict[str, Optional[int]]:
    """
    Parses workout metrics (cadence, stride length, running power, elevation) from OCR lines.
    """
    metrics = {
        "cadence_avg": None,
        "cadence_max": None,
        "stride_length_avg": None,
        "running_power_avg": None,
        "running_power_max": None,
        "elevation_gain": None,
        "elevation_loss": None,
        "elevation_min": None,
        "elevation_max": None,
        "elevation_avg": None
    }

    for line in lines:
        line = line.strip()

        if "Cadence" in line:
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if match:
                metrics["cadence_max"] = int(match.group(1))
                metrics["cadence_avg"] = int(match.group(2))

        elif "Stride Length" in line and "Average" in line:
            match = re.search(r"Average\s+(\d+)", line)
            if match:
                metrics["stride_length_avg"] = int(match.group(1))

        elif "Running Power" in line:
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if match:
                metrics["running_power_max"] = int(match.group(1))
                metrics["running_power_avg"] = int(match.group(2))

        elif "Elevation" in line:
            gain = re.search(r"Gain\s+(\d+)", line)
            loss = re.search(r"Loss\s+(\d+)", line)
            max_ = re.search(r"Max\s+(\d+)", line)
            min_ = re.search(r"Min\s+(\d+)", line)
            avg = re.search(r"Average\s+(\d+)", line)

            if gain:
                metrics["elevation_gain"] = int(gain.group(1))
            if loss:
                metrics["elevation_loss"] = int(loss.group(1))
            if max_:
                metrics["elevation_max"] = int(max_.group(1))
            if min_:
                metrics["elevation_min"] = int(min_.group(1))
            if avg:
                metrics["elevation_avg"] = int(avg.group(1))

    return metrics
