'use client';

import { useState, useEffect } from 'react';
import TideChart from './TideChart';
import WaveChart from './WaveChart';

interface EnvironmentalData {
  timestamp: string;
  waterTemperature: number;
  airTemperature: number;
  windSpeed: number;
  windDirection: number;
  barometricPressure: number;
  humidity: number;
  visibility: number;
  uvIndex: number;
}

interface DataVisualizationProps {
  stationId?: string;
  stationName?: string;
  className?: string;
}

// Mock environmental data generator
const generateEnvironmentalData = (): EnvironmentalData[] => {
  const data: EnvironmentalData[] = [];
  const now = new Date();
  
  for (let i = -12; i <= 12; i++) {
    const timestamp = new Date(now.getTime() + i * 60 * 60 * 1000);
    const hours = i + 12;
    
    // Simulate realistic coastal environmental data
    const baseWaterTemp = 68;
    const waterTempVariation = 3 * Math.sin((hours * 2 * Math.PI) / 24) + Math.random() * 2;
    const waterTemperature = baseWaterTemp + waterTempVariation;
    
    const baseAirTemp = 72;
    const airTempVariation = 8 * Math.sin((hours * 2 * Math.PI) / 24) + Math.random() * 3;
    const airTemperature = baseAirTemp + airTempVariation;
    
    const baseWindSpeed = 12;
    const windSpeedVariation = 6 * Math.sin((hours * 2 * Math.PI) / 16) + Math.random() * 4;
    const windSpeed = Math.max(0, baseWindSpeed + windSpeedVariation);
    
    const windDirection = 180 + 45 * Math.sin((hours * 2 * Math.PI) / 20) + 20 * (Math.random() - 0.5);
    
    const basePressure = 1013.25;
    const pressureVariation = 10 * Math.sin((hours * 2 * Math.PI) / 48) + Math.random() * 3;
    const barometricPressure = basePressure + pressureVariation;
    
    const baseHumidity = 75;
    const humidityVariation = 15 * Math.sin((hours * 2 * Math.PI) / 24) + Math.random() * 5;
    const humidity = Math.max(30, Math.min(100, baseHumidity + humidityVariation));
    
    const baseVisibility = 10;
    const visibilityVariation = 3 * Math.sin((hours * 2 * Math.PI) / 36) + Math.random() * 2;
    const visibility = Math.max(1, baseVisibility + visibilityVariation);
    
    const baseUV = Math.max(0, 8 * Math.sin((hours * 2 * Math.PI) / 24));
    const uvIndex = Math.max(0, baseUV + Math.random() * 2);
    
    data.push({
      timestamp: timestamp.toISOString(),
      waterTemperature: Math.round(waterTemperature * 10) / 10,
      airTemperature: Math.round(airTemperature * 10) / 10,
      windSpeed: Math.round(windSpeed * 10) / 10,
      windDirection: Math.round(windDirection),
      barometricPressure: Math.round(barometricPressure * 100) / 100,
      humidity: Math.round(humidity),
      visibility: Math.round(visibility * 10) / 10,
      uvIndex: Math.round(uvIndex * 10) / 10
    });
  }
  
  return data;
};

