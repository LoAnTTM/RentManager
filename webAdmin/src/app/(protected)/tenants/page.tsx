'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { tenantsAPI, roomsAPI } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import Loading from '@/components/Loading';
import EmptyState from '@/components/EmptyState';
import Modal from '@/components/Modal';
import toast from 'react-hot-toast';
import { Users, Plus, Edit2, LogOut, Phone, CreditCard, Calendar } from 'lucide-react';

interface Room {
  id: number;
  room_code: string;
  location_id: number;
  status: string;
}

interface Tenant {
  id: number;
  room_id: number;
  full_name: string;
  phone: string;
  id_card: string;
  move_in_date: string;
  move_out_date: string | null;
  is_active: boolean;
  notes: string;
  room?: Room;
}

export default function TenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInactive, setShowInactive] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingTenant, setEditingTenant] = useState<Tenant | null>(null);
  const [formData, setFormData] = useState({
    room_id: '',
    full_name: '',
    phone: '',
    id_card: '',
    move_in_date: new Date().toISOString().split('T')[0],
    notes: '',
  });
  const [saving, setSaving] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [tenantsRes, roomsRes] = await Promise.all([
        tenantsAPI.getAll({ is_active: showInactive ? undefined : true }),
        roomsAPI.getAll(),
      ]);
      setTenants(tenantsRes.data);
      setRooms(roomsRes.data);
    } catch (error) {
      toast.error('Không thể tải dữ liệu');
    } finally {
      setLoading(false);
    }
  }, [showInactive]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const availableRooms = rooms.filter((r) => r.status === 'vacant');

  const openCreateModal = () => {
    setEditingTenant(null);
    setFormData({
      room_id: availableRooms[0]?.id?.toString() || '',
      full_name: '',
      phone: '',
      id_card: '',
      move_in_date: new Date().toISOString().split('T')[0],
      notes: '',
    });
    setModalOpen(true);
  };

  const openEditModal = (tenant: Tenant) => {
    setEditingTenant(tenant);
    setFormData({
      room_id: tenant.room_id.toString(),
      full_name: tenant.full_name,
      phone: tenant.phone || '',
      id_card: tenant.id_card || '',
      move_in_date: tenant.move_in_date,
      notes: tenant.notes || '',
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.room_id || !formData.full_name || !formData.move_in_date) {
      toast.error('Vui lòng điền đầy đủ thông tin bắt buộc');
      return;
    }

    setSaving(true);
    try {
      const data = {
        ...formData,
        room_id: parseInt(formData.room_id),
      };

      if (editingTenant) {
        await tenantsAPI.update(editingTenant.id, data);
        toast.success('Đã cập nhật thông tin');
      } else {
        await tenantsAPI.create(data);
        toast.success('Đã thêm người thuê mới');
      }
      setModalOpen(false);
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    } finally {
      setSaving(false);
    }
  };

  const handleMoveOut = async (tenant: Tenant) => {
    if (!confirm(`Xác nhận ${tenant.full_name} trả phòng?`)) return;

    try {
      await tenantsAPI.moveOut(tenant.id);
      toast.success('Đã cập nhật trả phòng');
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    }
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Người thuê</h1>
          <p className="text-gray-500 mt-1">Quản lý thông tin người thuê trọ</p>
        </div>
        <button onClick={openCreateModal} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          <span>Thêm người thuê</span>
        </button>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showInactive}
            onChange={(e) => setShowInactive(e.target.checked)}
            className="w-5 h-5 rounded border-gray-300"
          />
          <span className="text-gray-600">Hiển thị người đã trả phòng</span>
        </label>
      </div>

      {/* Tenants list */}
      {tenants.length === 0 ? (
        <EmptyState
          icon={<Users className="w-10 h-10" />}
          title="Chưa có người thuê nào"
          description="Thêm người thuê mới để bắt đầu quản lý"
          action={
            <button onClick={openCreateModal} className="btn btn-primary">
              Thêm người thuê
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tenants.map((tenant) => (
            <div
              key={tenant.id}
              className={`card hover:shadow-md transition-shadow ${
                !tenant.is_active ? 'opacity-60' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center text-white text-xl font-bold ${
                      tenant.is_active ? 'bg-primary-500' : 'bg-gray-400'
                    }`}
                  >
                    {tenant.full_name.charAt(0)}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-800">{tenant.full_name}</h3>
                    <p className="text-sm text-gray-500">
                      Phòng {tenant.room?.room_code}
                    </p>
                  </div>
                </div>
                <span className={`badge ${tenant.is_active ? 'badge-success' : 'badge-gray'}`}>
                  {tenant.is_active ? 'Đang thuê' : 'Đã trả phòng'}
                </span>
              </div>

              <div className="space-y-2 text-sm">
                {tenant.phone && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <Phone className="w-4 h-4" />
                    <span>{tenant.phone}</span>
                  </div>
                )}
                {tenant.id_card && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <CreditCard className="w-4 h-4" />
                    <span>{tenant.id_card}</span>
                  </div>
                )}
                <div className="flex items-center gap-2 text-gray-600">
                  <Calendar className="w-4 h-4" />
                  <span>Vào ở: {formatDate(tenant.move_in_date)}</span>
                </div>
                {tenant.move_out_date && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <LogOut className="w-4 h-4" />
                    <span>Trả phòng: {formatDate(tenant.move_out_date)}</span>
                  </div>
                )}
              </div>

              {tenant.is_active && (
                <div className="flex gap-2 mt-4 pt-4 border-t border-warm-100">
                  <button
                    onClick={() => openEditModal(tenant)}
                    className="flex-1 btn btn-secondary py-2 flex items-center justify-center gap-2"
                  >
                    <Edit2 className="w-4 h-4" />
                    Sửa
                  </button>
                  <button
                    onClick={() => handleMoveOut(tenant)}
                    className="btn btn-danger py-2 flex items-center gap-2"
                  >
                    <LogOut className="w-4 h-4" />
                    Trả phòng
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingTenant ? 'Sửa thông tin người thuê' : 'Thêm người thuê mới'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Phòng *</label>
            <select
              value={formData.room_id}
              onChange={(e) => setFormData({ ...formData, room_id: e.target.value })}
              className="input"
              disabled={!!editingTenant}
            >
              <option value="">Chọn phòng</option>
              {(editingTenant ? rooms : availableRooms).map((room) => (
                <option key={room.id} value={room.id}>
                  Phòng {room.room_code}
                </option>
              ))}
            </select>
            {!editingTenant && availableRooms.length === 0 && (
              <p className="text-sm text-amber-600 mt-1">Không có phòng trống</p>
            )}
          </div>

          <div>
            <label className="label">Họ tên *</label>
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              className="input"
              placeholder="Nhập họ tên đầy đủ"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Số điện thoại</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="input"
                placeholder="0901234567"
              />
            </div>
            <div>
              <label className="label">CCCD/CMND</label>
              <input
                type="text"
                value={formData.id_card}
                onChange={(e) => setFormData({ ...formData, id_card: e.target.value })}
                className="input"
                placeholder="079123456789"
              />
            </div>
          </div>

          <div>
            <label className="label">Ngày vào ở *</label>
            <input
              type="date"
              value={formData.move_in_date}
              onChange={(e) => setFormData({ ...formData, move_in_date: e.target.value })}
              className="input"
            />
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
              {saving ? 'Đang lưu...' : editingTenant ? 'Cập nhật' : 'Thêm mới'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
