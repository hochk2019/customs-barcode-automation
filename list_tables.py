"""
List all tables in ECUS5 database

This script connects to the database and lists all available tables.
"""

import sys
from config.configuration_manager import ConfigurationManager
from database.ecus_connector import EcusDataConnector
from logging_system.logger import Logger, LoggingConfig

def list_tables():
    """List all tables in database"""
    print("=" * 60)
    print("ECUS5 Database - List All Tables")
    print("=" * 60)
    print()
    
    try:
        # Load configuration
        print("1. Loading configuration...")
        config_manager = ConfigurationManager("config.ini")
        db_config = config_manager.get_database_config()
        print(f"   Server: {db_config.server}")
        print(f"   Database: {db_config.database}")
        print()
        
        # Initialize logger
        logging_config = LoggingConfig(
            log_level='INFO',
            log_file='logs/list_tables.log',
            max_log_size=10485760,
            backup_count=5
        )
        logger = Logger(logging_config)
        
        # Create connector
        print("2. Connecting to database...")
        connector = EcusDataConnector(db_config, logger)
        
        if not connector.connect():
            print("   ✗ Connection failed!")
            return False
        
        print("   ✓ Connected successfully!")
        print()
        
        # List all tables
        print("3. Listing all tables...")
        print()
        
        cursor = connector._connection.cursor()
        
        # Query to get all user tables
        query = """
            SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        
        cursor.execute(query)
        
        tables = cursor.fetchall()
        
        if not tables:
            print("   No tables found!")
            return False
        
        print(f"   Found {len(tables)} tables:")
        print()
        print("   Schema          | Table Name")
        print("   " + "-" * 56)
        
        # Group by schema
        current_schema = None
        for schema, table_name, table_type in tables:
            if current_schema != schema:
                current_schema = schema
                print()
                print(f"   [{schema}]")
            
            print(f"   {schema:15} | {table_name}")
        
        print()
        print("=" * 60)
        
        # Search for tables containing "ToKhai" or "Hang"
        print()
        print("4. Searching for declaration-related tables...")
        print()
        
        search_terms = ['ToKhai', 'Hang', 'DoanhNghiep', 'DN']
        
        for term in search_terms:
            print(f"   Tables containing '{term}':")
            found = False
            for schema, table_name, table_type in tables:
                if term.lower() in table_name.lower():
                    print(f"      - {schema}.{table_name}")
                    found = True
            if not found:
                print(f"      (none)")
            print()
        
        cursor.close()
        connector.disconnect()
        
        print("=" * 60)
        print("✓ COMPLETED")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = list_tables()
    sys.exit(0 if success else 1)
