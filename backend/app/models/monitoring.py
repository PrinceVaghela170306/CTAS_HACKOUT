from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class MonitoringStation(Base):
    __tablename__ = "monitoring_stations"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    station_type = Column(String, nullable=False)  # tide, weather, wave, water_quality
    
    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_m = Column(Float, nullable=True)
    water_depth_m = Column(Float, nullable=True)
    
    # Station details
    operator = Column(String, nullable=True)  # NOAA, local authority, etc.
    station_code = Column(String, nullable=True, unique=True)
    description = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_data_received = Column(DateTime(timezone=True))
    data_quality_score = Column(Float, default=1.0)  # 0-1 quality score
    
    # Capabilities
    measures_tide = Column(Boolean, default=False)
    measures_waves = Column(Boolean, default=False)
    measures_weather = Column(Boolean, default=False)
    measures_water_quality = Column(Boolean, default=False)
    
    # Metadata
    installation_date = Column(DateTime(timezone=True))
    last_maintenance = Column(DateTime(timezone=True))
    next_maintenance = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    environmental_data = relationship("EnvironmentalData", back_populates="station")
    
    def __repr__(self):
        return f"<MonitoringStation(id={self.id}, name={self.name}, type={self.station_type})>"

class TideData(Base):
    __tablename__ = "tide_data"
    
    id = Column(String, primary_key=True, index=True)
    station_id = Column(String, nullable=False, index=True)
    
    # Measurement data
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    water_level_m = Column(Float, nullable=False)
    predicted_level_m = Column(Float, nullable=True)
    residual_m = Column(Float, nullable=True)  # observed - predicted
    
    # Tide characteristics
    tide_type = Column(String, nullable=True)  # high, low, rising, falling
    tidal_range_m = Column(Float, nullable=True)
    
    # Quality indicators
    data_quality = Column(String, default="good")  # excellent, good, fair, poor
    flags = Column(JSON, default=list)  # Quality control flags
    
    # Metadata
    source = Column(String, nullable=True)
    processing_level = Column(String, default="raw")  # raw, processed, verified
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_tide_station_time', 'station_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<TideData(station_id={self.station_id}, timestamp={self.timestamp}, level={self.water_level_m})>"

class WaveData(Base):
    __tablename__ = "wave_data"
    
    id = Column(String, primary_key=True, index=True)
    station_id = Column(String, nullable=False, index=True)
    
    # Measurement data
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    significant_wave_height_m = Column(Float, nullable=False)
    peak_wave_period_s = Column(Float, nullable=True)
    average_wave_period_s = Column(Float, nullable=True)
    
    # Wave characteristics
    wave_direction_deg = Column(Float, nullable=True)  # 0-360 degrees
    dominant_wave_direction = Column(String, nullable=True)  # N, NE, E, etc.
    max_wave_height_m = Column(Float, nullable=True)
    
    # Spectral data
    wave_energy_density = Column(Float, nullable=True)
    spectral_peak_frequency = Column(Float, nullable=True)
    
    # Quality indicators
    data_quality = Column(String, default="good")
    flags = Column(JSON, default=list)
    
    # Metadata
    source = Column(String, nullable=True)
    processing_level = Column(String, default="raw")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_wave_station_time', 'station_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<WaveData(station_id={self.station_id}, timestamp={self.timestamp}, height={self.significant_wave_height_m})>"

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id = Column(String, primary_key=True, index=True)
    station_id = Column(String, nullable=True, index=True)  # Can be null for gridded data
    
    # Location (for gridded data)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Measurement data
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    temperature_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)
    pressure_hpa = Column(Float, nullable=False)
    
    # Wind data
    wind_speed_kmh = Column(Float, nullable=True)
    wind_direction_deg = Column(Float, nullable=True)
    wind_gust_kmh = Column(Float, nullable=True)
    
    # Precipitation
    precipitation_mm = Column(Float, default=0.0)
    precipitation_type = Column(String, nullable=True)  # rain, snow, sleet
    
    # Visibility and conditions
    visibility_km = Column(Float, nullable=True)
    cloud_cover_percent = Column(Float, nullable=True)
    weather_condition = Column(String, nullable=True)  # clear, cloudy, stormy, etc.
    
    # Quality indicators
    data_quality = Column(String, default="good")
    flags = Column(JSON, default=list)
    
    # Metadata
    source = Column(String, nullable=True)  # OpenWeather, NOAA, etc.
    data_type = Column(String, default="observed")  # observed, forecast, reanalysis
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_weather_station_time', 'station_id', 'timestamp'),
        Index('idx_weather_location_time', 'latitude', 'longitude', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<WeatherData(station_id={self.station_id}, timestamp={self.timestamp}, temp={self.temperature_c})>"

class WaterQualityData(Base):
    __tablename__ = "water_quality_data"
    
    id = Column(String, primary_key=True, index=True)
    station_id = Column(String, nullable=False, index=True)
    
    # Measurement data
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Basic parameters
    temperature_c = Column(Float, nullable=True)
    ph_level = Column(Float, nullable=True)
    dissolved_oxygen_mg_l = Column(Float, nullable=True)
    turbidity_ntu = Column(Float, nullable=True)
    salinity_ppt = Column(Float, nullable=True)
    
    # Nutrients
    nitrate_mg_l = Column(Float, nullable=True)
    nitrite_mg_l = Column(Float, nullable=True)
    phosphate_mg_l = Column(Float, nullable=True)
    ammonia_mg_l = Column(Float, nullable=True)
    
    # Biological indicators
    chlorophyll_a_ug_l = Column(Float, nullable=True)
    bacteria_count_cfu_100ml = Column(Integer, nullable=True)
    coliform_count_cfu_100ml = Column(Integer, nullable=True)
    
    # Chemical indicators
    heavy_metals_mg_l = Column(JSON, default=dict)  # Dictionary of metal concentrations
    pesticides_mg_l = Column(JSON, default=dict)  # Dictionary of pesticide concentrations
    
    # Quality assessment
    water_quality_index = Column(Float, nullable=True)  # 0-100 scale
    quality_rating = Column(String, nullable=True)  # excellent, good, fair, poor
    
    # Pollution indicators
    oil_sheen_detected = Column(Boolean, default=False)
    algal_bloom_detected = Column(Boolean, default=False)
    unusual_color = Column(String, nullable=True)
    unusual_odor = Column(String, nullable=True)
    
    # Quality indicators
    data_quality = Column(String, default="good")
    flags = Column(JSON, default=list)
    
    # Metadata
    source = Column(String, nullable=True)
    sampling_method = Column(String, nullable=True)
    lab_analysis = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_water_quality_station_time', 'station_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<WaterQualityData(station_id={self.station_id}, timestamp={self.timestamp})>"

class SatelliteData(Base):
    __tablename__ = "satellite_data"
    
    id = Column(String, primary_key=True, index=True)
    
    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    bounding_box = Column(JSON, nullable=True)  # Geographic bounding box
    
    # Satellite information
    satellite_name = Column(String, nullable=False)  # Sentinel-2, Landsat-8, etc.
    sensor_type = Column(String, nullable=False)  # MSI, OLI, MODIS, etc.
    acquisition_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Image metadata
    cloud_cover_percent = Column(Float, nullable=True)
    resolution_meters = Column(Float, nullable=True)
    image_quality = Column(String, default="good")
    
    # Analysis results
    analysis_type = Column(String, nullable=False)  # erosion, vegetation, water_quality, etc.
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Coastal erosion analysis
    shoreline_change_m = Column(Float, nullable=True)
    erosion_rate_m_per_year = Column(Float, nullable=True)
    
    # Vegetation analysis
    ndvi_average = Column(Float, nullable=True)  # Normalized Difference Vegetation Index
    vegetation_coverage_percent = Column(Float, nullable=True)
    mangrove_area_km2 = Column(Float, nullable=True)
    
    # Water quality analysis
    chlorophyll_concentration = Column(Float, nullable=True)
    turbidity_estimate = Column(Float, nullable=True)
    algal_bloom_area_km2 = Column(Float, nullable=True)
    
    # Pollution detection
    oil_spill_detected = Column(Boolean, default=False)
    oil_spill_area_km2 = Column(Float, nullable=True)
    sediment_plume_detected = Column(Boolean, default=False)
    
    # Processing metadata
    processing_level = Column(String, default="L2")  # L1, L2, L3
    algorithm_version = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0-1
    
    # Quality flags
    flags = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_satellite_location_time', 'latitude', 'longitude', 'acquisition_date'),
        Index('idx_satellite_analysis_type', 'analysis_type', 'acquisition_date'),
    )
    
    def __repr__(self):
        return f"<SatelliteData(satellite={self.satellite_name}, analysis={self.analysis_type}, date={self.acquisition_date})>"