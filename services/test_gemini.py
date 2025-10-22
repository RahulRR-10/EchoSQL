"""
Test Google Gemini API connection and visualization validation
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

# Test Gemini connection
api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing Google Gemini API...")
print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")

if not api_key:
    print("❌ GEMINI_API_KEY not found in environment variables")
    exit(1)

try:
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # List available models
    print("\n📋 Listing available Gemini models...")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
    
    # Use the latest model
    model = genai.GenerativeModel('gemini-2.5-flash')
    print(f"\n✅ Using model: gemini-2.5-flash")
    
    # Test simple prompt
    print("\n✅ Testing Gemini API connection...")
    response = model.generate_content("Say 'Hello from Gemini!' in JSON format")
    print(f"Response: {response.text}")
    
    # Test visualization validation prompt
    print("\n✅ Testing visualization validation...")
    prompt = """Analyze this database query and determine if visualization is appropriate.

USER QUERY: "List all employees"

SQL QUERY: SELECT * FROM employees

RESULT DATA SUMMARY:
- Total rows: 5
- Columns: 3
- Column details: [{"name": "employee_name", "type": "categorical"}, {"name": "email", "type": "categorical"}, {"name": "id", "type": "numeric"}]

Should this data be visualized? If yes, which chart types are most appropriate?

Respond ONLY with valid JSON in this exact format:
{
    "should_visualize": true/false,
    "reason": "brief explanation",
    "recommended_charts": ["chart1", "chart2"],
    "confidence": 0.9
}"""
    
    response = model.generate_content(prompt)
    content = response.text.strip()
    
    # Clean markdown if present
    if content.startswith('```json'):
        content = content[7:]
    if content.startswith('```'):
        content = content[3:]
    if content.endswith('```'):
        content = content[:-3]
    content = content.strip()
    
    print(f"Raw response: {content}")
    
    # Parse JSON
    result = json.loads(content)
    print(f"\n✅ Parsed result:")
    print(json.dumps(result, indent=2))
    
    print("\n✅ All tests passed! Gemini API is working correctly.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
