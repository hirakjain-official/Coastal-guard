#!/usr/bin/env python3
"""
Direct test of Agent 2 _analyze_single_correlation function
with demo tweets, bypassing RapidAPI and Flask complexity.
"""

import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append('src')

from agents.agent2_report_analysis import ReportAnalysisAgent

# Demo report data
demo_report = {
    'title': 'Flooding in Delhi',
    'description': 'Severe flooding near Yamuna river affecting coaching centers',
    'hazard_type': 'flood',
    'severity': 'high',
    'city': 'Delhi',
    'state': 'Delhi',
    'latitude': 28.6139,
    'longitude': 77.2090
}

# Demo tweets with different structures
demo_tweets = [
    {
        'id': 'demo_1',
        'text': "Tragic flooding at Delhi's Rao IAS Coaching Centre: 2 students dead, 1 missing. Rescue operations ongoing. #DelhiFloods #RaoIAS #BreakingNews #StudentDeath #DelhiRains",
        'created_at': '2025-09-09T10:30:00Z',
        'author': 'news_reporter',
        'source': 'demo'
    },
    {
        'id': 'demo_2', 
        'text': "यमुना में बाढ़ से दिल्ली डूब गई। मेरा घर पानी में है। बचाओ! #DelhiFloods #बाढ़",
        'created_at': '2025-09-09T10:45:00Z',
        'author': 'citizen_alert',
        'source': 'demo'
    },
    {
        'id': 'demo_3',
        'text': "Water level rising rapidly in coaching centers area. Students trapped! Emergency services needed immediately. #Emergency #Delhi",
        'created_at': '2025-09-09T11:00:00Z',
        'author': 'local_witness', 
        'source': 'demo'
    }
]

async def test_agent2_analysis():
    """Test Agent 2 analysis with demo data"""
    print("🤖 Testing Agent 2 Analysis with Demo Data")
    print("=" * 50)
    
    # Initialize Agent 2
    agent = ReportAnalysisAgent()
    
    # Test each demo tweet
    for i, tweet in enumerate(demo_tweets, 1):
        print(f"\n📝 Testing Tweet {i}:")
        print(f"   Text: {tweet['text'][:60]}...")
        print(f"   Language: {'Hindi' if 'यमुना' in tweet['text'] else 'English'}")
        
        try:
            # Call the analysis function directly
            result = await agent._analyze_single_correlation(demo_report, tweet)
            
            print(f"✅ Analysis Result:")
            print(f"   🔍 Hazard Detected: {result.get('hazard_detected', 'N/A')}")
            print(f"   🌊 Hazard Type: {result.get('hazard_type', 'N/A')}")
            print(f"   ⚡ Urgency: {result.get('urgency', 'N/A')}")
            print(f"   📊 Confidence: {result.get('confidence', 'N/A')}")
            print(f"   🌍 Language: {result.get('original_language', 'N/A')}")
            print(f"   📋 Summary: {result.get('final_summary', 'N/A')[:80]}...")
            print(f"   💡 Action: {result.get('recommended_action', 'N/A')[:60]}...")
            
        except Exception as e:
            print(f"❌ Error analyzing tweet {i}: {str(e)}")
            print(f"   Using fallback analysis...")
            
            # Test fallback
            try:
                fallback_result = agent._basic_hazard_analysis(demo_report, tweet)
                print(f"🔄 Fallback Result:")
                print(f"   🌊 Hazard Type: {fallback_result.get('hazard_type', 'N/A')}")
                print(f"   ⚡ Urgency: {fallback_result.get('urgency', 'N/A')}")
                print(f"   📊 Confidence: {fallback_result.get('confidence', 'N/A')}")
            except Exception as e2:
                print(f"❌ Fallback also failed: {str(e2)}")
        
        print("-" * 40)
    
    print("\n🏁 Agent 2 Analysis Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_agent2_analysis())
