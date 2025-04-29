from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
#BitsAndBytes needs NVIDIA for CUDA to run!

model_name = "Qwen/Qwen2.5-7B"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype="float16" # Or "bfloat16" if supported
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained(model_name)

# Arabic text to translate
arabic_text = """
أمد يقول شيخ في حديث الرسول صلى الله عليه وسلم الذي ما معناه صلاة المرء له نصفها ثلثها ربعها خمسها سدسها 
لماذا بدأ الرسول صلى الله عليه وسلم بالنصف ولم يبدأ بالكل هل هذا كمال للصلاة؟ الله أعلم أنه لم يبدأ 
بالكل لأن الكمال صعب الكمال صعب ولكن دون الكمال والناس درجات في هذا والخشوع هو روح الصلاة قد أفلح 
المؤمنون الذين هم في صلاتهم خاشعون فهو روح الصلاة والصلاة ليس فيها خشوع مثل الجسد الذي ليس فيه روح 
ولا يقبلها الله سبحانه وتعالى فلابد من خشوع القلب حضوره في الصلاة والناس يتفاوتون في هذا فمنهم من 
يكتب له الأجر الكامل ومنهم من يكتب له دون ذلك حسب حضور قلبه وخشوعه ولا يخشع القلب إلا مع التأمل 
والتدبر كتاب أنزلناه إليك مبارك ليتدبروا آياته وليتذكر أولو الألباب تدبروا القرآن قال ابن القيم رحمه 
الله وتدبر القرآن إن رمت الهدى فالعلم تحت تتبر القرآن اتخاذ مكان واحد في البيت
"""

# Prepare your input
prompt = "Translate Arabic to English: " + arabic_text
messages = [
    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

# Generate text
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512,
    do_sample=True,
    top_p=0.8,
    temperature=0.7,
    repetition_penalty=1.05
)
generated_ids = [output_ids[len(input_ids):] for output_ids, input_ids in zip(generated_ids, model_inputs["input_ids"])]
generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

print(generated_text)
