'use client';

import React, { useState, useEffect } from 'react';
import { roomsAPI, locationsAPI, roomTypesAPI } from '@/lib/api';
import { formatCurrency, roomStatusLabels } from '@/lib/utils';
import Loading from '@/components/Loading';
import EmptyState from '@/components/EmptyState';
import Modal from '@/components/Modal';
import toast from 'react-hot-toast';
import { DoorOpen, Plus, Edit2, Trash2, Users, Building2, Tag } from 'lucide-react';

interface Location {
  id: number;
  name: string;
}

interface RoomType {
  id: number;
  code: string;
  name: string;
  price: string;
  daily_deduction: string;
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
  room_type_id: number | null;
  room_code: string;
  price: string | null;
  status: 'vacant' | 'occupied';
  notes: string;
  effective_price: string;
  location?: { id: number; name: string };
  room_type?: RoomType;
  tenants?: Tenant[];
}

export default function RoomsPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [roomTypes, setRoomTypes] = useState<RoomType[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterLocation, setFilterLocation] = useState<number | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);
  const [filterRoomType, setFilterRoomType] = useState<number | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const [formData, setFormData] = useState({
    location_id: '',
    room_type_id: '',
    room_code: '',
    price: '',
    notes: '',
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadData();
  }, [filterLocation, filterStatus, filterRoomType]);

  useEffect(() => {
    // Load room types when location changes
    if (formData.location_id) {
      loadRoomTypes(parseInt(formData.location_id));
    }
  }, [formData.location_id]);

  const loadData = async () => {
    try {
      const [roomsRes, locationsRes] = await Promise.all([
        roomsAPI.getAll({
          location_id: filterLocation || undefined,
          room_type_id: filterRoomType || undefined,
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

  const loadRoomTypes = async (locationId: number) => {
    try {
      const res = await roomTypesAPI.getAll({ location_id: locationId });
      setRoomTypes(res.data);
    } catch (error) {
      console.error('Error loading room types:', error);
    }
  };

  const openCreateModal = () => {
    setEditingRoom(null);
    const defaultLocation = filterLocation || locations[0]?.id || '';
    setFormData({
      location_id: defaultLocation.toString(),
      room_type_id: '',
      room_code: '',
      price: '',
      notes: '',
    });
    if (defaultLocation) {
      loadRoomTypes(Number(defaultLocation));
    }
    setModalOpen(true);
  };

  const openEditModal = (room: Room) => {
    setEditingRoom(room);
    setFormData({
      location_id: room.location_id.toString(),
      room_type_id: room.room_type_id?.toString() || '',
      room_code: room.room_code,
      price: room.price || '',
      notes: room.notes || '',
    });
    loadRoomTypes(room.location_id);
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.location_id || !formData.room_code) {
      toast.error('Vui lòng điền đầy đủ thông tin');
      return;
    }

    setSaving(true);
    try {
      const data = {
        location_id: parseInt(formData.location_id),
        room_type_id: formData.room_type_id ? parseInt(formData.room_type_id) : null,
        room_code: formData.room_code,
        price: formData.price || null,
        notes: formData.notes,
      };

      if (editingRoom) {
        await roomsAPI.update(editingRoom.id, {
          room_type_id: data.room_type_id,
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
          onChange={(e) => {
            setFilterLocation(e.target.value ? parseInt(e.target.value) : null);
            setFilterRoomType(null);
          }}
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

              {/* Room type */}
              {room.room_type && (
                <div className="flex items-center gap-2 mb-3">
                  <Tag className="w-4 h-4 text-gray-400" />
                  <span className="px-2 py-0.5 bg-primary-100 text-primary-700 rounded text-sm font-medium">
                    Loại {room.room_type.code}
                  </span>
                  <span className="text-sm text-gray-500">{room.room_type.name}</span>
                </div>
              )}

              <div className="mb-4">
                <p className="text-2xl font-bold text-primary-600">
                  {formatCurrency(room.effective_price || room.price || '0')}
                </p>
                <p className="text-sm text-gray-500">/tháng</p>
                {room.price && room.room_type && (
                  <p className="text-xs text-gray-400">(Giá riêng)</p>
                )}
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
                onChange={(e) => setFormData({ ...formData, location_id: e.target.value, room_type_id: '' })}
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
            <label className="label">Loại phòng</label>
            <select
              value={formData.room_type_id}
              onChange={(e) => setFormData({ ...formData, room_type_id: e.target.value })}
              className="input"
            >
              <option value="">-- Không chọn --</option>
              {roomTypes.map((rt) => (
                <option key={rt.id} value={rt.id}>
                  Loại {rt.code} - {formatCurrency(rt.price)}
                </option>
              ))}
            </select>
            <p className="text-sm text-gray-500 mt-1">
              Chọn loại phòng để lấy giá tự động
            </p>
          </div>

          <div>
            <label className="label">Mã phòng *</label>
            <input
              type="text"
              value={formData.room_code}
              onChange={(e) => setFormData({ ...formData, room_code: e.target.value })}
              className="input"
              placeholder="VD: 101, 102, số1..."
            />
          </div>

          <div>
            <label className="label">Giá riêng (nếu khác loại phòng)</label>
            <input
              type="number"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              className="input"
              placeholder="Để trống nếu dùng giá loại phòng"
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
