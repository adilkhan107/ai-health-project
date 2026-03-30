#!/usr/bin/env python3
"""
OpenAI API Key Test Script for Rural Healthcare App
Run this script to verify your OpenAI API key configuration
"""

import sys
import os

def test_openai_config():
    """Test OpenAI API key configuration"""
    print("🔍 Testing OpenAI API Configuration...")
    print("=" * 50)

    # Test 1: Check config file
    print("\n1. Checking config/openai_config.py...")
    try:
        sys.path.append(os.path.dirname(__file__))
        from config.openai_config import OPENAI_API_KEY
        print(f"   ✅ Config file found")

        if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here" and OPENAI_API_KEY != "sk-your-actual-openai-api-key-here":
            print(f"   ✅ API key appears to be configured (length: {len(OPENAI_API_KEY)})")
        else:
            print(f"   ❌ API key not properly configured in config file")
            print(f"   Please edit config/openai_config.py and replace the placeholder with your actual API key")
            return False
    except ImportError as e:
        print(f"   ❌ Could not import config file: {e}")
        return False

    # Test 2: Test OpenAI import and client creation
    print("\n2. Testing OpenAI package and client...")
    try:
        from openai import OpenAI
        print(f"   ✅ OpenAI package imported successfully")

        client = OpenAI(api_key=OPENAI_API_KEY)
        print(f"   ✅ OpenAI client created successfully")

    except ImportError as e:
        print(f"   ❌ OpenAI package not installed: {e}")
        print(f"   Run: pip install openai")
        return False
    except Exception as e:
        print(f"   ❌ OpenAI client creation failed: {e}")
        return False

    # Test 3: Test API call
    print("\n3. Testing OpenAI API call...")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, test message"}],
            max_tokens=10
        )
        print(f"   ✅ API call successful!")
        print(f"   Response: {response.choices[0].message.content.strip()}")

    except Exception as e:
        print(f"   ❌ API call failed: {e}")
        print(f"   Possible issues:")
        print(f"   - Invalid API key")
        print(f"   - No internet connection")
        print(f"   - API quota exceeded")
        print(f"   - Wrong API key format (should start with 'sk-')")
        return False

    print("\n" + "=" * 50)
    print("🎉 All tests passed! OpenAI is properly configured.")
    print("You can now use AI features in your Rural Healthcare app.")
    return True

if __name__ == "__main__":
    success = test_openai_config()
    sys.exit(0 if success else 1)