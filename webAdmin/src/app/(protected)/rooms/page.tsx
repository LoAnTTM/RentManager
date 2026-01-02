'use client';

import React, { useState, useEffect } from 'react';
import { roomsAPI, locationsAPI } from '@/lib/api';
import { formatCurrency, roomStatusLabels } from '@/lib/utils';
import Loading from '@/components/Loading';
import EmptyState from '@/components/EmptyState';
import Modal from '@/components/Modal';
import toast from 'react-hot-toast';
import { DoorOpen, Plus, Edit2, Trash2, Users, Building2 } from 'lucide-react';

interface Location {
  id: number;
  name: string;
}

interface Tenant {
  id: number;
  full_name: string;
  phone: string;
  is_active: boolean;
}

interface Room {
  id: number;
  location_id: number;
  room_code: string;
  price: string;
  status: 'vacant' | 'occupied';
  notes: string;
  location?: { id: number; name: string };
  tenants?: Tenant[];
}

export default function RoomsPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterLocation, setFilterLocation] = useState<number | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const [formData, setFormData] = useState({
    location_id: '',
    room_code: '',
    price: '',
    notes: '',
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadData();
  }, [filterLocation, filterStatus]);

  const loadData = async () => {
    try {
      const [roomsRes, locationsRes] = await Promise.all([
        roomsAPI.getAll({
          location_id: filterLocation || undefined,
          status: filterStatus || undefined,
        }),
        locationsAPI.getAll(),
      ]);
      setRooms(roomsRes.data);
      setLocations(locationsRes.data);
    } catch (error) {
      toast.error('Không thể tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const openCreateModal = () => {
    setEditingRoom(null);
    setFormData({
      location_id: locations[0]?.id?.toString() || '',
      room_code: '',
      price: '2000000',
      notes: '',
    });
    setModalOpen(true);
  };

  const openEditModal = (room: Room) => {
    setEditingRoom(room);
    setFormData({
      location_id: room.location_id.toString(),
      room_code: room.room_code,
      price: room.price,
      notes: room.notes || '',
    });
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.location_id || !formData.room_code || !formData.price) {
      toast.error('Vui lòng điền đầy đủ thông tin');
      return;
    }

    setSaving(true);
    try {
      const data = {
        ...formData,
        location_id: parseInt(formData.location_id),
        price: formData.price,
      };

      if (editingRoom) {
        await roomsAPI.update(editingRoom.id, {
          room_code: data.room_code,
          price: data.price,
          notes: data.notes,
        });
        toast.success('Đã cập nhật phòng');
      } else {
        await roomsAPI.create(data);
        toast.success('Đã thêm phòng mới');
      }
      setModalOpen(false);
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (room: Room) => {
    if (!confirm(`Bạn có chắc muốn xóa phòng ${room.room_code}?`)) return;

    try {
      await roomsAPI.delete(room.id);
      toast.success('Đã xóa phòng');
      loadData();
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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Phòng trọ</h1>
          <p className="text-gray-500 mt-1">Quản lý các phòng trong khu trọ</p>
        </div>
        <button onClick={openCreateModal} className="btn btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          <span>Thêm phòng mới</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
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
          <option value="occupied">Đang thuê</option>
          <option value="vacant">Phòng trống</option>
        </select>
      </div>

      {/* Rooms grid */}
      {rooms.length === 0 ? (
        <EmptyState
          icon={<DoorOpen className="w-10 h-10" />}
          title="Chưa có phòng nào"
          description="Thêm phòng đầu tiên để bắt đầu quản lý"
          action={
            <button onClick={openCreateModal} className="btn btn-primary">
              Thêm phòng
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {rooms.map((room) => (
            <div
              key={room.id}
              className={`card hover:shadow-md transition-shadow ${
                room.status === 'vacant' ? 'border-amber-200 bg-amber-50/30' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-xl font-bold text-gray-800">
                    Phòng {room.room_code}
                  </h3>
                  <p className="text-sm text-gray-500 flex items-center gap-1">
                    <Building2 className="w-4 h-4" />
                    {room.location?.name}
                  </p>
                </div>
                <span
                  className={`badge ${
                    room.status === 'occupied' ? 'badge-success' : 'badge-warning'
                  }`}
                >
                  {roomStatusLabels[room.status]}
                </span>
              </div>

              <div className="mb-4">
                <p className="text-2xl font-bold text-primary-600">
                  {formatCurrency(room.price)}
                </p>
                <p className="text-sm text-gray-500">/tháng</p>
              </div>

              {room.tenants && room.tenants.length > 0 && (
                <div className="mb-4 p-3 bg-warm-50 rounded-xl">
                  <p className="text-sm text-gray-500 mb-2 flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    Người thuê:
                  </p>
                  {room.tenants.map((tenant) => (
                    <p key={tenant.id} className="font-medium text-gray-800">
                      {tenant.full_name}
                    </p>
                  ))}
                </div>
              )}

              <div className="flex gap-2 pt-3 border-t border-warm-100">
                <button
                  onClick={() => openEditModal(room)}
                  className="flex-1 btn btn-secondary py-2 flex items-center justify-center gap-2"
                >
                  <Edit2 className="w-4 h-4" />
                  Sửa
                </button>
                <button
                  onClick={() => handleDelete(room)}
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
        title={editingRoom ? 'Sửa thông tin phòng' : 'Thêm phòng mới'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {!editingRoom && (
            <div>
              <label className="label">Khu trọ *</label>
              <select
                value={formData.location_id}
                onChange={(e) => setFormData({ ...formData, location_id: e.target.value })}
                className="input"
              >
                <option value="">Chọn khu trọ</option>
                {locations.map((loc) => (
                  <option key={loc.id} value={loc.id}>
                    {loc.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div>
            <label className="label">Mã phòng *</label>
            <input
              type="text"
              value={formData.room_code}
              onChange={(e) => setFormData({ ...formData, room_code: e.target.value })}
              className="input"
              placeholder="VD: 101, 102, A01..."
            />
          </div>

          <div>
            <label className="label">Giá phòng (VND/tháng) *</label>
            <input
              type="number"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              className="input"
              placeholder="2000000"
            />
          </div>

          <div>
            <label className="label">Ghi chú</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="input min-h-[100px]"
              placeholder="Ghi chú thêm về phòng..."
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
              {saving ? 'Đang lưu...' : editingRoom ? 'Cập nhật' : 'Thêm mới'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

