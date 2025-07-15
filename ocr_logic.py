import yaml
import cv2
import numpy as np
from PIL import Image
import pytesseract

from parsers import coros_parser, garmin_parser, polar_parser, suunto_parser, apple_parser

# Load ROI config once
def load_roi_config(path="layout.yaml"):
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    return config["roi"]

ROI_CONFIG = load_roi_config()

def pil_to_cv(image_pil):
    # Convert PIL Image to OpenCV BGR format
    open_cv_image = np.array(image_pil)
    return cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

def crop_roi(image_cv, roi_coords):
    x1, y1, x2, y2 = roi_coords["x1"], roi_coords["y1"], roi_coords["x2"], roi_coords["y2"]
    return image_cv[y1:y2, x1:x2]

def preprocess_roi(roi_image):
    gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text_from_roi(image_pil, roi_coords):
    image_cv = pil_to_cv(image_pil)
    cropped = crop_roi(image_cv, roi_coords)
    processed = preprocess_roi(cropped)
    text = pytesseract.image_to_string(processed, config="--psm 6")
    return text.strip()

from parsers import coros_parser, garmin_parser
from image_utils_cv import crop_roi, preprocess_roi
import numpy as np

def extract_workout_data(image, source: str):
    if source == 'coros':
        full_image_cv = np.array(image.convert("RGB"))[:, :, ::-1]  # PIL → OpenCV (BGR)
        roi_coords = (100, 200, 800, 1000)  # Replace with your actual coordinates
        roi_image = crop_roi(full_image_cv, roi_coords)
        preprocessed_roi = preprocess_roi(roi_image)

        return coros_parser(preprocessed_roi, preprocess=False)

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

        # Take extra data from the first valid response only
        if not extra_data:
            for key in ["avg_hr", "max_hr", "cadence_avg", "cadence_max", "stride_length_avg", "hr_zones"]:
                if key in data and data[key] is not None:
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
    except Exception:
        return 0

def _pace_to_seconds(pace_str):
    try:
        parts = pace_str.replace("’", "'").replace("`", "'").split("'")
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return None
