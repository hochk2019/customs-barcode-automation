#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test kết nối database ECUSVNACCS
"""

from database.ecus_connector import EcusDataConnector
from config.configuration_manager import ConfigurationManager

def test_database_connection():
    """Test kết nối database"""
    
    print("🔌 TESTING DATABASE CONNECTION")
    print("=" * 60)
    
    # Load config
    config_manager = ConfigurationManager("config.ini")
    db_config = config_manager.get_database_config()
    
    print(f"📋 Database configuration:")
    print(f"   Server: {db_config.server}")
    print(f"   Database: {db_config.database}")
    print(f"   Username: {db_config.username}")
    print(f"   Timeout: {db_config.timeout}")
    
    # Test connection
    print(f"\n🔌 Attempting to connect...")
    
    try:
        connector = EcusDataConnector(db_config)
        
        if connector.connect():
            print(f"   ✅ Connection successful!")
            
            # Test query
            print(f"\n📊 Testing query...")
            cursor = connector._connection.cursor()
            
            # Lấy danh sách tờ khai gần đây
            query = """
                SELECT TOP 5 SOTK, NGAY_DK, MA_HQ
                FROM DTOKHAIMD 
                ORDER BY NGAY_DK DESC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            print(f"   📋 Recent declarations:")
            for row in rows:
                print(f"      {row.SOTK} - {row.NGAY_DK} - {row.MA_HQ}")
            
            cursor.close()
            connector.disconnect()
            
            return True
        else:
            print(f"   ❌ Connection failed!")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_declaration_query(declaration_number: str):
    """Test query tờ khai cụ thể"""
    
    print(f"\n🔍 TESTING DECLARATION QUERY: {declaration_number}")
    print("=" * 60)
    
    config_manager = ConfigurationManager("config.ini")
    db_config = config_manager.get_database_config()
    
    try:
        connector = EcusDataConnector(db_config)
        
        if not connector.connect():
            print(f"   ❌ Connection failed!")
            return
        
        cursor = connector._connection.cursor()
        
        # Query tờ khai - lấy tất cả columns
        query = """
            SELECT TOP 1 *
            FROM DTOKHAIMD 
            WHERE SOTK = ?
        """
        
        cursor.execute(query, (declaration_number,))
        row = cursor.fetchone()
        
        if row:
            print(f"   ✅ Declaration found!")
            
            # Lấy tên các cột
            columns = [column[0] for column in cursor.description]
            print(f"\n   📋 COLUMNS ({len(columns)}):")
            for i, col in enumerate(columns):
                value = row[i]
                if value is not None and str(value).strip():
                    print(f"      {col}: {value}")
            
            # Query hàng hóa
            goods_query = """
                SELECT TOP 5 *
                FROM DHANGMDDK
                WHERE SOTK = ?
            """
            
            cursor.execute(goods_query, (declaration_number,))
            goods_rows = cursor.fetchall()
            
            if goods_rows:
                goods_columns = [column[0] for column in cursor.description]
                print(f"\n   📦 GOODS COLUMNS ({len(goods_columns)}):")
                print(f"      {goods_columns}")
                
                print(f"\n   📦 FIRST GOODS ITEM:")
                for i, col in enumerate(goods_columns):
                    value = goods_rows[0][i]
                    if value is not None and str(value).strip():
                        print(f"      {col}: {value}")
        else:
            print(f"   ❌ Declaration not found!")
        
        cursor.close()
        connector.disconnect()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if test_database_connection():
        # Test với tờ khai cụ thể
        test_declaration_query("107808761432")