# 🐦 Twitter API Setup Guide

## 📝 How to Get Twitter API Access

### **Step 1: Apply for Twitter Developer Account**

1. **Visit**: [developer.twitter.com](https://developer.twitter.com)
2. **Sign up** with your Twitter account
3. **Apply for developer access**:
   - Select "Making a bot" or "Academic research" use case
   - Describe your project: "Social media analytics for disaster monitoring in India"
   - Explain you're building a system to detect flood/cyclone hazards from tweets
4. **Wait for approval** (usually 1-7 days)

### **Step 2: Create Twitter App**

Once approved:
1. Go to [developer.twitter.com/en/portal/dashboard](https://developer.twitter.com/en/portal/dashboard)
2. Click **"Create App"**
3. Fill in app details:
   - **Name**: "Social Media Analytics Agent"
   - **Description**: "Monitors social media for water-related hazards in India"
   - **Website**: Your website or GitHub repo

### **Step 3: Get Your API Keys**

From your app dashboard, get these keys:
- ✅ **API Key** (Consumer Key)
- ✅ **API Key Secret** (Consumer Secret) 
- ✅ **Bearer Token** (Most important for our demo)
- ✅ **Access Token** (optional)
- ✅ **Access Token Secret** (optional)

### **Step 4: Update Your .env File**

Add these to your `.env` file:

```bash
# Twitter API v2
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here  
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

## 🚀 Alternative: Use RapidAPI for Twitter (Easier)

If Twitter API approval takes too long, you can use RapidAPI:

### **Step 1: Get RapidAPI Key**
1. Go to [rapidapi.com](https://rapidapi.com)
2. Sign up for free account
3. Subscribe to "Twitter API v2" by APIToolkit or similar
4. Get your RapidAPI key

### **Step 2: Update .env**
```bash
# RapidAPI Twitter Access
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=twitter154.p.rapidapi.com
```

## 💰 API Costs Comparison

### **Twitter API v2 (Official)**
- **Free Tier**: 500K tweets/month
- **Basic**: $100/month for 10M tweets
- **Academic Research**: Free with higher limits

### **RapidAPI Twitter**
- **Free Tier**: 100-1000 requests/month
- **Paid Plans**: $10-50/month depending on usage

## 🧪 Test Your Twitter API

I'll create a simple test script for you:

```python
# test_twitter_api.py
import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

# Test Twitter API connection
bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

if bearer_token:
    client = tweepy.Client(bearer_token=bearer_token)
    
    try:
        # Search for recent tweets about flooding in India
        tweets = client.search_recent_tweets(
            query='flood India lang:en -is:retweet',
            max_results=10,
            tweet_fields=['created_at', 'public_metrics', 'geo']
        )
        
        print("✅ Twitter API connection successful!")
        print(f"Found {len(tweets.data)} recent tweets about flooding in India:")
        
        for tweet in tweets.data:
            print(f"- {tweet.text[:100]}...")
            
    except Exception as e:
        print(f"❌ Twitter API error: {e}")
else:
    print("❌ Twitter Bearer Token not found in .env file")
```

## 🔧 Demo Modes

### **Mode 1: Full Twitter Integration**
```bash
# With Twitter API keys configured
python demo/enhanced_demo.py
```
- Real social media data ingestion
- Live tweet analysis
- Actual hotspot detection

### **Mode 2: AI-Only Demo**  
```bash
# Without Twitter API (current setup)
python demo/enhanced_demo.py
```
- Sample data processing
- Real AI analysis via OpenRouter
- Mock social media posts

### **Mode 3: Offline Demo**
```bash
# No APIs needed
python demo/simple_demo.py  
```
- Sample data + mock AI
- Full UI functionality
- Perfect for presentations

## 📊 Recommended Setup Priority

1. **✅ OpenRouter API** (You have this!) - Real AI analysis
2. **🔄 Twitter API** (Optional) - Real social media data  
3. **🔄 RapidAPI** (Alternative) - Easier Twitter access

## 🎯 Current Status

**You already have the most important part working!**

- ✅ **Real AI Analysis**: DeepSeek via OpenRouter
- ✅ **Interactive Demo**: Full UI with real hazard detection
- ✅ **Multi-language**: Hindi, Tamil, Telugu support
- 🔄 **Real Twitter Data**: Add when you get API access

Your demo is already impressive and functional with just the OpenRouter integration!

## 🚀 Next Steps

1. **For now**: Continue using your current setup - it's already great!
2. **This week**: Apply for Twitter Developer account
3. **Once approved**: Add Twitter keys to .env and get real social media data
4. **Alternative**: Try RapidAPI for quicker Twitter access

Would you like me to help you apply for Twitter API access or set up RapidAPI integration?
