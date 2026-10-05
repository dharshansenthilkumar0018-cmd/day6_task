"""Provider configuration for the Day 6 task."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "ollama").lower()
MODEL = os.getenv("MODEL", "qwen2.5:1.5b")

if PROVIDER == "ollama":
    BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")
elif PROVIDER == "groq":
    BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        raise RuntimeError("GROQ_API_KEY is required for Groq.")
elif PROVIDER in {"huggingface", "hf"}:
    BASE_URL = os.getenv("HF_BASE_URL", "https://router.huggingface.co/v1")
    API_KEY = os.getenv("HF_TOKEN")
    if not API_KEY:
        raise RuntimeError("HF_TOKEN is required for Hugging Face.")
else:
    BASE_URL = os.getenv("BASE_URL")
    API_KEY = os.getenv("API_KEY")
    if not BASE_URL or not API_KEY:
        raise RuntimeError("Set BASE_URL and API_KEY for the selected provider.")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

def banner(title):
    print(f"\n=== {title} | provider={PROVIDER} | model={MODEL} ===\n")
