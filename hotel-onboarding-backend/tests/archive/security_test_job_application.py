"""
Automated Security Testing Script for Job Application API
Tests all endpoints with malicious payloads
"""

import requests
import json
from datetime import datetime
from security_test_payloads import get_all_payloads, get_payloads_for_field

# Configuration
BASE_URL = "http://localhost:8000"
PROPERTY_ID = "property123"
APPLICATION_ENDPOINT = f"/apply/{PROPERTY_ID}"

# Test results storage
test_results = {
    "total_tests": 0,
    "blocked": 0,
    "passed": 0,
    "errors": [],
    "field_results": {}
}

def test_field(field_name, payload, valid_data):
    """Test a single field with a malicious payload"""
    # Create test data with the malicious payload
    test_data = valid_data.copy()
    test_data[field_name] = payload
    
    try:
        response = requests.post(
            f"{BASE_URL}{APPLICATION_ENDPOINT}",
            json=test_data
        )
        
        result = {
            "field": field_name,
            "payload": payload,
            "status_code": response.status_code,
            "response": response.text[:200] if response.text else ""
        }
        
        # Check if payload was blocked
        if response.status_code in [400, 422]:
            result["blocked"] = True
            test_results["blocked"] += 1
        elif response.status_code == 200:
            result["blocked"] = False
            test_results["passed"] += 1
            # This is concerning - payload was accepted
            test_results["errors"].append({
                "field": field_name,
                "payload": payload,
                "error": "PAYLOAD ACCEPTED - POTENTIAL VULNERABILITY"
            })
        else:
            result["blocked"] = True
            test_results["blocked"] += 1
        
        return result
        
    except Exception as e:
        test_results["errors"].append({
            "field": field_name,
            "payload": payload,
            "error": str(e)
        })
        return {
            "field": field_name,
            "payload": payload,
            "error": str(e),
            "blocked": True
        }

def run_security_tests():
    """Run comprehensive security tests on all fields"""
    
    # Valid baseline data
    valid_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "(555) 123-4567",
        "address": "123 Main Street",
        "city": "Springfield",
        "state": "IL",
        "zip_code": "62701",
        "date_of_birth": "1990-01-01",
        "position_applied": "Front Desk",
        "availability": {
            "monday": True,
            "tuesday": True,
            "wednesday": True,
            "thursday": True,
            "friday": True,
            "saturday": False,
            "sunday": False,
            "full_time": True,
            "part_time": False,
            "start_date": "2024-02-01"
        },
        "employment_history": [
            {
                "employer": "Previous Hotel",
                "position": "Receptionist",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "reason_for_leaving": "Career advancement"
            }
        ],
        "references": [
            {
                "name": "Jane Manager",
                "relationship": "Former Supervisor",
                "phone": "(555) 987-6543",
                "email": "jane.manager@example.com"
            }
        ],
        "emergency_contact": {
            "name": "Mary Doe",
            "relationship": "Sister",
            "phone": "(555) 456-7890"
        },
        "legal_eligibility": {
            "authorized_to_work": True,
            "require_visa_sponsorship": False,
            "convicted_of_crime": False,
            "crime_explanation": ""
        }
    }
    
    # Get all payloads
    all_payloads = get_all_payloads()
    
    # Test each field type
    fields_to_test = [
        ("first_name", "text"),
        ("last_name", "text"),
        ("email", "email"),
        ("phone", "phone"),
        ("address", "text"),
        ("city", "text"),
        ("state", "text"),
        ("zip_code", "zip"),
        ("position_applied", "text")
    ]
    
    print("Starting Security Testing...")
    print("=" * 60)
    
    for field_name, field_type in fields_to_test:
        print(f"\nTesting field: {field_name}")
        print("-" * 40)
        
        field_results = []
        payloads = get_payloads_for_field(field_name, field_type)
        
        for payload in payloads:
            test_results["total_tests"] += 1
            result = test_field(field_name, payload, valid_data)
            field_results.append(result)
            
            # Print progress
            if not result.get("blocked", True):
                print(f"⚠️  VULNERABILITY: {field_name} accepted: {payload[:50]}...")
            else:
                print(f"✓ Blocked: {payload[:50]}...")
        
        test_results["field_results"][field_name] = field_results
    
    # Generate report
    generate_report()

def generate_report():
    """Generate a comprehensive security test report"""
    
    report = f"""
# Security Test Report - Job Application API
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- Total Tests Run: {test_results['total_tests']}
- Payloads Blocked: {test_results['blocked']} ({test_results['blocked']/test_results['total_tests']*100:.1f}%)
- Payloads Accepted: {test_results['passed']} ({test_results['passed']/test_results['total_tests']*100:.1f}%)

## Critical Findings
"""
    
    if test_results["passed"] > 0:
        report += f"\n### ⚠️  SECURITY VULNERABILITIES FOUND\n"
        report += f"{test_results['passed']} malicious payloads were accepted!\n\n"
        
        for error in test_results["errors"]:
            if "POTENTIAL VULNERABILITY" in error.get("error", ""):
                report += f"- **{error['field']}**: Accepted `{error['payload']}`\n"
    else:
        report += "\n### ✅ No Critical Vulnerabilities Found\n"
        report += "All malicious payloads were properly rejected.\n"
    
    # Field-by-field analysis
    report += "\n## Field Analysis\n"
    for field_name, results in test_results["field_results"].items():
        blocked_count = sum(1 for r in results if r.get("blocked", True))
        total_count = len(results)
        
        report += f"\n### {field_name}\n"
        report += f"- Tests: {total_count}\n"
        report += f"- Blocked: {blocked_count} ({blocked_count/total_count*100:.1f}%)\n"
        
        # Show any accepted payloads
        accepted = [r for r in results if not r.get("blocked", True)]
        if accepted:
            report += f"- ⚠️  Accepted Payloads:\n"
            for r in accepted:
                report += f"  - `{r['payload']}`\n"
    
    # Save report
    with open("security_test_report.md", "w") as f:
        f.write(report)
    
    # Also save detailed JSON results
    with open("security_test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print("\n" + "=" * 60)
    print(report)
    print("\nDetailed results saved to:")
    print("- security_test_report.md")
    print("- security_test_results.json")

if __name__ == "__main__":
    print("Hotel Onboarding Security Testing Suite")
    print("=" * 60)
    print(f"Target: {BASE_URL}{APPLICATION_ENDPOINT}")
    print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server not responding. Please start the backend server.")
            exit(1)
    except:
        print("❌ Cannot connect to server. Please ensure backend is running on port 8000.")
        exit(1)
    
    run_security_tests()