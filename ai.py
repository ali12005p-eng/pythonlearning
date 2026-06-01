import os
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)


async def generate_story(history: str):
    prompt = f"""
أنت كاتب لعبة سيناريو تفاعلية.

هذا تسلسل الأحداث الحالي بين المستخدم والبوت:

{history}

🔴 القواعد المهمة:
- لا تبدأ قصة جديدة نهائياً
- أكمل نفس السيناريو الحالي فقط
- حافظ على نفس الشخصيات والأحداث
- ردك لازم يكون استمرار مباشر لما حدث
- لا تعيد المقدمة أو البداية

اكتب التكملة الآن بشكل مشوق.
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "أنت كاتب قصص وسيناريوهات تفاعلية تستمر بدون إعادة البداية."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.9
    )

    return completion.choices[0].message.content
