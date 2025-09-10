web: gunicorn --config gunicorn.conf.py app:app
worker: python src/agent_runner.py
release: python -c "from app import init_database; init_database()"
