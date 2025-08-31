# Coastal Monitor 🌊

A comprehensive AI-powered coastal monitoring and flood forecasting system that provides real-time data visualization, risk assessment, and early warning capabilities for coastal communities.

## 🚀 Features

### Core Functionality
- **Real-time Monitoring**: Live data from tide gauges, wave buoys, and weather stations
- **AI Flood Forecasting**: LSTM neural network-based flood risk prediction
- **Interactive Dashboard**: Multiple view modes (Map, List, Split, Monitoring)
- **Alert Management**: Customizable notifications and emergency alerts
- **Data Visualization**: Interactive charts for tide levels, wave conditions, and weather data

### Technical Highlights
- **Responsive Design**: Optimized for desktop and mobile devices
- **Real-time Updates**: Live data streaming and automatic refresh
- **Secure Authentication**: Supabase-powered user management
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Modern UI**: Clean, intuitive interface built with Next.js and Tailwind CSS

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (SQLite)      │
│   Port: 3001    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
           │                       │
           ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Supabase      │    │   ML Models     │
│ (Authentication)│    │   (LSTM/AI)     │
└─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher)
- **Python** (v3.8 or higher)
- **npm** or **yarn**
- **Git**

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd HACKOUT
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Database
DATABASE_URL=sqlite:///./coastal_guard.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME="Coastal Monitor API"

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# Supabase (Optional - for enhanced authentication)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
```

#### Initialize Database

```bash
python -c "from app.init_db import init_db; init_db()"
```

#### Start Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

#### Install Node.js Dependencies

```bash
cd frontend
npm install
```

#### Environment Configuration

Create a `.env.local` file in the `frontend` directory:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

#### Start Frontend Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3001`

## 🔐 Authentication Setup (Supabase)

### 1. Create Supabase Project

1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Get your project URL and anon key from Settings > API

### 2. Configure Authentication

1. In Supabase dashboard, go to Authentication > Settings
2. Configure your site URL: `http://localhost:3001`
3. Add redirect URLs for production deployment

### 3. Update Environment Variables

Add your Supabase credentials to both frontend and backend `.env` files as shown above.

## 📊 Usage

### Dashboard Views

1. **Map View**: Interactive coastal map with monitoring stations
2. **List View**: Tabular data with station information and charts
3. **Split View**: Combined map and list with data visualization
4. **AI Forecasting**: Machine learning-powered flood predictions
5. **Monitoring**: Real-time system status and alerts
6. **Notifications**: Customizable alert settings
7. **Alerts**: Emergency notification management

### Key Features

- **Station Selection**: Click on map markers or list items to view detailed data
- **Real-time Charts**: Tide levels, wave conditions, and weather data
- **Risk Assessment**: Color-coded risk levels (Low, Medium, High)
- **Forecasting**: 24-48 hour flood probability predictions
- **Alert Management**: Create, acknowledge, and resolve alerts

## 🧪 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/logout` - User logout

### Monitoring
- `GET /api/v1/stations` - Get all monitoring stations
- `GET /api/v1/stations/{station_id}` - Get specific station data
- `GET /api/v1/stations/{station_id}/readings` - Get station readings

### Forecasting
- `GET /api/v1/forecasting/flood-risk/{location}` - Get flood risk assessment
- `GET /api/v1/forecasting/advanced-prediction/{location}` - Get detailed predictions

### Alerts
- `GET /api/v1/alerts` - Get all alerts
- `POST /api/v1/alerts` - Create new alert
- `PUT /api/v1/alerts/{alert_id}` - Update alert status

## 🚀 Deployment

### Frontend (Vercel/Netlify)

1. Build the application:
   ```bash
   cd frontend
   npm run build
   ```

2. Deploy to your preferred platform
3. Update environment variables in deployment settings

### Backend (Railway/Heroku/DigitalOcean)

1. Create `Dockerfile` (already included)
2. Set up environment variables
3. Deploy using your preferred platform
4. Update CORS origins to include your frontend URL

### Database

- **Development**: SQLite (included)
- **Production**: PostgreSQL recommended
- Update `DATABASE_URL` in environment variables

## 🔧 Development

### Project Structure

```
HACKOUT/
├── backend/
│   ├── app/
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Database models
│   │   ├── routers/       # API endpoints
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/    # React components
│   │   │   ├── dashboard/    # Dashboard pages
│   │   │   └── login/        # Authentication
│   │   └── lib/              # Utilities
│   ├── package.json
│   └── next.config.ts
└── README.md
```

### Adding New Features

1. **Backend**: Add new routers in `app/routers/`
2. **Frontend**: Create components in `src/app/components/`
3. **Database**: Update models in `app/models/`
4. **API**: Define schemas in `app/schemas/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `npm test` (frontend) / `pytest` (backend)
5. Commit changes: `git commit -m 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the API documentation at `http://localhost:8000/docs`
- Review the frontend components for usage examples

## 🙏 Acknowledgments

- **FastAPI** for the robust backend framework
- **Next.js** for the powerful frontend framework
- **Supabase** for authentication services
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **Leaflet** for interactive maps

---

**Built with ❤️ for coastal communities worldwide** 🌊