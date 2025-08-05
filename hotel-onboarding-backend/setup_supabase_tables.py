#!/usr/bin/env python3
"""
Setup Supabase tables using the Supabase Admin API
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_tables():
    """Create the necessary tables in Supabase using the REST API"""
    
    # Get Supabase credentials
    project_url = os.environ.get("SUPABASE_URL")
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not project_url or not service_role_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
        print("The SERVICE_ROLE_KEY is required for admin operations")
        sys.exit(1)
    
    # Extract project ref from URL
    # URL format: https://[project-ref].supabase.co
    project_ref = project_url.split('//')[1].split('.')[0]
    
    # SQL to create the onboarding_form_data table
    sql_query = """
    -- Create the onboarding_form_data table
    CREATE TABLE IF NOT EXISTS onboarding_form_data (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        token VARCHAR NOT NULL,
        employee_id VARCHAR NOT NULL,
        step_id VARCHAR NOT NULL,
        form_data JSONB NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(token, step_id)
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_onboarding_form_data_token ON onboarding_form_data(token);
    CREATE INDEX IF NOT EXISTS idx_onboarding_form_data_employee ON onboarding_form_data(employee_id);

    -- Create update trigger
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';

    CREATE TRIGGER update_onboarding_form_data_updated_at 
    BEFORE UPDATE ON onboarding_form_data 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

    -- Enable RLS
    ALTER TABLE onboarding_form_data ENABLE ROW LEVEL SECURITY;

    -- Create a policy that allows all operations (for now)
    CREATE POLICY "Allow all operations" ON onboarding_form_data
    FOR ALL USING (true) WITH CHECK (true);
    """
    
    # Use Supabase REST API to execute SQL
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json"
    }
    
    # First, let's check if the table already exists
    check_url = f"{project_url}/rest/v1/onboarding_form_data?limit=1"
    
    try:
        response = requests.get(check_url, headers=headers)
        if response.status_code == 200:
            print("✓ Table 'onboarding_form_data' already exists")
            return
        elif response.status_code == 404:
            print("Table 'onboarding_form_data' does not exist. Creating it now...")
        else:
            print(f"Unexpected response: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error checking table existence: {e}")
    
    # If table doesn't exist, we need to create it
    # Unfortunately, Supabase REST API doesn't support DDL operations
    # We need to use the Supabase Management API or SQL Editor
    
    print("\n" + "="*60)
    print("IMPORTANT: Table creation via API is not supported.")
    print("Please follow these steps to create the table:")
    print("="*60)
    print("\n1. Go to your Supabase Dashboard")
    print(f"2. Project URL: {project_url}")
    print("3. Navigate to SQL Editor")
    print("4. Create a new query")
    print("5. Copy and paste the following SQL:")
    print("\n" + "-"*60)
    print(sql_query)
    print("-"*60)
    print("\n6. Click 'Run' to execute the SQL")
    print("7. You should see 'Success' message")
    print("\nOnce done, your onboarding system will be ready for cross-device access!")

if __name__ == "__main__":
    create_tables()