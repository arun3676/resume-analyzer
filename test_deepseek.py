#!/usr/bin/env python3
"""
Test script to verify DeepSeek API integration
"""
import os
import sys
import requests
import json

def test_deepseek_integration():
    """Test if DeepSeek API is working through our application"""
    
    print("🧪 Testing DeepSeek Integration...")
    print("=" * 50)
    
    # Check if server is running
    try:
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first.")
        return False
    
    # Test a simple analysis
    print("\n🔍 Testing Resume Analysis with DeepSeek...")
    
    # Sample resume text
    sample_resume = """
    John Doe
    Software Engineer
    
    Experience:
    - 3 years of Python development
    - Experience with FastAPI and React
    - Machine learning projects using TensorFlow
    
    Skills:
    - Python, JavaScript, SQL
    - FastAPI, React, Node.js
    - TensorFlow, scikit-learn
    - Git, Docker, AWS
    
    Education:
    - Bachelor's in Computer Science
    """
    
    # Create a test file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(sample_resume)
        temp_file_path = f.name
    
    try:
        # Test the analysis endpoint
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('resume.txt', f, 'text/plain')}
            data = {'job_description': 'Looking for a Python developer with FastAPI experience'}
            
            print("📤 Sending test request...")
            response = requests.post(
                "http://localhost:8000/analyze",
                files=files,
                data=data,
                timeout=60  # 60 second timeout
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ DeepSeek API call successful!")
            print(f"📊 Analysis preview: {result.get('analysis', 'No analysis')[:200]}...")
            
            if 'skill_match_details' in result:
                match_percentage = result['skill_match_details'].get('match_percentage', 0)
                print(f"🎯 Skill match: {match_percentage}%")
            
            return True
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this might indicate API key issues")
        return False
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False
    finally:
        # Clean up temp file
        os.unlink(temp_file_path)

def check_environment():
    """Check environment variables"""
    print("\n🔧 Environment Check:")
    print("=" * 30)
    
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if deepseek_key:
        if deepseek_key == "your_deepseek_api_key_here":
            print("⚠️  DEEPSEEK_API_KEY is set to placeholder value")
            print("   Please set your actual DeepSeek API key:")
            print("   $env:DEEPSEEK_API_KEY=\"your_actual_key_here\"")
            return False
        else:
            print(f"✅ DEEPSEEK_API_KEY is set (ends with: ...{deepseek_key[-4:]})")
            return True
    else:
        print("❌ DEEPSEEK_API_KEY is not set")
        print("   Please set it with: $env:DEEPSEEK_API_KEY=\"your_key_here\"")
        return False

if __name__ == "__main__":
    print("🚀 DeepSeek Integration Test")
    print("=" * 50)
    
    # Check environment first
    env_ok = check_environment()
    
    if env_ok:
        # Run the test
        success = test_deepseek_integration()
        
        if success:
            print("\n🎉 All tests passed! DeepSeek integration is working correctly.")
            print("💰 You're now using DeepSeek API instead of OpenAI - much cheaper!")
        else:
            print("\n❌ Tests failed. Please check your DeepSeek API key and try again.")
    else:
        print("\n⚠️  Please fix environment issues and run the test again.")
    
    print("\n" + "=" * 50) 