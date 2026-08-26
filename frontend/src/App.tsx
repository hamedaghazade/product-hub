import React, { useState, useEffect } from 'react';
import { PlusCircle, FileSpreadsheet, FileText, Barcode, Package } from 'lucide-react';

interface Product {
  id: number;
  title: str;
  cost_price: number;
  units_per_pack: number;
  barcode_value: string;
  consumer_price: number;
}

export default function App() {
  const [products, setProducts] = useState<Product[]>([]);
  const [form, setForm] = useState({
    title: '',
    cost_price: '',
    units_per_pack: '1',
    barcode_value: '',
    consumer_price: ''
  });

  const API_BASE = "http://localhost:8000/api/v1";

  const fetchProducts = async () => {
    try {
      const res = await fetch(`${API_BASE}/products`);
      if (res.ok) setProducts(await res.json());
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => { fetchProducts(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      title: form.title,
      cost_price: parseFloat(form.cost_price),
      units_per_pack: parseInt(form.units_per_pack),
      barcode_value: form.barcode_value,
      consumer_price: parseFloat(form.consumer_price)
    };

    const res = await fetch(`${API_BASE}/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      setForm({ title: '', cost_price: '', units_per_pack: '1', barcode_value: '', consumer_price: '' });
      fetchProducts();
    } else {
      alert("خطا در ثبت کالا. بررسی کنید بارکد تکراری نباشد.");
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-6 text-slate-800">
      <header className="flex justify-between items-center bg-white p-5 rounded-2xl shadow-sm border border-slate-100 mb-6">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Package className="w-6 h-6 text-sky-600" />
            سیستم مدیریت محصولات
          </h1>
          <p className="text-xs text-slate-500 mt-1">نسخه سازگار با Telegram Mini App و Web</p>
        </div>
        <div className="flex gap-2">
          <a href={`${API_BASE}/export/excel`} target="_blank" className="flex items-center gap-1 bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-2 rounded-xl text-xs font-semibold shadow-sm transition">
            <FileSpreadsheet className="w-4 h-4" /> اکسل
          </a>
          <a href={`${API_BASE}/export/pdf`} target="_blank" className="flex items-center gap-1 bg-rose-600 hover:bg-rose-700 text-white px-3 py-2 rounded-xl text-xs font-semibold shadow-sm transition">
            <FileText className="w-4 h-4" /> PDF
          </a>
        </div>
      </header>

      {/* Product Form */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 mb-6">
        <h2 className="text-sm font-bold text-slate-700 mb-4 flex items-center gap-2">
          <PlusCircle className="w-4 h-4 text-sky-600" /> ثبت محصول جدید
        </h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs text-slate-500 mb-1">نام کالا</label>
            <input required value={form.title} onChange={e => setForm({...form, title: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm focus:outline-sky-500" placeholder="مثال: مایع ظرفشویی ۱ لیتری" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">کد بارکد (EAN-13 / Code128)</label>
            <input required value={form.barcode_value} onChange={e => setForm({...form, barcode_value: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm focus:outline-sky-500 font-mono" placeholder="6260123456789" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">تعداد در بسته</label>
            <input type="number" required value={form.units_per_pack} onChange={e => setForm({...form, units_per_pack: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm focus:outline-sky-500" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">قیمت خرید (ریال)</label>
            <input type="number" required value={form.cost_price} onChange={e => setForm({...form, cost_price: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm focus:outline-sky-500" />
          </div>
          <div>
            <label className="block text-xs text-slate-500 mb-1">قیمت مصرف‌کننده (ریال)</label>
            <input type="number" required value={form.consumer_price} onChange={e => setForm({...form, consumer_price: e.target.value})} className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-sm focus:outline-sky-500" />
          </div>
          <div className="flex items-end">
            <button type="submit" className="w-full bg-sky-600 hover:bg-sky-700 text-white font-medium p-2 rounded-lg text-sm transition">ثبت و ایجاد بارکد</button>
          </div>
        </form>
      </div>

      {/* Products Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="p-4 border-b border-slate-100">
          <h3 className="text-sm font-bold text-slate-700">لیست محصولات ثبت شده ({products.length})</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-right text-xs">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="p-3">بارکد</th>
                <th className="p-3">نام کالا</th>
                <th className="p-3">کد عددی</th>
                <th className="p-3">قیمت خرید</th>
                <th className="p-3">بسته</th>
                <th className="p-3">قیمت مصرف‌کننده</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {products.map(p => (
                <tr key={p.id} className="hover:bg-slate-50/50">
                  <td className="p-3">
                    <img src={`${API_BASE}/barcode/${p.barcode_value}?title=${encodeURIComponent(p.title)}`} alt={p.title} className="h-12 w-auto object-contain bg-white border border-slate-100 rounded p-1" />
                  </td>
                  <td className="p-3 font-semibold text-slate-900">{p.title}</td>
                  <td className="p-3 font-mono text-slate-600">{p.barcode_value}</td>
                  <td className="p-3">{p.cost_price.toLocaleString()}</td>
                  <td className="p-3">{p.units_per_pack}</td>
                  <td className="p-3">{p.consumer_price.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}\n