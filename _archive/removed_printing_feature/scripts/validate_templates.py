#!/usr/bin/env python3
"""
Template validation script for customs declaration printing.

This script validates all installed templates and provides a comprehensive
report on their status, integrity, and configuration.

Usage:
    python scripts/validate_templates.py [--template-dir DIRECTORY] [--fix] [--verbose]

Requirements: 4.1, 4.2, 4.5
"""

import argparse
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from declaration_printing.template_installer import TemplateInstaller
from declaration_printing.models import DeclarationType


def main():
    """Main function for template validation script."""
    parser = argparse.ArgumentParser(
        description="Validate customs declaration templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/validate_templates.py
    python scripts/validate_templates.py --template-dir custom_templates
    python scripts/validate_templates.py --fix --verbose
        """
    )
    
    parser.add_argument(
        '--template-dir',
        default='templates',
        help='Directory containing template files (default: templates)'
    )
    
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix issues automatically'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed validation information'
    )
    
    parser.add_argument(
        '--install-samples',
        action='store_true',
        help='Install sample templates from sample directory'
    )
    
    args = parser.parse_args()
    
    # Initialize template installer
    installer = TemplateInstaller(args.template_dir)
    
    print("=== CUSTOMS DECLARATION TEMPLATE VALIDATOR ===")
    print(f"Template directory: {args.template_dir}")
    print()
    
    # Check current installation status
    print("Checking template installation status...")
    is_complete, status = installer.check_template_installation()
    
    if args.verbose:
        print("\nDETAILED STATUS:")
        print(f"  Directory exists: {status['directory_exists']}")
        print(f"  Directory accessible: {status['directory_accessible']}")
        print(f"  Templates found: {len([t for t in status['templates_found'].values() if t])}")
        print(f"  Templates valid: {sum(status['templates_valid'].values())}")
        print(f"  Mapping files: {sum(status['mapping_files'].values())}")
        print()
    
    # Show errors and suggestions
    if status['errors']:
        print("ERRORS FOUND:")
        for error in status['errors']:
            print(f"  ❌ {error}")
        print()
    
    if status['suggestions']:
        print("SUGGESTIONS:")
        for suggestion in status['suggestions']:
            print(f"  💡 {suggestion}")
        print()
    
    # Validate individual templates
    print("TEMPLATE VALIDATION RESULTS:")
    validation_results = {}
    
    for declaration_type in [DeclarationType.EXPORT_CLEARANCE, DeclarationType.IMPORT_CLEARANCE]:
        type_name = "Export" if "export" in declaration_type.value else "Import"
        template_name = installer.template_manager.TEMPLATE_FILENAMES[declaration_type]
        
        print(f"\n{type_name} Template ({template_name}):")
        
        template_found = status['templates_found'].get(declaration_type.value)
        if template_found:
            is_valid, issues = installer.validate_template_file(template_found)
            validation_results[declaration_type] = (is_valid, issues)
            
            if is_valid:
                print(f"  ✅ Template is valid")
            else:
                print(f"  ❌ Template has issues:")
                for issue in issues:
                    print(f"     - {issue}")
            
            if args.verbose and is_valid:
                # Show mapping information
                try:
                    mapping = installer.template_manager.load_template_mapping(template_found)
                    print(f"  📋 Mapping fields: {len(mapping)} fields configured")
                    if args.verbose:
                        for field, cell in list(mapping.items())[:5]:  # Show first 5 fields
                            print(f"     {field} → {cell}")
                        if len(mapping) > 5:
                            print(f"     ... and {len(mapping) - 5} more fields")
                except Exception as e:
                    print(f"  ⚠️  Mapping error: {e}")
        else:
            print(f"  ❌ Template not found")
            validation_results[declaration_type] = (False, ["Template file not found"])
    
    # Install samples if requested
    if args.install_samples:
        print("\nINSTALLING SAMPLE TEMPLATES:")
        success, messages = installer.install_sample_templates()
        
        for message in messages:
            if "Successfully" in message:
                print(f"  ✅ {message}")
            elif "Failed" in message or "not found" in message:
                print(f"  ❌ {message}")
            else:
                print(f"  ℹ️  {message}")
        
        if success:
            print("  ✅ Sample installation completed")
        else:
            print("  ❌ Sample installation failed")
    
    # Attempt fixes if requested
    if args.fix:
        print("\nATTEMPTING AUTOMATIC FIXES:")
        fixes_applied = 0
        
        # Create missing mapping files
        for declaration_type in [DeclarationType.EXPORT_CLEARANCE, DeclarationType.IMPORT_CLEARANCE]:
            template_found = status['templates_found'].get(declaration_type.value)
            if template_found and not status['mapping_files'].get(declaration_type.value, False):
                try:
                    template_path = Path(template_found)
                    mapping_file = template_path.parent / f"{template_path.stem}_mapping.json"
                    
                    if not mapping_file.exists():
                        installer._create_default_mapping_file(template_path)
                        print(f"  ✅ Created mapping file: {mapping_file.name}")
                        fixes_applied += 1
                except Exception as e:
                    print(f"  ❌ Failed to create mapping file: {e}")
        
        if fixes_applied == 0:
            print("  ℹ️  No automatic fixes available")
        else:
            print(f"  ✅ Applied {fixes_applied} fix(es)")
    
    # Final summary
    print("\n" + "="*50)
    if is_complete:
        print("🎉 TEMPLATE INSTALLATION IS COMPLETE!")
        print("All required templates are installed and valid.")
    else:
        print("⚠️  TEMPLATE INSTALLATION NEEDS ATTENTION")
        print("Some templates are missing or invalid.")
        
        if not args.fix and not args.install_samples:
            print("\nTo fix issues automatically, run:")
            print(f"  python {__file__} --fix --install-samples")
    
    # Generate installation report
    if args.verbose:
        print("\nFULL INSTALLATION REPORT:")
        print("-" * 30)
        report = installer.create_installation_report()
        print(report)
    
    # Exit with appropriate code
    sys.exit(0 if is_complete else 1)


if __name__ == '__main__':
    main()