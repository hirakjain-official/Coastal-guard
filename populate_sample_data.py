#!/usr/bin/env python3
"""
Script to populate the database with sample data for demonstration purposes
"""

import sqlite3
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import random

# Database connection
DATABASE = 'coastal_hazards.db'

def create_sample_users():
    """Create sample users for testing"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Sample users data
    sample_users = [
        {
            'email': 'user1@example.com',
            'name': 'Rajesh Kumar',
            'phone_number': '+919876543210',
            'role': 'user'
        },
        {
            'email': 'user2@example.com', 
            'name': 'Priya Sharma',
            'phone_number': '+919876543211',
            'role': 'user'
        },
        {
            'email': 'user3@example.com',
            'name': 'Amit Patel',
            'phone_number': '+919876543212', 
            'role': 'user'
        },
        {
            'email': 'emergency@coastal.gov',
            'name': 'Emergency Coordinator',
            'phone_number': '+919876543213',
            'role': 'admin'
        }
    ]
    
    print("Creating sample users...")
    for user_data in sample_users:
        # Check if user already exists
        existing = cursor.execute('SELECT id FROM users WHERE email = ?', (user_data['email'],)).fetchone()
        if existing:
            print(f"  ⚠️  User {user_data['email']} already exists, skipping")
            continue
            
        password_hash = generate_password_hash('password123')
        
        cursor.execute('''
            INSERT INTO users (email, name, password_hash, phone_number, role, alert_preferences)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_data['email'], user_data['name'], password_hash, 
              user_data['phone_number'], user_data['role'], 'sms,voice'))
        
        print(f"  ✅ Created user: {user_data['name']} ({user_data['email']})")
    
    conn.commit()
    conn.close()

def create_sample_reports():
    """Create sample hazard reports"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get user IDs
    users = cursor.execute('SELECT id, name FROM users WHERE role = "user"').fetchall()
    
    if not users:
        print("❌ No users found. Please create users first.")
        conn.close()
        return
    
    # Sample coastal locations in India
    sample_locations = [
        {'city': 'Mumbai', 'state': 'Maharashtra', 'lat': 19.0760, 'lng': 72.8777},
        {'city': 'Chennai', 'state': 'Tamil Nadu', 'lat': 13.0827, 'lng': 80.2707},
        {'city': 'Kolkata', 'state': 'West Bengal', 'lat': 22.5726, 'lng': 88.3639},
        {'city': 'Kochi', 'state': 'Kerala', 'lat': 9.9312, 'lng': 76.2673},
        {'city': 'Visakhapatnam', 'state': 'Andhra Pradesh', 'lat': 17.6868, 'lng': 83.2185},
        {'city': 'Goa', 'state': 'Goa', 'lat': 15.2993, 'lng': 74.1240},
        {'city': 'Mangalore', 'state': 'Karnataka', 'lat': 12.9716, 'lng': 74.7965},
        {'city': 'Pondicherry', 'state': 'Puducherry', 'lat': 11.9416, 'lng': 79.8083}
    ]
    
    # Sample hazard types and descriptions
    hazard_samples = [
        {
            'type': 'Flood',
            'titles': [
                'Coastal flooding reported in beach area',
                'High tide causing water logging',
                'Storm water overflow near shore'
            ],
            'descriptions': [
                'Heavy rainfall combined with high tide has caused flooding in the coastal areas. Water level is rising rapidly.',
                'Unusual high tide patterns observed. Several low-lying areas are waterlogged.',
                'Storm drainage system unable to cope with water influx. Immediate attention required.'
            ]
        },
        {
            'type': 'Storm_Surge',
            'titles': [
                'Large waves hitting coastline',
                'Storm surge warning in effect',
                'Dangerous wave conditions observed'
            ],
            'descriptions': [
                'Strong storm system causing large waves to crash against the shore. Potential property damage.',
                'Meteorological conditions indicate storm surge risk. Coastal areas should be evacuated.',
                'Unusually large waves observed. Fishing boats advised to stay in harbor.'
            ]
        },
        {
            'type': 'Coastal_Erosion',
            'titles': [
                'Beach erosion accelerating',
                'Shoreline retreating rapidly',
                'Coastal infrastructure at risk'
            ],
            'descriptions': [
                'Significant erosion of beach sand observed over past few days. Structures near shore at risk.',
                'Continuous wave action causing shoreline to retreat. Monitoring required.',
                'Coastal road showing signs of undermining due to erosion. Urgent assessment needed.'
            ]
        }
    ]
    
    severities = ['Low', 'Medium', 'High', 'Critical']
    statuses = ['pending', 'reviewing', 'investigating', 'resolved']
    
    print("Creating sample reports...")
    
    # Create 15-20 sample reports
    for i in range(15):
        user = random.choice(users)
        location = random.choice(sample_locations)
        hazard = random.choice(hazard_samples)
        
        title = random.choice(hazard['titles'])
        description = random.choice(hazard['descriptions'])
        severity = random.choice(severities)
        status = random.choice(statuses)
        
        # Generate random coordinates near the city
        lat_offset = random.uniform(-0.05, 0.05)
        lng_offset = random.uniform(-0.05, 0.05)
        
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        cursor.execute('''
            INSERT INTO reports (
                user_id, title, description, hazard_type, severity, status,
                latitude, longitude, city, state, address,
                correlation_confidence, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user[0], title, description, hazard['type'], severity, status,
            location['lat'] + lat_offset, location['lng'] + lng_offset,
            location['city'], location['state'], f"Near {location['city']} coast",
            random.uniform(0.6, 0.95), created_at, created_at
        ))
        
        report_id = cursor.lastrowid
        
        # Add status history
        cursor.execute('''
            INSERT INTO report_status_history (
                report_id, old_status, new_status, changed_by, 
                admin_notes, correlation_confidence, social_media_count, change_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report_id, None, 'pending', user[0], 
            'Report created by user', random.uniform(0.6, 0.95), 
            random.randint(0, 10), 'Initial report submission'
        ))
        
        print(f"  ✅ Created report: {title} by {user[1]} in {location['city']}")
    
    conn.commit()
    conn.close()

