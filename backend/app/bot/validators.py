from typing import Optional, Tuple

PERSIAN_ARABIC_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

def normalize_digits(text: str) -> str:
    if not text:
        return ""
    return text.translate(PERSIAN_ARABIC_DIGITS).strip()

def validate_and_normalize_barcode(barcode_text: str) -> Tuple[bool, str]:
    """پذیرش هر نوع بارکد دلخواه (حداقل ۱ کاراکتر)"""
    clean_code = normalize_digits(barcode_text).strip()
    if len(clean_code) >= 1:
        return True, clean_code
    return False, ""

def parse_price(text: str) -> Optional[float]:
    clean_text = normalize_digits(text).replace(",", "").replace("_", "")
    try:
        val = float(clean_text)
        return val if val >= 0 else None
    except ValueError:
        return None

def parse_int_positive(text: str) -> Optional[int]:
    clean_text = normalize_digits(text)
    if clean_text.isdigit():
        val = int(clean_text)
        return val if val > 0 else None
    return None