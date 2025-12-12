"""
Test script to check database column values for TTTK_HQ and SO_HD
"""
import sys
sys.path.insert(0, '.')

from config.configuration_manager import ConfigurationManager
from database.ecus_connector import EcusDataConnector
from logging_system.logger import Logger
from datetime import datetime, timedelta

def main():
    # Initialize
    config_manager = ConfigurationManager('config.ini')
    logger = Logger(config_manager.get_logging_config())
    db_config = config_manager.get_database_config()
    
    connector = EcusDataConnector(db_config, logger)
    
    if not connector.connect():
        print("Failed to connect to database")
        return
    
    try:
        cursor = connector._connection.cursor()
        
        # First, list all columns that contain 'TT' or 'HQ' to find status column
        print("Checking columns containing 'TT' or status-related:")
        col_query = """
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'DTOKHAIMD'
            AND (COLUMN_NAME LIKE '%TT%' OR COLUMN_NAME LIKE '%TRANG%' OR COLUMN_NAME LIKE '%STATUS%')
            ORDER BY COLUMN_NAME
        """
        cursor.execute(col_query)
        for row in cursor:
            print(f"  Column: {row.COLUMN_NAME} ({row.DATA_TYPE})")
        print()
        
        # Check invoice columns - SO_HD vs SO_HDTM
        print("Checking invoice columns (SO_HD vs SO_HDTM):")
        invoice_query = """
            SELECT TOP 10
                SOTK,
                SO_HD,
                SO_HDTM,
                VAN_DON
            FROM DTOKHAIMD
            WHERE NGAY_DK >= DATEADD(day, -7, GETDATE())
                AND TTTK = 'T'
            ORDER BY NGAY_DK DESC
        """
        cursor.execute(invoice_query)
        for row in cursor:
            print(f"  SOTK: {row.SOTK}")
            print(f"    SO_HD (Số hợp đồng): '{row.SO_HD}'")
            print(f"    SO_HDTM (Số hóa đơn TM): '{row.SO_HDTM}'")
            print(f"    VAN_DON: '{row.VAN_DON}'")
            print("-" * 80)
        
        cursor.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        connector.disconnect()

if __name__ == "__main__":
    main()
