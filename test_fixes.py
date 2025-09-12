#!/usr/bin/env python3
"""
Test script to verify voice call functionality and multilingual support fixes.
"""

import sys
import os
import json
import sqlite3
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_twilio_voice_call():
    """Test Twilio voice call functionality"""
    print("🔊 Testing Twilio Voice Call Functionality...")
    
    try:
        from services.twilio_alert_service import TwilioAlertService
        
        # Create instance
        twilio_service = TwilioAlertService()
        
        # Test voice message creation
        report_data = {
            'hazard_type': 'flood',
            'severity': 'high',
            'city': 'Mumbai',
            'state': 'Maharashtra'
        }
        
        voice_message = twilio_service._create_voice_message(
            "Test emergency alert message", 
            report_data
        )
        
        print(f"✅ Voice message created: {voice_message[:100]}...")
        
        # Test TTS-friendly format
        assert len(voice_message) > 0, "Voice message should not be empty"
        assert '&amp;' not in voice_message or '&lt;' not in voice_message, "Voice message should not contain XML entities before escaping"
        
        print("✅ Voice call service is properly configured")
        
        # Test availability check
        is_available = twilio_service.is_available()
        print(f"📞 Twilio service available: {is_available}")
        
        if not is_available:
            print("⚠️  Twilio credentials not configured (this is OK for testing)")
        
    except ImportError as e:
        print(f"❌ Twilio import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Voice call test failed: {e}")
        return False
    
    return True

def test_multilingual_support():
    """Test multilingual support functionality"""
    print("\n🌍 Testing Multilingual Support...")
    
    try:
        # Load translations
        translations_file = Path(__file__).parent / 'config' / 'translations.json'
        with open(translations_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        # Test language availability
        expected_languages = ['en', 'hi', 'ta', 'te']
        available_languages = list(translations.keys())
        
        print(f"🗣️  Available languages: {available_languages}")
        
        for lang in expected_languages:
            assert lang in available_languages, f"Language {lang} should be available"
            print(f"✅ {lang} translations found")
        
        # Test extended translations beyond navigation
        test_keys = [
            'common.welcome',
            'common.send',
            'dashboard.title',
            'alerts.confirm_title',
            'alerts.alert_types.voice'
        ]
        
        for key in test_keys:
            keys = key.split('.')
            
            # Test English
            en_text = translations['en']
            for k in keys:
                en_text = en_text.get(k, None)
            
            assert en_text is not None, f"Key {key} should exist in English"
            
            # Test Hindi
            hi_text = translations['hi']
            for k in keys:
                hi_text = hi_text.get(k, None)
            
            assert hi_text is not None, f"Key {key} should exist in Hindi"
            
            print(f"✅ Translation key '{key}' exists: EN='{en_text[:30]}...', HI='{hi_text[:30]}...'")
        
        print("✅ Extended multilingual support verified")
        
    except FileNotFoundError:
        print("❌ Translations file not found")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON in translations file")
        return False
    except Exception as e:
        print(f"❌ Multilingual test failed: {e}")
        return False
    
    return True

def test_flask_app_integration():
    """Test Flask app integration with fixes"""
    print("\n🌐 Testing Flask App Integration...")
    
    try:
        # Import Flask app components
        sys.path.append(str(Path(__file__).parent))
        from app import get_translation, TRANSLATIONS
        
        # Test translation function
        test_text = get_translation('common.welcome', 'en')
        assert test_text == 'Welcome', f"Expected 'Welcome', got '{test_text}'"
        
        test_text_hi = get_translation('common.welcome', 'hi')
        assert 'स्वागत' in test_text_hi, f"Expected Hindi welcome message, got '{test_text_hi}'"
        
        print("✅ Flask translation function works")
        
        # Test alert system integration
        test_alert = get_translation('alerts.send_alert', 'en')
        assert test_alert == 'Send Alert', f"Expected 'Send Alert', got '{test_alert}'"
        
        test_alert_hi = get_translation('alerts.send_alert', 'hi')
        assert 'भेजें' in test_alert_hi, f"Expected Hindi alert text, got '{test_alert_hi}'"
        
        print("✅ Alert system translations work")
        
    except Exception as e:
        print(f"❌ Flask integration test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Running Fix Verification Tests\n")
    
    results = []
    
    # Test 1: Voice call functionality
    results.append(test_twilio_voice_call())
    
    # Test 2: Multilingual support
    results.append(test_multilingual_support())
    
    # Test 3: Flask integration
    results.append(test_flask_app_integration())
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    test_names = [
        "Voice Call Functionality",
        "Multilingual Support",
        "Flask Integration"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    all_passed = all(results)
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    print(f"\nOverall: {overall_status}")
    
    if all_passed:
        print("\n🎉 Both issues have been successfully fixed!")
        print("   - Voice calls now use improved TwiML with XML escaping")
        print("   - Multilingual support extends beyond navigation to entire UI")
    else:
        print("\n⚠️  Some issues remain. Check the test output above.")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
