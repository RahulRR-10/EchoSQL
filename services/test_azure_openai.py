"""
Test script to verify Azure OpenAI credentials
Run this to check if your Azure OpenAI configuration is correct
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# Load credentials
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-07-01-preview")

print("=" * 60)
print("Azure OpenAI Configuration Test")
print("=" * 60)
print(f"Endpoint: {endpoint}")
print(f"Deployment: {deployment}")
print(f"API Version: {api_version}")
print(f"API Key: {api_key[:10]}...{api_key[-10:] if api_key else 'NOT SET'}")
print("=" * 60)

if not endpoint or not api_key:
    print("❌ ERROR: Missing Azure OpenAI credentials in .env file")
    print("\nRequired environment variables:")
    print("  - AZURE_OPENAI_ENDPOINT")
    print("  - AZURE_OPENAI_API_KEY")
    print("  - AZURE_OPENAI_DEPLOYMENT")
    print("  - AZURE_OPENAI_API_VERSION")
    exit(1)

# Remove trailing slash from endpoint
if endpoint.endswith('/'):
    endpoint = endpoint[:-1]
    print(f"📝 Removed trailing slash from endpoint: {endpoint}")

print("\n🔄 Testing connection...")

try:
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version
    )
    
    print("✅ Client initialized successfully")
    print("\n🔄 Testing API call...")
    
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Say 'Hello, Azure OpenAI is working!'"
            }
        ],
        temperature=0.2,
        max_tokens=50
    )
    
    result = response.choices[0].message.content
    print(f"✅ API call successful!")
    print(f"📝 Response: {result}")
    print("\n" + "=" * 60)
    print("🎉 Azure OpenAI is configured correctly!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n" + "=" * 60)
    print("Troubleshooting steps:")
    print("=" * 60)
    print("1. Verify your API key is correct in .env file")
    print("2. Check that the endpoint URL is correct")
    print("3. Ensure the deployment name matches your Azure resource")
    print("4. Verify your Azure subscription is active")
    print("5. Check that your API key has not expired")
    print("\nFor Azure OpenAI specific errors:")
    print("- Go to Azure Portal > Your OpenAI Resource")
    print("- Navigate to 'Keys and Endpoint'")
    print("- Copy the correct values to your .env file")
    print("=" * 60)
