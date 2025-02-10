import pandas as pd
import google.generativeai as genai
from fastapi import HTTPException
import os
from .prompt import SYST_PROMPT
from dotenv import load_dotenv


# Load environment variables from the .env file
load_dotenv()
# Configure the Generative AI API
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Generate a response using the Generative AI model
model = genai.GenerativeModel("gemini-1.5-flash",system_instruction=SYST_PROMPT)

# Maintain a conversation history 
conversation_history = []
# Function to generate content with context preservation
def generate_with_context(message,model):
    print("----------------------------------")
    conversation_history.append(message)
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    context = " ".join(conversation_history)
    print("##################################")
    response = model.generate_content(context)
    print("***********************************")
    conversation_history.append(response.text)
    print(conversation_history)
    return response.text

# Function to handle chat logic with Generative AI API
def generate_response(message: str) -> str:
    try:        
        # print(user)
        # response = model.generate_content(message)        
        response = generate_with_context(message,model)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generative AI API error: {str(e)}")
    





















# # Load service provider data from an Excel file
# SERVICE_PROVIDERS_FILE = r"D:\academic_pro\service_providers.xlsx"
# service_providers = pd.read_excel(SERVICE_PROVIDERS_FILE)

# # Function to find the nearest service provider based on location
# def get_nearest_service_provider(location: str) -> str:
#     matching_providers = service_providers[service_providers['Location'].str.contains(location, case=False, na=False)]
#     if not matching_providers.empty:
#         provider = matching_providers.iloc[0]
#         return f"The nearest service provider is {provider['Name']} located at {provider['Address']}."
#     else:
#         return "Sorry, I couldn't find a service provider near your location."