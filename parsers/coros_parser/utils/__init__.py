import re

def parse_time_to_sec(t):
    try:
        parts = re.split(r"[:.]", t)
        return int(parts[0]) * 60 + float(parts[1])
    except:
        return 0

def pace_to_seconds(p):
    try:
        parts = p.replace("’", "'").replace("`", "'").split("'")
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return None
