import requests
import os
from config import Config
api_key = Config.NVIDIA_API_KEY

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
print("Base URL:", Config.NVIDIA_BASE_URL)
print("Model:", Config.MODEL_NAME)

url = "https://integrate.api.nvidia.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {os.getenv('NVIDIA_API_KEY')}",
    "Content-Type": "application/json"
}

payload = {
    "model": Config.VISION_MODEL,
    "messages": [
        {
            "role": "user",
            "content": "Say hello."
        }
    ],
    "max_tokens": 50,
    "stream": False
}

print("Sending...")

r = requests.post(url, headers=headers, json=payload, timeout=60)

print(r.status_code)
print(r.text)