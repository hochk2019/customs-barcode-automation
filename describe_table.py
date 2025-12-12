"""
Describe table structure

This script shows the columns of specific tables.
"""

import sys
from config.configuration_manager import ConfigurationManager
from database.ecus_connector import EcusDataConnector
from logging_system.logger import Logger, LoggingConfig

def describe_tables():
    """Describe table structure"""
    print("=" * 60)
    print("ECUS5 Database - Describe Tables")
    print("=" * 60)
    print()
    
    try:
        # Load configuration
        config_manager = ConfigurationManager("config.ini")
        db_config = config_manager.get_database_config()
        
        # Initialize logger
        logging_config = LoggingConfig(
            log_level='INFO',
            log_file='logs/describe_table.log',
            max_log_size=10485760,
            backup_count=5
        )
        logger = Logger(logging_config)
        
        # Create connector
        print("Connecting to database...")
        connector = EcusDataConnector(db_config, logger)
        
        if not connector.connect():
            print("✗ Connection failed!")
            return False
        
        print("✓ Connected successfully!")
        print()
        
        # Tables to describe
        tables = ['DTOKHAIMD', 'DHANGMDDK', 'DaiLy_DoanhNghiep']
        
        cursor = connector._connection.cursor()
        
        for table_name in tables:
            print("=" * 60)
            print(f"Table: {table_name}")
            print("=" * 60)
            
            try:
                # Query to get column information
                query = """
                    SELECT 
                        COLUMN_NAME,
                        DATA_TYPE,
                        CHARACTER_MAXIMUM_LENGTH,
                        IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = ?
                    ORDER BY ORDINAL_POSITION
                """
                
                cursor.execute(query, (table_name,))
                columns = cursor.fetchall()
                
                if not columns:
                    print(f"   Table '{table_name}' not found or no columns!")
                    print()
                    continue
                
                print()
                print(f"   Found {len(columns)} columns:")
                print()
                print("   Column Name                  | Type          | Length | Nullable")
                print("   " + "-" * 56)
                
                for col_name, data_type, max_length, is_nullable in columns:
                    length_str = str(max_length) if max_length else "-"
                    nullable_str = "YES" if is_nullable == "YES" else "NO"
                    print(f"   {col_name:28} | {data_type:13} | {length_str:6} | {nullable_str}")
                
                print()
                
            except Exception as e:
                print(f"   Error describing table '{table_name}': {e}")
                print()
        
        cursor.close()
        connector.disconnect()
        
        print("=" * 60)
        print("✓ COMPLETED")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = describe_tables()
    sys.exit(0 if success else 1)
