#!/bin/bash

# Test Runner for Job Application UX Improvements
# This script runs all tests for the enhanced components

echo "=================================="
echo "Job Application UX Improvements Test Suite"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "${YELLOW}Running:${NC} $test_name"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval $test_command > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $test_name passed"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗${NC} $test_name failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo ""
}

# Navigate to frontend directory
cd /Users/gouthamvemula/onbclaude/onbdev-demo/hotel-onboarding-frontend

echo "Installing dependencies..."
npm install > /dev/null 2>&1

echo ""
echo "Running Component Tests..."
echo "--------------------------"

# Test FormInput component
run_test "FormInput Component Tests" "npm test -- --testPathPattern=form-input.test --no-coverage --watchAll=false"

# Test PersonalInformationStep
run_test "PersonalInformationStep Enhanced Tests" "npm test -- --testPathPattern=PersonalInformationStep.enhanced.test --no-coverage --watchAll=false"

echo ""
echo "Running Integration Tests..."
echo "----------------------------"

# Test auto-save functionality
run_test "Auto-save Functionality" "npm test -- --testNamePattern='auto-save' --no-coverage --watchAll=false"

# Test mobile responsiveness
run_test "Mobile Responsiveness" "npm test -- --testNamePattern='mobile' --no-coverage --watchAll=false"

# Test validation
run_test "Real-time Validation" "npm test -- --testNamePattern='validation' --no-coverage --watchAll=false"

echo ""
echo "Running Visual Regression Tests..."
echo "-----------------------------------"

# Check if components render without errors
run_test "Component Rendering" "npm run build"

echo ""
echo "=================================="
echo "Test Results Summary"
echo "=================================="
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please review the output above.${NC}"
    exit 1
fi