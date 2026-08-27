export interface Product {
  id: number;
  title: string;
  cost_price: number;
  units_per_pack: number;
  barcode_value: string;
  consumer_price?: number | null;
  created_at: string;
}

export interface ProductCreateInput {
  title: string;
  cost_price: number;
  units_per_pack: number;
  barcode_value: string;
  consumer_price?: number | null;
}