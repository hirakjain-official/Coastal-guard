#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from services.twilio_alert_service import TwilioAlertService

def main():
    print("🚨 EMERGENCY CALL TO VERIFIED NUMBER")
    print("=" * 60)
    
    service = TwilioAlertService()
    
    # Use the verified number
    target_number = "+917011384027"
    
    message = "EMERGENCY TEST: This is a test alert from the Coastal Hazard Management System. The call is working successfully."
    
    report_data = {
        'hazard_type': 'Test',
        'severity': 'High',
        'city': 'Delhi',
        'state': 'Delhi'
    }
    
    print(f"Calling: {target_number}")
    print("Status: Verified ✅")
    print("-" * 40)
    
    # Make the call
    try:
        success, result = service.make_voice_call_alert(target_number, message, report_data)
        
        if success:
            print("🎉 SUCCESS!")
            print(f"Call ID: {result}")
            print("📞 YOUR PHONE SHOULD BE RINGING!")
            print("Answer to hear the emergency alert.")
        else:
            print("❌ FAILED")
            print(f"Error: {result}")
            
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
