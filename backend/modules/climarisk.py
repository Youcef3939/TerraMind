import requests
import asyncio
import aiohttp # type: ignore
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import numpy as np
from dataclasses import dataclass

@dataclass
class WeatherData:
    temperature: float
    humidity: float
    precipitation: float
    wind_speed: float
    pressure: float
    timestamp: datetime

@dataclass
class ClimateRisk:
    drought_risk: str
    flood_risk: str
    heat_stress_risk: str
    overall_risk: str
    confidence: float

class ClimaRiskPredictor:
    
    def __init__(self, openweather_api_key: str = None): # type: ignore
        self.api_key = openweather_api_key or "demo_key" 
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.forecast_url = f"{self.base_url}/forecast"
        self.current_url = f"{self.base_url}/weather"
        
        self.drought_thresholds = {
            "precipitation_mm": 50,  
            "humidity_percent": 40,  
            "temperature_celsius": 35  
        }
        
        self.flood_thresholds = {
            "precipitation_mm": 100,  
            "humidity_percent": 80,  
            "wind_speed_ms": 15  
        }
    
    async def analyze_climate_risks(self, lat: float, lon: float) -> Dict[str, Any]:
        try:
            current_weather = await self._get_current_weather(lat, lon)
            
            forecast_data = await self._get_weather_forecast(lat, lon)
            
            drought_analysis = self._analyze_drought_risk(current_weather, forecast_data)
            
            flood_analysis = self._analyze_flood_risk(current_weather, forecast_data)
            
            heat_stress_analysis = self._analyze_heat_stress_risk(current_weather, forecast_data)
            
            overall_risk = self._calculate_overall_risk(drought_analysis, flood_analysis, heat_stress_analysis)
            
            recommendations = self._generate_climate_recommendations(
                drought_analysis, flood_analysis, heat_stress_analysis
            )
            
            return {
                "current_weather": current_weather,
                "forecast_data": forecast_data,
                "drought_analysis": drought_analysis,
                "flood_analysis": flood_analysis,
                "heat_stress_analysis": heat_stress_analysis,
                "overall_risk": overall_risk,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Climate risk analysis failed: {str(e)}")
    
    async def get_weather_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        try:
            forecast_data = await self._get_weather_forecast(lat, lon)
            return {
                "forecast": forecast_data,
                "coordinates": {"lat": lat, "lon": lon},
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Weather forecast failed: {str(e)}")
    
    async def assess_climate_risks(self, lat: float, lon: float) -> Dict[str, Any]:
        try:
            current_weather = await self._get_current_weather(lat, lon)
            forecast_data = await self._get_weather_forecast(lat, lon)
            
            risks = {
                "drought_risk": self._assess_drought_risk(current_weather, forecast_data),
                "flood_risk": self._assess_flood_risk(current_weather, forecast_data),
                "heat_stress_risk": self._assess_heat_stress_risk(current_weather, forecast_data),
                "storm_risk": self._assess_storm_risk(current_weather, forecast_data)
            }
            
            return risks
        except Exception as e:
            raise Exception(f"Climate risk assessment failed: {str(e)}")
    
    async def _get_current_weather(self, lat: float, lon: float) -> WeatherData:
        if self.api_key == "demo_key":
            return self._get_demo_weather_data()
        
        try:
            url = f"{self.current_url}?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return WeatherData(
                            temperature=data["main"]["temp"],
                            humidity=data["main"]["humidity"],
                            precipitation=data.get("rain", {}).get("1h", 0),
                            wind_speed=data["wind"]["speed"],
                            pressure=data["main"]["pressure"],
                            timestamp=datetime.now()
                        )
                    else:
                        raise Exception(f"Weather API error: {response.status}")
        except Exception as e:
            return self._get_demo_weather_data()
    
    async def _get_weather_forecast(self, lat: float, lon: float) -> List[WeatherData]:
        if self.api_key == "demo_key":
            return self._get_demo_forecast_data()
        
        try:
            url = f"{self.forecast_url}?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        forecast = []
                        
                        for item in data["list"][:40]:  
                            forecast.append(WeatherData(
                                temperature=item["main"]["temp"],
                                humidity=item["main"]["humidity"],
                                precipitation=item.get("rain", {}).get("3h", 0),
                                wind_speed=item["wind"]["speed"],
                                pressure=item["main"]["pressure"],
                                timestamp=datetime.fromtimestamp(item["dt"])
                            ))
                        
                        return forecast
                    else:
                        raise Exception(f"Forecast API error: {response.status}")
        except Exception as e:
            return self._get_demo_forecast_data()
    
    def _get_demo_weather_data(self) -> WeatherData:
        return WeatherData(
            temperature=25.0 + np.random.normal(0, 5),
            humidity=60.0 + np.random.normal(0, 15),
            precipitation=np.random.exponential(2),
            wind_speed=5.0 + np.random.exponential(2),
            pressure=1013.25 + np.random.normal(0, 10),
            timestamp=datetime.now()
        )
    
    def _get_demo_forecast_data(self) -> List[WeatherData]:
        forecast = []
        base_temp = 25.0
        base_humidity = 60.0
        
        for i in range(40): 
            hour = (i * 3) % 24
            temp_variation = 5 * np.sin((hour - 6) * np.pi / 12)  
            
            forecast.append(WeatherData(
                temperature=base_temp + temp_variation + np.random.normal(0, 2),
                humidity=base_humidity + np.random.normal(0, 10),
                precipitation=np.random.exponential(1),
                wind_speed=5.0 + np.random.exponential(1.5),
                pressure=1013.25 + np.random.normal(0, 5),
                timestamp=datetime.now() + timedelta(hours=i * 3)
            ))
        
        return forecast
    
    def _analyze_drought_risk(self, current_weather: WeatherData, forecast_data: List[WeatherData]) -> Dict[str, Any]:

        total_precipitation = sum(w.precipitation for w in forecast_data) * 3.75  # Scale to 30 days
        
        avg_humidity = np.mean([w.humidity for w in forecast_data])
        
        avg_temperature = np.mean([w.temperature for w in forecast_data])
        
        drought_factors = []
        
        if total_precipitation < self.drought_thresholds["precipitation_mm"]:
            drought_factors.append("low_precipitation")
        
        if avg_humidity < self.drought_thresholds["humidity_percent"]:
            drought_factors.append("low_humidity")
        
        if avg_temperature > self.drought_thresholds["temperature_celsius"]:
            drought_factors.append("high_temperature")
        
        if len(drought_factors) >= 3:
            drought_risk = "severe"
            confidence = 0.9
        elif len(drought_factors) >= 2:
            drought_risk = "moderate"
            confidence = 0.7
        elif len(drought_factors) >= 1:
            drought_risk = "low"
            confidence = 0.5
        else:
            drought_risk = "minimal"
            confidence = 0.8
        
        return {
            "risk_level": drought_risk,
            "confidence": confidence,
            "factors": drought_factors,
            "precipitation_30d": total_precipitation,
            "avg_humidity": avg_humidity,
            "avg_temperature": avg_temperature,
            "recommendations": self._get_drought_recommendations(drought_risk)
        }
    
    def _analyze_flood_risk(self, current_weather: WeatherData, forecast_data: List[WeatherData]) -> Dict[str, Any]:

        max_24h_precipitation = max(w.precipitation for w in forecast_data) * 8  # Scale to 24h
 
        avg_humidity = np.mean([w.humidity for w in forecast_data])
        
        max_wind_speed = max(w.wind_speed for w in forecast_data)
        
        flood_factors = []
        
        if max_24h_precipitation > self.flood_thresholds["precipitation_mm"]:
            flood_factors.append("heavy_precipitation")
        
        if avg_humidity > self.flood_thresholds["humidity_percent"]:
            flood_factors.append("high_humidity")
        
        if max_wind_speed > self.flood_thresholds["wind_speed_ms"]:
            flood_factors.append("high_winds")
        
        if len(flood_factors) >= 2:
            flood_risk = "high"
            confidence = 0.8
        elif len(flood_factors) >= 1:
            flood_risk = "moderate"
            confidence = 0.6
        else:
            flood_risk = "low"
            confidence = 0.7
        
        return {
            "risk_level": flood_risk,
            "confidence": confidence,
            "factors": flood_factors,
            "max_24h_precipitation": max_24h_precipitation,
            "avg_humidity": avg_humidity,
            "max_wind_speed": max_wind_speed,
            "recommendations": self._get_flood_recommendations(flood_risk)
        }
    
    def _analyze_heat_stress_risk(self, current_weather: WeatherData, forecast_data: List[WeatherData]) -> Dict[str, Any]:

        max_temperature = max(w.temperature for w in forecast_data)
        
        avg_humidity = np.mean([w.humidity for w in forecast_data])
        
        heat_index = self._calculate_heat_index(max_temperature, avg_humidity) # type: ignore
        
        if heat_index > 40:
            heat_stress_risk = "severe"
            confidence = 0.9
        elif heat_index > 35:
            heat_stress_risk = "moderate"
            confidence = 0.7
        elif heat_index > 30:
            heat_stress_risk = "low"
            confidence = 0.5
        else:
            heat_stress_risk = "minimal"
            confidence = 0.8
        
        return {
            "risk_level": heat_stress_risk,
            "confidence": confidence,
            "max_temperature": max_temperature,
            "heat_index": heat_index,
            "avg_humidity": avg_humidity,
            "recommendations": self._get_heat_stress_recommendations(heat_stress_risk)
        }
    
    def _calculate_overall_risk(self, drought_analysis: Dict, flood_analysis: Dict, heat_stress_analysis: Dict) -> Dict[str, Any]:
 
        risk_scores = {
            "minimal": 0.1,
            "low": 0.3,
            "moderate": 0.6,
            "high": 0.8,
            "severe": 0.9
        }
        
        drought_score = risk_scores.get(drought_analysis["risk_level"], 0.5)
        flood_score = risk_scores.get(flood_analysis["risk_level"], 0.5)
        heat_score = risk_scores.get(heat_stress_analysis["risk_level"], 0.5)
        
        overall_score = (drought_score * 0.4 + flood_score * 0.3 + heat_score * 0.3)
        
        if overall_score > 0.8:
            overall_risk = "high"
        elif overall_score > 0.6:
            overall_risk = "moderate"
        elif overall_score > 0.3:
            overall_risk = "low"
        else:
            overall_risk = "minimal"
        
        return {
            "risk_level": overall_risk,
            "risk_score": overall_score,
            "confidence": np.mean([
                drought_analysis["confidence"],
                flood_analysis["confidence"],
                heat_stress_analysis["confidence"]
            ]),
            "primary_concerns": self._identify_primary_climate_concerns(
                drought_analysis, flood_analysis, heat_stress_analysis
            )
        }
    
    def _generate_climate_recommendations(self, drought_analysis: Dict, flood_analysis: Dict, heat_stress_analysis: Dict) -> List[str]:

        recommendations = []
        
        if drought_analysis["risk_level"] in ["moderate", "severe"]:
            recommendations.extend([
                "Implement water conservation measures",
                "Consider drought-resistant crop varieties",
                "Monitor soil moisture levels closely",
                "Prepare irrigation backup plans"
            ])
        
        if flood_analysis["risk_level"] in ["moderate", "high"]:
            recommendations.extend([
                "Implement drainage improvements",
                "Consider flood-resistant crop varieties",
                "Monitor weather forecasts closely",
                "Prepare emergency response plans"
            ])
        
        if heat_stress_analysis["risk_level"] in ["moderate", "severe"]:
            recommendations.extend([
                "Implement shade structures or cover crops",
                "Increase irrigation frequency",
                "Consider heat-tolerant crop varieties",
                "Monitor crop stress indicators"
            ])
        
        if not recommendations:
            recommendations.append("Continue regular monitoring")
            recommendations.append("Maintain current agricultural practices")
        
        return recommendations
    
    def _calculate_heat_index(self, temperature: float, humidity: float) -> float:
        hi = -42.379 + 2.04901523 * temperature + 10.14333127 * humidity
        hi -= 0.22475541 * temperature * humidity
        hi -= 6.83783e-3 * temperature**2
        hi -= 5.481717e-2 * humidity**2
        hi += 1.22874e-3 * temperature**2 * humidity
        hi += 8.5282e-4 * temperature * humidity**2
        hi -= 1.99e-6 * temperature**2 * humidity**2
        
        return max(hi, temperature)  
    
    def _get_drought_recommendations(self, risk_level: str) -> List[str]:
        if risk_level == "severe":
            return [
                "immediate water conservation required",
                "consider emergency irrigation",
                "switch to drought-resistant crops",
                "implement soil moisture monitoring"
            ]
        elif risk_level == "moderate":
            return [
                "increase water conservation measures",
                "monitor soil moisture daily",
                "consider mulching to retain moisture",
                "prepare irrigation contingency plans"
            ]
        else:
            return ["continue regular monitoring", "maintain current irrigation practices"]
    
    def _get_flood_recommendations(self, risk_level: str) -> List[str]:
        if risk_level == "high":
            return [
                "implement immediate drainage measures",
                "consider flood-resistant crop varieties",
                "prepare emergency evacuation plans",
                "monitor water levels continuously"
            ]
        elif risk_level == "moderate":
            return [
                "improve drainage systems",
                "monitor weather forecasts closely",
                "consider raised bed planting",
                "prepare sandbags or barriers"
            ]
        else:
            return ["continue regular monitoring", "maintain current drainage practices"]
    
    def _get_heat_stress_recommendations(self, risk_level: str) -> List[str]:
        if risk_level == "severe":
            return [
                "implement immediate shade protection",
                "increase irrigation frequency",
                "consider heat-tolerant crop varieties",
                "monitor crop stress indicators hourly"
            ]
        elif risk_level == "moderate":
            return [
                "provide partial shade protection",
                "increase irrigation slightly",
                "monitor crop health closely",
                "consider misting systems"
            ]
        else:
            return ["continue regular monitoring", "maintain current practices"]
    
    def _identify_primary_climate_concerns(self, drought_analysis: Dict, flood_analysis: Dict, heat_stress_analysis: Dict) -> List[str]:

        concerns = []
        
        if drought_analysis["risk_level"] in ["moderate", "severe"]:
            concerns.append("Drought conditions")
        
        if flood_analysis["risk_level"] in ["moderate", "high"]:
            concerns.append("Flood risk")
        
        if heat_stress_analysis["risk_level"] in ["moderate", "severe"]:
            concerns.append("Heat stress")
        
        if not concerns:
            concerns.append("Normal weather conditions")
        
        return concerns
    
    def _assess_drought_risk(self, current_weather: WeatherData, forecast_data: List[WeatherData]) -> str:

        total_precipitation = sum(w.precipitation for w in forecast_data) * 3.75
        avg_humidity = np.mean([w.humidity for w in forecast_data])
        
        if total_precipitation < 30 and avg_humidity < 40:
            return "high"
        elif total_precipitation < 50 and avg_humidity < 50:
            return "moderate"
        else:
            return "low"
    
    def _assess_flood_risk(self, current_weather: WeatherData, forecast_data: List[WeatherData]) -> str:

        max_precipitation = max(w.precipitation for w in forecast_data) * 8
        avg_humidity = np.mean([w.humidity for w in forecast_data])
        
        if max_precipitation > 80 and avg_humidity > 70:
            return "high"
        elif max_precipitation > 50 and avg_humidity > 60:
            return "moderate"
        else:
            return "low"
    
    def _assess_heat_stress_risk(self, current_weather: WeatherData, forecast_data: List[WeatherData]) -> str:
  
        max_temp = max(w.temperature for w in forecast_data)
        avg_humidity = np.mean([w.humidity for w in forecast_data])
        heat_index = self._calculate_heat_index(max_temp, avg_humidity) # type: ignore
        
        if heat_index > 40:
            return "high"
        elif heat_index > 35:
            return "moderate"
        else:
            return "low"
    
    def _assess_storm_risk(self, current_weather: WeatherData, forecast_data: List[WeatherData]) -> str:

        max_wind = max(w.wind_speed for w in forecast_data)
        max_precipitation = max(w.precipitation for w in forecast_data) * 8
        
        if max_wind > 15 and max_precipitation > 50:
            return "high"
        elif max_wind > 10 and max_precipitation > 30:
            return "moderate"
        else:
            return "low"