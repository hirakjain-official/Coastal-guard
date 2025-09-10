# 🚀 Quick Setup Guide

## 📝 How to Run the Social Media Analytics Demo

### **Step 1: Get Your OpenRouter API Key**

1. **Go to OpenRouter**: Visit [openrouter.ai](https://openrouter.ai)
2. **Create Account**: Sign up for a free account
3. **Get API Key**: 
   - Go to your dashboard
   - Click on "API Keys" 
   - Create a new key
   - Copy the key (starts with `sk-or-v1-...`)

### **Step 2: Update Your .env File**

Open the `.env` file and add your OpenRouter API key:

```bash
# DeepSeek via OpenRouter
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
DEEPSEEK_MODEL=deepseek/deepseek-chat
DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1
```

**💡 Important:** Replace `sk-or-v1-your-actual-key-here` with your real API key!

### **Step 3: Run the Enhanced Demo**

```bash
# Make sure you're in the project directory
cd C:\Users\user\social-media-analytics-agent

# Run the enhanced demo with real AI
python demo/enhanced_demo.py
```

### **Step 4: Open Your Browser**

Go to: **http://localhost:5000**

## 🎯 What You Can Test

### **1. Single Post Analysis**
- Click "Test Single Post" 
- Try these examples:
  - `Heavy flooding in Mumbai! Streets completely waterlogged. Need immediate help!`
  - `Just had great coffee in Delhi. Beautiful weather today!`
  - `चेन्नई में बाढ़ का खतरा। सभी सावधान रहें।`

### **2. Batch Processing**
- Click "Run Batch Test"
- Watch real-time AI analysis of sample posts
- View detected hotspots and confidence scores

### **3. Configuration Check**
- Go to Configuration page
- Verify your API key status
- Check system settings

## 💰 API Costs

- **OpenRouter DeepSeek**: Very cheap (~$0.0001 per 1K tokens)
- **Demo Usage**: Should cost less than $0.01 for extensive testing
- **Free Credits**: OpenRouter gives free credits for new users

## 🔧 Alternative: Run Without API

If you don't want to set up APIs yet, you can still run the basic demo:

```bash
python demo/simple_demo.py
```

This uses mock AI analysis but shows the full interface.

## 📊 Features You'll See

✅ **Real AI Analysis** - DeepSeek classifies posts for hazards  
✅ **Multi-language Support** - Works with Hindi, Tamil, Telugu text  
✅ **Confidence Scoring** - AI provides confidence levels (0.0-1.0)  
✅ **Urgency Detection** - Low/Medium/High urgency classification  
✅ **Hotspot Detection** - Groups related hazard posts by location  
✅ **Interactive Dashboard** - Real-time processing status  

## 🛠️ Troubleshooting

### **Port Already in Use**
```bash
# Find and kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

### **Module Import Errors**
```bash
pip install Flask aiohttp python-dotenv loguru
```

### **API Key Not Working**
1. Check your `.env` file has the correct key
2. Verify the key starts with `sk-or-v1-`
3. Make sure you have credits in your OpenRouter account

## 🎉 That's It!

Your Social Media Analytics Agent demo is ready to test real AI-powered hazard detection! 

**Next Steps:**
- Test different types of posts
- Experiment with multi-language content  
- Try batch processing to see hotspot detection
- Check the detailed results page

---

🇮🇳 **Built for disaster preparedness and community safety in India**
