import pytesseract
import json
from .extract_hr_zones import extract_hr_zones
from .extract_summary import extract_summary
from .extract_splits import extract_splits
from .fallbacks import apply_fallbacks

def coros_parser(image):
    text = pytesseract.image_to_string(image, config='--psm 6')
    print("===== OCR TEXT START =====", flush=True)
    print(text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    text = text.replace("’", "'").replace("“", '"').replace("”", '"').replace("°", "'").replace("`", "'")
    lines = text.splitlines()

    hr_zones = extract_hr_zones(lines)
    summary = extract_summary(lines)
    splits, total_split_distance = extract_splits(lines)

    final_result = apply_fallbacks(summary, splits, total_split_distance, lines, text)

    final_result["splits"] = splits
    final_result["hr_zones"] = hr_zones if hr_zones else None

    print("\n===== FINAL PARSED WORKOUT DATA =====", flush=True)
    print(json.dumps(final_result, indent=2), flush=True)
    print("======================================\n", flush=True)

    return final_result
