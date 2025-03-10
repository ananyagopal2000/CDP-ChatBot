from openai import OpenAI
client = OpenAI()
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Get the API key
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

if not OpenAI.api_key:
    print("❌ OpenAI API key is missing! Check your .env file.")
else:
    print("✅ API key loaded successfully:", OpenAI.api_key[:5] + "..." + OpenAI.api_key[-5:])
