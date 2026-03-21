import psycopg2
import os

# ==========================================
# 1. DATABASE CONFIGURATION (Render PostgreSQL)
# ==========================================
def get_db_connection():
    """
    Connects to the Render PostgreSQL database.
    It prefers the environment variable 'DATABASE_URL' for security,
    but falls back to your provided connection string for testing.
    """
    # 1. Try to get the URL from Render's environment settings (Best Practice)
    db_url = os.environ.get("DATABASE_URL")
    
    # 2. Fallback to your provided connection string if environment variable isn't set
    if not db_url:
        db_url = "postgresql://lie_t6gn_user:LhQvToUBBjIbOghXl7OI0nc2kZdip5Cv@dpg-d6qfsd450q8c73bhmpi0-a/lie_t6gn"
    
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def init_db():
    """
    Initializes the database by creating the 'students' table.
    Note: SERIAL is used for auto-increment in PostgreSQL.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Create table if it doesn't exist
            # We use DECIMAL(5, 2) to allow grades like 98.50
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    grade DECIMAL(5, 2) NOT NULL,
                    section VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Render PostgreSQL initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")

if __name__ == "__main__":
    # Running this file directly will initialize the table
    init_db()
