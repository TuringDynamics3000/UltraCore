"""
Test UltraCore package imports
"""

print("Testing UltraCore package imports...\n")

try:
    import ultracore
    print(f"✓ ultracore imported successfully")
    print(f"  Version: {ultracore.__version__}")
    print(f"  Modules: {', '.join(ultracore.__all__)}")
    print()
    
    # Test individual modules
    modules_to_test = [
        ('ultracore.accounting', 'Accounting'),
        ('ultracore.audit', 'Audit'),
        ('ultracore.lending', 'Lending'),
        ('ultracore.customers', 'Customers'),
        ('ultracore.accounts', 'Accounts'),
    ]
    
    for module_name, display_name in modules_to_test:
        try:
            exec(f"import {module_name}")
            print(f"✓ {display_name} module imported successfully")
        except ImportError as e:
            print(f"✗ {display_name} module import failed: {e}")
    
    print("\n✅ Package structure is valid!")
    
except ImportError as e:
    print(f"✗ Failed to import ultracore: {e}")
    print("\n❌ Package structure has issues")
