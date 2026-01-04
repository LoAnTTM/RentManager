import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  getMe: () => api.get('/auth/me'),
};

// Dashboard
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getReport: (month: number, year: number) =>
    api.get('/dashboard/report', { params: { month, year } }),
};

// Locations
export const locationsAPI = {
  getAll: () => api.get('/locations'),
  getOne: (id: number) => api.get(`/locations/${id}`),
  create: (data: any) => api.post('/locations', data),
  update: (id: number, data: any) => api.put(`/locations/${id}`, data),
  delete: (id: number) => api.delete(`/locations/${id}`),
};

// Room Types
export const roomTypesAPI = {
  getAll: (params?: { location_id?: number }) =>
    api.get('/room-types', { params }),
  getOne: (id: number) => api.get(`/room-types/${id}`),
  create: (data: any) => api.post('/room-types', data),
  update: (id: number, data: any) => api.put(`/room-types/${id}`, data),
  delete: (id: number) => api.delete(`/room-types/${id}`),
};

// Rooms
export const roomsAPI = {
  getAll: (params?: { location_id?: number; room_type_id?: number; status?: string }) =>
    api.get('/rooms', { params }),
  getOne: (id: number) => api.get(`/rooms/${id}`),
  create: (data: any) => api.post('/rooms', data),
  update: (id: number, data: any) => api.put(`/rooms/${id}`, data),
  delete: (id: number) => api.delete(`/rooms/${id}`),
};

// Tenants
export const tenantsAPI = {
  getAll: (params?: { room_id?: number; is_active?: boolean }) =>
    api.get('/tenants', { params }),
  getOne: (id: number) => api.get(`/tenants/${id}`),
  create: (data: any) => api.post('/tenants', data),
  update: (id: number, data: any) => api.put(`/tenants/${id}`, data),
  moveOut: (id: number, move_out_date?: string) =>
    api.put(`/tenants/${id}/move-out`, null, { params: { move_out_date } }),
  delete: (id: number) => api.delete(`/tenants/${id}`),
};

// Meters
export const metersAPI = {
  getAll: (params?: { room_id?: number; meter_type?: string }) =>
    api.get('/meters', { params }),
  create: (data: any) => api.post('/meters', data),
  getReadings: (params?: { month?: number; year?: number; room_id?: number }) =>
    api.get('/meters/readings', { params }),
  createReading: (data: any) => api.post('/meters/readings', data),
  createReadingsBatch: (data: any) => api.post('/meters/readings/batch', data),
  updateReading: (id: number, data: any) => api.put(`/meters/readings/${id}`, data),
};

// Invoices
export const invoicesAPI = {
  getAll: (params?: { month?: number; year?: number; location_id?: number; status?: string }) =>
    api.get('/invoices', { params }),
  getOne: (id: number) => api.get(`/invoices/${id}`),
  generate: (data: { month: number; year: number; location_id?: number }) =>
    api.post('/invoices/generate', data),
  update: (id: number, data: any) => api.put(`/invoices/${id}`, data),
  pay: (id: number, amount?: number) =>
    api.put(`/invoices/${id}/pay`, null, { params: amount ? { amount } : {} }),
  updateAbsent: (id: number, absent_days: number) =>
    api.put(`/invoices/${id}/absent`, null, { params: { absent_days } }),
};

// Payments
export const paymentsAPI = {
  getAll: (params?: { invoice_id?: number }) =>
    api.get('/payments', { params }),
  create: (data: any) => api.post('/payments', data),
};

// Expenses
export const expensesAPI = {
  getAll: (params?: { location_id?: number; category?: string; month?: number; year?: number }) =>
    api.get('/expenses', { params }),
  getOne: (id: number) => api.get(`/expenses/${id}`),
  create: (data: any) => api.post('/expenses', data),
  update: (id: number, data: any) => api.put(`/expenses/${id}`, data),
  delete: (id: number) => api.delete(`/expenses/${id}`),
};

export default api;
