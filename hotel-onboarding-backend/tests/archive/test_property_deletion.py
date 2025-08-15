#!/usr/bin/env python3
"""Test property deletion with foreign key constraint handling"""

import asyncio
import httpx

async def test_property_deletion():
    async with httpx.AsyncClient() as client:
        # First login as HR
        login_response = await client.post(
            'http://localhost:8000/auth/login',
            json={'email': 'freshhr@test.com', 'password': 'test123'}
        )
        
        if login_response.status_code != 200:
            print(f'Login failed: {login_response.text}')
            return
            
        token = login_response.json().get('token')
        headers = {'Authorization': f'Bearer {token}'}
        
        # Get list of properties
        properties_response = await client.get(
            'http://localhost:8000/hr/properties',
            headers=headers
        )
        
        if properties_response.status_code == 200:
            properties = properties_response.json().get('data', [])
            print(f'Found {len(properties)} properties')
            
            # Try to delete the first property without active employees/applications
            for prop in properties:
                print(f"\nAttempting to delete property: {prop['name']} (ID: {prop['id']})")
                
                delete_response = await client.delete(
                    f"http://localhost:8000/hr/properties/{prop['id']}",
                    headers=headers
                )
                
                if delete_response.status_code == 200:
                    print(f'✅ Successfully deleted property: {delete_response.json()}')
                    break
                elif delete_response.status_code == 400:
                    error_detail = delete_response.json().get('detail', 'Unknown error')
                    print(f'⚠️  Cannot delete (expected): {error_detail}')
                else:
                    print(f'❌ Failed to delete: {delete_response.status_code} - {delete_response.text}')
        else:
            print(f'Failed to get properties: {properties_response.text}')

if __name__ == "__main__":
    asyncio.run(test_property_deletion())