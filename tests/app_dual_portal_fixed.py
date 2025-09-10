"""
Coastal Disaster Management System - Dual Portal Application
Main Flask app with Admin (Government) and User (Citizen) portals.
"""

import os
import sys
import json
import asyncio
import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
import threading
from pathlib import Path
from loguru import logger
from functools import wraps

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print(f"🔑 Environment Variables Loaded:")
print(f"   RAPIDAPI_KEY: {'✅ Set' if os.getenv('RAPIDAPI_KEY') else '❌ Not set'}")
print(f"   OPENROUTER_API_KEY: {'✅ Set' if os.getenv('OPENROUTER_API_KEY') else '❌ Not set'}")
print(f"   TWITTER_BEARER_TOKEN: {'✅ Set' if os.getenv('TWITTER_BEARER_TOKEN') else '❌ Not set'}")

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    from models.database import (
        db_manager, init_database, UserReport, SocialMediaPost, 
        Hotspot, SocialMediaCorrelation, AgentExecution
    )
    from agents.agent2_report_analysis import process_user_report
    from modules.ai_analysis import AIAnalysisService
    from modules.data_ingestion import DataIngestionService
    from modules.preprocessing import PreprocessingService
    from modules.aggregation import AggregationService
    from modules.storage import StorageService
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.info("Some modules may not be available, but the app will still start")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'coastal-disaster-management-secret-key')
CORS(app)  # Enable CORS for API access

# Global services (with error handling)
try:
    data_ingestion = DataIngestionService()
    preprocessing = PreprocessingService()
    ai_analysis = AIAnalysisService()
    aggregation = AggregationService()
    storage = StorageService()
    services_available = True
except Exception as e:
    logger.warning(f"Services initialization failed: {e}")
    services_available = False

# Global status tracking
system_status = {
    'agent1_running': False,
    'agent1_last_run': None,
    'agent1_next_run': None,
    'total_reports': 0,
    'total_hotspots': 0,
    'total_social_posts': 0,
    'system_health': 'healthy'
}

# Demo user credentials (in production, use proper database and hashing)
USERS = {
    'admin': {
        'password': 'admin123',
        'role': 'admin',
        'name': 'System Administrator'
    },
    'citizen': {
        'password': 'citizen123',
        'role': 'citizen',
        'name': 'Citizen User'
    }
}

# ==============================================================================
# AUTHENTICATION SYSTEM
# ==============================================================================

def login_required(role=None):
    """Decorator to require login for routes."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            if role and session.get('role') != role:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both admin and citizen users."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        # Check credentials
        if username in USERS and USERS[username]['password'] == password:
            user = USERS[username]
            
            # Verify user type matches role
            if (user_type == 'admin' and user['role'] == 'admin') or \
               (user_type == 'citizen' and user['role'] == 'citizen'):
                
                # Set session
                session['user_id'] = username
                session['role'] = user['role']
                session['name'] = user['name']
                
                flash(f'Welcome, {user["name"]}!', 'success')
                
                # Redirect based on role
                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid user type for this account.', 'error')
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout current user."""
    name = session.get('name', 'User')
    session.clear()
    flash(f'Goodbye, {name}! You have been logged out.', 'info')
    return redirect(url_for('login'))

# ==============================================================================
# ADMIN PORTAL ROUTES (Government Dashboard)
# ==============================================================================

@app.route('/admin')
@login_required('admin')
def admin_dashboard():
    """Admin dashboard - Government portal for monitoring and management."""
    
    # Placeholder data for UI testing
    stats = {
        'total_reports': 0,
        'total_hotspots': 0,
        'total_social_posts': 0,
        'recent_reports_count': 0,
        'high_confidence_reports_count': 0
    }
    
    recent_reports = []
    active_hotspots = []
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_reports=recent_reports,
                         active_hotspots=active_hotspots,
                         system_status=system_status)

@app.route('/admin/reports')
@login_required('admin')
def admin_reports():
    """Admin view of all user reports with management options."""
    
    # Get filters from query parameters
    status_filter = request.args.get('status', 'all')
    severity_filter = request.args.get('severity', 'all')
    
    # Placeholder data
    reports = []
    
    return render_template('admin/reports.html', 
                         reports=reports,
                         status_filter=status_filter,
                         severity_filter=severity_filter)

