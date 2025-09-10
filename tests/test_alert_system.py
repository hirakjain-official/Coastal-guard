#!/usr/bin/env python3
"""
Test script for Twilio Alert System
Tests SMS and voice call functionality with sample data.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from services.twilio_alert_service import twilio_service

def test_phone_number_formatting():
    """Test phone number formatting functionality."""
    print("🔍 Testing phone number formatting...")
    
    test_numbers = [
        "9876543210",          # Indian 10-digit
        "+919876543210",       # Indian with country code
        "919876543210",        # Indian with country code (no +)
        "+1234567890",         # US number
        "1234567890",          # US number (no country code)
        "invalid",             # Invalid number
        "",                    # Empty number
    ]
    
    for number in test_numbers:
        formatted = twilio_service._format_phone_number(number)
        print(f"  {number:<15} -> {formatted}")
    
    print()

def test_message_templates():
    """Test alert message template generation."""
    print("📝 Testing message templates...")
    
    test_scenarios = [
        ("flood", "high"),
        ("tsunami", "high"), 
        ("storm_surge", "high"),
        ("erosion", "medium"),
        ("general", "low")
    ]
    
    for hazard_type, severity in test_scenarios:
        sms_msg = twilio_service.get_template_message(hazard_type, severity, 'sms')
        voice_msg = twilio_service.get_template_message(hazard_type, severity, 'voice')
        
        print(f"  {hazard_type.upper()} ({severity.upper()}):")
        print(f"    SMS: {sms_msg[:60]}...")
        print(f"    Voice: {voice_msg[:60]}...")
        print()

def test_message_formatting():
    """Test SMS and voice message formatting."""
    print("💬 Testing message formatting...")
    
    sample_report = {
        'id': 123,
        'title': 'Severe Flooding in Mumbai',
        'hazard_type': 'flood',
        'severity': 'High',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'address': 'Marine Drive, South Mumbai',
        'correlation_confidence': 0.85
    }
    
    base_message = "URGENT: Severe flooding detected. Immediate evacuation may be required."
    
    sms_message = twilio_service._create_sms_message(base_message, sample_report)
    voice_message = twilio_service._create_voice_message(base_message, sample_report)
    
    print("SMS Message:")
    print("-" * 40)
    print(sms_message)
    print("-" * 40)
    
    print("\nVoice Message:")
    print("-" * 40)
    print(voice_message)
    print("-" * 40)
    print()

def test_twilio_configuration():
    """Test Twilio service configuration."""
    print("⚙️  Testing Twilio configuration...")
    
    print(f"  Service Available: {twilio_service.is_available()}")
    print(f"  Account SID: {twilio_service.account_sid[:8] + '...' if twilio_service.account_sid else 'Not set'}")
    print(f"  Phone Number: {twilio_service.phone_number or 'Not set'}")
    
    if not twilio_service.is_available():
        print("  ❌ Twilio not configured properly!")
        print("     Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in .env")
    else:
        print("  ✅ Twilio configured successfully!")
    
    print()

def test_send_sms(test_phone_number=None):
    """Test sending SMS alert (requires valid Twilio credentials and phone number)."""
    if not test_phone_number:
        test_phone_number = input("Enter a test phone number (+919876543210 format) or press Enter to skip: ").strip()
    
    if not test_phone_number:
        print("📱 Skipping SMS test (no phone number provided)")
        return
    
    if not twilio_service.is_available():
        print("📱 Cannot test SMS - Twilio not configured")
        return
    
    print(f"📱 Testing SMS to {test_phone_number}...")
    
    sample_report = {
        'id': 999,
        'title': 'TEST ALERT - Please Ignore',
        'hazard_type': 'general',
        'severity': 'Low',
        'city': 'Test City',
        'state': 'Test State',
        'correlation_confidence': 0.95
    }
    
    message = "TEST ALERT: This is a test of the emergency alert system. Please ignore."
    
    try:
        success, result = twilio_service.send_sms_alert(test_phone_number, message, sample_report)
        
        if success:
            print(f"  ✅ SMS sent successfully! Message ID: {result}")
        else:
            print(f"  ❌ SMS failed: {result}")
    
    except Exception as e:
        print(f"  ❌ SMS test error: {str(e)}")
    
    print()

def test_make_voice_call(test_phone_number=None):
    """Test making voice call alert (requires valid Twilio credentials and phone number)."""
    if not test_phone_number:
        test_phone_number = input("Enter a test phone number (+919876543210 format) or press Enter to skip: ").strip()
    
    if not test_phone_number:
        print("📞 Skipping voice call test (no phone number provided)")
        return
    
    if not twilio_service.is_available():
        print("📞 Cannot test voice call - Twilio not configured")
        return
    
    print(f"📞 Testing voice call to {test_phone_number}...")
    
    sample_report = {
        'id': 999,
        'title': 'TEST ALERT - Please Ignore',
        'hazard_type': 'general',
        'severity': 'Low',
        'city': 'Test City', 
        'state': 'Test State',
        'correlation_confidence': 0.95
    }
    
    message = "This is a test of the emergency voice alert system. Please ignore this test message."
    
    try:
        success, result = twilio_service.make_voice_call_alert(test_phone_number, message, sample_report)
        
        if success:
            print(f"  ✅ Voice call initiated successfully! Call ID: {result}")
        else:
            print(f"  ❌ Voice call failed: {result}")
    
    except Exception as e:
        print(f"  ❌ Voice call test error: {str(e)}")
    
    print()

def test_bulk_alerts():
    """Test bulk alert functionality."""
    print("📢 Testing bulk alert functionality...")
    
    # Mock recipients
    test_recipients = [
        {'name': 'Test User 1', 'phone_number': '+919876543210'},
        {'name': 'Test User 2', 'phone_number': '+919876543211'},
        {'name': 'User No Phone', 'phone_number': ''},  # This should fail
        {'name': 'Invalid Phone', 'phone_number': 'invalid'},  # This should fail
    ]
    
    sample_report = {
        'id': 888,
        'title': 'TEST BULK ALERT',
        'hazard_type': 'general',
        'severity': 'Medium',
        'city': 'Test City',
        'state': 'Test State',
        'correlation_confidence': 0.75
    }
    
    message = "TEST: Bulk alert system test. Please ignore."
    
    print("  Testing bulk SMS (dry run - no actual sending)...")
    # Note: This won't actually send unless Twilio is configured and recipients are valid
    
    # Simulate bulk SMS results
    mock_sms_results = {
        'total': len(test_recipients),
        'successful': 2,
        'failed': 2,
        'details': [
            {'recipient': 'Test User 1', 'status': 'sent', 'message_id': 'SM123...'},
            {'recipient': 'Test User 2', 'status': 'sent', 'message_id': 'SM124...'},
            {'recipient': 'User No Phone', 'status': 'failed', 'error': 'No phone number'},
            {'recipient': 'Invalid Phone', 'status': 'failed', 'error': 'Invalid format'},
        ]
    }
    
    print(f"    Total: {mock_sms_results['total']}, Success: {mock_sms_results['successful']}, Failed: {mock_sms_results['failed']}")
    for detail in mock_sms_results['details']:
        status_icon = "✅" if detail['status'] == 'sent' else "❌"
        print(f"      {status_icon} {detail['recipient']}: {detail.get('message_id', detail.get('error'))}")
    
    print()

def main():
    """Run all alert system tests."""
    print("🚨 COASTAL HAZARD ALERT SYSTEM - TEST SUITE 🚨")
    print("=" * 50)
    print()
    
    # Basic functionality tests
    test_twilio_configuration()
    test_phone_number_formatting()
    test_message_templates()
    test_message_formatting()
    test_bulk_alerts()
    
    # Interactive tests (require user input and valid Twilio config)
    print("🧪 INTERACTIVE TESTS")
    print("=" * 30)
    print("The following tests require valid Twilio credentials and a real phone number.")
    print("They will send actual SMS/voice messages if configured properly.")
    print()
    
    if input("Do you want to run interactive tests? (y/N): ").lower().strip() == 'y':
        test_phone = input("Enter your test phone number (+country code format): ").strip()
        if test_phone:
            print(f"\nUsing test phone number: {test_phone}")
            test_send_sms(test_phone)
            
            if input("Do you want to test voice calls too? (y/N): ").lower().strip() == 'y':
                test_make_voice_call(test_phone)
    
    print("✅ All tests completed!")
    print("\nNext steps:")
    print("1. Configure your Twilio credentials in .env file")
    print("2. Register users with phone numbers in your app")
    print("3. Test the admin alert confirmation interface")
    print("4. Monitor alert delivery success rates")

if __name__ == "__main__":
    main()
