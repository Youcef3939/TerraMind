import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Circle, useMapEvents } from 'react-leaflet';
import { toast, Toaster } from 'react-hot-toast';
import axios from 'axios';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import Dashboard from './components/Dashboard';
import AnalysisResults from './components/AnalysisResults';
import LoadingSpinner from './components/LoadingSpinner';
import Header from './components/Header';

import { MapPin, Satellite, Brain, Download, AlertTriangle } from 'lucide-react';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

function App() {
  const [selectedAOI, setSelectedAOI] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentView, setCurrentView] = useState('map'); 

  const defaultCenter = [36.7783, -119.4179];
  const defaultZoom = 10;

  const handleAOISelection = (aoi) => {
    setSelectedAOI(aoi);
    setCurrentView('dashboard');
  };

  const handleAnalysis = async () => {
    if (!selectedAOI) {
      toast.error('Please select an Area of Interest first');
      return;
    }

    setIsAnalyzing(true);
    toast.loading('Analyzing area... This may take a few minutes.', { id: 'analysis' });

    try {
      const response = await axios.post('http://localhost:8000/analyze', {
        center_lat: selectedAOI.center[0],
        center_lon: selectedAOI.center[1],
        radius_km: selectedAOI.radius,
        analysis_type: 'comprehensive'
      });

      setAnalysisResult(response.data);
      setCurrentView('results');
      toast.success('Analysis completed successfully!', { id: 'analysis' });
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error('Analysis failed. Please try again.', { id: 'analysis' });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!analysisResult?.aoi_id) {
      toast.error('No analysis results available for download');
      return;
    }

    try {
      const response = await axios.get(
        `http://localhost:8000/report/${analysisResult.aoi_id}`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `terramind_report_${analysisResult.aoi_id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('Report downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download report');
    }
  };

  const resetAnalysis = () => {
    setSelectedAOI(null);
    setAnalysisResult(null);
    setCurrentView('map');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      <Header 
        currentView={currentView}
        onReset={resetAnalysis}
        hasAnalysis={!!analysisResult}
        onDownload={handleDownloadReport}
      />

      <main className="container mx-auto px-4 py-6">
        {currentView === 'map' && (
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                <MapPin className="w-6 h-6 mr-2 text-green-600" />
                Select Area of Interest
              </h2>
              <p className="text-gray-600 mt-2">
                Draw a circular area on the map to analyze vegetation health, climate risks, and environmental conditions.
              </p>
            </div>
            
            <div className="h-96">
              <MapContainer
                center={defaultCenter}
                zoom={defaultZoom}
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                <MapEventHandler onAOISelected={handleAOISelection} />
                {selectedAOI && (
                  <Circle
                    center={selectedAOI.center}
                    radius={selectedAOI.radius * 1000} // Convert km to meters
                    pathOptions={{
                      color: '#10B981',
                      fillColor: '#10B981',
                      fillOpacity: 0.2,
                      weight: 2
                    }}
                  />
                )}
              </MapContainer>
            </div>

            {selectedAOI && (
              <div className="p-6 bg-green-50 border-t border-green-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-green-900">AOI Selected</h3>
                    <p className="text-green-700">
                      Center: {selectedAOI.center[0].toFixed(4)}, {selectedAOI.center[1].toFixed(4)}
                    </p>
                    <p className="text-green-700">
                      Radius: {selectedAOI.radius} km
                    </p>
                  </div>
                  <button
                    onClick={handleAnalysis}
                    disabled={isAnalyzing}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-semibold flex items-center transition-colors"
                  >
                    {isAnalyzing ? (
                      <LoadingSpinner size="sm" />
                    ) : (
                      <>
                        <Brain className="w-4 h-4 mr-2" />
                        Analyze Area
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {currentView === 'dashboard' && selectedAOI && (
          <Dashboard 
            aoi={selectedAOI}
            onAnalyze={handleAnalysis}
            isAnalyzing={isAnalyzing}
            onBack={() => setCurrentView('map')}
          />
        )}

        {currentView === 'results' && analysisResult && (
          <AnalysisResults 
            result={analysisResult}
            onBack={() => setCurrentView('map')}
            onDownload={handleDownloadReport}
          />
        )}
      </main>

      {/* Quick Stats Footer */}
      <footer className="bg-white border-t border-gray-200 py-4">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center space-x-6">
              <div className="flex items-center">
                <Satellite className="w-4 h-4 mr-1" />
                <span>Satellite Analysis</span>
              </div>
              <div className="flex items-center">
                <Brain className="w-4 h-4 mr-1" />
                <span>AI-Powered Insights</span>
              </div>
              <div className="flex items-center">
                <AlertTriangle className="w-4 h-4 mr-1" />
                <span>Climate Risk Assessment</span>
              </div>
            </div>
            <div>
              TerraMind v1.0.0 - AI for Sustainable Agriculture
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function MapEventHandler({ onAOISelected }) {
  const [isDrawing, setIsDrawing] = useState(false);
  const [startPoint, setStartPoint] = useState(null);

  useMapEvents({
    click: (e) => {
      if (!isDrawing) {
        setIsDrawing(true);
        setStartPoint([e.latlng.lat, e.latlng.lng]);
      } else {
        const endPoint = [e.latlng.lat, e.latlng.lng];
        const radius = calculateDistance(startPoint, endPoint);
        
        if (radius > 0.1) { 
          onAOISelected({
            center: startPoint,
            radius: radius,
            timestamp: new Date().toISOString()
          });
        }
        
        setIsDrawing(false);
        setStartPoint(null);
      }
    }
  });

  return null;
}

function calculateDistance(point1, point2) {
  const R = 6371; 
  const dLat = (point2[0] - point1[0]) * Math.PI / 180;
  const dLon = (point2[1] - point1[1]) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(point1[0] * Math.PI / 180) * Math.cos(point2[0] * Math.PI / 180) *
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

export default App;