from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.database import get_db
from app.models.alert import Alert, AlertNotification, AlertSubscription, AlertHistory, AlertMetrics
from app.models.user import User, UserPreferences, UserLocation
from app.models.monitoring import MonitoringStation, TideData, WeatherData
from app.services.notification_service import notification_service
from app.services.ml_service import ml_service
import asyncio
import json
import uuid
from geopy.distance import geodesic

class AlertService:
    """Service for managing alerts and notifications"""
    
    def __init__(self):
        self.alert_thresholds = {
            'flood': {
                'low': 0.2,
                'medium': 0.4,
                'high': 0.7,
                'critical': 0.9
            },
            'tide': {
                'low': 2.0,
                'medium': 2.5,
                'high': 3.0,
                'critical': 3.5
            },
            'wave': {
                'low': 2.0,
                'medium': 3.0,
                'high': 4.0,
                'critical': 5.0
            },
            'storm': {
                'low': 0.3,
                'medium': 0.6,
                'high': 0.8,
                'critical': 1.0
            }
        }
        self.active_monitoring = False
        self.monitoring_task = None
    
    async def create_alert(self, alert_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Create a new alert"""
        try:
            # Generate alert ID
            alert_id = str(uuid.uuid4())
            
            # Determine severity based on alert type and values
            severity = self._calculate_severity(
                alert_data.get('alert_type'),
                alert_data.get('values', {})
            )
            
            # Create alert record
            alert = Alert(
                id=alert_id,
                alert_type=alert_data.get('alert_type'),
                severity=severity,
                title=alert_data.get('title'),
                description=alert_data.get('description'),
                location_name=alert_data.get('location', {}).get('name'),
                latitude=alert_data.get('location', {}).get('latitude'),
                longitude=alert_data.get('location', {}).get('longitude'),
                affected_radius_km=alert_data.get('affected_radius_km', 10.0),
                source=alert_data.get('source', 'system'),
                source_id=alert_data.get('source_id'),
                metadata=json.dumps(alert_data.get('metadata', {})),
                expires_at=alert_data.get('expires_at'),
                created_at=datetime.utcnow(),
                is_active=True
            )
            
            db.add(alert)
            db.commit()
            
            # Find affected users
            affected_users = await self._find_affected_users(
                alert_data.get('location', {}),
                alert_data.get('affected_radius_km', 10.0),
                alert_data.get('alert_type'),
                severity,
                db
            )
            
            # Send notifications
            notification_results = await self._send_alert_notifications(
                alert, affected_users, db
            )
            
            # Update alert metrics
            await self._update_alert_metrics(alert_id, len(affected_users), db)
            
            return {
                "success": True,
                "alert_id": alert_id,
                "severity": severity,
                "affected_users": len(affected_users),
                "notifications_sent": notification_results.get('successful', 0),
                "created_at": alert.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_alerts(self, filters: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Get alerts with optional filters"""
        try:
            query = db.query(Alert)
            
            # Apply filters
            if filters.get('alert_type'):
                query = query.filter(Alert.alert_type == filters['alert_type'])
            
            if filters.get('severity'):
                query = query.filter(Alert.severity == filters['severity'])
            
            if filters.get('is_active') is not None:
                query = query.filter(Alert.is_active == filters['is_active'])
            
            if filters.get('location'):
                # Filter by location radius
                lat = filters['location'].get('latitude')
                lon = filters['location'].get('longitude')
                radius = filters['location'].get('radius_km', 50)
                
                if lat and lon:
                    # Simple bounding box filter (more complex spatial queries would need PostGIS)
                    lat_delta = radius / 111.0  # Approximate km to degrees
                    lon_delta = radius / (111.0 * abs(lat) if lat != 0 else 111.0)
                    
                    query = query.filter(
                        and_(
                            Alert.latitude.between(lat - lat_delta, lat + lat_delta),
                            Alert.longitude.between(lon - lon_delta, lon + lon_delta)
                        )
                    )
            
            if filters.get('start_date'):
                query = query.filter(Alert.created_at >= filters['start_date'])
            
            if filters.get('end_date'):
                query = query.filter(Alert.created_at <= filters['end_date'])
            
            # Order by creation date (newest first)
            query = query.order_by(desc(Alert.created_at))
            
            # Limit results
            limit = filters.get('limit', 50)
            alerts = query.limit(limit).all()
            
            # Convert to response format
            alert_list = []
            for alert in alerts:
                alert_dict = {
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "title": alert.title,
                    "description": alert.description,
                    "location": {
                        "name": alert.location_name,
                        "latitude": alert.latitude,
                        "longitude": alert.longitude
                    },
                    "affected_radius_km": alert.affected_radius_km,
                    "source": alert.source,
                    "created_at": alert.created_at.isoformat(),
                    "expires_at": alert.expires_at.isoformat() if alert.expires_at else None,
                    "is_active": alert.is_active,
                    "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
                }
                
                # Add metadata if present
                if alert.metadata:
                    try:
                        alert_dict["metadata"] = json.loads(alert.metadata)
                    except:
                        pass
                
                alert_list.append(alert_dict)
            
            return alert_list
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
    
    async def get_alert_by_id(self, alert_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get specific alert by ID"""
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            
            if not alert:
                return None
            
            # Get notification history
            notifications = db.query(AlertNotification).filter(
                AlertNotification.alert_id == alert_id
            ).all()
            
            notification_summary = {
                "total_sent": len(notifications),
                "successful": len([n for n in notifications if n.status == 'sent']),
                "failed": len([n for n in notifications if n.status == 'failed']),
                "methods_used": list(set([n.delivery_method for n in notifications]))
            }
            
            return {
                "id": alert.id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "description": alert.description,
                "location": {
                    "name": alert.location_name,
                    "latitude": alert.latitude,
                    "longitude": alert.longitude
                },
                "affected_radius_km": alert.affected_radius_km,
                "source": alert.source,
                "created_at": alert.created_at.isoformat(),
                "expires_at": alert.expires_at.isoformat() if alert.expires_at else None,
                "is_active": alert.is_active,
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "metadata": json.loads(alert.metadata) if alert.metadata else {},
                "notifications": notification_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting alert {alert_id}: {e}")
            return None
    
    async def acknowledge_alert(self, alert_id: str, user_id: str, db: Session) -> Dict[str, Any]:
        """Acknowledge an alert"""
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            
            if not alert:
                return {
                    "success": False,
                    "error": "Alert not found"
                }
            
            if alert.acknowledged_at:
                return {
                    "success": False,
                    "error": "Alert already acknowledged"
                }
            
            # Update alert
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = user_id
            
            # Create acknowledgment record
            acknowledgment = AlertHistory(
                alert_id=alert_id,
                user_id=user_id,
                action='acknowledged',
                timestamp=datetime.utcnow(),
                details=json.dumps({"acknowledged_by": user_id})
            )
            
            db.add(acknowledgment)
            db.commit()
            
            return {
                "success": True,
                "alert_id": alert_id,
                "acknowledged_at": alert.acknowledged_at.isoformat(),
                "acknowledged_by": user_id
            }
            
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    async def resolve_alert(self, alert_id: str, user_id: str, 
                          resolution_notes: str = None, db: Session = None) -> Dict[str, Any]:
        """Resolve an alert"""
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            
            if not alert:
                return {
                    "success": False,
                    "error": "Alert not found"
                }
            
            if alert.resolved_at:
                return {
                    "success": False,
                    "error": "Alert already resolved"
                }
            
            # Update alert
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = user_id
            alert.is_active = False
            alert.resolution_notes = resolution_notes
            
            # Create resolution record
            resolution = AlertHistory(
                alert_id=alert_id,
                user_id=user_id,
                action='resolved',
                timestamp=datetime.utcnow(),
                details=json.dumps({
                    "resolved_by": user_id,
                    "notes": resolution_notes
                })
            )
            
            db.add(resolution)
            db.commit()
            
            return {
                "success": True,
                "alert_id": alert_id,
                "resolved_at": alert.resolved_at.isoformat(),
                "resolved_by": user_id,
                "resolution_notes": resolution_notes
            }
            
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {e}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_alert_history(self, location: Dict[str, float], 
                              days: int = 30, db: Session = None) -> List[Dict[str, Any]]:
        """Get alert history for a location"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get alerts within radius of location
            lat = location.get('latitude')
            lon = location.get('longitude')
            radius = location.get('radius_km', 50)
            
            if not (lat and lon):
                return []
            
            # Simple bounding box filter
            lat_delta = radius / 111.0
            lon_delta = radius / (111.0 * abs(lat) if lat != 0 else 111.0)
            
            alerts = db.query(Alert).filter(
                and_(
                    Alert.latitude.between(lat - lat_delta, lat + lat_delta),
                    Alert.longitude.between(lon - lon_delta, lon + lon_delta),
                    Alert.created_at >= start_date
                )
            ).order_by(desc(Alert.created_at)).all()
            
            # Group by date and type
            history = []
            for alert in alerts:
                # Calculate actual distance
                if alert.latitude and alert.longitude:
                    distance = geodesic(
                        (lat, lon),
                        (alert.latitude, alert.longitude)
                    ).kilometers
                    
                    if distance <= radius:
                        history.append({
                            "id": alert.id,
                            "alert_type": alert.alert_type,
                            "severity": alert.severity,
                            "title": alert.title,
                            "location_name": alert.location_name,
                            "distance_km": round(distance, 2),
                            "created_at": alert.created_at.isoformat(),
                            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                            "duration_hours": (
                                (alert.resolved_at - alert.created_at).total_seconds() / 3600
                                if alert.resolved_at else None
                            )
                        })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting alert history: {e}")
            return []
    
    async def start_real_time_monitoring(self, db: Session) -> Dict[str, Any]:
        """Start real-time environmental monitoring for automatic alerts"""
        try:
            if self.active_monitoring:
                return {
                    "success": False,
                    "error": "Monitoring already active"
                }
            
            self.active_monitoring = True
            self.monitoring_task = asyncio.create_task(self._monitor_environmental_conditions(db))
            
            logger.info("Started real-time environmental monitoring")
            return {
                "success": True,
                "message": "Real-time monitoring started",
                "started_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def stop_real_time_monitoring(self) -> Dict[str, Any]:
        """Stop real-time environmental monitoring"""
        try:
            if not self.active_monitoring:
                return {
                    "success": False,
                    "error": "Monitoring not active"
                }
            
            self.active_monitoring = False
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Stopped real-time environmental monitoring")
            return {
                "success": True,
                "message": "Real-time monitoring stopped",
                "stopped_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _monitor_environmental_conditions(self, db: Session):
        """Continuously monitor environmental conditions and trigger alerts"""
        logger.info("Environmental monitoring loop started")
        
        while self.active_monitoring:
            try:
                # Get all active monitoring stations
                stations = db.query(MonitoringStation).filter(
                    MonitoringStation.is_active == True
                ).all()
                
                for station in stations:
                    # Get latest data for each station
                    latest_data = await self._get_latest_station_data(station.id, db)
                    
                    if latest_data:
                        # Process data and check for alert conditions
                        await self._check_alert_conditions(station, latest_data, db)
                
                # Check for system-wide conditions
                await self._check_system_wide_conditions(db)
                
                # Wait 5 minutes before next check
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                logger.info("Monitoring cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _get_latest_station_data(self, station_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get latest data from a monitoring station"""
        try:
            # Get latest tide data
            latest_tide = db.query(TideData).filter(
                TideData.station_id == station_id
            ).order_by(desc(TideData.timestamp)).first()
            
            # Get latest weather data
            latest_weather = db.query(WeatherData).filter(
                WeatherData.station_id == station_id
            ).order_by(desc(WeatherData.timestamp)).first()
            
            if not latest_tide and not latest_weather:
                return None
            
            data = {
                "station_id": station_id,
                "timestamp": datetime.utcnow()
            }
            
            if latest_tide:
                data.update({
                    "tide_level": latest_tide.water_level,
                    "tide_timestamp": latest_tide.timestamp
                })
            
            if latest_weather:
                data.update({
                    "wave_height": latest_weather.wave_height,
                    "wind_speed_kmh": latest_weather.wind_speed,
                    "atmospheric_pressure": latest_weather.atmospheric_pressure,
                    "weather_timestamp": latest_weather.timestamp
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting station data for {station_id}: {e}")
            return None
    
    async def _check_alert_conditions(self, station: MonitoringStation, data: Dict[str, Any], db: Session):
        """Check if current conditions warrant an alert"""
        try:
            alerts_created = []
            
            # Check if we've already sent a similar alert recently
            recent_cutoff = datetime.utcnow() - timedelta(hours=2)
            
            # Check for flood risk
            if data.get('tide_level') or data.get('wave_height'):
                flood_risk = await ml_service.flood_model.predict_flood_risk(data)
                
                if flood_risk.get('flood_probability', 0) > 0.3:
                    # Check if similar flood alert exists recently
                    existing_alert = db.query(Alert).filter(
                        and_(
                            Alert.alert_type == 'flood',
                            Alert.source_id == station.id,
                            Alert.created_at >= recent_cutoff,
                            Alert.is_active == True
                        )
                    ).first()
                    
                    if not existing_alert:
                        station_data = {
                            "station_name": station.name,
                            "latitude": station.latitude,
                            "longitude": station.longitude,
                            **data
                        }
                        flood_alert = await self._create_flood_alert(station_data, flood_risk, db)
                        if flood_alert.get('success'):
                            alerts_created.append(flood_alert['alert_id'])
            
            # Check for high tide alerts
            if data.get('tide_level', 0) > self.alert_thresholds['tide']['medium']:
                existing_alert = db.query(Alert).filter(
                    and_(
                        Alert.alert_type == 'tide',
                        Alert.source_id == station.id,
                        Alert.created_at >= recent_cutoff,
                        Alert.is_active == True
                    )
                ).first()
                
                if not existing_alert:
                    station_data = {
                        "station_name": station.name,
                        "latitude": station.latitude,
                        "longitude": station.longitude,
                        **data
                    }
                    tide_alert = await self._create_tide_alert(station_data, db)
                    if tide_alert.get('success'):
                        alerts_created.append(tide_alert['alert_id'])
            
            # Check for high wave alerts
            if data.get('wave_height', 0) > self.alert_thresholds['wave']['medium']:
                existing_alert = db.query(Alert).filter(
                    and_(
                        Alert.alert_type == 'wave',
                        Alert.source_id == station.id,
                        Alert.created_at >= recent_cutoff,
                        Alert.is_active == True
                    )
                ).first()
                
                if not existing_alert:
                    station_data = {
                        "station_name": station.name,
                        "latitude": station.latitude,
                        "longitude": station.longitude,
                        **data
                    }
                    wave_alert = await self._create_wave_alert(station_data, db)
                    if wave_alert.get('success'):
                        alerts_created.append(wave_alert['alert_id'])
            
            # Check for storm conditions
            if (data.get('wind_speed_kmh', 0) > 60 or 
                data.get('atmospheric_pressure', 1013) < 990):
                existing_alert = db.query(Alert).filter(
                    and_(
                        Alert.alert_type == 'storm',
                        Alert.source_id == station.id,
                        Alert.created_at >= recent_cutoff,
                        Alert.is_active == True
                    )
                ).first()
                
                if not existing_alert:
                    station_data = {
                        "station_name": station.name,
                        "latitude": station.latitude,
                        "longitude": station.longitude,
                        **data
                    }
                    storm_alert = await self._create_storm_alert(station_data, db)
                    if storm_alert.get('success'):
                        alerts_created.append(storm_alert['alert_id'])
            
            if alerts_created:
                logger.info(f"Created {len(alerts_created)} alerts for station {station.name}")
            
        except Exception as e:
            logger.error(f"Error checking alert conditions for station {station.id}: {e}")
    
    async def _check_system_wide_conditions(self, db: Session):
        """Check for system-wide conditions that might warrant alerts"""
        try:
            # Check for multiple station failures
            total_stations = db.query(MonitoringStation).filter(
                MonitoringStation.is_active == True
            ).count()
            
            # Check stations with recent data (last 30 minutes)
            recent_cutoff = datetime.utcnow() - timedelta(minutes=30)
            
            stations_with_recent_data = db.query(MonitoringStation.id).join(
                TideData, MonitoringStation.id == TideData.station_id
            ).filter(
                and_(
                    MonitoringStation.is_active == True,
                    TideData.timestamp >= recent_cutoff
                )
            ).distinct().count()
            
            # If less than 50% of stations are reporting, create system alert
            if total_stations > 0 and (stations_with_recent_data / total_stations) < 0.5:
                # Check if system alert already exists
                existing_alert = db.query(Alert).filter(
                    and_(
                        Alert.alert_type == 'system',
                        Alert.created_at >= datetime.utcnow() - timedelta(hours=1),
                        Alert.is_active == True
                    )
                ).first()
                
                if not existing_alert:
                    system_alert_data = {
                        "alert_type": "system",
                        "title": "System Monitoring Alert",
                        "description": f"Multiple monitoring stations offline. Only {stations_with_recent_data}/{total_stations} stations reporting.",
                        "location": {
                            "name": "System Wide",
                            "latitude": 25.7617,  # Florida center
                            "longitude": -80.1918
                        },
                        "affected_radius_km": 500.0,
                        "source": "monitoring_system",
                        "metadata": {
                            "total_stations": total_stations,
                            "active_stations": stations_with_recent_data,
                            "system_health": (stations_with_recent_data / total_stations) * 100
                        },
                        "expires_at": datetime.utcnow() + timedelta(hours=4)
                    }
                    
                    await self.create_alert(system_alert_data, db)
                    logger.warning(f"System alert created: {stations_with_recent_data}/{total_stations} stations reporting")
            
        except Exception as e:
            logger.error(f"Error checking system-wide conditions: {e}")
    
    async def process_monitoring_data(self, station_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Process monitoring data and generate alerts if needed"""
        try:
            alerts_created = []
            
            # Check for flood risk
            if station_data.get('tide_level') or station_data.get('wave_height'):
                flood_risk = await ml_service.flood_model.predict_flood_risk(station_data)
                
                if flood_risk.get('flood_probability', 0) > 0.3:
                    flood_alert = await self._create_flood_alert(station_data, flood_risk, db)
                    if flood_alert.get('success'):
                        alerts_created.append(flood_alert['alert_id'])
            
            # Check for high tide alerts
            if station_data.get('tide_level', 0) > self.alert_thresholds['tide']['medium']:
                tide_alert = await self._create_tide_alert(station_data, db)
                if tide_alert.get('success'):
                    alerts_created.append(tide_alert['alert_id'])
            
            # Check for high wave alerts
            if station_data.get('wave_height', 0) > self.alert_thresholds['wave']['medium']:
                wave_alert = await self._create_wave_alert(station_data, db)
                if wave_alert.get('success'):
                    alerts_created.append(wave_alert['alert_id'])
            
            # Check for storm conditions
            if (station_data.get('wind_speed_kmh', 0) > 60 or 
                station_data.get('atmospheric_pressure', 1013) < 990):
                storm_alert = await self._create_storm_alert(station_data, db)
                if storm_alert.get('success'):
                    alerts_created.append(storm_alert['alert_id'])
            
            return {
                "success": True,
                "alerts_created": len(alerts_created),
                "alert_ids": alerts_created,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing monitoring data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_severity(self, alert_type: str, values: Dict[str, Any]) -> str:
        """Calculate alert severity based on type and values"""
        if alert_type not in self.alert_thresholds:
            return 'medium'
        
        thresholds = self.alert_thresholds[alert_type]
        
        # Get the relevant value based on alert type
        if alert_type == 'flood':
            value = values.get('flood_probability', 0)
        elif alert_type == 'tide':
            value = values.get('tide_level', 0)
        elif alert_type == 'wave':
            value = values.get('wave_height', 0)
        elif alert_type == 'storm':
            value = values.get('storm_intensity', 0)
        else:
            return 'medium'
        
        # Determine severity
        if value >= thresholds['critical']:
            return 'critical'
        elif value >= thresholds['high']:
            return 'high'
        elif value >= thresholds['medium']:
            return 'medium'
        else:
            return 'low'
    
    async def _find_affected_users(self, location: Dict[str, float], 
                                 radius_km: float, alert_type: str, 
                                 severity: str, db: Session) -> List[str]:
        """Find users affected by an alert"""
        try:
            lat = location.get('latitude')
            lon = location.get('longitude')
            
            if not (lat and lon):
                return []
            
            # Simple bounding box to find nearby users
            lat_delta = radius_km / 111.0
            lon_delta = radius_km / (111.0 * abs(lat) if lat != 0 else 111.0)
            
            # Get users with locations and preferences
            users_query = db.query(User.id).join(UserLocation).join(UserPreferences).filter(
                and_(
                    UserLocation.latitude.between(lat - lat_delta, lat + lat_delta),
                    UserLocation.longitude.between(lon - lon_delta, lon + lon_delta),
                    User.is_active == True
                )
            )
            
            # Filter by alert type preferences
            if alert_type:
                users_query = users_query.filter(
                    UserPreferences.alert_types.contains([alert_type])
                )
            
            # Filter by severity threshold
            severity_levels = ['low', 'medium', 'high', 'critical']
            if severity in severity_levels:
                min_severity_index = severity_levels.index(severity)
                user_severity_filters = []
                
                for i in range(min_severity_index + 1):
                    user_severity_filters.append(
                        UserPreferences.severity_threshold == severity_levels[i]
                    )
                
                if user_severity_filters:
                    users_query = users_query.filter(or_(*user_severity_filters))
            
            user_ids = [user.id for user in users_query.all()]
            
            # Filter by actual distance
            filtered_users = []
            for user_id in user_ids:
                user_location = db.query(UserLocation).filter(
                    UserLocation.user_id == user_id
                ).first()
                
                if user_location and user_location.latitude and user_location.longitude:
                    distance = geodesic(
                        (lat, lon),
                        (user_location.latitude, user_location.longitude)
                    ).kilometers
                    
                    if distance <= radius_km:
                        filtered_users.append(user_id)
            
            return filtered_users
            
        except Exception as e:
            logger.error(f"Error finding affected users: {e}")
            return []
    
    async def _send_alert_notifications(self, alert: Alert, 
                                      user_ids: List[str], db: Session) -> Dict[str, Any]:
        """Send notifications for an alert"""
        if not user_ids:
            return {"successful": 0, "failed": 0}
        
        alert_data = {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "description": alert.description,
            "location": {
                "name": alert.location_name,
                "latitude": alert.latitude,
                "longitude": alert.longitude
            },
            "created_at": alert.created_at.isoformat()
        }
        
        # Send notifications in batches
        batch_size = 10
        successful = 0
        failed = 0
        
        for i in range(0, len(user_ids), batch_size):
            batch = user_ids[i:i + batch_size]
            
            try:
                result = await notification_service.send_bulk_alert(alert_data, batch, db)
                successful += result.get('successful', 0)
                failed += result.get('failed', 0)
            except Exception as e:
                logger.error(f"Error sending notification batch: {e}")
                failed += len(batch)
        
        return {"successful": successful, "failed": failed}
    
    async def _update_alert_metrics(self, alert_id: str, affected_users: int, db: Session):
        """Update alert metrics"""
        try:
            metrics = AlertMetrics(
                alert_id=alert_id,
                users_notified=affected_users,
                notification_success_rate=1.0,  # Will be updated after notifications
                response_time_seconds=0,
                created_at=datetime.utcnow()
            )
            
            db.add(metrics)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error updating alert metrics: {e}")
    
    async def _create_flood_alert(self, station_data: Dict[str, Any], 
                                flood_risk: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Create flood alert"""
        alert_data = {
            "alert_type": "flood",
            "title": f"Flood Risk Alert - {flood_risk.get('risk_level', 'Unknown').title()}",
            "description": f"Flood probability: {flood_risk.get('flood_probability', 0):.1%}. "
                          f"Expected conditions may lead to coastal flooding.",
            "location": {
                "name": station_data.get('station_name', 'Monitoring Station'),
                "latitude": station_data.get('latitude'),
                "longitude": station_data.get('longitude')
            },
            "affected_radius_km": 15.0,
            "values": {"flood_probability": flood_risk.get('flood_probability', 0)},
            "metadata": {
                "flood_risk": flood_risk,
                "station_data": station_data
            },
            "expires_at": datetime.utcnow() + timedelta(hours=12)
        }
        
        return await self.create_alert(alert_data, db)
    
    async def _create_tide_alert(self, station_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Create high tide alert"""
        tide_level = station_data.get('tide_level', 0)
        
        alert_data = {
            "alert_type": "tide",
            "title": "High Tide Alert",
            "description": f"High tide level detected: {tide_level:.2f}m. "
                          f"Coastal areas may experience elevated water levels.",
            "location": {
                "name": station_data.get('station_name', 'Monitoring Station'),
                "latitude": station_data.get('latitude'),
                "longitude": station_data.get('longitude')
            },
            "affected_radius_km": 10.0,
            "values": {"tide_level": tide_level},
            "metadata": {"station_data": station_data},
            "expires_at": datetime.utcnow() + timedelta(hours=6)
        }
        
        return await self.create_alert(alert_data, db)
    
    async def _create_wave_alert(self, station_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Create high wave alert"""
        wave_height = station_data.get('wave_height', 0)
        
        alert_data = {
            "alert_type": "wave",
            "title": "High Wave Alert",
            "description": f"High waves detected: {wave_height:.2f}m. "
                          f"Dangerous conditions for coastal activities.",
            "location": {
                "name": station_data.get('station_name', 'Monitoring Station'),
                "latitude": station_data.get('latitude'),
                "longitude": station_data.get('longitude')
            },
            "affected_radius_km": 8.0,
            "values": {"wave_height": wave_height},
            "metadata": {"station_data": station_data},
            "expires_at": datetime.utcnow() + timedelta(hours=8)
        }
        
        return await self.create_alert(alert_data, db)
    
    async def _create_storm_alert(self, station_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Create storm alert"""
        wind_speed = station_data.get('wind_speed_kmh', 0)
        pressure = station_data.get('atmospheric_pressure', 1013)
        
        alert_data = {
            "alert_type": "storm",
            "title": "Storm Conditions Alert",
            "description": f"Severe weather detected. Wind: {wind_speed:.1f} km/h, "
                          f"Pressure: {pressure:.1f} hPa. Take precautions.",
            "location": {
                "name": station_data.get('station_name', 'Monitoring Station'),
                "latitude": station_data.get('latitude'),
                "longitude": station_data.get('longitude')
            },
            "affected_radius_km": 25.0,
            "values": {
                "wind_speed": wind_speed,
                "pressure": pressure,
                "storm_intensity": min(wind_speed / 100.0, 1.0)
            },
            "metadata": {"station_data": station_data},
            "expires_at": datetime.utcnow() + timedelta(hours=24)
        }
        
        return await self.create_alert(alert_data, db)
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "active_monitoring": self.active_monitoring,
            "monitoring_task_running": self.monitoring_task is not None and not self.monitoring_task.done() if self.monitoring_task else False,
            "status_checked_at": datetime.utcnow().isoformat()
        }
    
    async def trigger_manual_check(self, db: Session) -> Dict[str, Any]:
        """Manually trigger a check of all monitoring stations"""
        try:
            logger.info("Manual monitoring check triggered")
            
            # Get all active monitoring stations
            stations = db.query(MonitoringStation).filter(
                MonitoringStation.is_active == True
            ).all()
            
            alerts_created = []
            
            for station in stations:
                # Get latest data for each station
                latest_data = await self._get_latest_station_data(station.id, db)
                
                if latest_data:
                    # Process data and check for alert conditions
                    station_alerts = await self._check_alert_conditions_manual(station, latest_data, db)
                    alerts_created.extend(station_alerts)
            
            # Check system-wide conditions
            await self._check_system_wide_conditions(db)
            
            return {
                "success": True,
                "stations_checked": len(stations),
                "alerts_created": len(alerts_created),
                "alert_ids": alerts_created,
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in manual monitoring check: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_alert_conditions_manual(self, station: MonitoringStation, data: Dict[str, Any], db: Session) -> List[str]:
        """Check alert conditions for manual trigger (ignores recent alert check)"""
        try:
            alerts_created = []
            
            # Check for flood risk
            if data.get('tide_level') or data.get('wave_height'):
                flood_risk = await ml_service.flood_model.predict_flood_risk(data)
                
                if flood_risk.get('flood_probability', 0) > 0.3:
                    station_data = {
                        "station_name": station.name,
                        "latitude": station.latitude,
                        "longitude": station.longitude,
                        **data
                    }
                    flood_alert = await self._create_flood_alert(station_data, flood_risk, db)
                    if flood_alert.get('success'):
                        alerts_created.append(flood_alert['alert_id'])
            
            # Check for high tide alerts
            if data.get('tide_level', 0) > self.alert_thresholds['tide']['medium']:
                station_data = {
                    "station_name": station.name,
                    "latitude": station.latitude,
                    "longitude": station.longitude,
                    **data
                }
                tide_alert = await self._create_tide_alert(station_data, db)
                if tide_alert.get('success'):
                    alerts_created.append(tide_alert['alert_id'])
            
            # Check for high wave alerts
            if data.get('wave_height', 0) > self.alert_thresholds['wave']['medium']:
                station_data = {
                    "station_name": station.name,
                    "latitude": station.latitude,
                    "longitude": station.longitude,
                    **data
                }
                wave_alert = await self._create_wave_alert(station_data, db)
                if wave_alert.get('success'):
                    alerts_created.append(wave_alert['alert_id'])
            
            # Check for storm conditions
            if (data.get('wind_speed_kmh', 0) > 60 or 
                data.get('atmospheric_pressure', 1013) < 990):
                station_data = {
                    "station_name": station.name,
                    "latitude": station.latitude,
                    "longitude": station.longitude,
                    **data
                }
                storm_alert = await self._create_storm_alert(station_data, db)
                if storm_alert.get('success'):
                    alerts_created.append(storm_alert['alert_id'])
            
            return alerts_created
            
        except Exception as e:
            logger.error(f"Error checking alert conditions for station {station.id}: {e}")
            return []

# Global alert service instance
alert_service = AlertService()