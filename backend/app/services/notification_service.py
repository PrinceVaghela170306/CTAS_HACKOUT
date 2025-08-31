import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from loguru import logger
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException
import firebase_admin
from firebase_admin import credentials, messaging
from app.config import settings
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.alert import Alert, AlertNotification
from app.models.user import User, UserPreferences

class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email
    
    async def send_email(self, to_email: str, subject: str, 
                        html_content: str, text_content: str = None) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def generate_alert_email(self, alert_data: Dict[str, Any], 
                           user_name: str = "User") -> tuple[str, str]:
        """Generate HTML and text content for alert email"""
        alert_type = alert_data.get('alert_type', 'General Alert')
        severity = alert_data.get('severity', 'medium')
        location = alert_data.get('location', {}).get('name', 'Your area')
        description = alert_data.get('description', 'No description available')
        
        # Severity color mapping
        severity_colors = {
            'low': '#28a745',
            'medium': '#ffc107', 
            'high': '#fd7e14',
            'critical': '#dc3545'
        }
        
        color = severity_colors.get(severity, '#6c757d')
        
        # HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Coastal Alert - {alert_type}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">🌊 Coastal Alert System</h1>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; border-left: 4px solid {color};">
                    <h2 style="color: {color}; margin-top: 0;">{alert_type}</h2>
                    <p><strong>Severity:</strong> <span style="color: {color}; text-transform: uppercase; font-weight: bold;">{severity}</span></p>
                    <p><strong>Location:</strong> {location}</p>
                    <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
                </div>
                
                <div style="background: white; padding: 20px; border: 1px solid #dee2e6;">
                    <h3>Alert Details</h3>
                    <p>{description}</p>
                    
                    <div style="background: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h4 style="margin-top: 0;">Recommended Actions:</h4>
                        <ul>
                            <li>Stay informed about current conditions</li>
                            <li>Avoid coastal areas if conditions are severe</li>
                            <li>Follow local emergency management guidance</li>
                            <li>Keep emergency supplies ready</li>
                        </ul>
                    </div>
                </div>
                
                <div style="background: #6c757d; color: white; padding: 15px; border-radius: 0 0 8px 8px; text-align: center;">
                    <p style="margin: 0; font-size: 14px;">This is an automated alert from the Coastal Monitoring System</p>
                    <p style="margin: 5px 0 0 0; font-size: 12px;">To manage your alert preferences, log in to your dashboard</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text content
        text_content = f"""
        COASTAL ALERT SYSTEM
        
        Alert Type: {alert_type}
        Severity: {severity.upper()}
        Location: {location}
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
        
        ALERT DETAILS:
        {description}
        
        RECOMMENDED ACTIONS:
        - Stay informed about current conditions
        - Avoid coastal areas if conditions are severe
        - Follow local emergency management guidance
        - Keep emergency supplies ready
        
        This is an automated alert from the Coastal Monitoring System.
        To manage your alert preferences, log in to your dashboard.
        """
        
        return html_content, text_content

