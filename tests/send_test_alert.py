#!/usr/bin/env python3
"""
Direct test script to send SMS and voice alerts via Twilio.
Use this to test alert functionality without the web interface.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from services.twilio_alert_service import twilio_service

def send_test_sms():
    """Send a test SMS alert."""
    print("📱 Sending test SMS alert...")
    
    # Test phone number (replace with your number)
    phone_number = input("Enter recipient phone number (+919876543210 format): ").strip()
    
    if not phone_number:
        print("❌ No phone number provided")
        return
    
    # Sample report data
    report_data = {
        'id': 999,
        'title': 'TEST: Coastal Flooding Alert',
        'hazard_type': 'flood',
        'severity': 'High',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'address': 'Marine Drive Area',
        'correlation_confidence': 0.92
    }
    
    # Alert message
    message = "URGENT TEST: Severe coastal flooding detected in Mumbai. This is a test of the emergency alert system. Please ignore if received in error."
    
    # Send SMS
    success, result = twilio_service.send_sms_alert(phone_number, message, report_data)
    
    if success:
        print(f"✅ SMS sent successfully!")
        print(f"   Message ID: {result}")
        print(f"   Sent to: {phone_number}")
    else:
        print(f"❌ SMS failed: {result}")

def send_test_voice_call():
    """Send a test voice call alert."""
    print("📞 Sending test voice call alert...")
    
    # Test phone number (replace with your number)
    phone_number = input("Enter recipient phone number (+919876543210 format): ").strip()
    
    if not phone_number:
        print("❌ No phone number provided")
        return
    
    # Sample report data
    report_data = {
        'id': 999,
        'title': 'TEST: Coastal Emergency Alert',
        'hazard_type': 'tsunami',
        'severity': 'High',
        'city': 'Chennai',
        'state': 'Tamil Nadu',
        'correlation_confidence': 0.95
    }
    
    # Alert message (will be converted to speech)
    message = "This is a test of the emergency voice alert system. Tsunami warning issued for Chennai coastal areas. This is only a test. Please ignore."
    
    # Send voice call
    success, result = twilio_service.make_voice_call_alert(phone_number, message, report_data)
    
    if success:
        print(f"✅ Voice call initiated successfully!")
        print(f"   Call ID: {result}")
        print(f"   Called: {phone_number}")
        print("   📞 You should receive the call shortly...")
    else:
        print(f"❌ Voice call failed: {result}")

def send_bulk_alerts():
    """Send alerts to multiple recipients."""
    print("📢 Sending bulk alerts...")
    
    # Multiple recipients
    recipients = []
    print("Enter recipient phone numbers (press Enter with empty line to finish):")
    
    while True:
        phone = input("Phone number: ").strip()
        if not phone:
            break
        name = input(f"Name for {phone}: ").strip() or "User"
        recipients.append({'phone_number': phone, 'name': name})
    
    if not recipients:
        print("❌ No recipients provided")
        return
    
    # Sample report data
    report_data = {
        'id': 888,
        'title': 'BULK TEST: Multi-City Weather Alert',
        'hazard_type': 'storm_surge',
        'severity': 'Medium',
        'city': 'Multiple Cities',
        'state': 'India',
        'correlation_confidence': 0.78
    }
    
    # Alert message
    message = "BULK TEST: Storm surge warning for multiple coastal cities. This is a test of the bulk alert system. Please ignore if received."
    
    # Choose alert type
    alert_type = input("Choose alert type (sms/voice/both) [sms]: ").strip().lower() or 'sms'
    
    if alert_type in ['sms', 'both']:
        print("📱 Sending bulk SMS...")
        sms_results = twilio_service.send_bulk_sms_alerts(recipients, message, report_data)
        print(f"   SMS Results: {sms_results['successful']}/{sms_results['total']} successful")
        
        for detail in sms_results['details']:
            status_icon = "✅" if detail['status'] == 'sent' else "❌"
            print(f"   {status_icon} {detail['recipient']}: {detail.get('message_id', detail.get('error'))}")
    
    if alert_type in ['voice', 'both']:
        print("📞 Making bulk voice calls...")
        voice_results = twilio_service.make_bulk_voice_alerts(recipients, message, report_data)
        print(f"   Voice Results: {voice_results['successful']}/{voice_results['total']} successful")
        
        for detail in voice_results['details']:
            status_icon = "✅" if detail['status'] == 'called' else "❌"
            print(f"   {status_icon} {detail['recipient']}: {detail.get('call_id', detail.get('error'))}")

def main():
    """Main menu for testing alerts."""
    print("🚨 TWILIO ALERT SYSTEM - DIRECT TEST TOOL 🚨")
    print("=" * 50)
    
    if not twilio_service.is_available():
        print("❌ Twilio service not available!")
        print("Please check your .env configuration:")
        print("- TWILIO_ACCOUNT_SID")
        print("- TWILIO_AUTH_TOKEN") 
        print("- TWILIO_PHONE_NUMBER")
        return
    
    print("✅ Twilio service is ready!")
    print(f"📞 Using Twilio number: {twilio_service.phone_number}")
    print()
    
    while True:
        print("\nChoose an option:")
        print("1. Send test SMS")
        print("2. Send test voice call") 
        print("3. Send bulk alerts")
        print("4. View alert templates")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            send_test_sms()
        elif choice == '2':
            send_test_voice_call()
        elif choice == '3':
            send_bulk_alerts()
        elif choice == '4':
            print("\n📝 Available Alert Templates:")
            templates = twilio_service.get_alert_templates()
            for key, template in templates.items():
                print(f"   {key.upper()}:")
                print(f"     SMS: {template['sms'][:80]}...")
                print(f"     Voice: {template['voice'][:80]}...")
                print()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
