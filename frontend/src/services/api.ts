import axios from 'axios';
import { Product, ProductCreatePayload, SummaryStats } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
});

// تزریق خودکار initData تلگرام به تمام هدرهای ارسالی
apiClient.interceptors.request.use((config) => {
  if (window.Telegram?.WebApp?.initData) {
    config.headers['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData;
  }
  return config;
});

export const ProductAPI = {
  getSummary: async (): Promise<SummaryStats> => {
    const res = await apiClient.get('/products/summary');
    return res.data;
  },
  getAll: async (search?: string): Promise<Product[]> => {
    const res = await apiClient.get('/products', { params: { search } });
    return res.data;
  },
  create: async (data: ProductCreatePayload): Promise<Product> => {
    const res = await apiClient.post('/products', data);
    return res.data;
  },
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/products/${id}`);
  },
  getExcelDownloadUrl: () => `${API_BASE}/export/excel`,
  getPdfDownloadUrl: () => `${API_BASE}/export/pdf`,
};