from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
أنت لعبة سيناريوهات تفاعلية.
كل مرة المستخدم يرد، قم ببناء قصة جديدة قصيرة (5-8 أسطر).
اجعل القصة تعتمد على اختيار المستخدم.
اجعل النهاية دائمًا مفتوحة ليكمل اللاعب.
لا تخرج عن دورك كلعبة.
"""

def generate_story(history):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history
    ]

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        temperature=0.9
    )

    return response.choices[0].message.content
