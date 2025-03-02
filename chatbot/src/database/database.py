from sqlalchemy import create_engine, text, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os   # Import the os module

# Load environment variables from .env file
load_dotenv()

# Database credentials
DATABASE_URL = os.getenv("mysql+pymysql://root:@localhost:3306/chat_bot_academia")  # Use .get() to avoid KeyError

# SQLAlchemy engine and session setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Models
class Auth(Base):
    __tablename__ = "auth"
    uuid = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

# Dependency to get a database session
def get_db():
    """Provides a session for interacting with the database."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to fetch location details by place
def get_location_by_place(place_value,service_provider):
    """Fetches all details from `location_table` where `place` matches the given value."""
    try:
        with engine.connect() as conn:
            print("Database connected successfully!")

            query = text("SELECT * FROM location_table WHERE place = :place AND service_provider = :service_provider")
            result = conn.execute(query, {"place": place_value,"service_provider":service_provider})

            rows = result.fetchall()

        return rows  # Returns a list of tuples

    except Exception as e:
        return f"Error: {e}"
    

def appointment_database(new_appointment):
    """Inserts a new appointment into the `appointments` table."""
    try:
        # Ensure new_appointment is a dictionary
        if not isinstance(new_appointment, dict):
            raise ValueError("Invalid input: new_appointment must be a dictionary.")

        # Open a database session
        with engine.begin() as conn:  # `begin()` automatically commits if no errors occur
            print("Database connected successfully!")
            
            # Define the SQL query
            query = text("""
                INSERT INTO appointments (appointment_id, place, service_provider, service, date, time, user_id) 
                VALUES (:appointment_id, :place, :service_provider, :service, :date, :time, :user_id)
            """)

            print("Inserting:", new_appointment)

            # Execute query
            conn.execute(query, new_appointment)

        return {
            "message": "Appointment created successfully",
            "appointment_id": new_appointment["appointment_id"]
        }

    except Exception as e:
        return {"error": str(e)}
