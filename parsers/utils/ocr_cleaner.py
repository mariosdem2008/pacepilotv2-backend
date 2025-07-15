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
