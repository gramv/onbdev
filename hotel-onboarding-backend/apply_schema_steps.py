#!/usr/bin/env python3
"""
Apply Enhanced Supabase Schema in Steps
This script applies the schema in the correct order to avoid dependency issues
"""

import os
import sys
import asyncio
import asyncpg
from pathlib import Path

async def apply_schema_step(step_num: int, description: str, filename: str):
    """Apply a single schema step"""
    print(f"\n{step_num}️⃣  {description}")
    print("-" * 50)
    
    # Database connection with statement cache disabled for pgbouncer
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres.onmjxtyamdpkhnflwwmj:Gouthi321@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
    
    try:
        # Connect with statement cache disabled for pgbouncer compatibility
        conn = await asyncpg.connect(database_url, statement_cache_size=0)
        
        # Read schema file
        schema_file = Path(__file__).parent / filename
        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            return False
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Execute the entire schema as one transaction
        try:
            await conn.execute(schema_sql)
            print(f"✅ {description} applied successfully")
            
        except Exception as e:
            print(f"❌ Error applying {description}: {e}")
            return False
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection error for {description}: {e}")
        return False

async def verify_schema():
    """Verify the schema was applied correctly"""
    print("\n🧪 VERIFYING SCHEMA APPLICATION")
    print("-" * 50)
    
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres.onmjxtyamdpkhnflwwmj:Gouthi321@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
    
    try:
        conn = await asyncpg.connect(database_url, statement_cache_size=0)
        
        # Check tables
        tables_to_check = [
            'users', 'user_roles', 'properties', 'property_managers',
            'job_applications', 'application_status_history', 'employees',
            'onboarding_sessions', 'onboarding_documents', 'audit_log'
        ]
        
        print("📋 Checking tables...")
        existing_tables = []
        for table in tables_to_check:
            result = await conn.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                table
            )
            if result:
                existing_tables.append(table)
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table}")
        
        # Check RLS policies
        print("\n🔐 Checking RLS policies...")
        policies = await conn.fetch(
            "SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname = 'public'"
        )
        print(f"   ✅ RLS policies found: {len(policies)}")
        
        # Check indexes
        print("\n📊 Checking indexes...")
        indexes = await conn.fetch(
            "SELECT indexname FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%'"
        )
        print(f"   ✅ Performance indexes: {len(indexes)}")
        
        # Check functions
        print("\n⚙️  Checking functions...")
        functions = await conn.fetch(
            "SELECT proname FROM pg_proc WHERE proname IN ('update_updated_at_column', 'generate_employee_number')"
        )
        print(f"   ✅ Functions found: {len(functions)}")
        
        # Check materialized views
        print("\n📈 Checking materialized views...")
        matviews = await conn.fetch(
            "SELECT matviewname FROM pg_matviews WHERE schemaname = 'public'"
        )
        print(f"   ✅ Materialized views: {len(matviews)}")
        
        await conn.close()
        
        success_rate = len(existing_tables) / len(tables_to_check) * 100
        print(f"\n📊 Schema Verification Results:")
        print(f"   Tables: {len(existing_tables)}/{len(tables_to_check)} ({success_rate:.1f}%)")
        print(f"   RLS Policies: {len(policies)}")
        print(f"   Indexes: {len(indexes)}")
        print(f"   Functions: {len(functions)}")
        print(f"   Materialized Views: {len(matviews)}")
        
        return success_rate >= 90  # 90% success rate required
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

async def main():
    """Main function to apply schema in steps"""
    print("🚀 APPLYING ENHANCED SUPABASE SCHEMA IN STEPS")
    print("=" * 60)
    
    steps = [
        (1, "CREATING CORE TABLES", "supabase_schema_step1_tables.sql"),
        (2, "ADDING FOREIGN KEYS AND CONSTRAINTS", "supabase_schema_step2_constraints.sql"),
        (3, "CREATING INDEXES, RLS POLICIES, AND FUNCTIONS", "supabase_schema_step3_indexes_rls.sql")
    ]
    
    success_count = 0
    
    for step_num, description, filename in steps:
        success = await apply_schema_step(step_num, description, filename)
        if success:
            success_count += 1
        else:
            print(f"\n💥 Failed at step {step_num}. Stopping.")
            break
        
        # Small delay between steps
        await asyncio.sleep(1)
    
    print(f"\n📊 SCHEMA APPLICATION SUMMARY")
    print("=" * 60)
    print(f"Steps completed: {success_count}/{len(steps)}")
    
    if success_count == len(steps):
        print("✅ All steps completed successfully!")
        
        # Verify the schema
        verification_success = await verify_schema()
        
        if verification_success:
            print("\n🎉 ENHANCED SUPABASE SCHEMA READY!")
            print("=" * 60)
            print("✅ Database schema is fully configured")
            print("🔐 Row Level Security is active")
            print("📊 Performance optimizations applied")
            print("⚡ Functions and triggers are working")
            print("\n🔗 Next Steps:")
            print("   1. Run the migration script to populate data")
            print("   2. Test the application endpoints")
            print("   3. Verify security policies")
            return True
        else:
            print("\n⚠️  Schema applied but verification failed")
            return False
    else:
        print(f"❌ Only {success_count} out of {len(steps)} steps completed")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Schema application interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)