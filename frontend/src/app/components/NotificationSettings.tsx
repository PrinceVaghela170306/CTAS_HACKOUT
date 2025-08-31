'use client';

import React, { useState, useEffect } from 'react';
import { Bell, Mail, MessageSquare, Smartphone, Settings, History } from 'lucide-react';

interface NotificationPreferences {
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  flood_alerts: boolean;
  weather_updates: boolean;
  system_maintenance: boolean;
  emergency_only: boolean;
}

interface NotificationHistory {
  id: string;
  type: 'email' | 'sms' | 'push';
  title: string;
  message: string;
  sent_at: string;
  status: 'sent' | 'delivered' | 'failed';
}

interface NotificationStats {
  total_sent: number;
  delivered: number;
  failed: number;
  email_count: number;
  sms_count: number;
  push_count: number;
}

interface NotificationSettingsProps {
  userId: string;
}

const NotificationSettings: React.FC<NotificationSettingsProps> = ({ userId }) => {
  const [activeTab, setActiveTab] = useState<'preferences' | 'history'>('preferences');
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    email_enabled: true,
    sms_enabled: false,
    push_enabled: true,
    flood_alerts: true,
    weather_updates: true,
    system_maintenance: false,
    emergency_only: false
  });
  const [history, setHistory] = useState<NotificationHistory[]>([]);
  const [stats, setStats] = useState<NotificationStats>({
    total_sent: 0,
    delivered: 0,
    failed: 0,
    email_count: 0,
    sms_count: 0,
    push_count: 0
  });
  const [loading, setLoading] = useState(false);

  // Mock data for demonstration
  useEffect(() => {
    // Simulate loading notification history
    const mockHistory: NotificationHistory[] = [
      {
        id: '1',
        type: 'email',
        title: 'Flood Alert - High Risk',
        message: 'Flood risk level has increased to HIGH for your area. Please take necessary precautions.',
        sent_at: '2024-01-15T10:30:00Z',
        status: 'delivered'
      },
      {
        id: '2',
        type: 'push',
        title: 'Weather Update',
        message: 'Storm surge warning issued for the next 6 hours.',
        sent_at: '2024-01-15T08:15:00Z',
        status: 'delivered'
      },
      {
        id: '3',
        type: 'sms',
        title: 'Emergency Alert',
        message: 'URGENT: Evacuation recommended for coastal areas.',
        sent_at: '2024-01-14T22:45:00Z',
        status: 'sent'
      }
    ];
    setHistory(mockHistory);

    // Simulate loading stats
    setStats({
      total_sent: 45,
      delivered: 42,
      failed: 3,
      email_count: 20,
      sms_count: 8,
      push_count: 17
    });
  }, []);

  const handlePreferenceChange = (key: keyof NotificationPreferences, value: boolean) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  };

  const savePreferences = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Preferences saved:', preferences);
    } catch (error) {
      console.error('Failed to save preferences:', error);
    } finally {
      setLoading(false);
    }
  };



  const getStatusColor = (status: string) => {
    switch (status) {
      case 'delivered': return 'text-green-600';
      case 'sent': return 'text-blue-600';
      case 'failed': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'email': return <Mail className="w-4 h-4" />;
      case 'sms': return <MessageSquare className="w-4 h-4" />;
      case 'push': return <Smartphone className="w-4 h-4" />;
      default: return <Bell className="w-4 h-4" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-3 mb-6">
        <Bell className="w-6 h-6 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-800">Notification Settings</h2>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        <button
          onClick={() => setActiveTab('preferences')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-colors ${
            activeTab === 'preferences'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          <Settings className="w-4 h-4" />
          Preferences
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-colors ${
            activeTab === 'history'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          <History className="w-4 h-4" />
          History
        </button>

      </div>

      {/* Preferences Tab */}
      {activeTab === 'preferences' && (
        <div className="space-y-6">
          {/* Notification Channels */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Notification Channels</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Mail className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium text-gray-800">Email Notifications</p>
                    <p className="text-sm text-gray-600">Receive alerts via email</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={preferences.email_enabled}
                    onChange={(e) => handlePreferenceChange('email_enabled', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <MessageSquare className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="font-medium text-gray-800">SMS Notifications</p>
                    <p className="text-sm text-gray-600">Receive alerts via text message</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={preferences.sms_enabled}
                    onChange={(e) => handlePreferenceChange('sms_enabled', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Smartphone className="w-5 h-5 text-purple-600" />
                  <div>
                    <p className="font-medium text-gray-800">Push Notifications</p>
                    <p className="text-sm text-gray-600">Receive alerts on your device</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={preferences.push_enabled}
                    onChange={(e) => handlePreferenceChange('push_enabled', e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </div>

          {/* Alert Types */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Alert Types</h3>
            <div className="space-y-3">
              {[
                { key: 'flood_alerts', label: 'Flood Alerts', desc: 'Critical flood warnings and risk updates' },
                { key: 'weather_updates', label: 'Weather Updates', desc: 'Storm surge and weather condition alerts' },
                { key: 'system_maintenance', label: 'System Maintenance', desc: 'Scheduled maintenance notifications' },
                { key: 'emergency_only', label: 'Emergency Only', desc: 'Only receive critical emergency alerts' }
              ].map(({ key, label, desc }) => (
                <div key={key} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-800">{label}</p>
                    <p className="text-sm text-gray-600">{desc}</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={preferences[key as keyof NotificationPreferences] as boolean}
                      onChange={(e) => handlePreferenceChange(key as keyof NotificationPreferences, e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={savePreferences}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-blue-600 font-medium">Total Sent</p>
              <p className="text-2xl font-bold text-blue-800">{stats.total_sent}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-sm text-green-600 font-medium">Delivered</p>
              <p className="text-2xl font-bold text-green-800">{stats.delivered}</p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <p className="text-sm text-red-600 font-medium">Failed</p>
              <p className="text-2xl font-bold text-red-800">{stats.failed}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm text-purple-600 font-medium">Success Rate</p>
              <p className="text-2xl font-bold text-purple-800">
                {stats.total_sent > 0 ? Math.round((stats.delivered / stats.total_sent) * 100) : 0}%
              </p>
            </div>
          </div>

          {/* Notification History */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Notifications</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {history.map((notification) => (
                <div key={notification.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className="mt-1">
                        {getTypeIcon(notification.type)}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-800">{notification.title}</h4>
                        <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                        <p className="text-xs text-gray-500 mt-2">
                          {new Date(notification.sent_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${getStatusColor(notification.status)}`}>
                      {notification.status.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}


    </div>
  );
};

export default NotificationSettings;