#!/usr/bin/env python3
"""
Test Neo4j connection for Aura project
"""

def test_neo4j_connection():
    try:
        # Try importing neo4j driver
        from neo4j import GraphDatabase
        print("✅ Neo4j driver available")
        
        # Connection details (update these with your actual credentials)
        uri = "bolt://localhost:7687"
        username = "neo4j"
        password = "password"  # Replace with your actual password
        
        # Test connection
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            # Simple test query
            result = session.run("RETURN 'Hello Neo4j!' as greeting")
            record = result.single()
            print(f"✅ Connection successful: {record['greeting']}")
            
            # Test basic node creation and retrieval
            session.run("CREATE (test:TestNode {name: 'Aura Test', timestamp: datetime()})")
            result = session.run("MATCH (test:TestNode) RETURN test.name as name, test.timestamp as timestamp")
            
            for record in result:
                print(f"✅ Created test node: {record['name']} at {record['timestamp']}")
            
            # Clean up test node
            session.run("MATCH (test:TestNode) DELETE test")
            print("✅ Test completed successfully!")
            
        driver.close()
        return True
        
    except ImportError:
        print("❌ Neo4j driver not installed. Install with: pip install neo4j")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Neo4j instance is STARTED in Neo4j Desktop")
        print("2. Verify the connection details (URI, username, password)")
        print("3. Check if ports 7474 and 7687 are accessible")
        return False

if __name__ == "__main__":
    print("🚀 Testing Neo4j Connection for Aura...")
    print("=" * 50)
    test_neo4j_connection()
