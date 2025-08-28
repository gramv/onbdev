#!/bin/bash

# Script to generate test onboarding token using the API

echo "🔑 Generating test onboarding token..."

# Default values
EMPLOYEE_NAME="${1:-Test Employee}"
PROPERTY_ID="${2:-test-property-001}"

# Call the API endpoint
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/test/generate-onboarding-token" \
  -H "Content-Type: application/json" \
  -d "{\"employee_name\": \"$EMPLOYEE_NAME\", \"property_id\": \"$PROPERTY_ID\"}")

# Check if the request was successful
if echo "$RESPONSE" | grep -q '"success":true'; then
    # Extract the onboarding URL
    URL=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['onboarding_url'])")
    TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['token'])")
    EMPLOYEE_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['data']['test_employee']['id'])")
    
    echo "✅ Token generated successfully!"
    echo ""
    echo "📋 Employee Details:"
    echo "  ID: $EMPLOYEE_ID"
    echo "  Name: $EMPLOYEE_NAME"
    echo "  Property: $PROPERTY_ID"
    echo ""
    echo "🔗 Onboarding URL:"
    echo "  $URL"
    echo ""
    echo "📝 Raw Token:"
    echo "  $TOKEN"
    echo ""
    echo "💡 To open in browser, run:"
    echo "  open \"$URL\""
else
    echo "❌ Failed to generate token"
    echo "$RESPONSE" | python3 -m json.tool
fi