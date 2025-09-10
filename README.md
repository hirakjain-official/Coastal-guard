# Coastal Hazard Management System

A comprehensive real-time coastal hazard monitoring and report management system that combines citizen reporting with AI-powered social media intelligence to detect and respond to water-related hazards across India's coastal regions.

## 🌊 Overview

This system provides a **dual-portal architecture** with integrated AI analysis:

- **Citizen Portal** - Submit hazard reports with location, description, and disaster type
- **Admin Dashboard** - Monitor reports, view analytics, and manage system configuration
- **AI Intelligence (Agent 2)** - Real-time Twitter analysis using DeepSeek LLM for hazard detection
- **Interactive Maps** - Live visualization of hazard reports and social media alerts
- **Multilingual Support** - English + Hindi, Tamil, Telugu, Malayalam, Bengali, Odia, Gujarati
- **Real-time Processing** - Immediate report analysis and social media correlation

### Key Features

✅ **Dual Web Interface** - Citizen reporting portal + Admin dashboard with live maps
✅ **AI-Powered Intelligence** - DeepSeek LLM analysis with multilingual hazard detection
✅ **Real-time Twitter Integration** - RapidAPI Twitter search with location-based filtering
✅ **Comprehensive Terminal Output** - Detailed logs showing tweets and AI analysis results
✅ **Interactive Maps** - Leaflet-based visualization with hazard markers and geolocation
✅ **Persistent Data Storage** - JSON-based report storage with automatic backup
✅ **Multilingual Processing** - Support for English + 8 Indian regional languages
✅ **Configurable Scheduling** - Adjustable Agent 1 intervals via admin controls
✅ **Fallback Analysis** - Keyword-based hazard detection when LLM is unavailable

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Flask web framework
- API Keys:
  - RapidAPI Key (for Twitter search)
  - OpenRouter API Key (for DeepSeek LLM)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd social-media-analytics-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask requests python-dotenv loguru asyncio aiohttp
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```bash
   # API Configuration
   RAPIDAPI_KEY=your_rapidapi_key_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   
   # Optional: Flask Configuration
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

5. **Run the application**
   ```bash
   # Start the Flask web application
   python app.py
   
   # Access the system:
   # Citizen Portal: http://localhost:5000
   # Admin Dashboard: http://localhost:5000/admin
   ```

📊 System Architecture

### Dual-Portal Web Application

```
┌────────────────────┐    ┌────────────────────┐
│  👥 Citizen Portal   │    │  📊 Admin Dashboard  │
│  - Report Submission  │    │  - View All Reports   │
│  - Interactive Map    │    │  - AI Intelligence    │
│  - Real-time Alerts   │    │  - System Controls    │
└────────────────────┘    └────────────────────┘
             │                           │
             └───────────┬───────────┘
                        │
        ┌──────────────────────────────┐
        │      🤖 AI AGENT 2         │
        │   Social Media Intelligence  │
        └──────────────────────────────┘
                        │
        ┌───────────┬──────────────────┐
        │           │               │
  ┌─────────────────┐ ┌─────────────────┐
  │ 📡 RapidAPI     │ │ 🧠 DeepSeek LLM  │
  │ Twitter Search  │ │ Hazard Analysis │
  └─────────────────┘ └─────────────────┘
```

### System Workflow

#### Citizen Report Processing
1. **Report Submission** via citizen portal:
   - Location (city, state, coordinates)
   - Hazard description (multilingual support)
   - Disaster type selection (flood, tsunami, etc.)
2. **Immediate Storage** in JSON format with timestamp
3. **Agent 2 Trigger** - Automatic social media intelligence analysis
4. **Map Visualization** - Real-time marker placement

#### AI Intelligence Processing (Agent 2)
1. **Twitter Search** using RapidAPI:
   - Location-based filtering (50km radius)
   - Hazard-related keyword matching
   - Recent posts (last hour)
2. **DeepSeek LLM Analysis** for each tweet:
   - Multilingual hazard detection
   - Urgency assessment (Low/Medium/High)
   - Confidence scoring (0.0-1.0)
   - Historical pattern analysis
   - Seasonal risk evaluation
3. **Terminal Output** with detailed results:
   - Raw tweet content display
   - AI analysis breakdown
   - Correlation scoring
4. **Admin Dashboard Integration** - Results display with urgency badges

#### Fallback Processing
- **Keyword-based Analysis** when LLM unavailable
- **Local Storage** ensures no data loss
- **Error Handling** with comprehensive logging


## 🧪 Development

### Project Structure
```
coastal-hazard-management-system/
├── app.py      # Main Flask application
├── src/
│   └── agents/
│       └── agent2_report_analysis.py  # AI-powered social media analysis
├── templates/
│   ├── citizen_portal.html     # Citizen report submission interface
│   ├── admin_dashboard.html    # Admin monitoring interface
│   └── base.html              # Common template base
├── static/
│   ├── css/                   # Styling
│   └── js/                    # JavaScript for maps & interactions
├── data/
│   └── reports.json           # Persistent report storage
├── test_agent2_analysis.py  # Agent 2 testing script
├── .env                    # Environment variables (API keys)
├── README.md               # This documentation
└── requirements.txt        # Python dependencies
```

### Adding New Languages

1. Update `config/regional_config.yaml`:
   ```yaml
   hazard_keywords:
     new_language:
       flood: ["flood_word1", "flood_word2"]
       tsunami: ["tsunami_word1", "tsunami_word2"]
   ```

2. Update location aliases for city/state names in the new language

3. Test with sample posts in that language

### Adding New Hazard Types

1. Update AI analysis prompts in `src/modules/ai_analysis.py`
2. Add keywords to regional configuration
3. Update validation logic and alert templates
4. Test classification accuracy

### Testing

```bash
# Run unit tests
pytest tests/

# Test specific module
pytest tests/test_preprocessing.py

# Test with coverage
pytest --cov=src tests/
```

## 📈 Monitoring & Metrics

### Key Performance Indicators

- **Data Ingestion Rate**: Posts fetched per hour
- **Processing Latency**: Time from fetch to analysis completion  
- **Classification Accuracy**: AI model performance on hazard detection
- **Hotspot Detection Rate**: Geographic clusters identified per batch
- **Validation Response Time**: Analyst review turnaround
- **Alert Delivery Success**: Notification system reliability

### Log Analysis

```bash
# Monitor processing performance
grep "batch processing completed" logs/social_analytics.log

# Check API errors
grep "ERROR" logs/social_analytics.log | grep "API"

# View hotspot detections
grep "Detected.*hotspots" logs/social_analytics.log
```

## 🔮 Phase 2 - Future Enhancements

### Near Real-time Streaming
- Migrate from hourly batches to 15-minute or streaming processing
- Implement WebSocket connections for live data feeds
- Add event-driven architecture with message queues

### Enhanced AI Capabilities
- Fine-tune DeepSeek models on validated Indian hazard data
- Add image/video analysis for visual hazard detection
- Implement sentiment analysis for urgency assessment

### Advanced Analytics
- Predictive modeling for hazard forecasting
- Social network analysis for information spread tracking
- Integration with weather data and satellite imagery

### Expanded Coverage
- Support for additional social platforms (Facebook, Instagram, WhatsApp)
- Integration with news media and government sources
- Citizen reporting mobile application

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Built with ❤️ for disaster preparedness and community safety in India** 🇮🇳
