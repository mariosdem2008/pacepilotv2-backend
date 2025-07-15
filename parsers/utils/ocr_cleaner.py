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






def recover_distance_from_lines(lines):
    """
    Try to find distance info in distorted OCR lines by looking for numeric patterns
    close to 'km' or 'istance' keywords, and fix common OCR confusions.
    """
    joined_text = " ".join(lines).lower()

    # Fix common OCR misreads for decimal/digits
    joined_text = joined_text.replace("e", ".").replace("o", "0").replace("l", "1").replace("|", "1")

    # Look for patterns like: digit(s) . digit(s) km or digit(s) km, allowing spaces and noise between
    patterns = [
        r"(\d{1,3}[.,]?\s?\d{1,2})\s*km",
        r"(\d{1,3})\s*[.,]?\s*(\d{1,2})\s*km"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, joined_text)
        if matches:
            # matches can be tuples or strings depending on pattern
            for m in matches:
                if isinstance(m, tuple):
                    # Join parts e.g. ('4', '97') -> '4.97'
                    dist_str = ".".join(part.strip() for part in m)
                else:
                    dist_str = m.strip()
                try:
                    dist = float(dist_str.replace(",", "."))
                    if 0.1 < dist < 100:  # reasonable distance range
                        return f"{dist:.2f} km"
                except:
                    continue
    return None