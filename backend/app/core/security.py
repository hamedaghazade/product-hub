import hmac
import hashlib
from urllib.parse import parse_qsl, unquote

def validate_telegram_init_data(init_data: str, bot_token: str) -> bool:
    """
    Validates data received from Telegram Mini App via HMAC-SHA256.
    """
    if not init_data or not bot_token:
        return False
        
    try:
        parsed_data = dict(parse_qsl(init_data, keep_blank_values=True))
        if "hash" not in parsed_data:
            return False
            
        received_hash = parsed_data.pop("hash")
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))
        
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(calculated_hash, received_hash)
    except Exception:
        return False\n