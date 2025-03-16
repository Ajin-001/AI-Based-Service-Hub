import os
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import HTTPException
from .prompt import SYST_PROMPT

load_dotenv()
genai.configure(api_key=os.environ["CHATBOT_STARTER"])
llm = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYST_PROMPT)

# Use a dictionary to store conversation history per user
conversation_histories = {}

PERSISTENT_ISSUE_KEYWORDS = ["not fixed", "issue persists", "still not working", "problem remains", "didn't work", "not working"]
GOODBYE_KEYWORDS = ["bye", "goodbye", "see you later", "quit"]

def generate_with_context(message, model, user_id):
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []
    conversation_histories[user_id].append(message)
    context = " ".join(conversation_histories[user_id])
    response = model.generate_content(context)
    conversation_histories[user_id].append(response.text)
    print(f"User {user_id} history: {conversation_histories[user_id]}")
    return response.text

def generate_response(message: str, username: str = None, user_id: str = None) -> str:
    try:
        if any(keyword in message.lower() for keyword in GOODBYE_KEYWORDS):
            return f"See you later{', ' + username if username else ''}! Have a great day!"

        if any(keyword in message.lower() for keyword in PERSISTENT_ISSUE_KEYWORDS):
            return "It seems the issue is still unresolved. Would you like help finding a nearby service center?"

        response = generate_with_context(message, llm, user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generative AI API error: {str(e)}")

def reset_chat_history(user_id: str):
    if user_id in conversation_histories:
        del conversation_histories[user_id]
        print(f"Chat history reset for user {user_id}")
    else:
        print(f"No chat history found for user {user_id}")