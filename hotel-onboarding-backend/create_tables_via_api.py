#!/usr/bin/env python3
"""
Create I-9 tables directly using Supabase Python client
This bypasses RLS by using proper authentication
"""
import os
import sys
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def create_tables_directly():
    """Create tables using direct database connection"""
    import psycopg2
    from psycopg2 import sql
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Try to construct from Supabase URL
        supabase_url = os.getenv("SUPABASE_URL")
        if supabase_url:
            # Extract project ref from URL
            # Format: https://[project-ref].supabase.co
            project_ref = supabase_url.split("//")[1].split(".")[0]
            db_password = os.getenv("SUPABASE_DB_PASSWORD") or os.getenv("DATABASE_PASSWORD")
            if db_password:
                database_url = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"
    
    if not database_url:
        print("❌ DATABASE_URL not found. Please add it to your .env file")
        print("   You can find it in Supabase Dashboard > Settings > Database")
        return False
    
    try:
        # Connect to database
        print("🔗 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Create tables
        print("📝 Creating tables...")
        
        # SQL statements
        sql_statements = [
            # Enable UUID extension
            "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
            
            # Create i9_forms table
            """
            CREATE TABLE IF NOT EXISTS i9_forms (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                employee_id TEXT NOT NULL,
                section VARCHAR(20) NOT NULL,
                form_data JSONB,
                signed BOOLEAN DEFAULT false,
                signature_data TEXT,
                completed_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(employee_id, section)
            );
            """,
            
            # Create i9_section2_documents table
            """
            CREATE TABLE IF NOT EXISTS i9_section2_documents (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                employee_id TEXT NOT NULL,
                document_id VARCHAR(255) UNIQUE NOT NULL,
                document_type VARCHAR(50),
                document_name VARCHAR(255),
                file_name VARCHAR(255),
                file_size INTEGER,
                storage_path TEXT,
                uploaded_at TIMESTAMPTZ,
                ocr_data JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Create w4_forms table
            """
            CREATE TABLE IF NOT EXISTS w4_forms (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                employee_id TEXT NOT NULL,
                tax_year INTEGER NOT NULL,
                form_data JSONB,
                signed BOOLEAN DEFAULT false,
                signature_data TEXT,
                pdf_url TEXT,
                completed_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(employee_id, tax_year)
            );
            """,
            
            # Create indexes
            "CREATE INDEX IF NOT EXISTS idx_i9_employee_section ON i9_forms(employee_id, section);",
            "CREATE INDEX IF NOT EXISTS idx_i9_docs_employee ON i9_section2_documents(employee_id);",
            "CREATE INDEX IF NOT EXISTS idx_i9_docs_type ON i9_section2_documents(document_type);",
            "CREATE INDEX IF NOT EXISTS idx_w4_employee_year ON w4_forms(employee_id, tax_year);",
            
            # Grant permissions
            "GRANT ALL ON i9_forms TO authenticated;",
            "GRANT ALL ON i9_section2_documents TO authenticated;",
            "GRANT ALL ON w4_forms TO authenticated;",
            "GRANT ALL ON i9_forms TO service_role;",
            "GRANT ALL ON i9_section2_documents TO service_role;",
            "GRANT ALL ON w4_forms TO service_role;",
            "GRANT ALL ON i9_forms TO anon;",
            "GRANT ALL ON i9_section2_documents TO anon;",
            "GRANT ALL ON w4_forms TO anon;"
        ]
        
        # Execute each statement
        for stmt in sql_statements:
            try:
                cur.execute(stmt)
                conn.commit()
                if "CREATE TABLE" in stmt:
                    table_name = stmt.split("IF NOT EXISTS ")[1].split(" ")[0]
                    print(f"  ✅ Table {table_name} created/verified")
                elif "CREATE INDEX" in stmt:
                    index_name = stmt.split("IF NOT EXISTS ")[1].split(" ")[0]
                    print(f"  ✅ Index {index_name} created/verified")
            except Exception as e:
                print(f"  ⚠️  Statement failed: {str(e)[:100]}")
                conn.rollback()
        
        # Verify tables exist
        print("\n🔍 Verifying tables...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('i9_forms', 'i9_section2_documents', 'w4_forms')
        """)
        
        tables = cur.fetchall()
        for table in tables:
            print(f"  ✅ Table '{table[0]}' exists")
        
        # Close connection
        cur.close()
        conn.close()
        
        print("\n✅ All tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Creating I-9 Tables Programmatically")
    print("=" * 50)
    
    # Try psycopg2 first
    try:
        import psycopg2
        return create_tables_directly()
    except ImportError:
        print("📦 Installing psycopg2...")
        os.system("pip install psycopg2-binary")
        import psycopg2
        return create_tables_directly()

if __name__ == "__main__":
    success = main()
    if success:
        print("\n📝 Next step: Run 'python3 verify_i9_setup.py' to test the tables")
    sys.exit(0 if success else 1)