import React, { useState } from 'react';
import { ArrowLeft, Download, TrendingUp, Cloud, AlertTriangle, Brain, MapPin, Calendar } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function AnalysisResults({ result, onBack, onDownload }) {
  const [activeTab, setActiveTab] = useState('overview');

  const vegetationData = result.vegetation_analysis || {};
  const climateData = result.climate_analysis || {};
  const degradationData = result.degradation_analysis || {};
  const predictions = result.predictions || {};

  const ndviChartData = {
    labels: ['Historical', 'Current', '3 Months', '6 Months', '12 Months'],
    datasets: [
      {
        label: 'NDVI',
        data: [
          vegetationData.ndvi_historical || 0,
          vegetationData.ndvi_current || 0,
          predictions.predicted_ndvi_3_months || 0,
          predictions.predicted_ndvi_6_months || 0,
          predictions.predicted_ndvi_12_months || 0
        ],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Vegetation Health Trend (NDVI)'
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1
      }
    }
  };

  const getRiskColor = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'high':
      case 'severe':
        return 'text-red-600 bg-red-50';
      case 'moderate':
        return 'text-yellow-600 bg-yellow-50';
      case 'low':
      case 'minimal':
        return 'text-green-600 bg-green-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getHealthColor = (health) => {
    switch (health?.toLowerCase()) {
      case 'good':
        return 'text-green-600 bg-green-50';
      case 'fair':
        return 'text-yellow-600 bg-yellow-50';
      case 'poor':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
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
            <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
            <p className="text-gray-600">
              AOI ID: {result.aoi_id} | Generated: {new Date(result.timestamp).toLocaleString()}
            </p>
          </div>
        </div>

        <button
          onClick={onDownload}
          className="flex items-center px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors"
        >
          <Download className="w-4 h-4 mr-2" />
          Download Report
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: Brain },
            { id: 'vegetation', label: 'Vegetation', icon: TrendingUp },
            { id: 'climate', label: 'Climate', icon: Cloud },
            { id: 'environment', label: 'Environment', icon: AlertTriangle }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-green-500 text-green-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Health Score</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {(vegetationData.health_score * 100 || 0).toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Cloud className="w-6 h-6 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Climate Risk</p>
                  <p className={`text-lg font-bold ${getRiskColor(climateData.overall_risk?.risk_level).split(' ')[0]}`}>
                    {climateData.overall_risk?.risk_level || 'Unknown'}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <AlertTriangle className="w-6 h-6 text-orange-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Environmental Health</p>
                  <p className={`text-lg font-bold ${getHealthColor(degradationData.environmental_health?.health_status).split(' ')[0]}`}>
                    {degradationData.environmental_health?.health_status || 'Unknown'}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Brain className="w-6 h-6 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Recovery Time</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {predictions.recovery_time_months || 0} months
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* NDVI Trend Chart */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Vegetation Health Trend</h3>
            <div className="h-64">
              <Line data={ndviChartData} options={chartOptions} />
            </div>
          </div>

          {/* Key Insights */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
            <div className="space-y-3">
              {result.insights?.slice(0, 5).map((insight, index) => (
                <div key={index} className="flex items-start">
                  <div className="flex-shrink-0 w-2 h-2 bg-green-500 rounded-full mt-2 mr-3"></div>
                  <p className="text-gray-700">{insight}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'vegetation' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Vegetation Metrics</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Current NDVI:</span>
                  <span className="font-medium">{(vegetationData.ndvi_current || 0).toFixed(3)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Historical NDVI:</span>
                  <span className="font-medium">{(vegetationData.ndvi_historical || 0).toFixed(3)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">NDVI Change:</span>
                  <span className={`font-medium ${(vegetationData.ndvi_change || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {(vegetationData.ndvi_change || 0).toFixed(3)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Vegetation Coverage:</span>
                  <span className="font-medium">{((vegetationData.vegetation_coverage || 0) * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Drought Risk:</span>
                  <span className={`font-medium ${getRiskColor(vegetationData.drought_risk).split(' ')[0]}`}>
                    {vegetationData.drought_risk || 'Unknown'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Crop Stress Analysis</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Stress Level:</span>
                  <span className={`font-medium ${getRiskColor(vegetationData.crop_stress_level).split(' ')[0]}`}>
                    {vegetationData.crop_stress_level || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Stress Areas:</span>
                  <span className="font-medium">{((vegetationData.crop_stress_areas || 0) * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'climate' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Drought Risk</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Risk Level:</span>
                  <span className={`font-medium ${getRiskColor(climateData.drought_analysis?.risk_level).split(' ')[0]}`}>
                    {climateData.drought_analysis?.risk_level || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Confidence:</span>
                  <span className="font-medium">{((climateData.drought_analysis?.confidence || 0) * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Flood Risk</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Risk Level:</span>
                  <span className={`font-medium ${getRiskColor(climateData.flood_analysis?.risk_level).split(' ')[0]}`}>
                    {climateData.flood_analysis?.risk_level || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Confidence:</span>
                  <span className="font-medium">{((climateData.flood_analysis?.confidence || 0) * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Heat Stress Risk</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Risk Level:</span>
                  <span className={`font-medium ${getRiskColor(climateData.heat_stress_analysis?.risk_level).split(' ')[0]}`}>
                    {climateData.heat_stress_analysis?.risk_level || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Confidence:</span>
                  <span className="font-medium">{((climateData.heat_stress_analysis?.confidence || 0) * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'environment' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Land Cover Changes</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Change Percentage:</span>
                  <span className="font-medium">{(degradationData.land_cover_changes?.change_percentage || 0).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Change Type:</span>
                  <span className="font-medium">{degradationData.land_cover_changes?.change_type || 'Unknown'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Severity:</span>
                  <span className={`font-medium ${getRiskColor(degradationData.land_cover_changes?.severity).split(' ')[0]}`}>
                    {degradationData.land_cover_changes?.severity || 'Unknown'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Deforestation Analysis</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Deforestation %:</span>
                  <span className="font-medium">{(degradationData.deforestation?.deforestation_percentage || 0).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Severity:</span>
                  <span className={`font-medium ${getRiskColor(degradationData.deforestation?.severity).split(' ')[0]}`}>
                    {degradationData.deforestation?.severity || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Illegal Clearing Risk:</span>
                  <span className={`font-medium ${getRiskColor(degradationData.deforestation?.illegal_clearing_risk).split(' ')[0]}`}>
                    {degradationData.deforestation?.illegal_clearing_risk || 'Unknown'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
        <div className="space-y-3">
          {result.recommendations?.slice(0, 10).map((recommendation, index) => (
            <div key={index} className="flex items-start">
              <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3"></div>
              <p className="text-gray-700">{recommendation}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default AnalysisResults;