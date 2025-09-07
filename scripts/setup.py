#!/usr/bin/env python3
"""
Setup script for Social Media Analytics Agent
Helps with initial project configuration and dependency installation.
"""

import os
import sys
import subprocess
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_template = Path('.env.template')
    env_file = Path('.env')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if env_template.exists():
        import shutil
        shutil.copy(env_template, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your API keys and credentials")
    else:
        print("❌ .env.template not found")

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def create_directories():
    """Ensure all necessary directories exist."""
    directories = [
        'logs',
        'data/raw',
        'data/processed', 
        'data/alerts',
        'tests'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ All directories created")

def main():
    """Main setup function."""
    print("🚀 Setting up Social Media Analytics Agent...")
    print()
    
    # Change to project root if running from scripts/
    if Path.cwd().name == 'scripts':
        os.chdir('..')
    
    create_directories()
    create_env_file()
    
    if install_dependencies():
        print()
        print("🎉 Setup completed successfully!")
        print()
        print("Next steps:")
        print("1. Edit .env file with your API keys")
        print("2. Set up PostgreSQL and Redis (optional)")
        print("3. Run: python src/main.py --test")
        print()
    else:
        print("❌ Setup failed during dependency installation")
        sys.exit(1)

if __name__ == '__main__':
    main()
