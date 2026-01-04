'use client';

import React, { useState, useEffect } from 'react';
import { locationsAPI, roomTypesAPI } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import Loading from '@/components/Loading';
import EmptyState from '@/components/EmptyState';
import Modal from '@/components/Modal';
import toast from 'react-hot-toast';
import { Building2, Plus, Edit2, Trash2, MapPin, Phone, User, Tag } from 'lucide-react';

interface RoomType {
  id: number;
  code: string;
  name: string;
  price: string;
  daily_deduction: string;
}

interface Location {
  id: number;
  name: string;
  address: string;
  owner_name: string;
  owner_phone: string;
  electric_price: string;
  water_price: string;
  garbage_fee: string;
  wifi_fee: string;
  tv_fee: string;
  laundry_fee: string;
  payment_due_day: number;
  notes: string;
  room_count: number;
  occupied_count: number;
  room_types: RoomType[];
}

export default function LocationsPage() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [roomTypeModalOpen, setRoomTypeModalOpen] = useState(false);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    owner_name: '',
    owner_phone: '',
    electric_price: '3500',
    water_price: '8000',
    garbage_fee: '30000',
    wifi_fee: '0',
    tv_fee: '0',
    laundry_fee: '0',
    payment_due_day: '5',
    notes: '',
  });
  const [roomTypeForm, setRoomTypeForm] = useState({
    code: '',
    name: '',
    price: '',
    daily_deduction: '0',
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
      owner_name: '',
      owner_phone: '',
      electric_price: '3500',
      water_price: '8000',
      garbage_fee: '30000',
      wifi_fee: '0',
      tv_fee: '0',
      laundry_fee: '0',
      payment_due_day: '5',
      notes: '',
    });
    setModalOpen(true);
  };

  const openEditModal = (location: Location) => {
    setEditingLocation(location);
    setFormData({
      name: location.name,
      address: location.address || '',
      owner_name: location.owner_name || '',
      owner_phone: location.owner_phone || '',
      electric_price: location.electric_price,
      water_price: location.water_price,
      garbage_fee: location.garbage_fee,
      wifi_fee: location.wifi_fee,
      tv_fee: location.tv_fee,
      laundry_fee: location.laundry_fee,
      payment_due_day: location.payment_due_day?.toString() || '5',
      notes: location.notes || '',
    });
    setModalOpen(true);
  };

  const openRoomTypeModal = (location: Location) => {
    setSelectedLocation(location);
    setRoomTypeForm({ code: '', name: '', price: '', daily_deduction: '0' });
    setRoomTypeModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name) {
      toast.error('Vui lòng nhập tên khu trọ');
      return;
    }

    setSaving(true);
    try {
      const data = {
        ...formData,
        payment_due_day: parseInt(formData.payment_due_day),
      };

      if (editingLocation) {
        await locationsAPI.update(editingLocation.id, data);
        toast.success('Đã cập nhật khu trọ');
      } else {
        await locationsAPI.create(data);
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

  const handleAddRoomType = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!roomTypeForm.code || !roomTypeForm.price || !selectedLocation) {
      toast.error('Vui lòng nhập đầy đủ thông tin');
      return;
    }

    setSaving(true);
    try {
      await roomTypesAPI.create({
        location_id: selectedLocation.id,
        ...roomTypeForm,
      });
      toast.success('Đã thêm loại phòng');
      setRoomTypeModalOpen(false);
      loadLocations();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteRoomType = async (roomTypeId: number) => {
    if (!confirm('Bạn có chắc muốn xóa loại phòng này?')) return;

    try {
      await roomTypesAPI.delete(roomTypeId);
      toast.success('Đã xóa loại phòng');
      loadLocations();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể xóa');
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

      {/* Locations */}
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
        <div className="space-y-6">
          {locations.map((location) => (
            <div key={location.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-primary-100 flex items-center justify-center">
                    <Building2 className="w-7 h-7 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-gray-800">{location.name}</h3>
                    {location.address && (
                      <p className="text-gray-500 flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        {location.address}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => openEditModal(location)}
                    className="btn btn-secondary py-2 px-4"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(location)}
                    className="btn btn-danger py-2 px-4"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Owner info */}
              {(location.owner_name || location.owner_phone) && (
                <div className="flex flex-wrap gap-4 mb-4 text-sm">
                  {location.owner_name && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <User className="w-4 h-4" />
                      <span>Chủ trọ: {location.owner_name}</span>
                    </div>
                  )}
                  {location.owner_phone && (
                    <div className="flex items-center gap-2 text-gray-600">
                      <Phone className="w-4 h-4" />
                      <span>{location.owner_phone}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="p-3 bg-blue-50 rounded-xl">
                  <p className="text-sm text-blue-600">Tổng phòng</p>
                  <p className="text-2xl font-bold text-blue-700">{location.room_count}</p>
                </div>
                <div className="p-3 bg-emerald-50 rounded-xl">
                  <p className="text-sm text-emerald-600">Đang thuê</p>
                  <p className="text-2xl font-bold text-emerald-700">{location.occupied_count}</p>
                </div>
                <div className="p-3 bg-amber-50 rounded-xl">
                  <p className="text-sm text-amber-600">Giá điện</p>
                  <p className="text-lg font-bold text-amber-700">{formatCurrency(location.electric_price)}/kWh</p>
                </div>
                <div className="p-3 bg-cyan-50 rounded-xl">
                  <p className="text-sm text-cyan-600">Giá nước</p>
                  <p className="text-lg font-bold text-cyan-700">{formatCurrency(location.water_price)}/m³</p>
                </div>
              </div>

              {/* Fixed fees */}
              <div className="flex flex-wrap gap-3 mb-4 text-sm">
                {parseFloat(location.garbage_fee) > 0 && (
                  <span className="px-3 py-1 bg-gray-100 rounded-full">
                    Rác: {formatCurrency(location.garbage_fee)}
                  </span>
                )}
                {parseFloat(location.wifi_fee) > 0 && (
                  <span className="px-3 py-1 bg-gray-100 rounded-full">
                    Wifi: {formatCurrency(location.wifi_fee)}
                  </span>
                )}
                {parseFloat(location.tv_fee) > 0 && (
                  <span className="px-3 py-1 bg-gray-100 rounded-full">
                    TV: {formatCurrency(location.tv_fee)}
                  </span>
                )}
                {parseFloat(location.laundry_fee) > 0 && (
                  <span className="px-3 py-1 bg-gray-100 rounded-full">
                    Giặt: {formatCurrency(location.laundry_fee)}
                  </span>
                )}
                <span className="px-3 py-1 bg-gray-100 rounded-full">
                  Hạn nộp: ngày {location.payment_due_day}
                </span>
              </div>

              {/* Room Types */}
              <div className="border-t border-warm-100 pt-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold text-gray-700 flex items-center gap-2">
                    <Tag className="w-5 h-5" />
                    Loại phòng ({location.room_types?.length || 0})
                  </h4>
                  <button
                    onClick={() => openRoomTypeModal(location)}
                    className="text-sm text-primary-600 hover:underline"
                  >
                    + Thêm loại
                  </button>
                </div>
                
                {location.room_types && location.room_types.length > 0 ? (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {location.room_types.map((rt) => (
                      <div key={rt.id} className="p-3 bg-warm-50 rounded-xl relative group">
                        <button
                          onClick={() => handleDeleteRoomType(rt.id)}
                          className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="px-2 py-0.5 bg-primary-100 text-primary-700 rounded font-bold text-sm">
                            {rt.code}
                          </span>
                          <span className="text-sm text-gray-600">{rt.name}</span>
                        </div>
                        <p className="font-bold text-gray-800">{formatCurrency(rt.price)}</p>
                        <p className="text-xs text-gray-500">
                          Trừ {formatCurrency(rt.daily_deduction)}/ngày nghỉ
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400 text-sm">Chưa có loại phòng nào</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Location Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingLocation ? 'Sửa khu trọ' : 'Thêm khu trọ mới'}
        size="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Tên khu trọ *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="input"
                placeholder="VD: 68 Nguyễn Viết Xuân"
              />
            </div>
            <div>
              <label className="label">Địa chỉ</label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="input"
                placeholder="Địa chỉ đầy đủ"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Tên chủ trọ</label>
              <input
                type="text"
                value={formData.owner_name}
                onChange={(e) => setFormData({ ...formData, owner_name: e.target.value })}
                className="input"
                placeholder="Họ tên chủ trọ"
              />
            </div>
            <div>
              <label className="label">SĐT chủ trọ</label>
              <input
                type="text"
                value={formData.owner_phone}
                onChange={(e) => setFormData({ ...formData, owner_phone: e.target.value })}
                className="input"
                placeholder="0912345678"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
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
            <div>
              <label className="label">Hạn nộp (ngày)</label>
              <input
                type="number"
                value={formData.payment_due_day}
                onChange={(e) => setFormData({ ...formData, payment_due_day: e.target.value })}
                className="input"
                min="1"
                max="31"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="label">Tiền rác</label>
              <input
                type="number"
                value={formData.garbage_fee}
                onChange={(e) => setFormData({ ...formData, garbage_fee: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="label">Tiền wifi</label>
              <input
                type="number"
                value={formData.wifi_fee}
                onChange={(e) => setFormData({ ...formData, wifi_fee: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="label">Tiền TV</label>
              <input
                type="number"
                value={formData.tv_fee}
                onChange={(e) => setFormData({ ...formData, tv_fee: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="label">Tiền giặt</label>
              <input
                type="number"
                value={formData.laundry_fee}
                onChange={(e) => setFormData({ ...formData, laundry_fee: e.target.value })}
                className="input"
              />
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
              {saving ? 'Đang lưu...' : editingLocation ? 'Cập nhật' : 'Thêm mới'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Room Type Modal */}
      <Modal
        isOpen={roomTypeModalOpen}
        onClose={() => setRoomTypeModalOpen(false)}
        title={`Thêm loại phòng - ${selectedLocation?.name}`}
        size="sm"
      >
        <form onSubmit={handleAddRoomType} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Mã loại *</label>
              <input
                type="text"
                value={roomTypeForm.code}
                onChange={(e) => setRoomTypeForm({ ...roomTypeForm, code: e.target.value.toUpperCase() })}
                className="input"
                placeholder="A, B, C..."
                maxLength={3}
              />
            </div>
            <div>
              <label className="label">Tên</label>
              <input
                type="text"
                value={roomTypeForm.name}
                onChange={(e) => setRoomTypeForm({ ...roomTypeForm, name: e.target.value })}
                className="input"
                placeholder="Loại A"
              />
            </div>
          </div>

          <div>
            <label className="label">Giá thuê/tháng (VND) *</label>
            <input
              type="number"
              value={roomTypeForm.price}
              onChange={(e) => setRoomTypeForm({ ...roomTypeForm, price: e.target.value })}
              className="input"
              placeholder="2000000"
            />
          </div>

          <div>
            <label className="label">Tiền trừ/ngày nghỉ (VND)</label>
            <input
              type="number"
              value={roomTypeForm.daily_deduction}
              onChange={(e) => setRoomTypeForm({ ...roomTypeForm, daily_deduction: e.target.value })}
              className="input"
              placeholder="66000"
            />
            <p className="text-sm text-gray-500 mt-1">
              Số tiền trừ khi người thuê nghỉ 1 ngày
            </p>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={() => setRoomTypeModalOpen(false)}
              className="flex-1 btn btn-secondary"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 btn btn-primary"
            >
              {saving ? 'Đang lưu...' : 'Thêm'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
