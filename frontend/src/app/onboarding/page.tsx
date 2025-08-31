'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface Location {
  id: string;
  name: string;
  state: string;
  coordinates: [number, number];
  description: string;
  riskLevel: 'low' | 'medium' | 'high';
}

const COASTAL_LOCATIONS: Location[] = [
  {
    id: 'miami-fl',
    name: 'Miami',
    state: 'Florida',
    coordinates: [25.7617, -80.1918],
    description: 'Major metropolitan area with extensive coastline',
    riskLevel: 'high'
  },
  {
    id: 'charleston-sc',
    name: 'Charleston',
    state: 'South Carolina',
    coordinates: [32.7765, -79.9311],
    description: 'Historic coastal city with tidal flooding concerns',
    riskLevel: 'medium'
  },
  {
    id: 'virginia-beach-va',
    name: 'Virginia Beach',
    state: 'Virginia',
    coordinates: [36.8529, -75.9780],
    description: 'Popular beach destination with storm surge risks',
    riskLevel: 'medium'
  },
  {
    id: 'outer-banks-nc',
    name: 'Outer Banks',
    state: 'North Carolina',
    coordinates: [35.5582, -75.4665],
    description: 'Barrier islands vulnerable to hurricanes',
    riskLevel: 'high'
  },
  {
    id: 'galveston-tx',
    name: 'Galveston',
    state: 'Texas',
    coordinates: [29.3013, -94.7977],
    description: 'Gulf Coast city with hurricane history',
    riskLevel: 'high'
  },
  {
    id: 'san-diego-ca',
    name: 'San Diego',
    state: 'California',
    coordinates: [32.7157, -117.1611],
    description: 'Pacific Coast with moderate coastal risks',
    riskLevel: 'low'
  }
];

export default function OnboardingPage() {
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const [customLocation, setCustomLocation] = useState({ name: '', latitude: '', longitude: '' });
  const [useCustomLocation, setUseCustomLocation] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const { getSession } = await import('../../../lib/supabase');
        const { session } = await getSession();
        if (!session?.access_token) {
          router.push('/login');
        }
      } catch (error) {
        router.push('/login');
      }
    };

    checkAuth();
  }, [router]);

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      let locationData;

      if (useCustomLocation) {
        locationData = {
          name: customLocation.name,
          latitude: parseFloat(customLocation.latitude),
          longitude: parseFloat(customLocation.longitude),
          is_custom: true
        };
      } else {
        const location = COASTAL_LOCATIONS.find(loc => loc.id === selectedLocation);
        if (!location) {
          setError('Please select a location');
          setIsLoading(false);
          return;
        }
        locationData = {
          name: `${location.name}, ${location.state}`,
          latitude: location.coordinates[0],
          longitude: location.coordinates[1],
          is_custom: false
        };
      }

      const response = await fetch('http://localhost:8000/api/v1/auth/set-location', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(locationData),
      });

      if (response.ok) {
        router.push('/dashboard');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to set location');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-teal-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full space-y-8">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="mx-auto h-16 w-16 bg-gradient-to-r from-blue-500 to-teal-500 rounded-full flex items-center justify-center mb-4">
              <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900">Choose Your Location</h2>
            <p className="mt-2 text-gray-600">Select your coastal area to receive personalized monitoring and alerts</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Location Selection Toggle */}
            <div className="flex items-center space-x-4 mb-6">
              <button
                type="button"
                onClick={() => setUseCustomLocation(false)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  !useCustomLocation
                    ? 'bg-blue-100 text-blue-700 border-2 border-blue-200'
                    : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-gray-200'
                }`}
              >
                Popular Locations
              </button>
              <button
                type="button"
                onClick={() => setUseCustomLocation(true)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  useCustomLocation
                    ? 'bg-blue-100 text-blue-700 border-2 border-blue-200'
                    : 'bg-gray-100 text-gray-600 border-2 border-transparent hover:bg-gray-200'
                }`}
              >
                Custom Location
              </button>
            </div>

            {!useCustomLocation ? (
              /* Popular Locations */
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {COASTAL_LOCATIONS.map((location) => (
                  <div
                    key={location.id}
                    className={`relative p-4 border-2 rounded-lg cursor-pointer transition-all hover:shadow-md ${
                      selectedLocation === location.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedLocation(location.id)}
                  >
                    <input
                      type="radio"
                      name="location"
                      value={location.id}
                      checked={selectedLocation === location.id}
                      onChange={() => setSelectedLocation(location.id)}
                      className="absolute top-4 right-4"
                    />
                    <div className="pr-8">
                      <h3 className="font-semibold text-gray-900">{location.name}</h3>
                      <p className="text-sm text-gray-600">{location.state}</p>
                      <p className="text-xs text-gray-500 mt-1">{location.description}</p>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-2 ${getRiskLevelColor(location.riskLevel)}`}>
                        {location.riskLevel.toUpperCase()} RISK
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              /* Custom Location */
              <div className="space-y-4">
                <div>
                  <label htmlFor="locationName" className="block text-sm font-medium text-gray-700 mb-2">
                    Location Name
                  </label>
                  <input
                    id="locationName"
                    type="text"
                    required={useCustomLocation}
                    value={customLocation.name}
                    onChange={(e) => setCustomLocation(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    placeholder="e.g., My Beach House, Myrtle Beach"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="latitude" className="block text-sm font-medium text-gray-700 mb-2">
                      Latitude
                    </label>
                    <input
                      id="latitude"
                      type="number"
                      step="any"
                      required={useCustomLocation}
                      value={customLocation.latitude}
                      onChange={(e) => setCustomLocation(prev => ({ ...prev, latitude: e.target.value }))}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                      placeholder="e.g., 33.6891"
                    />
                  </div>
                  <div>
                    <label htmlFor="longitude" className="block text-sm font-medium text-gray-700 mb-2">
                      Longitude
                    </label>
                    <input
                      id="longitude"
                      type="number"
                      step="any"
                      required={useCustomLocation}
                      value={customLocation.longitude}
                      onChange={(e) => setCustomLocation(prev => ({ ...prev, longitude: e.target.value }))}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                      placeholder="e.g., -78.8867"
                    />
                  </div>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-sm text-blue-700">
                    <strong>Tip:</strong> You can find coordinates by searching your location on Google Maps and right-clicking to get the coordinates.
                  </p>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || (!useCustomLocation && !selectedLocation) || (useCustomLocation && (!customLocation.name || !customLocation.latitude || !customLocation.longitude))}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isLoading ? (
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : null}
              {isLoading ? 'Setting up...' : 'Continue to Dashboard'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}