import hmac
import hashlib
import json
from urllib.parse import parse_qsl, unquote
from typing import Dict, Any
from fastapi import HTTPException, Header, status, Depends
from app.core.config import settings

def verify_telegram_init_data(
    x_telegram_init_data: str = Header(None, alias="X-Telegram-Init-Data")
) -> Dict[str, Any]:
    """
    اعتبارسنجی امنیتی هش رمزنگاری‌شده initData تلگرام با الگوریتم HMAC-SHA256
    """
    if not x_telegram_init_data:
        # در صورت نبود هدر تلگرام، برای دسترسی وب مستقیم مسدود نمی‌شود
        return {"auth_type": "web_guest", "user": None}

    try:
        parsed_data = dict(parse_qsl(x_telegram_init_data, keep_blank_values=True))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="ساختار هدر اطلاعات تلگرام نامعتبر است."
        )

    if "hash" not in parsed_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="امضای امنیتی تلگرام یافت نشد."
        )

    received_hash = parsed_data.pop("hash")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))

    # محاسبه Secret Key از توکن بات
    secret_key = hmac.new(b"WebAppData", settings.BOT_TOKEN.encode("utf-8"), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="اعتبارسنجی کاربر تلگرام ناموفق بود (Signature Mismatch)."
        )

    user_data = None
    if "user" in parsed_data:
        user_data = json.loads(unquote(parsed_data["user"]))

    return {"auth_type": "telegram_miniapp", "user": user_data, "raw_data": parsed_data}