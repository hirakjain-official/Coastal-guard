#!/usr/bin/env python3
"""
Test script to verify Twilio service functionality
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from services.twilio_alert_service import TwilioAlertService

def test_twilio_config():
    """Test Twilio configuration"""
    print("🧪 Testing Twilio Configuration...")
    print("-" * 50)
    
    # Check environment variables
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN') 
    phone_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    print(f"TWILIO_ACCOUNT_SID: {'✅ Set' if account_sid else '❌ Missing'}")
    if account_sid:
        print(f"  Value: {account_sid[:8]}...{account_sid[-4:]}")
    
    print(f"TWILIO_AUTH_TOKEN: {'✅ Set' if auth_token else '❌ Missing'}")
    if auth_token:
        print(f"  Value: {auth_token[:8]}...{auth_token[-4:]}")
        
    print(f"TWILIO_PHONE_NUMBER: {'✅ Set' if phone_number else '❌ Missing'}")
    if phone_number:
        print(f"  Value: {phone_number}")
    
    return account_sid and auth_token and phone_number

def test_twilio_service():
    """Test Twilio service initialization"""
    print("\n📞 Testing Twilio Service...")
    print("-" * 50)
    
    service = TwilioAlertService()
    
    print(f"Service Available: {'✅ Yes' if service.is_available() else '❌ No'}")
    
    if service.is_available():
        print("Twilio client initialized successfully")
        return service
    else:
        print("Twilio service not available - check credentials")
        return None

def test_phone_number_formatting(service):
    """Test phone number formatting"""
    print("\n📱 Testing Phone Number Formatting...")
    print("-" * 50)
    
    test_numbers = [
        "7011384027",        # 10 digit Indian
        "+917011384027",     # Already formatted Indian
        "917011384027",      # 12 digit with country code
        "1234567890",        # US format
        "+1234567890",       # Already formatted US
        "invalid",           # Invalid
        "",                  # Empty
    ]
    
    for number in test_numbers:
        formatted = service._format_phone_number(number)
        status = "✅" if formatted else "❌"
        print(f"  {number:15} -> {formatted or 'INVALID':15} {status}")

def test_message_creation(service):
    """Test message creation"""
    print("\n💬 Testing Message Creation...")
    print("-" * 50)
    
    sample_report = {
        'hazard_type': 'Flood',
        'severity': 'High',
        'city': 'Delhi',
        'state': 'Delhi',
        'description': 'Severe flooding detected in the area'
    }
    
    base_message = "Emergency alert: Immediate action required"
    
    # Test SMS message
    sms_message = service._create_sms_message(base_message, sample_report)
    print("SMS Message Preview:")
    print("─" * 30)
    print(sms_message[:200] + "..." if len(sms_message) > 200 else sms_message)
    
    print(f"\nSMS Length: {len(sms_message)} characters")
    
    # Test voice message
    voice_message = service._create_voice_message(base_message, sample_report)
    print(f"\nVoice Message Preview:")
    print("─" * 30)
    print(voice_message)
    print(f"\nVoice Length: {len(voice_message)} characters")

def test_send_test_alert(service):
    """Test sending actual alert"""
    print("\n🚨 Testing Alert Sending...")
    print("-" * 50)
    
    # Get the current Twilio phone number for testing
    test_phone = os.getenv('TWILIO_PHONE_NUMBER', '+917011384027')
    
    print(f"Target Phone: {test_phone}")
    print("⚠️  NOTE: This will only work if the phone number is verified in your Twilio account")
    print("          For trial accounts, you can only call/SMS verified numbers")
    
    sample_report = {
        'hazard_type': 'Flood',
        'severity': 'High', 
        'city': 'Delhi',
        'state': 'Delhi',
        'description': 'Test alert from system'
    }
    
    test_message = "This is a test alert from the Coastal Hazard Management System"
    
    # Test SMS
    print(f"\n📱 Attempting SMS to {test_phone}...")
    sms_success, sms_result = service.send_sms_alert(test_phone, test_message, sample_report)
    
    if sms_success:
        print(f"✅ SMS Success! Message ID: {sms_result}")
    else:
        print(f"❌ SMS Failed: {sms_result}")
        if "unverified" in sms_result.lower():
            print("   💡 TIP: Verify this phone number in your Twilio console")
            print("   💡 OR: Upgrade to a paid Twilio account")
    
    # Test Voice Call
    print(f"\n📞 Attempting Voice Call to {test_phone}...")
    voice_success, voice_result = service.make_voice_call_alert(test_phone, test_message, sample_report)
    
    if voice_success:
        print(f"✅ Voice Call Success! Call ID: {voice_result}")
    else:
        print(f"❌ Voice Call Failed: {voice_result}")
        if "unverified" in voice_result.lower():
            print("   💡 TIP: Verify this phone number in your Twilio console")
            print("   💡 OR: Upgrade to a paid Twilio account")

def main():
    """Main test function"""
    print("🧪 TWILIO SERVICE TEST")
    print("=" * 70)
    
    # Test 1: Configuration
    if not test_twilio_config():
        print("\n❌ FAILED: Twilio not configured properly")
        print("   Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER")
        return False
    
    # Test 2: Service initialization  
    service = test_twilio_service()
    if not service:
        print("\n❌ FAILED: Could not initialize Twilio service")
        return False
    
    # Test 3: Phone number formatting
    test_phone_number_formatting(service)
    
    # Test 4: Message creation
    test_message_creation(service)
    
    # Test 5: Send actual test alert
    print("\n" + "=" * 50)
    response = input("Do you want to send a test alert? (y/N): ").lower().strip()
    if response == 'y' or response == 'yes':
        test_send_test_alert(service)
    else:
        print("Skipping test alert sending...")
    
    print("\n" + "=" * 70)
    print("🏁 TWILIO TEST COMPLETE")
    
    return True

if __name__ == "__main__":
    success = True
    try:
        success = main()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)
