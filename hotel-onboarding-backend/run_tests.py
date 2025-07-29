#!/usr/bin/env python3
"""
Test runner for Hotel Onboarding System
Runs all test suites with coverage reporting
"""
import subprocess
import sys
import os
from pathlib import Path

# Test categories
TEST_SUITES = {
    "unit": {
        "description": "Unit tests for individual components",
        "path": "tests/",
        "pattern": "test_*.py",
        "exclude": ["test_integration.py", "test_three_phase_workflow.py"]
    },
    "integration": {
        "description": "Integration tests for API endpoints",
        "path": "tests/test_integration.py",
        "markers": "-m integration"
    },
    "compliance": {
        "description": "Federal compliance tests (I-9, W-4, ESIGN)",
        "path": "tests/test_compliance.py",
        "markers": "-m compliance"
    },
    "workflow": {
        "description": "Three-phase workflow tests",
        "path": "tests/test_three_phase_workflow.py"
    },
    "auth": {
        "description": "Authentication and authorization tests",
        "path": "tests/test_authentication.py",
        "markers": "-m security"
    },
    "all": {
        "description": "All tests with coverage report",
        "path": "tests/",
        "coverage": True
    }
}


def run_command(cmd: list, cwd: str = None) -> int:
    """Run a command and return exit code"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


def run_backend_tests(suite: str = "all"):
    """Run backend test suite"""
    print(f"\n{'='*60}")
    print(f"Running Backend Tests: {suite}")
    print(f"{'='*60}\n")
    
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    if suite not in TEST_SUITES:
        print(f"Unknown test suite: {suite}")
        print(f"Available suites: {', '.join(TEST_SUITES.keys())}")
        return 1
    
    config = TEST_SUITES[suite]
    print(f"Description: {config['description']}\n")
    
    # Build pytest command
    cmd = ["poetry", "run", "pytest"]
    
    # Add test path
    if "path" in config:
        cmd.append(config["path"])
    
    # Add markers
    if "markers" in config:
        cmd.extend(config["markers"].split())
    
    # Add coverage if requested
    if config.get("coverage"):
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Add verbosity
    cmd.append("-v")
    
    # Add color
    cmd.append("--color=yes")
    
    # Run tests
    exit_code = run_command(cmd)
    
    if exit_code == 0:
        print(f"\n✅ {suite} tests passed!")
        if config.get("coverage"):
            print("\nCoverage report generated in htmlcov/index.html")
    else:
        print(f"\n❌ {suite} tests failed!")
    
    return exit_code


def run_frontend_tests():
    """Run frontend test suite"""
    print(f"\n{'='*60}")
    print("Running Frontend Tests")
    print(f"{'='*60}\n")
    
    frontend_dir = Path(__file__).parent.parent / "hotel-onboarding-frontend"
    
    if not frontend_dir.exists():
        print("Frontend directory not found!")
        return 1
    
    # Run Jest tests
    cmd = ["npm", "test", "--", "--coverage", "--watchAll=false"]
    exit_code = run_command(cmd, cwd=str(frontend_dir))
    
    if exit_code == 0:
        print("\n✅ Frontend tests passed!")
    else:
        print("\n❌ Frontend tests failed!")
    
    return exit_code


def run_specific_test(test_file: str):
    """Run a specific test file"""
    print(f"\n{'='*60}")
    print(f"Running Specific Test: {test_file}")
    print(f"{'='*60}\n")
    
    cmd = ["poetry", "run", "pytest", test_file, "-v", "--color=yes"]
    return run_command(cmd)


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hotel Onboarding System Test Runner")
    parser.add_argument(
        "suite",
        nargs="?",
        default="all",
        choices=list(TEST_SUITES.keys()) + ["frontend", "full"],
        help="Test suite to run"
    )
    parser.add_argument(
        "-f", "--file",
        help="Run specific test file"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage report"
    )
    
    args = parser.parse_args()
    
    if args.file:
        # Run specific file
        exit_code = run_specific_test(args.file)
    elif args.suite == "frontend":
        # Run frontend tests only
        exit_code = run_frontend_tests()
    elif args.suite == "full":
        # Run all backend and frontend tests
        backend_code = run_backend_tests("all")
        frontend_code = run_frontend_tests()
        exit_code = backend_code or frontend_code
    else:
        # Run backend test suite
        if args.no_coverage and args.suite == "all":
            TEST_SUITES["all"]["coverage"] = False
        exit_code = run_backend_tests(args.suite)
    
    # Print summary
    print(f"\n{'='*60}")
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print(f"{'='*60}\n")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())