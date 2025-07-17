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
    Joins all lines and looks for number + km pattern allowing for OCR noise.
    """
    joined_text = " ".join(lines).lower()

    # Fix common OCR confusions
    joined_text = (
        joined_text.replace("o", "0")
        .replace("l", "1")
        .replace("|", "1")
    )

    # Remove km/h to avoid false positives
    joined_text = re.sub(r"\d+\s*[.,]?\s*\d*\s*km/h", "", joined_text)
    joined_text = re.sub(r"\.{2,}", ".", joined_text)

    # Handle OCR like "4 e 9 / km" → "4.90 km"
    joined_text = re.sub(r"(\d)\s*[eE]\s*(\d)\s*/\s*km", r"\1.\2" + "0 km", joined_text)

    # Also handle "5 e 3 3 km" → "5.33 km"
    joined_text = re.sub(r"(\d)\s*[eE]\s*(\d)\s*(\d)\s*km", r"\1.\2\3 km", joined_text)

    # Clean up malformed decimal numbers like "4.9.0"
    joined_text = re.sub(r"(\d)\.(\d)\.(\d)", r"\1.\2\3", joined_text)

    patterns = [
        r"(\d{1,3}[.,]\d{1,2})\s*km",
        r"(\d{1,3})\s*[.,]?\s*(\d{1,2})\s*km"
    ]

    best_dist = 0.0

    for pattern in patterns:
        matches = re.findall(pattern, joined_text)
        if matches:
            for m in matches:
                if isinstance(m, tuple):
                    dist_str = ".".join(part.strip() for part in m)
                else:
                    dist_str = m.strip()
                try:
                    dist = float(dist_str.replace(",", "."))
                    if 0.5 < dist < 100 and dist > best_dist:
                        best_dist = dist
                except:
                    continue

    if best_dist > 0:
        print(f"[DEBUG] OCR recovered distance: {best_dist:.2f} km", flush=True)
        return f"{best_dist:.2f} km"

    return None