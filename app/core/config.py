import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
print("HF Token Loaded:", HF_TOKEN is not None)