@app.route('/admin/hotspots')
@login_required('admin')
def admin_hotspots():
    """Admin view of detected hotspots."""
    
    # Placeholder data
    hotspots = []
    
    return render_template('admin/hotspots.html', 
                         hotspots=hotspots)

@app.route('/admin/map')
@login_required('admin')
def admin_map():
    """Interactive map view for admin with all hotspots and reports."""
    
    # Placeholder map data
    map_data = {
        'hotspots': [],
        'reports': []
    }
    
    return render_template('admin/map.html', map_data=map_data)

@app.route('/admin/api/update-report-status', methods=['POST'])
@login_required('admin')
def admin_update_report_status():
    """API endpoint for admin to update report status."""
    
    data = request.get_json()
    report_id = data.get('report_id')
    new_status = data.get('status')
    admin_notes = data.get('notes', '')
    
    # Placeholder - in production this would update database
    return jsonify({'success': True, 'message': 'Report status updated (placeholder)'})

# ==============================================================================
# USER PORTAL ROUTES (Citizen Interface)
# ==============================================================================

@app.route('/')
def index():
    """Redirect to login page."""
    return redirect(url_for('login'))

@app.route('/user')
@login_required('citizen')
def user_dashboard():
    """User dashboard - Citizen portal for reporting and viewing hazards."""
    
    # Placeholder data
    active_hotspots = []
    
    return render_template('user/dashboard.html', 
                         active_hotspots=active_hotspots)

