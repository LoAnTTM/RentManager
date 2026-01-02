'use client';

import React, { useState, useEffect } from 'react';
import { locationsAPI } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import Loading from '@/components/Loading';
import EmptyState from '@/components/EmptyState';
import Modal from '@/components/Modal';
import toast from 'react-hot-toast';
import { Building2, Plus, Edit2, Trash2, MapPin } from 'lucide-react';

interface Location {
  id: number;
  name: string;
  address: string;
  electric_price: string;
  water_price: string;
  notes: string;
  room_count: number;
  occupied_count: number;
}

export default function LocationsPage() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    electric_price: '3500',
    water_price: '15000',
    notes: '',
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadLocations();
  }, []);

  const loadLocations = async () => {
    try {
      const res = await locationsAPI.getAll();
      setLocations(res.data);
    } catch (error) {
      toast.error('Không thể tải danh sách khu trọ');
    } finally {
      setLoading(false);
    }
  };

  const openCreateModal = () => {
    setEditingLocation(null);
    setFormData({
      name: '',
      address: '',
      electric_price: '3500',
      water_price: '15000',
      notes: '',
    });
    setModalOpen(true);
  };

  const openEditModal = (location: Location) => {
    setEditingLocation(location);
    setFormData({
      name: location.name,
      address: location.address || '',
      electric_price: location.electric_price,
      water_price: location.water_price,
      notes: location.notes || '',
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name) {
      toast.error('Vui lòng nhập tên khu trọ');
      return;
    }

    setSaving(true);
    try {
      if (editingLocation) {
        await locationsAPI.update(editingLocation.id, formData);
        toast.success('Đã cập nhật khu trọ');
      } else {
        await locationsAPI.create(formData);
        toast.success('Đã thêm khu trọ mới');
      }
      setModalOpen(false);
      loadLocations();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (location: Location) => {
    if (!confirm(`Bạn có chắc muốn xóa ${location.name}?`)) return;

    try {
      await locationsAPI.delete(location.id);
      toast.success('Đã xóa khu trọ');
      loadLocations();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể xóa');
    }
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Khu trọ</h1>
          <p className="text-gray-500 mt-1">Quản lý các khu nhà trọ</p>
        </div>
        <button onClick={openCreateModal} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          <span>Thêm khu mới</span>
        </button>
      </div>

      {/* Locations grid */}
      {locations.length === 0 ? (
        <EmptyState
          icon={<Building2 className="w-10 h-10" />}
          title="Chưa có khu trọ nào"
          description="Thêm khu trọ đầu tiên để bắt đầu quản lý"
          action={
            <button onClick={openCreateModal} className="btn btn-primary">
              Thêm khu trọ
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {locations.map((location) => (
            <div key={location.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center">
                    <Building2 className="w-6 h-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-800">{location.name}</h3>
                    {location.address && (
                      <p className="text-sm text-gray-500 flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        {location.address}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="p-3 bg-warm-50 rounded-xl">
                  <p className="text-sm text-gray-500">Tổng phòng</p>
                  <p className="text-2xl font-bold text-gray-800">{location.room_count}</p>
                </div>
                <div className="p-3 bg-emerald-50 rounded-xl">
                  <p className="text-sm text-gray-500">Đang thuê</p>
                  <p className="text-2xl font-bold text-emerald-600">{location.occupied_count}</p>
                </div>
              </div>

              <div className="space-y-2 text-sm border-t border-warm-100 pt-4">
                <div className="flex justify-between">
                  <span className="text-gray-500">Giá điện:</span>
                  <span className="font-medium">{formatCurrency(location.electric_price)}/kWh</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Giá nước:</span>
                  <span className="font-medium">{formatCurrency(location.water_price)}/m³</span>
                </div>
              </div>

              <div className="flex gap-2 mt-4 pt-4 border-t border-warm-100">
                <button
                  onClick={() => openEditModal(location)}
                  className="flex-1 btn btn-secondary py-2 flex items-center justify-center gap-2"
                >
                  <Edit2 className="w-4 h-4" />
                  Sửa
                </button>
                <button
                  onClick={() => handleDelete(location)}
                  className="btn btn-danger py-2 px-4"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingLocation ? 'Sửa khu trọ' : 'Thêm khu trọ mới'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Tên khu trọ *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input"
              placeholder="VD: Khu A, Khu B..."
            />
          </div>

          <div>
            <label className="label">Địa chỉ</label>
            <input
              type="text"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              className="input"
              placeholder="Nhập địa chỉ khu trọ"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Giá điện (VND/kWh)</label>
              <input
                type="number"
                value={formData.electric_price}
                onChange={(e) => setFormData({ ...formData, electric_price: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="label">Giá nước (VND/m³)</label>
              <input
                type="number"
                value={formData.water_price}
                onChange={(e) => setFormData({ ...formData, water_price: e.target.value })}
                className="input"
              />
            </div>
          </div>

          <div>
            <label className="label">Ghi chú</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="input min-h-[100px]"
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
              {saving ? 'Đang lưu...' : editingLocation ? 'Cập nhật' : 'Thêm mới'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

