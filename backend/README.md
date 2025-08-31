# Coastal Monitor Backend API 🌊

A robust FastAPI-based backend service for coastal monitoring and flood forecasting with real-time data processing and AI-powered predictions.

## 🚀 Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.8+
- **Database**: PostgreSQL (via Supabase)
- **ORM**: SQLAlchemy
- **Authentication**: Supabase Auth
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn, TensorFlow/PyTorch
- **HTTP Client**: httpx
- **Validation**: Pydantic
- **ASGI Server**: Uvicorn

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection and setup
│   ├── dependencies.py         # Dependency injection
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── station.py
│   │   ├── sensor_data.py
│   │   └── alert.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── station.py
│   │   ├── sensor_data.py
│   │   └── alert.py
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── stations.py
│   │   ├── sensor_data.py
│   │   ├── alerts.py
│   │   └── forecasting.py
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── data_service.py
│   │   ├── forecasting_service.py
│   │   └── alert_service.py
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── security.py
│       ├── data_processing.py
│       └── ml_models.py
├── tests/                      # Test files
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (or Supabase account)
- pip or poetry

### Setup Steps

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

5. **Configure environment variables** in `.env`:
   ```env
   # Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/coastal_monitor
   
   # Supabase Configuration
   SUPABASE_URL=your-supabase-project-url
   SUPABASE_KEY=your-supabase-service-role-key
   SUPABASE_JWT_SECRET=your-supabase-jwt-secret
   
   # API Configuration
   SECRET_KEY=your-secret-key-for-jwt
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # External APIs
   WEATHER_API_KEY=your-weather-api-key
   TIDE_API_KEY=your-tide-api-key
   
   # Application Settings
   DEBUG=True
   CORS_ORIGINS=http://localhost:3001,http://localhost:3000
   ```

6. **Run database migrations** (if using Alembic):
   ```bash
   alembic upgrade head
   ```

7. **Start development server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Access API documentation**: `http://localhost:8000/docs`

## 🔧 Development

### Available Scripts

```bash
# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Development Workflow

1. **API Development**:
   - Create new endpoints in `app/routers/`
   - Define Pydantic schemas in `app/schemas/`
   - Implement business logic in `app/services/`
   - Add database models in `app/models/`

2. **Database Operations**:
   - Use SQLAlchemy for ORM operations
   - Create migrations with Alembic
   - Follow database naming conventions

3. **Testing**:
   - Write unit tests for services
   - Create integration tests for endpoints
   - Use pytest fixtures for test data

## 📊 API Endpoints

### Authentication

```http
POST /auth/login
POST /auth/register
POST /auth/refresh
POST /auth/logout
GET  /auth/me
```

### Monitoring Stations

```http
GET    /stations/              # List all stations
GET    /stations/{station_id}  # Get station details
POST   /stations/              # Create new station
PUT    /stations/{station_id}  # Update station
DELETE /stations/{station_id}  # Delete station
```

### Sensor Data

```http
GET  /sensor-data/                    # Get sensor data with filters
GET  /sensor-data/station/{station_id} # Get data for specific station
POST /sensor-data/                    # Submit new sensor data
GET  /sensor-data/latest              # Get latest readings
GET  /sensor-data/historical          # Get historical data
```

### Alerts

```http
GET    /alerts/              # List alerts
GET    /alerts/{alert_id}    # Get alert details
POST   /alerts/              # Create alert
PUT    /alerts/{alert_id}    # Update alert
DELETE /alerts/{alert_id}    # Delete alert
POST   /alerts/acknowledge   # Acknowledge alert
```

### Forecasting

```http
GET  /forecasting/flood-risk/{station_id}  # Get flood risk prediction
GET  /forecasting/tide/{station_id}        # Get tide predictions
GET  /forecasting/wave/{station_id}        # Get wave predictions
POST /forecasting/train-model             # Retrain ML models
GET  /forecasting/model-performance       # Get model metrics
```

## 🗄️ Database Schema

### Core Tables

#### Users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Monitoring Stations
```sql
CREATE TABLE monitoring_stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    elevation DECIMAL(8, 3),
    station_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Sensor Data
