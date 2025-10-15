#!/usr/bin/env python3
"""
Test script to verify PR Copilot setup
"""

import os
import sys
import json
from pathlib import Path

def test_environment():
    """Test environment configuration"""
    print("🔍 Testing environment configuration...")
    
    required_vars = [
        "OPENAI_API_KEY",
        "GITHUB_APP_ID", 
        "GITHUB_WEBHOOK_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_github_key():
    """Test GitHub private key file"""
    print("🔍 Testing GitHub private key...")
    
    key_path = os.getenv("GITHUB_PRIVATE_KEY_PATH", "./github_private_key.pem")
    
    if not Path(key_path).exists():
        print(f"❌ GitHub private key not found at: {key_path}")
        print("Please download your GitHub App private key and save it as github_private_key.pem")
        return False
    
    print("✅ GitHub private key found")
    return True

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        from api.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_redis_connection():
    """Test Redis connection"""
    print("🔍 Testing Redis connection...")
    
    try:
        import redis
        r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_openai_api():
    """Test OpenAI API connection"""
    print("🔍 Testing OpenAI API...")
    
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Test with a simple completion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello, PR Copilot!'"}],
            max_tokens=10
        )
        
        print("✅ OpenAI API connection successful")
        return True
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

def test_classifier():
    """Test PR classifier"""
    print("🔍 Testing PR classifier...")
    
    try:
        from api.services.classifier import PRClassifier
        
        classifier = PRClassifier()
        
        # Test with sample PR data
        sample_pr = {
            "title": "Fix typo in README",
            "body": "Fixed a small typo in the documentation",
            "user": {"login": "testuser"},
            "state": "open",
            "additions": 1,
            "deletions": 1,
            "changed_files": 1,
            "commits": 1
        }
        
        result = classifier.classify_pr(sample_pr)
        
        required_fields = ["classification", "confidence", "priority_score", "reasoning", "suggested_action"]
        for field in required_fields:
            if field not in result:
                print(f"❌ Missing field in classification result: {field}")
                return False
        
        print("✅ PR classifier working correctly")
        print(f"   Classification: {result['classification']}")
        print(f"   Priority: {result['priority_score']}/100")
        return True
        
    except Exception as e:
        print(f"❌ PR classifier test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 PR Copilot Setup Test")
    print("=" * 40)
    
    tests = [
        test_environment,
        test_github_key,
        test_database_connection,
        test_redis_connection,
        test_openai_api,
        test_classifier
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        return True
    else:
        print("❌ Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
