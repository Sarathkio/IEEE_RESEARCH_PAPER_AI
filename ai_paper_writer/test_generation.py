import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use the exact name you saw in list_models.py
model = genai.GenerativeModel("gemini-1.0")  

resp = model.generate_content("Generate a single sentence about why listing models matters.")
print("✅ Response:\n", resp.text)