export default function DataVisualization({ stationId, stationName, className = '' }: DataVisualizationProps) {
  const [environmentalData, setEnvironmentalData] = useState<EnvironmentalData[]>([]);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [activeTab, setActiveTab] = useState<'overview' | 'tides' | 'waves' | 'weather'>('overview');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate data loading
    const loadData = async () => {
      setIsLoading(true);
      await new Promise(resolve => setTimeout(resolve, 800)); // Simulate API call
      setEnvironmentalData(generateEnvironmentalData());
      setIsLoading(false);
    };
    
    loadData();
    
    // Update current time every minute
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    
    return () => clearInterval(interval);
  }, [stationId]);

  const getCurrentData = () => {
    const currentIndex = environmentalData.findIndex(d => new Date(d.timestamp) > currentTime);
    return currentIndex > 0 ? environmentalData[currentIndex - 1] : environmentalData[0];
  };

  const getWindDirection = (degrees: number) => {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const index = Math.round(degrees / 22.5) % 16;
    return directions[index];
  };

  const getUVLevel = (uvIndex: number) => {
    if (uvIndex < 3) return { text: 'Low', color: 'text-green-600' };
    if (uvIndex < 6) return { text: 'Moderate', color: 'text-yellow-600' };
    if (uvIndex < 8) return { text: 'High', color: 'text-orange-600' };
    if (uvIndex < 11) return { text: 'Very High', color: 'text-red-600' };
    return { text: 'Extreme', color: 'text-purple-600' };
  };

  const getWindCondition = (speed: number) => {
    if (speed < 7) return { text: 'Light', color: 'text-green-600' };
    if (speed < 14) return { text: 'Moderate', color: 'text-yellow-600' };
    if (speed < 25) return { text: 'Strong', color: 'text-orange-600' };
    return { text: 'Gale', color: 'text-red-600' };
  };

  if (isLoading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              {Array.from({ length: 4 }, (_, i) => (
                <div key={i} className="h-16 bg-gray-200 rounded"></div>
              ))}
            </div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  const currentData = getCurrentData();
  const windCondition = getWindCondition(currentData?.windSpeed || 0);
  const uvLevel = getUVLevel(currentData?.uvIndex || 0);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow-lg p-1">
        <div className="flex space-x-1">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors flex-1 ${
              activeTab === 'overview' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('tides')}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors flex-1 ${
              activeTab === 'tides' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            Tides
          </button>
          <button
            onClick={() => setActiveTab('waves')}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors flex-1 ${
              activeTab === 'waves' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            Waves
          </button>
          <button
            onClick={() => setActiveTab('weather')}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors flex-1 ${
              activeTab === 'weather' ? 'bg-blue-500 text-white' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }`}
          >
            Weather
          </button>
        </div>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Current Conditions Summary */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Current Conditions</h3>
                {stationName && (
                  <p className="text-sm text-gray-600">{stationName}</p>
                )}
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500">
                  Last updated: {currentTime.toLocaleTimeString()}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">{currentData?.waterTemperature.toFixed(1)}°F</div>
                <div className="text-xs text-gray-600">Water Temp</div>
              </div>
              <div className="bg-orange-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-orange-600">{currentData?.airTemperature.toFixed(1)}°F</div>
                <div className="text-xs text-gray-600">Air Temp</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-600">{currentData?.windSpeed.toFixed(1)}</div>
                <div className="text-xs text-gray-600">Wind (mph)</div>
                <div className={`text-xs font-medium ${windCondition.color}`}>{windCondition.text}</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-purple-600">{getWindDirection(currentData?.windDirection || 0)}</div>
                <div className="text-xs text-gray-600">Wind Dir</div>
                <div className="text-xs text-gray-500">{currentData?.windDirection}°</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-gray-600">{currentData?.barometricPressure.toFixed(1)}</div>
                <div className="text-xs text-gray-600">Pressure (mb)</div>
              </div>
              <div className="bg-cyan-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-cyan-600">{currentData?.humidity}%</div>
                <div className="text-xs text-gray-600">Humidity</div>
              </div>
              <div className="bg-indigo-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-indigo-600">{currentData?.visibility.toFixed(1)}</div>
                <div className="text-xs text-gray-600">Visibility (mi)</div>
              </div>
              <div className="bg-yellow-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-yellow-600">{currentData?.uvIndex.toFixed(1)}</div>
                <div className="text-xs text-gray-600">UV Index</div>
                <div className={`text-xs font-medium ${uvLevel.color}`}>{uvLevel.text}</div>
              </div>
            </div>
          </div>

          {/* Mini Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TideChart stationId={stationId} stationName={stationName} className="h-80" />
            <WaveChart stationId={stationId} stationName={stationName} className="h-80" />
          </div>
        </div>
      )}

      {/* Tides Tab */}
      {activeTab === 'tides' && (
        <TideChart stationId={stationId} stationName={stationName} />
      )}

      {/* Waves Tab */}
      {activeTab === 'waves' && (
        <WaveChart stationId={stationId} stationName={stationName} />
      )}

      {/* Weather Tab */}
      {activeTab === 'weather' && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Weather Conditions</h3>
              {stationName && (
                <p className="text-sm text-gray-600">{stationName}</p>
              )}
            </div>
          </div>

          {/* Weather Chart */}
          <div className="relative h-64 mb-6">
            <svg className="w-full h-full" viewBox="0 0 800 200">
              {/* Temperature lines */}
              <path
                d={environmentalData.map((point, index) => {
                  const x = 40 + (index / (environmentalData.length - 1)) * 720;
                  const y = 180 - ((point.airTemperature - 60) / 30) * 160;
                  return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
                }).join(' ')}
                fill="none"
                stroke="#f59e0b"
                strokeWidth="3"
              />
              
              <path
                d={environmentalData.map((point, index) => {
                  const x = 40 + (index / (environmentalData.length - 1)) * 720;
                  const y = 180 - ((point.waterTemperature - 60) / 30) * 160;
                  return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
                }).join(' ')}
                fill="none"
                stroke="#3b82f6"
                strokeWidth="3"
              />
              
              {/* Current time line */}
              <line
                x1="400"
                y1="20"
                x2="400"
                y2="180"
                stroke="#ef4444"
                strokeWidth="2"
                strokeDasharray="4,4"
              />
            </svg>
          </div>

          {/* Weather Legend */}
          <div className="flex items-center justify-center space-x-6 mb-6">
            <div className="flex items-center">
              <div className="w-4 h-0.5 bg-amber-500 mr-2"></div>
              <span className="text-sm text-gray-600">Air Temperature</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-0.5 bg-blue-500 mr-2"></div>
              <span className="text-sm text-gray-600">Water Temperature</span>
            </div>
          </div>

          {/* Detailed Weather Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">Temperature</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-blue-700">Air:</span>
                  <span className="font-medium text-blue-900">{currentData?.airTemperature.toFixed(1)}°F</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-blue-700">Water:</span>
                  <span className="font-medium text-blue-900">{currentData?.waterTemperature.toFixed(1)}°F</span>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
              <h4 className="font-semibold text-green-900 mb-2">Wind</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-green-700">Speed:</span>
                  <span className="font-medium text-green-900">{currentData?.windSpeed.toFixed(1)} mph</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-green-700">Direction:</span>
                  <span className="font-medium text-green-900">{getWindDirection(currentData?.windDirection || 0)} ({currentData?.windDirection}°)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-green-700">Condition:</span>
                  <span className={`font-medium ${windCondition.color}`}>{windCondition.text}</span>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
              <h4 className="font-semibold text-purple-900 mb-2">Atmospheric</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-purple-700">Pressure:</span>
                  <span className="font-medium text-purple-900">{currentData?.barometricPressure.toFixed(1)} mb</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-purple-700">Humidity:</span>
                  <span className="font-medium text-purple-900">{currentData?.humidity}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-purple-700">Visibility:</span>
                  <span className="font-medium text-purple-900">{currentData?.visibility.toFixed(1)} mi</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}