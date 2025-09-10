# Gunicorn Configuration for Coastal Hazard Management System
# Production deployment settings

import multiprocessing
import os

# Server Socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"  # Use "gevent" if you need async support
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'coastal-hazard-management'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Application preloading
preload_app = True

# Graceful restarts
graceful_timeout = 30

# SSL (if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
