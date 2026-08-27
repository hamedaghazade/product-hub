import React, { useState, useEffect } from 'react';

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
  onSaved: () => void;
}

export const BarcodeSettingsModal: React.FC<SettingsProps> = ({ isOpen, onClose, onSaved }) => {
  const [form, setForm] = useState({
    title_font_size: 22,
    code_font_size: 20,
    barcode_height_mm: 18.0,
    module_width_mm: 0.35,
    padding_x: 20,
    padding_y: 15,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetch('/api/barcodes/settings')
        .then((res) => res.json())
        .then((data) => setForm(data))
        .catch(() => {});
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await fetch('/api/barcodes/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      onSaved();
      onClose();
    } catch (err) {
      alert('خطا در ذخیره تنظیمات');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" dir="rtl">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 border border-gray-100">
        <div className="flex justify-between items-center border-b pb-3 mb-4">
          <h3 className="font-bold text-gray-800 text-base">تنظیمات ظاهری و چاپ بارکد</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 font-bold">✕</button>
        </div>

        <form onSubmit={handleSave} className="space-y-4 text-sm">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 mb-1 font-medium">سایز فونت نام کالا (px)</label>
              <input
                type="number"
                value={form.title_font_size}
                onChange={(e) => setForm({ ...form, title_font_size: Number(e.target.value) })}
                className="w-full border rounded-lg px-3 py-2 text-left"
              />
            </div>
            <div>
              <label className="block text-gray-700 mb-1 font-medium">سایز فونت کد زیر بارکد (px)</label>
              <input
                type="number"
                value={form.code_font_size}
                onChange={(e) => setForm({ ...form, code_font_size: Number(e.target.value) })}
                className="w-full border rounded-lg px-3 py-2 text-left"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-700 mb-1 font-medium">ارتفاع بارکد (mm)</label>
              <input
                type="number"
                step="0.5"
                value={form.barcode_height_mm}
                onChange={(e) => setForm({ ...form, barcode_height_mm: Number(e.target.value) })}
                className="w-full border rounded-lg px-3 py-2 text-left"
              />
            </div>
            <div>
              <label className="block text-gray-700 mb-1 font-medium">ضخامت خطوط (Module Width)</label>
              <input
                type="number"
                step="0.05"
                value={form.module_width_mm}
                onChange={(e) => setForm({ ...form, module_width_mm: Number(e.target.value) })}
                className="w-full border rounded-lg px-3 py-2 text-left"
              />
            </div>
          </div>

          <div className="flex gap-3 pt-3">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-slate-900 hover:bg-slate-800 text-white font-medium py-2.5 rounded-xl transition"
            >
              {loading ? 'در حال ذخیره...' : 'ذخیره تنظیمات'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2.5 rounded-xl transition"
            >
              انصراف
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};