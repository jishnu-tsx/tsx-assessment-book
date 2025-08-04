#!/usr/bin/env python3
"""
Development environment setup script for TSX Assessment Book API.
This script helps set up the development environment quickly.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}")
    print(f"Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_pip():
    """Check if pip is available."""
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      check=True, capture_output=True)
        print("✅ pip is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip is not available")
        return False


def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("🔄 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def get_activate_command():
    """Get the appropriate activate command for the OS."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"


def install_dependencies():
    """Install project dependencies."""
    # Upgrade pip
    if not run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      "Upgrading pip"):
        return False
    
    # Install production dependencies
    if not run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      "Installing production dependencies"):
        return False
    
    # Install development dependencies
    if not run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-dev.txt'], 
                      "Installing development dependencies"):
        return False
    
    return True


def setup_pre_commit():
    """Set up pre-commit hooks."""
    try:
        subprocess.run([sys.executable, '-m', 'pre_commit', 'install'], 
                      check=True, capture_output=True)
        print("✅ Pre-commit hooks installed")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Pre-commit installation failed (optional)")
        return True


def run_initial_tests():
    """Run initial tests to verify setup."""
    print("\n🧪 Running initial tests to verify setup...")
    if run_command([sys.executable, '-m', 'pytest', 'tests/test_books.py', '-v'], 
                  "Running initial tests"):
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False


def main():
    """Main setup function."""
    print("🚀 TSX Assessment Book API - Development Setup")
    print("=" * 50)
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"Working directory: {os.getcwd()}")
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup pre-commit
    setup_pre_commit()
    
    # Run initial tests
    if not run_initial_tests():
        print("\n⚠️  Setup completed with test failures. Please review the output above.")
        sys.exit(1)
    
    # Success message
    print("\n" + "=" * 50)
    print("🎉 Development environment setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    print(f"   {get_activate_command()}")
    print("\n2. Run the application:")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\n3. Run tests:")
    print("   pytest tests/test_books.py -v")
    print("\n4. View available commands:")
    print("   make help")
    print("\n5. Access the API:")
    print("   - API: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("=" * 50)


if __name__ == '__main__':
    main() 