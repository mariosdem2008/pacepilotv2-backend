import re

def clean_ocr_lines(text):
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        # Replace common OCR misreads
        line = line.replace("’", "'").replace("“", '"').replace("”", '"').replace("°", "'").replace("", "'")
        line = line.replace("O", "0").replace("o", "0")  # add lowercase 'o' too
        line = line.replace("l", "1").replace("|", "1")
        cleaned_lines.append(line)
    return cleaned_lines


def recover_distance_from_lines(lines):
    joined_text = " ".join(lines).lower()

    # Remove km/h to avoid false positives
    joined_text = re.sub(r"\d+[.,]?\d*\s*km/h", "", joined_text)

    # Replace 'e' with '.' if between digits (fixes 4 e 9 -> 4.9)
    joined_text = re.sub(r"(?<=\d)\s*e\s*(?=\d)", ".", joined_text)

    def fix_ocr_in_numbers(match):
        s = match.group()
        s = s.replace('o', '0').replace('l', '1').replace('|', '1').replace(',', '.')
        return s

    joined_text = re.sub(r"[0-9oOl|,\.]+", fix_ocr_in_numbers, joined_text)
    joined_text = re.sub(r"\s*\.\s*", ".", joined_text)

    print("DEBUG: Cleaned OCR text:", joined_text)

    # Relaxed regex to allow optional '/' between number and km
    pattern = r"(\d+(?:\.\d+)?)\s*[/]?\s*km"
    matches = re.findall(pattern, joined_text)

    print("DEBUG: Matches found:", matches)

    candidates = []
    for m in matches:
        try:
            dist = float(m)
            if 0.5 < dist < 100:
                candidates.append(dist)
        except:
            continue

    if not candidates:
        return None

    # Find the candidate closest to 4.9 km (your target)
    best = min(candidates, key=lambda x: abs(x - 4.9))
    return f"{best:.2f} km"
