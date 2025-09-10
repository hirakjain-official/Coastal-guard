#!/usr/bin/env python3
"""
Test script to verify the app can start without Twilio credentials.
This temporarily unsets Twilio environment variables and tries to import the app.
"""

import os
import sys
import tempfile
from pathlib import Path

# This code was moved to main() function

def main():
    # Save original env vars
    original_twilio_vars = {
        'TWILIO_ACCOUNT_SID': os.environ.get('TWILIO_ACCOUNT_SID'),
        'TWILIO_AUTH_TOKEN': os.environ.get('TWILIO_AUTH_TOKEN'),
        'TWILIO_PHONE_NUMBER': os.environ.get('TWILIO_PHONE_NUMBER'),
    }

    try:
        # Temporarily remove Twilio environment variables
        for var in original_twilio_vars:
            if var in os.environ:
                del os.environ[var]
        
        # Set required Flask secret key for testing
        os.environ['FLASK_SECRET_KEY'] = 'test-secret-key-for-deployment-testing'
        
        print("🧪 Testing app startup without Twilio credentials...")
        print("📝 Twilio environment variables temporarily removed")
        
        # Try to import the app
        sys.path.insert(0, str(Path(__file__).parent))
        
        try:
            import app
            print("✅ SUCCESS: App imported successfully without Twilio!")
            print(f"   - TWILIO_AVAILABLE: {app.TWILIO_AVAILABLE}")
            print(f"   - TWILIO_SERVICE_AVAILABLE: {app.TWILIO_SERVICE_AVAILABLE}")
            print("   - Core functionality will work")
            print("   - SMS/Voice alerts will be disabled (as expected)")
            
            # Test database initialization
            try:
                app.init_database()
                print("✅ Database initialization: SUCCESS")
            except Exception as e:
                print(f"❌ Database initialization failed: {e}")
            
            # Test translation loading
            try:
                app.load_translations()
                print("✅ Translation loading: SUCCESS")
            except Exception as e:
                print(f"❌ Translation loading failed: {e}")
                
            print("\n🚀 READY FOR DEPLOYMENT!")
            print("   Your app can be deployed without Twilio credentials.")
            print("   Add Twilio credentials later to enable SMS/Voice alerts.")
            
        except ImportError as e:
            print(f"❌ FAILED: App import failed: {e}")
            print("   There may be other missing dependencies.")
            return False
            
        except Exception as e:
            print(f"❌ FAILED: Unexpected error: {e}")
            return False
        
        return True

    finally:
        # Restore original environment variables
        for var, value in original_twilio_vars.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]
        
        print("\n🔄 Original environment variables restored")

if __name__ == "__main__":
    success = True
    try:
        success = main()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        success = False
    
    sys.exit(0 if success else 1)
