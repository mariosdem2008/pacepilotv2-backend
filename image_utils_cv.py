import cv2
import numpy as np

def crop_roi(image: np.ndarray, roi_coords: tuple) -> np.ndarray:
    """
    Crop the region of interest from an OpenCV image.

    :param image: OpenCV image (NumPy array)
    :param roi_coords: (x, y, width, height)
    :return: Cropped OpenCV image
    """
    x, y, w, h = roi_coords
    return image[y:y + h, x:x + w]


def preprocess_roi(image: np.ndarray) -> np.ndarray:
    """
    Preprocess cropped ROI for OCR:
    - Grayscale
    - Median blur
    - Contrast adjustment
    - Sharpening

    :param image: OpenCV image (NumPy array)
    :return: Preprocessed OpenCV image
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Denoise with median filter
    blurred = cv2.medianBlur(gray, 3)

    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(blurred)

    # Sharpening kernel
    kernel = np.array([[0, -1, 0],
                       [-1, 5,-1],
                       [0, -1, 0]])
    sharpened = cv2.filter2D(contrast, -1, kernel)

    return sharpened
