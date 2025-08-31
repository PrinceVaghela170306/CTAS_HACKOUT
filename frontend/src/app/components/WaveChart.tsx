'use client';

import { useState, useEffect } from 'react';

interface WaveData {
  timestamp: string;
  height: number;
  period: number;
  direction: number;
  energy: number;
}

interface WaveChartProps {
  stationId?: string;
  stationName?: string;
  className?: string;
}

// Mock wave data generator
const generateWaveData = (): WaveData[] => {
  const data: WaveData[] = [];
  const now = new Date();
  
  for (let i = -24; i <= 24; i++) {
    const timestamp = new Date(now.getTime() + i * 60 * 60 * 1000);
    const hours = i + 24;
    
    // Simulate wave patterns with some randomness
    const baseHeight = 3.5;
    const waveVariation = 1.5 * Math.sin((hours * 2 * Math.PI) / 8) + 0.5 * Math.random();
    const height = Math.max(0.5, baseHeight + waveVariation);
    
    const basePeriod = 8;
    const periodVariation = 2 * Math.sin((hours * 2 * Math.PI) / 12) + 0.5 * Math.random();
    const period = Math.max(4, basePeriod + periodVariation);
    
    const direction = 180 + 30 * Math.sin((hours * 2 * Math.PI) / 16) + 10 * (Math.random() - 0.5);
    
    const energy = Math.pow(height, 2) * period / 16; // Simplified energy calculation
    
    data.push({
      timestamp: timestamp.toISOString(),
      height: Math.round(height * 10) / 10,
      period: Math.round(period * 10) / 10,
      direction: Math.round(direction),
      energy: Math.round(energy * 100) / 100
    });
  }
  
  return data;
};

