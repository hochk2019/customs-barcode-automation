#!/usr/bin/env python3
"""
Template setup script for customs declaration printing.

This script sets up templates by copying them from the sample directory
and creating the necessary mapping files.

Usage:
    python scripts/setup_templates.py [--source-dir DIRECTORY] [--force]

Requirements: 4.1, 4.2
"""

import argparse
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from declaration_printing.template_installer import TemplateInstaller


def main():
    """Main function for template setup script."""
    parser = argparse.ArgumentParser(
        description="Set up customs declaration templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/setup_templates.py
    python scripts/setup_templates.py --source-dir sample
    python scripts/setup_templates.py --force
        """
    )
    
    parser.add_argument(
        '--source-dir',
        default='sample',
        help='Source directory containing template files (default: sample)'
    )
    
    parser.add_argument(
        '--template-dir',
        default='templates',
        help='Target directory for templates (default: templates)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing templates without confirmation'
    )
    
    args = parser.parse_args()
    
    print("=== CUSTOMS DECLARATION TEMPLATE SETUP ===")
    print(f"Source directory: {args.source_dir}")
    print(f"Template directory: {args.template_dir}")
    print()
    
    # Initialize template installer
    installer = TemplateInstaller(args.template_dir)
    
    # Check if templates already exist
    is_complete, status = installer.check_template_installation()
    
    if is_complete and not args.force:
        print("✅ Templates are already installed and valid.")
        print("Use --force to reinstall templates.")
        return 0
    
    # Check source directory
    source_path = Path(args.source_dir)
    if not source_path.exists():
        print(f"❌ Source directory does not exist: {args.source_dir}")
        print("Please ensure the sample directory contains template files.")
        return 1
    
    # List available templates in source
    print("Available templates in source directory:")
    template_files = []
    for pattern in ['ToKhaiHQ*.xlsx', 'ToKhaiHQ*.xls']:
        template_files.extend(source_path.glob(pattern))
    
    if not template_files:
        print("❌ No template files found in source directory.")
        print("Expected files like: ToKhaiHQ7X_QDTQ.xlsx, ToKhaiHQ7N_QDTQ.xlsx")
        return 1
    
    for template_file in template_files:
        print(f"  📄 {template_file.name}")
    print()
    
    # Confirm installation
    if not args.force:
        response = input("Proceed with template installation? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Installation cancelled.")
            return 0
    
    # Install templates
    print("Installing templates...")
    success, messages = installer.install_sample_templates(args.source_dir)
    
    # Show results
    for message in messages:
        if "Successfully" in message:
            print(f"✅ {message}")
        elif "Failed" in message or "not found" in message:
            print(f"❌ {message}")
        else:
            print(f"ℹ️  {message}")
    
    print()
    
    if success:
        print("🎉 Template installation completed successfully!")
        
        # Validate installation
        print("\nValidating installation...")
        is_complete, status = installer.check_template_installation()
        
        if is_complete:
            print("✅ All templates are installed and valid.")
        else:
            print("⚠️  Some issues remain:")
            for error in status['errors']:
                print(f"  - {error}")
        
        # Show next steps
        print("\nNext steps:")
        print("1. Run validation: python scripts/validate_templates.py")
        print("2. Test printing functionality in the application")
        print("3. Customize templates if needed (see docs/TEMPLATE_CUSTOMIZATION_GUIDE.md)")
        
        return 0
    else:
        print("❌ Template installation failed.")
        print("\nTroubleshooting:")
        print("1. Check that source directory contains valid Excel files")
        print("2. Ensure you have write permissions to the templates directory")
        print("3. Run with --force to overwrite existing files")
        return 1


if __name__ == '__main__':
    sys.exit(main())