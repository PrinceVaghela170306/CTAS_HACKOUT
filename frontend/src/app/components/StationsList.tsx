'use client';

import { useState } from 'react';

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

interface StationsListProps {
  stations: MonitoringStation[];
  selectedStation?: MonitoringStation | null;
  onStationSelect?: (station: MonitoringStation) => void;
  onStationFilter?: (type: string) => void;
}

export default function StationsList({ 
  stations, 
  selectedStation, 
  onStationSelect, 
  onStationFilter 
}: StationsListProps) {
  const [filterType, setFilterType] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'type' | 'status' | 'risk'>('name');
  const [searchTerm, setSearchTerm] = useState('');

  const getTypeIcon = (type: string) => {
    const baseClasses = "w-4 h-4";
    
    switch (type) {
      case 'tide':
        return (
          <svg className={`${baseClasses} text-blue-600`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        );
      case 'wave':
        return (
          <svg className={`${baseClasses} text-cyan-600`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        );
      case 'weather':
        return (
          <svg className={`${baseClasses} text-orange-600`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
          </svg>
        );
      case 'water_quality':
        return (
          <svg className={`${baseClasses} text-green-600`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
        );
      default:
        return (
          <svg className={`${baseClasses} text-gray-600`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          </svg>
        );
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'maintenance': return 'bg-yellow-100 text-yellow-800';
      case 'inactive': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const filteredStations = stations
    .filter(station => {
      const matchesType = filterType === 'all' || station.type === filterType;
      const matchesSearch = station.name.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesType && matchesSearch;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'type':
          return a.type.localeCompare(b.type);
        case 'status':
          return a.status.localeCompare(b.status);
        case 'risk':
          const riskOrder = { 'high': 3, 'medium': 2, 'low': 1 };
          return riskOrder[b.riskLevel as keyof typeof riskOrder] - riskOrder[a.riskLevel as keyof typeof riskOrder];
        default:
          return 0;
      }
    });

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  const handleFilterChange = (type: string) => {
    setFilterType(type);
    onStationFilter?.(type);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-3 sm:p-6">
      <div className="flex items-center justify-between mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl font-bold text-gray-900">Monitoring Stations</h2>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">{filteredStations.length} stations</span>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="space-y-3 sm:space-y-4 mb-4 sm:mb-6">
        {/* Search */}
        <div className="relative">
          <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search stations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Filter Buttons */}
        <div className="flex flex-wrap gap-2">
          {['all', 'tide', 'wave', 'weather', 'water_quality'].map((type) => (
            <button
              key={type}
              onClick={() => handleFilterChange(type)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                filterType === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {type === 'all' ? 'All' : type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
        </div>

        {/* Sort Options */}
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-600">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="name">Name</option>
            <option value="type">Type</option>
            <option value="status">Status</option>
            <option value="risk">Risk Level</option>
          </select>
        </div>
      </div>

      {/* Stations List */}
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {filteredStations.map((station) => (
          <div
            key={station.id}
            onClick={() => onStationSelect?.(station)}
            className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
              selectedStation?.id === station.id
                ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                <div className="flex-shrink-0 mt-1">
                  {getTypeIcon(station.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-gray-900 truncate">{station.name}</h3>
                  <p className="text-sm text-gray-600 capitalize">
                    {station.type.replace('_', ' ')} Station
                  </p>
                  <div className="flex items-center space-x-4 mt-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(station.status)}`}>
                      {station.status}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getRiskColor(station.riskLevel)}`}>
                      {station.riskLevel} risk
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-right flex-shrink-0 ml-4">
                <div className="text-lg font-bold text-gray-900">
                  {station.lastReading.value} {station.lastReading.unit}
                </div>
                <div className="text-xs text-gray-500">
                  {formatTimestamp(station.lastReading.timestamp)}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredStations.length === 0 && (
        <div className="text-center py-8">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.291-1.1-5.291-2.709M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No stations found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'Try adjusting your search terms.' : 'No stations match the current filter.'}
          </p>
        </div>
      )}
    </div>
  );
}