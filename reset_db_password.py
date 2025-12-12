"""
Script để reset mật khẩu database khi bị corrupt.

Sử dụng: python reset_db_password.py

Script này sẽ:
1. Hỏi mật khẩu mới
2. Mã hóa và lưu vào config.ini
"""

import getpass
from config.configuration_manager import ConfigurationManager


def main():
    print("=" * 50)
    print("RESET MẬT KHẨU DATABASE")
    print("=" * 50)
    print()
    
    try:
        cm = ConfigurationManager('config.ini')
        
        # Show current config
        print("Cấu hình hiện tại:")
        print(f"  Server: {cm.config.get('Database', 'server')}")
        print(f"  Database: {cm.config.get('Database', 'database')}")
        print(f"  Username: {cm.config.get('Database', 'username')}")
        print()
        
        # Get new password
        password = getpass.getpass("Nhập mật khẩu mới: ")
        
        if not password:
            print("Mật khẩu không được để trống!")
            return
        
        # Confirm
        confirm = getpass.getpass("Xác nhận mật khẩu: ")
        
        if password != confirm:
            print("Mật khẩu không khớp!")
            return
        
        # Save new password
        server = cm.config.get('Database', 'server')
        database = cm.config.get('Database', 'database')
        username = cm.config.get('Database', 'username')
        
        cm.set_database_config(server, database, username, password)
        
        print()
        print("✓ Đã lưu mật khẩu mới thành công!")
        print()
        
        # Test connection
        test = input("Bạn có muốn kiểm tra kết nối? (y/n): ")
        if test.lower() == 'y':
            try:
                import pyodbc
                db_config = cm.get_database_config()
                conn = pyodbc.connect(db_config.connection_string, timeout=10)
                conn.close()
                print("✓ Kết nối thành công!")
            except Exception as e:
                print(f"✗ Lỗi kết nối: {e}")
        
    except Exception as e:
        print(f"Lỗi: {e}")


if __name__ == "__main__":
    main()
