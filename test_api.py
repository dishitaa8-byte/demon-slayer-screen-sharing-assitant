from openai import OpenAI
from config import Config
import time

client = OpenAI(
    base_url=Config.NVIDIA_BASE_URL,
    api_key=Config.NVIDIA_API_KEY
)

print("Sending request...")
start = time.time()

response = client.chat.completions.create(
    model=Config.MODEL_NAME,
    messages=[
        {"role": "user", "content": "Say hello in one sentence."}
    ],
    max_tokens=2048,
    stream=False
)

print("Time:", time.time() - start)
print(response.choices[0].message.content)