#!/usr/bin/env python3
"""Simple test script without pytest dependency."""

def test_basic_imports():
    """Test that the package can be imported and basic functionality works."""
    print("Testing movedb imports...")
    
    # Test basic import
    import movedb
    print(f"✓ Successfully imported movedb version: {movedb.__version__}")
    
    # Test main classes import from submodules
    from movedb.core import Trial, Event, ImportMethod
    print("✓ Successfully imported core classes")
    
    # Test file I/O imports from submodules
    from movedb.file_io import C3DLoader, OpenSimExporter
    print("✓ Successfully imported file I/O classes")
    
    # Test creating an Event
    event = Event(label="test", frame=100, context="test")
    assert event.label == "test"
    assert event.frame == 100
    print("✓ Event creation works")
    
    print("\n🎉 All basic tests passed!")

if __name__ == "__main__":
    test_basic_imports()
