# Coastal Threat Alert System (CTAS)

A unified, full-stack platform integrating real-time coastal and environmental data, AI-based forecasts, and user-friendly dashboards with alerting systems.

## Overview

The Coastal Threat Alert System (CTAS) serves as a centralized intelligence hub for monitoring and predicting coastal hazards. It integrates data from multiple sources including IMD, INCOIS, NOAA, Open-Meteo, NASA, and Copernicus to provide timely alerts and forecasts for coastal threats.

## Key Features

- Real-Time Data Ingestion: Automatically fetches live data from multiple sources
- AI/ML Forecasting: Predicts short-term flood and surge risk using historical tide and storm data
- User Dashboard: Provides interactive maps, tide charts, and alerts — accessible on web and mobile
- Multi-Channel Alerts: Push notifications and SMS alerts ensure rapid dissemination
- Environmental Monitoring: Satellite data integration for erosion and algal bloom detection

## System Architecture

### Data Sources
- IMD (cyclone & storm surge bulletins)
- INCOIS (tsunami & high wave alerts)
- Open-Meteo Marine (hourly wave, wind, SST forecasts)
- NOAA Tides & Currents (real-time water level data)
- NASA Earthdata (algal bloom detection)
- Copernicus Sentinel Hub (erosion & pollution monitoring)

### Backend
- Python + FastAPI
- Data ingestion scripts
- AI/ML module for forecasting
- Supabase/Postgres database

### Frontend
- Next.js + React + Tailwind CSS
- User authentication & onboarding
- Dashboard with maps and visualizations
- Mobile-responsive design

### Notification System
- Firebase Cloud Messaging (push)
- Twilio (SMS alerts)

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL

### Installation

1. Clone the repository
2. Set up the backend:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up the frontend:
   ```
   cd frontend
   npm install
   ```

### Configuration

Create a `.env` file in both the backend and frontend directories with the necessary environment variables.

### Running the Application

1. Start the backend server:
   ```
   cd backend
   uvicorn main:app --reload
   ```
2. Start the frontend development server:
   ```
   cd frontend
   npm run dev
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.