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
model = model_name or "qwen3:4b" # granite3.3:2b
print(f"🧮🧮🧮 Using model: {model}")
super_time_start = time.time()

def sanitize_model_name(model_name: str) -> str:
    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', model_name)
    return sanitized

#file_to_read = "testnew.txt"
output_file = f"{translate_file_name}_translation_{sanitize_model_name(model)}.txt"  # Define the output file name
translation_folder = 'Translation/'

instruction = """Translate the following Arabic text to English only. Replace "peace be upon him" with "ﷺ" and "God" with "Allah". Do not add any explanations or reasoning—only return to me the ENGLISH translation."""


#with open(f"Media/{file_to_read}", "r", encoding="utf-8") as file:
    #content = file.read()

arabic_text = transcribed_arabic_text

def chunk_text(text, max_words=800):
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

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

def clean_text(text):
    #text = text.replace('<think>', '').replace('</think>', '')
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

# Chunk and translate
chunks = chunk_text(arabic_text, max_words=200)
print(f"\n🧩 Divided input into {len(chunks)} chunks...")

full_translation = ""

previous_chunk_tail = ""
prev_chunk_context_length = 6

abs_translation_start_time = time.time()

for i, chunk in enumerate(chunks, 1):
    chunk_start_time = time.time()
    print(f"\n📦 Chunk {i}/{len(chunks)}", end="", flush=True)
    prompt = instruction + previous_chunk_tail + chunk
    wait_start = time.time()
    streaming_response = generate_streaming_response(prompt)
    print(f" ⏳ Chunk Start Time: {time.time() - wait_start:.2f}s\n")

    if streaming_response.status_code == 200:
        try:
            for line in streaming_response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    try:
                        json_data = json.loads(decoded_line)
                        response_part = json_data.get('response', '')
                        print(response_part, end='', flush=True)
                        full_translation += response_part
                    except json.JSONDecodeError:
                        print(f"\n❌ JSON Error: {decoded_line}")
            chunk_done_time = time.time()
            abs_chunk_time_took = chunk_done_time - abs_translation_start_time
            chunk_time_took = chunk_done_time - chunk_start_time
            # Add a newline after finishing a chunk
            full_translation += "\n\n"

            print(f'\n\n⏰⏰ {abs_chunk_time_took:.2f}s ({chunk_time_took:.2f})s')
            previous_chunk_tail = ' '.join(chunk.split()[-prev_chunk_context_length:])  # Take last 20 words for context
            print(f"PREV CHUNK🪡🪡🪡: {previous_chunk_tail}")
        except requests.exceptions.RequestException as e:
            print(f"\n❌ Streaming error: {e}")
    else:
        print("❌ Error:", streaming_response.status_code, streaming_response.text)

full_translation = clean_text(full_translation)
translation_time_took = time.time() - abs_translation_start_time
token_speed = (len(full_translation.split(' ')))/translation_time_took

print(f"\n⏰ Translation Total time: {translation_time_took:.2f}s | ⚡ Token Speed:{token_speed:.2f}/s")

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