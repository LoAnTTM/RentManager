'use client';

import React, { useState, useEffect } from 'react';
import { invoicesAPI, locationsAPI } from '@/lib/api';
import { formatCurrency, getCurrentPeriod, getMonthName, invoiceStatusLabels } from '@/lib/utils';
import Loading from '@/components/Loading';
import EmptyState from '@/components/EmptyState';
import Modal from '@/components/Modal';
import toast from 'react-hot-toast';
import {
  FileText,
  Plus,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  Clock,
  AlertCircle,
} from 'lucide-react';

interface Location {
  id: number;
  name: string;
}

interface Invoice {
  id: number;
  room_id: number;
  month: number;
  year: number;
  room_fee: string;
  electric_fee: string;
  water_fee: string;
  other_fee: string;
  total: string;
  paid_amount: string;
  status: 'unpaid' | 'partial' | 'paid';
  notes: string;
  room?: {
    id: number;
    room_code: string;
    location_id: number;
  };
}

export default function InvoicesPage() {
  const { month: currentMonth, year: currentYear } = getCurrentPeriod();
  const [month, setMonth] = useState(currentMonth);
  const [year, setYear] = useState(currentYear);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterLocation, setFilterLocation] = useState<number | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [detailModal, setDetailModal] = useState<Invoice | null>(null);

  useEffect(() => {
    loadData();
  }, [month, year, filterLocation, filterStatus]);

  const loadData = async () => {
    try {
      const [invoicesRes, locationsRes] = await Promise.all([
        invoicesAPI.getAll({
          month,
          year,
          location_id: filterLocation || undefined,
          status: filterStatus || undefined,
        }),
        locationsAPI.getAll(),
      ]);
      setInvoices(invoicesRes.data);
      setLocations(locationsRes.data);
    } catch (error) {
      toast.error('Không thể tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

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

  const handleGenerate = async () => {
    if (!confirm(`Tạo hóa đơn cho ${getMonthName(month)}/${year}?`)) return;

    setGenerating(true);
    try {
      const res = await invoicesAPI.generate({
        month,
        year,
        location_id: filterLocation || undefined,
      });
      toast.success(res.data.message);
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    } finally {
      setGenerating(false);
    }
  };

  const handleMarkPaid = async (invoice: Invoice) => {
    try {
      await invoicesAPI.markPaid(invoice.id);
      toast.success('Đã cập nhật trạng thái');
      loadData();
      setDetailModal(null);
    } catch (error) {
      toast.error('Không thể cập nhật');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'paid':
        return <CheckCircle className="w-5 h-5 text-emerald-500" />;
      case 'partial':
        return <Clock className="w-5 h-5 text-amber-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-red-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return 'badge-success';
      case 'partial':
        return 'badge-warning';
      default:
        return 'badge-danger';
    }
  };

  // Calculate totals
  const totalAmount = invoices.reduce((sum, inv) => sum + parseFloat(inv.total), 0);
  const paidAmount = invoices.reduce((sum, inv) => sum + parseFloat(inv.paid_amount), 0);
  const unpaidAmount = totalAmount - paidAmount;

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Hóa đơn</h1>
          <p className="text-gray-500 mt-1">Quản lý hóa đơn thu tiền hàng tháng</p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          <span>{generating ? 'Đang tạo...' : 'Tạo hóa đơn tháng'}</span>
        </button>
      </div>

      {/* Month selector and filters */}
      <div className="flex flex-wrap items-center gap-4">
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

        <select
          value={filterLocation || ''}
          onChange={(e) => setFilterLocation(e.target.value ? parseInt(e.target.value) : null)}
          className="input w-auto"
        >
          <option value="">Tất cả khu</option>
          {locations.map((loc) => (
            <option key={loc.id} value={loc.id}>
              {loc.name}
            </option>
          ))}
        </select>

        <select
          value={filterStatus || ''}
          onChange={(e) => setFilterStatus(e.target.value || null)}
          className="input w-auto"
        >
          <option value="">Tất cả trạng thái</option>
          <option value="unpaid">Chưa thu</option>
          <option value="partial">Thu một phần</option>
          <option value="paid">Đã thu</option>
        </select>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <p className="text-blue-600 text-sm mb-1">Tổng cần thu</p>
          <p className="text-2xl font-bold text-blue-700">{formatCurrency(totalAmount)}</p>
        </div>
        <div className="card bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200">
          <p className="text-emerald-600 text-sm mb-1">Đã thu</p>
          <p className="text-2xl font-bold text-emerald-700">{formatCurrency(paidAmount)}</p>
        </div>
        <div className="card bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <p className="text-orange-600 text-sm mb-1">Còn nợ</p>
          <p className="text-2xl font-bold text-orange-700">{formatCurrency(unpaidAmount)}</p>
        </div>
      </div>

      {/* Invoices list */}
      {invoices.length === 0 ? (
        <EmptyState
          icon={<FileText className="w-10 h-10" />}
          title="Chưa có hóa đơn"
          description={`Nhấn "Tạo hóa đơn tháng" để tạo hóa đơn cho ${getMonthName(month)}`}
          action={
            <button onClick={handleGenerate} className="btn btn-primary">
              Tạo hóa đơn
            </button>
          }
        />
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="table-header">
                <th className="table-cell rounded-tl-xl">Phòng</th>
                <th className="table-cell text-right">Tiền phòng</th>
                <th className="table-cell text-right">Tiền điện</th>
                <th className="table-cell text-right">Tiền nước</th>
                <th className="table-cell text-right">Tổng</th>
                <th className="table-cell text-center">Trạng thái</th>
                <th className="table-cell text-center rounded-tr-xl">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((invoice) => (
                <tr key={invoice.id} className="hover:bg-warm-50">
                  <td className="table-cell">
                    <p className="font-medium">Phòng {invoice.room?.room_code}</p>
                  </td>
                  <td className="table-cell text-right">
                    {formatCurrency(invoice.room_fee)}
                  </td>
                  <td className="table-cell text-right">
                    {formatCurrency(invoice.electric_fee)}
                  </td>
                  <td className="table-cell text-right">
                    {formatCurrency(invoice.water_fee)}
                  </td>
                  <td className="table-cell text-right font-bold text-primary-600">
                    {formatCurrency(invoice.total)}
                  </td>
                  <td className="table-cell text-center">
                    <span className={`badge ${getStatusBadge(invoice.status)}`}>
                      {invoiceStatusLabels[invoice.status]}
                    </span>
                  </td>
                  <td className="table-cell text-center">
                    <div className="flex items-center justify-center gap-2">
                      <button
                        onClick={() => setDetailModal(invoice)}
                        className="px-3 py-1 text-sm bg-warm-100 hover:bg-warm-200 rounded-lg"
                      >
                        Chi tiết
                      </button>
                      {invoice.status !== 'paid' && (
                        <button
                          onClick={() => handleMarkPaid(invoice)}
                          className="px-3 py-1 text-sm bg-emerald-100 text-emerald-700 hover:bg-emerald-200 rounded-lg"
                        >
                          Thu tiền
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Detail Modal */}
      <Modal
        isOpen={!!detailModal}
        onClose={() => setDetailModal(null)}
        title={`Hóa đơn phòng ${detailModal?.room?.room_code}`}
      >
        {detailModal && (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-warm-50 rounded-xl">
              <span className="text-gray-600">Tháng:</span>
              <span className="font-medium">
                {getMonthName(detailModal.month)} / {detailModal.year}
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b border-warm-100">
                <span className="text-gray-600">Tiền phòng</span>
                <span className="font-medium">{formatCurrency(detailModal.room_fee)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-warm-100">
                <span className="text-gray-600">Tiền điện</span>
                <span className="font-medium">{formatCurrency(detailModal.electric_fee)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-warm-100">
                <span className="text-gray-600">Tiền nước</span>
                <span className="font-medium">{formatCurrency(detailModal.water_fee)}</span>
              </div>
              {parseFloat(detailModal.other_fee) > 0 && (
                <div className="flex justify-between py-2 border-b border-warm-100">
                  <span className="text-gray-600">Phí khác</span>
                  <span className="font-medium">{formatCurrency(detailModal.other_fee)}</span>
                </div>
              )}
              <div className="flex justify-between py-3 bg-primary-50 rounded-xl px-4">
                <span className="font-bold text-primary-700">TỔNG CỘNG</span>
                <span className="font-bold text-primary-700 text-xl">
                  {formatCurrency(detailModal.total)}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-warm-50 rounded-xl">
              <span className="text-gray-600">Trạng thái:</span>
              <span className={`badge ${getStatusBadge(detailModal.status)}`}>
                {invoiceStatusLabels[detailModal.status]}
              </span>
            </div>

            {detailModal.status !== 'paid' && (
              <button
                onClick={() => handleMarkPaid(detailModal)}
                className="w-full btn btn-success flex items-center justify-center gap-2"
              >
                <CheckCircle className="w-5 h-5" />
                Đánh dấu đã thu tiền
              </button>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}

