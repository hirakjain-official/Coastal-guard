#!/usr/bin/env python3
"""
Simple test to call +917011384027
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from services.twilio_alert_service import TwilioAlertService

def main():
    print("🚨 EMERGENCY CALL TEST")
    print("=" * 50)
    
    # Initialize service
    service = TwilioAlertService()
    
    if not service.is_available():
        print("❌ Twilio service not available")
        return False
    
    # Target number
    target_number = "+917011384027"
    
    # Test message
    message = "URGENT TEST: This is an emergency alert from the Coastal Hazard Management System."
    
    # Sample report data
    report_data = {
        'hazard_type': 'Flood',
        'severity': 'High',
        'city': 'Delhi',
        'state': 'Delhi',
        'description': 'Emergency test call'
    }
    
    print(f"📞 Attempting to call: {target_number}")
    print(f"📢 Message: {message}")
    print("-" * 50)
    
    # Make the call
    success, result = service.make_voice_call_alert(target_number, message, report_data)
    
    if success:
        print("✅ SUCCESS!")
        print(f"📱 Call ID: {result}")
        print("🔔 Phone should be ringing now...")
        return True
    else:
        print("❌ FAILED!")
        print(f"🚫 Error Details:")
        print(f"   {result}")
        
        if "unverified" in result.lower():
            print("\n💡 SOLUTION:")
            print("   This phone number is not verified in your Twilio account.")
            print("   For trial accounts, you can only call verified numbers.")
            print("\n📝 To fix this:")
            print("   1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
            print(f"   2. Add and verify: {target_number}")
            print("   3. OR upgrade to a paid Twilio account")
        
        return False

if __name__ == "__main__":
    try:
        success = main()
        print("\n" + "=" * 50)
        if success:
            print("🏁 TEST COMPLETED SUCCESSFULLY")
        else:
            print("🏁 TEST FAILED - SEE INSTRUCTIONS ABOVE")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
