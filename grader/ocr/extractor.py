import pytesseract
import cv2
import numpy as np
import re
import os

# Windows pe Tesseract ka path set karo
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_text_tesseract(img):
    """
    Tesseract OCR se text nikalo
    Primary OCR engine - clear handwriting ke liye best
    """
    # Tesseract config: handwritten text ke liye
    config = '--oem 3 --psm 6 -l eng'

    # PIL Image chahiye Tesseract ko
    from PIL import Image
    if isinstance(img, np.ndarray):
        pil_img = Image.fromarray(img)
    else:
        pil_img = img

    text = pytesseract.image_to_string(pil_img, config=config)
    return clean_ocr_text(text)


def extract_text_easyocr(img):
    """
    EasyOCR se text nikalo
    Fallback engine - cursive/unclear handwriting ke liye
    Pehli baar thoda slow hoga (model download karta hai)
    """
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)

        if isinstance(img, np.ndarray):
            results = reader.readtext(img)
        else:
            results = reader.readtext(np.array(img))

        # Results combine karo
        text = ' '.join([result[1] for result in results if result[2] > 0.3])
        return clean_ocr_text(text)
    except Exception as e:
        return ""


def clean_ocr_text(text):
    """
    OCR ke baad text clean karo
    - Extra spaces hatao
    - Special characters fix karo
    - Common OCR errors fix karo
    """
    if not text:
        return ""

    # Extra whitespace hatao
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    # Common OCR mistakes fix karo
    replacements = {
        '|': 'I',
        '0': 'O',  # Sirf jab context mein word ho
        '1': 'l',  # l aur 1 confusion
    }

    # Basic cleaning
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)

    return text


def extract_text_from_section(section_img, question_type='short'):
    """
    Ek answer section se text nikalo
    Pehle Tesseract try karo, kam result aaye to EasyOCR
    """
    if section_img is None or section_img.size == 0:
        return ""

    # Pehle Tesseract try karo
    text = extract_text_tesseract(section_img)

    # Agar text bahut kam mila to EasyOCR try karo
    if len(text.split()) < 3 and question_type != 'mcq':
        easy_text = extract_text_easyocr(section_img)
        if len(easy_text) > len(text):
            text = easy_text

    return text


def extract_all_answers(processed_result, questions):
    """
    Poore page se saare answers extract karo
    Returns: dict {question_no: extracted_text}
    """
    binary_img = processed_result['binary']
    ocr_ready  = processed_result['ocr_ready']
    sections   = processed_result['sections']

    extracted = {}
    h, w = binary_img.shape[:2]

    for i, question in enumerate(questions):
        if i >= len(sections):
            break

        x, y, sw, sh = sections[i]

        # Section crop karo
        section = ocr_ready[y:y+sh, x:x+sw]

        if question.q_type == 'mcq':
            # MCQ ke liye bubble detect karo
            from grader.dip.pipeline import detect_mcq_answer
            answer = detect_mcq_answer(section)
            extracted[question.question_no] = answer or ""
        else:
            # Short/Long ke liye OCR
            text = extract_text_from_section(section, question.q_type)
            extracted[question.question_no] = text

    return extracted
