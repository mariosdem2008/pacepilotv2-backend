import re

def extract_hr_zones(lines):
    hr_zones = {}

    for line in lines:
        if any(zone in line for zone in ["Recovery", "Aerobic", "Threshold", "Anaerobic"]):
            # Match pattern: ZoneName <or> Range <optional percent> <time>
            match = re.match(
                r"(Recovery|Aerobic Endurance|Aerobic Power|Threshold|Anaerobic Endurance|Anaerobic Power)[^\d<>=]*([\d>–<\-]+)?[^\d]*(\d{1,3})?%?\s*[=:-]?\s*(\d{1,2}:\d{2})",
                line
            )
            if match:
                zone_name = match.group(1).strip()
                hr_range = match.group(2).strip() if match.group(2) else None
                percent = int(match.group(3)) if match.group(3) else None
                time_str = match.group(4)

                hr_zones[zone_name] = {
                    "time": time_str,
                    "percent": percent,
                    "hr_range": hr_range
                }

    return hr_zones if hr_zones else None
