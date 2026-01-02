# 🏠 Minh Rental - Property Management System

An easy-to-use internal rental property management system for small landlords.

## ✨ Features

- 🏘️ **Location & Room Management**: Manage multiple rental locations, add/edit/delete rooms
- 👤 **Tenant Management**: Track tenant information, move-in/move-out dates
- ⚡ **Utility Meter Reading**: Record monthly electricity and water meter readings, automatic consumption calculation
- 🧾 **Automatic Invoicing**: Generate monthly invoices automatically, track payment status
- 💰 **Income & Expenses**: Record expenses, comprehensive reports
- 📊 **Dashboard**: Overview of business operations

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 + React + Tailwind CSS
- **Backend**: Python FastAPI
- **Database**: PostgreSQL
- **Auth**: JWT (JSON Web Token)

## 🚀 Installation

### Requirements

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### 1. Clone repository

```bash
git clone <repository-url>
cd RentManager
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit DATABASE_URL and SECRET_KEY in .env

# Create database
createdb minh_rental

# Run seed data
python seed_data.py

# Start server
uvicorn app.main:app --reload
```

Backend will run at: http://localhost:8000

### 3. Setup Frontend

```bash
cd webAdmin

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Run development server
npm run dev
```

Frontend will run at: http://localhost:3000

### 4. Using Docker (Optional)

```bash
cd workspace
docker-compose up -d
```

## 📝 Demo Account

- **Email**: cominh@gmail.com
- **Password**: 123456

## 📚 API Documentation

After running the backend, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📂 Project Structure

```
RentManager/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Config, security, database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── main.py         # App entry point
│   ├── requirements.txt
│   └── seed_data.py        # Sample data
│
├── webAdmin/               # Next.js Frontend
│   ├── src/
│   │   ├── app/           # Pages (App Router)
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   └── lib/           # Utilities, API client
│   ├── package.json
│   └── tailwind.config.ts
│
└── workspace/
    └── compose.yml        # Docker Compose
```

## 🔧 Configuration

### Backend (.env)

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/minh_rental
SECRET_KEY=your-super-secret-key
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 📱 Screenshots

### Dashboard
Overview page displaying:
- Total rooms, occupied rooms, vacant rooms
- Monthly income/expenses
- List of unpaid rooms

### Room Management
- View room list by location
- Add/edit/delete rooms
- View tenants in rooms

### Utility Meter Reading
- Batch record electricity and water meters
- Automatic consumption calculation
- Historical records by month

### Invoices
- Generate monthly invoices automatically
- Track status: Unpaid / Paid
- View invoice details

## 🤝 Contributing

All contributions are welcome! Please create an Issue or Pull Request.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for more details.

---

Made with ❤️ for Cô Minh