@app.route('/user/report', methods=['GET', 'POST'])
@login_required('citizen')
def user_create_report():
    """Create new disaster report."""
    
    if request.method == 'POST':
        try:
            # Get location from form
            report_data = {
                'id': str(uuid.uuid4()),
                'title': request.form['title'],
                'description': request.form['description'],
                'hazard_type': request.form['hazard_type'],
                'severity': request.form['severity'],
                'latitude': float(request.form['latitude']),
                'longitude': float(request.form['longitude']),
                'location_name': request.form.get('location_name', ''),
                'city': request.form.get('city', ''),
                'state': request.form.get('state', ''),
                'reporter_ip': request.remote_addr,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Process report with Agent 2 in background
            if services_available:
                thread = threading.Thread(
                    target=process_report_background, 
                    args=(report_data,)
                )
                thread.daemon = True
                thread.start()
            
            flash('Report submitted successfully! Our system is analyzing it for correlations with social media data.', 'success')
            return redirect(url_for('user_my_reports'))
            
        except Exception as e:
            flash(f'Error submitting report: {str(e)}', 'error')
            return redirect(url_for('user_create_report'))
    
    return render_template('user/create_report.html')

@app.route('/user/my-reports')
@login_required('citizen')
def user_my_reports():
    """View user's own reports (based on IP for MVP)."""
    
    # Placeholder data
    reports = []
    
    return render_template('user/my_reports.html', 
                         reports=reports)

@app.route('/user/map')
@login_required('citizen')
def user_map():
    """User map view showing nearby hotspots and hazards."""
    
    # Get user's approximate location (could be from query params or session)
    user_lat = request.args.get('lat', type=float)
    user_lon = request.args.get('lon', type=float)
    
    # Placeholder data
    map_data = {
        'hotspots': [],
        'user_location': {'lat': user_lat, 'lon': user_lon} if user_lat and user_lon else None
    }
    
    return render_template('user/map.html', map_data=map_data)

@app.route('/user/verify-report/<report_id>', methods=['POST'])
@login_required('citizen')
def user_verify_report(report_id):
    """Allow users to verify/validate existing reports."""
    
    verification_type = request.json.get('type')  # 'confirm' or 'dispute'
    user_notes = request.json.get('notes', '')
    
    # Placeholder response
    return jsonify({'success': True, 'message': 'Verification recorded (placeholder)'})

# ==============================================================================
# BACKGROUND PROCESSING
# ==============================================================================

def process_report_background(report_data):
    """Process user report with Agent 2 in background thread."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Process with Agent 2
        enhanced_report = loop.run_until_complete(process_user_report(report_data))
        
        logger.info(f"Successfully processed user report {enhanced_report['id']} with confidence {enhanced_report.get('correlation_confidence', 0.0)}")
        
        loop.close()
        
    except Exception as e:
        logger.error(f"Error processing user report in background: {str(e)}")

# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@app.route('/api/system-status')
def api_system_status():
    """Get current system status."""
    return jsonify(system_status)

@app.route('/api/hotspots')
def api_hotspots():
    """API endpoint for hotspot data."""
    return jsonify({
        'hotspots': []
    })

@app.route('/api/reports')
def api_reports():
    """API endpoint for report data."""
    return jsonify({
        'reports': []
    })

@app.route('/api/run-agent1', methods=['POST'])
def api_run_agent1():
    """Manually trigger Agent 1 (social media monitoring)."""
    
    if system_status['agent1_running']:
        return jsonify({'error': 'Agent 1 is already running'}), 400
    
    if not services_available:
        return jsonify({'error': 'Services not available'}), 500
    
    # Start Agent 1 in background
    thread = threading.Thread(target=run_agent1_background)
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Agent 1 started successfully'})

def run_agent1_background():
    """Run Agent 1 in background thread."""
    system_status['agent1_running'] = True
    system_status['agent1_last_run'] = datetime.utcnow().isoformat()
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Fetch social media posts
        start_time = datetime.utcnow() - timedelta(hours=12)
        end_time = datetime.utcnow()
        
        raw_posts = loop.run_until_complete(
            data_ingestion.fetch_social_media_posts(start_time, end_time)
        )
        
        # Process posts
        processed_posts = loop.run_until_complete(
            preprocessing.process_posts(raw_posts)
        )
        
        analyzed_posts = loop.run_until_complete(
            ai_analysis.analyze_posts(processed_posts)
        )
        
        hotspots = loop.run_until_complete(
            aggregation.detect_hotspots(analyzed_posts)
        )
        
        system_status['total_social_posts'] = len(analyzed_posts)
        system_status['total_hotspots'] = len(hotspots)
        
        logger.info(f"Agent 1 completed: {len(analyzed_posts)} posts, {len(hotspots)} hotspots")
        
        loop.close()
        
    except Exception as e:
        logger.error(f"Error in Agent 1 background processing: {str(e)}")
        system_status['system_health'] = 'error'
    finally:
        system_status['agent1_running'] = False
        system_status['agent1_next_run'] = (datetime.utcnow() + timedelta(hours=12)).isoformat()

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers."""
    import math
    R = 6371  # Earth's radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

# ==============================================================================
# BASIC HTML TEMPLATES (For Testing)
# ==============================================================================

@app.route('/create-templates')
def create_basic_templates():
    """Create basic HTML templates for testing."""
    
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    # Create admin templates directory
    (templates_dir / 'admin').mkdir(exist_ok=True)
    (templates_dir / 'user').mkdir(exist_ok=True)
    
    # Basic admin dashboard template
    admin_dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - Coastal Disaster Management</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav-links { margin-bottom: 20px; }
        .nav-links a { background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; margin-right: 10px; border-radius: 4px; }
        .nav-links a:hover { background: #2563eb; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ Admin Dashboard - Coastal Disaster Management</h1>
        <p>Government Portal for Disaster Monitoring & Management</p>
    </div>
    
    <div class="nav-links">
        <a href="/admin">Dashboard</a>
        <a href="/admin/reports">Reports</a>
        <a href="/admin/hotspots">Hotspots</a>
        <a href="/admin/map">Map View</a>
        <a href="/user">Switch to User Portal</a>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <h3>📋 Total Reports</h3>
            <h2>{{ stats.total_reports }}</h2>
        </div>
        <div class="stat-card">
            <h3>🔥 Active Hotspots</h3>
            <h2>{{ stats.total_hotspots }}</h2>
        </div>
        <div class="stat-card">
            <h3>📱 Social Posts</h3>
            <h2>{{ stats.total_social_posts }}</h2>
        </div>
        <div class="stat-card">
            <h3>⚡ System Health</h3>
            <h2>{{ system_status.system_health.title() }}</h2>
        </div>
    </div>
    
    <div style="background: white; padding: 20px; border-radius: 8px;">
        <h2>🚀 Quick Actions</h2>
        <button onclick="runAgent1()" style="background: #10b981; color: white; padding: 10px 20px; border: none; border-radius: 4px; margin-right: 10px; cursor: pointer;">Run Agent 1 (Social Media Scan)</button>
        <button onclick="window.location.href='/admin/reports'" style="background: #f59e0b; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Review Reports</button>
    </div>
    
    <script>
        function runAgent1() {
            fetch('/api/run-agent1', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    alert(data.message || data.error);
                    if (data.message) location.reload();
                });
        }
    </script>
</body>
</html>
    """
    
    # Basic user dashboard template
    user_dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Portal - Coastal Disaster Management</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #059669; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .nav-links { margin-bottom: 20px; }
        .nav-links a { background: #10b981; color: white; padding: 10px 20px; text-decoration: none; margin-right: 10px; border-radius: 4px; }
        .nav-links a:hover { background: #059669; }
        .action-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .action-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .report-btn { background: #dc2626; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>👥 Citizen Portal - Coastal Disaster Management</h1>
        <p>Report disasters, stay informed, help your community</p>
    </div>
    
    <div class="nav-links">
        <a href="/user">Dashboard</a>
        <a href="/user/report">🚨 Create Report</a>
        <a href="/user/my-reports">My Reports</a>
        <a href="/user/map">🗺️ View Map</a>
        <a href="/admin">Switch to Admin Portal</a>
    </div>
    
    <div class="action-cards">
        <div class="action-card">
            <h2>🚨 Report Emergency</h2>
            <p>Spotted a disaster? Report it immediately to help authorities respond quickly and save lives.</p>
            <button class="report-btn" onclick="window.location.href='/user/report'">Create Report</button>
        </div>
        
        <div class="action-card">
            <h2>🗺️ View Hotspots</h2>
            <p>Check active disaster hotspots in your area. Stay informed and stay safe.</p>
            <button onclick="window.location.href='/user/map'" style="background: #f59e0b; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">View Map</button>
        </div>
        
        <div class="action-card">
            <h2>📋 My Reports</h2>
            <p>Track your submitted reports and see how they're helping the community.</p>
            <button onclick="window.location.href='/user/my-reports'" style="background: #3b82f6; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">View Reports</button>
        </div>
    </div>
</body>
</html>
    """
    
    # Basic report creation form
    create_report_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Report - Coastal Disaster Management</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .header { background: #059669; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .form-container { background: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        textarea { height: 100px; resize: vertical; }
        .submit-btn { background: #dc2626; color: white; padding: 15px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
        .location-btn { background: #3b82f6; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 Create Disaster Report</h1>
        <p>Help save lives by reporting disasters in your area</p>
    </div>
    
    <div class="form-container">
        <form method="POST">
            <div class="form-group">
                <label>Report Title:</label>
                <input type="text" name="title" required placeholder="e.g., Severe flooding on Marine Drive">
            </div>
            
            <div class="form-group">
                <label>Description:</label>
                <textarea name="description" required placeholder="Describe what you're seeing. Include specific details like water levels, affected areas, people in danger, etc."></textarea>
            </div>
            
            <div class="form-group">
                <label>Hazard Type:</label>
                <select name="hazard_type" required>
                    <option value="">Select hazard type</option>
                    <option value="flood">Flood</option>
                    <option value="cyclone">Cyclone/Storm</option>
                    <option value="tsunami">Tsunami</option>
                    <option value="high_waves">High Waves</option>
                    <option value="coastal_erosion">Coastal Erosion</option>
                    <option value="other">Other</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Severity:</label>
                <select name="severity" required>
                    <option value="">Select severity</option>
                    <option value="low">Low - Minor impact</option>
                    <option value="medium">Medium - Moderate impact</option>
                    <option value="high">High - Major impact</option>
                    <option value="critical">Critical - Life threatening</option>
                </select>
            </div>
            
            <div class="form-group">
                <button type="button" class="location-btn" onclick="getLocation()">📍 Get My Location</button>
                <input type="hidden" name="latitude" id="latitude" required>
                <input type="hidden" name="longitude" id="longitude" required>
                <input type="text" name="location_name" placeholder="Location will appear here" readonly>
            </div>
            
            <div class="form-group">
                <input type="text" name="city" placeholder="City" required>
            </div>
            
            <div class="form-group">
                <input type="text" name="state" placeholder="State" required>
            </div>
            
            <button type="submit" class="submit-btn">🚨 Submit Report</button>
            <a href="/user" style="margin-left: 20px; color: #666; text-decoration: none;">Cancel</a>
        </form>
    </div>
    
    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    document.getElementById('latitude').value = position.coords.latitude;
                    document.getElementById('longitude').value = position.coords.longitude;
                    document.getElementsByName('location_name')[0].value = 
                        `Lat: ${position.coords.latitude.toFixed(6)}, Lon: ${position.coords.longitude.toFixed(6)}`;
                    alert('Location captured successfully!');
                });
            } else {
                alert('Geolocation is not supported by this browser.');
            }
        }
    </script>
