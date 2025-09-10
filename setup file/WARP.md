# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Common Development Commands

### Environment Setup
```bash
# Initial setup
python scripts/setup.py

# Create virtual environment and install dependencies
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Set up environment variables
cp .env.template .env
# Edit .env with your API keys and configuration
```

### Running the Application
```bash
# Run single test batch (recommended for development)
python src/main.py --test

# Start scheduled hourly processing
python src/main.py

# Monitor logs in real-time
tail -f logs/social_analytics.log
```

### Development and Testing
```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/test_preprocessing.py

# Run tests with coverage
pytest --cov=src tests/

# Code formatting (if configured)
black src/
flake8 src/

# Check data processing results
ls data/processed/
cat data/processed/batch_*.json | jq .
```

### Database Operations (if using PostgreSQL)
```bash
# The application will use file storage by default
# For database setup, ensure PostgreSQL and Redis are running
# Update DATABASE_URL and REDIS_URL in .env file
```

## Architecture Overview

This is a **social media analytics system** for detecting water-related hazards (floods, tsunamis, cyclones, high waves) across India through AI-powered analysis of social media posts.

### Core Workflow (Phase 1 - Hourly Batch Processing)

The system follows a **7-step pipeline** that runs every hour:

1. **Scheduler** → Triggers batch processing every 60 minutes
2. **Data Ingestion** → Fetches posts from Twitter/X APIs (RapidAPI + official Twitter API v2)
3. **Preprocessing** → Deduplication, text cleaning, location inference
4. **AI Analysis** → DeepSeek API classifies posts for hazard type, urgency, confidence
5. **Aggregation** → Groups posts geographically to detect hotspots (≥20 posts in 10km radius)
6. **Validation** → Sends hotspots to analyst dashboard for human review
7. **Alerts** → Notifies authorities and citizen apps for confirmed hazards

### Key Components

**Main Application (`src/main.py`)**
- Entry point orchestrating the entire workflow
- Service initialization and coordination
- Error handling and logging setup

**Service Modules (`src/modules/`)**
- `data_ingestion.py` - Twitter API clients with India geo-filtering and multi-language keyword support
- `preprocessing.py` - Text cleaning, deduplication, location inference from text and geotags
- `ai_analysis.py` - DeepSeek API integration for hazard classification with confidence scoring
- `aggregation.py` - Spatial clustering and hotspot detection algorithms
- `validation.py` - Human-in-the-loop validation workflow integration
- `alerts.py` - Multi-channel notification system for authorities and citizens
- `storage.py` - Database/file system operations for batch results
- `scheduler.py` - Job scheduling and execution management

**Configuration**
- `config/regional_config.yaml` - India-specific geography, languages, hazard keywords, seasonal risks
- `config/database.yaml` - Database schema, indexes, retention policies
- `.env` - API keys, thresholds, application settings

### Multi-Language Support

The system supports **12 languages**: English + 11 Indian regional languages (Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Odia, Punjabi, Assamese).

Each language has specific hazard keywords and location aliases configured in `config/regional_config.yaml`.

### Key Business Logic

**Hotspot Detection Criteria:**
- ≥20 high-confidence posts (confidence ≥ 0.75) 
- Within 10km geographical radius
- Same hazard type (Flood, Tsunami, High Wave, Storm Surge, Cyclone)
- Grouped by location and time window

**AI Classification Categories:**
- **Relevance**: hazard vs non-hazard
- **Hazard Type**: Flood, Tsunami, High Wave, Storm Surge, Cyclone, Other
- **Urgency**: Low, Medium, High 
- **Confidence**: 0.0 to 1.0 scoring

**Priority Regions**: Coastal cities (Mumbai, Chennai, Visakhapatnam) get higher alert priority due to marine hazard risk.

## Development Guidelines

### Adding New Languages
1. Update `config/regional_config.yaml` with hazard keywords for the new language
2. Add location aliases for cities/states in that language
3. Update `SUPPORTED_LANGUAGES` environment variable
4. Test with sample posts in the target language

### Adding New Hazard Types
1. Update AI analysis prompts in `ai_analysis.py`
2. Add keywords to `regional_config.yaml` 
3. Update validation logic and alert templates
4. Test classification accuracy with sample data

### Location Processing
The system infers location from:
- Tweet geotags (if available)
- City/state mentions in text content
- Location aliases and abbreviations (configured in regional_config.yaml)
- All locations are normalized to Indian geography

### Testing Strategy
- Use `--test` flag for single batch runs during development
- Monitor `logs/social_analytics.log` for detailed processing information
- Check `data/processed/` for batch results in JSON format
- Test with various Indian locations and hazard scenarios

### Performance Considerations
- API rate limiting: Batch processing with delays between API calls
- Memory: Large datasets are processed in chunks
- Storage: File-based storage by default, database optional
- Geospatial operations: Efficient clustering algorithms for hotspot detection

### Environment Variables Important for Development
- `CONFIDENCE_THRESHOLD=0.75` - Minimum AI confidence for hotspot detection
- `HOTSPOT_POST_THRESHOLD=20` - Minimum posts required for hotspot
- `HOTSPOT_RADIUS_KM=10` - Geographic clustering radius
- `SCHEDULER_INTERVAL=3600` - Batch processing frequency (seconds)
- `LOG_LEVEL=INFO` - Logging verbosity

## API Dependencies

**Required API Keys:**
- `DEEPSEEK_API_KEY` - AI analysis service
- `TWITTER_BEARER_TOKEN` - Twitter API v2 access
- `RAPIDAPI_KEY` - Twitter data via RapidAPI

**Optional Database:**
- `DATABASE_URL` - PostgreSQL connection (file storage used if not provided)
- `REDIS_URL` - Caching and session management
