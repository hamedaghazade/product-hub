import hashlib
import hmac
import time
from urllib.parse import parse_qsl, unquote
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security_scheme = HTTPBearer()

def validate_telegram_init_data(init_data: str, bot_token: str, max_age_seconds: int = 86400) -> dict:
    """
    اعتبارسنجی امضای رمزنگاری‌شده داده‌های مینی‌اپ تلگرام
    """
    try:
        parsed_data = dict(parse_qsl(init_data, keep_blank_values=True))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="فرمت initData تلگرام نامعتبر است."
        )

    received_hash = parsed_data.pop("hash", None)
    if not received_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="امضای امنیتی تلگرام یافت نشد."
        )

    # بررسی انقضای زمانی (جلوگیری از حملات Replay)
    auth_date = int(parsed_data.get("auth_date", 0))
    if time.time() - auth_date > max_age_seconds:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="نشست تلگرام منقضی شده است."
        )

    # مرتب‌سازی الفبایی کلیدها طبق داکیومنت رسمی تلگرام
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))

    # محاسبه کلید مخفی با HMAC-SHA256
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    
    # محاسبه هش نهایی
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="احراز هویت نامعتبر است؛ امضا با کلید بات همخوانی ندارد."
        )

    return parsed_data