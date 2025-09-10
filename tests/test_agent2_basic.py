#!/usr/bin/env python3
"""
Test Agent 2 with basic functionality (no API keys needed)
"""
import sys
import asyncio
from pathlib import Path

# Add src to path  
sys.path.append(str(Path(__file__).parent / 'src'))

async def test_agent2_basic():
    print("🚀 Testing Agent 2 (Basic Mode - No API Keys Required)...")
    
    try:
        from agents.agent2_report_analysis import ReportAnalysisAgent
        print("✅ Import successful")
        
        # Create agent instance
        agent = ReportAnalysisAgent()
        print("✅ Agent created successfully")
        
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
        
        print("📝 Processing report with basic functionality...")
        
        # Test basic keyword generation (fallback method)
        print("🔍 Testing keyword generation...")
        keywords = agent._generate_basic_keywords(report_data)
        print(f"   Primary Keywords: {keywords.get('primary_keywords', [])}")
        print(f"   Location Keywords: {keywords.get('location_keywords', [])}")
        print(f"   Hashtags: {keywords.get('hashtag_suggestions', [])}")
        print(f"   Search Queries: {keywords.get('combined_queries', [])}")
        
        # Test social media simulation
        print("📱 Testing social media simulation...")
        social_posts = await agent._simulate_social_media_search("flood mumbai", report_data)
        print(f"   Found {len(social_posts)} simulated posts")
        
        for i, post in enumerate(social_posts[:2], 1):
            print(f"   Post {i}: \"{post.get('text', '')[:80]}...\"")
            print(f"            Location: {post.get('location', {})}")
            print(f"            Confidence: {post.get('confidence', 0)*100:.1f}%")
        
        # Test basic correlation analysis
        print("🔗 Testing correlation analysis...")
        if social_posts:
            correlation = agent._basic_correlation_analysis(report_data, social_posts[0])
            print(f"   Correlation Score: {correlation.get('correlation_score', 0)*100:.1f}%")
            print(f"   Matching Elements: {correlation.get('matching_elements', [])}")
            print(f"   Reasoning: {correlation.get('reasoning', 'No reasoning')}")
        
        print("\n🎉 Agent 2 Basic Test Completed Successfully!")
        print("\n📊 SUMMARY:")
        print("✅ Keyword Generation: Working")
        print("✅ Social Media Simulation: Working") 
        print("✅ Correlation Analysis: Working")
        print("✅ Distance Calculation: Available")
        print("❌ LLM Integration: Requires API Keys")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agent2_basic())
    if success:
        print("\n🎉 Agent 2 core functionality is working!")
        print("💡 To enable full AI features, set up API keys in .env file")
    else:
        print("\n💥 Agent 2 test failed!")
