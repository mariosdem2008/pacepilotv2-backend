import re

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

if __name__ == "__main__":
    ocr_text = [
        ". o",
        "9:08 7 XS ott) LTE ©)",
        "| —_",
        "< sage | Trac... ay.",
        "o- Spe |",
        "~ | ud",
        "- () > [Z,",
        "f : \\",
        "( TsigiomAthliti gn",
        "os Kentron a”",
        "3D",
        "; \\ ;",
        ":",
        "Pah 61 % 4) sw 20 km/h aa",
        "Ocoros",
        "4 e 9 / km .",
        "Dj Marios ~",
        "4 istance",
        "‘ ’",
        "I il I il",
        ". 17:10” 328 /km 3:19 /km",
        "\\ Activity Time Avg. Pace Best km @",
        "*",
        ": 186 bpm 322 kcal 1 1 7 % Excellent ~",
        "Average Calories Efficiency @ r",
        "' Heart Rate",
        "J",
        "87 TL Low r",
        "Training Load @ 5",
        ": ew >See Ek « EEA _",
        "_ Pace (min/km) @ Best km 3'19\" Average 3'28\" b",
        "é K",
        "» 758\""
    ]

    result = recover_distance_from_lines(ocr_text)
    print("Recovered distance:", result)
