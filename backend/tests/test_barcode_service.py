import io
import pytest
from app.services.barcode_service import BarcodeService

def test_ean13_barcode_generation():
    title = "شیر کم چرب کاله"
    valid_ean13 = "6261234567890"
    
    img_stream = BarcodeService.generate_barcode_image(title=title, barcode_value=valid_ean13)
    
    assert isinstance(img_stream, io.BytesIO)
    assert img_stream.getbuffer().nbytes > 0
    
    img_stream.seek(0)
    header = img_stream.read(8)
    assert header == b'\x89PNG\r\n\x1a\n'

def test_code128_barcode_generation():
    title = "کالای آزمایشی"
    code128_val = "PROD-987654"
    
    img_stream = BarcodeService.generate_barcode_image(title=title, barcode_value=code128_val)
    
    assert isinstance(img_stream, io.BytesIO)
    assert img_stream.getbuffer().nbytes > 0
    
    img_stream.seek(0)
    header = img_stream.read(8)
    assert header == b'\x89PNG\r\n\x1a\n'