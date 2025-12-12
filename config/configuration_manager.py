"""
Configuration Manager

This module handles loading, validating, and managing application configuration
including encryption of sensitive data like passwords.
"""

import configparser
import os
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet

from models.config_models import DatabaseConfig, DatabaseProfile, BarcodeServiceConfig, LoggingConfig, UIConfig


class ConfigurationError(Exception):
    """Exception raised for configuration errors"""
    pass


class ConfigurationManager:
    """Manages application configuration with encryption support"""
    
    # Default encryption key file location
    KEY_FILE = ".encryption_key"
    
    def __init__(self, config_path: str):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to the INI configuration file
        """
        self.config_path = config_path
        # Disable interpolation to allow special characters in passwords
        self.config = configparser.ConfigParser(interpolation=None)
        self._cipher: Optional[Fernet] = None
        
        # Load or generate encryption key
        self._load_or_generate_key()
        
        # Load configuration if file exists
        if os.path.exists(config_path):
            self._load_config()
        else:
            raise ConfigurationError(f"Configuration file not found: {config_path}")
    
    def _load_or_generate_key(self) -> None:
        """Load existing encryption key or generate a new one"""
        key_path = Path(self.KEY_FILE)
        
        if key_path.exists():
            with open(key_path, 'rb') as key_file:
                key = key_file.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_path, 'wb') as key_file:
                key_file.write(key)
        
        self._cipher = Fernet(key)
    
    def _load_config(self) -> None:
        """Load configuration from INI file"""
        try:
            self.config.read(self.config_path)
        except Exception as e:
            raise ConfigurationError(f"Failed to read configuration file: {e}")
    
    def _encrypt_password(self, password: str) -> str:
        """
        Encrypt a password
        
        Args:
            password: Plain text password
            
        Returns:
            Encrypted password as string
        """
        if not password:
            return ""
        encrypted = self._cipher.encrypt(password.encode())
        return encrypted.decode()
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """
        Decrypt a password, handling double encryption if needed.
        
        Args:
            encrypted_password: Encrypted password string
            
        Returns:
            Decrypted plain text password
        """
        if not encrypted_password:
            return ""
        
        # If it doesn't look encrypted, return as-is
        if not encrypted_password.startswith('gAAAAA'):
            return encrypted_password
        
        try:
            decrypted = self._cipher.decrypt(encrypted_password.encode())
            result = decrypted.decode()
            
            # Handle double encryption - if result still looks encrypted, try to decrypt again
            # But only if it's a valid Fernet token
            if result.startswith('gAAAAA'):
                try:
                    decrypted2 = self._cipher.decrypt(result.encode())
                    return decrypted2.decode()
                except Exception:
                    # Second decryption failed, return first result
                    # This might still be encrypted with a different key
                    return result
            
            return result
        except Exception:
            # If decryption fails, assume it's plain text (for backward compatibility)
            return encrypted_password
    
    def get_database_config(self) -> DatabaseConfig:
        """
        Get database configuration
        
        Returns:
            DatabaseConfig object
            
        Raises:
            ConfigurationError: If required configuration is missing
        """
        try:
            encrypted_password = self.config.get('Database', 'password')
            password = self._decrypt_password(encrypted_password)
            
            return DatabaseConfig(
                server=self.config.get('Database', 'server'),
                database=self.config.get('Database', 'database'),
                username=self.config.get('Database', 'username'),
                password=password,
                timeout=self.config.getint('Database', 'timeout', fallback=30)
            )
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            raise ConfigurationError(f"Missing database configuration: {e}")
    
    def get_barcode_service_config(self) -> BarcodeServiceConfig:
        """
        Get barcode service configuration
        
        Returns:
            BarcodeServiceConfig object
            
        Raises:
            ConfigurationError: If required configuration is missing
        """
        try:
            # Get output path from BarcodeService section first, fall back to Application section
            output_path = self.config.get('BarcodeService', 'output_path', fallback=None)
            if not output_path:
                output_path = self.config.get('Application', 'output_directory', fallback=None)
            
            return BarcodeServiceConfig(
                api_url=self.config.get('BarcodeService', 'api_url'),
                primary_web_url=self.config.get('BarcodeService', 'primary_web_url'),
                backup_web_url=self.config.get('BarcodeService', 'backup_web_url', fallback=''),
                timeout=self.config.getint('BarcodeService', 'timeout', fallback=30),
                max_retries=self.config.getint('BarcodeService', 'max_retries', 
                                               fallback=self.config.getint('Application', 'max_retries', fallback=1)),
                retry_delay=self.config.getint('Application', 'retry_delay', fallback=5),
                api_timeout=self.config.getint('BarcodeService', 'api_timeout', fallback=30),
                web_timeout=self.config.getint('BarcodeService', 'web_timeout', fallback=60),
                session_reuse=self.config.getboolean('BarcodeService', 'session_reuse', fallback=True),
                output_path=output_path,
                retrieval_method=self.config.get('BarcodeService', 'retrieval_method', fallback='auto'),
                pdf_naming_format=self.config.get('BarcodeService', 'pdf_naming_format', fallback='tax_code')
            )
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            raise ConfigurationError(f"Missing barcode service configuration: {e}")
    
    def get_logging_config(self) -> LoggingConfig:
        """
        Get logging configuration
        
        Returns:
            LoggingConfig object
        """
        return LoggingConfig(
            log_level=self.config.get('Logging', 'log_level', fallback='INFO'),
            log_file=self.config.get('Logging', 'log_file', fallback='logs/app.log'),
            max_log_size=self.config.getint('Logging', 'max_log_size', fallback=10485760),
            backup_count=self.config.getint('Logging', 'backup_count', fallback=5)
        )
    
    def get_output_path(self) -> str:
        """
        Get output directory path
        
        Returns:
            Output directory path
        """
        return self.config.get('Application', 'output_directory', 
                              fallback='C:\\CustomsBarcodes')
    
    def get_polling_interval(self) -> int:
        """
        Get polling interval in seconds
        
        Returns:
            Polling interval
        """
        return self.config.getint('Application', 'polling_interval', fallback=300)
    
    def get_operation_mode(self) -> str:
        """
        Get operation mode (automatic or manual)
        
        Returns:
            Operation mode string
        """
        return self.config.get('Application', 'operation_mode', fallback='automatic')
    
    def set_output_path(self, path: str) -> None:
        """
        Set output directory path
        
        Args:
            path: New output directory path
        """
        if not self.config.has_section('Application'):
            self.config.add_section('Application')
        self.config.set('Application', 'output_directory', path)
    
    def set_operation_mode(self, mode: str) -> None:
        """
        Set operation mode
        
        Args:
            mode: Operation mode ('automatic' or 'manual')
        """
        if mode not in ['automatic', 'manual']:
            raise ValueError(f"Invalid operation mode: {mode}")
        
        if not self.config.has_section('Application'):
            self.config.add_section('Application')
        self.config.set('Application', 'operation_mode', mode)
    
    def get_retrieval_method(self) -> str:
        """
        Get barcode retrieval method
        
        Returns:
            Retrieval method ('auto', 'api', or 'web')
        """
        return self.config.get('BarcodeService', 'retrieval_method', fallback='auto')
    
    def set_retrieval_method(self, method: str) -> None:
        """
        Set barcode retrieval method
        
        Args:
            method: Retrieval method ('auto', 'api', or 'web')
        """
        if method not in ['auto', 'api', 'web']:
            raise ValueError(f"Invalid retrieval method: {method}")
        
        if not self.config.has_section('BarcodeService'):
            self.config.add_section('BarcodeService')
        self.config.set('BarcodeService', 'retrieval_method', method)
    
    def get_pdf_naming_format(self) -> str:
        """
        Get PDF file naming format
        
        Returns:
            PDF naming format ('tax_code', 'invoice', or 'bill_of_lading')
        """
        return self.config.get('BarcodeService', 'pdf_naming_format', fallback='tax_code')
    
    def set_pdf_naming_format(self, format_type: str) -> None:
        """
        Set PDF file naming format
        
        Args:
            format_type: Naming format ('tax_code', 'invoice', or 'bill_of_lading')
        """
        if format_type not in ['tax_code', 'invoice', 'bill_of_lading']:
            raise ValueError(f"Invalid PDF naming format: {format_type}")
        
        if not self.config.has_section('BarcodeService'):
            self.config.add_section('BarcodeService')
        self.config.set('BarcodeService', 'pdf_naming_format', format_type)
    
    def save(self) -> None:
        """
        Save configuration to file
        
        Encrypts passwords before saving.
        """
        # Encrypt password before saving
        if self.config.has_section('Database'):
            password = self.config.get('Database', 'password')
            # Check if password is already encrypted (starts with 'gAAAAA')
            if not password.startswith('gAAAAA'):
                encrypted = self._encrypt_password(password)
                self.config.set('Database', 'password', encrypted)
        
        with open(self.config_path, 'w') as config_file:
            self.config.write(config_file)
    
    def validate(self) -> None:
        """
        Validate configuration completeness
        
        Raises:
            ConfigurationError: If required configuration is missing or invalid
        """
        errors = []
        
        # Validate Database section
        if not self.config.has_section('Database'):
            errors.append("Missing [Database] section")
        else:
            required_db_fields = ['server', 'database', 'username', 'password']
            for field in required_db_fields:
                if not self.config.has_option('Database', field):
                    errors.append(f"Missing Database.{field}")
        
        # Validate BarcodeService section
        if not self.config.has_section('BarcodeService'):
            errors.append("Missing [BarcodeService] section")
        else:
            required_service_fields = ['api_url', 'primary_web_url', 'backup_web_url']
            for field in required_service_fields:
                if not self.config.has_option('BarcodeService', field):
                    errors.append(f"Missing BarcodeService.{field}")
        
        # Validate Application section
        if not self.config.has_section('Application'):
            errors.append("Missing [Application] section")
        else:
            if not self.config.has_option('Application', 'output_directory'):
                errors.append("Missing Application.output_directory")
        
        if errors:
            raise ConfigurationError("Configuration validation failed:\n" + "\n".join(errors))
    
    # ==================== Database Profiles Management ====================
    
    def _get_profile_section_name(self, profile_name: str) -> str:
        """
        Get section name for a profile (sanitize special characters).
        
        Args:
            profile_name: Human-readable profile name
            
        Returns:
            Safe section name for config file
        """
        # Replace spaces and special chars with underscores
        safe_name = profile_name.replace(' ', '_').replace('-', '_')
        return f"Profile_{safe_name}"
    
    def get_database_profiles(self) -> list:
        """
        Get list of all saved database profiles.
        
        Returns:
            List of DatabaseProfile objects
        """
        profiles = []
        
        # Get profile names from DatabaseProfiles section
        if not self.config.has_section('DatabaseProfiles'):
            return profiles
        
        profile_names_str = self.config.get('DatabaseProfiles', 'profiles', fallback='')
        if not profile_names_str:
            return profiles
        
        profile_names = [name.strip() for name in profile_names_str.split('|') if name.strip()]
        
        for name in profile_names:
            profile = self.get_database_profile(name)
            if profile:
                profiles.append(profile)
        
        return profiles
    
    def get_database_profile(self, profile_name: str) -> DatabaseProfile:
        """
        Get a specific database profile by name.
        
        Args:
            profile_name: Name of the profile
            
        Returns:
            DatabaseProfile object or None if not found
        """
        section_name = self._get_profile_section_name(profile_name)
        
        if not self.config.has_section(section_name):
            return None
        
        try:
            encrypted_password = self.config.get(section_name, 'password', fallback='')
            password = self._decrypt_password(encrypted_password)
            
            return DatabaseProfile(
                name=profile_name,
                server=self.config.get(section_name, 'server', fallback=''),
                database=self.config.get(section_name, 'database', fallback=''),
                username=self.config.get(section_name, 'username', fallback=''),
                password=password,
                timeout=self.config.getint(section_name, 'timeout', fallback=30)
            )
        except Exception:
            return None
    
    def save_database_profile(self, profile: DatabaseProfile) -> None:
        """
        Save a database profile.
        
        Args:
            profile: DatabaseProfile to save
        """
        section_name = self._get_profile_section_name(profile.name)
        
        # Create section if not exists
        if not self.config.has_section(section_name):
            self.config.add_section(section_name)
        
        # Save profile data
        self.config.set(section_name, 'server', profile.server)
        self.config.set(section_name, 'database', profile.database)
        self.config.set(section_name, 'username', profile.username)
        # Only encrypt if not already encrypted
        password = profile.password
        if not password.startswith('gAAAAA'):
            password = self._encrypt_password(password)
        self.config.set(section_name, 'password', password)
        self.config.set(section_name, 'timeout', str(profile.timeout))
        
        # Update profile list
        self._add_profile_to_list(profile.name)
        
        # Save to file
        self._save_config_file()
    
    def delete_database_profile(self, profile_name: str) -> bool:
        """
        Delete a database profile.
        
        Args:
            profile_name: Name of the profile to delete
            
        Returns:
            True if deleted, False if not found
        """
        section_name = self._get_profile_section_name(profile_name)
        
        if not self.config.has_section(section_name):
            return False
        
        # Remove section
        self.config.remove_section(section_name)
        
        # Update profile list
        self._remove_profile_from_list(profile_name)
        
        # Save to file
        self._save_config_file()
        
        return True
    
    def _add_profile_to_list(self, profile_name: str) -> None:
        """Add profile name to the profiles list."""
        if not self.config.has_section('DatabaseProfiles'):
            self.config.add_section('DatabaseProfiles')
        
        profile_names_str = self.config.get('DatabaseProfiles', 'profiles', fallback='')
        profile_names = [name.strip() for name in profile_names_str.split('|') if name.strip()]
        
        if profile_name not in profile_names:
            profile_names.append(profile_name)
        
        self.config.set('DatabaseProfiles', 'profiles', '|'.join(profile_names))
    
    def _remove_profile_from_list(self, profile_name: str) -> None:
        """Remove profile name from the profiles list."""
        if not self.config.has_section('DatabaseProfiles'):
            return
        
        profile_names_str = self.config.get('DatabaseProfiles', 'profiles', fallback='')
        profile_names = [name.strip() for name in profile_names_str.split('|') if name.strip()]
        
        if profile_name in profile_names:
            profile_names.remove(profile_name)
        
        self.config.set('DatabaseProfiles', 'profiles', '|'.join(profile_names))
    
    def get_active_profile_name(self) -> str:
        """
        Get the name of the currently active profile.
        
        Returns:
            Active profile name or empty string if none
        """
        return self.config.get('Database', 'active_profile', fallback='')
    
    def set_active_profile(self, profile_name: str) -> None:
        """
        Set the active profile and update Database section.
        
        Args:
            profile_name: Name of the profile to activate
        """
        profile = self.get_database_profile(profile_name)
        if not profile:
            raise ConfigurationError(f"Profile not found: {profile_name}")
        
        # Update Database section with profile data
        if not self.config.has_section('Database'):
            self.config.add_section('Database')
        
        self.config.set('Database', 'server', profile.server)
        self.config.set('Database', 'database', profile.database)
        self.config.set('Database', 'username', profile.username)
        # Only encrypt if not already encrypted (profile.password is already decrypted)
        password = profile.password
        if not password.startswith('gAAAAA'):
            password = self._encrypt_password(password)
        self.config.set('Database', 'password', password)
        self.config.set('Database', 'timeout', str(profile.timeout))
        self.config.set('Database', 'active_profile', profile_name)
        
        # Save to file
        self._save_config_file()
    
    def set_database_config(self, server: str, database: str, username: str, password: str) -> None:
        """
        Set database configuration directly (without profile).
        
        Args:
            server: Database server
            database: Database name
            username: Username
            password: Password (plain text, will be encrypted)
        """
        if not self.config.has_section('Database'):
            self.config.add_section('Database')
        
        self.config.set('Database', 'server', server)
        self.config.set('Database', 'database', database)
        self.config.set('Database', 'username', username)
        # Only encrypt if not already encrypted
        if not password.startswith('gAAAAA'):
            password = self._encrypt_password(password)
        self.config.set('Database', 'password', password)
        
        # Save to file
        self._save_config_file()
    
    def _save_config_file(self) -> None:
        """Save configuration to file without re-encrypting already encrypted passwords."""
        with open(self.config_path, 'w') as config_file:
            self.config.write(config_file)
    
    # ==================== UI Settings Management ====================
    
    def _ensure_ui_section(self) -> None:
        """Ensure [UI] section exists in config."""
        if not self.config.has_section('UI'):
            self.config.add_section('UI')
    
    def get_ui_config(self) -> UIConfig:
        """
        Get UI configuration settings.
        
        Returns:
            UIConfig object with all UI settings
        """
        return UIConfig(
            theme=self.get_theme(),
            notifications_enabled=self.get_notifications_enabled(),
            sound_enabled=self.get_sound_enabled(),
            batch_limit=self.get_batch_limit(),
            window_x=self.get_window_x(),
            window_y=self.get_window_y(),
            window_width=self.get_window_width(),
            window_height=self.get_window_height()
        )
    
    def set_ui_config(self, ui_config: UIConfig) -> None:
        """
        Set all UI configuration settings at once.
        
        Args:
            ui_config: UIConfig object with settings to save
        """
        self.set_theme(ui_config.theme)
        self.set_notifications_enabled(ui_config.notifications_enabled)
        self.set_sound_enabled(ui_config.sound_enabled)
        self.set_batch_limit(ui_config.batch_limit)
        self.set_window_state(
            ui_config.window_x,
            ui_config.window_y,
            ui_config.window_width,
            ui_config.window_height
        )
    
    def get_theme(self) -> str:
        """
        Get current theme setting.
        
        Returns:
            Theme name ('light' or 'dark')
        """
        return self.config.get('UI', 'theme', fallback='light')
    
    def set_theme(self, theme: str) -> None:
        """
        Set theme setting.
        
        Args:
            theme: Theme name ('light' or 'dark')
        """
        if theme not in ('light', 'dark'):
            theme = 'light'  # Default to light for invalid values
        self._ensure_ui_section()
        self.config.set('UI', 'theme', theme)
    
    def get_notifications_enabled(self) -> bool:
        """
        Get notifications enabled setting.
        
        Returns:
            True if notifications are enabled
        """
        return self.config.getboolean('UI', 'notifications_enabled', fallback=True)
    
    def set_notifications_enabled(self, enabled: bool) -> None:
        """
        Set notifications enabled setting.
        
        Args:
            enabled: True to enable notifications
        """
        self._ensure_ui_section()
        self.config.set('UI', 'notifications_enabled', str(enabled).lower())
    
    def get_sound_enabled(self) -> bool:
        """
        Get sound enabled setting.
        
        Returns:
            True if sound is enabled
        """
        return self.config.getboolean('UI', 'sound_enabled', fallback=True)
    
    def set_sound_enabled(self, enabled: bool) -> None:
        """
        Set sound enabled setting.
        
        Args:
            enabled: True to enable sound
        """
        self._ensure_ui_section()
        self.config.set('UI', 'sound_enabled', str(enabled).lower())
    
    def get_batch_limit(self) -> int:
        """
        Get batch download limit.
        
        Returns:
            Maximum number of declarations per batch (1-50, default 20)
        """
        limit = self.config.getint('UI', 'batch_limit', fallback=20)
        # Validate and clamp to valid range
        if limit < 1 or limit > 50:
            return 20  # Default for invalid values
        return limit
    
    def set_batch_limit(self, limit: int) -> None:
        """
        Set batch download limit.
        
        Args:
            limit: Maximum declarations per batch (1-50)
        """
        # Clamp to valid range
        if limit < 1:
            limit = 1
        elif limit > 50:
            limit = 50
        self._ensure_ui_section()
        self.config.set('UI', 'batch_limit', str(limit))
    
    def get_window_x(self) -> int:
        """
        Get window X position.
        
        Returns:
            Window X position (-1 for center)
        """
        return self.config.getint('UI', 'window_x', fallback=-1)
    
    def get_window_y(self) -> int:
        """
        Get window Y position.
        
        Returns:
            Window Y position (-1 for center)
        """
        return self.config.getint('UI', 'window_y', fallback=-1)
    
    def get_window_width(self) -> int:
        """
        Get window width.
        
        Returns:
            Window width in pixels (default 1200)
        """
        width = self.config.getint('UI', 'window_width', fallback=1200)
        return max(800, width)  # Minimum width
    
    def get_window_height(self) -> int:
        """
        Get window height.
        
        Returns:
            Window height in pixels (default 850)
        """
        height = self.config.getint('UI', 'window_height', fallback=850)
        return max(600, height)  # Minimum height
    
    def get_window_state(self) -> tuple:
        """
        Get window position and size.
        
        Returns:
            Tuple of (x, y, width, height)
        """
        return (
            self.get_window_x(),
            self.get_window_y(),
            self.get_window_width(),
            self.get_window_height()
        )
    
    def set_window_state(self, x: int, y: int, width: int, height: int) -> None:
        """
        Set window position and size.
        
        Args:
            x: Window X position (-1 for center)
            y: Window Y position (-1 for center)
            width: Window width in pixels
            height: Window height in pixels
        """
        self._ensure_ui_section()
        self.config.set('UI', 'window_x', str(x))
        self.config.set('UI', 'window_y', str(y))
        self.config.set('UI', 'window_width', str(max(800, width)))
        self.config.set('UI', 'window_height', str(max(600, height)))
