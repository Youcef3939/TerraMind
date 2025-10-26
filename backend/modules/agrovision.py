import cv2 
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
import requests
from typing import Dict, Any, Tuple, List
import asyncio
from datetime import datetime, timedelta
import json
import io

class UNetSegmentation(nn.Module):
    
    def __init__(self, in_channels=3, out_channels=1):
        super(UNetSegmentation, self).__init__()
        
        self.enc1 = self._conv_block(in_channels, 64)
        self.enc2 = self._conv_block(64, 128)
        self.enc3 = self._conv_block(128, 256)
        self.enc4 = self._conv_block(256, 512)
        
        self.bottleneck = self._conv_block(512, 1024)
        
        self.dec4 = self._conv_block(1024 + 512, 512)
        self.dec3 = self._conv_block(512 + 256, 256)
        self.dec2 = self._conv_block(256 + 128, 128)
        self.dec1 = self._conv_block(128 + 64, 64)
        
        self.final = nn.Conv2d(64, out_channels, kernel_size=1)
        
        self.pool = nn.MaxPool2d(2)
        self.upsample = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        
    def _conv_block(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))
        
        b = self.bottleneck(self.pool(e4))
        
        d4 = self.dec4(torch.cat([self.upsample(b), e4], dim=1))
        d3 = self.dec3(torch.cat([self.upsample(d4), e3], dim=1))
        d2 = self.dec2(torch.cat([self.upsample(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.upsample(d2), e1], dim=1))
        
        return torch.sigmoid(self.final(d1))

class AgroVisionAnalyzer:
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model()
        self.model.eval()
        
    def _load_model(self):
        model = UNetSegmentation(in_channels=3, out_channels=1)
        return model.to(self.device)
    
    async def analyze_vegetation(self, current_image_url: str, historical_image_url: str) -> Dict[str, Any]:
        try:
            current_img = await self._download_image(current_image_url)
            historical_img = await self._download_image(historical_image_url)
            
            current_ndvi = self._calculate_ndvi(current_img)
            historical_ndvi = self._calculate_ndvi(historical_img)
            
            current_ndwi = self._calculate_ndwi(current_img)
            historical_ndwi = self._calculate_ndwi(historical_img)
            
            vegetation_change = self._detect_vegetation_changes(current_ndvi, historical_ndvi)
            
            stress_analysis = self._analyze_crop_stress(current_ndvi, current_ndwi)
            
            vegetation_mask = await self._segment_vegetation(current_img)
            
            health_metrics = self._calculate_health_metrics(
                current_ndvi, historical_ndvi, vegetation_mask
            )
            
            return {
                "ndvi_current": float(np.mean(current_ndvi)),
                "ndvi_historical": float(np.mean(historical_ndvi)),
                "ndvi_change": float(np.mean(current_ndvi - historical_ndvi)),
                "ndwi_current": float(np.mean(current_ndwi)),
                "ndwi_historical": float(np.mean(historical_ndwi)),
                "ndwi_change": float(np.mean(current_ndwi - historical_ndwi)),
                "vegetation_change_percentage": vegetation_change["percentage"],
                "vegetation_change_type": vegetation_change["type"],
                "crop_stress_level": stress_analysis["stress_level"],
                "crop_stress_areas": stress_analysis["stress_areas"],
                "vegetation_coverage": float(np.mean(vegetation_mask)),
                "health_score": health_metrics["health_score"],
                "drought_risk": health_metrics["drought_risk"],
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Vegetation analysis failed: {str(e)}")
    
    async def predict_future_conditions(self, vegetation_analysis: Dict, climate_analysis: Dict) -> Dict[str, Any]:
        try:
            current_ndvi = vegetation_analysis["ndvi_current"]
            ndvi_trend = vegetation_analysis["ndvi_change"]
            drought_risk = vegetation_analysis["drought_risk"]
            rainfall_forecast = climate_analysis.get("rainfall_forecast", 0)
            temperature_forecast = climate_analysis.get("temperature_forecast", 20)
            
            future_ndvi = self._predict_ndvi_trend(
                current_ndvi, ndvi_trend, drought_risk, rainfall_forecast, temperature_forecast
            )
            
            recovery_time = self._predict_recovery_time(ndvi_trend, drought_risk)
            
            optimal_planting = self._predict_optimal_planting(climate_analysis)
            
            return {
                "predicted_ndvi_3_months": future_ndvi["3_months"],
                "predicted_ndvi_6_months": future_ndvi["6_months"],
                "predicted_ndvi_12_months": future_ndvi["12_months"],
                "recovery_time_months": recovery_time,
                "recovery_probability": future_ndvi["recovery_probability"],
                "optimal_planting_date": optimal_planting["date"],
                "optimal_planting_confidence": optimal_planting["confidence"],
                "prediction_confidence": future_ndvi["confidence"],
                "prediction_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Future prediction failed: {str(e)}")
    
    async def _download_image(self, image_url: str) -> np.ndarray:
        response = requests.get(image_url)
        response.raise_for_status()
        
        image = Image.open(io.BytesIO(response.content))
        return np.array(image)
    
    def _calculate_ndvi(self, image: np.ndarray) -> np.ndarray:
        if image.shape[2] < 4:
            nir = image[:, :, 0]  
            red = image[:, :, 1] if image.shape[2] > 1 else image[:, :, 0]
        else:
            nir = image[:, :, 3] 
            red = image[:, :, 2]  
        
        nir = nir.astype(np.float32)
        red = red.astype(np.float32)
        
        ndvi = (nir - red) / (nir + red + 1e-8)  
        return np.clip(ndvi, -1, 1)
    
    def _calculate_ndwi(self, image: np.ndarray) -> np.ndarray:
        if image.shape[2] < 4:
            nir = image[:, :, 0]
            swir = image[:, :, 1] if image.shape[2] > 1 else image[:, :, 0]
        else:
            nir = image[:, :, 3]  
            swir = image[:, :, 4] if image.shape[2] > 4 else image[:, :, 3]  
        
        nir = nir.astype(np.float32)
        swir = swir.astype(np.float32)
        
        ndwi = (nir - swir) / (nir + swir + 1e-8)
        return np.clip(ndwi, -1, 1)
    
    def _detect_vegetation_changes(self, current_ndvi: np.ndarray, historical_ndvi: np.ndarray) -> Dict[str, Any]:
        change = current_ndvi - historical_ndvi
        change_percentage = (np.mean(change) / np.mean(historical_ndvi)) * 100
        
        if change_percentage > 5:
            change_type = "improvement"
        elif change_percentage < -5:
            change_type = "degradation"
        else:
            change_type = "stable"
        
        return {
            "percentage": change_percentage,
            "type": change_type,
            "areas_of_change": np.where(np.abs(change) > 0.1, 1, 0)
        }
    
    def _analyze_crop_stress(self, ndvi: np.ndarray, ndwi: np.ndarray) -> Dict[str, Any]:
        stress_mask = (ndvi < 0.3) & (ndwi < 0.1)
        stress_percentage = np.mean(stress_mask) * 100
        
        if stress_percentage > 30:
            stress_level = "high"
        elif stress_percentage > 10:
            stress_level = "moderate"
        else:
            stress_level = "low"
        
        return {
            "stress_level": stress_level,
            "stress_percentage": stress_percentage,
            "stress_areas": stress_mask
        }
    
    async def _segment_vegetation(self, image: np.ndarray) -> np.ndarray:
        input_tensor = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0).float() / 255.0
        input_tensor = input_tensor.to(self.device)
        
        with torch.no_grad():
            prediction = self.model(input_tensor)
            mask = (prediction > 0.5).cpu().numpy().squeeze()
        
        return mask
    
    def _calculate_health_metrics(self, current_ndvi: np.ndarray, historical_ndvi: np.ndarray, vegetation_mask: np.ndarray) -> Dict[str, Any]:
        ndvi_score = np.mean(current_ndvi[vegetation_mask > 0.5]) if np.any(vegetation_mask > 0.5) else 0
        coverage_score = np.mean(vegetation_mask)
        health_score = (ndvi_score + coverage_score) / 2
        
        if health_score < 0.3:
            drought_risk = "high"
        elif health_score < 0.6:
            drought_risk = "moderate"
        else:
            drought_risk = "low"
        
        return {
            "health_score": float(health_score),
            "drought_risk": drought_risk,
            "vegetation_density": float(coverage_score)
        }
    
    def _predict_ndvi_trend(self, current_ndvi: float, ndvi_change: float, drought_risk: str, rainfall: float, temperature: float) -> Dict[str, Any]:

        base_trend = ndvi_change
        
        rainfall_factor = min(rainfall / 100, 1.0) 
        temperature_factor = max(0, (25 - temperature) / 10)  
        
        climate_adjustment = (rainfall_factor + temperature_factor) / 2
        
        months_3 = current_ndvi + (base_trend * 0.25) + (climate_adjustment * 0.1)
        months_6 = current_ndvi + (base_trend * 0.5) + (climate_adjustment * 0.2)
        months_12 = current_ndvi + (base_trend * 1.0) + (climate_adjustment * 0.4)
        
        recovery_prob = min(1.0, max(0.0, (climate_adjustment + 0.5)))
        
        return {
            "3_months": float(np.clip(months_3, 0, 1)),
            "6_months": float(np.clip(months_6, 0, 1)),
            "12_months": float(np.clip(months_12, 0, 1)),
            "recovery_probability": recovery_prob,
            "confidence": 0.75  
        }
    
    def _predict_recovery_time(self, ndvi_change: float, drought_risk: str) -> int:
        if drought_risk == "high":
            return 12
        elif drought_risk == "moderate":
            return 6
        else:
            return 3
    
    def _predict_optimal_planting(self, climate_analysis: Dict) -> Dict[str, Any]:
        rainfall = climate_analysis.get("rainfall_forecast", 0)
        temperature = climate_analysis.get("temperature_forecast", 20)
        
        if 50 <= rainfall <= 150 and 20 <= temperature <= 25:
            confidence = 0.9
            date = "Next 2-4 weeks"
        elif 30 <= rainfall <= 200 and 15 <= temperature <= 30:
            confidence = 0.7
            date = "Next 4-8 weeks"
        else:
            confidence = 0.4
            date = "Monitor conditions"
        
        return {
            "date": date,
            "confidence": confidence
        }