class SMSService:
    """Service for sending SMS notifications via Twilio"""
    
    def __init__(self):
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.from_number = settings.twilio_phone_number
        self.client = None
        
        if self.account_sid and self.auth_token:
            try:
                self.client = TwilioClient(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
    
    async def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS notification"""
        if not self.client:
            logger.warning("Twilio client not initialized, simulating SMS send")
            logger.info(f"SMS to {to_number}: {message}")
            return True
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully to {to_number}, SID: {message.sid}")
            return True
            
        except TwilioException as e:
            logger.error(f"Twilio error sending SMS to {to_number}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {e}")
            return False
    
    def generate_alert_sms(self, alert_data: Dict[str, Any]) -> str:
        """Generate SMS content for alert"""
        alert_type = alert_data.get('alert_type', 'Alert')
        severity = alert_data.get('severity', 'medium')
        location = alert_data.get('location', {}).get('name', 'your area')
        
        # Keep SMS short due to character limits
        message = f"🌊 COASTAL ALERT: {alert_type} ({severity.upper()}) in {location}. "
        
        if severity in ['high', 'critical']:
            message += "Take immediate precautions. "
        
        message += "Check app for details."
        
        return message[:160]  # SMS character limit

class PushNotificationService:
    """Service for sending push notifications via Firebase"""
    
    def __init__(self):
        self.app = None
        
        if settings.firebase_credentials_path:
            try:
                cred = credentials.Certificate(settings.firebase_credentials_path)
                self.app = firebase_admin.initialize_app(cred)
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}")
    
    async def send_push_notification(self, device_token: str, title: str, 
                                   body: str, data: Dict[str, str] = None) -> bool:
        """Send push notification"""
        if not self.app:
            logger.warning("Firebase not initialized, simulating push notification")
            logger.info(f"Push to {device_token[:20]}...: {title} - {body}")
            return True
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=device_token
            )
            
            response = messaging.send(message)
            logger.info(f"Push notification sent successfully: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False
    
    async def send_topic_notification(self, topic: str, title: str, 
                                    body: str, data: Dict[str, str] = None) -> bool:
        """Send notification to a topic (multiple users)"""
        if not self.app:
            logger.warning("Firebase not initialized, simulating topic notification")
            logger.info(f"Topic {topic}: {title} - {body}")
            return True
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                topic=topic
            )
            
            response = messaging.send(message)
            logger.info(f"Topic notification sent successfully: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send topic notification: {e}")
            return False

class NotificationService:
    """Main notification service that coordinates all notification methods"""
    
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushNotificationService()
    
    async def send_alert_notification(self, alert_data: Dict[str, Any], 
                                    user_id: str, db: Session) -> Dict[str, Any]:
        """Send alert notification to a specific user"""
        try:
            # Get user and preferences
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            preferences = db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            
            if not preferences:
                return {"success": False, "error": "User preferences not found"}
            
            results = {}
            notification_methods = preferences.notification_methods or ['email']
            
            # Send email notification
            if 'email' in notification_methods and user.email:
                html_content, text_content = self.email_service.generate_alert_email(
                    alert_data, user.full_name or user.email
                )
                
                subject = f"Coastal Alert: {alert_data.get('alert_type', 'Alert')}"
                email_success = await self.email_service.send_email(
                    user.email, subject, html_content, text_content
                )
                results['email'] = email_success
            
            # Send SMS notification
            if 'sms' in notification_methods and preferences.phone_number:
                sms_content = self.sms_service.generate_alert_sms(alert_data)
                sms_success = await self.sms_service.send_sms(
                    preferences.phone_number, sms_content
                )
                results['sms'] = sms_success
            
            # Send push notification
            if 'push' in notification_methods and user.device_token:
                title = f"🌊 {alert_data.get('alert_type', 'Coastal Alert')}"
                body = alert_data.get('description', 'Check the app for details')[:100]
                
                push_data = {
                    'alert_id': str(alert_data.get('id', '')),
                    'severity': alert_data.get('severity', 'medium'),
                    'type': 'alert'
                }
                
                push_success = await self.push_service.send_push_notification(
                    user.device_token, title, body, push_data
                )
                results['push'] = push_success
            
            # Log notification attempt
            notification = AlertNotification(
                alert_id=alert_data.get('id'),
                user_id=user_id,
                notification_type='multi',
                delivery_method=','.join(notification_methods),
                status='sent' if any(results.values()) else 'failed',
                sent_at=datetime.utcnow(),
                delivery_details=json.dumps(results)
            )
            
            db.add(notification)
            db.commit()
            
            return {
                "success": True,
                "user_id": user_id,
                "methods_attempted": list(results.keys()),
                "results": results,
                "notification_id": notification.id
            }
            
        except Exception as e:
            logger.error(f"Error sending alert notification to user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_bulk_alert(self, alert_data: Dict[str, Any], 
                            user_ids: List[str], db: Session) -> Dict[str, Any]:
        """Send alert to multiple users"""
        results = []
        
        # Send notifications concurrently
        tasks = [
            self.send_alert_notification(alert_data, user_id, db)
            for user_id in user_ids
        ]
        
        notification_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = 0
        failed = 0
        
        for i, result in enumerate(notification_results):
            if isinstance(result, Exception):
                results.append({
                    "user_id": user_ids[i],
                    "success": False,
                    "error": str(result)
                })
                failed += 1
            else:
                results.append(result)
                if result.get('success'):
                    successful += 1
                else:
                    failed += 1
        
        return {
            "total_users": len(user_ids),
            "successful": successful,
            "failed": failed,
            "results": results,
            "sent_at": datetime.utcnow().isoformat()
        }
    
    async def send_area_alert(self, alert_data: Dict[str, Any], 
                            location_bounds: Dict[str, float], 
                            db: Session) -> Dict[str, Any]:
        """Send alert to all users in a specific geographical area"""
        try:
            # Get users within the specified bounds
            # This would typically involve a spatial query
            # For now, we'll simulate getting users in the area
            
            # Simulate finding users in area
            area_users = db.query(User).join(UserPreferences).filter(
                UserPreferences.latitude.between(
                    location_bounds.get('min_lat', 0),
                    location_bounds.get('max_lat', 90)
                ),
                UserPreferences.longitude.between(
                    location_bounds.get('min_lon', -180),
                    location_bounds.get('max_lon', 180)
                )
            ).all()
            
            user_ids = [user.id for user in area_users]
            
            if not user_ids:
                return {
                    "success": True,
                    "message": "No users found in the specified area",
                    "total_users": 0
                }
            
            # Send bulk alert
            result = await self.send_bulk_alert(alert_data, user_ids, db)
            
            # Also send as topic notification for immediate delivery
            topic = f"area_{location_bounds.get('area_code', 'general')}"
            title = f"🌊 {alert_data.get('alert_type', 'Area Alert')}"
            body = alert_data.get('description', 'Check the app for details')[:100]
            
            await self.push_service.send_topic_notification(topic, title, body)
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending area alert: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_test_notification(self, user_id: str, 
                                   notification_type: str, db: Session) -> Dict[str, Any]:
        """Send test notification to verify delivery methods"""
        test_alert = {
            "id": "test-" + datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            "alert_type": "Test Notification",
            "severity": "low",
            "description": "This is a test notification to verify your alert settings are working correctly.",
            "location": {"name": "Test Location"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if notification_type == "all":
            return await self.send_alert_notification(test_alert, user_id, db)
        else:
            # Send specific type only
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            result = {"success": False}
            
            if notification_type == "email" and user.email:
                html_content, text_content = self.email_service.generate_alert_email(
                    test_alert, user.full_name or user.email
                )
                result["email"] = await self.email_service.send_email(
                    user.email, "Test: Coastal Alert System", html_content, text_content
                )
                result["success"] = result["email"]
            
            elif notification_type == "sms":
                preferences = db.query(UserPreferences).filter(
                    UserPreferences.user_id == user_id
                ).first()
                
                if preferences and preferences.phone_number:
                    sms_content = "🌊 Test: Coastal Alert System is working correctly!"
                    result["sms"] = await self.sms_service.send_sms(
                        preferences.phone_number, sms_content
                    )
                    result["success"] = result["sms"]
            
            elif notification_type == "push" and user.device_token:
                result["push"] = await self.push_service.send_push_notification(
                    user.device_token,
                    "🌊 Test Notification",
                    "Coastal Alert System is working correctly!",
                    {"type": "test"}
                )
                result["success"] = result["push"]
            
            return result

# Global notification service instance
notification_service = NotificationService()