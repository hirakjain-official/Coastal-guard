# Social Media Analytics Agent

A comprehensive social media monitoring system designed to detect and analyze water-related hazards (floods, tsunamis, high waves, cyclones) across India through real-time social media analysis.

## 🌊 Overview

This system implements a **Phase 1 - Hourly Batch Processing** workflow that:

- **Fetches** social media posts every hour from Twitter/X using RapidAPI and official Twitter API
- **Processes** posts through deduplication, cleaning, and location inference  
- **Analyzes** content using DeepSeek AI for hazard classification and urgency assessment
- **Aggregates** results to detect geographical hotspots of hazard activity
- **Validates** findings through an analyst dashboard workflow
- **Alerts** relevant authorities and citizen applications when hazards are confirmed

### Key Features

✅ **Multi-source Data Ingestion** - Twitter/X via RapidAPI and official API  
✅ **Multi-language Support** - English + 11 Indian regional languages  
✅ **AI-Powered Classification** - DeepSeek API for hazard type and urgency detection  
✅ **Geospatial Hotspot Detection** - Cluster analysis for identifying affected areas  
✅ **Human-in-the-Loop Validation** - Analyst dashboard for confirmation  
✅ **Automated Alerting** - Integration with official dashboards and citizen apps  
✅ **India-Focused** - Optimized for Indian geography, languages, and hazard patterns  

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+ 
- Redis 6+
- API Keys for Twitter/X and DeepSeek

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
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys and database credentials
   ```

5. **Initialize database** (optional - will use file storage by default)
   ```bash
   # Set up PostgreSQL and Redis if using database storage
   # Update DATABASE_URL and REDIS_URL in .env
   ```

6. **Run the application**
   ```bash
   # Test single batch
   python src/main.py --test
   
   # Start scheduled hourly processing
   python src/main.py
   ```

## 📊 Architecture Overview

### Phase 1 - Hourly Batch Workflow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   🕐 Scheduler   │───▶│  📥 Data Ingest  │───▶│ 🧹 Preprocessing │
│   (Every hour)  │    │ Twitter/X APIs   │    │ Clean & Dedupe  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                          │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ 🚨 Alerts       │◀───│ ✅ Validation    │◀───│ 🤖 AI Analysis  │
│ Official/Citizen│    │ Analyst Review   │    │ DeepSeek API    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                          │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ 💾 Storage      │◀───│ 📍 Aggregation   │◀───│                 │
│ Database/Files  │    │ Hotspot Detection│    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Data Flow

1. **Scheduler** triggers every 60 minutes
2. **Data Ingestion** fetches posts from last hour using:
   - Twitter/X RapidAPI with India geo-filter + hazard keywords
   - Official Twitter API v2 with comprehensive search queries
3. **Preprocessing** performs:
   - Deduplication and retweet removal
   - Text cleaning and normalization  
   - Language detection (English + regional languages)
   - Location inference from geotags and text content
4. **AI Analysis** classifies each post:
   - Relevance: hazard vs non-hazard
   - Hazard Type: Flood, Tsunami, High Wave, Storm Surge, Cyclone, Other
   - Urgency: Low, Medium, High
   - Confidence Score: 0.0 to 1.0
5. **Aggregation** detects hotspots:
   - Groups posts by location + hazard type
   - Flags areas with ≥20 high-confidence posts in 10km radius
6. **Validation** sends to analyst dashboard:
   - Human review of detected hotspots
   - Confirm/reject decisions feed back into system
7. **Alerts** notify relevant channels:
   - Official emergency dashboards
   - Citizen mobile applications
   - Geographic push notifications

## 🛠️ Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/social_analytics
REDIS_URL=redis://localhost:6379/0

# API Keys
TWITTER_API_KEY=your_key
TWITTER_BEARER_TOKEN=your_token
RAPIDAPI_KEY=your_key
DEEPSEEK_API_KEY=your_key

# Application Settings
SCHEDULER_INTERVAL=3600  # 1 hour
CONFIDENCE_THRESHOLD=0.75
HOTSPOT_POST_THRESHOLD=20
HOTSPOT_RADIUS_KM=10

# Regional Settings  
SUPPORTED_LANGUAGES=en,hi,ta,te,bn,mr,gu,kn,ml,or,pa,as
TIMEZONE=Asia/Kolkata
```

### Regional Configuration (config/regional_config.yaml)

Contains India-specific:
- 🗺️ Geographic boundaries and coastal cities
- 🗣️ Multi-language hazard keywords  
- 📍 Location aliases and variations
- 🌧️ Seasonal risk factors
- ⚡ Priority alert regions

## 📝 Usage Examples

### Running Single Test Batch
```bash
python src/main.py --test
```

### Starting Scheduled Processing  
```bash
python src/main.py
```

### Monitoring Logs
```bash
tail -f logs/social_analytics.log
```

### Checking Stored Results
```bash
# View processed batch files
ls data/processed/

# Examine specific batch
cat data/processed/batch_[id].json | jq .
```

## 🧪 Development

### Project Structure
```
social-media-analytics-agent/
├── src/
│   ├── main.py                 # Application entry point
│   └── modules/
│       ├── scheduler.py        # Job scheduling  
│       ├── data_ingestion.py   # Social media API clients
│       ├── preprocessing.py    # Text cleaning & location inference
│       ├── ai_analysis.py      # DeepSeek hazard classification
│       ├── aggregation.py      # Hotspot detection
│       ├── validation.py       # Analyst dashboard integration
│       ├── alerts.py          # Notification systems
│       └── storage.py         # Database operations
├── config/
│   ├── regional_config.yaml   # India-specific configuration
│   └── database.yaml         # Database schema & settings
├── data/
│   ├── raw/                  # Ingested posts
│   ├── processed/            # Batch processing results
│   └── alerts/              # Generated alerts
├── logs/                    # Application logs
├── tests/                  # Unit tests
└── scripts/               # Utility scripts
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

## 🆘 Support & Contact

- **Issues**: Create a GitHub issue for bugs or feature requests
- **Documentation**: Check the `/docs` folder for detailed API documentation  
- **Community**: Join our Slack channel for discussions

---

**Built with ❤️ for disaster preparedness and community safety in India** 🇮🇳