```sql
CREATE TABLE sensor_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES monitoring_stations(id),
    timestamp TIMESTAMP NOT NULL,
    water_level DECIMAL(8, 3),
    wave_height DECIMAL(8, 3),
    wave_period DECIMAL(8, 3),
    wind_speed DECIMAL(8, 3),
    wind_direction DECIMAL(5, 2),
    temperature DECIMAL(5, 2),
    pressure DECIMAL(8, 2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Alerts
```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id UUID REFERENCES monitoring_stations(id),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    threshold_value DECIMAL(10, 3),
    current_value DECIMAL(10, 3),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP
);
```

## 🤖 Machine Learning Models

### Flood Risk Prediction

```python
# Example model structure
class FloodRiskModel:
    def __init__(self):
        self.model = RandomForestRegressor()
        self.features = [
            'water_level', 'wave_height', 'tide_level',
            'wind_speed', 'pressure', 'temperature'
        ]
    
    def train(self, data):
        X = data[self.features]
        y = data['flood_risk']
        self.model.fit(X, y)
    
    def predict(self, current_data):
        return self.model.predict(current_data)
```

### Model Training Pipeline

1. **Data Collection**: Gather historical sensor data
2. **Feature Engineering**: Create relevant features
3. **Model Training**: Train ML models
4. **Validation**: Cross-validate model performance
5. **Deployment**: Update production models

## 🔐 Authentication & Security

### JWT Authentication

```python
# Token creation
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### Security Features

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Rate limiting
- Input validation with Pydantic
- SQL injection prevention

## 📈 Data Processing

### Real-time Data Pipeline

1. **Data Ingestion**: Receive sensor data via API
2. **Validation**: Validate data format and ranges
3. **Storage**: Store in PostgreSQL database
4. **Processing**: Calculate derived metrics
5. **Alerting**: Check thresholds and trigger alerts
6. **Forecasting**: Update ML model predictions

### Data Quality Checks

```python
def validate_sensor_data(data: SensorDataCreate):
    checks = [
        (data.water_level, 0, 50, "Water level out of range"),
        (data.wave_height, 0, 30, "Wave height out of range"),
        (data.temperature, -10, 50, "Temperature out of range"),
    ]
    
    for value, min_val, max_val, error_msg in checks:
        if value and not (min_val <= value <= max_val):
            raise ValueError(error_msg)
```

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**:
   ```env
   DEBUG=False
   DATABASE_URL=postgresql://prod_user:password@prod_host:5432/coastal_monitor
   CORS_ORIGINS=https://your-frontend-domain.com
   ```

2. **Docker Deployment**:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **Database Migrations**:
   ```bash
   alembic upgrade head
   ```

### Deployment Platforms

#### Heroku
```bash
# Create Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port $PORT" > Procfile

# Deploy
heroku create coastal-monitor-api
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

#### Railway
```bash
# railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

## 🧪 Testing

### Test Structure

```python
# tests/test_stations.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_stations():
    response = client.get("/stations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_station():
    station_data = {
        "name": "Test Station",
        "latitude": 25.7617,
        "longitude": -80.1918
    }
    response = client.post("/stations/", json=station_data)
    assert response.status_code == 201
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_stations.py

# Run with verbose output
pytest -v
```

## 📊 Monitoring & Logging

### Application Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.4f}s")
    return response
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Verify DATABASE_URL format
   - Check database server status
   - Ensure proper credentials

2. **Authentication Issues**:
   - Verify JWT secret configuration
   - Check token expiration
   - Validate Supabase settings

3. **API Performance**:
   - Monitor database query performance
   - Implement caching for frequent queries
   - Use database indexing

### Debug Commands

```bash
# Check database connection
python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"

# Validate environment variables
python -c "from app.config import settings; print(settings.dict())"

# Test API endpoints
curl -X GET http://localhost:8000/health
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Contributing

1. Follow PEP 8 style guidelines
2. Write comprehensive tests
3. Document API endpoints
4. Use type hints
5. Handle errors gracefully
6. Write meaningful commit messages

---

**Happy coding! 🚀**