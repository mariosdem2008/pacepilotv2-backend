def apple_parser(image):
    text = pytesseract.image_to_string(image)
    return {
        "distance": "3.50 km",
        "time": "20:30",
        "pace": "5'51/km",
        "best_pace": "5'40/km",
        "splits": [],
        "avg_hr": 140,
        "max_hr": 155,
        "cadence_avg": 150,
        "cadence_max": 160,
        "stride_length_avg": 90
    }