import re
from typing import Optional, Tuple, List

def parse_cadence_and_stride(lines: List[str]) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Parses cadence max, cadence average, and stride length average from given lines.

    Args:
        lines (List[str]): List of text lines to parse.

    Returns:
        Tuple containing:
            cadence_avg (Optional[int]): Average cadence, or None if not found.
            cadence_max (Optional[int]): Max cadence, or None if not found.
            stride_length_avg (Optional[int]): Average stride length, or None if not found.
    """
    cadence_avg = None
    cadence_max = None
    stride_length_avg = None

    for line in lines:
        if "Cadence" in line:
            # Example pattern: "Max 180 Average 160"
            match = re.search(r"Max\s+(\d+)\s+Average\s+(\d+)", line)
            if match:
                cadence_max = int(match.group(1))
                cadence_avg = int(match.group(2))
        if "Stride Length" in line and "Average" in line:
            # Example pattern: "Average 120"
            match = re.search(r"Average\s+(\d+)", line)
            if match:
                stride_length_avg = int(match.group(1))

    return cadence_avg, cadence_max, stride_length_avg
