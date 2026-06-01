import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

async def generate_story(user_input: str):
    prompt = f"""
أنت كاتب قصص وسيناريوهات تفاعلية.
المستخدم كتب: {user_input}

اكتب سيناريو قصير ومثير وخلّه تفاعلي.
"""

    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": "أنت مساعد يكتب سيناريوهات تفاعلية ممتعة."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9
    )

    return completion.choices[0].message.content
