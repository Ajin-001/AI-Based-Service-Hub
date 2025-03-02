from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from fastapi.requests import Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from typing import List
from uuid import uuid4
from datetime import date, time

# Setup logging
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

from ..database import get_db, Auth ,get_location_by_place,appointment_database  # Import the database connection and model
from ..google_api import chat  # Import your chat logic

# Define the FastAPI app
app = FastAPI()

templates = Jinja2Templates(directory=r".\src\templates")
# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend's URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define a Pydantic model for the chat message
class ChatMessage(BaseModel):
    # user: str
    message: str

# Define a Pydantic model for the chat response
class ChatResponse(BaseModel):
    responses: List[str]

class SignUpModel(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class AppointmentModel(BaseModel):
    place: str
    service_provider: str
    service: str
    date: str  
    time: str  
    user_id: str 

class AppointmentResponseModel(BaseModel):
    appointment_id: str

class locationResponseModel(BaseModel):
    location_data: dict
    

# Create password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Optional: Route for rendering frontend
@app.get("/", response_class=JSONResponse)
async def chat_frontend(request: Request):
    """
    This function renders the chat frontend
    """
    return templates.TemplateResponse("index.html", {"request": request})


# Define the signup endpoint
@app.post("/signup")
def sign_up(user: SignUpModel, db: Session = Depends(get_db)):
    try:
        # Check for empty fields
        if not user.email or not user.password or not user.username:
            raise HTTPException(
                status_code=400,
                detail="All fields are required"
            )
        
        # Check if email exists
        existing_user = db.query(Auth).filter(Auth.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Hash password before storing
        hashed_password = pwd_context.hash(user.password)
        
        # Create new user
        new_user = Auth(
            uuid=str(uuid4()),
            username=user.username,
            email=user.email,
            password=hashed_password,  # Store hashed password
        )
        
        # Add to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "message": "User registered successfully",
            "user_id": new_user.uuid
        }
        
    except Exception as e:
        # Rollback in case of error
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during registration: {str(e)}"
        )

# Define the login endpoint
@app.post("/login")
def login(credentials: LoginModel, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(Auth).filter(Auth.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Verify password using hash
    if not pwd_context.verify(credentials.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    return {
        "message": "Login successful",
        "user_id": user.uuid
    }


# Define the main chat endpoint
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(chat_message: ChatMessage):
    print("chat_message", chat_message.message)
    # if not chat_message.user or not chat_message.message:
    if not chat_message.message:
        raise HTTPException(status_code=400, detail="message fields are required.")

    # Generate a response using your chat logic
    response = chat.generate_response(chat_message.message)

    # Return the response as a list of strings
    return ChatResponse(responses=[response])


# Define the location endpoint
@app.get("/location/{place}/{service_provider}")
def get_location(place: str,service_provider:str, db: Session = Depends(get_db)):
    # Check if place is empty
    if not place:
        raise HTTPException(status_code=400, detail="Place field is required.")
    print("place", place)
    
    # Fetch location details from the database
    location_data = get_location_by_place(place,service_provider)
    
    print("location_data", location_data)
    # Check if location exists
    if not location_data:
        raise HTTPException(status_code=404, detail="Location not found.")
    
    # Converting to dictionary
    keys = ["id", "name", "address", "city", "location_name", "maps_link", "contact"]
    location_dict = dict(zip(keys, location_data[0]))

    # Return the location details as a JSON response
    return {"location_data": location_dict}


# Define the create appointment endpoint
@app.post("/schedule_appointment")
def create_appointment(appointment: AppointmentModel, db: Session = Depends(get_db)):
    try:
        print("heloooo")
        # Check for empty fields
        required_fields = ["place", "service_provider", "service", "date", "time", "user_id"]
        for field in required_fields:
            if not getattr(appointment, field, None):
                raise HTTPException(
                    status_code=400,
                    detail=f"{field} is required"
                )

        # Generate unique ID for appointment
        new_appointment = {
            "appointment_id": uuid4(),
            "place": appointment.place,
            "service_provider": appointment.service_provider,
            "service": appointment.service,
            "date": appointment.date,
            "time": appointment.time,
            "user_id": appointment.user_id
        }
        # print("hi")
    
        # Insert the new appointment into the database
        result = appointment_database(new_appointment)

        print("result", result) # Debugging

        return {
            "message": "Appointment created successfully",
            "appointment_id": result["appointment_id"]

        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during appointment creation: {str(e)}"
        )
