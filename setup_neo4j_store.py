#!/usr/bin/env python3
"""
Neo4j Sample Store Database Setup for Aura
Creates a realistic e-commerce graph database with customers, products, orders, categories, etc.
"""

from neo4j import GraphDatabase
import json
from datetime import datetime, timedelta
import random

class StoreDataGenerator:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Clear all existing data"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✅ Database cleared")
    
    def create_sample_store_data(self):
        """Create comprehensive store data"""
        with self.driver.session() as session:
            
            # 1. Create Categories
            print("📦 Creating product categories...")
            categories = [
                {"name": "Electronics", "description": "Gadgets and electronic devices"},
                {"name": "Clothing", "description": "Fashion and apparel"},
                {"name": "Books", "description": "Books and literature"},
                {"name": "Home & Garden", "description": "Home improvement and gardening"},
                {"name": "Sports", "description": "Sports and fitness equipment"},
                {"name": "Beauty", "description": "Beauty and personal care"},
            ]
            
            for cat in categories:
                session.run("""
                    CREATE (c:Category {
                        name: $name,
                        description: $description,
                        created_at: datetime()
                    })
                """, cat)
            
            # 2. Create Products
            print("🛍️ Creating products...")
            products = [
                # Electronics
                {"name": "iPhone 15 Pro", "price": 999.99, "category": "Electronics", "stock": 50, "rating": 4.8},
                {"name": "MacBook Air M3", "price": 1199.99, "category": "Electronics", "stock": 25, "rating": 4.9},
                {"name": "AirPods Pro", "price": 249.99, "category": "Electronics", "stock": 100, "rating": 4.7},
                {"name": "Samsung 4K TV", "price": 799.99, "category": "Electronics", "stock": 15, "rating": 4.6},
                
                # Clothing
                {"name": "Nike Air Max", "price": 129.99, "category": "Clothing", "stock": 75, "rating": 4.5},
                {"name": "Levi's Jeans", "price": 79.99, "category": "Clothing", "stock": 120, "rating": 4.4},
                {"name": "Adidas Hoodie", "price": 59.99, "category": "Clothing", "stock": 90, "rating": 4.3},
                
                # Books
                {"name": "Python Programming", "price": 49.99, "category": "Books", "stock": 200, "rating": 4.7},
                {"name": "Data Science Handbook", "price": 69.99, "category": "Books", "stock": 150, "rating": 4.8},
                {"name": "Machine Learning Guide", "price": 89.99, "category": "Books", "stock": 80, "rating": 4.6},
                
                # Home & Garden
                {"name": "Smart Thermostat", "price": 199.99, "category": "Home & Garden", "stock": 40, "rating": 4.5},
                {"name": "Robot Vacuum", "price": 299.99, "category": "Home & Garden", "stock": 30, "rating": 4.4},
                
                # Sports
                {"name": "Yoga Mat", "price": 29.99, "category": "Sports", "stock": 200, "rating": 4.2},
                {"name": "Dumbbells Set", "price": 149.99, "category": "Sports", "stock": 45, "rating": 4.6},
                
                # Beauty
                {"name": "Skincare Set", "price": 79.99, "category": "Beauty", "stock": 85, "rating": 4.5},
                {"name": "Hair Dryer", "price": 119.99, "category": "Beauty", "stock": 60, "rating": 4.3},
            ]
            
            for product in products:
                session.run("""
                    MATCH (c:Category {name: $category})
                    CREATE (p:Product {
                        name: $name,
                        price: $price,
                        stock: $stock,
                        rating: $rating,
                        created_at: datetime(),
                        sku: 'SKU-' + toString(toInteger(rand() * 1000000))
                    })
                    CREATE (p)-[:BELONGS_TO]->(c)
                """, product)
            
            # 3. Create Customers
            print("👥 Creating customers...")
            customers = [
                {"name": "John Smith", "email": "john@email.com", "city": "New York", "age": 32},
                {"name": "Sarah Johnson", "email": "sarah@email.com", "city": "Los Angeles", "age": 28},
                {"name": "Mike Brown", "email": "mike@email.com", "city": "Chicago", "age": 35},
                {"name": "Emily Davis", "email": "emily@email.com", "city": "Houston", "age": 24},
                {"name": "David Wilson", "email": "david@email.com", "city": "Phoenix", "age": 41},
                {"name": "Lisa Garcia", "email": "lisa@email.com", "city": "Philadelphia", "age": 29},
                {"name": "Tom Anderson", "email": "tom@email.com", "city": "San Antonio", "age": 38},
                {"name": "Anna Martinez", "email": "anna@email.com", "city": "San Diego", "age": 26},
                {"name": "Chris Taylor", "email": "chris@email.com", "city": "Dallas", "age": 33},
                {"name": "Jessica White", "email": "jessica@email.com", "city": "San Jose", "age": 31},
            ]
            
            for customer in customers:
                days_ago = random.randint(30, 1000)
                session.run("""
                    CREATE (c:Customer {
                        name: $name,
                        email: $email,
                        city: $city,
                        age: $age,
                        member_since: datetime() - duration({days: $days_ago}),
                        total_spent: 0.0
                    })
                """, {**customer, "days_ago": days_ago})
            
            # 4. Create Orders and Purchases
            print("🛒 Creating orders and purchases...")
            
            # Get all customers and products
            customers_result = session.run("MATCH (c:Customer) RETURN c.email as email")
            products_result = session.run("MATCH (p:Product) RETURN p.name as name, p.price as price")
            
            customers_list = [record["email"] for record in customers_result]
            products_list = [(record["name"], record["price"]) for record in products_result]
            
            # Create random orders
            for i in range(50):  # 50 orders
                customer_email = random.choice(customers_list)
                order_date = datetime.now() - timedelta(days=random.randint(1, 365))
                order_id = f"ORD-{1000 + i}"
                
                # Create order
                session.run("""
                    MATCH (c:Customer {email: $email})
                    CREATE (o:Order {
                        order_id: $order_id,
                        status: $status,
                        order_date: $order_date,
                        total_amount: 0.0
                    })
                    CREATE (c)-[:PLACED]->(o)
                """, {
                    "email": customer_email,
                    "order_id": order_id,
                    "status": random.choice(["completed", "shipped", "processing", "delivered"]),
                    "order_date": order_date
                })
                
                # Add random products to order
                num_items = random.randint(1, 5)
                selected_products = random.sample(products_list, min(num_items, len(products_list)))
                order_total = 0
                
                for product_name, product_price in selected_products:
                    quantity = random.randint(1, 3)
                    order_total += product_price * quantity
                    
                    session.run("""
                        MATCH (o:Order {order_id: $order_id})
                        MATCH (p:Product {name: $product_name})
                        CREATE (o)-[:CONTAINS {quantity: $quantity, unit_price: $price}]->(p)
                    """, {
                        "order_id": order_id,
                        "product_name": product_name,
                        "quantity": quantity,
                        "price": product_price
                    })
                
                # Update order total
                session.run("""
                    MATCH (o:Order {order_id: $order_id})
                    SET o.total_amount = $total
                """, {"order_id": order_id, "total": order_total})
                
                # Update customer total spent
                session.run("""
                    MATCH (c:Customer {email: $email})
                    SET c.total_spent = c.total_spent + $amount
                """, {"email": customer_email, "amount": order_total})
            
            # 5. Create Reviews
            print("⭐ Creating product reviews...")
            for i in range(75):  # 75 reviews
                customer_email = random.choice(customers_list)
                product_name = random.choice([p[0] for p in products_list])
                rating = random.choice([3, 4, 4, 4, 5, 5, 5])  # Bias toward higher ratings
                
                reviews_text = [
                    "Great product, highly recommend!",
                    "Good value for money",
                    "Excellent quality and fast shipping",
                    "Love it! Will buy again",
                    "Decent product, met expectations",
                    "Outstanding customer service",
                    "Perfect for my needs",
                    "Great build quality",
                    "Fast delivery and good packaging",
                    "Excellent experience overall"
                ]
                
                session.run("""
                    MATCH (c:Customer {email: $email})
                    MATCH (p:Product {name: $product_name})
                    MERGE (c)-[:REVIEWED {
                        rating: $rating,
                        comment: $comment,
                        review_date: datetime() - duration({days: $days_ago})
                    }]->(p)
                """, {
                    "email": customer_email,
                    "product_name": product_name,
                    "rating": rating,
                    "comment": random.choice(reviews_text),
                    "days_ago": random.randint(1, 200)
                })
            
            print("✅ Sample store database created successfully!")
    
    def get_database_stats(self):
        """Get database statistics"""
        with self.driver.session() as session:
            stats = {}
            
            # Count nodes by type
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY count DESC
            """)
            
            for record in result:
                stats[record["type"]] = record["count"]
            
            # Count relationships
            rel_result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as relationship, count(r) as count
                ORDER BY count DESC
            """)
            
            relationships = {}
            for record in rel_result:
                relationships[record["relationship"]] = record["count"]
            
            stats["relationships"] = relationships
            
            return stats

def main():
    # Connection details
    uri = "neo4j://127.0.0.1:7687"
    username = "neo4j"
    password = "password"  # Your actual password
    
    print("🚀 Setting up Neo4j Sample Store Database...")
    print("=" * 60)
    
    try:
        generator = StoreDataGenerator(uri, username, password)
        
        # Clear existing data
        generator.clear_database()
        
        # Create sample data
        generator.create_sample_store_data()
        
        # Show statistics
        stats = generator.get_database_stats()
        print("\n📊 Database Statistics:")
        print("-" * 30)
        for node_type, count in stats.items():
            if node_type != "relationships":
                print(f"{node_type}: {count}")
        
        print("\n🔗 Relationships:")
        print("-" * 30)
        for rel_type, count in stats["relationships"].items():
            print(f"{rel_type}: {count}")
        
        print(f"\n✅ Store database ready for Aura integration!")
        print(f"🔗 Connection: {uri}")
        print(f"👤 Username: {username}")
        
        generator.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Neo4j instance is running")
        print("2. Check username/password")
        print("3. Verify connection URI")

if __name__ == "__main__":
    main()
