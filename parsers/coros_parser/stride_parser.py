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

    def fix_common_ocr_errors(text: str) -> str:
        # Only fix common OCR mistakes in known keywords
        replacements = {
            'cadence': 'cadence',
            'stride': 'stride',
            'length': 'length',
            'average': 'average',
            'max': 'max',
            'min': 'min',
            'gain': 'gain',
            'loss': 'loss',
            'power': 'power',
            'elevation': 'elevation',
        }
        for wrong, correct in replacements.items():
            pattern = re.compile(''.join(f"[{c}{c.swapcase()}0o]" if c.lower() == 'o' else 
                                         f"[{c}{c.swapcase()}1l]" if c.lower() == 'l' else 
                                         f"[{c}{c.swapcase()}5s]" if c.lower() == 's' else 
                                         f"[{c}{c.swapcase()}]" for c in wrong), re.IGNORECASE)
            text = pattern.sub(correct, text)
        return text

    def try_extract_int(text: str) -> Optional[int]:
        try:
            return int(text)
        except ValueError:
            return None

    for line in lines:
        raw_line = line.strip()
        fixed_line = fix_common_ocr_errors(raw_line)
        line_lower = fixed_line.lower()

        # Cadence
        if "cadence" in line_lower:
            match = re.search(r"max[^0-9]*(\d+)[^0-9]+average[^0-9]*(\d+)", line_lower)
            if match:
                data["cadence_max"] = try_extract_int(match.group(1))
                data["cadence_avg"] = try_extract_int(match.group(2))

        # Stride Length
        if "stride length" in line_lower:
            match = re.search(r"average[^0-9]*(\d+)", line_lower)
            if match:
                data["stride_length_avg"] = try_extract_int(match.group(1))

        # Running Power
        if "running power" in line_lower:
            match = re.search(r"max[^0-9]*(\d+)[^0-9]+average[^0-9]*(\d+)", line_lower)
            if match:
                data["running_power_max"] = try_extract_int(match.group(1))
                data["running_power_avg"] = try_extract_int(match.group(2))
            else:
                match = re.search(r"average[^0-9]*(\d+)[^0-9]+max[^0-9]*(\d+)", line_lower)
                if match:
                    data["running_power_avg"] = try_extract_int(match.group(1))
                    data["running_power_max"] = try_extract_int(match.group(2))

        # Elevation Gain / Loss
        if "elevation" in line_lower and ("gain" in line_lower or "loss" in line_lower):
            match = re.search(r"gain[^0-9]*(\d+)[^\d]+loss[^0-9]*(\d+)", line_lower)
            if match:
                data["elevation_gain"] = try_extract_int(match.group(1))
                data["elevation_loss"] = try_extract_int(match.group(2))

        # Elevation Max / Min / Avg
        if "max" in line_lower and "min" in line_lower and "average" in line_lower:
            match = re.search(r"max[^0-9]*(\d+)[^\d]+min[^0-9]*(\d+)[^\d]+average[^0-9]*(\d+)", line_lower)
            if match:
                data["elevation_max"] = try_extract_int(match.group(1))
                data["elevation_min"] = try_extract_int(match.group(2))
                data["elevation_avg"] = try_extract_int(match.group(3))

    return data
