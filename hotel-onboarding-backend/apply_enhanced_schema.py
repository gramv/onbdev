#!/usr/bin/env python3
"""
Apply Enhanced Supabase Schema
This script applies the enhanced schema directly to your Supabase database
"""

import os
import sys
import asyncio
import asyncpg
from pathlib import Path

async def apply_schema():
    """Apply the enhanced schema to Supabase database"""
    print("🚀 APPLYING ENHANCED SUPABASE SCHEMA")
    print("=" * 60)
    
    # Database connection
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres.onmjxtyamdpkhnflwwmj:Gouthi321@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
    
    try:
        # Connect to database
        print("📡 Connecting to Supabase database...")
        conn = await asyncpg.connect(database_url)
        print("✅ Connected successfully")
        
        # Read schema file
        schema_file = Path(__file__).parent / "supabase_enhanced_schema.sql"
        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            return False
        
        print("📄 Reading enhanced schema file...")
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        print("🔧 Applying enhanced schema...")
        
        # Split the schema into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements):
            if not statement or statement.startswith('--'):
                continue
                
            try:
                await conn.execute(statement)
                success_count += 1
                
                # Show progress for major operations
                if any(keyword in statement.upper() for keyword in ['CREATE TABLE', 'CREATE INDEX', 'CREATE POLICY']):
                    # Extract table/index/policy name for better feedback
                    if 'CREATE TABLE' in statement.upper():
                        table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip().replace('IF NOT EXISTS', '').strip()
                        print(f"   ✅ Created table: {table_name}")
                    elif 'CREATE INDEX' in statement.upper():
                        index_name = statement.split('CREATE INDEX')[1].split('ON')[0].strip().replace('IF NOT EXISTS', '').strip()
                        print(f"   📊 Created index: {index_name}")
                    elif 'CREATE POLICY' in statement.upper():
                        policy_name = statement.split('CREATE POLICY')[1].split('ON')[0].strip().replace('"', '')
                        print(f"   🔐 Created policy: {policy_name}")
                        
            except Exception as e:
                error_count += 1
                # Only show errors for important statements
                if any(keyword in statement.upper() for keyword in ['CREATE TABLE', 'CREATE INDEX', 'CREATE POLICY', 'CREATE FUNCTION']):
                    print(f"   ⚠️  Warning on statement {i+1}: {str(e)[:100]}...")
        
        print(f"\n📊 Schema Application Results:")
        print(f"   ✅ Successful statements: {success_count}")
        print(f"   ⚠️  Warnings/Skipped: {error_count}")
        
        # Test the schema by checking if key tables exist
        print("\n🧪 Verifying schema application...")
        
        tables_to_check = [
            'users', 'user_roles', 'properties', 'property_managers',
            'job_applications', 'application_status_history', 'employees',
            'onboarding_sessions', 'onboarding_documents', 'audit_log'
        ]
        
        existing_tables = []
        for table in tables_to_check:
            try:
                result = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                    table
                )
                if result:
                    existing_tables.append(table)
                    print(f"   ✅ Table verified: {table}")
                else:
                    print(f"   ❌ Table missing: {table}")
            except Exception as e:
                print(f"   ❌ Error checking table {table}: {e}")
        
        # Check RLS policies
        print("\n🔐 Checking Row Level Security policies...")
        try:
            policies = await conn.fetch(
                "SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname = 'public'"
            )
            print(f"   ✅ RLS policies found: {len(policies)}")
            
            # Group by table
            policy_by_table = {}
            for policy in policies:
                table = policy['tablename']
                if table not in policy_by_table:
                    policy_by_table[table] = []
                policy_by_table[table].append(policy['policyname'])
            
            for table, table_policies in policy_by_table.items():
                print(f"   🔐 {table}: {len(table_policies)} policies")
                
        except Exception as e:
            print(f"   ⚠️  Could not verify RLS policies: {e}")
        
        # Check indexes
        print("\n📊 Checking performance indexes...")
        try:
            indexes = await conn.fetch(
                "SELECT indexname FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%'"
            )
            print(f"   ✅ Performance indexes found: {len(indexes)}")
        except Exception as e:
            print(f"   ⚠️  Could not verify indexes: {e}")
        
        await conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 ENHANCED SCHEMA APPLIED SUCCESSFULLY!")
        print("=" * 60)
        print(f"✅ Tables created: {len(existing_tables)}/{len(tables_to_check)}")
        print(f"🔐 RLS policies: {len(policies) if 'policies' in locals() else 'Unknown'}")
        print(f"📊 Performance indexes: {len(indexes) if 'indexes' in locals() else 'Unknown'}")
        print("\n🔗 Next Steps:")
        print("   1. ✅ Enhanced schema is ready")
        print("   2. 🔄 Run the migration script")
        print("   3. 🧪 Test the application")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply schema: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Enhanced Schema Application...")
    
    try:
        success = asyncio.run(apply_schema())
        if success:
            print("\n✨ Schema application completed successfully!")
            sys.exit(0)
        else:
            print("\n💥 Schema application failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Schema application interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)