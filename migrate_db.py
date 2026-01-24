from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Check if column exists first or just try to add it
            db.session.execute(text("ALTER TABLE bus ADD COLUMN booked_seats INTEGER DEFAULT 0"))
            db.session.commit()
            print("Successfully added 'booked_seats' column to 'bus' table.")
        except Exception as e:
            print(f"Error during migration: {e}")
            print("The column might already exist.")

if __name__ == "__main__":
    migrate()
