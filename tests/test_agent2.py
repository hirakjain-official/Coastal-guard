#!/usr/bin/env python3
"""
Simple test script for Agent 2
"""
import sys
import asyncio
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

async def test_agent2():
    print("🚀 Testing Agent 2...")
    
    try:
        from agents.agent2_report_analysis import process_user_report
        print("✅ Import successful")
        
        # Sample report data
        report_data = {
            'id': 'test-001',
            'title': 'Coastal flooding on Marine Drive Mumbai',
            'description': 'Heavy flooding observed on Marine Drive due to high tides. Water level reached road surface.',
            'hazard_type': 'coastal_flooding',
            'severity': 'high',
            'latitude': 18.9220,
            'longitude': 72.8267,
            'location_name': 'Marine Drive, Mumbai',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'created_at': '2025-09-09T04:00:00Z'
        }
        
        print("📝 Processing report...")
        result = await process_user_report(report_data)
        
        print("\n✅ Agent 2 Results:")
        print(f"📋 Report ID: {result.get('id')}")
        print(f"🎯 Correlation Confidence: {result.get('correlation_confidence', 0)*100:.1f}%")
        
        # Show generated keywords
        if 'generated_keywords' in result:
            keywords = result['generated_keywords']
            print(f"🔍 Primary Keywords: {keywords.get('primary_keywords', [])}")
            print(f"📍 Location Keywords: {keywords.get('location_keywords', [])}")
            print(f"#️⃣  Hashtags: {keywords.get('hashtag_suggestions', [])}")
        
        # Show correlations
        if 'social_media_correlations' in result:
            correlations = result['social_media_correlations']
            print(f"📱 Social Media Matches Found: {len(correlations)}")
            
            for i, corr in enumerate(correlations[:3], 1):  # Show first 3
                score = corr.get('correlation_score', 0) * 100
                preview = corr.get('post_text_preview', 'No preview')
                print(f"   {i}. Score: {score:.1f}% - \"{preview[:80]}...\"")
        
        print("\n🎉 Agent 2 test completed successfully!")
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_agent2())
    if result:
        print("\n✅ Agent 2 is working correctly!")
    else:
        print("\n💥 Agent 2 test failed!")
