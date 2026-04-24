import os
from dotenv import load_dotenv
from huggingface_hub import HfApi, InferenceClient

load_dotenv()
api = HfApi(token=os.getenv("HF_API_KEY"))
print("Account Info:", api.whoami())

client = InferenceClient(api_key=os.getenv("HF_API_KEY"))
result = client.text_generation(
    prompt="Hello Hugging Face! Test successful.",
    model="google/flan-t5-small",
    max_new_tokens=30
)
print(result)
