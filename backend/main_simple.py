from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from datetime import datetime, timedelta
import random
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, green, red, orange, blue
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

app = FastAPI(
    title="TerraMind API",
    description="AI-powered environmental intelligence platform for sustainable agriculture",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AOIRequest(BaseModel):
    center_lat: float
    center_lon: float
    radius_km: float
    analysis_type: str = "comprehensive"

class AnalysisResult(BaseModel):
    aoi_id: str
    timestamp: datetime
    current_image_url: str
    historical_image_url: str
    vegetation_analysis: Dict[str, Any]
    climate_analysis: Dict[str, Any]
    degradation_analysis: Dict[str, Any]
    predictions: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    report_url: Optional[str] = None

analysis_cache = {}

@app.get("/")
async def root():
    return {
        "message": "TerraMind API - AI for Sustainable Agriculture",
        "version": "1.0.0",
        "status": "operational",
        "modules": ["AgroVision", "EcoGuard", "ClimaRisk", "InsightEngine"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules_status": {
            "agrovision": "operational",
            "ecoguard": "operational", 
            "climarisk": "operational",
            "insight_engine": "operational"
        }
    }

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_aoi(request: AOIRequest, background_tasks: BackgroundTasks):
    try:
        aoi_id = f"aoi_{request.center_lat}_{request.center_lon}_{request.radius_km}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        current_image_url = f"https://demo-terramind-images.s3.amazonaws.com/recent_{request.center_lat:.2f}_{request.center_lon:.2f}.jpg"
        historical_image_url = f"https://demo-terramind-images.s3.amazonaws.com/historical_{request.center_lat:.2f}_{request.center_lon:.2f}.jpg"
        
        vegetation_analysis = generate_demo_vegetation_analysis()
        
        climate_analysis = generate_demo_climate_analysis()
        
        degradation_analysis = generate_demo_degradation_analysis()
        
        predictions = generate_demo_predictions()
        
        insights = generate_demo_insights(vegetation_analysis, climate_analysis, degradation_analysis)
        
        recommendations = generate_demo_recommendations(vegetation_analysis, climate_analysis, degradation_analysis)
        
        result = AnalysisResult(
            aoi_id=aoi_id,
            timestamp=datetime.now(),
            current_image_url=current_image_url,
            historical_image_url=historical_image_url,
            vegetation_analysis=vegetation_analysis,
            climate_analysis=climate_analysis,
            degradation_analysis=degradation_analysis,
            predictions=predictions,
            insights=insights,
            recommendations=recommendations
        )
        
        analysis_cache[aoi_id] = result
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/analysis/{aoi_id}")
async def get_analysis(aoi_id: str):
    if aoi_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_cache[aoi_id]

@app.get("/report/{aoi_id}")
async def download_report(aoi_id: str):
    if aoi_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        os.makedirs("reports", exist_ok=True)
        
        report_path = f"reports/{aoi_id}_report.pdf"
        await generate_pdf_report(aoi_id, analysis_cache[aoi_id], report_path)
        
        return FileResponse(
            report_path,
            media_type="application/pdf",
            filename=f"terramind_report_{aoi_id}.pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@app.get("/satellite/imagery")
async def get_satellite_imagery(
    lat: float,
    lon: float,
    radius_km: float = 5.0,
    date: Optional[str] = None
):
    try:
        image_url = f"https://demo-terramind-images.s3.amazonaws.com/satellite_{lat:.2f}_{lon:.2f}.jpg"
        
        return {
            "image_url": image_url,
            "coordinates": {"lat": lat, "lon": lon},
            "radius_km": radius_km,
            "date": date or "recent"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch imagery: {str(e)}")

@app.get("/climate/forecast")
async def get_climate_forecast(lat: float, lon: float):
    try:
        forecast = generate_demo_forecast()
        risks = generate_demo_risks()
        
        return {
            "forecast": forecast,
            "risks": risks,
            "coordinates": {"lat": lat, "lon": lon}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get climate data: {str(e)}")

def generate_demo_vegetation_analysis():
    current_ndvi = random.uniform(0.3, 0.8)
    historical_ndvi = random.uniform(0.2, 0.7)
    ndvi_change = current_ndvi - historical_ndvi
    
    current_ndwi = random.uniform(0.1, 0.6)
    historical_ndwi = random.uniform(0.1, 0.5)
    ndwi_change = current_ndwi - historical_ndwi
    
    if ndvi_change > 0.1:
        change_type = "improvement"
        change_percentage = random.uniform(5, 20)
    elif ndvi_change < -0.1:
        change_type = "degradation"
        change_percentage = random.uniform(-20, -5)
    else:
        change_type = "stable"
        change_percentage = random.uniform(-5, 5)
    
    if current_ndvi < 0.3:
        stress_level = "high"
    elif current_ndvi < 0.5:
        stress_level = "moderate"
    else:
        stress_level = "low"
    
    health_score = (current_ndvi + current_ndwi) / 2
    
    if health_score < 0.3:
        drought_risk = "high"
    elif health_score < 0.6:
        drought_risk = "moderate"
    else:
        drought_risk = "low"
    
    return {
        "ndvi_current": round(current_ndvi, 3),
        "ndvi_historical": round(historical_ndvi, 3),
        "ndvi_change": round(ndvi_change, 3),
        "ndwi_current": round(current_ndwi, 3),
        "ndwi_historical": round(historical_ndwi, 3),
        "ndwi_change": round(ndwi_change, 3),
        "vegetation_change_percentage": round(change_percentage, 1),
        "vegetation_change_type": change_type,
        "crop_stress_level": stress_level,
        "crop_stress_areas": round(random.uniform(0.1, 0.4), 2),
        "vegetation_coverage": round(random.uniform(0.3, 0.9), 2),
        "health_score": round(health_score, 2),
        "drought_risk": drought_risk,
        "analysis_timestamp": datetime.now().isoformat()
    }

def generate_demo_climate_analysis():
    drought_risk = random.choice(["low", "moderate", "high"])
    flood_risk = random.choice(["low", "moderate", "high"])
    heat_stress_risk = random.choice(["low", "moderate", "high"])
    
    overall_risk = "high" if any(risk == "high" for risk in [drought_risk, flood_risk, heat_stress_risk]) else "moderate" if any(risk == "moderate" for risk in [drought_risk, flood_risk, heat_stress_risk]) else "low"
    
    return {
        "drought_analysis": {
            "risk_level": drought_risk,
            "confidence": round(random.uniform(0.6, 0.9), 2),
            "factors": ["precipitation", "humidity", "temperature"] if drought_risk != "low" else [],
            "precipitation_30d": round(random.uniform(20, 100), 1),
            "avg_humidity": round(random.uniform(30, 80), 1),
            "avg_temperature": round(random.uniform(15, 35), 1)
        },
        "flood_analysis": {
            "risk_level": flood_risk,
            "confidence": round(random.uniform(0.6, 0.9), 2),
            "factors": ["precipitation", "humidity", "wind"] if flood_risk != "low" else [],
            "max_24h_precipitation": round(random.uniform(30, 120), 1),
            "avg_humidity": round(random.uniform(50, 90), 1),
            "max_wind_speed": round(random.uniform(5, 20), 1)
        },
        "heat_stress_analysis": {
            "risk_level": heat_stress_risk,
            "confidence": round(random.uniform(0.6, 0.9), 2),
            "max_temperature": round(random.uniform(25, 40), 1),
            "heat_index": round(random.uniform(25, 45), 1),
            "avg_humidity": round(random.uniform(40, 80), 1)
        },
        "overall_risk": {
            "risk_level": overall_risk,
            "risk_score": round(random.uniform(0.2, 0.9), 2),
            "confidence": round(random.uniform(0.7, 0.9), 2),
            "primary_concerns": ["drought", "flood", "heat_stress"] if overall_risk == "high" else ["weather_variability"]
        }
    }

def generate_demo_degradation_analysis():
    land_cover_change = round(random.uniform(-15, 15), 1)
    deforestation_percentage = round(random.uniform(0, 20), 1)
    soil_degradation = round(random.uniform(0, 25), 1)
    
    if any(x > 15 for x in [abs(land_cover_change), deforestation_percentage, soil_degradation]):
        health_status = "poor"
        overall_score = round(random.uniform(0.2, 0.4), 2)
    elif any(x > 8 for x in [abs(land_cover_change), deforestation_percentage, soil_degradation]):
        health_status = "fair"
        overall_score = round(random.uniform(0.4, 0.6), 2)
    else:
        health_status = "good"
        overall_score = round(random.uniform(0.6, 0.9), 2)
    
    return {
        "land_cover_changes": {
            "change_percentage": land_cover_change,
            "change_type": "major_transformation" if abs(land_cover_change) > 15 else "moderate_change" if abs(land_cover_change) > 8 else "minor_change",
            "severity": "high" if abs(land_cover_change) > 15 else "moderate" if abs(land_cover_change) > 8 else "low"
        },
        "deforestation": {
            "deforestation_percentage": deforestation_percentage,
            "severity": "severe" if deforestation_percentage > 15 else "moderate" if deforestation_percentage > 8 else "mild",
            "illegal_clearing_risk": "high" if deforestation_percentage > 12 else "moderate" if deforestation_percentage > 6 else "low"
        },
        "soil_degradation": {
            "degradation_percentage": soil_degradation,
            "soil_health": "poor" if soil_degradation > 15 else "fair" if soil_degradation > 8 else "good"
        },
        "environmental_health": {
            "overall_score": overall_score,
            "health_status": health_status,
            "primary_concerns": ["significant_degradation"] if health_status == "poor" else ["moderate_changes"] if health_status == "fair" else ["stable_conditions"],
            "improvement_potential": "high_improvement_potential" if health_status == "poor" else "moderate_improvement_potential" if health_status == "fair" else "maintain_current_conditions"
        }
    }

def generate_demo_predictions():
    base_ndvi = random.uniform(0.3, 0.7)
    
    return {
        "predicted_ndvi_3_months": round(base_ndvi + random.uniform(-0.1, 0.2), 3),
        "predicted_ndvi_6_months": round(base_ndvi + random.uniform(-0.2, 0.3), 3),
        "predicted_ndvi_12_months": round(base_ndvi + random.uniform(-0.3, 0.4), 3),
        "recovery_time_months": random.randint(3, 12),
        "recovery_probability": round(random.uniform(0.6, 0.9), 2),
        "optimal_planting_date": "Next 2-4 weeks",
        "optimal_planting_confidence": round(random.uniform(0.7, 0.9), 2),
        "prediction_confidence": round(random.uniform(0.7, 0.9), 2),
        "prediction_timestamp": datetime.now().isoformat()
    }

def generate_demo_insights(vegetation_analysis, climate_analysis, degradation_analysis):
    insights = []
    
    if vegetation_analysis["ndvi_change"] > 0.1:
        insights.append(f"Vegetation health has improved by {vegetation_analysis['ndvi_change']:.3f} NDVI units, indicating positive growth conditions.")
    elif vegetation_analysis["ndvi_change"] < -0.1:
        insights.append(f"Vegetation health has declined by {abs(vegetation_analysis['ndvi_change']):.3f} NDVI units, suggesting stress or degradation.")
    else:
        insights.append("Vegetation health remains relatively stable with minimal changes detected.")
    
    overall_risk = climate_analysis["overall_risk"]["risk_level"]
    if overall_risk == "high":
        insights.append("High climate risk detected - immediate action required to protect agricultural assets.")
    elif overall_risk == "moderate":
        insights.append("Moderate climate risk present - proactive measures recommended.")
    else:
        insights.append("Climate conditions are favorable for agricultural activities.")
    
    env_health = degradation_analysis["environmental_health"]["health_status"]
    if env_health == "poor":
        insights.append("Environmental health is poor - immediate restoration measures are required.")
    elif env_health == "fair":
        insights.append("Environmental health is fair - improvement measures are recommended.")
    else:
        insights.append("Environmental health is good - maintain current conservation practices.")
    
    return insights[:5]

def generate_demo_recommendations(vegetation_analysis, climate_analysis, degradation_analysis):
    recommendations = []
    
    if vegetation_analysis["drought_risk"] == "high":
        recommendations.append("URGENT: Implement immediate irrigation - drought conditions detected")
    
    if climate_analysis["overall_risk"]["risk_level"] == "high":
        recommendations.append("URGENT: Activate emergency response protocols - high climate risk")
    
    if degradation_analysis["environmental_health"]["health_status"] == "poor":
        recommendations.append("URGENT: Begin environmental restoration - significant degradation detected")
    
    if vegetation_analysis["vegetation_change_percentage"] < -5:
        recommendations.append("Implement vegetation recovery program - focus on degraded areas")
    
    if vegetation_analysis["health_score"] < 0.6:
        recommendations.append("Apply soil amendments and fertilizers to improve vegetation health")
    
    if degradation_analysis["environmental_health"]["improvement_potential"] == "high_improvement_potential":
        recommendations.append("Develop comprehensive environmental restoration plan")
    
    if vegetation_analysis["health_score"] < 0.6:
        recommendations.append("Implement sustainable agriculture practices to improve long-term soil health")
    
    return recommendations[:10]

def generate_demo_forecast():
    return {
        "current": {
            "temperature": round(random.uniform(15, 35), 1),
            "humidity": round(random.uniform(30, 80), 1),
            "precipitation": round(random.uniform(0, 10), 1)
        },
        "forecast_5_days": [
            {
                "date": (datetime.now() + timedelta(days=i)).isoformat(),
                "temperature": round(random.uniform(15, 35), 1),
                "humidity": round(random.uniform(30, 80), 1),
                "precipitation": round(random.uniform(0, 15), 1)
            }
            for i in range(5)
        ]
    }

def generate_demo_risks():
    return {
        "drought_risk": random.choice(["low", "moderate", "high"]),
        "flood_risk": random.choice(["low", "moderate", "high"]),
        "heat_stress_risk": random.choice(["low", "moderate", "high"]),
        "storm_risk": random.choice(["low", "moderate", "high"])
    }

async def generate_pdf_report(aoi_id: str, analysis_result: AnalysisResult, report_path: str):
    try:
        doc = SimpleDocTemplate(
            report_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2E7D32')
        )
        
        subtitle_style = ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=HexColor('#388E3C')
        )
        
        story = []
        
        story.append(Paragraph("TerraMind Analysis Report", title_style))
        story.append(Spacer(1, 12))
        
        metadata = [
            ["Report ID:", aoi_id],
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Analysis Type:", "Comprehensive Environmental Assessment"],
            ["Status:", "Complete"]
        ]
        
        metadata_table = Table(metadata, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Executive Summary", subtitle_style))
        story.append(Spacer(1, 12))
        
        vegetation = analysis_result.vegetation_analysis
        climate = analysis_result.climate_analysis
        degradation = analysis_result.degradation_analysis
        
        summary_text = f"""
        This comprehensive environmental analysis reveals the current state of vegetation health, 
        climate risks, and environmental conditions in the specified Area of Interest (AOI). 
        The analysis combines satellite imagery, climate data, and AI-powered assessments to 
        provide actionable insights for sustainable land management.
        
        Key findings include a vegetation health score of {vegetation['health_score']:.2f}, 
        {climate['overall_risk']['risk_level']} climate risk levels, and {degradation['environmental_health']['health_status']} 
        environmental health conditions.
        """
        
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Key Metrics", subtitle_style))
        story.append(Spacer(1, 12))
        
        key_metrics = [
            ["Metric", "Value", "Status"],
            ["Vegetation Health Score", f"{vegetation['health_score']:.2f}", 
             "Excellent" if vegetation['health_score'] > 0.7 else "Good" if vegetation['health_score'] > 0.5 else "Fair" if vegetation['health_score'] > 0.3 else "Poor"],
            ["NDVI Change", f"{vegetation['ndvi_change']:.3f}", 
             "Improving" if vegetation['ndvi_change'] > 0.1 else "Declining" if vegetation['ndvi_change'] < -0.1 else "Stable"],
            ["Drought Risk", vegetation['drought_risk'].title(), 
             vegetation['drought_risk'].title()],
            ["Climate Risk", climate['overall_risk']['risk_level'].title(), 
             climate['overall_risk']['risk_level'].title()],
            ["Environmental Health", degradation['environmental_health']['health_status'].title(), 
             degradation['environmental_health']['health_status'].title()]
        ]
        
        metrics_table = Table(key_metrics, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, black),
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Vegetation Analysis", subtitle_style))
        story.append(Spacer(1, 12))
        
        veg_text = f"""
        The vegetation analysis indicates a health score of {vegetation['health_score']:.2f}, which suggests 
        {'excellent' if vegetation['health_score'] > 0.7 else 'good' if vegetation['health_score'] > 0.5 else 'fair' if vegetation['health_score'] > 0.3 else 'poor'} 
        vegetation conditions. The NDVI change of {vegetation['ndvi_change']:.3f} indicates 
        {'improving' if vegetation['ndvi_change'] > 0.1 else 'declining' if vegetation['ndvi_change'] < -0.1 else 'stable'} 
        vegetation health. The drought risk assessment shows {vegetation['drought_risk']} risk levels.
        """
        
        story.append(Paragraph(veg_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Climate Risk Assessment", subtitle_style))
        story.append(Spacer(1, 12))
        
        climate_text = f"""
        The climate risk assessment indicates {climate['overall_risk']['risk_level']} overall risk levels. 
        Primary concerns include drought risk ({climate['drought_analysis']['risk_level']}), 
        flood risk ({climate['flood_analysis']['risk_level']}), and heat stress risk ({climate['heat_stress_analysis']['risk_level']}). 
        This analysis should inform agricultural planning and risk mitigation strategies.
        """
        
        story.append(Paragraph(climate_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Environmental Health Analysis", subtitle_style))
        story.append(Spacer(1, 12))
        
        env_text = f"""
        The environmental health assessment shows {degradation['environmental_health']['health_status']} conditions with an overall 
        score of {degradation['environmental_health']['overall_score']:.2f}. This indicates the need for 
        {'immediate restoration' if degradation['environmental_health']['health_status'] == 'poor' else 'improvement measures' if degradation['environmental_health']['health_status'] == 'fair' else 'maintaining current practices'} 
        environmental management practices.
        """
        
        story.append(Paragraph(env_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Key Insights", subtitle_style))
        story.append(Spacer(1, 12))
        
        for i, insight in enumerate(analysis_result.insights[:5], 1):
            story.append(Paragraph(f"{i}. {insight}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Recommendations", subtitle_style))
        story.append(Spacer(1, 12))
        
        for i, recommendation in enumerate(analysis_result.recommendations[:8], 1):
            story.append(Paragraph(f"{i}. {recommendation}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Technical Details", subtitle_style))
        story.append(Spacer(1, 12))
        
        tech_details = f"""
        Analysis Parameters:
        • Analysis Date: {analysis_result.timestamp}
        • Current Image: {analysis_result.current_image_url}
        • Historical Image: {analysis_result.historical_image_url}
        • Analysis Type: Comprehensive Environmental Assessment
        • AI Models: U-Net Segmentation, LSTM Prediction, Climate Risk Assessment
        • Data Sources: Satellite Imagery, Climate APIs, Environmental Monitoring
        """
        
        story.append(Paragraph(tech_details, styles['Normal']))
        
        doc.build(story)
        
    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")

if __name__ == "__main__":
    os.makedirs("reports", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)