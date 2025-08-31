'use client';

import { useState, useEffect } from 'react';

interface TideData {
  timestamp: string;
  height: number;
  type: 'high' | 'low' | 'rising' | 'falling';
}

interface TideChartProps {
  stationId?: string;
  stationName?: string;
  className?: string;
}

// Mock tide data generator
const generateTideData = (): TideData[] => {
  const data: TideData[] = [];
  const now = new Date();
  const baseHeight = 3.2;
  
  for (let i = -24; i <= 24; i++) {
    const timestamp = new Date(now.getTime() + i * 60 * 60 * 1000);
    const hours = i + 24;
    
    // Simulate tidal pattern (roughly 12.5 hour cycle)
    const tidePhase = (hours * 2 * Math.PI) / 12.5;
    const height = baseHeight + 2.5 * Math.sin(tidePhase) + 0.3 * Math.sin(tidePhase * 2);
    
    // Determine tide type based on derivative
    const nextHeight = baseHeight + 2.5 * Math.sin(((hours + 0.5) * 2 * Math.PI) / 12.5);
    let type: 'high' | 'low' | 'rising' | 'falling';
    
    if (height > 5.0) type = 'high';
    else if (height < 1.5) type = 'low';
    else if (nextHeight > height) type = 'rising';
    else type = 'falling';
    
    data.push({
      timestamp: timestamp.toISOString(),
      height: Math.max(0, height),
      type
    });
  }
  
  return data;
};

export default function TideChart({ stationId, stationName, className = '' }: TideChartProps) {
  const [tideData, setTideData] = useState<TideData[]>([]);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedPoint, setSelectedPoint] = useState<TideData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate data loading
    const loadData = async () => {
      setIsLoading(true);
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API call
      setTideData(generateTideData());
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

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'high': return 'text-blue-600';
      case 'low': return 'text-red-600';
      case 'rising': return 'text-green-600';
      case 'falling': return 'text-orange-600';
      default: return 'text-gray-600';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'high':
        return (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
        );
      case 'low':
        return (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        );
      case 'rising':
        return (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        );
      case 'falling':
        return (
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
          </svg>
        );
      default:
        return null;
    }
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

  const maxHeight = Math.max(...tideData.map(d => d.height));
  const minHeight = Math.min(...tideData.map(d => d.height));
  const heightRange = maxHeight - minHeight;
  
  const currentIndex = tideData.findIndex(d => new Date(d.timestamp) > currentTime);
  const currentData = currentIndex > 0 ? tideData[currentIndex - 1] : tideData[0];

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Tide Levels</h3>
          {stationName && (
            <p className="text-sm text-gray-600">{stationName}</p>
          )}
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">
            {currentData?.height.toFixed(1)} ft
          </div>
          <div className={`flex items-center text-sm ${getTypeColor(currentData?.type || 'rising')}`}>
            {getTypeIcon(currentData?.type || 'rising')}
            <span className="ml-1 capitalize">{currentData?.type}</span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="relative h-64 mb-4">
        <svg className="w-full h-full" viewBox="0 0 800 200">
          {/* Grid lines */}
          {[0, 1, 2, 3, 4, 5, 6].map(level => {
            const y = 180 - ((level - minHeight) / heightRange) * 160;
            return (
              <g key={level}>
                <line
                  x1="40"
                  y1={y}
                  x2="760"
                  y2={y}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                  strokeDasharray={level % 2 === 0 ? "none" : "2,2"}
                />
                <text
                  x="35"
                  y={y + 4}
                  textAnchor="end"
                  className="text-xs fill-gray-500"
                >
                  {level}ft
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
          
          {/* Tide curve */}
          <path
            d={tideData.map((point, index) => {
              const x = 40 + (index / (tideData.length - 1)) * 720;
              const y = 180 - ((point.height - minHeight) / heightRange) * 160;
              return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
            }).join(' ')}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="3"
          />
          
          {/* Data points */}
          {tideData.map((point, index) => {
            const x = 40 + (index / (tideData.length - 1)) * 720;
            const y = 180 - ((point.height - minHeight) / heightRange) * 160;
            const isHighLow = point.type === 'high' || point.type === 'low';
            
            return (
              <circle
                key={index}
                cx={x}
                cy={y}
                r={isHighLow ? "6" : "3"}
                fill={point.type === 'high' ? '#3b82f6' : point.type === 'low' ? '#ef4444' : '#6b7280'}
                stroke="white"
                strokeWidth="2"
                className="cursor-pointer hover:r-8 transition-all"
                onClick={() => setSelectedPoint(point)}
              />
            );
          })}
          
          {/* Time labels */}
          {tideData.filter((_, index) => index % 8 === 0).map((point, index) => {
            const originalIndex = index * 8;
            const x = 40 + (originalIndex / (tideData.length - 1)) * 720;
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

      {/* Legend */}
      <div className="flex items-center justify-between text-xs text-gray-600 mb-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>High Tide</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span>Low Tide</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-0.5 bg-red-500"></div>
            <span>Current Time</span>
          </div>
        </div>
        <div className="text-gray-500">
          48-hour forecast
        </div>
      </div>

      {/* Selected point details */}
      {selectedPoint && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">
                {formatDate(selectedPoint.timestamp)} at {formatTime(selectedPoint.timestamp)}
              </p>
              <p className="text-sm text-gray-600">
                Height: {selectedPoint.height.toFixed(1)} ft
              </p>
            </div>
            <div className={`flex items-center ${getTypeColor(selectedPoint.type)}`}>
              {getTypeIcon(selectedPoint.type)}
              <span className="ml-1 capitalize font-medium">{selectedPoint.type}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}