import React, { useEffect } from 'react';

export interface BarcodeModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  title: string;
  barcodeValue: string;
}

export const BarcodeModal: React.FC<BarcodeModalProps> = ({
  isOpen,
  onClose,
  imageUrl,
  title,
  barcodeValue,
}) => {
  // بستن مودال با کلید Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
    >
      <div
        className="bg-white rounded-2xl shadow-2xl p-6 max-w-md w-full flex flex-col items-center gap-4 transition-all transform scale-100"
        onClick={(e) => e.stopPropagation()}
        dir="rtl"
      >
        <div className="w-full flex justify-between items-center border-b border-gray-100 pb-3">
          <h3 className="font-bold text-gray-800 text-base">پیش‌نمایش بارکد کالا</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"
            aria-label="بستن"
          >
            ✕
          </button>
        </div>

        <div className="p-4 bg-gray-50 border border-gray-200 rounded-xl flex items-center justify-center w-full min-h-[160px]">
          <img
            src={imageUrl}
            alt={title}
            className="max-h-56 max-w-full object-contain"
            loading="lazy"
          />
        </div>

        <div className="text-center w-full">
          <p className="text-base font-bold text-gray-800 truncate">{title}</p>
          <p className="font-mono text-sm tracking-widest text-gray-500 mt-1">
            {barcodeValue}
          </p>
        </div>

        <div className="flex gap-3 w-full mt-2">
          <a
            href={imageUrl}
            download={`barcode-${barcodeValue}.png`}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-xl text-center text-sm transition-colors shadow-sm"
          >
            دانلود تصویر
          </a>
          <button
            type="button"
            onClick={onClose}
            className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2.5 rounded-xl text-sm transition-colors"
          >
            بستن
          </button>
        </div>
      </div>
    </div>
  );
};