import re

def extract_hr_zones(lines):
    hr_zones = {}

    pattern = re.compile(
        r"(Recovery|Aerobic Endurance|Aerobic Power|Threshold|Anaerobic Endurance|Anaerobic Power)[^\d<>]*"
        r"([<>]?\d{2,3}(?:[-–]\d{2,3})?)\s+(\d{1,3})%\D*?(\d{1,2}:\d{2})",
        re.IGNORECASE
    )

    for line in lines:
        match = pattern.search(line)
        if match:
            zone = match.group(1).strip().title()
            hr_range = match.group(2).strip()
            percent = int(match.group(3))
            time_str = match.group(4)

            hr_zones[zone] = {
                "time": time_str,
                "percent": percent,
                "hr_range": hr_range
            }
            print(f"[DEBUG] Parsed HR zone: {zone} → {hr_zones[zone]}")
        else:
            print(f"[DEBUG] No HR zone match in line: {line}")

    return hr_zones or None
