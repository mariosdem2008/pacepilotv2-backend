import pytesseract
import json
from .extract_summary import extract_summary
from .extract_splits import extract_splits
from .fallbacks import apply_fallbacks
from .utils.ocr_cleaner import clean_ocr_lines
from .stride_parser import parse_workout_metrics  # ← updated

def coros_parser(image):
    raw_text = pytesseract.image_to_string(image, config='--psm 6')
    print("===== OCR TEXT START =====", flush=True)                                      
    print(raw_text, flush=True)
    print("===== OCR TEXT END =====", flush=True)

    # Clean OCR text before splitting
    lines = clean_ocr_lines(raw_text)

    summary = extract_summary(lines)
    splits, total_split_distance = extract_splits(lines)

    # Parse all workout metrics
    metrics = parse_workout_metrics(lines)

    # Pass cleaned lines and raw_text if needed to fallbacks
    final_result = apply_fallbacks(summary, splits, total_split_distance, lines, raw_text)

    final_result["splits"] = splits

    # Add parsed metrics to final result
    final_result.update(metrics)

    print("\n===== FINAL PARSED WORKOUT DATA =====", flush=True)
    print(json.dumps(final_result, indent=2), flush=True)
    print("======================================\n", flush=True)

    return final_result
