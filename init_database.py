"""
Initialize database and create all necessary tables
"""
import sqlite3
import os
from datetime import datetime

def init_database():
    """Initialize database"""
    db_path = "account_plan_agent.db"
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name VARCHAR(255) UNIQUE NOT NULL,
                industry VARCHAR(100),
                company_size VARCHAR(50),
                website VARCHAR(255),
                country VARCHAR(100) NOT NULL DEFAULT 'Unknown',
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create account_plans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                content TEXT,
                status VARCHAR(50) DEFAULT 'draft',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                change_log JSON,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)
        
        # Create interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                plan_id INTEGER,
                interaction_type VARCHAR(50) NOT NULL,
                question TEXT,
                answer TEXT,
                structured_data JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id),
                FOREIGN KEY (plan_id) REFERENCES account_plans (id)
            )
        """)
        
        # Create question_templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category VARCHAR(100) NOT NULL,
                question_text TEXT NOT NULL,
                description TEXT,
                is_core BOOLEAN DEFAULT 1,
                follow_up_questions JSON,
                "order" INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create external_info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS external_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                info_type VARCHAR(50) NOT NULL,
                content TEXT,
                source_url VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id),
                UNIQUE(account_id, info_type)
            )
        """)
        
        # Create countries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add country column to existing accounts table if it doesn't exist
        try:
            cursor.execute("ALTER TABLE accounts ADD COLUMN country VARCHAR(100) DEFAULT 'Unknown'")
            print("✅ Added country column to accounts table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️  Country column already exists in accounts table")
            else:
                print(f"⚠️  Could not add country column: {e}")
        
        # Add updated_at column to interactions table if it doesn't exist
        try:
            cursor.execute("ALTER TABLE interactions ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            print("✅ Added updated_at column to interactions table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️  updated_at column already exists in interactions table")
            else:
                print(f"⚠️  Could not add updated_at column: {e}")
        
        # Add updated_at column to external_info table if it doesn't exist
        try:
            cursor.execute("ALTER TABLE external_info ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            print("✅ Added updated_at column to external_info table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️  updated_at column already exists in external_info table")
            else:
                print(f"⚠️  Could not add updated_at column: {e}")
        
        # Add order column to existing question_templates table if it doesn't exist
        try:
            cursor.execute('ALTER TABLE question_templates ADD COLUMN "order" INTEGER DEFAULT 0')
            print("✅ Added order column to question_templates table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("ℹ️  Order column already exists in question_templates table")
            else:
                print(f"⚠️  Could not add order column: {e}")
        
        # Insert default question templates
        default_questions = [
            ("Cooperation History", "What cooperation projects have you had with this company in the past?", "Understand historical cooperation", 1),
            ("Products & Services", "What products or services have you sold?", "Understand products and services sold", 2),
            ("Challenges & Issues", "What challenges or issues have you encountered in cooperation?", "Understand difficulties and challenges in cooperation", 3),
            ("Key Contacts", "Who are the key contacts?", "Understand key decision makers on the customer side", 4),
            ("Future Plans", "What are the next cooperation plans?", "Understand future cooperation planning", 5),
            ("Resource Needs", "Are there any missing support or resources currently?", "Understand support needed by customers", 6)
        ]
        
        for category, question_text, description, order_idx in default_questions:
            cursor.execute("""
                INSERT OR IGNORE INTO question_templates 
                (category, question_text, description, is_core, "order", is_active)
                VALUES (?, ?, ?, 1, ?, 1)
            """, (category, question_text, description, order_idx))
        
        # Insert default countries
        default_countries = [
            "United States", "China", "Japan", "Germany", "United Kingdom",
            "France", "India", "Italy", "Brazil", "Canada",
            "South Korea", "Russia", "Australia", "Spain", "Mexico",
            "Indonesia", "Netherlands", "Saudi Arabia", "Turkey", "Switzerland"
        ]
        
        for country_name in default_countries:
            cursor.execute("""
                INSERT OR IGNORE INTO countries (name, is_active)
                VALUES (?, 1)
            """, (country_name,))
        
        # Create default admin user (password: admin)
        # Use the same password hashing method as auth.py (salt + SHA-256)
        import hashlib
        import secrets
        
        admin_password = "admin"
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((admin_password + salt).encode()).hexdigest()
        full_hash = f"{salt}:{password_hash}"
        
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, password_hash, is_admin, is_active)
            VALUES (?, ?, 1, 1)
        """, ("admin", full_hash))
        
        # Commit changes
        conn.commit()
        print("✅ Database initialization successful!")
        print(f"   📁 Database file: {db_path}")
        print(f"   📊 Created all necessary tables:")
        print(f"      - accounts")
        print(f"      - account_plans")
        print(f"      - interactions")
        print(f"      - question_templates")
        print(f"      - external_info")
        print(f"      - countries")
        print(f"      - users")
        print(f"   📝 Inserted {len(default_questions)} default question templates")
        print(f"   🌍 Inserted {len(default_countries)} default countries")
        print(f"   👤 Created default admin user (username: admin, password: admin)")
        
        # Validate table structure
        cursor.execute("PRAGMA table_info(question_templates)")
        columns = cursor.fetchall()
        print(f"   🔍 question_templates table columns: {[col[1] for col in columns]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