def create_sample_alerts():
    """Create some sample alert broadcasts"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get admin user and some reports
    admin = cursor.execute('SELECT id FROM users WHERE role = "admin" LIMIT 1').fetchone()
    reports = cursor.execute('SELECT id FROM reports WHERE status != "pending" LIMIT 3').fetchall()
    
    if not admin or not reports:
        print("⚠️  No admin user or reports found for creating sample alerts")
        conn.close()
        return
    
    print("Creating sample alert broadcasts...")
    
    for report in reports:
        alert_type = random.choice(['sms', 'voice', 'both'])
        recipients_count = random.randint(5, 20)
        successful_count = random.randint(int(recipients_count * 0.7), recipients_count)
        failed_count = recipients_count - successful_count
        
        cursor.execute('''
            INSERT INTO alert_broadcasts (
                report_id, alert_type, message_content, recipients_count,
                successful_count, failed_count, broadcast_details, admin_user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report[0], alert_type, 
            "Emergency coastal hazard alert - please follow local safety guidelines",
            recipients_count, successful_count, failed_count,
            json.dumps({'test': 'sample alert data'}), admin[0]
        ))
        
        print(f"  ✅ Created alert broadcast for report {report[0]}")
    
    conn.commit()
    conn.close()

def main():
    """Main function to populate sample data"""
    print("🏗️  Populating Database with Sample Data")
    print("="*50)
    
    try:
        # Create sample users
        create_sample_users()
        print()
        
        # Create sample reports
        create_sample_reports()
        print()
        
        # Create sample alerts
        create_sample_alerts()
        print()
        
        print("✅ Sample data creation completed successfully!")
        print("\nYou can now log in with:")
        print("  👤 User: user1@example.com / password123")
        print("  👤 User: user2@example.com / password123") 
        print("  👤 User: user3@example.com / password123")
        print("  👑 Admin: admin@coastal.gov / admin123")
        print("  👑 Admin: emergency@coastal.gov / password123")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
