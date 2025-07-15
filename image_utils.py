from PIL import Image, ImageEnhance, ImageFilter

def crop_roi(image: Image.Image, roi_coords: tuple) -> Image.Image:
    """
    Crop the region of interest from the image.

    :param image: PIL Image
    :param roi_coords: (x, y, width, height)
    :return: Cropped PIL Image
    """
    x, y, w, h = roi_coords
    return image.crop((x, y, x + w, y + h))


def preprocess_roi(image: Image.Image) -> Image.Image:
    """
    Basic preprocessing on the cropped ROI to enhance OCR accuracy.
    - Converts to grayscale
    - Sharpens
    - Enhances contrast
    - Applies slight blur for denoising

    :param image: PIL Image
    :return: Preprocessed PIL Image
    """
    image = image.convert("L")  # Convert to grayscale

    image = image.filter(ImageFilter.MedianFilter(size=3))  # Denoise
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # Boost contrast

    image = image.filter(ImageFilter.SHARPEN)  # Final sharpen

    return image
