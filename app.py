from fastapi import FastAPI
from typing import  Optional
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from assistant import chat_with_assistant
load_dotenv()

from openai import OpenAI
client = OpenAI()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/get_information")
async def get_information(message: str, new: bool, id_thread: Optional[str] = None):
    if new:
        thread = client.beta.threads.create()
        id = thread.id
    elif new==False: 
        thread = client.beta.threads.retrieve(id_thread)  
        id = thread.id
    else:
        return {"error": "id_thread must be provided when new is False"}

    response = chat_with_assistant(message, thread, id)
    return response
