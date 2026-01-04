'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { expensesAPI, locationsAPI } from '@/lib/api';
import { formatCurrency, formatDate, getCurrentPeriod, getMonthName, expenseCategoryLabels } from '@/lib/utils';
import Loading from '@/components/Loading';
import EmptyState from '@/components/EmptyState';
import Modal from '@/components/Modal';
import toast from 'react-hot-toast';
import {
  Wallet,
  Plus,
  Edit2,
  Trash2,
  ChevronLeft,
  ChevronRight,
  TrendingDown,
} from 'lucide-react';

interface Location {
  id: number;
  name: string;
}

interface Expense {
  id: number;
  location_id: number | null;
  category: 'repair' | 'utility' | 'maintenance' | 'other';
  description: string;
  amount: string;
  expense_date: string;
  notes: string;
}

export default function ExpensesPage() {
  const { month: currentMonth, year: currentYear } = getCurrentPeriod();
  const [month, setMonth] = useState(currentMonth);
  const [year, setYear] = useState(currentYear);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null);
  const [formData, setFormData] = useState({
    location_id: '',
    category: 'other',
    description: '',
    amount: '',
    expense_date: new Date().toISOString().split('T')[0],
    notes: '',
  });
  const [saving, setSaving] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [expensesRes, locationsRes] = await Promise.all([
        expensesAPI.getAll({ month, year }),
        locationsAPI.getAll(),
      ]);
      setExpenses(expensesRes.data);
      setLocations(locationsRes.data);
    } catch (error) {
      toast.error('Không thể tải dữ liệu');
    } finally {
      setLoading(false);
    }
  }, [month, year]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const changeMonth = (delta: number) => {
    let newMonth = month + delta;
    let newYear = year;

    if (newMonth > 12) {
      newMonth = 1;
      newYear++;
    } else if (newMonth < 1) {
      newMonth = 12;
      newYear--;
    }

    setMonth(newMonth);
    setYear(newYear);
  };

  const openCreateModal = () => {
    setEditingExpense(null);
    setFormData({
      location_id: '',
      category: 'other',
      description: '',
      amount: '',
      expense_date: new Date().toISOString().split('T')[0],
      notes: '',
    });
    setModalOpen(true);
  };

  const openEditModal = (expense: Expense) => {
    setEditingExpense(expense);
    setFormData({
      location_id: expense.location_id?.toString() || '',
      category: expense.category,
      description: expense.description,
      amount: expense.amount,
      expense_date: expense.expense_date,
      notes: expense.notes || '',
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.description || !formData.amount || !formData.expense_date) {
      toast.error('Vui lòng điền đầy đủ thông tin');
      return;
    }

    setSaving(true);
    try {
      const data = {
        ...formData,
        location_id: formData.location_id ? parseInt(formData.location_id) : null,
      };

      if (editingExpense) {
        await expensesAPI.update(editingExpense.id, data);
        toast.success('Đã cập nhật khoản chi');
      } else {
        await expensesAPI.create(data);
        toast.success('Đã thêm khoản chi mới');
      }
      setModalOpen(false);
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (expense: Expense) => {
    if (!confirm('Bạn có chắc muốn xóa khoản chi này?')) return;

    try {
      await expensesAPI.delete(expense.id);
      toast.success('Đã xóa khoản chi');
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể xóa');
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'repair':
        return 'bg-red-100 text-red-700';
      case 'utility':
        return 'bg-blue-100 text-blue-700';
      case 'maintenance':
        return 'bg-purple-100 text-purple-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getLocationName = (locationId: number | null) => {
    if (!locationId) return 'Chung';
    const loc = locations.find((l) => l.id === locationId);
    return loc?.name || 'N/A';
  };

  // Calculate totals by category
  const totalExpense = expenses.reduce((sum, exp) => sum + parseFloat(exp.amount), 0);
  const categoryTotals = expenses.reduce((acc, exp) => {
    acc[exp.category] = (acc[exp.category] || 0) + parseFloat(exp.amount);
    return acc;
  }, {} as Record<string, number>);

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Thu chi</h1>
          <p className="text-gray-500 mt-1">Quản lý các khoản chi tiêu</p>
        </div>
        <button onClick={openCreateModal} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          <span>Thêm khoản chi</span>
        </button>
      </div>

      {/* Month selector */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 bg-white rounded-xl border border-warm-200 p-1">
          <button
            onClick={() => changeMonth(-1)}
            className="p-2 hover:bg-warm-100 rounded-lg"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div className="px-4 py-2 font-medium">
            {getMonthName(month)} / {year}
          </div>
          <button
            onClick={() => changeMonth(1)}
            className="p-2 hover:bg-warm-100 rounded-lg"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Summary */}
      <div className="card bg-gradient-to-r from-red-500 to-rose-500 text-white border-none">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/80">Tổng chi tháng này</p>
            <p className="text-4xl font-bold mt-2">{formatCurrency(totalExpense)}</p>
          </div>
          <div className="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center">
            <TrendingDown className="w-8 h-8" />
          </div>
        </div>
      </div>

      {/* Category breakdown */}
      {Object.keys(categoryTotals).length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {Object.entries(categoryTotals).map(([category, total]) => (
            <div key={category} className="card">
              <span className={`badge ${getCategoryColor(category)} mb-2`}>
                {expenseCategoryLabels[category]}
              </span>
              <p className="text-xl font-bold text-gray-800">{formatCurrency(total)}</p>
            </div>
          ))}
        </div>
      )}

      {/* Expenses list */}
      {expenses.length === 0 ? (
        <EmptyState
          icon={<Wallet className="w-10 h-10" />}
          title="Chưa có khoản chi nào"
          description={`Thêm khoản chi cho ${getMonthName(month)}`}
          action={
            <button onClick={openCreateModal} className="btn btn-primary">
              Thêm khoản chi
            </button>
          }
        />
      ) : (
        <div className="space-y-3">
          {expenses.map((expense) => (
            <div key={expense.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`badge ${getCategoryColor(expense.category)}`}>
                      {expenseCategoryLabels[expense.category]}
                    </span>
                    <span className="text-sm text-gray-500">
                      {getLocationName(expense.location_id)}
                    </span>
                  </div>
                  <h3 className="font-medium text-gray-800">{expense.description}</h3>
                  <p className="text-sm text-gray-500 mt-1">
                    {formatDate(expense.expense_date)}
                  </p>
                  {expense.notes && (
                    <p className="text-sm text-gray-500 mt-1 italic">{expense.notes}</p>
                  )}
                </div>
                <div className="flex items-center gap-4">
                  <p className="text-xl font-bold text-red-600">
                    -{formatCurrency(expense.amount)}
                  </p>
                  <div className="flex gap-1">
                    <button
                      onClick={() => openEditModal(expense)}
                      className="p-2 hover:bg-warm-100 rounded-lg"
                    >
                      <Edit2 className="w-4 h-4 text-gray-500" />
                    </button>
                    <button
                      onClick={() => handleDelete(expense)}
                      className="p-2 hover:bg-red-50 rounded-lg"
                    >
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingExpense ? 'Sửa khoản chi' : 'Thêm khoản chi mới'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Mô tả *</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="input"
              placeholder="VD: Sửa ống nước, mua bóng đèn..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Số tiền (VND) *</label>
              <input
                type="number"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                className="input"
                placeholder="500000"
              />
            </div>
            <div>
              <label className="label">Ngày chi *</label>
              <input
                type="date"
                value={formData.expense_date}
                onChange={(e) => setFormData({ ...formData, expense_date: e.target.value })}
                className="input"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Loại chi</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="input"
              >
                <option value="repair">Sửa chữa</option>
                <option value="utility">Điện nước chung</option>
                <option value="maintenance">Bảo trì</option>
                <option value="other">Khác</option>
              </select>
            </div>
            <div>
              <label className="label">Khu trọ</label>
              <select
                value={formData.location_id}
                onChange={(e) => setFormData({ ...formData, location_id: e.target.value })}
                className="input"
              >
                <option value="">Chi chung</option>
                {locations.map((loc) => (
                  <option key={loc.id} value={loc.id}>
                    {loc.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="label">Ghi chú</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="input min-h-[80px]"
              placeholder="Ghi chú thêm..."
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={() => setModalOpen(false)}
              className="flex-1 btn btn-secondary"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 btn btn-primary"
            >
              {saving ? 'Đang lưu...' : editingExpense ? 'Cập nhật' : 'Thêm mới'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
