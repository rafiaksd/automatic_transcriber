from transformers import pipeline
import os, time

# ✅ Use the correct Arabic-to-English model
translation_pipe = pipeline("translation_ar_to_en", model="Helsinki-NLP/opus-mt-tc-big-ar-en")

folder_name = "Media/"
file_name = "testnew.txt"  # Input file name

# Step 1: Read Arabic text from file
input_file = os.path.join(folder_name, file_name)
with open(input_file, "r", encoding="utf-8") as file:
    text_to_translate = file.read()

# Step 2: Translate Arabic to English
start = time.time()
translated = translation_pipe(text_to_translate, max_length=512)
time_took = time.time() - start

translated_text = translated[0]['translation_text']

# Step 3: Save translated result
base_name = os.path.splitext(file_name)[0]
output_file = os.path.join(folder_name, f"{base_name}_en.txt")  # Save in same folder with _en suffix

with open(output_file, "w", encoding="utf-8") as file:
    file.write(translated_text)

print(f"🕗🕗 Time took: {time_took:.2f}s")
print(f"✅ Translation saved to: {output_file}")
