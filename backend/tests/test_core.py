import hmac
import hashlib
from app.services.barcode_service import BarcodeEngine
from app.core.security import verify_telegram_init_data

def test_ean13_checksum_validation():
    assert BarcodeEngine.validate_ean13("6260123456784") is False
    # محاسبه مقدار صحیح Checksum برای 626012345678
    # 6*1 + 2*3 + 6*1 + 0*3 + 1*1 + 2*3 + 3*1 + 4*3 + 5*1 + 6*3 + 7*1 + 8*3 = 88 -> Check digit = 2
    assert BarcodeEngine.validate_ean13("6260123456782") is True

def test_barcode_image_stream_generation():
    img_buffer = BarcodeEngine.generate_barcode_image("کالای تستی", "6260123456782")
    assert img_buffer is not None
    assert len(img_buffer.getvalue()) > 0
    assert img_buffer.getvalue().startswith(b'\x89PNG')

def test_telegram_init_data_verification():
    bot_token = "123456789:AAFakeTokenForCiPipelineValidationXyZ"
    auth_date = "1700000000"
    data_check_string = f"auth_date={auth_date}\nquery_id=AAHdF6IQAAAAAN0XohD3test"
    
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    valid_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    init_data = f"auth_date={auth_date}&query_id=AAHdF6IQAAAAAN0XohD3test&hash={valid_hash}"
    assert verify_telegram_init_data(init_data, bot_token) is True