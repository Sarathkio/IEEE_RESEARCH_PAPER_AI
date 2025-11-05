import google.generativeai as genai
from dotenv import load_dotenv
import osa

# Load your API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Ask the API which models you can call
result = genai.list_models()  

print("Available models and supported generation methods:\n")
for m in result.models:
    print(f"{m.name}  →  {m.supported_generation_methods}")
