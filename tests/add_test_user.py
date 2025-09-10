#!/usr/bin/env python3
"""
Add a test user with phone number for alert testing
"""

import sqlite3
from werkzeug.security import generate_password_hash

def add_test_user():
    """Add test user with phone number."""
    
    # Connect to database
    conn = sqlite3.connect('coastal_hazards.db')
    cursor = conn.cursor()
    
    # Check if test user already exists
    cursor.execute('SELECT * FROM users WHERE email = ?', ('testuser@example.com',))
    if cursor.fetchone():
        print("✅ Test user already exists")
        conn.close()
        return
    
    # Create test user with phone number
    password_hash = generate_password_hash('testpass123')
    cursor.execute('''
        INSERT INTO users (email, name, password_hash, phone_number, alert_preferences, role)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        'testuser@example.com', 
        'Test User', 
        password_hash, 
        '+919876543210',  # Test Indian phone number
        'sms,voice',      # Both SMS and voice alerts
        'user'
    ))
    
    user_id = cursor.lastrowid
    
    # Also create a test report for the user
    cursor.execute('''
        INSERT INTO reports (
            user_id, title, description, hazard_type, severity,
            latitude, longitude, city, state, status, correlation_confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        'TEST: Coastal Flooding in Mumbai',
        'Severe flooding observed near Marine Drive. Water levels rising rapidly due to high tide and heavy rains.',
        'flood',
        'High',
        19.0176, 72.8562,  # Mumbai coordinates
        'Mumbai', 'Maharashtra',
        'pending',
        0.85
    ))
    
    report_id = cursor.lastrowid
    
    # Add to status history
    cursor.execute('''
        INSERT INTO report_status_history (
            report_id, old_status, new_status, changed_by,
            admin_notes, correlation_confidence, social_media_count, change_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        report_id, None, 'pending', user_id,
        'Test report created for alert system testing', 0.85, 0,
        'Test data creation'
    ))
    
    conn.commit()
    conn.close()
    
    print("✅ Test user created successfully!")
    print("📧 Email: testuser@example.com")
    print("🔑 Password: testpass123")  
    print("📱 Phone: +919876543210")
    print(f"📋 Created test report ID: {report_id}")
    print("\nYou can now:")
    print("1. Login as admin and send alerts to this test user")
    print("2. Login as this test user to see the user experience")

if __name__ == "__main__":
    add_test_user()
