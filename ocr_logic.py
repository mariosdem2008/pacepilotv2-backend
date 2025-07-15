#ocr_logic.py
from parsers import coros_parser, garmin_parser, polar_parser, suunto_parser, apple_parser

def extract_workout_data(image, source: str):
    if source == 'coros':
        return coros_parser(image)
    elif source == 'garmin':
        return garmin_parser(image)
    else:
        raise ValueError(f"Unsupported source: {source}")

def extract_workout_data_combined(images, source: str):
    if source != 'coros':
        raise ValueError(f"Multi-image parsing not supported for: {source}")

    total_distance = 0.0
    total_seconds = 0
    combined_splits = []
    best_pace_seconds = None
    extra_data = {}

    for image in images:
        data = coros_parser(image)
        splits = data.get("splits", [])

        for s in splits:
            km = float(s["km"].split()[0])
            total_distance += km
            sec = _parse_time_to_sec(s["time"])
            total_seconds += sec
            pace_sec = _pace_to_seconds(s["pace"])
            if pace_sec is not None:
                if best_pace_seconds is None or pace_sec < best_pace_seconds:
                    best_pace_seconds = pace_sec
            combined_splits.append(s)

        # Merge meta once (just take from the first valid response)
        if not extra_data:
            for key in ["avg_hr", "max_hr", "cadence_avg", "cadence_max", "stride_length_avg", "hr_zones"]:
                if data.get(key):
                    extra_data[key] = data[key]

    time_str = f"{int(total_seconds // 60)}:{int(total_seconds % 60):02d}"
    pace_str = "Unknown"
    if total_distance > 0:
        avg_pace_sec = int(total_seconds / total_distance)
        pace_str = f"{avg_pace_sec // 60}'{avg_pace_sec % 60:02d}"

    best_pace_str = f"{best_pace_seconds // 60}'{best_pace_seconds % 60:02d}" if best_pace_seconds else "Unknown"

    return {
        "distance": f"{total_distance:.2f} km",
        "time": time_str,
        "pace": pace_str,
        "best_pace": best_pace_str,
        "splits": combined_splits,
        **extra_data
    }

def _parse_time_to_sec(t):
    try:
        if ':' in t:
            mins, secs = t.split(':')
        elif '.' in t:
            mins, secs = t.split('.')
        else:
            return 0
        return int(mins) * 60 + float(secs)
    except:
        return 0

def _pace_to_seconds(pace_str):
    try:
        parts = pace_str.replace("’", "'").replace("`", "'").split("'")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
    except:
        return None
