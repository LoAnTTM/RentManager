"""
Seed data for testing - Dữ liệu mẫu
"""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.location import Location
from app.models.room import Room, RoomStatus
from app.models.tenant import Tenant
from app.models.meter import Meter, MeterReading, MeterType
from app.models.invoice import Invoice, InvoiceStatus
from app.models.expense import Expense, ExpenseCategory


def seed_database():
    """Seed database with sample data"""
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
            full_name="Cô Minh",
            is_active=True
        )
        db.add(admin)
        db.flush()
        
        # ============ LOCATIONS ============
        print("Creating locations...")
        locations = [
            Location(
                name="Khu A",
                address="123 Đường Nguyễn Văn A, Quận 1",
                electric_price=Decimal("3500"),
                water_price=Decimal("15000"),
                notes="Khu trọ chính, gần chợ"
            ),
            Location(
                name="Khu B",
                address="456 Đường Trần Văn B, Quận 2",
                electric_price=Decimal("3500"),
                water_price=Decimal("15000"),
                notes="Khu trọ mới xây"
            ),
            Location(
                name="Khu C",
                address="789 Đường Lê Văn C, Quận 3",
                electric_price=Decimal("3800"),
                water_price=Decimal("18000"),
                notes="Khu cao cấp"
            ),
        ]
        for loc in locations:
            db.add(loc)
        db.flush()
        
        # ============ ROOMS ============
        print("Creating rooms...")
        rooms_data = [
            # Khu A - 5 phòng
            {"location_id": 1, "room_code": "A101", "price": Decimal("2000000")},
            {"location_id": 1, "room_code": "A102", "price": Decimal("2000000")},
            {"location_id": 1, "room_code": "A103", "price": Decimal("2200000")},
            {"location_id": 1, "room_code": "A201", "price": Decimal("2500000")},
            {"location_id": 1, "room_code": "A202", "price": Decimal("2500000")},
            # Khu B - 5 phòng
            {"location_id": 2, "room_code": "B101", "price": Decimal("1800000")},
            {"location_id": 2, "room_code": "B102", "price": Decimal("1800000")},
            {"location_id": 2, "room_code": "B103", "price": Decimal("2000000")},
            {"location_id": 2, "room_code": "B201", "price": Decimal("2200000")},
            {"location_id": 2, "room_code": "B202", "price": Decimal("2200000")},
            # Khu C - 5 phòng
            {"location_id": 3, "room_code": "C101", "price": Decimal("3000000")},
            {"location_id": 3, "room_code": "C102", "price": Decimal("3000000")},
            {"location_id": 3, "room_code": "C103", "price": Decimal("3200000")},
            {"location_id": 3, "room_code": "C201", "price": Decimal("3500000")},
            {"location_id": 3, "room_code": "C202", "price": Decimal("3500000")},
        ]
        
        rooms = []
        for room_data in rooms_data:
            room = Room(**room_data, status=RoomStatus.VACANT)
            db.add(room)
            rooms.append(room)
        db.flush()
        
        # ============ METERS ============
        print("Creating meters...")
        for room in rooms:
            # Electric meter
            db.add(Meter(room_id=room.id, meter_type=MeterType.ELECTRIC))
            # Water meter
            db.add(Meter(room_id=room.id, meter_type=MeterType.WATER))
        db.flush()
        
        # ============ TENANTS ============
        print("Creating tenants...")
        tenants_data = [
            # Khu A
            {"room_id": 1, "full_name": "Nguyễn Văn An", "phone": "0901234001", "id_card": "079123456001", "move_in_date": date(2024, 6, 1)},
            {"room_id": 2, "full_name": "Trần Thị Bình", "phone": "0901234002", "id_card": "079123456002", "move_in_date": date(2024, 7, 15)},
            {"room_id": 3, "full_name": "Lê Văn Cường", "phone": "0901234003", "id_card": "079123456003", "move_in_date": date(2024, 8, 1)},
            {"room_id": 4, "full_name": "Phạm Thị Dung", "phone": "0901234004", "id_card": "079123456004", "move_in_date": date(2024, 5, 1)},
            # Khu B
            {"room_id": 6, "full_name": "Hoàng Văn Em", "phone": "0901234005", "id_card": "079123456005", "move_in_date": date(2024, 9, 1)},
            {"room_id": 7, "full_name": "Vũ Thị Phương", "phone": "0901234006", "id_card": "079123456006", "move_in_date": date(2024, 10, 1)},
            {"room_id": 8, "full_name": "Đặng Văn Giang", "phone": "0901234007", "id_card": "079123456007", "move_in_date": date(2024, 4, 15)},
            # Khu C
            {"room_id": 11, "full_name": "Bùi Văn Hùng", "phone": "0901234008", "id_card": "079123456008", "move_in_date": date(2024, 3, 1)},
            {"room_id": 12, "full_name": "Ngô Thị Lan", "phone": "0901234009", "id_card": "079123456009", "move_in_date": date(2024, 11, 1)},
            {"room_id": 13, "full_name": "Đỗ Văn Minh", "phone": "0901234010", "id_card": "079123456010", "move_in_date": date(2024, 12, 1)},
        ]
        
        for tenant_data in tenants_data:
            tenant = Tenant(**tenant_data, is_active=True)
            db.add(tenant)
            # Update room status
            room = db.query(Room).filter(Room.id == tenant_data["room_id"]).first()
            room.status = RoomStatus.OCCUPIED
        db.flush()
        
        # ============ METER READINGS ============
        print("Creating meter readings...")
        # Get all meters
        meters = db.query(Meter).all()
        
        # December 2025 readings for occupied rooms
        occupied_room_ids = [1, 2, 3, 4, 6, 7, 8, 11, 12, 13]
        for meter in meters:
            if meter.room_id in occupied_room_ids:
                if meter.meter_type == MeterType.ELECTRIC:
                    old_reading = Decimal("1000") + meter.room_id * 100
                    new_reading = old_reading + Decimal("150")  # ~150 kWh/month
                else:
                    old_reading = Decimal("50") + meter.room_id * 5
                    new_reading = old_reading + Decimal("8")  # ~8 m3/month
                
                reading = MeterReading(
                    meter_id=meter.id,
                    month=12,
                    year=2025,
                    old_reading=old_reading,
                    new_reading=new_reading,
                    consumption=new_reading - old_reading
                )
                db.add(reading)
        db.flush()
        
        # ============ INVOICES ============
        print("Creating invoices...")
        # December 2025 invoices
        for room_id in occupied_room_ids:
            room = db.query(Room).filter(Room.id == room_id).first()
            location = db.query(Location).filter(Location.id == room.location_id).first()
            
            # Get electric reading
            electric_meter = db.query(Meter).filter(
                Meter.room_id == room_id,
                Meter.meter_type == MeterType.ELECTRIC
            ).first()
            electric_reading = db.query(MeterReading).filter(
                MeterReading.meter_id == electric_meter.id,
                MeterReading.month == 12,
                MeterReading.year == 2025
            ).first()
            electric_fee = electric_reading.consumption * location.electric_price if electric_reading else Decimal("0")
            
            # Get water reading
            water_meter = db.query(Meter).filter(
                Meter.room_id == room_id,
                Meter.meter_type == MeterType.WATER
            ).first()
            water_reading = db.query(MeterReading).filter(
                MeterReading.meter_id == water_meter.id,
                MeterReading.month == 12,
                MeterReading.year == 2025
            ).first()
            water_fee = water_reading.consumption * location.water_price if water_reading else Decimal("0")
            
            room_fee = room.price
            total = room_fee + electric_fee + water_fee
            
            # Some paid, some unpaid
            if room_id in [1, 2, 6, 11]:
                status = InvoiceStatus.PAID
                paid_amount = total
            elif room_id in [3, 7]:
                status = InvoiceStatus.PARTIAL
                paid_amount = room_fee  # Only paid room fee
            else:
                status = InvoiceStatus.UNPAID
                paid_amount = Decimal("0")
            
            invoice = Invoice(
                room_id=room_id,
                month=12,
                year=2025,
                room_fee=room_fee,
                electric_fee=electric_fee,
                water_fee=water_fee,
                total=total,
                paid_amount=paid_amount,
                status=status
            )
            db.add(invoice)
        db.flush()
        
        # ============ EXPENSES ============
        print("Creating expenses...")
        expenses_data = [
            {"location_id": 1, "category": ExpenseCategory.REPAIR, "description": "Sửa ống nước phòng A101", "amount": Decimal("500000"), "expense_date": date(2025, 12, 5)},
            {"location_id": 1, "category": ExpenseCategory.UTILITY, "description": "Tiền điện khu vực chung Khu A", "amount": Decimal("350000"), "expense_date": date(2025, 12, 10)},
            {"location_id": 2, "category": ExpenseCategory.MAINTENANCE, "description": "Vệ sinh bể nước Khu B", "amount": Decimal("800000"), "expense_date": date(2025, 12, 15)},
            {"location_id": 3, "category": ExpenseCategory.REPAIR, "description": "Thay bóng đèn hành lang Khu C", "amount": Decimal("200000"), "expense_date": date(2025, 12, 20)},
            {"location_id": None, "category": ExpenseCategory.OTHER, "description": "Chi phí thuê nhân viên thu tiền", "amount": Decimal("1000000"), "expense_date": date(2025, 12, 25)},
        ]
        
        for exp_data in expenses_data:
            expense = Expense(**exp_data)
            db.add(expense)
        
        db.commit()
        print("✅ Database seeded successfully!")
        
        # Print summary
        print("\n📊 Summary:")
        print(f"   - Users: {db.query(User).count()}")
        print(f"   - Locations: {db.query(Location).count()}")
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

