import requests
import time

# Define the model and prompt
model = "qwen2.5:7b"
instruction = "You are an excellent Arabic to English translator. Translate the following text clearly and accurately and end it there.:\n"

with open("Media/testnew.txt", "r", encoding="utf-8") as file:
    content = file.read()

arabic_text = content

prompt = instruction + arabic_text

# Send request to Ollama API
def generate_response(own_prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": own_prompt,
            "temperature": 0.8,
            "stream": False,
        }
    )
    return response

start = time.time()
print('\n🔍🔍🔍 started translation...')
translation = generate_response(prompt)
time_took = time.time() - start
print(f"\n⏰⏰ Time took: {time_took:.2f}s")

# Check and print result
if translation.status_code == 200:
    result = translation.json()['response']
    print("Translation:📖📖\n", result)
else:
    print("Error:", translation.status_code, translation.text)