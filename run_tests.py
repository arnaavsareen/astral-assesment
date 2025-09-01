#!/usr/bin/env python3
"""
Test Runner Script for Astral Assessment

This script provides easy commands for running different test categories.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Astral Assessment Test Runner")
    parser.add_argument(
        "test_type",
        choices=["all", "core", "examples", "linkedin", "inngest", "quick"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests with verbose output"
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    if not (project_root / "requirements.txt").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Build pytest command
    verbose_flag = "-v" if args.verbose else ""
    
    if args.test_type == "all":
        cmd = f"python -m pytest {verbose_flag}"
        success = run_command(cmd, "All Tests")
        
    elif args.test_type == "core":
        cmd = f"python -m pytest tests/domains/intelligence_collection/ {verbose_flag}"
        success = run_command(cmd, "Core Business Logic Tests")
        
    elif args.test_type == "examples":
        cmd = f"python -m pytest tests/test_examples.py {verbose_flag}"
        success = run_command(cmd, "Real Company Examples Tests")
        
    elif args.test_type == "linkedin":
        cmd = f"python -m pytest tests/test_linkedin_integration.py {verbose_flag}"
        success = run_command(cmd, "LinkedIn Integration Tests")
        
    elif args.test_type == "inngest":
        cmd = f"python -m pytest tests/test_inngest_integration.py {verbose_flag}"
        success = run_command(cmd, "Inngest Integration Tests")
        
    elif args.test_type == "quick":
        # Run a subset of tests for quick validation
        cmd = f"python -m pytest tests/domains/intelligence_collection/test_process.py::TestProcessRegistration::test_website_only_registration {verbose_flag}"
        success = run_command(cmd, "Quick Validation Test")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 