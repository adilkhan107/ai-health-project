# OpenAI Configuration for Rural Healthcare App
# Add your OpenAI API key here for AI-powered medical advice
# Get your API key from: https://platform.openai.com/api-keys

# 🔑 REPLACE THIS WITH YOUR ACTUAL OPENAI API KEY 🔑
# RECOMMENDED: Use environment variable for security
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Alternative: Set directly (less secure)
# OPENAI_API_KEY = "sk-proj-your-actual-key-here"

# Example of what a real API key looks like:
# OPENAI_API_KEY = "sk-proj-ABC123def456ghi789jkl012mno345pqr678stu901vwx234yz"

# Usage instructions:
# 1. Replace "sk-your-actual-openai-api-key-here" with your actual OpenAI API key
# 2. Save this file
# 3. The AI Advisor will automatically use this key
# 4. Keep this file secure and never share your API key publicly

# Note: This app uses GPT-3.5-turbo for medical analysis
# Monitor your OpenAI usage at: https://platform.openai.com/usage

# Alternative: Set as environment variable
# export OPENAI_API_KEY="your-key-here"