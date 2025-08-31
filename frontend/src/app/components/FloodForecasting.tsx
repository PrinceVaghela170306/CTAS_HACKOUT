'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Brain, TrendingUp, AlertTriangle, CheckCircle, Clock, Target, Zap, Activity } from 'lucide-react';

interface FloodPrediction {
  flood_probability: number;
  risk_level: string;
  confidence: number;
  time_to_peak: number;
  duration_hours: number;
  factors: Record<string, number>;
  model_version: string;
  prediction_time: string;
  model_type: string;
}

interface ForecastTimeline {
  timestamp: string;
  flood_probability: number;
  risk_level: string;
  confidence: number;
}

interface ModelPerformance {
  accuracy: number;
  loss?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  training_samples: number;
  last_trained: string;
}

interface FloodForecastingProps {
  stationId?: string;
  stationName?: string;
  latitude?: number;
  longitude?: number;
}

const FloodForecasting: React.FC<FloodForecastingProps> = ({
  stationId = 'station-001',
  stationName = 'Miami Beach Station',
  latitude = 25.7907,
  longitude = -80.1300
}) => {
  const [currentPrediction, setCurrentPrediction] = useState<FloodPrediction | null>(null);
  const [forecastTimeline, setForecastTimeline] = useState<ForecastTimeline[]>([]);
  const [modelPerformance, setModelPerformance] = useState<Record<string, ModelPerformance>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [activeTab, setActiveTab] = useState('prediction');

  // Mock current environmental conditions
  const [currentConditions] = useState({
    tide_level: 1.8,
    wave_height: 1.5,
    storm_surge: 0.3,
    rainfall_mm: 12.5,
    wind_speed_kmh: 35,
    atmospheric_pressure: 1008.2,
    temperature_c: 28.5,
    humidity_percent: 78
  });

  // Generate mock historical data for LSTM
  const generateHistoricalData = () => {
    const data = [];
    const now = new Date();
    
    for (let i = 48; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
      data.push({
        timestamp: timestamp.toISOString(),
        tide_level: 1.5 + Math.sin(i * 0.26) * 1.2 + (Math.random() - 0.5) * 0.3,
        wave_height: 1.0 + Math.sin(i * 0.15) * 0.8 + (Math.random() - 0.5) * 0.4,
        storm_surge: Math.max(0, 0.2 + (Math.random() - 0.5) * 0.4),
        rainfall_mm: Math.max(0, Math.random() * 20),
        wind_speed_kmh: 20 + Math.random() * 30,
        atmospheric_pressure: 1010 + (Math.random() - 0.5) * 20,
        temperature_c: 25 + Math.random() * 8,
        humidity_percent: 65 + Math.random() * 25
      });
    }
    
    return data;
  };

  // Simulate API calls
  const fetchFloodPrediction = async () => {
    setIsLoading(true);
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Mock LSTM prediction
    const prediction: FloodPrediction = {
      flood_probability: 0.35 + Math.random() * 0.4,
      risk_level: Math.random() > 0.6 ? 'high' : Math.random() > 0.3 ? 'medium' : 'low',
      confidence: 0.82 + Math.random() * 0.15,
      time_to_peak: Math.floor(6 + Math.random() * 12),
      duration_hours: Math.floor(4 + Math.random() * 8),
      factors: {
        tide_impact: Math.random() * 0.8,
        wave_impact: Math.random() * 0.6,
        surge_impact: Math.random() * 0.4,
        rainfall_impact: Math.random() * 0.7,
        wind_impact: Math.random() * 0.5
      },
      model_version: '2.1.0',
      prediction_time: new Date().toISOString(),
      model_type: 'LSTM'
    };
    
    setCurrentPrediction(prediction);
    
    // Generate forecast timeline
    const timeline: ForecastTimeline[] = [];
    const baseTime = new Date();
    
    for (let i = 0; i < 48; i += 2) {
      const timestamp = new Date(baseTime.getTime() + i * 60 * 60 * 1000);
      const prob = prediction.flood_probability + (Math.random() - 0.5) * 0.3;
      
      timeline.push({
        timestamp: timestamp.toISOString(),
        flood_probability: Math.max(0, Math.min(1, prob)),
        risk_level: prob > 0.7 ? 'high' : prob > 0.4 ? 'medium' : 'low',
        confidence: 0.75 + Math.random() * 0.2
      });
    }
    
    setForecastTimeline(timeline);
    setLastUpdate(new Date());
    setIsLoading(false);
  };

  const fetchModelPerformance = async () => {
    // Mock model performance data
    const performance = {
      flood_model: {
        accuracy: 0.89,
        loss: 0.15,
        precision: 0.87,
        recall: 0.91,
        f1_score: 0.89,
        training_samples: 15420,
        last_trained: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
      },
      tide_model: {
        accuracy: 0.94,
        training_samples: 28500,
        last_trained: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
      },
      storm_surge_model: {
        accuracy: 0.86,
        training_samples: 8200,
        last_trained: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
      }
    };
    
    setModelPerformance(performance);
  };

  const trainModel = async () => {
    setIsTraining(true);
    
    // Simulate training time
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Update model performance after training
    const updatedPerformance = { ...modelPerformance };
    if (updatedPerformance.flood_model) {
      updatedPerformance.flood_model.accuracy = Math.min(0.95, updatedPerformance.flood_model.accuracy + 0.02);
      updatedPerformance.flood_model.last_trained = new Date().toISOString();
    }
    
    setModelPerformance(updatedPerformance);
    setIsTraining(false);
  };

  useEffect(() => {
    fetchFloodPrediction();
    fetchModelPerformance();
  }, []);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchFloodPrediction();
    }, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Brain className="h-8 w-8 text-blue-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">AI Flood Forecasting</h2>
            <p className="text-gray-600">{stationName} • LSTM Neural Network</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <Badge variant="outline" className="flex items-center space-x-1">
            <Clock className="h-3 w-3" />
            <span>Updated {formatTimestamp(lastUpdate.toISOString())}</span>
          </Badge>
          <Button onClick={fetchFloodPrediction} disabled={isLoading} size="sm">
            {isLoading ? 'Updating...' : 'Refresh'}
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="prediction">Current Prediction</TabsTrigger>
          <TabsTrigger value="forecast">48h Forecast</TabsTrigger>
          <TabsTrigger value="performance">Model Performance</TabsTrigger>
          <TabsTrigger value="training">Model Training</TabsTrigger>
        </TabsList>

        <TabsContent value="prediction" className="space-y-6">
          {currentPrediction && (
            <>
              {/* Current Risk Assessment */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <AlertTriangle className="h-5 w-5" />
                    <span>Current Flood Risk Assessment</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className={`inline-flex items-center px-4 py-2 rounded-full text-lg font-semibold border ${getRiskColor(currentPrediction.risk_level)}`}>
                        {currentPrediction.risk_level.toUpperCase()}
                      </div>
                      <p className="text-sm text-gray-600 mt-2">Risk Level</p>
                    </div>
                    
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600">
                        {(currentPrediction.flood_probability * 100).toFixed(1)}%
                      </div>
                      <p className="text-sm text-gray-600">Flood Probability</p>
                      <Progress value={currentPrediction.flood_probability * 100} className="mt-2" />
                    </div>
                    
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-600">
                        {(currentPrediction.confidence * 100).toFixed(1)}%
                      </div>
                      <p className="text-sm text-gray-600">Model Confidence</p>
                      <Progress value={currentPrediction.confidence * 100} className="mt-2" />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-xl font-semibold text-gray-900">{currentPrediction.time_to_peak}h</div>
                      <p className="text-sm text-gray-600">Time to Peak</p>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-xl font-semibold text-gray-900">{currentPrediction.duration_hours}h</div>
                      <p className="text-sm text-gray-600">Duration</p>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-xl font-semibold text-gray-900">{currentPrediction.model_type}</div>
                      <p className="text-sm text-gray-600">Model Type</p>
                    </div>
                    <div className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-xl font-semibold text-gray-900">v{currentPrediction.model_version}</div>
                      <p className="text-sm text-gray-600">Version</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Contributing Factors */}
              <Card>
                <CardHeader>
                  <CardTitle>Contributing Factors Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Object.entries(currentPrediction.factors).map(([factor, impact]) => (
                      <div key={factor} className="flex items-center justify-between">
                        <span className="text-sm font-medium capitalize">
                          {factor.replace('_', ' ')}
                        </span>
                        <div className="flex items-center space-x-3">
                          <Progress value={impact * 100} className="w-24" />
                          <span className="text-sm text-gray-600 w-12">
                            {(impact * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="forecast" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>48-Hour Flood Probability Forecast</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={forecastTimeline}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={formatTimestamp}
                      interval="preserveStartEnd"
                    />
                    <YAxis 
                      domain={[0, 1]}
                      tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                    />
                    <Tooltip 
                      labelFormatter={(value) => formatTimestamp(value as string)}
                      formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, 'Flood Probability']}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="flood_probability" 
                      stroke="#3b82f6" 
                      fill="#3b82f6" 
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {Object.entries(modelPerformance).map(([modelName, metrics]) => (
              <Card key={modelName}>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Target className="h-5 w-5" />
                    <span>{modelName.replace('_', ' ').toUpperCase()}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Accuracy</span>
                      <span className="font-semibold">{(metrics.accuracy * 100).toFixed(1)}%</span>
                    </div>
                    
                    {metrics.precision && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Precision</span>
                        <span className="font-semibold">{(metrics.precision * 100).toFixed(1)}%</span>
                      </div>
                    )}
                    
                    {metrics.recall && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Recall</span>
                        <span className="font-semibold">{(metrics.recall * 100).toFixed(1)}%</span>
                      </div>
                    )}
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Training Samples</span>
                      <span className="font-semibold">{metrics.training_samples.toLocaleString()}</span>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Last Trained</span>
                      <span className="font-semibold text-xs">
                        {new Date(metrics.last_trained).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="training" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5" />
                <span>Model Training & Optimization</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <Alert>
                  <Activity className="h-4 w-4" />
                  <AlertDescription>
                    Train the LSTM model with the latest environmental data to improve prediction accuracy.
                    Training typically takes 2-5 minutes depending on dataset size.
                  </AlertDescription>
                </Alert>
                
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-semibold">Flood Prediction Model (LSTM)</h4>
                    <p className="text-sm text-gray-600">
                      Current accuracy: {modelPerformance.flood_model ? (modelPerformance.flood_model.accuracy * 100).toFixed(1) : 'N/A'}%
                    </p>
                  </div>
                  <Button 
                    onClick={trainModel} 
                    disabled={isTraining}
                    className="flex items-center space-x-2"
                  >
                    {isTraining ? (
                      <>
                        <Activity className="h-4 w-4 animate-spin" />
                        <span>Training...</span>
                      </>
                    ) : (
                      <>
                        <Zap className="h-4 w-4" />
                        <span>Retrain Model</span>
                      </>
                    )}
                  </Button>
                </div>
                
                {isTraining && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Training Progress</span>
                      <span>Processing...</span>
                    </div>
                    <Progress value={65} className="w-full" />
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FloodForecasting;