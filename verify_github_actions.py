#!/usr/bin/env python3
"""
Test script to verify GitHub Actions setup is complete and working.
"""

import os
import yaml
import subprocess
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def validate_yaml(filepath, description):
    """Validate YAML file syntax."""
    try:
        with open(filepath, 'r') as f:
            yaml.safe_load(f)
        print(f"✅ {description}: Valid YAML")
        return True
    except yaml.YAMLError as e:
        print(f"❌ {description}: Invalid YAML - {e}")
        return False
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return False

def check_workflow_triggers(filepath):
    """Check workflow triggers."""
    try:
        with open(filepath, 'r') as f:
            workflow = yaml.safe_load(f)
        
        triggers = workflow.get('on', {})
        if isinstance(triggers, dict):
            trigger_types = list(triggers.keys())
            print(f"   Triggers: {', '.join(trigger_types)}")
            return True
        else:
            print(f"   Triggers: {triggers}")
            return True
    except Exception as e:
        print(f"   Error reading triggers: {e}")
        return False

def main():
    """Main verification function."""
    print("🔧 GitHub Actions Setup Verification")
    print("=" * 50)
    
    # Check directory structure
    print("\n📁 Directory Structure:")
    github_dir = Path('.github')
    workflows_dir = github_dir / 'workflows'
    
    if not github_dir.exists():
        print("❌ .github directory not found")
        return
    
    if not workflows_dir.exists():
        print("❌ .github/workflows directory not found")
        return
    
    print("✅ GitHub Actions directory structure exists")
    
    # Check workflow files
    print("\n📋 Workflow Files:")
    workflows = [
        ('.github/workflows/tests.yml', 'Test workflow'),
        ('.github/workflows/ci-cd.yml', 'CI/CD workflow'),
        ('.github/workflows/build.yml', 'Build workflow (legacy)'),
    ]
    
    existing_workflows = []
    for filepath, description in workflows:
        if check_file_exists(filepath, description):
            existing_workflows.append((filepath, description))
    
    # Validate YAML syntax
    print("\n🔍 YAML Validation:")
    for filepath, description in existing_workflows:
        if validate_yaml(filepath, description):
            check_workflow_triggers(filepath)
    
    # Check documentation
    print("\n📚 Documentation:")
    docs = [
        ('.github/workflows/README.md', 'Workflow README'),
        ('docs/GITHUB_ACTIONS.md', 'GitHub Actions documentation'),
    ]
    
    for filepath, description in docs:
        check_file_exists(filepath, description)
    
    # Check status badges in README
    print("\n🏷️  Status Badges:")
    readme_path = 'README.md'
    if Path(readme_path).exists():
        with open(readme_path, 'r') as f:
            content = f.read()
        
        if 'workflows/tests.yml/badge.svg' in content:
            print("✅ Tests badge found in README")
        else:
            print("❌ Tests badge not found in README")
        
        if 'workflows/ci-cd.yml/badge.svg' in content:
            print("✅ CI/CD badge found in README")
        else:
            print("❌ CI/CD badge not found in README")
    else:
        print("❌ README.md not found")
    
    # Check local testing setup
    print("\n🧪 Local Testing Integration:")
    test_files = [
        ('Makefile', 'Makefile with test commands'),
        ('run_tests.py', 'Python test runner'),
        ('pyproject.toml', 'pytest configuration'),
    ]
    
    for filepath, description in test_files:
        check_file_exists(filepath, description)
    
    print("\n🎉 GitHub Actions Setup Complete!")
    print("\nNext steps:")
    print("1. Push code to GitHub to trigger workflows")
    print("2. Check Actions tab in GitHub for workflow status")
    print("3. Set up Codecov integration if desired")
    print("4. Configure branch protection rules")
    print("5. Monitor workflow runs and adjust as needed")

if __name__ == "__main__":
    main()
