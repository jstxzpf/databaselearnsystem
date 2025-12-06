import os
from app import create_app, db
from models.user import User

def verify_database():
    print("Verifying database...")
    app = create_app('testing')
    with app.app_context():
        # 1. Test Table Creation
        try:
            db.create_all()
            print("SUCCESS: Database tables created.")
        except Exception as e:
            print(f"FAILURE: Database creation failed: {e}")
            return

        # 2. Test User Model
        try:
            user = User.get_or_create("test_user")
            print(f"SUCCESS: User created: {user}")
            
            user2 = User.get_or_create("test_user")
            print(f"SUCCESS: User retrieved: {user2}")
            
            if user.id != user2.id:
                print("FAILURE: User IDs do not match.")
            else:
                print("SUCCESS: User ID consistency check passed.")
                
        except Exception as e:
            print(f"FAILURE: User model test failed: {e}")

if __name__ == "__main__":
    verify_database()
