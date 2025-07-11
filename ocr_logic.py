from .parsers import coros_parser, garmin_parser

def extract_workout_data(image, source: str):
    if source == 'coros':
        return coros_parser(image)
    elif source == 'garmin':
        return garmin_parser(image)
    else:
        raise ValueError(f"Unsupported source: {source}")
