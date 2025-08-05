import ollama

def summarize_text(text):
    """Summarizes text using the Llama 3 model."""
    response = ollama.chat(
        model='llama3',
        messages=[
            {
                'role': 'user',
                'content': f'Summarize this text: {text}',
            },
        ],
    )
    return response['message']['content']

text_to_summarize = """The ancient city of Petra, located in southwestern Jordan, is a world-renowned archaeological site. Carved directly into vibrant red sandstone cliffs, it is often referred to as the "Rose City." Established as the capital of the Nabataean kingdom around the 4th century BC, Petra was a major trading hub, strategically positioned along key caravan routes. Its prosperity was built on controlling trade in incense, myrrh, and spices. The most famous structure, the Treasury (Al-Khazneh), is an elaborately carved tomb believed to be a mausoleum for a Nabataean king. For centuries, Petra was lost to the Western world until it was rediscovered in 1812 by Swiss explorer Johann Ludwig Burckhardt. Today, it stands as a UNESCO World Heritage site and one of the new Seven Wonders of the World, drawing millions of tourists who are captivated by its unique rock-cut architecture and rich history."""

print(summarize_text(text_to_summarize))