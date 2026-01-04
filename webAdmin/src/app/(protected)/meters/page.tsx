'use client';

import React, { useState, useEffect } from 'react';
import { metersAPI, roomsAPI, locationsAPI } from '@/lib/api';
import { formatNumber, getCurrentPeriod, getMonthName } from '@/lib/utils';
import Loading from '@/components/Loading';
import toast from 'react-hot-toast';
import { Zap, Droplets, Save, ChevronLeft, ChevronRight } from 'lucide-react';

interface Location {
  id: number;
  name: string;
}

interface Room {
  id: number;
  room_code: string;
  location_id: number;
  status: string;
}

interface Meter {
  id: number;
  room_id: number;
  meter_type: 'electric' | 'water';
  latest_reading: string | null;
}

interface MeterReading {
  id: number;
  meter_id: number;
  month: number;
  year: number;
  old_reading: string;
  new_reading: string;
  consumption: string;
}

interface RoomReadings {
  room: Room;
  electric: {
    meter_id: number;
    old_reading: string;
    new_reading: string;
    consumption: string;
    reading_id?: number;
  } | null;
  water: {
    meter_id: number;
    old_reading: string;
    new_reading: string;
    consumption: string;
    reading_id?: number;
  } | null;
}

export default function MetersPage() {
  const { month: currentMonth, year: currentYear } = getCurrentPeriod();
  const [month, setMonth] = useState(currentMonth);
  const [year, setYear] = useState(currentYear);
  const [locations, setLocations] = useState<Location[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [meters, setMeters] = useState<Meter[]>([]);
  const [readings, setReadings] = useState<MeterReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [filterLocation, setFilterLocation] = useState<number | null>(null);

  // Form state for each room
  const [formReadings, setFormReadings] = useState<Record<number, {
    electric_old: string;
    electric_new: string;
    water_old: string;
    water_new: string;
  }>>({});

  useEffect(() => {
    loadData();
  }, [month, year, filterLocation]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [locationsRes, roomsRes, metersRes, readingsRes] = await Promise.all([
        locationsAPI.getAll(),
        roomsAPI.getAll({ location_id: filterLocation || undefined }),
        metersAPI.getAll(),
        metersAPI.getReadings({ month, year }),
      ]);

      setLocations(locationsRes.data);
      setRooms(roomsRes.data.filter((r: Room) => r.status === 'occupied'));
      setMeters(metersRes.data);
      setReadings(readingsRes.data);

      // Initialize form readings
      const initialReadings: Record<number, any> = {};
      roomsRes.data.filter((r: Room) => r.status === 'occupied').forEach((room: Room) => {
        const electricMeter = metersRes.data.find(
          (m: Meter) => m.room_id === room.id && m.meter_type === 'electric'
        );
        const waterMeter = metersRes.data.find(
          (m: Meter) => m.room_id === room.id && m.meter_type === 'water'
        );

        const electricReading = readingsRes.data.find(
          (r: MeterReading) => r.meter_id === electricMeter?.id
        );
        const waterReading = readingsRes.data.find(
          (r: MeterReading) => r.meter_id === waterMeter?.id
        );

        initialReadings[room.id] = {
          electric_old: electricReading?.old_reading || electricMeter?.latest_reading || '0',
          electric_new: electricReading?.new_reading || '',
          water_old: waterReading?.old_reading || waterMeter?.latest_reading || '0',
          water_new: waterReading?.new_reading || '',
        };
      });
      setFormReadings(initialReadings);
    } catch (error) {
      toast.error('Không thể tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (roomId: number, field: string, value: string) => {
    setFormReadings((prev) => ({
      ...prev,
      [roomId]: {
        ...prev[roomId],
        [field]: value,
      },
    }));
  };

  const handleSaveAll = async () => {
    setSaving(true);
    try {
      const batchItems: any[] = [];

      Object.entries(formReadings).forEach(([roomIdStr, values]) => {
        const roomId = parseInt(roomIdStr);
        
        if (values.electric_new) {
          batchItems.push({
            room_id: roomId,
            meter_type: 'electric',
            old_reading: values.electric_old || '0',
            new_reading: values.electric_new,
          });
        }
        
        if (values.water_new) {
          batchItems.push({
            room_id: roomId,
            meter_type: 'water',
            old_reading: values.water_old || '0',
            new_reading: values.water_new,
          });
        }
      });

      if (batchItems.length === 0) {
        toast.error('Chưa nhập chỉ số nào');
        return;
      }

      await metersAPI.createReadingsBatch({
        month,
        year,
        readings: batchItems,
      });

      toast.success(`Đã lưu ${batchItems.length} chỉ số`);
      loadData();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Có lỗi xảy ra');
    } finally {
      setSaving(false);
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

  const getConsumption = (oldVal: string, newVal: string) => {
    if (!oldVal || !newVal) return '-';
    const consumption = parseFloat(newVal) - parseFloat(oldVal);
    return consumption >= 0 ? formatNumber(consumption) : '-';
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Điện nước</h1>
          <p className="text-gray-500 mt-1">Ghi chỉ số điện nước hàng tháng</p>
        </div>
        <button
          onClick={handleSaveAll}
          disabled={saving}
          className="btn btn-primary flex items-center gap-2"
        >
          <Save className="w-5 h-5" />
          <span>{saving ? 'Đang lưu...' : 'Lưu tất cả'}</span>
        </button>
      </div>

      {/* Month selector and filter */}
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
      </div>

      {/* Readings table */}
      {rooms.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500 text-lg">Không có phòng đang thuê</p>
        </div>
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="table-header">
                <th className="table-cell rounded-tl-xl">Phòng</th>
                <th className="table-cell text-center" colSpan={3}>
                  <div className="flex items-center justify-center gap-2">
                    <Zap className="w-5 h-5 text-amber-500" />
                    <span>Điện (kWh)</span>
                  </div>
                </th>
                <th className="table-cell text-center rounded-tr-xl" colSpan={3}>
                  <div className="flex items-center justify-center gap-2">
                    <Droplets className="w-5 h-5 text-blue-500" />
                    <span>Nước (m³)</span>
                  </div>
                </th>
              </tr>
              <tr className="table-header text-sm">
                <th className="table-cell"></th>
                <th className="table-cell text-center">Số cũ</th>
                <th className="table-cell text-center">Số mới</th>
                <th className="table-cell text-center">Tiêu thụ</th>
                <th className="table-cell text-center">Số cũ</th>
                <th className="table-cell text-center">Số mới</th>
                <th className="table-cell text-center">Tiêu thụ</th>
              </tr>
            </thead>
            <tbody>
              {rooms.map((room) => {
                const values = formReadings[room.id] || {
                  electric_old: '0',
                  electric_new: '',
                  water_old: '0',
                  water_new: '',
                };

                return (
                  <tr key={room.id} className="hover:bg-warm-50">
                    <td className="table-cell font-medium">
                      Phòng {room.room_code}
                    </td>
                    <td className="table-cell text-center">
                      <input
                        type="number"
                        value={values.electric_old}
                        onChange={(e) =>
                          handleInputChange(room.id, 'electric_old', e.target.value)
                        }
                        className="w-24 px-2 py-1 text-center border border-warm-200 rounded-lg"
                      />
                    </td>
                    <td className="table-cell text-center">
                      <input
                        type="number"
                        value={values.electric_new}
                        onChange={(e) =>
                          handleInputChange(room.id, 'electric_new', e.target.value)
                        }
                        className="w-24 px-2 py-1 text-center border-2 border-amber-300 rounded-lg focus:border-amber-500 focus:outline-none"
                        placeholder="..."
                      />
                    </td>
                    <td className="table-cell text-center font-medium text-amber-600">
                      {getConsumption(values.electric_old, values.electric_new)}
                    </td>
                    <td className="table-cell text-center">
                      <input
                        type="number"
                        value={values.water_old}
                        onChange={(e) =>
                          handleInputChange(room.id, 'water_old', e.target.value)
                        }
                        className="w-24 px-2 py-1 text-center border border-warm-200 rounded-lg"
                      />
                    </td>
                    <td className="table-cell text-center">
                      <input
                        type="number"
                        value={values.water_new}
                        onChange={(e) =>
                          handleInputChange(room.id, 'water_new', e.target.value)
                        }
                        className="w-24 px-2 py-1 text-center border-2 border-blue-300 rounded-lg focus:border-blue-500 focus:outline-none"
                        placeholder="..."
                      />
                    </td>
                    <td className="table-cell text-center font-medium text-blue-600">
                      {getConsumption(values.water_old, values.water_new)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Instructions */}
      <div className="card bg-warm-50 border-warm-200">
        <h3 className="font-semibold text-gray-700 mb-2">📝 Hướng dẫn</h3>
        <ul className="text-gray-600 space-y-1 list-disc list-inside">
          <li>Nhập chỉ số mới vào ô có viền màu</li>
          <li>Số tiêu thụ sẽ tự động tính</li>
          <li>Nhấn &quot;Lưu tất cả&quot; để lưu toàn bộ chỉ số</li>
          <li>Sau khi lưu, có thể tạo hóa đơn ở trang Hóa đơn</li>
        </ul>
      </div>
    </div>
  );
}

