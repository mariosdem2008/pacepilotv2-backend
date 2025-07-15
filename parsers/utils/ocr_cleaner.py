import re

def clean_ocr_lines(raw_text):
    # Normalize characters
    text = raw_text
    text = text.replace("O", "0").replace("o", "0")
    text = text.replace("|", "1").replace("l", "1").replace("I", "1")
    text = text.replace("e", ".")
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("°", "'").replace("`", "'")

    # Remove very noisy lines
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # Skip lines that are mostly symbols or very short
        if len(line) < 3 or re.match(r"^[^\w\d]+$", line):
            continue
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
