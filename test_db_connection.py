"""
Test Database Connection Script

This script tests the connection to ECUS5 database and displays connection details.
"""

import sys
from config.configuration_manager import ConfigurationManager
from database.ecus_connector import EcusDataConnector
from logging_system.logger import Logger, LoggingConfig

def test_connection():
    """Test database connection"""
    print("=" * 60)
    print("ECUS5 Database Connection Test")
    print("=" * 60)
    print()
    
    try:
        # Load configuration
        print("1. Loading configuration...")
        config_manager = ConfigurationManager("config.ini")
        db_config = config_manager.get_database_config()
        
        print(f"   Server: {db_config.server}")
        print(f"   Database: {db_config.database}")
        print(f"   Username: {db_config.username}")
        print(f"   Timeout: {db_config.timeout}s")
        print()
        
        # Initialize logger
        print("2. Initializing logger...")
        logging_config = LoggingConfig(
            log_level='INFO',
            log_file='logs/test_connection.log',
            max_log_size=10485760,
            backup_count=5
        )
        logger = Logger(logging_config)
        print("   ✓ Logger initialized")
        print()
        
        # Create connector
        print("3. Creating database connector...")
        connector = EcusDataConnector(db_config, logger)
        print("   ✓ Connector created")
        print()
        
        # Test connection
        print("4. Testing connection...")
        if connector.connect():
            print("   ✓ Connection successful!")
            print()
            
            # Test query
            print("5. Testing query (fetching 5 recent declarations)...")
            try:
                declarations = connector.get_new_declarations(set(), days_back=7)
                print(f"   ✓ Query successful! Found {len(declarations)} declarations")
                
                if declarations:
                    print()
                    print("   Sample declarations:")
                    for i, decl in enumerate(declarations[:5], 1):
                        print(f"   {i}. {decl.declaration_number} - {decl.tax_code} - {decl.channel}")
                
                print()
                print("=" * 60)
                print("✓ ALL TESTS PASSED")
                print("=" * 60)
                
                # Test company name lookup
                if declarations:
                    print()
                    print("6. Testing company name lookup...")
                    test_tax_code = declarations[0].tax_code
                    company_name = connector.get_company_name(test_tax_code)
                    if company_name:
                        print(f"   ✓ Company name for {test_tax_code}: {company_name}")
                    else:
                        print(f"   ⚠ No company name found for {test_tax_code}")
                
            except Exception as e:
                print(f"   ✗ Query failed: {e}")
                print()
                print("=" * 60)
                print("✗ QUERY TEST FAILED")
                print("=" * 60)
                return False
            
            # Disconnect
            connector.disconnect()
            print()
            print("Connection closed.")
            return True
            
        else:
            print("   ✗ Connection failed!")
            print()
            print("=" * 60)
            print("✗ CONNECTION TEST FAILED")
            print("=" * 60)
            print()
            print("Possible issues:")
            print("- Check if SQL Server is running")
            print("- Verify server address and port")
            print("- Check username and password")
            print("- Ensure ODBC Driver for SQL Server is installed")
            print("- Check network connectivity")
            print("- Verify firewall settings")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        print()
        print("=" * 60)
        print("✗ TEST FAILED")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
