import requests
import time, json, re

def sanitize_model_name(model_name: str) -> str:
    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', model_name)
    return sanitized

# Define the model and prompt
model = "qwen2.5:14b-instruct-q3_K_M"

file_to_read = "testnew.txt"
output_file = f"{file_to_read.split('.')[0]}_translation_{sanitize_model_name(model)}.txt"  # Define the output file name
translation_folder = 'Translation/'

instruction = """Translate the following Arabic subtitles into English, maintaining the original sentence order. Present the translation in standard paragraph form, without numbering. Whenever the phrase "peace be upon him" appears, replace it with "ﷺ". Whenever the word 'God' appears, replace it with "Allah". Ensure the English translation accurately reflects the meaning of the Arabic text while striving to preserve the sequence of the original sentences. The input may contain consecutive text segments that should be translated in order. End the translation after rendering all input.
"""

with open(f"Media/{file_to_read}", "r", encoding="utf-8") as file:
    content = file.read()

arabic_text = content

prompt = instruction + arabic_text

# Send request to Ollama API with streaming enabled
def generate_streaming_response(own_prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": own_prompt,
            "temperature": 0.6,
            "stream": True,
        },
        stream=True,
    )
    return response

start = time.time()
print('\n🔍🔍🔍 started streaming translation...')
streaming_response = generate_streaming_response(prompt)
full_translation = ""  # Initialize an empty string to store the full translation

# Check and print streaming result
if streaming_response.status_code == 200:
    print("Streaming Translation:📖📖\n")
    try:
        for line in streaming_response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                try:
                    json_data = json.loads(decoded_line)
                    response_part = json_data.get('response', '')
                    print(response_part, end='', flush=True)
                    full_translation += response_part  # Append the current part to the full translation
                except json.JSONDecodeError:
                    print(f"Error decoding JSON: {decoded_line}")
        print()  # Add a newline at the end of the stream
    except requests.exceptions.RequestException as e:
        print(f"Error during streaming: {e}")
else:
    print("Error:", streaming_response.status_code, streaming_response.text)

time_took = time.time() - start
token_speed = (len(full_translation.split(' ')))/time_took

print(f"\n⏰ Total time: {time_took:.2f}s | ⚡ Token Speed:{token_speed:.2f}/s")

# Save the full translation to a file
try:
    with open(translation_folder + output_file, "w", encoding="utf-8") as outfile:
        outfile.write(full_translation)
    print(f"\n💾💾💾 Translation saved to: {translation_folder + output_file}")
except Exception as e:
    print(f"\n⚠️⚠️⚠️ Error saving to file: {e}")