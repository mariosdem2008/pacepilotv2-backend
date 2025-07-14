import easyocr
import numpy as np

reader = easyocr.Reader(['en'], gpu=False)

def polar_parser(image):
    text_lines = reader.readtext(np.array(image), detail=0)
    text = "\n".join(text_lines)
    
    # You can parse `text` here if needed, currently returning fixed dummy data
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
