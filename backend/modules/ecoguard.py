import cv2
import numpy as np
from PIL import Image
import requests
from typing import Dict, Any, List, Tuple
import asyncio
from datetime import datetime
import json
import io

class EcoGuardDetector:
    
    def __init__(self):
        self.degradation_threshold = 0.15  
        self.clearing_threshold = 0.3      
        
    async def detect_degradation(self, current_image_url: str, historical_image_url: str) -> Dict[str, Any]:
 
        try:
            current_img = await self._download_image(current_image_url)
            historical_img = await self._download_image(historical_image_url)
            
            land_cover_changes = self._detect_land_cover_changes(current_img, historical_img)
            
            deforestation = self._detect_deforestation(current_img, historical_img)
            
            soil_degradation = self._detect_soil_degradation(current_img, historical_img)
            
            pollution_indicators = self._detect_pollution_indicators(current_img)
            
            environmental_health = self._assess_environmental_health(
                land_cover_changes, deforestation, soil_degradation, pollution_indicators
            )
            
            return {
                "land_cover_changes": land_cover_changes,
                "deforestation": deforestation,
                "soil_degradation": soil_degradation,
                "pollution_indicators": pollution_indicators,
                "environmental_health": environmental_health,
                "violation_risk": self._calculate_violation_risk(environmental_health),
                "recommended_actions": self._generate_environmental_recommendations(environmental_health),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Degradation detection failed: {str(e)}")
    
    async def _download_image(self, image_url: str) -> np.ndarray:
        response = requests.get(image_url)
        response.raise_for_status()
        
        image = Image.open(io.BytesIO(response.content))
        return np.array(image)
    
    def _detect_land_cover_changes(self, current_img: np.ndarray, historical_img: np.ndarray) -> Dict[str, Any]:
 
        current_gray = cv2.cvtColor(current_img, cv2.COLOR_RGB2GRAY)
        historical_gray = cv2.cvtColor(historical_img, cv2.COLOR_RGB2GRAY)
 
        diff = cv2.absdiff(current_gray, historical_gray)
 
        _, change_mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        change_percentage = np.sum(change_mask > 0) / (change_mask.shape[0] * change_mask.shape[1]) * 100 # type: ignore

        if change_percentage > 20:
            change_type = "major_transformation"
        elif change_percentage > 10:
            change_type = "moderate_change"
        elif change_percentage > 5:
            change_type = "minor_change"
        else:
            change_type = "stable"
        
        return {
            "change_percentage": change_percentage,
            "change_type": change_type,
            "change_mask": change_mask,
            "severity": "high" if change_percentage > 15 else "moderate" if change_percentage > 5 else "low"
        }
    
    def _detect_deforestation(self, current_img: np.ndarray, historical_img: np.ndarray) -> Dict[str, Any]:

        current_ndvi = self._calculate_ndvi(current_img)
        historical_ndvi = self._calculate_ndvi(historical_img)

        vegetation_loss = historical_ndvi - current_ndvi
        loss_mask = vegetation_loss > self.degradation_threshold
 
        deforestation_percentage = np.sum(loss_mask) / (loss_mask.shape[0] * loss_mask.shape[1]) * 100
 
        if deforestation_percentage > 20:
            severity = "severe"
        elif deforestation_percentage > 10:
            severity = "moderate"
        elif deforestation_percentage > 5:
            severity = "mild"
        else:
            severity = "minimal"
 
        illegal_clearing_risk = "high" if deforestation_percentage > 15 else "moderate" if deforestation_percentage > 8 else "low"
        
        return {
            "deforestation_percentage": deforestation_percentage,
            "severity": severity,
            "illegal_clearing_risk": illegal_clearing_risk,
            "affected_areas": loss_mask,
            "vegetation_loss": float(np.mean(vegetation_loss))
        }
    
    def _detect_soil_degradation(self, current_img: np.ndarray, historical_img: np.ndarray) -> Dict[str, Any]:

        current_soil = self._extract_soil_areas(current_img)
        historical_soil = self._extract_soil_areas(historical_img)

        soil_exposure_increase = current_soil - historical_soil
        exposure_mask = soil_exposure_increase > 0.1
 
        degradation_percentage = np.sum(exposure_mask) / (exposure_mask.shape[0] * exposure_mask.shape[1]) * 100
        
        if degradation_percentage > 15:
            soil_health = "poor"
        elif degradation_percentage > 8:
            soil_health = "fair"
        else:
            soil_health = "good"
        
        return {
            "degradation_percentage": degradation_percentage,
            "soil_health": soil_health,
            "exposure_increase": float(np.mean(soil_exposure_increase)),
            "degraded_areas": exposure_mask
        }
    
    def _detect_pollution_indicators(self, current_img: np.ndarray) -> Dict[str, Any]:
        water_pollution = self._analyze_water_quality(current_img)
        
        pollution_patterns = self._detect_pollution_patterns(current_img)
        
        air_quality_indicators = self._assess_air_quality_indicators(current_img)
        
        return {
            "water_pollution": water_pollution,
            "pollution_patterns": pollution_patterns,
            "air_quality_indicators": air_quality_indicators,
            "overall_pollution_risk": self._calculate_pollution_risk(water_pollution, pollution_patterns)
        }
    
    def _assess_environmental_health(self, land_cover_changes: Dict, deforestation: Dict, 
                                   soil_degradation: Dict, pollution_indicators: Dict) -> Dict[str, Any]:
 
        health_factors = [
            land_cover_changes["severity"],
            deforestation["severity"],
            soil_degradation["soil_health"],
            pollution_indicators["overall_pollution_risk"]
        ]
        
        severity_scores = {"low": 0.8, "moderate": 0.5, "high": 0.2, "severe": 0.1}
        health_scores = [severity_scores.get(factor, 0.5) for factor in health_factors]
        
        overall_health_score = np.mean(health_scores)
        
        if overall_health_score > 0.7:
            health_status = "good"
        elif overall_health_score > 0.4:
            health_status = "fair"
        else:
            health_status = "poor"
        
        return {
            "overall_score": overall_health_score,
            "health_status": health_status,
            "primary_concerns": self._identify_primary_concerns(health_factors),
            "improvement_potential": self._assess_improvement_potential(overall_health_score) # type: ignore
        }
    
    def _calculate_violation_risk(self, environmental_health: Dict) -> str:
        health_score = environmental_health["overall_score"]
        
        if health_score < 0.3:
            return "high"
        elif health_score < 0.6:
            return "moderate"
        else:
            return "low"
    
    def _generate_environmental_recommendations(self, environmental_health: Dict) -> List[str]:
        recommendations = []
        
        if environmental_health["health_status"] == "poor":
            recommendations.extend([
                "immediate environmental assessment required",
                "consider soil restoration measures",
                "implement erosion control practices",
                "monitor for illegal activities"
            ])
        elif environmental_health["health_status"] == "fair":
            recommendations.extend([
                "regular monitoring recommended",
                "implement sustainable land management",
                "consider reforestation in degraded areas"
            ])
        else:
            recommendations.extend([
                "maintain current practices",
                "continue regular monitoring",
                "consider expansion of conservation measures"
            ])
        
        return recommendations
    
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
    
    def _extract_soil_areas(self, image: np.ndarray) -> np.ndarray:
 
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
 
        lower_soil = np.array([10, 30, 30])
        upper_soil = np.array([30, 255, 255])

        soil_mask = cv2.inRange(hsv, lower_soil, upper_soil)
        
        return soil_mask.astype(np.float32) / 255.0
    
    def _analyze_water_quality(self, image: np.ndarray) -> Dict[str, Any]:

        water_mask = self._detect_water_bodies(image)
        
        if np.sum(water_mask) == 0:
            return {"quality": "no_water_detected", "risk": "low"}

        water_areas = image[water_mask > 0.5]
        if len(water_areas) == 0:
            return {"quality": "no_water_detected", "risk": "low"}
 
        avg_color = np.mean(water_areas, axis=0)

        if avg_color[0] > 150 and avg_color[1] < 100:  
            quality = "poor"
            risk = "high"
        elif avg_color[1] > 150 and avg_color[2] < 100:  
            quality = "fair"
            risk = "moderate"
        else:
            quality = "good"
            risk = "low"
        
        return {
            "quality": quality,
            "risk": risk,
            "color_indicators": avg_color.tolist()
        }
    
    def _detect_water_bodies(self, image: np.ndarray) -> np.ndarray:
 
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        lower_water = np.array([100, 50, 50])
        upper_water = np.array([130, 255, 255])
        
        water_mask = cv2.inRange(hsv, lower_water, upper_water)
        
        return water_mask.astype(np.float32) / 255.0
    
    def _detect_pollution_patterns(self, image: np.ndarray) -> Dict[str, Any]:
      
        color_std = np.std(image, axis=(0, 1))
        
        unusual_colors = np.sum(color_std > np.mean(color_std) * 2)
        
        if unusual_colors > 1:
            pattern_risk = "high"
        elif unusual_colors > 0:
            pattern_risk = "moderate"
        else:
            pattern_risk = "low"
        
        return {
            "pattern_risk": pattern_risk,
            "unusual_color_indicators": unusual_colors,
            "color_variance": color_std.tolist()
        }
    
    def _assess_air_quality_indicators(self, image: np.ndarray) -> Dict[str, Any]:
     
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        clarity = cv2.Laplacian(gray, cv2.CV_64F).var() # type: ignore
        
        if clarity < 100:
            air_quality = "poor"
        elif clarity < 500:
            air_quality = "fair"
        else:
            air_quality = "good"
        
        return {
            "air_quality": air_quality,
            "clarity_score": clarity,
            "haze_indicators": clarity < 200
        }
    
    def _calculate_pollution_risk(self, water_pollution: Dict, pollution_patterns: Dict) -> str:
        water_risk = water_pollution["risk"]
        pattern_risk = pollution_patterns["pattern_risk"]
        
        if water_risk == "high" or pattern_risk == "high":
            return "high"
        elif water_risk == "moderate" or pattern_risk == "moderate":
            return "moderate"
        else:
            return "low"
    
    def _identify_primary_concerns(self, health_factors: List[str]) -> List[str]:
        concerns = []
        
        if "high" in health_factors or "severe" in health_factors:
            concerns.append("Significant environmental degradation detected")
        
        if "moderate" in health_factors:
            concerns.append("Moderate environmental changes observed")
        
        if "low" in health_factors:
            concerns.append("Minor environmental variations")
        
        return concerns
    
    def _assess_improvement_potential(self, health_score: float) -> str:
        if health_score < 0.3:
            return "high_improvement_potential"
        elif health_score < 0.6:
            return "moderate_improvement_potential"
        else:
            return "maintain_current_conditions"