import os
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, green, red, orange, blue
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
import json

class ReportGenerator:
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#2E7D32') 
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=HexColor('#388E3C')
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=HexColor('#D32F2F'),  
            fontName='Helvetica-Bold'
        ))
    
    async def generate_report(self, aoi_id: str, analysis_result: Dict[str, Any]) -> str:
        try:
            report_path = os.path.join(self.reports_dir, f"{aoi_id}_report.pdf")
            
            doc = SimpleDocTemplate(
                report_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            story = []
            
            story.extend(self._create_header(analysis_result))
            
            story.extend(self._create_executive_summary(analysis_result))
            
            story.extend(self._create_analysis_sections(analysis_result))
            
            story.extend(self._create_recommendations_section(analysis_result))
            
            story.extend(self._create_appendices(analysis_result))
            
            doc.build(story)
            
            return report_path
            
        except Exception as e:
            raise Exception(f"Report generation failed: {str(e)}")
    
    def _create_header(self, analysis_result: Dict[str, Any]) -> List:
        story = []
        
        story.append(Paragraph("TerraMind Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        metadata = [
            ["Report ID:", analysis_result.get("aoi_id", "N/A")],
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
        
        return story
    
    def _create_executive_summary(self, analysis_result: Dict[str, Any]) -> List:
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        vegetation_analysis = analysis_result.get("vegetation_analysis", {})
        climate_analysis = analysis_result.get("climate_analysis", {})
        degradation_analysis = analysis_result.get("degradation_analysis", {})
        
        summary_text = f"""
        This comprehensive environmental analysis reveals the current state of vegetation health, 
        climate risks, and environmental conditions in the specified Area of Interest (AOI). 
        The analysis combines satellite imagery, climate data, and AI-powered assessments to 
        provide actionable insights for sustainable land management
        """
        
        story.append(Paragraph(summary_text, self.styles['CustomBody']))
        story.append(Spacer(1, 12))
        
        key_metrics = [
            ["Metric", "Current Value", "Status"],
            ["Vegetation Health Score", f"{vegetation_analysis.get('health_score', 0):.2f}", 
             self._get_status_text(vegetation_analysis.get('health_score', 0))],
            ["NDVI Change", f"{vegetation_analysis.get('ndvi_change', 0):.3f}", 
             self._get_change_status(vegetation_analysis.get('ndvi_change', 0))],
            ["Drought Risk", vegetation_analysis.get('drought_risk', 'Unknown').title(), 
             self._get_risk_status(vegetation_analysis.get('drought_risk', 'low'))],
            ["Climate Risk", climate_analysis.get('overall_risk', {}).get('risk_level', 'Unknown').title(), 
             self._get_risk_status(climate_analysis.get('overall_risk', {}).get('risk_level', 'low'))],
            ["Environmental Health", degradation_analysis.get('environmental_health', {}).get('health_status', 'Unknown').title(), 
             self._get_health_status(degradation_analysis.get('environmental_health', {}).get('health_status', 'unknown'))]
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
        
        return story
    
    def _create_analysis_sections(self, analysis_result: Dict[str, Any]) -> List:
        story = []
        
        story.extend(self._create_vegetation_analysis_section(analysis_result))
        story.append(PageBreak())
        
        story.extend(self._create_climate_analysis_section(analysis_result))
        story.append(PageBreak())
        
        story.extend(self._create_environmental_analysis_section(analysis_result))
        story.append(PageBreak())
        
        story.extend(self._create_predictions_section(analysis_result))
        
        return story
    
    def _create_vegetation_analysis_section(self, analysis_result: Dict[str, Any]) -> List:
        story = []
        
        story.append(Paragraph("Vegetation Analysis", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        vegetation_analysis = analysis_result.get("vegetation_analysis", {})
        
        story.append(Paragraph("Key Vegetation Metrics:", self.styles['Heading3']))
        
        metrics_data = [
            ["Current NDVI", f"{vegetation_analysis.get('ndvi_current', 0):.3f}"],
            ["Historical NDVI", f"{vegetation_analysis.get('ndvi_historical', 0):.3f}"],
            ["NDVI Change", f"{vegetation_analysis.get('ndvi_change', 0):.3f}"],
            ["Current NDWI", f"{vegetation_analysis.get('ndwi_current', 0):.3f}"],
            ["Vegetation Coverage", f"{vegetation_analysis.get('vegetation_coverage', 0):.1%}"],
            ["Health Score", f"{vegetation_analysis.get('health_score', 0):.2f}"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 12))
        
        interpretation = self._interpret_vegetation_analysis(vegetation_analysis)
        story.append(Paragraph(interpretation, self.styles['CustomBody']))
        
        return story
    
    def _create_climate_analysis_section(self, analysis_result: Dict[str, Any]) -> List:
        story = []
        
        story.append(Paragraph("Climate Risk Analysis", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        climate_analysis = analysis_result.get("climate_analysis", {})
        
        story.append(Paragraph("Climate Risk Assessment:", self.styles['Heading3']))
        
        drought_analysis = climate_analysis.get("drought_analysis", {})
        flood_analysis = climate_analysis.get("flood_analysis", {})
        heat_stress_analysis = climate_analysis.get("heat_stress_analysis", {})
        
        risk_data = [
            ["Risk Type", "Level", "Confidence", "Key Factors"],
            ["Drought Risk", drought_analysis.get("risk_level", "Unknown").title(), 
             f"{drought_analysis.get('confidence', 0):.1%}", 
             ", ".join(drought_analysis.get("factors", []))],
            ["Flood Risk", flood_analysis.get("risk_level", "Unknown").title(), 
             f"{flood_analysis.get('confidence', 0):.1%}", 
             ", ".join(flood_analysis.get("factors", []))],
            ["Heat Stress Risk", heat_stress_analysis.get("risk_level", "Unknown").title(), 
             f"{heat_stress_analysis.get('confidence', 0):.1%}", 
             f"Max Temp: {heat_stress_analysis.get('max_temperature', 0):.1f}°C"]
        ]
        
        risk_table = Table(risk_data, colWidths=[1.5*inch, 1*inch, 1*inch, 2.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2196F3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 1, black),
        ]))
        
        story.append(risk_table)
        story.append(Spacer(1, 12))
        
        interpretation = self._interpret_climate_analysis(climate_analysis)
        story.append(Paragraph(interpretation, self.styles['CustomBody']))
        
        return story
    
    def _create_environmental_analysis_section(self, analysis_result: Dict[str, Any]) -> List:
        story = []
        
        story.append(Paragraph("Environmental Health Analysis", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        degradation_analysis = analysis_result.get("degradation_analysis", {})
        
        story.append(Paragraph("Environmental Health Metrics:", self.styles['Heading3']))
        
        land_cover = degradation_analysis.get("land_cover_changes", {})
        deforestation = degradation_analysis.get("deforestation", {})
        soil_degradation = degradation_analysis.get("soil_degradation", {})
        environmental_health = degradation_analysis.get("environmental_health", {})
        
        env_data = [
            ["Metric", "Value", "Status"],
            ["Land Cover Change", f"{land_cover.get('change_percentage', 0):.1f}%", 
             land_cover.get('change_type', 'Unknown').title()],
            ["Deforestation", f"{deforestation.get('deforestation_percentage', 0):.1f}%", 
             deforestation.get('severity', 'Unknown').title()],
            ["Soil Degradation", f"{soil_degradation.get('degradation_percentage', 0):.1f}%", 
             soil_degradation.get('soil_health', 'Unknown').title()],
            ["Overall Health", f"{environmental_health.get('overall_score', 0):.2f}", 
             environmental_health.get('health_status', 'Unknown').title()]
        ]
        
        env_table = Table(env_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        env_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        story.append(env_table)
        story.append(Spacer(1, 12))
        
        interpretation = self._interpret_environmental_analysis(degradation_analysis)
        story.append(Paragraph(interpretation, self.styles['CustomBody']))
        
        return story
    
    def _create_predictions_section(self, analysis_result: Dict[str, Any]) -> List:
        story = []
        
        story.append(Paragraph("Future Predictions", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        predictions = analysis_result.get("predictions", {})
        
        story.append(Paragraph("Predicted Vegetation Health:", self.styles['Heading3']))
        
        pred_data = [
            ["Timeframe", "Predicted NDVI", "Confidence"],
            ["3 Months", f"{predictions.get('predicted_ndvi_3_months', 0):.3f}", 
             f"{predictions.get('prediction_confidence', 0):.1%}"],
            ["6 Months", f"{predictions.get('predicted_ndvi_6_months', 0):.3f}", 
             f"{predictions.get('prediction_confidence', 0):.1%}"],
            ["12 Months", f"{predictions.get('predicted_ndvi_12_months', 0):.3f}", 
             f"{predictions.get('prediction_confidence', 0):.1%}"]
        ]
        
        pred_table = Table(pred_data, colWidths=[2*inch, 2*inch, 2*inch])
        pred_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, black),
        ]))
        
        story.append(pred_table)
        story.append(Spacer(1, 12))
        
        recovery_time = predictions.get('recovery_time_months', 0)
        recovery_prob = predictions.get('recovery_probability', 0)
        
        recovery_text = f"""
        <b>Recovery Assessment:</b><br/>
        Estimated recovery time: {recovery_time} months<br/>
        Recovery probability: {recovery_prob:.1%}<br/>
        Optimal planting window: {predictions.get('optimal_planting_date', 'TBD')}
        """
        
        story.append(Paragraph(recovery_text, self.styles['CustomBody']))
        
        return story
    
    def _create_recommendations_section(self, analysis_result: Dict[str, Any]) -> List:
        story = []
        
        story.append(Paragraph("Recommendations & Action Items", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        insights = analysis_result.get("insights", [])
        recommendations = analysis_result.get("recommendations", [])
        
        story.append(Paragraph("Key Insights:", self.styles['Heading3']))
        for i, insight in enumerate(insights[:5], 1):
            story.append(Paragraph(f"{i}. {insight}", self.styles['CustomBody']))
        
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Recommended Actions:", self.styles['Heading3']))
        for i, recommendation in enumerate(recommendations[:10], 1):
            story.append(Paragraph(f"{i}. {recommendation}", self.styles['CustomBody']))
        
        return story
    
    def _create_appendices(self, analysis_result: Dict[str, Any]) -> List:
        story = []
        
        story.append(PageBreak())
        story.append(Paragraph("Appendices", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Technical Details:", self.styles['Heading3']))
        
        tech_details = f"""
        <b>Analysis Parameters:</b><br/>
        • Analysis Date: {analysis_result.get('timestamp', 'N/A')}<br/>
        • Current Image: {analysis_result.get('current_image_url', 'N/A')}<br/>
        • Historical Image: {analysis_result.get('historical_image_url', 'N/A')}<br/>
        • Analysis Type: Comprehensive Environmental Assessment<br/>
        • AI Models: U-Net Segmentation, LSTM Prediction, Climate Risk Assessment<br/>
        • Data Sources: Satellite Imagery, Climate APIs, Environmental Monitoring
        """
        
        story.append(Paragraph(tech_details, self.styles['CustomBody']))
        
        return story
    
    def _get_status_text(self, score: float) -> str:
        if score > 0.7:
            return "Excellent"
        elif score > 0.5:
            return "Good"
        elif score > 0.3:
            return "Fair"
        else:
            return "Poor"
    
    def _get_change_status(self, change: float) -> str:
        if change > 0.1:
            return "Improving"
        elif change < -0.1:
            return "Declining"
        else:
            return "Stable"
    
    def _get_risk_status(self, risk: str) -> str:
        risk_colors = {
            "low": "Low Risk",
            "moderate": "Moderate Risk", 
            "high": "High Risk",
            "severe": "Severe Risk"
        }
        return risk_colors.get(risk.lower(), "Unknown")
    
    def _get_health_status(self, health: str) -> str:
        health_colors = {
            "good": "Good",
            "fair": "Fair",
            "poor": "Poor"
        }
        return health_colors.get(health.lower(), "Unknown")
    
    def _interpret_vegetation_analysis(self, vegetation_analysis: Dict) -> str:
        health_score = vegetation_analysis.get('health_score', 0)
        ndvi_change = vegetation_analysis.get('ndvi_change', 0)
        drought_risk = vegetation_analysis.get('drought_risk', 'low')
        
        interpretation = f"""
        The vegetation analysis indicates a health score of {health_score:.2f}, which suggests 
        {self._get_status_text(health_score).lower()} vegetation conditions. The NDVI change of 
        {ndvi_change:.3f} indicates {self._get_change_status(ndvi_change).lower()} vegetation health. 
        The drought risk assessment shows {drought_risk} risk levels, which should be considered 
        in future planning and management decisions.
        """
        
        return interpretation
    
    def _interpret_climate_analysis(self, climate_analysis: Dict) -> str:
        overall_risk = climate_analysis.get('overall_risk', {})
        risk_level = overall_risk.get('risk_level', 'unknown')
        primary_concerns = overall_risk.get('primary_concerns', [])
        
        interpretation = f"""
        The climate risk assessment indicates {risk_level} overall risk levels. Primary concerns 
        include: {', '.join(primary_concerns) if primary_concerns else 'None identified'}. 
        This analysis should inform agricultural planning and risk mitigation strategies.
        """
        
        return interpretation
    
    def _interpret_environmental_analysis(self, degradation_analysis: Dict) -> str:
        environmental_health = degradation_analysis.get('environmental_health', {})
        health_status = environmental_health.get('health_status', 'unknown')
        overall_score = environmental_health.get('overall_score', 0)
        
        interpretation = f"""
        The environmental health assessment shows {health_status} conditions with an overall 
        score of {overall_score:.2f}. This indicates the need for {self._get_health_status(health_status).lower()} 
        environmental management practices and potential restoration measures.
        """
        
        return interpretation