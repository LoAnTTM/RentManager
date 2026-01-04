'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { dashboardAPI, invoicesAPI } from '@/lib/api';
import { formatCurrency, getCurrentPeriod, getMonthName } from '@/lib/utils';
import Loading from '@/components/Loading';
import toast from 'react-hot-toast';
import {
  DoorOpen,
  Users,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Clock,
} from 'lucide-react';

interface DashboardStats {
  total_rooms: number;
  occupied_rooms: number;
  vacant_rooms: number;
  total_tenants: number;
  total_income_this_month: string;
  total_paid_this_month: string;
  total_unpaid_this_month: string;
  total_expense_this_month: string;
}

interface UnpaidInvoice {
  id: number;
  room_code: string;
  location_name: string;
  total: string;
  remaining: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [unpaidInvoices, setUnpaidInvoices] = useState<UnpaidInvoice[]>([]);
  const [loading, setLoading] = useState(true);
  const { month, year } = getCurrentPeriod();

  const loadData = useCallback(async () => {
    try {
      const [statsRes, reportRes] = await Promise.all([
        dashboardAPI.getStats(),
        dashboardAPI.getReport(month, year),
      ]);
      setStats(statsRes.data);
      setUnpaidInvoices(reportRes.data.unpaid_invoices || []);
    } catch (error) {
      toast.error('Không thể tải dữ liệu');
    } finally {
      setLoading(false);
    }
  }, [month, year]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleMarkPaid = async (invoiceId: number) => {
    try {
      await invoicesAPI.pay(invoiceId);
      toast.success('Đã cập nhật trạng thái');
      loadData();
    } catch (error) {
      toast.error('Không thể cập nhật');
    }
  };

  if (loading) {
    return <Loading />;
  }

  const netIncome = stats
    ? parseFloat(stats.total_paid_this_month) - parseFloat(stats.total_expense_this_month)
    : 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-800">Tổng quan</h1>
        <p className="text-gray-500 mt-1">
          {getMonthName(month)} năm {year}
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total rooms */}
        <div className="stat-card bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <div className="w-14 h-14 rounded-xl bg-blue-500 flex items-center justify-center mb-4">
            <DoorOpen className="w-7 h-7 text-white" />
          </div>
          <div className="stat-value text-blue-700">{stats?.total_rooms || 0}</div>
          <div className="stat-label text-blue-600">Tổng phòng</div>
        </div>

        {/* Occupied */}
        <div className="stat-card bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200">
          <div className="w-14 h-14 rounded-xl bg-emerald-500 flex items-center justify-center mb-4">
            <Users className="w-7 h-7 text-white" />
          </div>
          <div className="stat-value text-emerald-700">{stats?.occupied_rooms || 0}</div>
          <div className="stat-label text-emerald-600">Đang thuê</div>
        </div>

        {/* Vacant */}
        <div className="stat-card bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200">
          <div className="w-14 h-14 rounded-xl bg-amber-500 flex items-center justify-center mb-4">
            <Clock className="w-7 h-7 text-white" />
          </div>
          <div className="stat-value text-amber-700">{stats?.vacant_rooms || 0}</div>
          <div className="stat-label text-amber-600">Phòng trống</div>
        </div>

        {/* Total tenants */}
        <div className="stat-card bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <div className="w-14 h-14 rounded-xl bg-purple-500 flex items-center justify-center mb-4">
            <Users className="w-7 h-7 text-white" />
          </div>
          <div className="stat-value text-purple-700">{stats?.total_tenants || 0}</div>
          <div className="stat-label text-purple-600">Người thuê</div>
        </div>
      </div>

      {/* Financial stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Collected */}
        <div className="stat-card bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-green-500 flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-white" />
            </div>
            <div className="text-lg font-medium text-green-700">Đã thu</div>
          </div>
          <div className="text-3xl font-bold text-green-700">
            {formatCurrency(stats?.total_paid_this_month || 0)}
          </div>
        </div>

        {/* Pending */}
        <div className="stat-card bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-orange-500 flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-white" />
            </div>
            <div className="text-lg font-medium text-orange-700">Chưa thu</div>
          </div>
          <div className="text-3xl font-bold text-orange-700">
            {formatCurrency(stats?.total_unpaid_this_month || 0)}
          </div>
        </div>

        {/* Expenses */}
        <div className="stat-card bg-gradient-to-br from-red-50 to-red-100 border-red-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-red-500 flex items-center justify-center">
              <TrendingDown className="w-6 h-6 text-white" />
            </div>
            <div className="text-lg font-medium text-red-700">Đã chi</div>
          </div>
          <div className="text-3xl font-bold text-red-700">
            {formatCurrency(stats?.total_expense_this_month || 0)}
          </div>
        </div>
      </div>

      {/* Net income banner */}
      <div className={`card ${netIncome >= 0 ? 'bg-gradient-to-r from-emerald-500 to-teal-500' : 'bg-gradient-to-r from-red-500 to-rose-500'} text-white border-none`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/80 text-lg">Lãi/Lỗ tháng này</p>
            <p className="text-4xl font-bold mt-2">{formatCurrency(netIncome)}</p>
          </div>
          <div className="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center">
            <TrendingUp className="w-8 h-8" />
          </div>
        </div>
      </div>

      {/* Unpaid invoices */}
      {unpaidInvoices.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <AlertCircle className="w-6 h-6 text-orange-500" />
            Phòng chưa thu tiền ({unpaidInvoices.length})
          </h2>
          <div className="space-y-3">
            {unpaidInvoices.map((invoice) => (
              <div
                key={invoice.id}
                className="flex items-center justify-between p-4 bg-warm-50 rounded-xl"
              >
                <div>
                  <p className="font-semibold text-gray-800">
                    Phòng {invoice.room_code}
                  </p>
                  <p className="text-sm text-gray-500">{invoice.location_name}</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="font-bold text-orange-600">
                      {formatCurrency(invoice.remaining)}
                    </p>
                    <p className="text-sm text-gray-500">còn nợ</p>
                  </div>
                  <button
                    onClick={() => handleMarkPaid(invoice.id)}
                    className="btn btn-success py-2 px-4"
                  >
                    Thu tiền
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
