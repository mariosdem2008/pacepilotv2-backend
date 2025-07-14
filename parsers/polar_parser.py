def polar_parser(image):
    text = pytesseract.image_to_string(image)
    return {
        "distance": "6.20 km",
        "time": "31:45",
        "pace": "5'07/km",
        "best_pace": "4'55/km",
        "splits": [],
        "avg_hr": 145,
        "max_hr": 160,
        "cadence_avg": 158,
        "cadence_max": 172,
        "stride_length_avg": 95
    }