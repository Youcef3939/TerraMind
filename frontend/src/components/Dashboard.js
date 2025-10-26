import React, { useState, useEffect } from 'react';
import { ArrowLeft, Brain, Satellite, Cloud, AlertTriangle, TrendingUp, Download } from 'lucide-react';
import axios from 'axios';

function Dashboard({ aoi, onAnalyze, isAnalyzing, onBack }) {
  const [satelliteData, setSatelliteData] = useState(null);
  const [climateData, setClimateData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadPreviewData();
  }, [aoi]);

  const loadPreviewData = async () => {
    setIsLoading(true);
    try {
      const satelliteResponse = await axios.get('http://localhost:8000/satellite/imagery', {
        params: {
          lat: aoi.center[0],
          lon: aoi.center[1],
          radius_km: aoi.radius
        }
      });
      setSatelliteData(satelliteResponse.data);

      const climateResponse = await axios.get('http://localhost:8000/climate/forecast', {
        params: {
          lat: aoi.center[0],
          lon: aoi.center[1]
        }
      });
      setClimateData(climateResponse.data);
    } catch (error) {
      console.error('Error loading preview data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBack}
            className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Map
          </button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Analysis Dashboard</h2>
            <p className="text-gray-600">
              Center: {aoi.center[0].toFixed(4)}, {aoi.center[1].toFixed(4)} | 
              Radius: {aoi.radius} km
            </p>
          </div>
        </div>

        <button
          onClick={onAnalyze}
          disabled={isAnalyzing}
          className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-semibold flex items-center transition-colors"
        >
          {isAnalyzing ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          ) : (
            <Brain className="w-4 h-4 mr-2" />
          )}
          {isAnalyzing ? 'Analyzing...' : 'Start Analysis'}
        </button>
      </div>

      {/* Preview Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Satellite Imagery Preview */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center">
              <Satellite className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Satellite Imagery</h3>
            </div>
          </div>
          
          <div className="p-6">
            {isLoading ? (
              <div className="flex items-center justify-center h-48">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : satelliteData ? (
              <div className="space-y-4">
                <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <Satellite className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">Satellite Image Preview</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {satelliteData.coordinates.lat.toFixed(4)}, {satelliteData.coordinates.lon.toFixed(4)}
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Resolution:</span>
                    <span className="ml-2 font-medium">10m</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Date:</span>
                    <span className="ml-2 font-medium">Recent</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <Satellite className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>No satellite data available</p>
              </div>
            )}
          </div>
        </div>

        {/* Climate Forecast Preview */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center">
              <Cloud className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-gray-900">Climate Forecast</h3>
            </div>
          </div>
          
          <div className="p-6">
            {isLoading ? (
              <div className="flex items-center justify-center h-48">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : climateData ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {climateData.forecast?.current?.temperature || 'N/A'}°C
                    </div>
                    <div className="text-sm text-gray-600">Temperature</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {climateData.forecast?.current?.humidity || 'N/A'}%
                    </div>
                    <div className="text-sm text-gray-600">Humidity</div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Drought Risk:</span>
                    <span className={`font-medium ${
                      climateData.risks?.drought_risk === 'high' ? 'text-red-600' :
                      climateData.risks?.drought_risk === 'moderate' ? 'text-yellow-600' : 'text-green-600'
                    }`}>
                      {climateData.risks?.drought_risk || 'Unknown'}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Flood Risk:</span>
                    <span className={`font-medium ${
                      climateData.risks?.flood_risk === 'high' ? 'text-red-600' :
                      climateData.risks?.flood_risk === 'moderate' ? 'text-yellow-600' : 'text-green-600'
                    }`}>
                      {climateData.risks?.flood_risk || 'Unknown'}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <Cloud className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>No climate data available</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Analysis Preview */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center">
            <Brain className="w-5 h-5 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Analysis Preview</h3>
          </div>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Vegetation Analysis</h4>
              <p className="text-sm text-gray-600">
                NDVI/NDWI analysis, crop health assessment, and vegetation change detection
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Cloud className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Climate Risk Assessment</h4>
              <p className="text-sm text-gray-600">
                Drought, flood, and heat stress risk prediction using weather data
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <AlertTriangle className="w-8 h-8 text-orange-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-2">Environmental Monitoring</h4>
              <p className="text-sm text-gray-600">
                Land degradation detection, deforestation monitoring, and pollution assessment
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        <button
          onClick={onBack}
          className="px-6 py-3 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors"
        >
          Back to Map
        </button>
        
        <button
          onClick={onAnalyze}
          disabled={isAnalyzing}
          className="px-8 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-semibold flex items-center transition-colors"
        >
          {isAnalyzing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Analyzing...
            </>
          ) : (
            <>
              <Brain className="w-4 h-4 mr-2" />
              Start Comprehensive Analysis
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default Dashboard;