"""
Script to create/update admin user with properly hashed password
Run this script to create admin account
Usage: python create_admin.py
"""

from werkzeug.security import generate_password_hash
import mysql.connector
from config import Config

def create_admin():
    """Create or update admin user"""
    
    # Database connection
    conn = None
    cursor = None
    
    try:
        print("\n" + "="*50)
        print("  Admin User Creation Script")
        print("="*50 + "\n")
        
        # Connect to database
        print(" Connecting to database...")
        conn = mysql.connector.connect(**Config.DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        print("✓ Database connected successfully\n")
        
        # Admin details
        username = 'admin'
        email = 'admin@exam.com'
        password = 'admin123'
        full_name = 'System Administrator'
        
        # Hash the password properly
        print(" Hashing password...")
        password_hash = generate_password_hash(password, method='scrypt')
        print("✓ Password hashed successfully\n")
        
        # Check if admin exists
        print("🔍 Checking if admin user exists...")
        cursor.execute("SELECT user_id, username FROM users WHERE email = %s", (email,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing admin
            print(f"  Admin user already exists (ID: {existing['user_id']})")
            print(" Updating admin user...")
            
            query = """
                UPDATE users 
                SET password_hash = %s, 
                    username = %s, 
                    full_name = %s, 
                    role = 'admin', 
                    is_active = TRUE
                WHERE email = %s
            """
            cursor.execute(query, (password_hash, username, full_name, email))
            conn.commit()
            print("✓ Admin user updated successfully!\n")
        else:
            # Create new admin
            print("Creating new admin user...")
            
            query = """
                INSERT INTO users (username, email, password_hash, full_name, role, is_active)
                VALUES (%s, %s, %s, %s, 'admin', TRUE)
            """
            cursor.execute(query, (username, email, password_hash, full_name))
            conn.commit()
            print("✓ Admin user created successfully!\n")
        
        # Display credentials
        print("="*50)
        print("  Admin Login Credentials")
        print("="*50)
        print(f"  Email:    {email}")
        print(f"  Password: {password}")
        print("="*50)
        print("\nYou can now login with these credentials!\n")
        
        # Verify admin exists
        cursor.execute("""
            SELECT user_id, username, email, role, is_active 
            FROM users 
            WHERE email = %s
        """, (email,))
        admin = cursor.fetchone()
        
        if admin:
            print("Admin User Details:")
            print(f"   - User ID: {admin['user_id']}")
            print(f"   - Username: {admin['username']}")
            print(f"   - Email: {admin['email']}")
            print(f"   - Role: {admin['role']}")
            print(f"   - Active: {admin['is_active']}")
            print()
        
    except mysql.connector.Error as err:
        print(f"\nDatabase Error: {err}")
        print("   Make sure MySQL is running and database exists.")
        print("   Run: mysql -u root -p < database_setup.sql")
        
    except Exception as e:
        print(f"\nError: {e}")
        
    finally:
        # Close connections
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("🔌 Database connection closed.\n")


if __name__ == '__main__':
    create_admin()