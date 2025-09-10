# 🚀 Coastal Hazard Management System - Deployment Guide

This guide covers various deployment options for your Flask application.

## 📋 Prerequisites

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Create a `.env` file with your API keys:
   ```bash
   # Required for core functionality
   FLASK_SECRET_KEY=your-super-secret-key-here
   
   # Optional - for social media analysis
   RAPIDAPI_KEY=your-rapidapi-key
   OPENROUTER_API_KEY=your-openrouter-key
   DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1
   DEEPSEEK_MODEL=deepseek/deepseek-chat
   
   # Required for SMS/Voice alerts (can be added later)
   TWILIO_ACCOUNT_SID=your-twilio-sid
   TWILIO_AUTH_TOKEN=your-twilio-token
   TWILIO_PHONE_NUMBER=your-twilio-number
   ```
   
   **Note:** The app will work without Twilio credentials, but SMS/Voice alert features will be disabled.

## 🌐 Deployment Options

### Option 1: Railway (Recommended)
Railway is great for Python apps with easy deployment.

1. **Connect GitHub repo to Railway**
2. **Railway will automatically detect Python and use:**
   - `requirements.txt` for dependencies
   - `Procfile` for start command
   - Environment variables from Railway dashboard

3. **Set environment variables in Railway dashboard**
4. **Deploy command:** `railway up`

### Option 2: Render
Similar to Railway, supports Python apps well.

1. **Connect your GitHub repository**
2. **Configure build settings:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --config gunicorn.conf.py app:app`

3. **Add environment variables in Render dashboard**

### Option 3: Heroku
Traditional platform, requires Heroku CLI.

```bash
# Install Heroku CLI
# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set FLASK_SECRET_KEY=your-secret-key
heroku config:set RAPIDAPI_KEY=your-rapidapi-key
# ... add all other environment variables

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Option 4: DigitalOcean App Platform

1. **Connect GitHub repository**
2. **App Platform will detect:**
   - Python runtime from requirements.txt
   - Start command from Procfile

3. **Configure environment variables**

### Option 5: Google Cloud Run

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
   ```

2. **Deploy:**
   ```bash
   gcloud run deploy coastal-hazard --source .
   ```

### Option 6: Local Production Server

```bash
# Install gunicorn if not already installed
pip install gunicorn

# Run with gunicorn
gunicorn --config gunicorn.conf.py app:app

# Or run with specific settings
gunicorn --bind 0.0.0.0:8000 --workers 4 app:app
```

## 🔧 Configuration Files Explained

### `requirements.txt`
- Contains all Python dependencies
- Updated with latest versions and cleaned up

### `gunicorn.conf.py`
- Production WSGI server configuration
- Optimized for performance and security
- Auto-scales workers based on CPU cores

### `Procfile`
- Defines process types for deployment platforms
- `web`: Main Flask application
- `worker`: Background agent processes (optional)
- `release`: Database initialization on deployment

## 🛠️ Troubleshooting

### Common Issues:

1. **`gunicorn: command not found`**
   ```bash
   pip install gunicorn
   ```

2. **Port binding issues**
   - Ensure `PORT` environment variable is set
   - Use `0.0.0.0` instead of `127.0.0.1` for binding

3. **Database initialization**
   - Database will be created automatically on first run
   - SQLite database file will be created in project directory

4. **Static files not loading**
   - Ensure `static/` folder is included in deployment
   - Check static file paths in templates

5. **Environment variables not loading**
   - Verify `.env` file is not in `.gitignore` (if using local .env)
   - Set environment variables in hosting platform dashboard

## 📊 Performance Optimization

### For High Traffic:
1. **Enable gevent workers:**
   ```python
   # In gunicorn.conf.py
   worker_class = "gevent"
   worker_connections = 1000
   ```

2. **Add caching with Redis:**
   ```bash
   pip install redis flask-caching
   ```

3. **Use CDN for static files**
4. **Enable gzip compression**
5. **Add database connection pooling**

## 🔐 Security Checklist

- [ ] Set strong `FLASK_SECRET_KEY`
- [ ] Use HTTPS in production
- [ ] Set `FLASK_ENV=production`
- [ ] Disable Flask debug mode
- [ ] Use environment variables for secrets
- [ ] Enable CSRF protection
- [ ] Set secure headers
- [ ] Use proper authentication

## 📱 Monitoring

Most hosting platforms provide:
- Application logs
- Performance metrics
- Error tracking
- Uptime monitoring

## 🆘 Support

If you encounter deployment issues:
1. Check platform-specific documentation
2. Review application logs
3. Verify environment variables are set correctly
4. Test locally with gunicorn first

---

**Built for disaster preparedness and community safety** 🇮🇳
