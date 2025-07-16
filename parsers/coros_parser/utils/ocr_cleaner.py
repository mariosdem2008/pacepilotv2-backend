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

    # Normalize common OCR misreads
    joined_text = joined_text.replace("o", "0").replace("l", "1").replace("|", "1").replace("/", ".")

    # Fix 'e' or '/' between digits → '.'
    joined_text = re.sub(r"(?<=\d)[e/](?=\d)", ".", joined_text)

    # Remove km/h to avoid false matches
    joined_text = re.sub(r"\b\d{1,3}[.,]?\d{0,2}?\s*km/h\b", "", joined_text)

    # Now find all km distances in flexible formats:
    pattern = r"((?:\d+[., ]?)+)\s*km"

    matches = re.findall(pattern, joined_text)
    for match in matches:
        num_str = match.replace(" ", "").replace(",", ".")
        num_str = re.sub(r"[^\d.]", "", num_str)

        try:
            dist = float(num_str)
            if 0.5 < dist < 100:
                return f"{dist:.2f} km"
        except:
            continue

    return None


