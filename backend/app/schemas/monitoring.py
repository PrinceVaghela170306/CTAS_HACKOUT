from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class CoordinatesResponse(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")

class ErosionMetrics(BaseModel):
    shoreline_retreat_meters: float = Field(..., description="Shoreline retreat in meters")
    erosion_rate_m_per_year: float = Field(..., description="Annual erosion rate in meters")
    affected_coastline_km: float = Field(..., description="Length of affected coastline in kilometers")
    severity: str = Field(..., description="Erosion severity level")
    trend: str = Field(..., description="Erosion trend")

class HistoricalChange(BaseModel):
    date: str = Field(..., description="Date of measurement")
    shoreline_position: float = Field(..., description="Shoreline position change")
    vegetation_loss_percent: float = Field(..., description="Vegetation loss percentage")

class RiskAssessmentErosion(BaseModel):
    infrastructure_at_risk: bool = Field(..., description="Whether infrastructure is at risk")
    population_affected: int = Field(..., description="Number of people affected")
    economic_impact_estimate: int = Field(..., description="Economic impact estimate in USD")

class CoastalErosionResponse(BaseModel):
    location: str = Field(..., description="Location name")
    coordinates: CoordinatesResponse
    monitoring_period_months: int = Field(..., description="Monitoring period in months")
    data_source: str = Field(..., description="Data source")
    analysis_date: str = Field(..., description="Analysis date")
    erosion_metrics: ErosionMetrics
    historical_changes: List[HistoricalChange]
    risk_assessment: RiskAssessmentErosion

class BloomMetrics(BaseModel):
    chlorophyll_concentration: float = Field(..., description="Chlorophyll concentration")
    bloom_area_km2: float = Field(..., description="Bloom area in square kilometers")
    bloom_intensity: str = Field(..., description="Bloom intensity level")
    bloom_type: Optional[str] = Field(None, description="Type of algal bloom")
    toxicity_level: str = Field(..., description="Toxicity level")

class HealthAdvisory(BaseModel):
    swimming_advisory: str = Field(..., description="Swimming safety advisory")
    fishing_advisory: str = Field(..., description="Fishing safety advisory")
    water_contact_warning: bool = Field(..., description="Water contact warning")
    expected_duration_days: int = Field(..., description="Expected duration in days")

class EnvironmentalConditions(BaseModel):
    sea_surface_temperature: float = Field(..., description="Sea surface temperature")
    nutrient_levels: str = Field(..., description="Nutrient levels")
    water_turbidity: float = Field(..., description="Water turbidity")

class AlgalBloomResponse(BaseModel):
    location: str = Field(..., description="Location name")
    coordinates: CoordinatesResponse
    data_source: str = Field(..., description="Data source")
    observation_date: str = Field(..., description="Observation date")
    bloom_detected: bool = Field(..., description="Whether bloom is detected")
    bloom_metrics: BloomMetrics
    health_advisory: HealthAdvisory
    environmental_conditions: EnvironmentalConditions

class WaterQualityParameters(BaseModel):
    ph_level: float = Field(..., description="pH level")
    dissolved_oxygen_mg_l: float = Field(..., description="Dissolved oxygen in mg/L")
    turbidity_ntu: float = Field(..., description="Turbidity in NTU")
    salinity_ppt: float = Field(..., description="Salinity in parts per thousand")
    temperature_celsius: float = Field(..., description="Temperature in Celsius")
    nitrate_mg_l: float = Field(..., description="Nitrate in mg/L")
    phosphate_mg_l: float = Field(..., description="Phosphate in mg/L")
    bacteria_count_cfu_100ml: int = Field(..., description="Bacteria count per 100ml")

class QualityIndex(BaseModel):
    overall_score: int = Field(..., description="Overall quality score")
    rating: str = Field(..., description="Quality rating")
    safe_for_recreation: bool = Field(..., description="Safe for recreational activities")
    safe_for_marine_life: bool = Field(..., description="Safe for marine life")

class PollutionIndicators(BaseModel):
    oil_spill_detected: bool = Field(..., description="Oil spill detection")
    plastic_debris_level: str = Field(..., description="Plastic debris level")
    chemical_contamination: str = Field(..., description="Chemical contamination level")
    sewage_indicators: str = Field(..., description="Sewage indicator levels")

class WaterQualityResponse(BaseModel):
    location: str = Field(..., description="Location name")
    coordinates: CoordinatesResponse
    measurement_date: str = Field(..., description="Measurement date")
    parameters: WaterQualityParameters
    quality_index: QualityIndex
    pollution_indicators: PollutionIndicators

class CoastalErosionAnalysis(BaseModel):
    shoreline_change_m: float = Field(..., description="Shoreline change in meters")
    erosion_hotspots: int = Field(..., description="Number of erosion hotspots")
    vegetation_loss_percent: float = Field(..., description="Vegetation loss percentage")

class PollutionDetection(BaseModel):
    oil_slick_detected: bool = Field(..., description="Oil slick detection")
    sediment_plume_area_km2: float = Field(..., description="Sediment plume area")
    water_discoloration: str = Field(..., description="Water discoloration level")

class VegetationHealth(BaseModel):
    ndvi_average: float = Field(..., description="Average NDVI value")
    mangrove_coverage_km2: float = Field(..., description="Mangrove coverage area")
    vegetation_stress_level: str = Field(..., description="Vegetation stress level")

class SatelliteImageryResponse(BaseModel):
    location: str = Field(..., description="Location name")
    coordinates: CoordinatesResponse
    analysis_date: str = Field(..., description="Analysis date")
    satellite_source: str = Field(..., description="Satellite data source")
    image_resolution_meters: int = Field(..., description="Image resolution in meters")
    cloud_cover_percent: float = Field(..., description="Cloud cover percentage")
    analysis_results: Dict[str, Any] = Field(..., description="Analysis results")

class KeyIndicators(BaseModel):
    coastal_erosion_risk: str = Field(..., description="Coastal erosion risk level")
    water_quality_status: str = Field(..., description="Water quality status")
    algal_bloom_risk: str = Field(..., description="Algal bloom risk level")
    pollution_level: str = Field(..., description="Pollution level")
    ecosystem_health: str = Field(..., description="Ecosystem health status")

class RecentChanges(BaseModel):
    shoreline_stability: str = Field(..., description="Shoreline stability trend")
    water_temperature_trend: str = Field(..., description="Water temperature trend")
    biodiversity_trend: str = Field(..., description="Biodiversity trend")

class EnvironmentalSummaryResponse(BaseModel):
    location: str = Field(..., description="Location name")
    coordinates: CoordinatesResponse
    summary_date: str = Field(..., description="Summary date")
    overall_environmental_health: str = Field(..., description="Overall environmental health")
    key_indicators: KeyIndicators
    recent_changes: RecentChanges
    recommendations: List[str] = Field(..., description="Environmental recommendations")
    data_sources: List[str] = Field(..., description="Data sources used")