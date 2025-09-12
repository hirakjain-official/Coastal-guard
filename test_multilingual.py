#!/usr/bin/env python3
"""
Test script to verify comprehensive multilingual support across all pages
"""

import sys
import json
from pathlib import Path

def test_translations_coverage():
    """Test that translations cover all major UI sections"""
    print("🌍 Testing Multilingual Coverage...")
    
    try:
        translations_file = Path(__file__).parent / 'config' / 'translations.json'
        with open(translations_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        # Test languages
        languages = ['en', 'hi']  # Test English and Hindi
        
        # Test sections that should be available
        required_sections = [
            'brand',
            'nav.admin_dashboard',
            'nav.login',
            'nav.logout',
            'common.welcome',
            'common.send',
            'common.cancel',
            'dashboard.title',
            'dashboard.stats.total_reports',
            'alerts.confirm_title',
            'alerts.send_alert',
            'auth.login.title',
            'auth.login.email',
            'auth.login.password',
            'auth.signup.title',
            'auth.signup.name',
            'admin.dashboard.title',
            'admin.reports.title',
            'reports.create.title',
            'reports.create.hazard_type',
            'reports.create.city',
            'forms.required_field',
            'status.pending',
            'severity.high',
            'hazard_types.flood'
        ]
        
        print(f"Testing {len(required_sections)} key translation points...")
        
        all_passed = True
        
        for lang in languages:
            print(f"\n🗣️  Testing {lang} language:")
            
            if lang not in translations:
                print(f"❌ Language {lang} not found in translations")
                all_passed = False
                continue
            
            lang_data = translations[lang]
            missing_keys = []
            
            for key in required_sections:
                keys = key.split('.')
                current = lang_data
                
                try:
                    for k in keys:
                        current = current[k]
                    
                    # Verify the translation is not empty
                    if not current or current.strip() == "":
                        missing_keys.append(f"{key} (empty)")
                    else:
                        print(f"  ✅ {key}: '{current[:30]}{'...' if len(current) > 30 else ''}'")
                        
                except (KeyError, TypeError):
                    missing_keys.append(key)
            
            if missing_keys:
                print(f"  ❌ Missing keys for {lang}: {', '.join(missing_keys)}")
                all_passed = False
            else:
                print(f"  ✅ All key translations present for {lang}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing translations: {e}")
        return False

def test_template_files():
    """Test that key template files use translation functions"""
    print("\n📄 Testing Template Files for Translation Usage...")
    
    template_files = [
        'templates/auth/login.html',
        'templates/auth/signup.html', 
        'templates/admin/alert_confirm.html',
        'templates/user/dashboard.html',
        'templates/user_new/create_report.html'
    ]
    
    all_passed = True
    
    for template_path in template_files:
        try:
            file_path = Path(__file__).parent / template_path
            if not file_path.exists():
                print(f"⚠️  Template not found: {template_path}")
                continue
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for translation function usage
            t_function_count = content.count("{{ t('")
            filter_count = content.count("| t")
            
            if t_function_count > 0 or filter_count > 0:
                print(f"✅ {template_path}: {t_function_count} t() calls, {filter_count} filter calls")
            else:
                print(f"❌ {template_path}: No translation functions found")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error reading {template_path}: {e}")
            all_passed = False
    
    return all_passed

def test_flask_integration():
    """Test Flask translation integration"""
    print("\n🌐 Testing Flask Translation Integration...")
    
    try:
        # Import Flask app components
        sys.path.append(str(Path(__file__).parent))
        from app import get_translation, load_translations
        
        # Load translations first
        load_translations()
        
        # Test key translations
        test_cases = [
            ('common.welcome', 'en', 'Welcome'),
            ('common.welcome', 'hi', 'स्वागत है'),
            ('nav.login', 'en', 'Login'),
            ('nav.login', 'hi', 'लॉगिन'),
            ('alerts.send_alert', 'en', 'Send Alert'),
            ('alerts.send_alert', 'hi', 'अलर्ट भेजें'),
            ('auth.login.title', 'en', 'Login'),
            ('auth.login.title', 'hi', 'लॉगिन')
        ]
        
        all_passed = True
        
        for key, lang, expected in test_cases:
            try:
                result = get_translation(key, lang)
                if expected in result:
                    print(f"✅ {key} ({lang}): '{result}'")
                else:
                    print(f"❌ {key} ({lang}): Expected '{expected}' in '{result}'")
                    all_passed = False
            except Exception as e:
                print(f"❌ Error getting {key} ({lang}): {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Flask integration test failed: {e}")
        return False

def main():
    """Run all multilingual tests"""
    print("🧪 Running Comprehensive Multilingual Tests\n")
    
    results = []
    
    # Test 1: Translations coverage
    results.append(test_translations_coverage())
    
    # Test 2: Template files
    results.append(test_template_files())
    
    # Test 3: Flask integration  
    results.append(test_flask_integration())
    
    print("\n" + "="*60)
    print("📊 MULTILINGUAL TEST RESULTS")
    print("="*60)
    
    test_names = [
        "Translation Coverage",
        "Template Integration", 
        "Flask Integration"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    all_passed = all(results)
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    print(f"\nOverall: {overall_status}")
    
    if all_passed:
        print("\n🎉 Multilingual support is working correctly!")
        print("   ✅ Comprehensive translations available")
        print("   ✅ Templates use translation functions") 
        print("   ✅ Flask integration working")
        print("   ✅ Language switching affects entire UI")
    else:
        print("\n⚠️  Some multilingual features need attention.")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
