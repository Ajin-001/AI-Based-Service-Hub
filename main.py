from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel, EmailStr
from uuid import uuid4
from sqlalchemy.orm import Session
from passlib.context import CryptContext


from .database import get_db, Auth  # Import the database connection and model
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

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

@app.post("/signup")
def sign_up(user: SignUpModel, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = db.query(Auth).filter(Auth.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and create user
    # hashed_password = pwd_context.hash(user.password)
    new_user = Auth(
        uuid=str(uuid4()),
        username=user.username,
        email=user.email,
        password=user.password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.uuid}

@app.post("/login")
def login(credentials: LoginModel, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(Auth).filter(Auth.email == credentials.email).first()
    print("***************************")
    print(user.password)
    print("***************************")
    if not user and not (credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "Login successful", "user_id": user.uuid}


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


# Optional: Route for rendering frontend
@app.get("/", response_class=JSONResponse)
async def chat_frontend(request: Request):
    """
    This function renders the chat frontend
    """
    return templates.TemplateResponse("index.html", {"request": request})










