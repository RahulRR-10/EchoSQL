#!/usr/bin/env python3
"""
Test the /recommend endpoint specifically for Neo4j
"""
import requests
import json

# Test the /recommend endpoint
url = "http://127.0.0.1:1111/recommend"

# Test payload with uri field explicitly included
payload = {
    "database_config": {
        "dbtype": "neo4j",
        "host": "localhost",
        "user": "neo4j", 
        "password": "password",
        "dbname": "store",
        "uri": "neo4j://localhost:7687"
    }
}

print("Testing /recommend endpoint with Neo4j...")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ SUCCESS - Neo4j connection and recommendation generation worked!")
    else:
        print("❌ FAILED - Check the error above")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
