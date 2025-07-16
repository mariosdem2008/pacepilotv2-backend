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

    # Normalize common OCR confusions in numbers carefully
    # Only replace in contexts where digits are involved
    joined_text = re.sub(r"(?<=\d)[e]", ".", joined_text)  # only replace 'e' after digits
    joined_text = joined_text.replace("o", "0").replace("l", "1").replace("|", "1").replace("/", ".")

    # Remove km/h speeds (prevent false positives)
    joined_text = re.sub(r"\d+\s*[.,]?\s*\d*\s*km/h", "", joined_text)

    # Normalize multiple dots or mixed separators
    joined_text = re.sub(r"\.{2,}", ".", joined_text)
    joined_text = re.sub(r"[.,]\s*[.,]", ".", joined_text)

    # Patterns to catch distances like '4.97 km', '4 97 km', '4.9.7 km', or '5 km'
    patterns = [
        r"(\d{1,3}[.,]?\d{0,2})\s*km"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, joined_text)
        for m in matches:
            dist_str = m.replace(",", ".").replace(" ", "")
            try:
                dist = float(dist_str)
                if 0.5 < dist < 100:
                    return f"{dist:.2f} km"
            except:
                continue

    return None