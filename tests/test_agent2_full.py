#!/usr/bin/env python3
"""
Test Agent 2 with full API functionality
"""
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables first
load_dotenv()

# Add src to path  
sys.path.append(str(Path(__file__).parent / 'src'))

async def test_agent2_full():
    print("🚀 Testing Agent 2 (Full Mode with API Keys)...")
    
    # Check API keys
    rapidapi = '✅ Set' if os.getenv('RAPIDAPI_KEY') else '❌ Not set'
    openrouter = '✅ Set' if os.getenv('OPENROUTER_API_KEY') else '❌ Not set'
    twitter = '✅ Set' if os.getenv('TWITTER_BEARER_TOKEN') else '❌ Not set'
    
    print(f"🔑 API Keys Status:")
    print(f"   RAPIDAPI_KEY: {rapidapi}")
    print(f"   OPENROUTER_API_KEY: {openrouter}")
    print(f"   TWITTER_BEARER_TOKEN: {twitter}")
    
    try:
        from agents.agent2_report_analysis import process_user_report
        print("✅ Import successful")
        
        # Sample report data
        report_data = {
            'id': 'test-001',
            'title': 'Coastal flooding on Marine Drive Mumbai',
            'description': 'Heavy flooding observed on Marine Drive due to high tides. Water level reached road surface causing traffic disruption.',
            'hazard_type': 'coastal_flooding',
            'severity': 'high',
            'latitude': 18.9220,
            'longitude': 72.8267,
            'location_name': 'Marine Drive, Mumbai',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'created_at': '2025-09-09T04:00:00Z'
        }
        
        print("\n📝 Processing report with full Agent 2 pipeline...")
        result = await process_user_report(report_data)
        
        print("\n✅ Agent 2 Full Results:")
        print(f"📋 Report ID: {result.get('id')}")
        print(f"🎯 Correlation Confidence: {result.get('correlation_confidence', 0)*100:.1f}%")
        
        # Show generated keywords
        if 'generated_keywords' in result:
            keywords = result['generated_keywords']
            print(f"\n🔍 Generated Keywords:")
            print(f"   Primary: {keywords.get('primary_keywords', [])}")
            print(f"   Location: {keywords.get('location_keywords', [])}")  
            print(f"   Hashtags: {keywords.get('hashtag_suggestions', [])}")
            print(f"   Search Queries: {keywords.get('combined_queries', [])}")
        
        # Show correlations
        if 'social_media_correlations' in result:
            correlations = result['social_media_correlations']
            print(f"\n📱 Social Media Analysis:")
            print(f"   Total Matches Found: {len(correlations)}")
            
            for i, corr in enumerate(correlations[:3], 1):  # Show first 3
                score = corr.get('correlation_score', 0) * 100
                conf = corr.get('confidence', 0) * 100
                preview = corr.get('post_text_preview', 'No preview')
                elements = corr.get('matching_elements', [])
                
                print(f"\n   📊 Correlation {i}:")
                print(f"      Score: {score:.1f}%")
                print(f"      Confidence: {conf:.1f}%")  
                print(f"      Matching: {', '.join(elements)}")
                print(f"      Post: \"{preview[:60]}...\"")
        
        # Show processing errors if any
        if 'processing_error' in result:
            print(f"\n⚠️  Processing Error: {result['processing_error']}")
        
        print(f"\n🎉 Agent 2 Full Test Completed!")
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    success = asyncio.run(test_agent2_full())
    if success:
        print("\n🎉 Agent 2 is fully operational!")
        print("🔥 Social media correlation analysis working!")
    else:
        print("\n💥 Agent 2 test failed!")
