from fastapi import FastAPI
from typing import  Optional
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from assistant import chat_with_assistant
load_dotenv()


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
    response = chat_with_assistant(message, new, id_thread)
    return response