import React, { useState } from 'react';
import { PlusCircle, AlertCircle, Loader2, Check } from 'lucide-react';
import { ProductCreateInput } from '../types/product';
import { ProductApiService } from '../services/api';
import { useTelegram } from '../hooks/useTelegram';

interface Props {
  onProductCreated: () => void;
}

export const ProductForm: React.FC<Props> = ({ onProductCreated }) => {
  const { triggerHaptic } = useTelegram();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    cost_price: '',
    units_per_pack: '1',
    barcode_value: '',
    consumer_price: '',
  });

  const validateEAN13 = (code: string): boolean => {
    if (code.length !== 13 || !/^\d+$/.test(code)) return true;
    const digits = code.split('').map(Number);
    const sum = digits.slice(0, 12).reduce((acc, val, idx) => acc + (idx % 2 === 0 ? val : val * 3), 0);
    const checkDigit = (10 - (sum % 10)) % 10;
    return digits[12] === checkDigit;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!formData.barcode_value.trim().match(/^\d+$/)) {
      setError('کد بارکد باید صرفاً شامل ارقام عددی باشد.');
      triggerHaptic('error');
      return;
    }

    if (formData.barcode_value.length === 13 && !validateEAN13(formData.barcode_value)) {
      setError('رقم کنترل (Checksum) کد EAN-13 معتبر نیست.');
      triggerHaptic('error');
      return;
    }

    const payload: ProductCreateInput = {
      title: formData.title.trim(),
      cost_price: Number(formData.cost_price),
      units_per_pack: parseInt(formData.units_per_pack, 10),
      barcode_value: formData.barcode_value.trim(),
      consumer_price: Number(formData.consumer_price),
    };

    try {
      setLoading(true);
      await ProductApiService.createProduct(payload);
      triggerHaptic('success');
      setSuccess(true);
      setFormData({
        title: '',
        cost_price: '',
        units_per_pack: '1',
        barcode_value: '',
        consumer_price: '',
      });
      onProductCreated();
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      triggerHaptic('error');
      setError(err.message || 'خطا در برقراری ارتباط با سرور.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-100 mb-6">
      <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
        <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
          <PlusCircle className="w-5 h-5 text-sky-600" />
          ثبت کالای جدید
        </h2>
        {success && (
          <span className="text-xs bg-emerald-50 text-emerald-600 border border-emerald-200 px-2.5 py-1 rounded-full flex items-center gap-1 font-medium">
            <Check className="w-3.5 h-3.5" /> با موفقیت ثبت شد
          </span>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        <div className="md:col-span-2">
          <label className="block text-xs font-semibold text-slate-600 mb-1.5">نام کالا (فارسی / لاتین)</label>
          <input
            type="text"
            required
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="مثال: مایع ظرفشویی ۱ لیتری پریل"
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1.5">کد بارکد (EAN-13 / Code128)</label>
          <input
            type="text"
            required
            value={formData.barcode_value}
            onChange={(e) => setFormData({ ...formData, barcode_value: e.target.value })}
            placeholder="6260123456789"
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-sm font-mono text-left focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1.5">تعداد در کارتن / بسته</label>
          <input
            type="number"
            min="1"
            required
            value={formData.units_per_pack}
            onChange={(e) => setFormData({ ...formData, units_per_pack: e.target.value })}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1.5">قیمت خرید (ریال)</label>
          <input
            type="number"
            min="0"
            step="1000"
            required
            value={formData.cost_price}
            onChange={(e) => setFormData({ ...formData, cost_price: e.target.value })}
            placeholder="350000"
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1.5">قیمت مصرف‌کننده (ریال)</label>
          <input
            type="number"
            min="0"
            step="1000"
            required
            value={formData.consumer_price}
            onChange={(e) => setFormData({ ...formData, consumer_price: e.target.value })}
            placeholder="480000"
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition"
          />
        </div>

        <div className="md:col-span-3 flex justify-end mt-2">
          <button
            type="submit"
            disabled={loading}
            className="w-full md:w-auto min-w-[160px] bg-sky-600 hover:bg-sky-700 active:scale-95 text-white text-sm font-semibold py-2.5 px-6 rounded-xl transition duration-150 flex items-center justify-center gap-2 shadow-sm disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                در حال پردازش...
              </>
            ) : (
              'ثبت محصول و صدور بارکد'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};