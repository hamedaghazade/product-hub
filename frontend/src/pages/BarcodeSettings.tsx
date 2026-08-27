import React, { useState } from 'react';

export const BarcodeSettings: React.FC = () => {
  const [config, setConfig] = useState({
    title_font_size: 28,
    code_font_size: 24,
    barcode_height_mm: 20.0,
    module_width_mm: 0.4,
    padding_x: 30,
    padding_y: 20,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setConfig({ ...config, [e.target.name]: parseFloat(e.target.value) });
  };

  const handleSave = async () => {
    await fetch('/api/barcodes/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
  };

  return (
    <div className="max-w-xl mx-auto p-6 bg-white rounded-2xl shadow-sm border border-gray-100" dir="rtl">
      <h2 className="text-xl font-bold text-gray-800 mb-6">تنظیمات ظاهری و چاپ بارکد</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">اندازه فونت عنوان بالا (px)</label>
          <input type="number" name="title_font_size" value={config.title_font_size} onChange={handleChange} className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">اندازه فونت کد پایین (px)</label>
          <input type="number" name="code_font_size" value={config.code_font_size} onChange={handleChange} className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">ارتفاع خطوط بارکد (mm)</label>
          <input type="number" step="0.5" name="barcode_height_mm" value={config.barcode_height_mm} onChange={handleChange} className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">ضخامت میله‌ها (Module Width mm)</label>
          <input type="number" step="0.05" name="module_width_mm" value={config.module_width_mm} onChange={handleChange} className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500" />
        </div>
        <button onClick={handleSave} className="w-full mt-4 bg-slate-900 text-white font-medium py-2.5 rounded-xl hover:bg-slate-800 transition">
          ذخیره تنظیمات
        </button>
      </div>
    </div>
  );
};