import React, { useState } from 'react';
import { BarcodeModal } from './BarcodeModal';

export interface Product {
  id: number | string;
  title: string;
  units_per_pack: number;
  cost_price: number;
  barcode_value: string;
  consumer_price?: number | null;
}

interface ProductTableProps {
  products: Product[];
  refreshKey?: number;
}

export const ProductTable: React.FC<ProductTableProps> = ({ products = [], refreshKey = 0 }) => {
  const [selectedBarcode, setSelectedBarcode] = useState<{ url: string; title: string; code: string } | null>(null);

  const getBarcodeUrl = (code: string, title: string) => {
    return `/api/barcodes/render?barcode_value=${encodeURIComponent(code)}&title=${encodeURIComponent(title)}&v=${refreshKey}`;
  };

  return (
    <div className="w-full bg-white shadow-sm rounded-xl overflow-hidden border border-gray-200" dir="rtl">
      <div className="overflow-x-auto">
        <table className="w-full text-right border-collapse">
          <thead>
            <tr className="bg-slate-900 text-white text-xs sm:text-sm font-semibold">
              <th className="py-3.5 px-4 text-center w-16">ردیف</th>
              <th className="py-3.5 px-4">نام محصول</th>
              <th className="py-3.5 px-4 text-center">تعداد در بسته</th>
              <th className="py-3.5 px-4">قیمت</th>
              <th className="py-3.5 px-4 font-mono">بارکد</th>
              <th className="py-3.5 px-4 text-center">تصویر بارکد</th>
              <th className="py-3.5 px-4">قیمت مصرف‌کننده</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 text-xs sm:text-sm text-gray-700">
            {products.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-gray-400">محصولی ثبت نشده است.</td>
              </tr>
            ) : (
              products.map((item, index) => {
                const barcodeUrl = getBarcodeUrl(item.barcode_value, item.title);
                return (
                  <tr key={item.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-4 text-center font-medium text-gray-400">{index + 1}</td>
                    <td className="py-3 px-4 font-semibold text-gray-900">{item.title}</td>
                    <td className="py-3 px-4 text-center">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">
                        {item.units_per_pack || 1} عدد
                      </span>
                    </td>
                    <td className="py-3 px-4 font-medium text-gray-800">
                      {Number(item.cost_price || 0).toLocaleString('fa-IR')} ریال
                    </td>
                    <td className="py-3 px-4 font-mono text-gray-600 text-xs tracking-wider">
                      {item.barcode_value}
                    </td>
                    <td className="py-2 px-4 text-center">
                      <button
                        type="button"
                        onClick={() => setSelectedBarcode({ url: barcodeUrl, title: item.title, code: item.barcode_value })}
                        className="inline-flex items-center justify-center p-1.5 bg-white border border-gray-200 rounded-lg cursor-pointer hover:border-blue-500 hover:shadow-sm transition"
                        title="کلیک برای بزرگ‌نمایی"
                      >
                        <img src={barcodeUrl} alt={item.title} className="h-9 w-28 object-contain" />
                      </button>
                    </td>
                    <td className="py-3 px-4 font-bold text-emerald-600">
                      {item.consumer_price ? `${Number(item.consumer_price).toLocaleString('fa-IR')} ریال` : '—'}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {selectedBarcode && (
        <BarcodeModal
          isOpen={!!selectedBarcode}
          onClose={() => setSelectedBarcode(null)}
          imageUrl={selectedBarcode.url}
          title={selectedBarcode.title}
          barcodeValue={selectedBarcode.code}
        />
      )}
    </div>
  );
};