#!/usr/bin/env python3
"""
Test runner script for the TSX Assessment Book API.
This script helps run tests locally with proper setup and reporting.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print('='*60)
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print(f"Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    required_packages = [
        'pytest',
        'pytest-cov',
        'fastapi',
        'uvicorn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True


def main():
    parser = argparse.ArgumentParser(description='Run tests for TSX Assessment Book API')
    parser.add_argument('--test-file', default='tests/test_books.py', 
                       help='Specific test file to run (default: tests/test_books.py)')
    parser.add_argument('--coverage', action='store_true', 
                       help='Run tests with coverage report')
    parser.add_argument('--verbose', action='store_true', 
                       help='Run tests with verbose output')
    parser.add_argument('--parallel', action='store_true', 
                       help='Run tests in parallel')
    parser.add_argument('--lint', action='store_true', 
                       help='Run linting checks')
    parser.add_argument('--all', action='store_true', 
                       help='Run all checks (tests, coverage, linting)')
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🚀 TSX Assessment Book API - Test Runner")
    print(f"Working directory: {os.getcwd()}")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    success = True
    
    # Run tests
    if args.all or not any([args.coverage, args.lint]):
        test_command = ['pytest']
        
        if args.test_file:
            test_command.append(args.test_file)
        else:
            test_command.append('tests/')
        
        if args.verbose:
            test_command.append('-v')
        
        if args.parallel:
            test_command.extend(['-n', 'auto'])
        
        if args.coverage:
            test_command.extend([
                '--cov=app',
                '--cov-report=html',
                '--cov-report=term-missing',
                '--cov-report=xml'
            ])
        
        success &= run_command(test_command, "Running tests")
    
    # Run coverage if requested
    if args.coverage and not args.all:
        coverage_command = [
            'python', '-m', 'pytest', 'tests/', '-v',
            '--cov=app',
            '--cov-report=html',
            '--cov-report=term-missing',
            '--cov-report=xml'
        ]
        success &= run_command(coverage_command, "Running tests with coverage")
    
    # Run linting if requested
    if args.lint or args.all:
        # Check if linting tools are available
        try:
            import flake8
            import black
            import isort
            import mypy
        except ImportError:
            print("❌ Linting tools not installed. Install with: pip install -r requirements-dev.txt")
            success = False
        else:
            # Run flake8
            flake8_command = [
                'flake8', 'app/', 'tests/', 
                '--max-line-length=88', 
                '--extend-ignore=E203,W503'
            ]
            success &= run_command(flake8_command, "Running flake8 linting")
            
            # Run black check
            black_command = ['black', '--check', '--diff', 'app/', 'tests/']
            success &= run_command(black_command, "Running black formatting check")
            
            # Run isort check
            isort_command = ['isort', '--check-only', '--diff', 'app/', 'tests/']
            success &= run_command(isort_command, "Running isort import sorting check")
            
            # Run mypy
            mypy_command = ['mypy', 'app/', '--ignore-missing-imports']
            success &= run_command(mypy_command, "Running mypy type checking")
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All checks passed successfully!")
        print("📊 Coverage report available at: htmlcov/index.html")
        print("📋 Test results saved to: reports/")
    else:
        print("❌ Some checks failed. Please review the output above.")
        sys.exit(1)
    print('='*60)


if __name__ == '__main__':
    main() 