#!/usr/bin/env python3
"""
Supply Chain Network Database Creation Script for Neo4j
This script creates a comprehensive supply chain network with realistic data
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupplyChainNetworkCreator:
    def __init__(self, uri="neo4j://localhost:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        """Clear all existing data"""
        with self.driver.session() as session:
            print("🗑️  Clearing existing database...")
            session.run("MATCH (n) DETACH DELETE n")
            print("✅ Database cleared!")

    def create_supply_chain_network(self):
        """Create comprehensive supply chain network"""
        with self.driver.session() as session:
            print("🏭 Creating Supply Chain Network...")
            
            # Create Suppliers
            print("📦 Creating Suppliers...")
            suppliers_query = """
            CREATE 
            // Raw Material Suppliers
            (steel_corp:Supplier {
                name: "Global Steel Corp", 
                location: "Pittsburgh, USA", 
                type: "Raw Materials",
                capacity: 50000,
                lead_time: 14,
                quality_rating: 4.2,
                risk_level: "Low"
            }),
            (plastic_ind:Supplier {
                name: "Plastic Industries Ltd", 
                location: "Shanghai, China", 
                type: "Raw Materials",
                capacity: 75000,
                lead_time: 21,
                quality_rating: 3.8,
                risk_level: "Medium"
            }),
            (electronics_supply:Supplier {
                name: "Electronics Supply Co", 
                location: "Seoul, South Korea", 
                type: "Components",
                capacity: 30000,
                lead_time: 10,
                quality_rating: 4.7,
                risk_level: "Low"
            }),
            (rubber_works:Supplier {
                name: "Rubber Works Inc", 
                location: "Bangkok, Thailand", 
                type: "Raw Materials",
                capacity: 25000,
                lead_time: 18,
                quality_rating: 4.0,
                risk_level: "Medium"
            }),
            (glass_tech:Supplier {
                name: "Glass Tech Solutions", 
                location: "Munich, Germany", 
                type: "Components",
                capacity: 15000,
                lead_time: 12,
                quality_rating: 4.5,
                risk_level: "Low"
            })
            """
            session.run(suppliers_query)

            # Create Manufacturers
            print("🏭 Creating Manufacturers...")
            manufacturers_query = """
            CREATE 
            (auto_mfg:Manufacturer {
                name: "AutoTech Manufacturing", 
                location: "Detroit, USA", 
                type: "Automotive",
                capacity: 100000,
                employees: 2500,
                certifications: ["ISO9001", "ISO14001"],
                production_efficiency: 0.85
            }),
            (electronics_mfg:Manufacturer {
                name: "TechBuild Electronics", 
                location: "Shenzhen, China", 
                type: "Electronics",
                capacity: 200000,
                employees: 5000,
                certifications: ["ISO9001", "RoHS"],
                production_efficiency: 0.92
            }),
            (appliance_mfg:Manufacturer {
                name: "Home Appliance Corp", 
                location: "Osaka, Japan", 
                type: "Appliances",
                capacity: 80000,
                employees: 1800,
                certifications: ["ISO9001", "Energy Star"],
                production_efficiency: 0.88
            }),
            (furniture_mfg:Manufacturer {
                name: "Modern Furniture Ltd", 
                location: "Milan, Italy", 
                type: "Furniture",
                capacity: 50000,
                employees: 800,
                certifications: ["FSC", "ISO9001"],
                production_efficiency: 0.75
            })
            """
            session.run(manufacturers_query)

            # Create Distributors
            print("🚛 Creating Distributors...")
            distributors_query = """
            CREATE 
            (global_dist:Distributor {
                name: "Global Distribution Network", 
                location: "Memphis, USA", 
                type: "Multi-Modal",
                coverage: "Worldwide",
                fleet_size: 1200,
                warehouse_capacity: 500000,
                delivery_speed: "Standard"
            }),
            (express_log:Distributor {
                name: "Express Logistics", 
                location: "Amsterdam, Netherlands", 
                type: "Air Freight",
                coverage: "Europe/Asia",
                fleet_size: 85,
                warehouse_capacity: 150000,
                delivery_speed: "Express"
            }),
            (ocean_freight:Distributor {
                name: "Ocean Freight Solutions", 
                location: "Singapore", 
                type: "Maritime",
                coverage: "Asia-Pacific",
                fleet_size: 45,
                warehouse_capacity: 800000,
                delivery_speed: "Economy"
            }),
            (regional_dist:Distributor {
                name: "Regional Distribution Co", 
                location: "Chicago, USA", 
                type: "Ground Transport",
                coverage: "North America",
                fleet_size: 350,
                warehouse_capacity: 200000,
                delivery_speed: "Standard"
            })
            """
            session.run(distributors_query)

            # Create Retailers
            print("🏪 Creating Retailers...")
            retailers_query = """
            CREATE 
            (mega_retail:Retailer {
                name: "MegaMart", 
                location: "Bentonville, USA", 
                type: "Big Box",
                stores: 4500,
                annual_revenue: 559000000000,
                market_share: 0.23,
                customer_base: 265000000
            }),
            (tech_store:Retailer {
                name: "TechWorld", 
                location: "Cupertino, USA", 
                type: "Specialty Electronics",
                stores: 270,
                annual_revenue: 365000000000,
                market_share: 0.15,
                customer_base: 85000000
            }),
            (home_depot:Retailer {
                name: "Home & Garden Center", 
                location: "Atlanta, USA", 
                type: "Home Improvement",
                stores: 2300,
                annual_revenue: 151000000000,
                market_share: 0.12,
                customer_base: 45000000
            }),
            (online_giant:Retailer {
                name: "E-Commerce Giant", 
                location: "Seattle, USA", 
                type: "Online",
                stores: 0,
                annual_revenue: 469000000000,
                market_share: 0.38,
                customer_base: 200000000
            }),
            (luxury_retail:Retailer {
                name: "Luxury Lifestyle", 
                location: "Paris, France", 
                type: "Premium",
                stores: 150,
                annual_revenue: 25000000000,
                market_share: 0.02,
                customer_base: 5000000
            })
            """
            session.run(retailers_query)

            # Create Products
            print("📱 Creating Products...")
            products_query = """
            CREATE 
            // Automotive Products
            (car_engine:Product {
                name: "V6 Engine Block", 
                category: "Automotive",
                sku: "AUTO-ENG-V6-001",
                cost: 2500.00,
                weight: 180.5,
                dimensions: "60x45x50cm",
                lead_time: 30
            }),
            (car_battery:Product {
                name: "Lithium Car Battery", 
                category: "Automotive",
                sku: "AUTO-BAT-LI-002",
                cost: 450.00,
                weight: 15.2,
                dimensions: "25x15x20cm",
                lead_time: 14
            }),
            
            // Electronics Products
            (smartphone:Product {
                name: "Smart Phone Pro", 
                category: "Electronics",
                sku: "ELEC-PHN-PRO-003",
                cost: 800.00,
                weight: 0.2,
                dimensions: "15x7x0.8cm",
                lead_time: 21
            }),
            (laptop:Product {
                name: "Gaming Laptop X1", 
                category: "Electronics",
                sku: "ELEC-LAP-GAM-004",
                cost: 1200.00,
                weight: 2.5,
                dimensions: "35x25x2cm",
                lead_time: 28
            }),
            (tablet:Product {
                name: "Tablet Air", 
                category: "Electronics",
                sku: "ELEC-TAB-AIR-005",
                cost: 600.00,
                weight: 0.5,
                dimensions: "25x18x0.6cm",
                lead_time: 18
            }),
            
            // Appliances
            (refrigerator:Product {
                name: "Smart Refrigerator", 
                category: "Appliances",
                sku: "APPL-REF-SMT-006",
                cost: 1800.00,
                weight: 85.0,
                dimensions: "180x60x65cm",
                lead_time: 35
            }),
            (washing_machine:Product {
                name: "Eco Washing Machine", 
                category: "Appliances",
                sku: "APPL-WSH-ECO-007",
                cost: 750.00,
                weight: 65.0,
                dimensions: "85x60x55cm",
                lead_time: 25
            }),
            
            // Furniture
            (office_chair:Product {
                name: "Ergonomic Office Chair", 
                category: "Furniture",
                sku: "FURN-CHR-ERG-008",
                cost: 350.00,
                weight: 18.0,
                dimensions: "65x65x110cm",
                lead_time: 20
            }),
            (dining_table:Product {
                name: "Modern Dining Table", 
                category: "Furniture",
                sku: "FURN-TBL-MOD-009",
                cost: 800.00,
                weight: 45.0,
                dimensions: "180x90x75cm",
                lead_time: 40
            })
            """
            session.run(products_query)

            # Create Raw Materials
            print("⚙️ Creating Raw Materials...")
            materials_query = """
            CREATE 
            (steel:Material {
                name: "High-Grade Steel", 
                type: "Metal",
                grade: "A36",
                unit: "tons",
                cost_per_unit: 800.00,
                environmental_impact: "Medium"
            }),
            (aluminum:Material {
                name: "Aluminum Alloy", 
                type: "Metal",
                grade: "6061-T6",
                unit: "tons",
                cost_per_unit: 1800.00,
                environmental_impact: "Low"
            }),
            (plastic_abs:Material {
                name: "ABS Plastic", 
                type: "Polymer",
                grade: "General Purpose",
                unit: "kg",
                cost_per_unit: 2.50,
                environmental_impact: "High"
            }),
            (rubber:Material {
                name: "Natural Rubber", 
                type: "Organic",
                grade: "RSS1",
                unit: "kg",
                cost_per_unit: 1.80,
                environmental_impact: "Low"
            }),
            (glass:Material {
                name: "Tempered Glass", 
                type: "Ceramic",
                grade: "Safety Glass",
                unit: "sq_meters",
                cost_per_unit: 45.00,
                environmental_impact: "Low"
            }),
            (lithium:Material {
                name: "Lithium Carbonate", 
                type: "Chemical",
                grade: "Battery Grade",
                unit: "kg",
                cost_per_unit: 12.00,
                environmental_impact: "Medium"
            })
            """
            session.run(materials_query)

    def create_relationships(self):
        """Create all supply chain relationships"""
        with self.driver.session() as session:
            print("🔗 Creating Supply Chain Relationships...")
            
            # Supplier -> Material relationships
            print("   📦 Supplier-Material relationships...")
            supplier_material_query = """
            MATCH (steel_corp:Supplier {name: "Global Steel Corp"})
            MATCH (steel:Material {name: "High-Grade Steel"})
            MATCH (aluminum:Material {name: "Aluminum Alloy"})
            CREATE (steel_corp)-[:SUPPLIES {quantity: 1000, price_per_unit: 800, contract_duration: 12}]->(steel)
            CREATE (steel_corp)-[:SUPPLIES {quantity: 500, price_per_unit: 1800, contract_duration: 12}]->(aluminum)
            
            WITH steel_corp, steel, aluminum
            MATCH (plastic_ind:Supplier {name: "Plastic Industries Ltd"})
            MATCH (plastic:Material {name: "ABS Plastic"})
            CREATE (plastic_ind)-[:SUPPLIES {quantity: 50000, price_per_unit: 2.5, contract_duration: 6}]->(plastic)
            
            WITH plastic_ind, plastic
            MATCH (rubber_works:Supplier {name: "Rubber Works Inc"})
            MATCH (rubber:Material {name: "Natural Rubber"})
            CREATE (rubber_works)-[:SUPPLIES {quantity: 25000, price_per_unit: 1.8, contract_duration: 8}]->(rubber)
            
            WITH rubber_works, rubber
            MATCH (glass_tech:Supplier {name: "Glass Tech Solutions"})
            MATCH (glass:Material {name: "Tempered Glass"})
            CREATE (glass_tech)-[:SUPPLIES {quantity: 5000, price_per_unit: 45, contract_duration: 10}]->(glass)
            
            WITH glass_tech, glass
            MATCH (electronics_supply:Supplier {name: "Electronics Supply Co"})
            MATCH (lithium:Material {name: "Lithium Carbonate"})
            CREATE (electronics_supply)-[:SUPPLIES {quantity: 2000, price_per_unit: 12, contract_duration: 12}]->(lithium)
            """
            session.run(supplier_material_query)

            # Material -> Product relationships
            print("   🏭 Material-Product relationships...")
            material_product_query = """
            MATCH (steel:Material {name: "High-Grade Steel"})
            MATCH (car_engine:Product {name: "V6 Engine Block"})
            CREATE (steel)-[:USED_IN {quantity_required: 0.5, critical: true}]->(car_engine)
            
            WITH steel, car_engine
            MATCH (aluminum:Material {name: "Aluminum Alloy"})
            MATCH (laptop:Product {name: "Gaming Laptop X1"})
            CREATE (aluminum)-[:USED_IN {quantity_required: 2.0, critical: true}]->(laptop)
            
            WITH aluminum, laptop
            MATCH (plastic:Material {name: "ABS Plastic"})
            MATCH (smartphone:Product {name: "Smart Phone Pro"})
            CREATE (plastic)-[:USED_IN {quantity_required: 0.1, critical: false}]->(smartphone)
            
            WITH plastic, smartphone
            MATCH (lithium:Material {name: "Lithium Carbonate"})
            MATCH (car_battery:Product {name: "Lithium Car Battery"})
            CREATE (lithium)-[:USED_IN {quantity_required: 5.0, critical: true}]->(car_battery)
            
            WITH lithium, car_battery
            MATCH (glass:Material {name: "Tempered Glass"})
            MATCH (tablet:Product {name: "Tablet Air"})
            CREATE (glass)-[:USED_IN {quantity_required: 0.05, critical: true}]->(tablet)
            """
            session.run(material_product_query)

            # Manufacturer -> Product relationships
            print("   🏭 Manufacturer-Product relationships...")
            manufacturer_product_query = """
            MATCH (auto_mfg:Manufacturer {name: "AutoTech Manufacturing"})
            MATCH (car_engine:Product {name: "V6 Engine Block"})
            MATCH (car_battery:Product {name: "Lithium Car Battery"})
            CREATE (auto_mfg)-[:MANUFACTURES {monthly_capacity: 5000, setup_cost: 50000}]->(car_engine)
            CREATE (auto_mfg)-[:MANUFACTURES {monthly_capacity: 8000, setup_cost: 25000}]->(car_battery)
            
            WITH auto_mfg, car_engine, car_battery
            MATCH (electronics_mfg:Manufacturer {name: "TechBuild Electronics"})
            MATCH (smartphone:Product {name: "Smart Phone Pro"})
            MATCH (laptop:Product {name: "Gaming Laptop X1"})
            MATCH (tablet:Product {name: "Tablet Air"})
            CREATE (electronics_mfg)-[:MANUFACTURES {monthly_capacity: 50000, setup_cost: 100000}]->(smartphone)
            CREATE (electronics_mfg)-[:MANUFACTURES {monthly_capacity: 10000, setup_cost: 75000}]->(laptop)
            CREATE (electronics_mfg)-[:MANUFACTURES {monthly_capacity: 15000, setup_cost: 60000}]->(tablet)
            
            WITH electronics_mfg, smartphone, laptop, tablet
            MATCH (appliance_mfg:Manufacturer {name: "Home Appliance Corp"})
            MATCH (refrigerator:Product {name: "Smart Refrigerator"})
            MATCH (washing_machine:Product {name: "Eco Washing Machine"})
            CREATE (appliance_mfg)-[:MANUFACTURES {monthly_capacity: 3000, setup_cost: 80000}]->(refrigerator)
            CREATE (appliance_mfg)-[:MANUFACTURES {monthly_capacity: 4000, setup_cost: 60000}]->(washing_machine)
            
            WITH appliance_mfg, refrigerator, washing_machine
            MATCH (furniture_mfg:Manufacturer {name: "Modern Furniture Ltd"})
            MATCH (office_chair:Product {name: "Ergonomic Office Chair"})
            MATCH (dining_table:Product {name: "Modern Dining Table"})
            CREATE (furniture_mfg)-[:MANUFACTURES {monthly_capacity: 2000, setup_cost: 30000}]->(office_chair)
            CREATE (furniture_mfg)-[:MANUFACTURES {monthly_capacity: 800, setup_cost: 40000}]->(dining_table)
            """
            session.run(manufacturer_product_query)

            # Manufacturer -> Distributor relationships
            print("   🚛 Manufacturer-Distributor relationships...")
            manufacturer_distributor_query = """
            MATCH (auto_mfg:Manufacturer {name: "AutoTech Manufacturing"})
            MATCH (global_dist:Distributor {name: "Global Distribution Network"})
            MATCH (regional_dist:Distributor {name: "Regional Distribution Co"})
            CREATE (auto_mfg)-[:SHIPS_TO {capacity: 10000, transit_time: 3, cost_per_unit: 50}]->(global_dist)
            CREATE (auto_mfg)-[:SHIPS_TO {capacity: 5000, transit_time: 1, cost_per_unit: 25}]->(regional_dist)
            
            WITH auto_mfg, global_dist, regional_dist
            MATCH (electronics_mfg:Manufacturer {name: "TechBuild Electronics"})
            MATCH (express_log:Distributor {name: "Express Logistics"})
            MATCH (ocean_freight:Distributor {name: "Ocean Freight Solutions"})
            CREATE (electronics_mfg)-[:SHIPS_TO {capacity: 25000, transit_time: 2, cost_per_unit: 15}]->(express_log)
            CREATE (electronics_mfg)-[:SHIPS_TO {capacity: 50000, transit_time: 14, cost_per_unit: 8}]->(ocean_freight)
            
            WITH electronics_mfg, express_log, ocean_freight
            MATCH (appliance_mfg:Manufacturer {name: "Home Appliance Corp"})
            CREATE (appliance_mfg)-[:SHIPS_TO {capacity: 3000, transit_time: 7, cost_per_unit: 75}]->(ocean_freight)
            CREATE (appliance_mfg)-[:SHIPS_TO {capacity: 2000, transit_time: 3, cost_per_unit: 120}]->(express_log)
            
            WITH appliance_mfg, ocean_freight, express_log
            MATCH (furniture_mfg:Manufacturer {name: "Modern Furniture Ltd"})
            CREATE (furniture_mfg)-[:SHIPS_TO {capacity: 1500, transit_time: 5, cost_per_unit: 85}]->(global_dist)
            """
            session.run(manufacturer_distributor_query)

            # Distributor -> Retailer relationships
            print("   🏪 Distributor-Retailer relationships...")
            distributor_retailer_query = """
            MATCH (global_dist:Distributor {name: "Global Distribution Network"})
            MATCH (mega_retail:Retailer {name: "MegaMart"})
            MATCH (home_depot:Retailer {name: "Home & Garden Center"})
            CREATE (global_dist)-[:DELIVERS_TO {capacity: 50000, delivery_frequency: "Daily", cost_per_delivery: 500}]->(mega_retail)
            CREATE (global_dist)-[:DELIVERS_TO {capacity: 20000, delivery_frequency: "Bi-Daily", cost_per_delivery: 300}]->(home_depot)
            
            WITH global_dist, mega_retail, home_depot
            MATCH (express_log:Distributor {name: "Express Logistics"})
            MATCH (tech_store:Retailer {name: "TechWorld"})
            MATCH (online_giant:Retailer {name: "E-Commerce Giant"})
            CREATE (express_log)-[:DELIVERS_TO {capacity: 15000, delivery_frequency: "Hourly", cost_per_delivery: 200}]->(tech_store)
            CREATE (express_log)-[:DELIVERS_TO {capacity: 30000, delivery_frequency: "Continuous", cost_per_delivery: 150}]->(online_giant)
            
            WITH express_log, tech_store, online_giant
            MATCH (ocean_freight:Distributor {name: "Ocean Freight Solutions"})
            CREATE (ocean_freight)-[:DELIVERS_TO {capacity: 80000, delivery_frequency: "Weekly", cost_per_delivery: 800}]->(mega_retail)
            CREATE (ocean_freight)-[:DELIVERS_TO {capacity: 25000, delivery_frequency: "Bi-Weekly", cost_per_delivery: 400}]->(online_giant)
            
            WITH ocean_freight, mega_retail, online_giant
            MATCH (regional_dist:Distributor {name: "Regional Distribution Co"})
            MATCH (luxury_retail:Retailer {name: "Luxury Lifestyle"})
            CREATE (regional_dist)-[:DELIVERS_TO {capacity: 5000, delivery_frequency: "Weekly", cost_per_delivery: 250}]->(luxury_retail)
            CREATE (regional_dist)-[:DELIVERS_TO {capacity: 12000, delivery_frequency: "Tri-Weekly", cost_per_delivery: 350}]->(home_depot)
            """
            session.run(distributor_retailer_query)

            # Product -> Retailer relationships (inventory)
            print("   📦 Product-Retailer inventory relationships...")
            product_retailer_query = """
            MATCH (smartphone:Product {name: "Smart Phone Pro"})
            MATCH (tech_store:Retailer {name: "TechWorld"})
            MATCH (online_giant:Retailer {name: "E-Commerce Giant"})
            CREATE (tech_store)-[:STOCKS {quantity: 5000, reorder_point: 500, max_stock: 8000}]->(smartphone)
            CREATE (online_giant)-[:STOCKS {quantity: 15000, reorder_point: 2000, max_stock: 25000}]->(smartphone)
            
            WITH smartphone, tech_store, online_giant
            MATCH (laptop:Product {name: "Gaming Laptop X1"})
            CREATE (tech_store)-[:STOCKS {quantity: 800, reorder_point: 100, max_stock: 1200}]->(laptop)
            CREATE (online_giant)-[:STOCKS {quantity: 2500, reorder_point: 300, max_stock: 4000}]->(laptop)
            
            WITH laptop, tech_store, online_giant
            MATCH (refrigerator:Product {name: "Smart Refrigerator"})
            MATCH (mega_retail:Retailer {name: "MegaMart"})
            MATCH (home_depot:Retailer {name: "Home & Garden Center"})
            CREATE (mega_retail)-[:STOCKS {quantity: 300, reorder_point: 50, max_stock: 500}]->(refrigerator)
            CREATE (home_depot)-[:STOCKS {quantity: 150, reorder_point: 25, max_stock: 250}]->(refrigerator)
            
            WITH refrigerator, mega_retail, home_depot
            MATCH (office_chair:Product {name: "Ergonomic Office Chair"})
            MATCH (luxury_retail:Retailer {name: "Luxury Lifestyle"})
            CREATE (mega_retail)-[:STOCKS {quantity: 1200, reorder_point: 200, max_stock: 2000}]->(office_chair)
            CREATE (luxury_retail)-[:STOCKS {quantity: 80, reorder_point: 15, max_stock: 150}]->(office_chair)
            """
            session.run(product_retailer_query)

    def create_risk_and_performance_data(self):
        """Add risk indicators and performance metrics"""
        with self.driver.session() as session:
            print("⚠️ Adding Risk and Performance Data...")
            
            risk_query = """
            // Add risk relationships
            MATCH (plastic_ind:Supplier {name: "Plastic Industries Ltd"})
            CREATE (risk1:Risk {
                type: "Geopolitical", 
                description: "Trade war tensions", 
                probability: 0.3, 
                impact: "High",
                mitigation: "Diversify suppliers"
            })
            CREATE (plastic_ind)-[:HAS_RISK {severity: "Medium"}]->(risk1)
            
            WITH plastic_ind, risk1
            MATCH (ocean_freight:Distributor {name: "Ocean Freight Solutions"})
            CREATE (risk2:Risk {
                type: "Environmental", 
                description: "Severe weather disruptions", 
                probability: 0.4, 
                impact: "Medium",
                mitigation: "Alternative routes"
            })
            CREATE (ocean_freight)-[:HAS_RISK {severity: "Medium"}]->(risk2)
            
            WITH ocean_freight, risk2
            MATCH (electronics_supply:Supplier {name: "Electronics Supply Co"})
            CREATE (risk3:Risk {
                type: "Supply Chain", 
                description: "Semiconductor shortage", 
                probability: 0.6, 
                impact: "Very High",
                mitigation: "Strategic inventory"
            })
            CREATE (electronics_supply)-[:HAS_RISK {severity: "High"}]->(risk3)
            
            // Add performance metrics
            WITH electronics_supply, risk3
            MATCH (auto_mfg:Manufacturer {name: "AutoTech Manufacturing"})
            CREATE (perf1:Performance {
                metric: "On-Time Delivery", 
                value: 0.92, 
                period: "Q4 2024",
                target: 0.95,
                trend: "Improving"
            })
            CREATE (auto_mfg)-[:HAS_PERFORMANCE]->(perf1)
            
            WITH auto_mfg, perf1
            MATCH (global_dist:Distributor {name: "Global Distribution Network"})
            CREATE (perf2:Performance {
                metric: "Cost Efficiency", 
                value: 0.88, 
                period: "Q4 2024",
                target: 0.90,
                trend: "Stable"
            })
            CREATE (global_dist)-[:HAS_PERFORMANCE]->(perf2)
            """
            session.run(risk_query)

    def verify_data(self):
        """Verify that all data was created correctly"""
        with self.driver.session() as session:
            print("\n📊 Database Summary:")
            
            # Count nodes by type
            count_query = """
            MATCH (n) 
            RETURN labels(n)[0] as node_type, count(n) as count 
            ORDER BY count DESC
            """
            result = session.run(count_query)
            
            for record in result:
                print(f"   {record['node_type']}: {record['count']} nodes")
            
            # Count relationships
            rel_query = """
            MATCH ()-[r]->() 
            RETURN type(r) as relationship_type, count(r) as count 
            ORDER BY count DESC
            """
            result = session.run(rel_query)
            
            print("\n🔗 Relationships:")
            for record in result:
                print(f"   {record['relationship_type']}: {record['count']} relationships")

def main():
    print("🏭 Creating Supply Chain Network Database for Neo4j")
    print("=" * 60)
    
    creator = SupplyChainNetworkCreator()
    
    try:
        # Clear existing data
        creator.clear_database()
        
        # Create new supply chain network
        creator.create_supply_chain_network()
        creator.create_relationships()
        creator.create_risk_and_performance_data()
        
        # Verify creation
        creator.verify_data()
        
        print("\n✅ Supply Chain Network Database Created Successfully!")
        print("\nKey Features:")
        print("🏭 Multi-tier supply chain (Suppliers → Manufacturers → Distributors → Retailers)")
        print("📦 Raw materials and finished products with dependencies")
        print("⚠️ Risk analysis and performance metrics")
        print("🌍 Global network with realistic locations and capacities")
        print("💰 Cost optimization and bottleneck identification capabilities")
        
    except Exception as e:
        print(f"❌ Error creating database: {str(e)}")
    finally:
        creator.close()

if __name__ == "__main__":
    main()
