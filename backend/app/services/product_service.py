from typing import List, Dict, Any

# حافظه موقت برای ذخیره کالاها تا زمان اتصال کامل ORM/Database
_IN_MEMORY_PRODUCTS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "روغن مایع ۱.۵ لیتری",
        "cost_price": 120000,
        "units_per_pack": 12,
        "barcode_value": "6260000000019",
        "consumer_price": 145000
    },
    {
        "id": 2,
        "title": "رب گوجه فرنگی ۸۰۰ گرمی",
        "cost_price": 45000,
        "units_per_pack": 24,
        "barcode_value": "6261234567890",
        "consumer_price": 58000
    }
]

class ProductService:
    @staticmethod
    async def get_all_products() -> List[Dict[str, Any]]:
        """واکشی تمام محصولات از دیتابیس"""
        return _IN_MEMORY_PRODUCTS

    @staticmethod
    async def create_product(data: Dict[str, Any]) -> Dict[str, Any]:
        """ثبت محصول جدید در دیتابیس"""
        new_id = len(_IN_MEMORY_PRODUCTS) + 1
        new_product = {
            "id": new_id,
            "title": data.get("title", ""),
            "cost_price": float(data.get("cost_price", 0)),
            "units_per_pack": int(data.get("units_per_pack", 1)),
            "barcode_value": str(data.get("barcode_value", "")),
            "consumer_price": float(data.get("consumer_price", 0))
        }
        _IN_MEMORY_PRODUCTS.append(new_product)
        return new_product