import cv2
import numpy as np
import os


def preprocess_image(image_path):
    """
    Step 1: Raw image ko clean karo
    - Grayscale convert
    - Denoise (Gaussian blur)
    - Resize to standard size
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image load nahi hui: {image_path}")

    # Standard size pe resize hoga
    img = cv2.resize(img, (1200, 1600))

    # Grayscale convert
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Gaussian blur se noise hatega
    denoised = cv2.GaussianBlur(gray, (5, 5), 0)

    return img, denoised


def correct_skew(gray_img):
    """
    Step 2: Tilted pages seedhi karo
    - Skew angle detect karo
    - Rotate karke fix karo
    """
    # Threshold apply karo skew detection ke liye
    _, binary = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Non-zero pixels dhundho
    coords = np.column_stack(np.where(binary > 0))
    if len(coords) == 0:
        return gray_img

    # Skew angle calculate karo
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Sirf zyada tilt wali images fix karo (1 degree se zyada)
    if abs(angle) > 1.0:
        (h, w) = gray_img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        corrected = cv2.warpAffine(gray_img, M, (w, h),
                                   flags=cv2.INTER_CUBIC,
                                   borderMode=cv2.BORDER_REPLICATE)
        return corrected

    return gray_img


def apply_threshold(gray_img):
    """
    Step 3: Otsu thresholding - text ko background se alag karo
    Black text on white background banana
    """
    _, binary = cv2.threshold(
        gray_img, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Morphological operations se small noise hatega
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    return cleaned


def detect_answer_sections(binary_img, original_img):
    """
    Step 4: Answer sections ko detect karo
    - Horizontal lines dhundho (sections ke dividers)
    - Ya bade text blocks detect karo
    Returns: list of (x, y, w, h) for each section
    """
    h, w = binary_img.shape[:2]

    # Horizontal line detection - answer sections ke borders
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (w // 3, 1))
    detect_horizontal = cv2.morphologyEx(
        cv2.bitwise_not(binary_img), cv2.MORPH_OPEN,
        horizontal_kernel, iterations=2
    )

    # Horizontal lines ki positions nikalo
    contours, _ = cv2.findContours(
        detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # Y-coordinates of lines sort karo
    line_ys = sorted([cv2.boundingRect(c)[1] for c in contours if cv2.boundingRect(c)[2] > w // 4])

    # Sections banao lines ke beech mein
    sections = []
    if len(line_ys) >= 2:
        for i in range(len(line_ys) - 1):
            y1 = line_ys[i] + 5
            y2 = line_ys[i + 1] - 5
            if y2 - y1 > 50:  # Minimum section height
                sections.append((0, y1, w, y2 - y1))
    else:
        # Fallback: page ko equal parts mein divide karo
        section_h = h // 5
        for i in range(5):
            sections.append((0, i * section_h, w, section_h))

    return sections


def detect_mcq_answer(section_img):
    """
    MCQ ke liye: Filled circle/bubble detect karo
    Returns: detected option letter (A/B/C/D) or None
    """
    gray = section_img if len(section_img.shape) == 2 else cv2.cvtColor(section_img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Circles detect karo (bubbles/checkboxes)
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT,
        dp=1, minDist=20,
        param1=50, param2=30,
        minRadius=8, maxRadius=25
    )

    if circles is None:
        return None

    circles = np.round(circles[0, :]).astype("int")
    h, w = gray.shape

    # Sabse zyada filled circle dhundho
    max_fill = 0
    best_x = None

    for (x, y, r) in circles:
        # Circle ke andar ka area check karo
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.circle(mask, (x, y), r, 255, -1)
        filled_pixels = cv2.countNonZero(cv2.bitwise_and(binary, binary, mask=mask))
        circle_area = np.pi * r * r

        fill_ratio = filled_pixels / circle_area
        if fill_ratio > max_fill and fill_ratio > 0.4:
            max_fill = fill_ratio
            best_x = x

    if best_x is None:
        return None

    # X position ke hisaab se option determine karo
    section_w = w
    q_width = section_w / 4
    option_idx = int(best_x / q_width)
    options = ['A', 'B', 'C', 'D']
    return options[min(option_idx, 3)]


def enhance_for_ocr(img):
    """
    OCR ke liye image enhance karo
    - Contrast badhaao
    - Sharpening apply karo
    """
    gray = img if len(img.shape) == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE se contrast enhance karo
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Sharpening kernel
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    # Final threshold
    _, final = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return final


def save_processed_image(img, output_path):
    """Processed image save karo"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img)


def run_dip_pipeline(image_path, output_dir=None):
    """
    Complete DIP pipeline ek saath run karo
    Returns: processed image aur sections list
    """
    # Step 1: Preprocess
    original, gray = preprocess_image(image_path)

    # Step 2: Skew correct
    corrected = correct_skew(gray)

    # Step 3: Threshold
    binary = apply_threshold(corrected)

    # Step 4: Sections detect karo
    sections = detect_answer_sections(binary, original)

    # OCR ke liye enhanced image
    ocr_ready = enhance_for_ocr(corrected)

    # Processed image save karo (optional)
    if output_dir:
        base = os.path.splitext(os.path.basename(image_path))[0]
        save_processed_image(binary, os.path.join(output_dir, f"{base}_processed.jpg"))

    return {
        'original': original,
        'gray': corrected,
        'binary': binary,
        'ocr_ready': ocr_ready,
        'sections': sections,

    }
