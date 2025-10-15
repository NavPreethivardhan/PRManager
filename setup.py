#!/usr/bin/env python3
"""
Setup script for PR Copilot
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    requirements = [
        ("python", "python --version"),
        ("docker", "docker --version"),
        ("docker-compose", "docker-compose --version")
    ]
    
    missing = []
    for tool, cmd in requirements:
        if not run_command(cmd, f"Checking {tool}"):
            missing.append(tool)
    
    if missing:
        print(f"❌ Missing required tools: {', '.join(missing)}")
        print("Please install them and run this script again.")
        return False
    
    print("✅ All requirements satisfied")
    return True

def setup_environment():
    """Setup environment file"""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    # Copy example to .env
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")
    print("⚠️  Please edit .env file with your actual configuration values")
    return True

def setup_database():
    """Setup database migrations"""
    print("🗄️  Setting up database...")
    
    # Run database migrations
    if not run_command("alembic upgrade head", "Running database migrations"):
        return False
    
    print("✅ Database setup completed")
    return True

def main():
    """Main setup function"""
    print("🚀 PR Copilot Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. Create GitHub App (see README.md)")
    print("3. Run: docker-compose up -d")
    print("4. Test with a sample PR")

if __name__ == "__main__":
    main()
