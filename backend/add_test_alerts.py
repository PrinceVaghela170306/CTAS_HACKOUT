#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timedelta
import random

def add_test_alerts():
    conn = sqlite3.connect('ctas.db')
    cursor = conn.cursor()
    
    # Sample alert data
    test_alerts = [
        {
            'title': 'Cyclone Biparjoy Warning',
            'description': 'Very severe cyclonic storm approaching Gujarat coast. Expected landfall in 24-48 hours.',
            'alert_type': 'CYCLONE',
            'severity': 'CRITICAL',
            'status': 'ACTIVE',
            'location_id': 1,
            'user_id': None,
            'data_source_id': 1,
            'expires_at': (datetime.now() + timedelta(days=2)).isoformat(),
            'source_url': 'https://mausam.imd.gov.in/',
            'image_url': None,
            'push_sent': 1,
            'sms_sent': 1
        },
        {
            'title': 'High Tide Alert - Mumbai',
            'description': 'Exceptionally high tides expected during evening hours. Coastal areas may experience flooding.',
            'alert_type': 'FLOOD',
            'severity': 'HIGH',
            'status': 'ACTIVE',
            'location_id': 2,
            'user_id': None,
            'data_source_id': 2,
            'expires_at': (datetime.now() + timedelta(hours=12)).isoformat(),
            'source_url': 'https://incois.gov.in/',
            'image_url': None,
            'push_sent': 1,
            'sms_sent': 0
        },
        {
            'title': 'Coastal Erosion Alert - Puducherry',
            'description': 'Accelerated coastal erosion detected due to recent storm activity. Beach access restricted.',
            'alert_type': 'EROSION',
            'severity': 'MEDIUM',
            'status': 'ACTIVE',
            'location_id': 3,
            'user_id': None,
            'data_source_id': 3,
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat(),
            'source_url': None,
            'image_url': None,
            'push_sent': 0,
            'sms_sent': 0
        },
        {
            'title': 'Sea Level Rise Monitoring',
            'description': 'Gradual sea level rise observed. Long-term monitoring indicates 2.3mm annual increase.',
            'alert_type': 'SEA_LEVEL_RISE',
            'severity': 'LOW',
            'status': 'MONITORING',
            'location_id': 1,
            'user_id': None,
            'data_source_id': 4,
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'source_url': 'https://www.noaa.gov/',
            'image_url': None,
            'push_sent': 0,
            'sms_sent': 0
        },
        {
            'title': 'Algal Bloom Detection',
            'description': 'Harmful algal bloom detected in coastal waters. Swimming and fishing not recommended.',
            'alert_type': 'WATER_QUALITY',
            'severity': 'MEDIUM',
            'status': 'ACTIVE',
            'location_id': 2,
            'user_id': None,
            'data_source_id': 5,
            'expires_at': (datetime.now() + timedelta(days=5)).isoformat(),
            'source_url': None,
            'image_url': None,
            'push_sent': 1,
            'sms_sent': 1
        }
    ]
    
    # Insert test alerts
    for alert in test_alerts:
        cursor.execute("""
            INSERT INTO alerts (
                title, description, alert_type, severity, status, location_id, 
                user_id, data_source_id, created_at, updated_at, expires_at, 
                source_url, image_url, push_sent, sms_sent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert['title'],
            alert['description'],
            alert['alert_type'],
            alert['severity'],
            alert['status'],
            alert['location_id'],
            alert['user_id'],
            alert['data_source_id'],
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            alert['expires_at'],
            alert['source_url'],
            alert['image_url'],
            alert['push_sent'],
            alert['sms_sent']
        ))
    
    conn.commit()
    print(f"Added {len(test_alerts)} test alerts to the database.")
    
    # Display the alerts
    cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 10")
    alerts = cursor.fetchall()
    
    cursor.execute("PRAGMA table_info(alerts)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print("\nRecent alerts in database:")
    for alert in alerts:
        alert_dict = dict(zip(columns, alert))
        print(f"- {alert_dict['title']} ({alert_dict['severity']}) - {alert_dict['status']}")
    
    conn.close()

if __name__ == '__main__':
    add_test_alerts()