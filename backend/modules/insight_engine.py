from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

class InsightEngine:
    
    def __init__(self):
        self.insight_templates = self._load_insight_templates()
        self.recommendation_templates = self._load_recommendation_templates()
    
    async def generate_insights(self, vegetation_analysis: Dict, climate_analysis: Dict, degradation_analysis: Dict) -> List[str]:
    
        insights = []
        
        vegetation_insights = self._generate_vegetation_insights(vegetation_analysis)
        insights.extend(vegetation_insights)
        
        climate_insights = self._generate_climate_insights(climate_analysis)
        insights.extend(climate_insights)
        
        environmental_insights = self._generate_environmental_insights(degradation_analysis)
        insights.extend(environmental_insights)
        
        cross_insights = self._generate_cross_analysis_insights(
            vegetation_analysis, climate_analysis, degradation_analysis
        )
        insights.extend(cross_insights)
        
        return insights[:10]  
    
    async def generate_recommendations(self, vegetation_analysis: Dict, climate_analysis: Dict, 
                                     degradation_analysis: Dict, predictions: Dict) -> List[str]:
      
        recommendations = []
        
        immediate_actions = self._generate_immediate_actions(
            vegetation_analysis, climate_analysis, degradation_analysis
        )
        recommendations.extend(immediate_actions)
        
        short_term = self._generate_short_term_recommendations(
            vegetation_analysis, climate_analysis, predictions
        )
        recommendations.extend(short_term)
        
        long_term = self._generate_long_term_recommendations(
            vegetation_analysis, climate_analysis, degradation_analysis, predictions
        )
        recommendations.extend(long_term)
        
        preventive = self._generate_preventive_measures(
            climate_analysis, degradation_analysis
        )
        recommendations.extend(preventive)
        
        return recommendations[:15]  
    
    def _generate_vegetation_insights(self, vegetation_analysis: Dict) -> List[str]:
        insights = []
        
        ndvi_change = vegetation_analysis.get("ndvi_change", 0)
        vegetation_change = vegetation_analysis.get("vegetation_change_percentage", 0)
        health_score = vegetation_analysis.get("health_score", 0.5)
        drought_risk = vegetation_analysis.get("drought_risk", "low")
        
        if ndvi_change > 0.1:
            insights.append(f"Vegetation health has improved by {ndvi_change:.2f} NDVI units, indicating positive growth conditions.")
        elif ndvi_change < -0.1:
            insights.append(f"Vegetation health has declined by {abs(ndvi_change):.2f} NDVI units, suggesting stress or degradation.")
        else:
            insights.append("Vegetation health remains relatively stable with minimal changes detected.")
        
        if vegetation_change > 10:
            insights.append(f"Significant vegetation increase detected ({vegetation_change:.1f}%), indicating healthy growth or recovery.")
        elif vegetation_change < -10:
            insights.append(f"Concerning vegetation decrease detected ({abs(vegetation_change):.1f}%), requiring immediate attention.")
        
        if health_score > 0.7:
            insights.append("Overall vegetation health is excellent, with strong growth indicators.")
        elif health_score > 0.4:
            insights.append("Vegetation health is moderate, with room for improvement through targeted interventions.")
        else:
            insights.append("Vegetation health is poor, requiring immediate intervention and recovery measures.")
        
        if drought_risk == "high":
            insights.append("High drought risk detected - vegetation is under significant water stress.")
        elif drought_risk == "moderate":
            insights.append("Moderate drought risk present - monitor water availability closely.")
        
        return insights
    
    def _generate_climate_insights(self, climate_analysis: Dict) -> List[str]:
        insights = []
        
        overall_risk = climate_analysis.get("overall_risk", {})
        risk_level = overall_risk.get("risk_level", "low")
        primary_concerns = overall_risk.get("primary_concerns", [])
        
        if risk_level == "high":
            insights.append("High climate risk detected - immediate action required to protect agricultural assets.")
        elif risk_level == "moderate":
            insights.append("Moderate climate risk present - proactive measures recommended.")
        else:
            insights.append("Climate conditions are favorable for agricultural activities.")
        
        for concern in primary_concerns:
            if "drought" in concern.lower():
                insights.append("Drought conditions are a primary concern - water management is critical.")
            elif "flood" in concern.lower():
                insights.append("Flood risk is elevated - drainage and flood protection measures are essential.")
            elif "heat" in concern.lower():
                insights.append("Heat stress is a concern - crop protection and cooling measures may be needed.")
        
        forecast = climate_analysis.get("forecast_data", [])
        if forecast:
            avg_temp = sum(w.get("temperature", 20) for w in forecast) / len(forecast)
            total_precip = sum(w.get("precipitation", 0) for w in forecast)
            
            if avg_temp > 30:
                insights.append(f"Above-average temperatures expected (avg: {avg_temp:.1f}°C) - heat stress management needed.")
            elif avg_temp < 15:
                insights.append(f"Below-average temperatures expected (avg: {avg_temp:.1f}°C) - cold stress protection may be needed.")
            
            if total_precip > 50:
                insights.append(f"Significant precipitation expected ({total_precip:.1f}mm) - flood risk management recommended.")
            elif total_precip < 10:
                insights.append(f"Low precipitation expected ({total_precip:.1f}mm) - drought risk management recommended.")
        
        return insights
    
    def _generate_environmental_insights(self, degradation_analysis: Dict) -> List[str]:
        insights = []
        
        environmental_health = degradation_analysis.get("environmental_health", {})
        health_status = environmental_health.get("health_status", "unknown")
        primary_concerns = environmental_health.get("primary_concerns", [])
        
        if health_status == "poor":
            insights.append("Environmental health is poor - immediate restoration measures are required.")
        elif health_status == "fair":
            insights.append("Environmental health is fair - improvement measures are recommended.")
        else:
            insights.append("Environmental health is good - maintain current conservation practices.")
        
        deforestation = degradation_analysis.get("deforestation", {})
        if deforestation.get("deforestation_percentage", 0) > 10:
            insights.append(f"Significant deforestation detected ({deforestation['deforestation_percentage']:.1f}%) - reforestation efforts needed.")
        
        soil_degradation = degradation_analysis.get("soil_degradation", {})
        if soil_degradation.get("degradation_percentage", 0) > 15:
            insights.append(f"Soil degradation detected ({soil_degradation['degradation_percentage']:.1f}%) - soil restoration measures required.")
        
        pollution = degradation_analysis.get("pollution_indicators", {})
        if pollution.get("overall_pollution_risk") == "high":
            insights.append("High pollution risk detected, environmental monitoring and remediation needed.")
        
        return insights
    
    def _generate_cross_analysis_insights(self, vegetation_analysis: Dict, climate_analysis: Dict, degradation_analysis: Dict) -> List[str]:
        insights = []
        
        vegetation_health = vegetation_analysis.get("health_score", 0.5)
        climate_risk = climate_analysis.get("overall_risk", {}).get("risk_level", "low")
        
        if vegetation_health < 0.4 and climate_risk in ["moderate", "high"]:
            insights.append("Poor vegetation health combined with climate stress suggests immediate intervention is needed.")
        elif vegetation_health > 0.6 and climate_risk == "low":
            insights.append("Good vegetation health with favorable climate conditions - optimal growing environment.")
        
        env_health = degradation_analysis.get("environmental_health", {}).get("health_status", "unknown")
        
        if env_health == "poor" and vegetation_health < 0.4:
            insights.append("Both environmental and vegetation health are poor - comprehensive restoration program needed.")
        elif env_health == "good" and vegetation_health > 0.6:
            insights.append("Excellent environmental and vegetation health - sustainable practices are working well.")
        
        return insights
    
    def _generate_immediate_actions(self, vegetation_analysis: Dict, climate_analysis: Dict, degradation_analysis: Dict) -> List[str]:
        actions = []
        
        if vegetation_analysis.get("drought_risk") == "high":
            actions.append("URGENT: Implement immediate irrigation - drought conditions detected")
        
        if climate_analysis.get("overall_risk", {}).get("risk_level") == "high":
            actions.append("URGENT: Activate emergency response protocols - high climate risk")
        
        if degradation_analysis.get("environmental_health", {}).get("health_status") == "poor":
            actions.append("URGENT: Begin environmental restoration - significant degradation detected")
        
        if vegetation_analysis.get("crop_stress_level") == "high":
            actions.append("HIGH PRIORITY: Address crop stress - implement stress mitigation measures")
        
        if degradation_analysis.get("deforestation", {}).get("illegal_clearing_risk") == "high":
            actions.append("HIGH PRIORITY: Investigate potential illegal clearing - immediate monitoring required")
        
        return actions
    
    def _generate_short_term_recommendations(self, vegetation_analysis: Dict, climate_analysis: Dict, predictions: Dict) -> List[str]:
        recommendations = []
        
        if vegetation_analysis.get("vegetation_change_percentage", 0) < -5:
            recommendations.append("Implement vegetation recovery program - focus on degraded areas")
        
        if vegetation_analysis.get("health_score", 0.5) < 0.6:
            recommendations.append("Apply soil amendments and fertilizers to improve vegetation health")
        
        if climate_analysis.get("drought_analysis", {}).get("risk_level") == "moderate":
            recommendations.append("Prepare drought-resistant crop varieties for next planting season")
        
        if climate_analysis.get("flood_analysis", {}).get("risk_level") == "moderate":
            recommendations.append("Improve drainage systems and flood protection measures")
        
        if predictions.get("recovery_time_months", 0) > 6:
            recommendations.append("Plan long-term recovery strategy - extended recovery period expected")
        
        if predictions.get("optimal_planting_confidence", 0) > 0.7:
            recommendations.append(f"Prepare for optimal planting window: {predictions.get('optimal_planting_date', 'TBD')}")
        
        return recommendations
    
    def _generate_long_term_recommendations(self, vegetation_analysis: Dict, climate_analysis: Dict, 
                                          degradation_analysis: Dict, predictions: Dict) -> List[str]:
        recommendations = []
        
        if degradation_analysis.get("environmental_health", {}).get("improvement_potential") == "high_improvement_potential":
            recommendations.append("Develop comprehensive environmental restoration plan")
        
        if vegetation_analysis.get("health_score", 0.5) < 0.6:
            recommendations.append("Implement sustainable agriculture practices to improve long-term soil health")
        
        if climate_analysis.get("overall_risk", {}).get("risk_level") in ["moderate", "high"]:
            recommendations.append("Develop climate resilience strategy - adapt to changing conditions")
        
        if predictions.get("predicted_ndvi_12_months", 0) > 0.7:
            recommendations.append("Plan for expansion - positive growth trajectory predicted")
        elif predictions.get("predicted_ndvi_12_months", 0) < 0.4:
            recommendations.append("Plan for intensive restoration - challenging conditions predicted")
        
        return recommendations
    
    def _generate_preventive_measures(self, climate_analysis: Dict, degradation_analysis: Dict) -> List[str]:
        measures = []
        
        if climate_analysis.get("drought_analysis", {}).get("risk_level") in ["moderate", "severe"]:
            measures.append("Install water storage and conservation systems")
        
        if climate_analysis.get("flood_analysis", {}).get("risk_level") in ["moderate", "high"]:
            measures.append("Implement flood prevention infrastructure")
        
        if degradation_analysis.get("violation_risk") == "high":
            measures.append("Establish environmental monitoring and compliance systems")
        
        if degradation_analysis.get("environmental_health", {}).get("health_status") == "fair":
            measures.append("Implement preventive conservation measures")
        
        return measures
    
    def _load_insight_templates(self) -> Dict[str, List[str]]:
        return {
            "vegetation_positive": [
                "Vegetation health shows {metric} improvement",
                "Strong growth indicators detected in {area}",
                "Optimal growing conditions observed"
            ],
            "vegetation_negative": [
                "Vegetation stress detected in {area}",
                "Declining health indicators require attention",
                "Immediate intervention needed for {condition}"
            ],
            "climate_risks": [
                "Climate risk level: {risk_level}",
                "Primary concerns: {concerns}",
                "Weather conditions favor {condition}"
            ],
            "environmental": [
                "Environmental health status: {status}",
                "Degradation detected: {type}",
                "Conservation measures recommended"
            ]
        }
    
    def _load_recommendation_templates(self) -> Dict[str, List[str]]:
        return {
            "immediate": [
                "URGENT: {action}",
                "HIGH PRIORITY: {action}",
                "Immediate action required: {action}"
            ],
            "short_term": [
                "Within 1-3 months: {action}",
                "Next season: {action}",
                "Short-term goal: {action}"
            ],
            "long_term": [
                "Long-term strategy: {action}",
                "Sustainable practice: {action}",
                "Future planning: {action}"
            ],
            "preventive": [
                "Preventive measure: {action}",
                "Risk mitigation: {action}",
                "Protection strategy: {action}"
            ]
        }