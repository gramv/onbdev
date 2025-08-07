import requests

# Try to get properties from the HR endpoint
try:
    # First get HR token
    hr_users = requests.get("http://127.0.0.1:8000/api/hr-users").json()
    if hr_users:
        hr_token = hr_users[0]["user_id"]
        headers = {"Authorization": f"Bearer {hr_token}"}
        
        # Get properties
        properties = requests.get("http://127.0.0.1:8000/api/properties", headers=headers).json()
        if properties:
            prop = properties[0]
            print(f"\nProperty found:")
            print(f"Name: {prop['name']}")
            print(f"ID: {prop['id']}")
            print(f"\nApplication URL: http://localhost:3001/apply/{prop['id']}")
            
            # Get property info
            info = requests.get(f"http://127.0.0.1:8000/properties/{prop['id']}/info").json()
            print(f"\nDepartments available:")
            if "departments_and_positions" in info and info["departments_and_positions"]:
                for dept, positions in info["departments_and_positions"].items():
                    print(f"  - {dept}: {', '.join(positions)}")
            else:
                print("  No departments found in response")
except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure the backend is running at http://127.0.0.1:8000")