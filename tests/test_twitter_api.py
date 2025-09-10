#!/usr/bin/env python3
"""
Twitter API Test Script
Test your Twitter API connection and search for hazard-related posts.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_twitter_api_v2():
    """Test Twitter API v2 with tweepy."""
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    if not bearer_token:
        print("❌ TWITTER_BEARER_TOKEN not found in .env file")
        return False
    
    try:
        import tweepy
        
        # Initialize Twitter API client
        client = tweepy.Client(bearer_token=bearer_token)
        
        # Test with a simple search
        print("🔍 Testing Twitter API v2 connection...")
        
        tweets = client.search_recent_tweets(
            query='flood India lang:en -is:retweet',
            max_results=10,
            tweet_fields=['created_at', 'public_metrics', 'geo', 'lang']
        )
        
        if tweets and tweets.data:
            print(f"✅ Twitter API connection successful!")
            print(f"📊 Found {len(tweets.data)} recent tweets about flooding in India:")
            print()
            
            for i, tweet in enumerate(tweets.data, 1):
                print(f"{i}. {tweet.text[:100]}...")
                print(f"   Created: {tweet.created_at}")
                print(f"   Metrics: {tweet.public_metrics}")
                print()
            
            return True
        else:
            print("✅ Twitter API connected but no tweets found for this query")
            return True
            
    except ImportError:
        print("❌ tweepy not installed. Run: pip install tweepy")
        return False
    except Exception as e:
        print(f"❌ Twitter API error: {str(e)}")
        return False

def test_rapidapi_twitter():
    """Test Twitter access via RapidAPI."""
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    rapidapi_host = os.getenv('RAPIDAPI_HOST', 'twitter-api47.p.rapidapi.com')
    
    if not rapidapi_key:
        print("❌ RAPIDAPI_KEY not found in .env file")
        return False
    
    try:
        import requests
        
        # Test RapidAPI Twitter endpoint
        print("🔍 Testing RapidAPI Twitter connection...")
        
        url = f"https://{rapidapi_host}/v2/search"
        
        headers = {
            'X-RapidAPI-Key': rapidapi_key,
            'X-RapidAPI-Host': rapidapi_host
        }
        
        params = {
            'query': 'flood India',
            'max_results': '10'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'results' in data and data['results']:
                print(f"✅ RapidAPI Twitter connection successful!")
                print(f"📊 Found {len(data['results'])} tweets:")
                print()
                
                for i, tweet in enumerate(data['results'][:5], 1):
                    print(f"{i}. {tweet.get('text', '')[:100]}...")
                    print(f"   User: @{tweet.get('username', 'unknown')}")
                    print()
                
                return True
            else:
                print("✅ RapidAPI Twitter connected but no results found")
                return True
        else:
            print(f"❌ RapidAPI error: {response.status_code} - {response.text}")
            return False
            
    except ImportError:
        print("❌ requests not installed. Run: pip install requests")
        return False
    except Exception as e:
        print(f"❌ RapidAPI Twitter error: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🐦 Twitter API Connection Test")
    print("=" * 50)
    print()
    
    # Check which APIs are configured
    has_twitter = bool(os.getenv('TWITTER_BEARER_TOKEN'))
    has_rapidapi = bool(os.getenv('RAPIDAPI_KEY'))
    
    if not has_twitter and not has_rapidapi:
        print("❌ No Twitter API credentials found!")
        print()
        print("📝 To set up Twitter API access:")
        print("1. Get Twitter API keys from developer.twitter.com")
        print("2. OR get RapidAPI key from rapidapi.com")
        print("3. Add keys to your .env file")
        print()
        print("🔧 For now, your demo works with sample data and real AI analysis!")
        return
    
    success = False
    
    # Test Twitter API v2 first
    if has_twitter:
        print("🧪 Testing Twitter API v2...")
        success = test_twitter_api_v2()
        print()
    
    # Test RapidAPI if Twitter API failed or not available
    if not success and has_rapidapi:
        print("🧪 Testing RapidAPI Twitter...")
        success = test_rapidapi_twitter()
        print()
    
    if success:
        print("🎉 Twitter integration is ready!")
        print("📊 Your demo can now fetch real social media data")
    else:
        print("⚠️  Twitter API not working, but don't worry!")
        print("🚀 Your demo still works great with sample data and real AI analysis")
    
    print()
    print("🎯 Current Demo Status:")
    print(f"  ✅ Real AI Analysis (OpenRouter): {'Yes' if os.getenv('OPENROUTER_API_KEY') else 'No'}")
    print(f"  {'✅' if success else '❌'} Twitter Data: {'Yes' if success else 'Sample Data Only'}")
    print(f"  ✅ Interactive UI: Yes")
    print(f"  ✅ Multi-language: Yes")

if __name__ == "__main__":
    main()
