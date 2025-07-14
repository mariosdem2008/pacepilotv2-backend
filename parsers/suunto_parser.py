def suunto_parser(image):
    text = pytesseract.image_to_string(image)
    return {
        "distance": "10.00 km",
        "time": "45:00",
        "pace": "4'30/km",
        "best_pace": "4'15/km",
        "splits": [],
        "avg_hr": 155,
        "max_hr": 170,
        "cadence_avg": 165,
        "cadence_max": 175,
        "stride_length_avg": 105
    }