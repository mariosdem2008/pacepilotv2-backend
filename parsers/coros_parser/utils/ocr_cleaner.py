# ocr_cleaner.py
import re

def clean_ocr_lines(text):
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        # Replace common OCR misreads
        line = line.replace("’", "'").replace("“", '"').replace("”", '"').replace("°", "'").replace("`", "'")
        line = line.replace("O", "0").replace("o", "0")  # add lowercase 'o' too
        line = line.replace("l", "1").replace("|", "1")
        cleaned_lines.append(line)
    return cleaned_lines


def recover_distance_from_lines(lines):
    """
    Attempt to recover a decimal distance from noisy OCR lines.
    Joins all lines and looks for number + km pattern allowing for OCR noise,
    excluding 'km/h' speed entries.
    """
    joined_text = " ".join(lines).lower()

    # Remove speed entries like "20 km/h"
    joined_text = re.sub(r"\b\d{1,3}\s*[.,]?\s*\d{0,2}\s*km/h\b", "", joined_text)

    # Fix common OCR confusions
    joined_text = joined_text.replace("e", ".").replace("o", "0").replace("l", "1").replace("|", "1")

    # Match decimal or spaced-out values like 4.97 km, 4 ,97 km, etc.
    patterns = [
        r"\b(\d{1,3})\s*[.,]?\s*(\d{1,2})\s*km\b",       # 4 ,97 km
        r"\b(\d{1,3}[.,]\d{1,2})\s*km\b",                # 4.97 km
    ]

    for pattern in patterns:
        matches = re.findall(pattern, joined_text)
        if matches:
            for m in matches:
                try:
                    # Normalize number
                    dist_str = ".".join(m) if isinstance(m, tuple) else m
                    dist_str = dist_str.replace(",", ".").strip()
                    dist = float(dist_str)
                    if 0.5 < dist < 100:  # ignore outliers
                        return f"{dist:.2f} km"
                except ValueError:
                    continue
    return None
