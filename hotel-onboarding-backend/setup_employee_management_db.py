#!/usr/bin/env python3
"""
Setup Employee Management Database Tables
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.supabase_service_enhanced import EnhancedSupabaseService

async def create_tables():
    """Create employee management tables"""
    supabase = EnhancedSupabaseService()
    
    # Read the SQL file
    with open('create_employee_management_tables.sql', 'r') as f:
        sql_content = f.read()
    
    # Split by semicolons and execute each statement
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    print(f"Found {len(statements)} SQL statements to execute...")
    
    for i, statement in enumerate(statements, 1):
        try:
            print(f'[{i}/{len(statements)}] Executing: {statement[:100]}...')
            result = await supabase.execute_query(statement)
            print('✓ Success')
        except Exception as e:
            print(f'✗ Error: {e}')
            # Continue with other statements
            continue
    
    print("\n✅ Employee management database setup completed!")

if __name__ == "__main__":
    asyncio.run(create_tables())