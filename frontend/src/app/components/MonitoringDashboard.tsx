'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import {
  Play,
  Square,
  RefreshCw,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  MapPin,
  TrendingUp,
  Waves,
  Cloud,
  Thermometer
} from 'lucide-react';

interface MonitoringStatus {
  is_active: boolean;
  started_at: string;
  stations_monitored: number;
  last_check: string;
  alerts_generated_today: number;
}

interface AlertStatistics {
  period_days: number;
  total_alerts: number;
  alerts_by_type: Record<string, number>;
  alerts_by_severity: Record<string, number>;
  average_alerts_per_day: number;
  most_active_location: string;
}

interface StationData {
  id: string;
  name: string;
  location: string;
  status: 'online' | 'offline' | 'warning';
  last_update: string;
  tide_level: number;
  wave_height: number;
  temperature: number;
  wind_speed: number;
}

const MonitoringDashboard: React.FC = () => {
  const [monitoringStatus, setMonitoringStatus] = useState<MonitoringStatus | null>(null);
  const [alertStats, setAlertStats] = useState<AlertStatistics | null>(null);
  const [stations, setStations] = useState<StationData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  // Mock data for demonstration
  useEffect(() => {
    const mockStatus: MonitoringStatus = {
      is_active: true,
      started_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      stations_monitored: 5,
      last_check: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      alerts_generated_today: 3
    };

    const mockStats: AlertStatistics = {
      period_days: 30,
      total_alerts: 15,
      alerts_by_type: {
        flood: 6,
        storm_surge: 4,
        high_waves: 5
      },
      alerts_by_severity: {
        low: 3,
        medium: 7,
        high: 4,
        critical: 1
      },
      average_alerts_per_day: 0.5,
      most_active_location: 'Chennai Marina Beach'
    };

    const mockStations: StationData[] = [
      {
        id: 'station_001',
        name: 'Marina Beach Station',
        location: 'Chennai Marina Beach',
        status: 'online',
        last_update: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
        tide_level: 1.2,
        wave_height: 0.8,
        temperature: 28.5,
        wind_speed: 12.3
      },
      {
        id: 'station_002',
        name: 'Besant Nagar Station',
        location: 'Besant Nagar Beach',
        status: 'warning',
        last_update: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        tide_level: 1.8,
        wave_height: 1.2,
        temperature: 29.1,
        wind_speed: 18.7
      },
      {
        id: 'station_003',
        name: 'Pondicherry Station',
        location: 'Pondicherry Coast',
        status: 'online',
        last_update: new Date(Date.now() - 1 * 60 * 1000).toISOString(),
        tide_level: 0.9,
        wave_height: 0.6,
        temperature: 27.8,
        wind_speed: 8.9
      },
      {
        id: 'station_004',
        name: 'Kanyakumari Station',
        location: 'Kanyakumari',
        status: 'offline',
        last_update: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
        tide_level: 0,
        wave_height: 0,
        temperature: 0,
        wind_speed: 0
      },
      {
        id: 'station_005',
        name: 'Rameswaram Station',
        location: 'Rameswaram',
        status: 'online',
        last_update: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
        tide_level: 1.1,
        wave_height: 0.7,
        temperature: 28.9,
        wind_speed: 11.2
      }
    ];

    setMonitoringStatus(mockStatus);
    setAlertStats(mockStats);
    setStations(mockStations);
  }, []);

  const handleStartMonitoring = async () => {
    setLoading(true);
    setError(null);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setMonitoringStatus(prev => prev ? { ...prev, is_active: true, started_at: new Date().toISOString() } : null);
    } catch (err) {
      setError('Failed to start monitoring');
    } finally {
      setLoading(false);
    }
  };

  const handleStopMonitoring = async () => {
    setLoading(true);
    setError(null);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setMonitoringStatus(prev => prev ? { ...prev, is_active: false } : null);
    } catch (err) {
      setError('Failed to stop monitoring');
    } finally {
      setLoading(false);
    }
  };

  const handleManualCheck = async () => {
    setLoading(true);
    setError(null);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      setLastRefresh(new Date());
      setMonitoringStatus(prev => prev ? { ...prev, last_check: new Date().toISOString() } : null);
    } catch (err) {
      setError('Failed to perform manual check');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'offline':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-100 text-green-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'offline':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  return (
    <div className="space-y-6">
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {/* Control Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Monitoring Control Panel
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className={`h-3 w-3 rounded-full ${
                  monitoringStatus?.is_active ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
                }`} />
                <span className="font-medium">
                  {monitoringStatus?.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              {monitoringStatus?.is_active && (
                <span className="text-sm text-gray-600">
                  Running for {formatTimeAgo(monitoringStatus.started_at)}
                </span>
              )}
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleManualCheck}
                disabled={loading}
                variant="outline"
                size="sm"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Manual Check
              </Button>
              {monitoringStatus?.is_active ? (
                <Button
                  onClick={handleStopMonitoring}
                  disabled={loading}
                  variant="destructive"
                  size="sm"
                >
                  <Square className="h-4 w-4 mr-2" />
                  Stop Monitoring
                </Button>
              ) : (
                <Button
                  onClick={handleStartMonitoring}
                  disabled={loading}
                  size="sm"
                >
                  <Play className="h-4 w-4 mr-2" />
                  Start Monitoring
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="stations">Monitoring Stations</TabsTrigger>
          <TabsTrigger value="statistics">Alert Statistics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <Card>
              <CardContent className="p-4 sm:p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Stations Monitored</p>
                    <p className="text-2xl font-bold">{monitoringStatus?.stations_monitored || 0}</p>
                  </div>
                  <MapPin className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 sm:p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Alerts Today</p>
                    <p className="text-2xl font-bold">{monitoringStatus?.alerts_generated_today || 0}</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 sm:p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Last Check</p>
                    <p className="text-sm font-bold">
                      {monitoringStatus ? formatTimeAgo(monitoringStatus.last_check) : 'Never'}
                    </p>
                  </div>
                  <Clock className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 sm:p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">System Status</p>
                    <p className="text-sm font-bold text-green-600">Operational</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="stations" className="space-y-4">
          <div className="grid gap-4">
            {stations.map((station) => (
              <Card key={station.id}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(station.status)}
                      <div>
                        <h3 className="font-semibold">{station.name}</h3>
                        <p className="text-sm text-gray-600">{station.location}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(station.status)}>
                        {station.status.charAt(0).toUpperCase() + station.status.slice(1)}
                      </Badge>
                      <span className="text-xs text-gray-500">
                        {formatTimeAgo(station.last_update)}
                      </span>
                    </div>
                  </div>
                  
                  {station.status !== 'offline' && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="flex items-center gap-2">
                        <Waves className="h-4 w-4 text-blue-500" />
                        <div>
                          <p className="text-xs text-gray-600">Tide Level</p>
                          <p className="text-sm font-semibold">{station.tide_level}m</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-cyan-500" />
                        <div>
                          <p className="text-xs text-gray-600">Wave Height</p>
                          <p className="text-sm font-semibold">{station.wave_height}m</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Thermometer className="h-4 w-4 text-red-500" />
                        <div>
                          <p className="text-xs text-gray-600">Temperature</p>
                          <p className="text-sm font-semibold">{station.temperature}°C</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Cloud className="h-4 w-4 text-gray-500" />
                        <div>
                          <p className="text-xs text-gray-600">Wind Speed</p>
                          <p className="text-sm font-semibold">{station.wind_speed} km/h</p>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="statistics" className="space-y-4">
          {alertStats && (
            <div className="grid gap-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Alerts by Type (Last {alertStats.period_days} days)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(alertStats.alerts_by_type).map(([type, count]) => (
                        <div key={type} className="flex items-center justify-between">
                          <span className="capitalize">{type.replace('_', ' ')}</span>
                          <div className="flex items-center gap-2">
                            <Progress 
                              value={(count / alertStats.total_alerts) * 100} 
                              className="w-20 h-2" 
                            />
                            <span className="text-sm font-semibold w-8">{count}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Alerts by Severity</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {Object.entries(alertStats.alerts_by_severity).map(([severity, count]) => {
                        const colors = {
                          low: 'bg-green-500',
                          medium: 'bg-yellow-500',
                          high: 'bg-orange-500',
                          critical: 'bg-red-500'
                        };
                        return (
                          <div key={severity} className="flex items-center justify-between">
                            <span className="capitalize">{severity}</span>
                            <div className="flex items-center gap-2">
                              <div className="w-20 bg-gray-200 rounded-full h-2">
                                <div 
                                  className={`h-2 rounded-full ${colors[severity as keyof typeof colors]}`}
                                  style={{ width: `${(count / alertStats.total_alerts) * 100}%` }}
                                />
                              </div>
                              <span className="text-sm font-semibold w-8">{count}</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
                <Card>
                  <CardContent className="p-4 sm:p-6">
                    <div className="text-center">
                      <p className="text-2xl font-bold">{alertStats.total_alerts}</p>
                      <p className="text-sm text-gray-600">Total Alerts</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 sm:p-6">
                    <div className="text-center">
                      <p className="text-2xl font-bold">{alertStats.average_alerts_per_day}</p>
                      <p className="text-sm text-gray-600">Avg. per Day</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4 sm:p-6">
                    <div className="text-center">
                      <p className="text-sm font-bold">{alertStats.most_active_location}</p>
                      <p className="text-sm text-gray-600">Most Active Location</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MonitoringDashboard;