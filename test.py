from transformers import pipeline

# Initialize the translation pipeline with the "facebook/hf-seamless-m4t-large" model
translation_pipeline = pipeline(
    task="translation", 
    model="Qwen/Qwen2.5-7B", 
    device=0  # Set to 0 for GPU or -1 for CPU
)

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

# Translate from Arabic to English
translated_text = translation_pipeline('translate arabic to english: ' + arabic_text)

# Print the translated text
print("Translated Text: ", translated_text[0]['translation_text'])
