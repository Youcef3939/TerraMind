import React from 'react';
import { MapPin, Download, RotateCcw, Brain } from 'lucide-react';

function Header({ currentView, onReset, hasAnalysis, onDownload }) {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <div className="bg-green-600 p-2 rounded-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">TerraMind</h1>
              <p className="text-sm text-gray-600">AI for Sustainable Agriculture</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            {currentView === 'map' && (
              <div className="flex items-center text-sm text-gray-600">
                <MapPin className="w-4 h-4 mr-1" />
                <span>Select Area of Interest</span>
              </div>
            )}

            {currentView === 'dashboard' && (
              <div className="flex items-center text-sm text-gray-600">
                <Brain className="w-4 h-4 mr-1" />
                <span>Analysis Dashboard</span>
              </div>
            )}

            {currentView === 'results' && (
              <div className="flex items-center text-sm text-gray-600">
                <Brain className="w-4 h-4 mr-1" />
                <span>Analysis Results</span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              {hasAnalysis && (
                <button
                  onClick={onDownload}
                  className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  <Download className="w-4 h-4 mr-1" />
                  Download Report
                </button>
              )}

              <button
                onClick={onReset}
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <RotateCcw className="w-4 h-4 mr-1" />
                New Analysis
              </button>
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}

export default Header;