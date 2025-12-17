"""
AI Agent Engine for Crop Monitoring System
Implements rule-based logic for anomaly analysis and recommendations
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import json

class AnomalySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    SOIL_MOISTURE = "soil_moisture"
    PH_LEVEL = "ph_level"
    LIGHT_INTENSITY = "light_intensity"

@dataclass
class AnomalyAlert:
    """Represents an anomaly detected by the agent"""
    alert_type: AlertType
    severity: AnomalySeverity
    message: str
    current_value: float
    threshold_value: float
    timestamp: str
    recommendations: List[str]

class RuleEngine:
    """Defines rules for anomaly detection"""
    
    def __init__(self):
        self.rules = {
            AlertType.TEMPERATURE: {
                "min": 15,
                "max": 35,
                "critical_min": 10,
                "critical_max": 40
            },
            AlertType.HUMIDITY: {
                "min": 40,
                "max": 80,
                "critical_min": 20,
                "critical_max": 95
            },
            AlertType.SOIL_MOISTURE: {
                "min": 30,
                "max": 80,
                "critical_min": 15,
                "critical_max": 90
            },
            AlertType.PH_LEVEL: {
                "min": 6.0,
                "max": 7.5,
                "critical_min": 5.5,
                "critical_max": 8.0
            },
            AlertType.LIGHT_INTENSITY: {
                "min": 200,
                "max": 1000,
                "critical_min": 100,
                "critical_max": 1200
            }
        }
    
    def evaluate_value(self, alert_type: AlertType, value: float) -> Optional[Dict[str, Any]]:
        """
        Evaluate a sensor value against defined rules
        Returns severity level and threshold info if anomaly detected
        """
        if alert_type not in self.rules:
            return None
        
        rule = self.rules[alert_type]
        
        if value < rule["critical_min"] or value > rule["critical_max"]:
            return {
                "severity": AnomalySeverity.CRITICAL,
                "threshold": rule["critical_min"] if value < rule["min"] else rule["critical_max"]
            }
        elif value < rule["min"] or value > rule["max"]:
            return {
                "severity": AnomalySeverity.HIGH,
                "threshold": rule["min"] if value < rule["min"] else rule["max"]
            }
        elif (value < rule["min"] + 3) or (value > rule["max"] - 3):
            return {
                "severity": AnomalySeverity.MEDIUM,
                "threshold": rule["min"] if value < rule["min"] else rule["max"]
            }
        
        return None

class RecommendationGenerator:
    """Generates actionable recommendations based on anomalies"""
    
    RECOMMENDATION_TEMPLATES = {
        AlertType.TEMPERATURE: {
            "low": [
                "Increase greenhouse heating system to raise ambient temperature",
                "Consider using thermal blankets or row covers to protect plants",
                "Reduce ventilation to retain heat inside the growing area",
                "Apply mulch to soil surface to maintain root temperature"
            ],
            "high": [
                "Increase ventilation to cool the greenhouse",
                "Activate cooling systems or shade cloths if available",
                "Water plants more frequently during peak heat hours",
                "Spray water on leaves to provide evaporative cooling"
            ]
        },
        AlertType.HUMIDITY: {
            "low": [
                "Install misting systems to increase humidity levels",
                "Reduce ventilation to trap moisture",
                "Water plants more frequently to increase soil moisture evaporation",
                "Provide organic mulch to reduce moisture evaporation from soil"
            ],
            "high": [
                "Increase ventilation to reduce humidity",
                "Use dehumidifiers if available",
                "Space plants further apart to improve air circulation",
                "Reduce watering frequency to prevent fungal diseases"
            ]
        },
        AlertType.SOIL_MOISTURE: {
            "low": [
                "Increase irrigation frequency and duration",
                "Apply drip irrigation for more efficient water delivery",
                "Add mulch to soil to reduce evaporation",
                "Water during cooler parts of the day"
            ],
            "high": [
                "Reduce irrigation frequency to prevent root rot",
                "Improve soil drainage by adding organic matter",
                "Ensure drainage systems are functioning properly",
                "Aerate soil if it has become compacted"
            ]
        },
        AlertType.PH_LEVEL: {
            "low": [
                "Add lime (calcium carbonate) to raise soil pH",
                "Apply wood ash to increase alkalinity",
                "Reduce nitrogen-heavy fertilizers",
                "Test soil weekly to monitor pH changes"
            ],
            "high": [
                "Add sulfur or sulfuric acid to lower soil pH",
                "Apply aluminum sulfate to acidify soil",
                "Use acidifying fertilizers",
                "Incorporate peat moss into soil"
            ]
        },
        AlertType.LIGHT_INTENSITY: {
            "low": [
                "Install or increase supplemental LED grow lights",
                "Position plants closer to existing light sources",
                "Clean greenhouse panels to maximize natural light transmission",
                "Prune excess foliage to allow more light to lower leaves"
            ],
            "high": [
                "Install shade cloths to reduce light intensity",
                "Move plants to areas with less direct sunlight",
                "Adjust light fixtures to reduce intensity",
                "Provide adequate ventilation to prevent heat stress"
            ]
        }
    }
    
    @staticmethod
    def generate_recommendations(alert_type: AlertType, current_value: float, 
                                threshold_value: float) -> List[str]:
        """Generate recommendations based on anomaly type and direction"""
        direction = "low" if current_value < threshold_value else "high"
        
        if alert_type in RecommendationGenerator.RECOMMENDATION_TEMPLATES:
            templates = RecommendationGenerator.RECOMMENDATION_TEMPLATES[alert_type]
            if direction in templates:
                return templates[direction]
        
        return ["Monitor this metric closely and adjust environmental conditions accordingly"]

class CropMonitoringAgent:
    """Main AI Agent for crop monitoring"""
    
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.recommendation_gen = RecommendationGenerator()
    
    def analyze_sensor_data(self, sensor_data: Dict[str, float], 
                        plot_id: str, timestamp: str) -> List[AnomalyAlert]:
        """
        Analyze sensor data and generate alerts with recommendations
        
        Args:
            sensor_data: Dict with keys like temperature, humidity, soil_moisture, ph_level, light_intensity
            plot_id: ID of the monitoring plot
            timestamp: Timestamp of the measurement
        
        Returns:
            List of AnomalyAlert objects
        """
        alerts = []
        
        for sensor_type_str, value in sensor_data.items():
            try:
                sensor_type = AlertType[sensor_type_str.upper()]
            except KeyError:
                continue
            
            rule_result = self.rule_engine.evaluate_value(sensor_type, value)
            
            if rule_result:
                recommendations = self.recommendation_gen.generate_recommendations(
                    sensor_type, value, rule_result["threshold"]
                )
                
                alert = AnomalyAlert(
                    alert_type=sensor_type,
                    severity=rule_result["severity"],
                    message=self._generate_message(sensor_type, value, rule_result["threshold"]),
                    current_value=value,
                    threshold_value=rule_result["threshold"],
                    timestamp=timestamp,
                    recommendations=recommendations
                )
                alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def _generate_message(alert_type: AlertType, current_value: float, 
                         threshold_value: float) -> str:
        """Generate human-readable alert message"""
        direction = "below" if current_value < threshold_value else "above"
        return f"{alert_type.value.replace('_', ' ').title()} is {direction} optimal range: {current_value:.2f}"
    
    def get_alerts_summary(self, alerts: List[AnomalyAlert]) -> Dict[str, Any]:
        """Get summary statistics of alerts"""
        if not alerts:
            return {"total": 0, "by_severity": {}, "critical_count": 0}
        
        summary = {
            "total": len(alerts),
            "by_severity": {},
            "critical_count": sum(1 for a in alerts if a.severity == AnomalySeverity.CRITICAL)
        }
        
        for severity in AnomalySeverity:
            count = sum(1 for a in alerts if a.severity == severity)
            summary["by_severity"][severity.value] = count
        
        return summary