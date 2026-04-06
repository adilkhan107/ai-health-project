#!/usr/bin/env python3
"""
OpenAI API Key Test Script for Rural Healthcare App
Run this script to verify your OpenAI API key configuration
"""

import sys
import os

def test_openai_config(skip_api_call=False):
    """Test OpenAI API key configuration"""
    print("🔍 Testing OpenAI API Configuration...")
    print("=" * 50)

    # Test 1: Check config file and environment variable fallback
    print("\n1. Checking config/openai_config.py...")
    try:
        sys.path.append(os.path.dirname(__file__))
        from config.openai_config import OPENAI_API_KEY as FILE_OPENAI_API_KEY
        print(f"   ✅ Config file found")

        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", FILE_OPENAI_API_KEY)
        if os.getenv("OPENAI_API_KEY"):
            print(f"   ℹ️ Using OPENAI_API_KEY from environment variable")

        if OPENAI_API_KEY and OPENAI_API_KEY not in ("your_openai_api_key_here", "sk-your-actual-openai-api-key-here"):
            print(f"   ✅ API key appears to be configured (length: {len(OPENAI_API_KEY)})")
            if not OPENAI_API_KEY.startswith("sk-"):
                print(f"   ⚠️ API key format does not start with 'sk-'. The key may still be invalid for OpenAI.")
        else:
            if skip_api_call:
                print(f"   ⚠️ No valid API key configured, but --skip-api-call was requested.")
                OPENAI_API_KEY = None
            else:
                print(f"   ❌ API key not properly configured in config file or environment")
                print(f"   Set OPENAI_API_KEY in environment or update server/config/openai_config.py")
                return False
    except ImportError as e:
        print(f"   ❌ Could not import config file: {e}")
        return False

    # Test 2: Test OpenAI import and client creation
    print("\n2. Testing OpenAI package and client...")
    try:
        from openai import OpenAI
        print(f"   ✅ OpenAI package imported successfully")

        if OPENAI_API_KEY is not None:
            client = OpenAI(api_key=OPENAI_API_KEY)
            print(f"   ✅ OpenAI client created successfully")
        else:
            client = None
            print(f"   ⚠️ Skipping OpenAI client creation because no API key is configured")

    except ImportError as e:
        print(f"   ❌ OpenAI package not installed: {e}")
        print(f"   Run: pip install openai")
        return False
    except Exception as e:
        print(f"   ❌ OpenAI client creation failed: {e}")
        return False

    if skip_api_call:
        print("\n3. Skipping OpenAI API call as requested.")
        print("\n" + "=" * 50)
        print("⚠️ OpenAI API call was skipped. The configuration file and package import are okay.")
        print("You can rerun without --skip-api-call once you have a valid OpenAI API key.")
        return True

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
    skip_api_call = "--skip-api-call" in sys.argv or "--dry-run" in sys.argv
    success = test_openai_config(skip_api_call=skip_api_call)
    sys.exit(0 if success else 1)