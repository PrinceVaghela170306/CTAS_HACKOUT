'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
// import { getCurrentUser, signOut } from '../../../lib/supabase'; // Temporarily disabled
import CoastalMap from '../components/CoastalMap';
import StationsList from '../components/StationsList';
import DataVisualization from '../components/DataVisualization';
import FloodForecasting from '../components/FloodForecasting';
import NotificationSettings from '../components/NotificationSettings';
import AlertManagement from '../components/AlertManagement';
import MonitoringDashboard from '../components/MonitoringDashboard';

interface UserData {
  email: string;
  first_name: string;
  last_name: string;
  location?: {
    name: string;
    latitude: number;
    longitude: number;
  };
}

interface MonitoringStation {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  type: 'tide' | 'weather' | 'wave' | 'water_quality';
  status: 'active' | 'inactive' | 'maintenance';
  lastReading: {
    timestamp: string;
    value: number;
    unit: string;
  };
  riskLevel: 'low' | 'medium' | 'high';
}

const MONITORING_STATIONS: MonitoringStation[] = [
  {
    id: 'miami-tide-01',
    name: 'Miami Beach Tide Station',
    latitude: 25.7907,
    longitude: -80.1300,
    type: 'tide',
    status: 'active',
    lastReading: {
      timestamp: new Date().toISOString(),
      value: 2.3,
      unit: 'ft'
    },
    riskLevel: 'medium'
  },
  {
    id: 'charleston-wave-01',
    name: 'Charleston Harbor Wave Buoy',
    latitude: 32.7765,
    longitude: -79.9311,
    type: 'wave',
    status: 'active',
    lastReading: {
      timestamp: new Date().toISOString(),
      value: 4.2,
      unit: 'ft'
    },
    riskLevel: 'low'
  },
  {
    id: 'virginia-weather-01',
    name: 'Virginia Beach Weather Station',
    latitude: 36.8529,
    longitude: -75.9780,
    type: 'weather',
    status: 'active',
    lastReading: {
      timestamp: new Date().toISOString(),
      value: 15.2,
      unit: 'mph'
    },
    riskLevel: 'low'
  },
  {
    id: 'outer-banks-tide-01',
    name: 'Cape Hatteras Tide Gauge',
    latitude: 35.2269,
    longitude: -75.5261,
    type: 'tide',
    status: 'active',
    lastReading: {
      timestamp: new Date().toISOString(),
      value: 3.8,
      unit: 'ft'
    },
    riskLevel: 'high'
  },
  {
    id: 'galveston-wave-01',
    name: 'Galveston Bay Wave Monitor',
    latitude: 29.3013,
    longitude: -94.7977,
    type: 'wave',
    status: 'maintenance',
    lastReading: {
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      value: 2.1,
      unit: 'ft'
    },
    riskLevel: 'medium'
  },
  {
    id: 'san-diego-quality-01',
    name: 'San Diego Water Quality Monitor',
    latitude: 32.7157,
    longitude: -117.1611,
    type: 'water_quality',
    status: 'active',
    lastReading: {
      timestamp: new Date().toISOString(),
      value: 7.2,
      unit: 'pH'
    },
    riskLevel: 'low'
  }
];

