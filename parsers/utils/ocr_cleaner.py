import re

def clean_ocr_lines(text):
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        # Replace some common misread chars but be conservative:
        line = line.replace("’", "'").replace("“", '"').replace("”", '"').replace("°", "'").replace("`", "'")
        # Only fix digits that might be misread
        line = line.replace("O", "0")
        line = line.replace("l", "1")
        line = line.replace("|", "1")
        # Don't remove spaces or punctuation (keep commas, dots, colons)
        cleaned_lines.append(line)
    return cleaned_lines



def recover_distance_from_cleaned(cleaned_lines):
    joined = " ".join(cleaned_lines)
    match = re.search(r"(\d)\s*(\.|,)\s*(\d{1,2})\s*km", joined, re.IGNORECASE)
    if match:
        try:
            return float(f"{match.group(1)}.{match.group(3)}")
        except:
            pass
    return None


def recover_distance_from_lines(lines):
    """
    Attempt to recover a decimal distance from noisy OCR lines.
    Joins all lines and looks for number + km pattern allowing for OCR noise,
    excluding 'km/h' speed entries.
    """
    joined_text = " ".join(lines).lower()

    # Exclude text that clearly refers to speed (km/h)
    if "km/h" in joined_text:
        # remove or replace those segments entirely
        joined_text = re.sub(r"\d{1,3}\s*[.,]?\s*\d{0,2}\s*km/h", "", joined_text)

    # Fix common OCR confusions
    joined_text = joined_text.replace("e", ".").replace("o", "0").replace("l", "1").replace("|", "1")

    # Patterns to catch something like '4.97 km' or '4 97 km'
    patterns = [
        r"(\d{1,3}[.,]?\s?\d{1,2})\s*km",
        r"(\d{1,3})\s*[.,]?\s*(\d{1,2})\s*km"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, joined_text)
        if matches:
            for m in matches:
                dist_str = ".".join(part.strip() for part in m) if isinstance(m, tuple) else m.strip()
                try:
                    dist = float(dist_str.replace(",", "."))
                    if 0.1 < dist < 100:
                        return f"{dist:.2f} km"
                except:
                    continue
    return None