</body>
</html>
    """
    
    # Write template files
    with open(templates_dir / 'admin' / 'dashboard.html', 'w', encoding='utf-8') as f:
        f.write(admin_dashboard_html)
    
    with open(templates_dir / 'user' / 'dashboard.html', 'w', encoding='utf-8') as f:
        f.write(user_dashboard_html)
    
    with open(templates_dir / 'user' / 'create_report.html', 'w', encoding='utf-8') as f:
        f.write(create_report_html)
    
    # Create placeholder templates for other routes
    placeholder_templates = {
        'admin/reports.html': '<h1>Admin Reports</h1><p>Reports management interface coming soon...</p>',
        'admin/hotspots.html': '<h1>Admin Hotspots</h1><p>Hotspots management interface coming soon...</p>',
        'admin/map.html': '<h1>Admin Map</h1><p>Interactive map coming soon...</p>',
        'user/my_reports.html': '<h1>My Reports</h1><p>Your reports will appear here...</p>',
        'user/map.html': '<h1>User Map</h1><p>Interactive user map coming soon...</p>'
    }
    
    for template_path, content in placeholder_templates.items():
        template_file = templates_dir / template_path
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(f'<!DOCTYPE html><html><head><title>Coastal Disaster Management</title></head><body>{content}</body></html>')
    
    return jsonify({'message': 'Basic templates created successfully!'})

# ==============================================================================
# APPLICATION STARTUP
# ==============================================================================

if __name__ == '__main__':
    print("🌊 Starting Coastal Disaster Management System...")
    
    # Create basic templates on startup
    try:
        with app.app_context():
            create_basic_templates()
        print("✅ Basic templates created")
    except Exception as e:
        print(f"⚠️ Template creation failed: {e}")
    
    # Initialize database if available
    try:
        if 'init_database' in globals():
            init_database()
            print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {str(e)}")
    
    # Check API configurations
    api_config = {
        'deepseek_api': bool(os.getenv('OPENROUTER_API_KEY')),
        'twitter_api': bool(os.getenv('RAPIDAPI_KEY')),
        'services': services_available
    }
    
    print("\n🔧 System Configuration:")
    print(f"  ✅ DeepSeek AI: {'Configured' if api_config['deepseek_api'] else 'Not configured'}")
    print(f"  ✅ Twitter API: {'Configured' if api_config['twitter_api'] else 'Not configured'}")
    print(f"  ✅ Services: {'Available' if api_config['services'] else 'Limited'}")
    
    print("\n🚀 Features Available:")
    print("  📊 Admin Portal: http://localhost:5000/admin")
    print("  👥 User Portal: http://localhost:5000/user")
    print("  🗺️  Interactive Maps: Both portals")
    print("  🤖 Agent 1: Social media monitoring")
    print("  🔍 Agent 2: Report analysis & correlation")
    print("  📈 Real-time Dashboard: Admin portal")
    
    if not api_config['deepseek_api']:
        print("\n⚠️  Warning: DeepSeek API not configured. AI analysis will use fallback methods.")
    if not api_config['twitter_api']:
        print("⚠️  Warning: Twitter API not configured. Social media data will be limited.")
    if not api_config['services']:
        print("⚠️  Warning: Some services unavailable. Basic UI functionality will work.")
    
    print("\n🌐 Starting server at: http://localhost:5000")
    print("📋 Admin Dashboard: http://localhost:5000/admin")
    print("👥 User Portal: http://localhost:5000/user")
    
    # Start Flask development server
    app.run(
        debug=True if os.getenv('ENVIRONMENT') != 'production' else False,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000))
    )
