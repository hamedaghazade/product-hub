class ProductHubException(Exception):
    """پایه خطاهای اختصاصی سیستم"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class BarcodeAlreadyExistsError(ProductHubException):
    def __init__(self, barcode: str):
        super().__init__(f"محصولی با بارکد '{barcode}' قبلاً ثبت شده است.")
        self.barcode = barcode


class ProductNotFoundError(ProductHubException):
    def __init__(self, product_id: int):
        super().__init__(f"محصولی با شناسه {product_id} یافت نشد.")
        self.product_id = product_id