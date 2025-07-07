#!/usr/bin/env python3
"""
Version bumping script for movedb-core.
Automatically updates version numbers across all relevant files.
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# Files that contain version information
VERSION_FILES = [
    ("src/movedb/__init__.py", r'__version__ = "([^"]+)"', r'__version__ = "{}"'),
    ("pyproject.toml", r'version = "([^"]+)"', r'version = "{}"'),
    ("conda-recipe/meta.yaml", r'{% set version = "([^"]+)" %}', r'{{% set version = "{}" %}}'),
]

def get_current_version() -> str:
    """Get the current version from __init__.py."""
    init_file = Path("src/movedb/__init__.py")
    if not init_file.exists():
        print("❌ Error: src/movedb/__init__.py not found")
        sys.exit(1)
    
    content = init_file.read_text()
    match = re.search(r'__version__ = "([^"]+)"', content)
    if not match:
        print("❌ Error: Could not find version in __init__.py")
        sys.exit(1)
    
    return match.group(1)

def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse a semantic version string."""
    try:
        parts = version.split('.')
        if len(parts) != 3:
            raise ValueError("Version must have 3 parts")
        major, minor, patch = (int(part) for part in parts)
        return (major, minor, patch)
    except ValueError as e:
        print(f"❌ Error: Invalid version format '{version}': {e}")
        sys.exit(1)

def format_version(major: int, minor: int, patch: int) -> str:
    """Format version tuple as string."""
    return f"{major}.{minor}.{patch}"

def bump_version(version: str, bump_type: str) -> str:
    """Bump version according to semantic versioning."""
    major, minor, patch = parse_version(version)
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        print(f"❌ Error: Invalid bump type '{bump_type}'. Use: major, minor, or patch")
        sys.exit(1)
    
    return format_version(major, minor, patch)

def update_file(filepath: str, pattern: str, replacement: str, new_version: str) -> bool:
    """Update version in a single file."""
    file_path = Path(filepath)
    if not file_path.exists():
        print(f"⚠️  Warning: {filepath} not found, skipping")
        return False
    
    content = file_path.read_text()
    new_content = re.sub(pattern, replacement.format(new_version), content)
    
    if content == new_content:
        print(f"⚠️  Warning: No version found in {filepath}")
        return False
    
    file_path.write_text(new_content)
    print(f"✅ Updated {filepath}")
    return True

def update_all_files(new_version: str) -> None:
    """Update version in all relevant files."""
    print(f"📝 Updating version to {new_version}...")
    
    for filepath, pattern, replacement in VERSION_FILES:
        update_file(filepath, pattern, replacement, new_version)

def git_tag_version(version: str, push: bool = False) -> None:
    """Create and optionally push a git tag."""
    tag = f"v{version}"
    
    try:
        # Create tag
        subprocess.run(["git", "tag", tag], check=True, capture_output=True)
        print(f"✅ Created git tag: {tag}")
        
        if push:
            # Push tag
            subprocess.run(["git", "push", "origin", tag], check=True, capture_output=True)
            print(f"✅ Pushed git tag: {tag}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        print("You may need to create and push the tag manually:")
        print(f"   git tag {tag}")
        print(f"   git push origin {tag}")

def main():
    """Main version bumping function."""
    if len(sys.argv) < 2:
        print("Usage: python bump_version.py <major|minor|patch|x.y.z> [--tag] [--push]")
        print("\nExamples:")
        print("  python bump_version.py patch        # 0.1.0 -> 0.1.1")
        print("  python bump_version.py minor        # 0.1.0 -> 0.2.0")
        print("  python bump_version.py major        # 0.1.0 -> 1.0.0")
        print("  python bump_version.py 0.2.5        # Set specific version")
        print("  python bump_version.py patch --tag  # Bump and create git tag")
        print("  python bump_version.py minor --tag --push  # Bump, tag, and push")
        sys.exit(1)
    
    bump_type = sys.argv[1]
    create_tag = "--tag" in sys.argv
    push_tag = "--push" in sys.argv
    
    # Get current version
    current_version = get_current_version()
    print(f"📋 Current version: {current_version}")
    
    # Calculate new version
    if bump_type in ["major", "minor", "patch"]:
        new_version = bump_version(current_version, bump_type)
    else:
        # Assume it's a specific version
        try:
            parse_version(bump_type)  # Validate format
            new_version = bump_type
        except:
            print(f"❌ Error: Invalid version or bump type: {bump_type}")
            sys.exit(1)
    
    print(f"🚀 New version: {new_version}")
    
    # Confirm with user
    response = input(f"Update version from {current_version} to {new_version}? (y/N): ")
    if response.lower() != 'y':
        print("❌ Version bump cancelled")
        sys.exit(1)
    
    # Update files
    update_all_files(new_version)
    
    # Create git tag if requested
    if create_tag:
        git_tag_version(new_version, push_tag)
    
    print(f"\n🎉 Version successfully bumped to {new_version}!")
    print("\nNext steps:")
    print("1. Review the changes: git diff")
    print("2. Commit the changes: git add -A && git commit -m 'Bump version to {}'".format(new_version))
    print("3. Build new package: make build")
    print("4. Upload to conda: conda upload dist/conda/noarch/movedb-core-{}-*.conda".format(new_version))
    
    if not create_tag:
        print("5. Create git tag: git tag v{} && git push origin v{}".format(new_version, new_version))

if __name__ == "__main__":
    main()