export default function DashboardPage() {
  const [userData, setUserData] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedStation, setSelectedStation] = useState<MonitoringStation | null>(null);
  const [viewMode, setViewMode] = useState<'map' | 'list' | 'split' | 'forecasting' | 'notifications' | 'alerts' | 'monitoring'>('split');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          router.push('/login');
          return;
        }

        // Demo authentication - get user data from localStorage
        const userEmail = localStorage.getItem('user_email');
        
        if (!userEmail) {
          localStorage.removeItem('token');
          router.push('/login');
          return;
        }

        // Create demo user data
        const userData = {
          id: 'demo-user-' + Date.now(),
          email: userEmail,
          full_name: userEmail.split('@')[0] || 'Demo User',
          phone: null,
          is_verified: true,
          created_at: new Date().toISOString(),
          location: {
            name: 'Miami, FL',
            latitude: 25.7617,
            longitude: -80.1918
          },
          preferences: {
            notifications: {
              email: true,
              sms: false,
              push: true
            },
            units: 'metric',
            language: 'en'
          }
        };
        
        setUserData(userData);
      } catch (err) {
        setError('Network error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserData();
  }, [router]);

  const handleLogout = async () => {
    // Demo logout - just clear localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user_email');
    console.log('Demo logout successful');
    router.push('/login');
  };

  const handleStationSelect = (station: MonitoringStation) => {
    setSelectedStation(station);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-red-700">{error}</p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className="h-8 w-8 bg-gradient-to-r from-blue-500 to-teal-500 rounded-lg flex items-center justify-center mr-3">
                  <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h1 className="text-xl font-semibold text-gray-900">Coastal Monitor</h1>
              </div>
              {userData?.location && (
                <div className="text-sm text-gray-600">
                  📍 {userData.location.name}
                </div>
              )}
            </div>
            <div className="flex items-center space-x-4">
              {/* Desktop View Mode Toggle */}
              <div className="hidden lg:flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('map')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                    viewMode === 'map' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Map
                </button>
                <button
                  onClick={() => setViewMode('split')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                    viewMode === 'split' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Split
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                    viewMode === 'list' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  List
                </button>
                <button
                  onClick={() => setViewMode('forecasting')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                    viewMode === 'forecasting' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  AI Forecasting
                </button>
                <button
                  onClick={() => setViewMode('notifications')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                    viewMode === 'notifications' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Notifications
                </button>
                <button
                  onClick={() => setViewMode('alerts')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                    viewMode === 'alerts' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Alerts
                </button>
                <button
                  onClick={() => setViewMode('monitoring')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                    viewMode === 'monitoring' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Monitoring
                </button>
              </div>
              
              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <span className="text-sm text-gray-600">
                Welcome, {userData?.first_name} {userData?.last_name}
              </span>
              <button
                onClick={handleLogout}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Navigation Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-white border-b border-gray-200 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-3">
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => { setViewMode('map'); setMobileMenuOpen(false); }}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'map' ? 'bg-blue-100 text-blue-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                🗺️ Map
              </button>
              <button
                onClick={() => { setViewMode('split'); setMobileMenuOpen(false); }}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'split' ? 'bg-blue-100 text-blue-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                📊 Dashboard
              </button>
              <button
                onClick={() => { setViewMode('list'); setMobileMenuOpen(false); }}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'list' ? 'bg-blue-100 text-blue-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                📋 Stations
              </button>
              <button
                onClick={() => { setViewMode('forecasting'); setMobileMenuOpen(false); }}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'forecasting' ? 'bg-blue-100 text-blue-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                🤖 AI Forecast
              </button>
              <button
                onClick={() => { setViewMode('alerts'); setMobileMenuOpen(false); }}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'alerts' ? 'bg-blue-100 text-blue-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                🚨 Alerts
              </button>
              <button
                onClick={() => { setViewMode('monitoring'); setMobileMenuOpen(false); }}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  viewMode === 'monitoring' ? 'bg-blue-100 text-blue-900' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                📡 Monitor
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8 py-3 sm:py-6">
        {/* Dashboard Content */}
        <div className="h-[calc(100vh-120px)] sm:h-[calc(100vh-140px)] lg:h-[calc(100vh-140px)]">
          {viewMode === 'map' && (
            <div className="h-full space-y-6">
              <div className="h-3/4">
                <CoastalMap
                  userLocation={userData?.location}
                  onStationSelect={handleStationSelect}
                />
              </div>
              <div className="h-1/4">
                <DataVisualization 
                  stationId={selectedStation?.id} 
                  stationName={selectedStation?.name}
                />
              </div>
            </div>
          )}
          
          {viewMode === 'list' && (
            <div className="h-full flex flex-col">
              <div className="flex-1 mb-6">
                <StationsList
                  stations={MONITORING_STATIONS}
                  selectedStation={selectedStation}
                  onStationSelect={handleStationSelect}
                />
              </div>
              <div className="h-64 flex-shrink-0">
                <DataVisualization 
                  stationId={selectedStation?.id} 
                  stationName={selectedStation?.name}
                />
              </div>
            </div>
          )}
          
          {viewMode === 'split' && (
            <div className="h-full flex flex-col space-y-6">
              <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="h-full">
                  <CoastalMap
                    userLocation={userData?.location}
                    onStationSelect={handleStationSelect}
                  />
                </div>
                <div className="h-full">
                  <StationsList
                    stations={MONITORING_STATIONS}
                    selectedStation={selectedStation}
                    onStationSelect={handleStationSelect}
                  />
                </div>
              </div>
              <div className="h-64 flex-shrink-0">
                <DataVisualization 
                  stationId={selectedStation?.id} 
                  stationName={selectedStation?.name}
                />
              </div>
            </div>
          )}
          
          {viewMode === 'forecasting' && (
            <FloodForecasting
              stationId={selectedStation?.id}
              stationName={selectedStation?.name}
              latitude={selectedStation?.latitude}
              longitude={selectedStation?.longitude}
            />
          )}
          
          {viewMode === 'notifications' && (
            <div className="h-full">
              <NotificationSettings userId={userData?.email || ''} />
            </div>
          )}
          
          {viewMode === 'alerts' && (
            <div className="h-full">
              <AlertManagement 
                userId={userData?.email || ''} 
                location={userData?.location || ''}
              />
            </div>
          )}
          
          {viewMode === 'monitoring' && (
            <div className="h-full space-y-6">
              <MonitoringDashboard />
              <DataVisualization 
                stationId={selectedStation?.id} 
                stationName={selectedStation?.name}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}