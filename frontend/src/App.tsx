import React, { useState, useEffect } from 'react';
import { Plus, FileSpreadsheet, FileText, Search, RefreshCw, Barcode as BarcodeIcon } from 'lucide-react';
import { useTelegram } from './hooks/useTelegram';
import { ProductAPI } from './services/api';
import { Product, SummaryStats } from './types';
import { ProductFormModal } from './components/ProductForm';
import { ProductTable } from './components/ProductTable';
import { BarcodeGeneratorModal } from './components/BarcodePreviewModal';

export default function App() {
  const { user, isTelegram } = useTelegram();
  const [products, setProducts] = useState<Product[]>([]);
  const [summary, setSummary] = useState<SummaryStats | null>(null);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedBarcodeProduct, setSelectedBarcodeProduct] = useState<Product | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [prodsData, summaryData] = await Promise.all([
        ProductAPI.getAll(search),
        ProductAPI.getSummary(),
      ]);
      setProducts(prodsData);
      setSummary(summaryData);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [search]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-4 md:p-8" dir="rtl">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* هدر بالایی */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
          <div>
            <h1 className="text-2xl font-black text-white flex items-center gap-3">
              <BarcodeIcon className="w-8 h-8 text-blue-500" />
              سامانه یکپارچه مدیریت کالا و بارکد
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              {isTelegram && user ? `کاربر تلگرام: ${user.first_name} (@${user.username || 'بی‌نام'})` : 'پنل مدیریت تحت وب'}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <a
              href={ProductAPI.getExcelDownloadUrl()}
              download
              className="flex items-center gap-2 bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 px-4 py-2.5 rounded-xl hover:bg-emerald-600/30 transition text-sm font-semibold"
            >
              <FileSpreadsheet className="w-4 h-4" />
              خروجی Excel
            </a>
            <a
              href={ProductAPI.getPdfDownloadUrl()}
              download
              className="flex items-center gap-2 bg-rose-600/20 text-rose-400 border border-rose-500/30 px-4 py-2.5 rounded-xl hover:bg-rose-600/30 transition text-sm font-semibold"
            >
              <FileText className="w-4 h-4" />
              کاتالوگ PDF
            </a>
            <button
              onClick={() => setIsCreateOpen(true)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl transition text-sm font-bold shadow-lg shadow-blue-600/20"
            >
              <Plus className="w-4 h-4" />
              ثبت محصول جدید
            </button>
          </div>
        </header>

        {/* کارت‌های آمار کلیدی */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-xl">
              <span className="text-xs text-slate-400">تعداد کل اقلام ثبت‌شده</span>
              <p className="text-2xl font-black text-white mt-1">{summary.total_products} کالا</p>
            </div>
            <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-xl">
              <span className="text-xs text-slate-400">ارزش کل موجودی بر پایه خرید</span>
              <p className="text-2xl font-black text-emerald-400 mt-1">{summary.total_inventory_value.toLocaleString('fa-IR')} تومان</p>
            </div>
            <div className="bg-slate-900/60 border border-slate-800/80 p-5 rounded-xl">
              <span className="text-xs text-slate-400">میانگین حاشیه سود ناخالص</span>
              <p className="text-2xl font-black text-blue-400 mt-1">٪{summary.avg_profit_margin}</p>
            </div>
          </div>
        )}

        {/* فیلتر جستجو و جدول */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800 flex items-center gap-3">
            <Search className="w-5 h-5 text-slate-500" />
            <input
              type="text"
              placeholder="جستجو بر اساس نام کالا یا عدد بارکد..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-transparent border-none text-sm text-white placeholder-slate-500 focus:outline-none w-full"
            />
            {loading && <RefreshCw className="w-4 h-4 text-slate-500 animate-spin" />}
          </div>

          <ProductTable
            products={products}
            onSelectBarcode={(prod) => setSelectedBarcodeProduct(prod)}
            onDeleteSuccess={fetchData}
          />
        </div>
      </div>

      {/* مودال‌های عملیاتی */}
      {isCreateOpen && (
        <ProductFormModal
          isOpen={isCreateOpen}
          onClose={() => setIsCreateOpen(false)}
          onSuccess={() => {
            setIsCreateOpen(false);
            fetchData();
          }}
        />
      )}

      {selectedBarcodeProduct && (
        <BarcodeGeneratorModal
          isOpen={!!selectedBarcodeProduct}
          product={selectedBarcodeProduct}
          onClose={() => setSelectedBarcodeProduct(null)}
        />
      )}
    </div>
  );
}