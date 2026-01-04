"""
Seed data for testing - Dữ liệu mẫu theo cấu trúc file Excel thực tế
"""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.location import Location
from app.models.room_type import RoomType
from app.models.room import Room, RoomStatus
from app.models.tenant import Tenant
from app.models.meter import Meter, MeterReading, MeterType
from app.models.invoice import Invoice, InvoiceStatus
from app.models.expense import Expense, ExpenseCategory


def seed_database():
    """Seed database with sample data based on Excel file structure"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already seeded. Skipping...")
            return
        
        print("Seeding database...")
        
        # ============ USERS ============
        print("Creating users...")
        admin = User(
            email="cominh@gmail.com",
            hashed_password=get_password_hash("123456"),
            full_name="Lê Thị Kim Minh",
            is_active=True
        )
        db.add(admin)
        db.flush()
        
        # ============ LOCATION ============
        print("Creating location...")
        location = Location(
            name="68 Nguyễn Viết Xuân",
            address="68 Nguyễn Viết Xuân, TP Đà Nẵng",
            owner_name="Lê Thị Kim Minh",
            owner_phone="0932567812 - 0905123641",
            electric_price=Decimal("3500"),  # 3.5k/kWh (3.5 trong Excel)
            water_price=Decimal("8000"),  # 8k/m3
            garbage_fee=Decimal("30000"),  # 30k
            wifi_fee=Decimal("0"),
            tv_fee=Decimal("0"),
            laundry_fee=Decimal("0"),
            payment_due_day=5,
            notes="Nhà trọ chính"
        )
        db.add(location)
        db.flush()
        
        # ============ ROOM TYPES ============
        print("Creating room types...")
        # Theo bảng giá trong Excel
        room_types_data = [
            {"code": "A", "name": "Loại A", "price": Decimal("1800000"), "daily_deduction": Decimal("60000")},
            {"code": "B", "name": "Loại B", "price": Decimal("2700000"), "daily_deduction": Decimal("90000")},
            {"code": "C", "name": "Loại C", "price": Decimal("2600000"), "daily_deduction": Decimal("86000")},
            {"code": "D", "name": "Loại D", "price": Decimal("2500000"), "daily_deduction": Decimal("83000")},
            {"code": "E", "name": "Loại E", "price": Decimal("2300000"), "daily_deduction": Decimal("76000")},
            {"code": "F", "name": "Loại F", "price": Decimal("2200000"), "daily_deduction": Decimal("73000")},
            {"code": "G", "name": "Loại G", "price": Decimal("2000000"), "daily_deduction": Decimal("66000")},
            {"code": "H", "name": "Loại H", "price": Decimal("2400000"), "daily_deduction": Decimal("80000")},
        ]
        
        room_types = {}
        for rt_data in room_types_data:
            rt = RoomType(location_id=location.id, **rt_data)
            db.add(rt)
            db.flush()
            room_types[rt_data["code"]] = rt
        
        # ============ ROOMS ============
        print("Creating rooms...")
        # Theo danh sách phòng trong Excel
        rooms_data = [
            # Tầng 1
            {"room_code": "101", "room_type": "D"},
            {"room_code": "102", "room_type": "D"},
            {"room_code": "103", "room_type": "F"},
            # Tầng 2
            {"room_code": "201", "room_type": "C"},
            {"room_code": "202", "room_type": "C"},
            {"room_code": "203", "room_type": "F"},
            {"room_code": "204", "room_type": "F"},
            {"room_code": "205", "room_type": "F"},
            {"room_code": "206", "room_type": "F"},
            # Tầng 3
            {"room_code": "301", "room_type": "D"},
            {"room_code": "302", "room_type": "D"},
            {"room_code": "303", "room_type": "G"},
            {"room_code": "304", "room_type": "G"},
            {"room_code": "305", "room_type": "G"},
            {"room_code": "306", "room_type": "G"},
            # Tầng 4
            {"room_code": "401", "room_type": "D"},
            {"room_code": "402", "room_type": "D"},
            {"room_code": "403", "room_type": "G"},
            {"room_code": "404", "room_type": "G"},
            {"room_code": "405", "room_type": "G"},
            {"room_code": "406", "room_type": "G"},
            # Tầng 5
            {"room_code": "501", "room_type": "G"},
            # Phòng số
            {"room_code": "số1", "room_type": "D"},
            {"room_code": "số2", "room_type": "F"},
            {"room_code": "số3", "room_type": "E"},
            {"room_code": "số4", "room_type": "D"},
            {"room_code": "số5", "room_type": "E"},
            {"room_code": "số6", "room_type": "F"},
            {"room_code": "số7", "room_type": "D"},
        ]
        
        rooms = []
        for room_data in rooms_data:
            rt = room_types[room_data["room_type"]]
            room = Room(
                location_id=location.id,
                room_type_id=rt.id,
                room_code=room_data["room_code"],
                status=RoomStatus.VACANT
            )
            db.add(room)
            rooms.append(room)
        db.flush()
        
        # ============ METERS ============
        print("Creating meters...")
        # Dữ liệu đồng hồ từ Excel
        electric_readings = {
            "101": 8049, "102": 14887, "103": 7196, "201": 8977, "202": 12159,
            "203": 6228, "204": 7453, "205": 7565, "206": 6393, "301": 8691,
            "302": 4663, "303": 6066, "304": 7735, "305": 5738, "306": 6524,
            "401": 5533, "402": 8593, "403": 6300, "404": 5966, "405": 3433,
            "406": 4690, "501": 3231, "số1": 835, "số2": 1096, "số3": 258,
            "số4": 381, "số5": 336, "số6": 361, "số7": 708
        }
        
        water_readings = {
            "101": 260, "102": 408, "103": 268, "201": 599, "202": 421,
            "203": 190, "204": 337, "205": 226, "206": 295, "301": 287,
            "302": 214, "303": 295, "304": 342, "305": 296, "306": 204,
            "401": 375, "402": 371, "403": 343, "404": 289, "405": 193,
            "406": 248, "501": 145, "số1": 29, "số2": 23, "số3": 16,
            "số4": 9, "số5": 19, "số6": 26, "số7": 21
        }
        
        for room in rooms:
            # Electric meter
            e_meter = Meter(room_id=room.id, meter_type=MeterType.ELECTRIC)
            db.add(e_meter)
            # Water meter
            w_meter = Meter(room_id=room.id, meter_type=MeterType.WATER)
            db.add(w_meter)
        db.flush()
        
        # ============ TENANTS ============
        print("Creating tenants...")
        # Tạo người thuê cho tất cả các phòng (giả định tất cả đang thuê)
        tenant_names = [
            "Nguyễn Văn An", "Trần Thị Bình", "Lê Văn Cường", "Phạm Thị Dung",
            "Hoàng Văn Em", "Vũ Thị Phương", "Đặng Văn Giang", "Bùi Văn Hùng",
            "Ngô Thị Lan", "Đỗ Văn Minh", "Phan Văn Nam", "Lý Thị Oanh",
            "Trương Văn Phú", "Đinh Thị Quỳnh", "Mai Văn Rồng", "Hồ Thị Sen",
            "Dương Văn Tài", "Cao Thị Uyên", "Lưu Văn Vinh", "Châu Thị Xuyến",
            "Tạ Văn Yên", "Võ Thị Zung", "Nguyễn Thị Ánh", "Trần Văn Bảo",
            "Lê Thị Cẩm", "Phạm Văn Đức", "Hoàng Thị Hà", "Vũ Văn Khải",
            "Đặng Thị Loan"
        ]
        
        for i, room in enumerate(rooms):
            tenant = Tenant(
                room_id=room.id,
                full_name=tenant_names[i % len(tenant_names)],
                phone=f"090{1000000 + i:07d}",
                id_card=f"0791234{56000 + i:05d}",
                move_in_date=date(2024, 1 + (i % 12), 1),
                is_active=True
            )
            db.add(tenant)
            room.status = RoomStatus.OCCUPIED
        db.flush()
        
        # ============ METER READINGS ============
        print("Creating meter readings...")
        meters = db.query(Meter).all()
        
        for meter in meters:
            room = db.query(Room).filter(Room.id == meter.room_id).first()
            room_code = room.room_code
            
            if meter.meter_type == MeterType.ELECTRIC:
                current_reading = electric_readings.get(room_code, 0)
                # Tháng 12/2025 - giả sử tiêu thụ 100-150 kWh
                consumption = 120  # Trung bình
                old_reading = current_reading - consumption
            else:
                current_reading = water_readings.get(room_code, 0)
                # Tháng 12/2025 - giả sử tiêu thụ 5-10 m3
                consumption = 8
                old_reading = current_reading - consumption
            
            reading = MeterReading(
                meter_id=meter.id,
                month=1,
                year=2026,
                old_reading=Decimal(str(old_reading)),
                new_reading=Decimal(str(current_reading)),
                consumption=Decimal(str(consumption))
            )
            db.add(reading)
        db.flush()
        
        # ============ INVOICES ============
        print("Creating invoices...")
        for room in rooms:
            rt = db.query(RoomType).filter(RoomType.id == room.room_type_id).first()
            room_fee = rt.price
            
            # Get electric reading
            electric_meter = db.query(Meter).filter(
                Meter.room_id == room.id,
                Meter.meter_type == MeterType.ELECTRIC
            ).first()
            electric_reading = db.query(MeterReading).filter(
                MeterReading.meter_id == electric_meter.id,
                MeterReading.month == 1,
                MeterReading.year == 2026
            ).first()
            electric_fee = electric_reading.consumption * location.electric_price if electric_reading else Decimal("0")
            
            # Get water reading
            water_meter = db.query(Meter).filter(
                Meter.room_id == room.id,
                Meter.meter_type == MeterType.WATER
            ).first()
            water_reading = db.query(MeterReading).filter(
                MeterReading.meter_id == water_meter.id,
                MeterReading.month == 1,
                MeterReading.year == 2026
            ).first()
            water_fee = water_reading.consumption * location.water_price if water_reading else Decimal("0")
            
            # Calculate total
            total = room_fee + electric_fee + water_fee + location.garbage_fee
            
            # Random status
            room_idx = rooms.index(room)
            if room_idx % 3 == 0:
                status = InvoiceStatus.PAID
                paid_amount = total
            elif room_idx % 3 == 1:
                status = InvoiceStatus.PARTIAL
                paid_amount = room_fee
            else:
                status = InvoiceStatus.UNPAID
                paid_amount = Decimal("0")
            
            invoice = Invoice(
                room_id=room.id,
                month=1,
                year=2026,
                room_fee=room_fee,
                absent_days=0,
                absent_deduction=Decimal("0"),
                electric_fee=electric_fee,
                water_fee=water_fee,
                garbage_fee=location.garbage_fee,
                wifi_fee=Decimal("0"),
                tv_fee=Decimal("0"),
                laundry_fee=Decimal("0"),
                other_fee=Decimal("0"),
                previous_debt=Decimal("0"),
                previous_credit=Decimal("0"),
                total=total,
                paid_amount=paid_amount,
                remaining_debt=total - paid_amount if paid_amount < total else Decimal("0"),
                remaining_credit=paid_amount - total if paid_amount > total else Decimal("0"),
                status=status
            )
            db.add(invoice)
        db.flush()
        
        # ============ EXPENSES ============
        print("Creating expenses...")
        expenses_data = [
            {"category": ExpenseCategory.REPAIR, "description": "Sửa ống nước phòng 303", "amount": Decimal("500000"), "expense_date": date(2026, 1, 5)},
            {"category": ExpenseCategory.UTILITY, "description": "Tiền điện khu vực chung", "amount": Decimal("350000"), "expense_date": date(2026, 1, 10)},
            {"category": ExpenseCategory.MAINTENANCE, "description": "Vệ sinh bể nước", "amount": Decimal("800000"), "expense_date": date(2026, 1, 15)},
            {"category": ExpenseCategory.REPAIR, "description": "Thay bóng đèn hành lang", "amount": Decimal("200000"), "expense_date": date(2026, 1, 20)},
        ]
        
        for exp_data in expenses_data:
            expense = Expense(location_id=location.id, **exp_data)
            db.add(expense)
        
        db.commit()
        print("✅ Database seeded successfully!")
        
        # Print summary
        print("\n📊 Summary:")
        print(f"   - Users: {db.query(User).count()}")
        print(f"   - Locations: {db.query(Location).count()}")
        print(f"   - Room Types: {db.query(RoomType).count()}")
        print(f"   - Rooms: {db.query(Room).count()}")
        print(f"   - Tenants: {db.query(Tenant).count()}")
        print(f"   - Meters: {db.query(Meter).count()}")
        print(f"   - Meter Readings: {db.query(MeterReading).count()}")
        print(f"   - Invoices: {db.query(Invoice).count()}")
        print(f"   - Expenses: {db.query(Expense).count()}")
        print("\n🔐 Login credentials:")
        print("   Email: cominh@gmail.com")
        print("   Password: 123456")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
