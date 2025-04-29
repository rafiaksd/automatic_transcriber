import time, json, re, os, sys, time, requests

file_to_test = "sheikhfawzanlong.txt"
with open(f"Media/{file_to_test}", "r", encoding="utf-8") as file:
    arabic_text_from_file = file.read()

word_to_view = 100 #100 words
sample = arabic_text_from_file.split(' ')[:word_to_view]
sample = " ".join(sample)
print('Sample Text:\n' + sample + '\n')

translate_file_name = file_to_test.split('.')[0] + '_TEST'
transcribed_arabic_text = arabic_text_from_file

if len(transcribed_arabic_text) < 5:
    raise ValueError("💀💀💀 No transcription happened, exiting...")

model_name = sys.argv[1] if len(sys.argv) > 1 else None
model = model_name or "qwen2.5:7b-instruct" #qwen2.5:7b-instruct, qwen2.5:14b-instruct-q3_K_M
print(f"🧮🧮🧮 Using model: {model}")
super_time_start = time.time()

def sanitize_model_name(model_name: str) -> str:
    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', model_name)
    return sanitized

#file_to_read = "testnew.txt"
output_file = f"{translate_file_name}_translation_{sanitize_model_name(model)}.txt"  # Define the output file name
translation_folder = 'Translation/'

instruction = """Translate the following Arabic subtitles into English. Whenever the phrase "peace be upon him" appears, replace it with "ﷺ". Whenever the word 'God' appears, replace it with "Allah". End the translation after rendering all input.
"""

#with open(f"Media/{file_to_read}", "r", encoding="utf-8") as file:
    #content = file.read()

arabic_text = transcribed_arabic_text

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
print('\n💬📙📙 Started Streaming Translation...')
wait_start = time.time()
streaming_response = generate_streaming_response(prompt)
print(f"⏳ Delay to Start Translation: {time.time() - wait_start:.2f}s\n")
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

save_translation_file_name = translation_folder + output_file
# Save the full translation to a file
try:
    with open(save_translation_file_name, "w", encoding="utf-8") as outfile:
        outfile.write(full_translation)
    print(f"\n💾💾💾 Translation saved to: {save_translation_file_name}")

    #finished
    super_time_end = time.time()
    super_time_took = super_time_end - super_time_start
    print(f"🏆🏆🏆 FINISHED TRANSLATION 🏆🏆🏆 | TOTAL TIME : ⏱️⏱️⏱️ {super_time_took:.2f}s")

    # 🔓 Open file in default editor (Notepad on Windows)
    cwd = os.getcwd()
    complete_file_path = cwd + '/' + save_translation_file_name
    os.startfile(complete_file_path)
except Exception as e:
    print(f"\n⚠️⚠️⚠️ Error saving to file: {e}")