export default function WaveChart({ stationId, stationName, className = '' }: WaveChartProps) {
  const [waveData, setWaveData] = useState<WaveData[]>([]);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedPoint, setSelectedPoint] = useState<WaveData | null>(null);
  const [viewMode, setViewMode] = useState<'height' | 'period' | 'energy'>('height');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate data loading
    const loadData = async () => {
      setIsLoading(true);
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call
      setWaveData(generateWaveData());
      setIsLoading(false);
    };
    
    loadData();
    
    // Update current time every minute
    const interval = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    
    return () => clearInterval(interval);
  }, [stationId]);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const getDirectionText = (degrees: number) => {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const index = Math.round(degrees / 22.5) % 16;
    return directions[index];
  };

  const getWaveCondition = (height: number) => {
    if (height < 2) return { text: 'Calm', color: 'text-green-600' };
    if (height < 4) return { text: 'Moderate', color: 'text-yellow-600' };
    if (height < 6) return { text: 'Rough', color: 'text-orange-600' };
    return { text: 'Very Rough', color: 'text-red-600' };
  };

  if (isLoading) {
    return (
      <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const currentIndex = waveData.findIndex(d => new Date(d.timestamp) > currentTime);
  const currentData = currentIndex > 0 ? waveData[currentIndex - 1] : waveData[0];
  const condition = getWaveCondition(currentData?.height || 0);

  const getChartData = () => {
    switch (viewMode) {
      case 'height':
        return {
          data: waveData.map(d => d.height),
          unit: 'ft',
          color: '#3b82f6',
          label: 'Wave Height'
        };
      case 'period':
        return {
          data: waveData.map(d => d.period),
          unit: 's',
          color: '#10b981',
          label: 'Wave Period'
        };
      case 'energy':
        return {
          data: waveData.map(d => d.energy),
          unit: 'kJ/m²',
          color: '#f59e0b',
          label: 'Wave Energy'
        };
      default:
        return {
          data: waveData.map(d => d.height),
          unit: 'ft',
          color: '#3b82f6',
          label: 'Wave Height'
        };
    }
  };

  const chartData = getChartData();
  const maxValue = Math.max(...chartData.data);
  const minValue = Math.min(...chartData.data);
  const valueRange = maxValue - minValue;

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Wave Conditions</h3>
          {stationName && (
            <p className="text-sm text-gray-600">{stationName}</p>
          )}
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">
            {currentData?.height.toFixed(1)} ft
          </div>
          <div className={`text-sm font-medium ${condition.color}`}>
            {condition.text}
          </div>
          <div className="text-xs text-gray-500">
            {currentData?.period.toFixed(1)}s • {getDirectionText(currentData?.direction || 0)}
          </div>
        </div>
      </div>

      {/* View Mode Toggle */}
      <div className="flex bg-gray-100 rounded-lg p-1 mb-6">
        <button
          onClick={() => setViewMode('height')}
          className={`px-3 py-1 text-sm font-medium rounded-md transition-colors flex-1 ${
            viewMode === 'height' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Height
        </button>
        <button
          onClick={() => setViewMode('period')}
          className={`px-3 py-1 text-sm font-medium rounded-md transition-colors flex-1 ${
            viewMode === 'period' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Period
        </button>
        <button
          onClick={() => setViewMode('energy')}
          className={`px-3 py-1 text-sm font-medium rounded-md transition-colors flex-1 ${
            viewMode === 'energy' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Energy
        </button>
      </div>

      {/* Chart */}
      <div className="relative h-64 mb-4">
        <svg className="w-full h-full" viewBox="0 0 800 200">
          {/* Grid lines */}
          {Array.from({ length: 6 }, (_, i) => {
            const value = minValue + (i / 5) * valueRange;
            const y = 180 - (i / 5) * 160;
            return (
              <g key={i}>
                <line
                  x1="40"
                  y1={y}
                  x2="760"
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                  strokeDasharray={i % 2 === 0 ? "none" : "2,2"}
                />
                <text
                  x="35"
                  y={y + 4}
                  textAnchor="end"
                  className="text-xs fill-gray-500"
                >
                  {value.toFixed(1)}{chartData.unit}
                </text>
              </g>
            );
          })}
          
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
          
          {/* Wave curve */}
          <path
            d={waveData.map((point, index) => {
              const x = 40 + (index / (waveData.length - 1)) * 720;
              const value = chartData.data[index];
              const y = 180 - ((value - minValue) / valueRange) * 160;
              return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
            }).join(' ')}
            fill="none"
            stroke={chartData.color}
            strokeWidth="3"
          />
          
          {/* Fill area under curve */}
          <path
            d={[
              `M 40 180`,
              ...waveData.map((point, index) => {
                const x = 40 + (index / (waveData.length - 1)) * 720;
                const value = chartData.data[index];
                const y = 180 - ((value - minValue) / valueRange) * 160;
                return `L ${x} ${y}`;
              }),
              `L 760 180 Z`
            ].join(' ')}
            fill={chartData.color}
            fillOpacity="0.1"
          />
          
          {/* Data points */}
          {waveData.map((point, index) => {
            const x = 40 + (index / (waveData.length - 1)) * 720;
            const value = chartData.data[index];
            const y = 180 - ((value - minValue) / valueRange) * 160;
            
            return (
              <circle
                key={index}
                cx={x}
                cy={y}
                r="4"
                fill={chartData.color}
                stroke="white"
                strokeWidth="2"
                className="cursor-pointer hover:r-6 transition-all"
                onClick={() => setSelectedPoint(point)}
              />
            );
          })}
          
          {/* Time labels */}
          {waveData.filter((_, index) => index % 8 === 0).map((point, index) => {
            const originalIndex = index * 8;
            const x = 40 + (originalIndex / (waveData.length - 1)) * 720;
            return (
              <text
                key={originalIndex}
                x={x}
                y="195"
                textAnchor="middle"
                className="text-xs fill-gray-500"
              >
                {formatTime(point.timestamp)}
              </text>
            );
          })}
        </svg>
        
        {/* Current time label */}
        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 bg-red-500 text-white text-xs px-2 py-1 rounded">
          Now
        </div>
      </div>

      {/* Current conditions summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="text-center">
          <div className="text-lg font-bold text-blue-600">{currentData?.height.toFixed(1)} ft</div>
          <div className="text-xs text-gray-600">Height</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-green-600">{currentData?.period.toFixed(1)} s</div>
          <div className="text-xs text-gray-600">Period</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-purple-600">{getDirectionText(currentData?.direction || 0)}</div>
          <div className="text-xs text-gray-600">Direction</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-orange-600">{currentData?.energy.toFixed(1)}</div>
          <div className="text-xs text-gray-600">Energy (kJ/m²)</div>
        </div>
      </div>

      {/* Selected point details */}
      {selectedPoint && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <div>
              <p className="font-medium text-gray-900">
                {formatDate(selectedPoint.timestamp)} at {formatTime(selectedPoint.timestamp)}
              </p>
            </div>
            <button
              onClick={() => setSelectedPoint(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Height:</span>
              <span className="ml-1 font-medium">{selectedPoint.height.toFixed(1)} ft</span>
            </div>
            <div>
              <span className="text-gray-600">Period:</span>
              <span className="ml-1 font-medium">{selectedPoint.period.toFixed(1)} s</span>
            </div>
            <div>
              <span className="text-gray-600">Direction:</span>
              <span className="ml-1 font-medium">{getDirectionText(selectedPoint.direction)} ({selectedPoint.direction}°)</span>
            </div>
            <div>
              <span className="text-gray-600">Energy:</span>
              <span className="ml-1 font-medium">{selectedPoint.energy.toFixed(1)} kJ/m²</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}