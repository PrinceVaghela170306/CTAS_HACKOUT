'use client';

import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Clock, X, Eye, Bell, Filter, Search } from 'lucide-react';

interface Alert {
  id: string;
  type: 'flood' | 'weather' | 'system' | 'emergency';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  location: string;
  created_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  status: 'active' | 'acknowledged' | 'resolved';
  metadata?: {
    water_level?: number;
    wind_speed?: number;
    temperature?: number;
    coordinates?: [number, number];
  };
}

interface AlertStats {
  total: number;
  active: number;
  acknowledged: number;
  resolved: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

interface AlertManagementProps {
  userId: string;
  location?: string;
}

const AlertManagement: React.FC<AlertManagementProps> = ({ userId, location }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filteredAlerts, setFilteredAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<AlertStats>({
    total: 0,
    active: 0,
    acknowledged: 0,
    resolved: 0,
    critical: 0,
    high: 0,
    medium: 0,
    low: 0
  });
  const [loading, setLoading] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock data for demonstration
  useEffect(() => {
    const mockAlerts: Alert[] = [
      {
        id: '1',
        type: 'flood',
        severity: 'critical',
        title: 'Critical Flood Warning',
        message: 'Water levels have exceeded critical thresholds. Immediate evacuation recommended for low-lying areas.',
        location: 'Miami Beach, FL',
        created_at: '2024-01-15T14:30:00Z',
        status: 'active',
        metadata: {
          water_level: 8.5,
          coordinates: [25.7907, -80.1300]
        }
      },
      {
        id: '2',
        type: 'weather',
        severity: 'high',
        title: 'Storm Surge Alert',
        message: 'Storm surge of 6-8 feet expected within the next 4 hours. Coastal flooding likely.',
        location: 'Key West, FL',
        created_at: '2024-01-15T12:15:00Z',
        acknowledged_at: '2024-01-15T12:45:00Z',
        status: 'acknowledged',
        metadata: {
          wind_speed: 65,
          coordinates: [24.5551, -81.7800]
        }
      },
      {
        id: '3',
        type: 'system',
        severity: 'medium',
        title: 'Sensor Maintenance',
        message: 'Tide gauge sensor at Station #12 requires calibration. Data accuracy may be affected.',
        location: 'Fort Lauderdale, FL',
        created_at: '2024-01-15T10:00:00Z',
        resolved_at: '2024-01-15T13:30:00Z',
        status: 'resolved',
        metadata: {
          coordinates: [26.1224, -80.1373]
        }
      },
      {
        id: '4',
        type: 'emergency',
        severity: 'critical',
        title: 'Tsunami Warning',
        message: 'Tsunami warning issued for coastal areas. Move to higher ground immediately.',
        location: 'Naples, FL',
        created_at: '2024-01-15T09:45:00Z',
        acknowledged_at: '2024-01-15T09:50:00Z',
        status: 'acknowledged',
        metadata: {
          coordinates: [26.1420, -81.7948]
        }
      },
      {
        id: '5',
        type: 'flood',
        severity: 'low',
        title: 'Minor Flooding',
        message: 'Minor street flooding reported in downtown area. Exercise caution when driving.',
        location: 'Tampa, FL',
        created_at: '2024-01-15T08:20:00Z',
        resolved_at: '2024-01-15T11:15:00Z',
        status: 'resolved',
        metadata: {
          water_level: 3.2,
          coordinates: [27.9506, -82.4572]
        }
      }
    ];
    
    setAlerts(mockAlerts);
    setFilteredAlerts(mockAlerts);
    
    // Calculate stats
    const newStats = mockAlerts.reduce((acc, alert) => {
      acc.total++;
      acc[alert.status]++;
      acc[alert.severity]++;
      return acc;
    }, {
      total: 0,
      active: 0,
      acknowledged: 0,
      resolved: 0,
      critical: 0,
      high: 0,
      medium: 0,
      low: 0
    } as AlertStats);
    
    setStats(newStats);
  }, []);

  // Filter alerts based on selected filters and search query
  useEffect(() => {
    let filtered = alerts;

    if (filterType !== 'all') {
      filtered = filtered.filter(alert => alert.type === filterType);
    }

    if (filterSeverity !== 'all') {
      filtered = filtered.filter(alert => alert.severity === filterSeverity);
    }

    if (filterStatus !== 'all') {
      filtered = filtered.filter(alert => alert.status === filterStatus);
    }

    if (searchQuery) {
      filtered = filtered.filter(alert => 
        alert.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        alert.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
        alert.location.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredAlerts(filtered);
  }, [alerts, filterType, filterSeverity, filterStatus, searchQuery]);

  const acknowledgeAlert = async (alertId: string) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, status: 'acknowledged', acknowledged_at: new Date().toISOString() }
          : alert
      ));
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    } finally {
      setLoading(false);
    }
  };

  const resolveAlert = async (alertId: string) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, status: 'resolved', resolved_at: new Date().toISOString() }
          : alert
      ));
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-red-100 text-red-800';
      case 'acknowledged': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'flood': return '🌊';
      case 'weather': return '⛈️';
      case 'system': return '⚙️';
      case 'emergency': return '🚨';
      default: return '⚠️';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-3 mb-6">
        <AlertTriangle className="w-6 h-6 text-red-600" />
        <h2 className="text-2xl font-bold text-gray-800">Alert Management</h2>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-red-600 font-medium">Active Alerts</p>
              <p className="text-2xl font-bold text-red-800">{stats.active}</p>
            </div>
            <Bell className="w-8 h-8 text-red-600" />
          </div>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-yellow-600 font-medium">Acknowledged</p>
              <p className="text-2xl font-bold text-yellow-800">{stats.acknowledged}</p>
            </div>
            <Clock className="w-8 h-8 text-yellow-600" />
          </div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600 font-medium">Resolved</p>
              <p className="text-2xl font-bold text-green-800">{stats.resolved}</p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-purple-600 font-medium">Critical</p>
              <p className="text-2xl font-bold text-purple-800">{stats.critical}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-wrap gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">Filters:</span>
        </div>
        
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">All Types</option>
          <option value="flood">Flood</option>
          <option value="weather">Weather</option>
          <option value="system">System</option>
          <option value="emergency">Emergency</option>
        </select>
        
        <select
          value={filterSeverity}
          onChange={(e) => setFilterSeverity(e.target.value)}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">All Statuses</option>
          <option value="active">Active</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="resolved">Resolved</option>
        </select>
        
        <div className="flex items-center gap-2 flex-1 min-w-[200px]">
          <Search className="w-4 h-4 text-gray-600" />
          <input
            type="text"
            placeholder="Search alerts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {filteredAlerts.map((alert) => (
          <div key={alert.id} className={`border rounded-lg p-4 ${alert.severity === 'critical' ? 'border-red-300 bg-red-50' : 'border-gray-200'}`}>
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3 flex-1">
                <div className="text-2xl">{getTypeIcon(alert.type)}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold text-gray-800">{alert.title}</h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getSeverityColor(alert.severity)}`}>
                      {alert.severity.toUpperCase()}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(alert.status)}`}>
                      {alert.status.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-gray-600 mb-2">{alert.message}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>📍 {alert.location}</span>
                    <span>🕒 {new Date(alert.created_at).toLocaleString()}</span>
                    {alert.metadata?.water_level && (
                      <span>🌊 {alert.metadata.water_level}ft</span>
                    )}
                    {alert.metadata?.wind_speed && (
                      <span>💨 {alert.metadata.wind_speed}mph</span>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2 ml-4">
                <button
                  onClick={() => setSelectedAlert(alert)}
                  className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="View Details"
                >
                  <Eye className="w-4 h-4" />
                </button>
                
                {alert.status === 'active' && (
                  <button
                    onClick={() => acknowledgeAlert(alert.id)}
                    disabled={loading}
                    className="px-3 py-1 text-sm bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 transition-colors"
                  >
                    Acknowledge
                  </button>
                )}
                
                {alert.status === 'acknowledged' && (
                  <button
                    onClick={() => resolveAlert(alert.id)}
                    disabled={loading}
                    className="px-3 py-1 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
                  >
                    Resolve
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {filteredAlerts.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>No alerts found matching your criteria.</p>
          </div>
        )}
      </div>

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-gray-800">Alert Details</h3>
              <button
                onClick={() => setSelectedAlert(null)}
                className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="text-3xl">{getTypeIcon(selectedAlert.type)}</div>
                <div>
                  <h4 className="text-lg font-semibold text-gray-800">{selectedAlert.title}</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getSeverityColor(selectedAlert.severity)}`}>
                      {selectedAlert.severity.toUpperCase()}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(selectedAlert.status)}`}>
                      {selectedAlert.status.toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-700">{selectedAlert.message}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-600">Location</p>
                  <p className="text-gray-800">{selectedAlert.location}</p>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Created</p>
                  <p className="text-gray-800">{new Date(selectedAlert.created_at).toLocaleString()}</p>
                </div>
                {selectedAlert.acknowledged_at && (
                  <div>
                    <p className="text-sm font-medium text-gray-600">Acknowledged</p>
                    <p className="text-gray-800">{new Date(selectedAlert.acknowledged_at).toLocaleString()}</p>
                  </div>
                )}
                {selectedAlert.resolved_at && (
                  <div>
                    <p className="text-sm font-medium text-gray-600">Resolved</p>
                    <p className="text-gray-800">{new Date(selectedAlert.resolved_at).toLocaleString()}</p>
                  </div>
                )}
              </div>
              
              {selectedAlert.metadata && (
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-2">Additional Information</p>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    {selectedAlert.metadata.water_level && (
                      <p className="text-sm text-gray-700">Water Level: {selectedAlert.metadata.water_level} ft</p>
                    )}
                    {selectedAlert.metadata.wind_speed && (
                      <p className="text-sm text-gray-700">Wind Speed: {selectedAlert.metadata.wind_speed} mph</p>
                    )}
                    {selectedAlert.metadata.temperature && (
                      <p className="text-sm text-gray-700">Temperature: {selectedAlert.metadata.temperature}°F</p>
                    )}
                    {selectedAlert.metadata.coordinates && (
                      <p className="text-sm text-gray-700">
                        Coordinates: {selectedAlert.metadata.coordinates[0]}, {selectedAlert.metadata.coordinates[1]}
                      </p>
                    )}
                  </div>
                </div>
              )}
              
              <div className="flex gap-3 pt-4">
                {selectedAlert.status === 'active' && (
                  <button
                    onClick={() => {
                      acknowledgeAlert(selectedAlert.id);
                      setSelectedAlert(null);
                    }}
                    disabled={loading}
                    className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 transition-colors"
                  >
                    Acknowledge Alert
                  </button>
                )}
                
                {selectedAlert.status === 'acknowledged' && (
                  <button
                    onClick={() => {
                      resolveAlert(selectedAlert.id);
                      setSelectedAlert(null);
                    }}
                    disabled={loading}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
                  >
                    Resolve Alert
                  </button>
                )}
                
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertManagement;