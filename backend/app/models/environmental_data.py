from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .monitoring import Base

class EnvironmentalData(Base):
    """Model for storing environmental sensor data from monitoring stations"""
    __tablename__ = "environmental_data"
    
    id = Column(String, primary_key=True, index=True)
    station_id = Column(String, ForeignKey('monitoring_stations.id'), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    # Tide and water level data
    tide_level = Column(Float, nullable=True, comment="Tide level in meters")
    water_level = Column(Float, nullable=True, comment="Water level in meters")
    
    # Wave data
    wave_height = Column(Float, nullable=True, comment="Significant wave height in meters")
    wave_period = Column(Float, nullable=True, comment="Wave period in seconds")
    wave_direction = Column(Float, nullable=True, comment="Wave direction in degrees")
    
    # Wind data
    wind_speed = Column(Float, nullable=True, comment="Wind speed in km/h")
    wind_direction = Column(Float, nullable=True, comment="Wind direction in degrees")
    wind_gust = Column(Float, nullable=True, comment="Wind gust speed in km/h")
    
    # Temperature data
    air_temperature = Column(Float, nullable=True, comment="Air temperature in Celsius")
    water_temperature = Column(Float, nullable=True, comment="Water temperature in Celsius")
    feels_like_temperature = Column(Float, nullable=True, comment="Feels like temperature in Celsius")
    
    # Atmospheric data
    atmospheric_pressure = Column(Float, nullable=True, comment="Atmospheric pressure in hPa")
    humidity = Column(Float, nullable=True, comment="Relative humidity in percentage")
    visibility = Column(Float, nullable=True, comment="Visibility in kilometers")
    uv_index = Column(Float, nullable=True, comment="UV index")
    
    # Precipitation data
    precipitation = Column(Float, nullable=True, comment="Precipitation in mm")
    precipitation_probability = Column(Float, nullable=True, comment="Precipitation probability in percentage")
    
    # Ocean/Water quality data
    salinity = Column(Float, nullable=True, comment="Water salinity in PSU")
    ph_level = Column(Float, nullable=True, comment="Water pH level")
    dissolved_oxygen = Column(Float, nullable=True, comment="Dissolved oxygen in mg/L")
    turbidity = Column(Float, nullable=True, comment="Water turbidity in NTU")
    
    # Current data
    current_speed = Column(Float, nullable=True, comment="Current speed in m/s")
    current_direction = Column(Float, nullable=True, comment="Current direction in degrees")
    
    # Data quality and metadata
    data_quality = Column(String, nullable=True, default="good", comment="Data quality: good, fair, poor")
    sensor_status = Column(String, nullable=True, default="operational", comment="Sensor status")
    battery_level = Column(Float, nullable=True, comment="Battery level in percentage")
    signal_strength = Column(Float, nullable=True, comment="Signal strength in dBm")
    
    # Additional metadata
    data_source = Column(String, nullable=True, comment="Data source: sensor, satellite, model")
    processing_notes = Column(Text, nullable=True, comment="Data processing notes")
    is_validated = Column(Boolean, default=False, comment="Whether data has been validated")
    
    # Additional metadata fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    station = relationship("MonitoringStation", back_populates="environmental_data")
    
    __table_args__ = (
        Index('idx_environmental_data_timestamp', 'timestamp'),
        Index('idx_environmental_data_station_time', 'station_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<EnvironmentalData(station_id={self.station_id}, timestamp={self.timestamp})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'station_id': self.station_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'tide_level': self.tide_level,
            'water_level': self.water_level,
            'wave_height': self.wave_height,
            'wave_period': self.wave_period,
            'wave_direction': self.wave_direction,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'wind_gust': self.wind_gust,
            'air_temperature': self.air_temperature,
            'water_temperature': self.water_temperature,
            'feels_like_temperature': self.feels_like_temperature,
            'atmospheric_pressure': self.atmospheric_pressure,
            'humidity': self.humidity,
            'visibility': self.visibility,
            'uv_index': self.uv_index,
            'precipitation': self.precipitation,
            'precipitation_probability': self.precipitation_probability,
            'salinity': self.salinity,
            'ph_level': self.ph_level,
            'dissolved_oxygen': self.dissolved_oxygen,
            'turbidity': self.turbidity,
            'current_speed': self.current_speed,
            'current_direction': self.current_direction,
            'data_quality': self.data_quality,
            'sensor_status': self.sensor_status,
            'battery_level': self.battery_level,
            'signal_strength': self.signal_strength,
            'data_source': self.data_source,
            'processing_notes': self.processing_notes,
            'is_validated': self.is_validated
        }
    
    @classmethod
    def from_sensor_data(cls, station_id: str, sensor_data: dict):
        """Create EnvironmentalData from raw sensor data"""
        return cls(
            station_id=station_id,
            timestamp=datetime.utcnow(),
            tide_level=sensor_data.get('tide_level'),
            water_level=sensor_data.get('water_level'),
            wave_height=sensor_data.get('wave_height'),
            wave_period=sensor_data.get('wave_period'),
            wave_direction=sensor_data.get('wave_direction'),
            wind_speed=sensor_data.get('wind_speed'),
            wind_direction=sensor_data.get('wind_direction'),
            wind_gust=sensor_data.get('wind_gust'),
            air_temperature=sensor_data.get('air_temperature'),
            water_temperature=sensor_data.get('water_temperature'),
            feels_like_temperature=sensor_data.get('feels_like_temperature'),
            atmospheric_pressure=sensor_data.get('atmospheric_pressure'),
            humidity=sensor_data.get('humidity'),
            visibility=sensor_data.get('visibility'),
            uv_index=sensor_data.get('uv_index'),
            precipitation=sensor_data.get('precipitation'),
            precipitation_probability=sensor_data.get('precipitation_probability'),
            salinity=sensor_data.get('salinity'),
            ph_level=sensor_data.get('ph_level'),
            dissolved_oxygen=sensor_data.get('dissolved_oxygen'),
            turbidity=sensor_data.get('turbidity'),
            current_speed=sensor_data.get('current_speed'),
            current_direction=sensor_data.get('current_direction'),
            data_quality=sensor_data.get('data_quality', 'good'),
            sensor_status=sensor_data.get('sensor_status', 'operational'),
            battery_level=sensor_data.get('battery_level'),
            signal_strength=sensor_data.get('signal_strength'),
            data_source=sensor_data.get('data_source', 'sensor'),
            processing_notes=sensor_data.get('processing_notes'),
            is_validated=sensor_data.get('is_validated', False)
        )