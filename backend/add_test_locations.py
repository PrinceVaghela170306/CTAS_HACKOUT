#!/usr/bin/env python3

import sqlite3
from datetime import datetime

def add_test_locations():
    conn = sqlite3.connect('ctas.db')
    cursor = conn.cursor()
    
    # Sample location data with real coordinates
    test_locations = [
        {
            'name': 'Chennai Marina Beach',
            'latitude': 13.0827,
            'longitude': 80.2707,
            'user_id': None,
            'is_primary': 1,
            'state': 'Tamil Nadu',
            'district': 'Chennai',
            'pincode': '600001',
            'nearest_tide_station': 'Chennai Port',
            'nearest_weather_station': 'Chennai Nungambakkam'
        },
        {
            'name': 'Mumbai Marine Drive',
            'latitude': 18.9220,
            'longitude': 72.8347,
            'user_id': None,
            'is_primary': 0,
            'state': 'Maharashtra',
            'district': 'Mumbai',
            'pincode': '400020',
            'nearest_tide_station': 'Mumbai Port',
            'nearest_weather_station': 'Mumbai Colaba'
        },
        {
            'name': 'Puducherry Beach',
            'latitude': 11.9416,
            'longitude': 79.8083,
            'user_id': None,
            'is_primary': 0,
            'state': 'Puducherry',
            'district': 'Puducherry',
            'pincode': '605001',
            'nearest_tide_station': 'Puducherry Port',
            'nearest_weather_station': 'Puducherry'
        },
        {
            'name': 'Kochi Backwaters',
            'latitude': 9.9312,
            'longitude': 76.2673,
            'user_id': None,
            'is_primary': 0,
            'state': 'Kerala',
            'district': 'Ernakulam',
            'pincode': '682001',
            'nearest_tide_station': 'Kochi Port',
            'nearest_weather_station': 'Kochi'
        },
        {
            'name': 'Visakhapatnam Beach',
            'latitude': 17.6868,
            'longitude': 83.2185,
            'user_id': None,
            'is_primary': 0,
            'state': 'Andhra Pradesh',
            'district': 'Visakhapatnam',
            'pincode': '530001',
            'nearest_tide_station': 'Visakhapatnam Port',
            'nearest_weather_station': 'Visakhapatnam'
        },
        {
            'name': 'Goa Calangute Beach',
            'latitude': 15.5527,
            'longitude': 73.7545,
            'user_id': None,
            'is_primary': 0,
            'state': 'Goa',
            'district': 'North Goa',
            'pincode': '403516',
            'nearest_tide_station': 'Mormugao Port',
            'nearest_weather_station': 'Panaji'
        }
    ]
    
    # Clear existing test locations first
    cursor.execute("DELETE FROM locations WHERE user_id IS NULL")
    
    # Insert test locations
    for location in test_locations:
        cursor.execute("""
            INSERT INTO locations (
                name, latitude, longitude, user_id, is_primary, created_at, updated_at,
                state, district, pincode, nearest_tide_station, nearest_weather_station
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            location['name'],
            location['latitude'],
            location['longitude'],
            location['user_id'],
            location['is_primary'],
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            location['state'],
            location['district'],
            location['pincode'],
            location['nearest_tide_station'],
            location['nearest_weather_station']
        ))
    
    conn.commit()
    print(f"Added {len(test_locations)} test locations to the database.")
    
    # Display the locations
    cursor.execute("SELECT * FROM locations ORDER BY created_at DESC")
    locations = cursor.fetchall()
    
    cursor.execute("PRAGMA table_info(locations)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print("\nLocations in database:")
    for location in locations:
        location_dict = dict(zip(columns, location))
        print(f"- {location_dict['name']} ({location_dict['latitude']}, {location_dict['longitude']}) - {location_dict['state']}")
    
    conn.close()

if __name__ == '__main__':
    add_test_locations()