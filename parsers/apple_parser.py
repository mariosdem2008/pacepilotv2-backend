import easyocr
import numpy as np

reader = easyocr.Reader(['en'], gpu=False)

def apple_parser(image):
    text_lines = reader.readtext(np.array(image), detail=0)
    text = "\n".join(text_lines)
    
    # You can process `text` here if needed, for now returning static dummy data as before
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
