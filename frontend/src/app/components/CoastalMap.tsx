'use client';

import { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import 'leaflet/dist/leaflet.css';

// Dynamically import Leaflet components to avoid SSR issues
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false });
const useMap = dynamic(() => import('react-leaflet').then(mod => mod.useMap), { ssr: false });

// Custom icon creation function
const createCustomIcon = (type: string, status: string) => {
  if (typeof window === 'undefined') return null;
  
  const L = require('leaflet');
  
  const getIconColor = () => {
    switch (status) {
      case 'active': return '#10b981'; // green
      case 'maintenance': return '#f59e0b'; // yellow
      case 'inactive': return '#ef4444'; // red
      default: return '#6b7280'; // gray
    }
  };
  
  const getIconSymbol = () => {
    switch (type) {
      case 'tide': return '🌊';
      case 'wave': return '〰️';
      case 'weather': return '🌤️';
      case 'water_quality': return '💧';
      case 'user': return '📍';
      default: return '📍';
    }
  };
  
  const iconHtml = `
    <div style="
      background-color: ${getIconColor()};
      width: 30px;
      height: 30px;
      border-radius: 50%;
      border: 3px solid white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    ">
      ${getIconSymbol()}
    </div>
  `;
  
  return L.divIcon({
    html: iconHtml,
    className: 'custom-marker',
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -15]
  });
};

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

interface CoastalMapProps {
  userLocation?: {
    name: string;
    latitude: number;
    longitude: number;
  };
  onStationSelect?: (station: MonitoringStation) => void;
}

export default function CoastalMap({ userLocation, onStationSelect }: CoastalMapProps) {
  const [selectedStation, setSelectedStation] = useState<MonitoringStation | null>(null);
  const [mapCenter, setMapCenter] = useState<[number, number]>([39.8283, -98.5795]); // Center of US
  const [zoom, setZoom] = useState(4);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (userLocation) {
      setMapCenter([userLocation.latitude, userLocation.longitude]);
      setZoom(8);
    }
  }, [userLocation]);

  if (!isClient) {
    return (
      <div className="w-full h-full bg-blue-50 rounded-lg flex items-center justify-center">
        <div className="text-gray-500">Loading map...</div>
      </div>
      );
   };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'high': return 'bg-red-100 border-red-300 text-red-800';
      case 'medium': return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      case 'low': return 'bg-green-100 border-green-300 text-green-800';
      default: return 'bg-gray-100 border-gray-300 text-gray-800';
    }
  };

  const handleStationClick = (station: MonitoringStation) => {
    setSelectedStation(station);
    onStationSelect?.(station);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="relative w-full h-full bg-blue-50 rounded-lg overflow-hidden">
      {/* Leaflet Map Container */}
      <MapContainer
        center={mapCenter}
        zoom={zoom}
        className="w-full h-full z-0"
        zoomControl={false}
      >
        {/* OpenStreetMap Tile Layer */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* User Location Marker */}
        {userLocation && (
          <Marker 
            position={[userLocation.latitude, userLocation.longitude]}
            icon={createCustomIcon('user', 'active') || undefined}
          >
            <Popup>
              <div className="text-center">
                <strong>Your Location</strong><br/>
                {userLocation.name}
              </div>
            </Popup>
          </Marker>
        )}
        
        {/* Monitoring Stations */}
        {MONITORING_STATIONS.map((station) => (
          <Marker
            key={station.id}
            position={[station.latitude, station.longitude]}
            icon={createCustomIcon(station.type, station.status) || undefined}
            eventHandlers={{
              click: () => handleStationClick(station)
            }}
          >
            <Popup>
              <div className="min-w-[200px]">
                <h3 className="font-semibold text-gray-900 mb-2">{station.name}</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="capitalize">{station.type.replace('_', ' ')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Status:</span>
                    <span className={`capitalize ${
                      station.status === 'active' ? 'text-green-600' :
                      station.status === 'maintenance' ? 'text-yellow-600' :
                      'text-red-600'
                    }`}>
                      {station.status}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Risk Level:</span>
                    <span className={`capitalize ${
                      station.riskLevel === 'high' ? 'text-red-600' :
                      station.riskLevel === 'medium' ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {station.riskLevel}
                    </span>
                  </div>
                  <div className="border-t pt-2">
                    <div className="font-medium">Latest Reading:</div>
                    <div className="text-lg font-bold">
                      {station.lastReading.value} {station.lastReading.unit}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatTimestamp(station.lastReading.timestamp)}
                    </div>
                  </div>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      
      {/* Custom Map Controls */}
      <div className="absolute top-4 right-4 flex flex-col space-y-2 z-[1000]">
        <button
          onClick={() => setZoom(Math.min(zoom + 1, 18))}
          className="w-8 h-8 bg-white rounded shadow-lg flex items-center justify-center hover:bg-gray-50 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </button>
        <button
          onClick={() => setZoom(Math.max(zoom - 1, 1))}
          className="w-8 h-8 bg-white rounded shadow-lg flex items-center justify-center hover:bg-gray-50 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 12H6" />
          </svg>
        </button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-4 z-[1000]">
        <h3 className="font-semibold text-sm mb-2">Station Types</h3>
        <div className="space-y-1 text-xs">
          <div className="flex items-center space-x-2">
            <span className="text-lg">🌊</span>
            <span>Tide Gauge</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-lg">〰️</span>
            <span>Wave Buoy</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-lg">🌤️</span>
            <span>Weather Station</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-lg">💧</span>
            <span>Water Quality</span>
          </div>
        </div>
        <div className="mt-3 pt-2 border-t border-gray-200">
          <h4 className="font-semibold text-xs mb-1">Status</h4>
          <div className="flex space-x-3 text-xs">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Active</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span>Maintenance</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span>Offline</span>
            </div>
          </div>
        </div>
      </div>

      {/* Station Details Panel */}
      {selectedStation && (
        <div className="absolute top-4 left-4 bg-white rounded-lg shadow-xl p-4 max-w-sm z-40">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="font-semibold text-gray-900">{selectedStation.name}</h3>
              <p className="text-sm text-gray-600 capitalize">{selectedStation.type.replace('_', ' ')} Station</p>
            </div>
            <button
              onClick={() => setSelectedStation(null)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Status:</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${
                selectedStation.status === 'active' ? 'bg-green-100 text-green-800' :
                selectedStation.status === 'maintenance' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {selectedStation.status}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Risk Level:</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getRiskLevelColor(selectedStation.riskLevel)}`}>
                {selectedStation.riskLevel}
              </span>
            </div>
            
            <div className="border-t pt-3">
              <h4 className="font-medium text-sm mb-2">Latest Reading</h4>
              <div className="bg-gray-50 rounded p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-lg font-bold text-gray-900">
                    {selectedStation.lastReading.value} {selectedStation.lastReading.unit}
                  </span>
                </div>
                <p className="text-xs text-gray-500">
                  {formatTimestamp(selectedStation.lastReading.timestamp)}
                </p>
              </div>
            </div>
            
            <div className="text-xs text-gray-500">
              <p>Lat: {selectedStation.latitude.toFixed(4)}</p>
              <p>Lng: {selectedStation.longitude.toFixed(4)}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}