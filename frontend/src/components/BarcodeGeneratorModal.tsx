import React, { useState, useEffect, useRef, useCallback } from 'react';
import JsBarcode from 'jsbarcode';
import { Download, RefreshCw, X, Sliders, Type, Palette } from 'lucide-react';

export type BarcodeFormat = 'EAN13' | 'UPC' | 'CODE128' | 'ITF14';

export interface BarcodeSettings {
  title: string;
  codeValue: string;
  format: BarcodeFormat;
  titleFontSize: number;
  codeFontSize: number;
  titleFontFamily: string;
  codeFontFamily: string;
  barcodeWidth: number;
  barcodeHeight: number;
  margin: number;
  lineColor: string;
  backgroundColor: string;
}

export const BarcodeGeneratorModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const [settings, setSettings] = useState<BarcodeSettings>({
    title: 'روغن سرخ‌کردنی شفاف ۱.۵ لیتری',
    codeValue: '6260123456789',
    format: 'EAN13',
    titleFontSize: 20,
    codeFontSize: 16,
    titleFontFamily: 'Vazirmatn, Tahoma, sans-serif',
    codeFontFamily: 'Courier New, monospace',
    barcodeWidth: 2,
    barcodeHeight: 100,
    margin: 20,
    lineColor: '#000000',
    backgroundColor: '#FFFFFF',
  });

  const [error, setError] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const drawBarcode = useCallback(() => {
    setError(null);
    try {
      // ایجاد المان موقت SVG جهت استخراج خطوط استاندارد
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      
      JsBarcode(svg, settings.codeValue, {
        format: settings.format,
        width: settings.barcodeWidth,
        height: settings.barcodeHeight,
        displayValue: false, // جلوگیری از رسم متن پیش‌فرض
        lineColor: settings.lineColor,
        background: settings.backgroundColor,
        margin: 0,
      });

      const xml = new XMLSerializer().serializeToString(svg);
      const svg64 = btoa(unescape(encodeURIComponent(xml)));
      const image64 = 'data:image/svg+xml;base64,' + svg64;

      const barcodeImg = new Image();
      barcodeImg.onload = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // اندازه‌گیری متون
        ctx.font = `bold ${settings.titleFontSize}px ${settings.titleFontFamily}`;
        const titleMetrics = ctx.measureText(settings.title);
        const titleWidth = titleMetrics.width;
        const titleHeight = settings.titleFontSize;

        ctx.font = `${settings.codeFontSize}px ${settings.codeFontFamily}`;
        const codeMetrics = ctx.measureText(settings.codeValue);
        const codeWidth = codeMetrics.width;
        const codeHeight = settings.codeFontSize;

        const contentWidth = Math.max(barcodeImg.width, titleWidth, codeWidth);
        const totalWidth = contentWidth + settings.margin * 2;
        const spacing = 12;
        const totalHeight = settings.margin * 2 + titleHeight + spacing + barcodeImg.height + spacing + codeHeight;

        canvas.width = totalWidth;
        canvas.height = totalHeight;

        // رسم پس‌زمینه
        ctx.fillStyle = settings.backgroundColor;
        ctx.fillRect(0, 0, totalWidth, totalHeight);

        // ۱. رسم نام محصول (بالا - راست‌چین/وسط‌چین استاندارد)
        ctx.fillStyle = settings.lineColor;
        ctx.font = `bold ${settings.titleFontSize}px ${settings.titleFontFamily}`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillText(settings.title, totalWidth / 2, settings.margin);

        // ۲. رسم خطوط بارکد (مرکز)
        const barcodeX = (totalWidth - barcodeImg.width) / 2;
        const barcodeY = settings.margin + titleHeight + spacing;
        ctx.drawImage(barcodeImg, barcodeX, barcodeY);

        // ۳. رسم عدد بارکد (پایین)
        ctx.font = `${settings.codeFontSize}px ${settings.codeFontFamily}`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        const codeY = barcodeY + barcodeImg.height + spacing;
        ctx.fillText(settings.codeValue, totalWidth / 2, codeY);
      };

      barcodeImg.onerror = () => {
        setError('خطا در تبدیل گرافیکی استاندارد بارکد.');
      };

      barcodeImg.src = image64;
    } catch (err: any) {
      setError(err?.message || 'قالب داده برای این نوع بارکد سازگار نیست.');
    }
  }, [settings]);

  useEffect(() => {
    if (isOpen) {
      drawBarcode();
    }
  }, [settings, isOpen, drawBarcode]);

  const handleDownload = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const link = document.createElement('a');
    link.download = `barcode-${settings.codeValue}.png`;
    link.href = canvas.toDataURL('image/png', 1.0);
    link.click();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 font-sans" dir="rtl">
      <div className="bg-white dark:bg-slate-900 rounded-2xl w-full max-w-4xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden border border-slate-200 dark:border-slate-800">
        
        {/* هدر مودال */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <h2 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <Sliders className="w-5 h-5 text-blue-600" />
            تنظیمات و پیش‌نمایش پیشرفته بارکد کالا
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* بدنه دو ستونه: تنظیمات + پیش‌نمایش */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 p-6 overflow-y-auto">
          
          {/* ستون راست: پنل تنظیمات */}
          <div className="md:col-span-6 space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">نام کالا (نمایش بالا)</label>
              <input
                type="text"
                value={settings.title}
                onChange={(e) => setSettings({ ...settings, title: e.target.value })}
                className="w-full px-3 py-2 text-sm border rounded-lg dark:bg-slate-800 dark:border-slate-700 dark:text-white"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">کد عددی</label>
                <input
                  type="text"
                  value={settings.codeValue}
                  onChange={(e) => setSettings({ ...settings, codeValue: e.target.value })}
                  className="w-full px-3 py-2 text-sm border rounded-lg dark:bg-slate-800 dark:border-slate-700 dark:text-white font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">نوع بارکد</label>
                <select
                  value={settings.format}
                  onChange={(e) => setSettings({ ...settings, format: e.target.value as BarcodeFormat })}
                  className="w-full px-3 py-2 text-sm border rounded-lg dark:bg-slate-800 dark:border-slate-700 dark:text-white"
                >
                  <option value="EAN13">EAN-13</option>
                  <option value="UPC">UPC-A</option>
                  <option value="CODE128">Code 128</option>
                  <option value="ITF14">ITF-14</option>
                </select>
              </div>
            </div>

            {/* تنظیمات فونت */}
            <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl space-y-3">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-200 flex items-center gap-1">
                <Type className="w-4 h-4" /> تنظیمات تایپوگرافی
              </span>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] text-slate-500 mb-1">اندازه فونت عنوان</label>
                  <input
                    type="number"
                    value={settings.titleFontSize}
                    onChange={(e) => setSettings({ ...settings, titleFontSize: Number(e.target.value) })}
                    className="w-full px-2 py-1 text-sm border rounded dark:bg-slate-800 dark:border-slate-700"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-500 mb-1">اندازه فونت کد</label>
                  <input
                    type="number"
                    value={settings.codeFontSize}
                    onChange={(e) => setSettings({ ...settings, codeFontSize: Number(e.target.value) })}
                    className="w-full px-2 py-1 text-sm border rounded dark:bg-slate-800 dark:border-slate-700"
                  />
                </div>
              </div>
            </div>

            {/* تنظیمات ابعاد و رنگ */}
            <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl space-y-3">
              <span className="text-xs font-bold text-slate-700 dark:text-slate-200 flex items-center gap-1">
                <Palette className="w-4 h-4" /> ابعاد و رنگ‌بندی
              </span>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-[11px] text-slate-500 mb-1">ارتفاع میله</label>
                  <input
                    type="number"
                    value={settings.barcodeHeight}
                    onChange={(e) => setSettings({ ...settings, barcodeHeight: Number(e.target.value) })}
                    className="w-full px-2 py-1 text-sm border rounded dark:bg-slate-800"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-500 mb-1">حاشیه (Margin)</label>
                  <input
                    type="number"
                    value={settings.margin}
                    onChange={(e) => setSettings({ ...settings, margin: Number(e.target.value) })}
                    className="w-full px-2 py-1 text-sm border rounded dark:bg-slate-800"
                  />
                </div>
                <div>
                  <label className="block text-[11px] text-slate-500 mb-1">رنگ بارکد</label>
                  <input
                    type="color"
                    value={settings.lineColor}
                    onChange={(e) => setSettings({ ...settings, lineColor: e.target.value })}
                    className="w-full h-8 p-0 border rounded cursor-pointer"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* ستون چپ: پیش‌نمایش زنده */}
          <div className="md:col-span-6 flex flex-col items-center justify-center bg-slate-100 dark:bg-slate-950 p-4 rounded-xl border border-dashed border-slate-300 dark:border-slate-800 relative min-h-[300px]">
            {error ? (
              <div className="text-red-500 text-xs bg-red-50 dark:bg-red-950/50 p-3 rounded-lg border border-red-200 dark:border-red-900 text-center">
                {error}
              </div>
            ) : (
              <div className="max-w-full overflow-auto p-2 bg-white rounded-lg shadow-sm">
                <canvas ref={canvasRef} className="max-w-full h-auto block mx-auto" />
              </div>
            )}
          </div>
        </div>

        {/* فوتر مودال */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 dark:text-slate-300"
          >
            بستن
          </button>
          <button
            onClick={handleDownload}
            disabled={!!error}
            className="flex items-center gap-2 px-5 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 rounded-lg shadow-sm transition"
          >
            <Download className="w-4 h-4" />
            دانلود تصویر
          </button>
        </div>
      </div>
    </div>
  );
};