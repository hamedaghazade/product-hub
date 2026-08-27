import React, { useState } from 'react';
import { X, Check, Barcode, AlertCircle } from 'lucide-react';
import { ProductAPI } from '../services/api';
import { useTelegramContext } from '../providers/TelegramProvider';
import { ProductCreatePayload } from '../types';

interface ProductFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ProductFormModal: React.FC<ProductFormModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const { hapticNotification, hapticImpact } = useTelegramContext();
  
  const [formData, setFormData] = useState<ProductCreatePayload>({
    title: '',
    cost_price: 0,
    units_per_pack: 1,
    barcode_value: '',
    consumer_price: 0,
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setLoading(true);

    try {
      if (!formData.title.trim()) {
        throw new Error('نام کالا الزامی است.');
      }
      if (formData.cost_price < 0 || formData.consumer_price < 0) {
        throw new Error('قیمت‌ها نمی‌توانند مقادیر منفی باشند.');
      }
      if (formData.barcode_value.trim().length < 6) {
        throw new Error('عدد بارکد باید حداقل ۶ رقم باشد.');
      }

      await ProductAPI.create(formData);
      hapticNotification('success');
      onSuccess();
    } catch (err: any) {
      hapticNotification('error');
      const detail = err.response?.data?.detail || err.message || 'خطا در ثبت اطلاعات کالا';
      setErrorMessage(detail);
    } finally {
      setLoading(false);
    }
  };

  const calculateMargin = (): number => {
    if (formData.cost_price <= 0) return 0;
    return Number((((formData.consumer_price - formData.cost_price) / formData.cost_price) * 100).toFixed(1));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/70 backdrop-blur-sm p-0 sm:p-4" dir="rtl">
      <div className="bg-slate-900 border border-slate-800 w-full max-w-lg rounded-t-3xl sm:rounded-2xl shadow-2xl overflow-hidden max-h-[92vh] flex flex-col">
        
        {/* هدر */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Barcode className="w-5 h-5 text-blue-500" />
            ثبت مشخصات محصول جدید
          </h3>
          <button
            onClick={() => {
              hapticImpact('light');
              onClose();
            }}
            className="text-slate-400 hover:text-white transition p-1"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* بدنه فرم */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto">
          {errorMessage && (
            <div className="flex items-center gap-2 p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">نام محصول (فارسی / لاتین)</label>
            <input
              type="text"
              required
              placeholder="مثال: روغن آفتابگردان ۱.۵ لیتری"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">قیمت خرید (تومان)</label>
              <input
                type="number"
                required
                min="0"
                step="500"
                value={formData.cost_price || ''}
                onChange={(e) => setFormData({ ...formData, cost_price: Number(e.target.value) })}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">قیمت مصرف‌کننده (تومان)</label>
              <input
                type="number"
                required
                min="0"
                step="500"
                value={formData.consumer_price || ''}
                onChange={(e) => setFormData({ ...formData, consumer_price: Number(e.target.value) })}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">تعداد در هر بسته</label>
              <input
                type="number"
                required
                min="1"
                value={formData.units_per_pack}
                onChange={(e) => setFormData({ ...formData, units_per_pack: Math.max(1, Number(e.target.value)) })}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">عدد بارکد کالا</label>
              <input
                type="text"
                required
                placeholder="626..."
                value={formData.barcode_value}
                onChange={(e) => setFormData({ ...formData, barcode_value: e.target.value })}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500 font-mono tracking-wider"
              />
            </div>
          </div>

          {/* پیش‌نمایش آنی حاشیه سود */}
          <div className="p-3 bg-slate-800/50 border border-slate-700/50 rounded-xl flex items-center justify-between text-xs">
            <span className="text-slate-400">حاشیه سود ناخالص برآورد شده:</span>
            <span className={`font-bold font-mono text-sm ${calculateMargin() >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              ٪{calculateMargin()}
            </span>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-4 rounded-xl transition disabled:bg-slate-700 shadow-lg shadow-blue-600/20"
            >
              <Check className="w-4 h-4" />
              {loading ? 'در حال ثبت اطلاعات...' : 'ثبت نهایی محصول'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};