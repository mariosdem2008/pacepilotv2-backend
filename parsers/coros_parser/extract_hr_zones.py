import re

def extract_hr_zones(lines):
    hr_zones = {}
    # Define patterns to catch times in format mm:ss or h:mm:ss optionally, per zone name
    zone_patterns = {
        "Recovery": r"Recovery.*?(\d{1,2}:\d{2}(?::\d{2})?)",
        "Aerobic Endurance": r"Aerobic Endurance.*?(\d{1,2}:\d{2}(?::\d{2})?)",
        "Aerobic Power": r"Aerobic Power.*?(\d{1,2}:\d{2}(?::\d{2})?)",
        "Threshold": r"Threshold.*?(\d{1,2}:\d{2}(?::\d{2})?)",
        "Anaerobic Endurance": r"Anaerobic Endurance.*?(\d{1,2}:\d{2}(?::\d{2})?)",
        "Anaerobic Power": r"Anaerobic Power.*?(\d{1,2}:\d{2}(?::\d{2})?)"
    }

    for line in lines:
        for zone, pattern in zone_patterns.items():
            if zone in line:
                match = re.search(pattern, line)
                if match:
                    time_str = match.group(1)
                    # Normalize times like "1:05:10" or "22:37"
                    hr_zones[zone] = time_str

    return hr_zones if hr_zones else None
