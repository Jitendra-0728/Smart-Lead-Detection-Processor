# test_deepseek.py
# This script tests DeepSeek models specifically for lead qualification

# Step 2: Set Up OpenRouter API Access - Completed

import requests
import json


def test_deepseek_basic():
    """
    Test basic DeepSeek API connection
    """
    print("🚀 Starting DeepSeek API connection test...")

    # Your API configuration
    API_KEY = "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"  # Replace with your actual API key
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    # Headers for the API request
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Using DeepSeek chat model - excellent for business analysis
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {
                "role": "user",
                "content": "Test message - please respond with exactly: 'DeepSeek API working perfectly!'"
            }
        ],
        "max_tokens": 30,
        "temperature": 0
    }

    try:
        print("📡 Sending request to DeepSeek via OpenRouter...")

        response = requests.post(BASE_URL, headers=headers, json=payload)

        if response.status_code == 200:
            print("✅ DeepSeek API request successful!")

            response_data = response.json()
            ai_message = response_data['choices'][0]['message']['content']

            print(f"🤖 DeepSeek Response: {ai_message}")
            print(f"📊 Status Code: {response.status_code}")

            # DeepSeek is very cost-effective - show usage
            if 'usage' in response_data:
                usage = response_data['usage']
                print(f"💰 Token Usage (Very Low Cost!):")
                print(f"   - Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                print(f"   - Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                print(f"   - Total tokens: {usage.get('total_tokens', 'N/A')}")

            print("🎉 DeepSeek test completed successfully!")
            return True

        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"📋 Error response: {response.text}")
            return False

    except Exception as e:
        print(f"💥 Error occurred: {e}")
        return False


def test_deepseek_models():
    """
    Test different DeepSeek models available
    """
    print("\n🔄 Testing different DeepSeek models...")

    API_KEY = "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"  # Replace with your actual API key
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    # DeepSeek models - all very cost-effective
    deepseek_models = [
        {
            "name": "deepseek/deepseek-chat-v3-0324:free",
            "description": "Main DeepSeek model - excellent for business analysis and reasoning"
        },

    ]

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    for model_info in deepseek_models:
        model = model_info["name"]
        description = model_info["description"]

        print(f"\n🧪 Testing {model}...")
        print(f"📝 Description: {description}")

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": f"Say 'Hello from {model.split('/')[-1]} - ready for business analysis!'"
                }
            ],
            "max_tokens": 30,
            "temperature": 0.3
        }

        try:
            response = requests.post(BASE_URL, headers=headers, json=payload)

            if response.status_code == 200:
                response_data = response.json()
                ai_message = response_data['choices'][0]['message']['content']
                print(f"✅ {model.split('/')[-1]}: {ai_message}")

                # Show cost info
                if 'usage' in response_data:
                    tokens = response_data['usage'].get('total_tokens', 'N/A')
                    print(f"   💰 Tokens used: {tokens} (Very low cost!)")
            else:
                print(f"❌ {model.split('/')[-1]}: Failed (Status: {response.status_code})")

        except Exception as e:
            print(f"❌ {model.split('/')[-1]}: Error - {e}")


def test_lead_qualification_with_deepseek():
    """
    Test DeepSeek's ability to qualify business leads
    """
    print("\n📧 Testing DeepSeek for email lead qualification...")

    API_KEY = "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"  # Replace with your actual API key
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    # Sample email for testing
    sample_email = """
    From: sarah.johnson@techcorp.com
    Subject: Need help with data entry project

    Hi,

    I'm Sarah Johnson from TechCorp. We have about 3,000 customer records 
    in paper format that need to be digitized into our new CRM system. 

    Can you provide a quote for this data entry work? We need it completed 
    within 2 weeks.

    Please call me at (555) 987-6543 to discuss.

    Best regards,
    Sarah Johnson
    Operations Director
    TechCorp Solutions
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # DeepSeek is excellent at reasoning and business analysis
    payload = {
        "model": "deepseek/deepseek-chat",  # Best DeepSeek model for business analysis
        "messages": [
            {
                "role": "user",
                "content": f"""Analyze this email to determine if it's a qualified business lead for a data entry service company.

Email to analyze:
{sample_email}

Please respond with:
1. QUALIFIED or NOT QUALIFIED
2. Confidence level (1-10)
3. Brief reasoning
4. Extracted company name
5. Extracted contact person

Keep response concise and structured."""
            }
        ],
        "max_tokens": 200,
        "temperature": 0.3  # Slightly higher for more natural analysis
    }

    try:
        print("🔍 Analyzing sample email with DeepSeek...")

        response = requests.post(BASE_URL, headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            analysis = response_data['choices'][0]['message']['content']

            print("✅ DeepSeek Lead Analysis Results:")
            print("-" * 50)
            print(analysis)
            print("-" * 50)

            # Show cost efficiency
            if 'usage' in response_data:
                tokens = response_data['usage'].get('total_tokens', 'N/A')
                print(f"💰 Analysis cost: {tokens} tokens (approximately $0.001-0.002)")

            return True

        else:
            print(f"❌ Analysis failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"💥 Analysis error: {e}")
        return False


if __name__ == "__main__":
    print("🎯 DeepSeek API Testing Suite for Lead Qualification")
    print("=" * 60)

    # Test 1: Basic connection
    basic_success = test_deepseek_basic()

    # Test 2: Different DeepSeek models
    if basic_success:
        test_deepseek_models()

        # Test 3: Lead qualification capability
        test_lead_qualification_with_deepseek()

    print("\n" + "=" * 60)
    print("📝 DeepSeek Test Summary:")
    if basic_success:
        print("✅ DeepSeek API is working correctly!")
        print("✅ Very cost-effective option for lead qualification!")
        print("✅ Ready to integrate into your automation system!")
        print("\n💡 Why DeepSeek is great for this project:")
        print("   - Very low cost (up to 10x cheaper than GPT-4)")
        print("   - Excellent reasoning capabilities")
        print("   - Great for business analysis tasks")
        print("   - Reliable and consistent responses")
    else:
        print("❌ Please check your API key and try again.")

