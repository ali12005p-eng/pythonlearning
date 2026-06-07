import os
import re
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)


# =========================
# 🧹 فلترة اللغة العربية
# =========================

def clean_arabic_text(text: str):
    text = re.sub(r"[A-Za-z]+", "", text)

    text = re.sub(
        r"[^\u0600-\u06FF0-9\s\.\،\!\؟\:\-\(\)]",
        "",
        text
    )

    text = re.sub(r"\s+", " ", text).strip()

    return text


# =========================
# 🎮 توليد القصة
# =========================

async def generate_story(
    character_name: str,
    gender: str,
    story_type: str,
    story_summary: str,
    history: str,
    player_action: str
):

    prompt = f"""
أنت مدير لعبة RPG عربية احترافية ومتقدمة.

بيانات الشخصية:

الاسم: {character_name}
الجنس: {gender}
نوع العالم: {story_type}

ملخص القصة:

{story_summary}

آخر الأحداث:

{history}

تصرف اللاعب الجديد:

{player_action}

قواعد إلزامية:

1- اعتبر أن اللاعب يعيش داخل هذا العالم منذ فترة طويلة.

2- حافظ على نفس العالم والشخصيات.

3- لا تنشئ بطلاً جديداً.

4- اسم اللاعب دائماً هو:
{character_name}

5- يجب أن تؤثر أفعال اللاعب على العالم.

6- تذكر العلاقات السابقة والعداوات والمكاسب.

7- لا تضع خيارات مرقمة.

8- اسمح للاعب بكتابة أي تصرف يريده.

9- لا تنهِ القصة بسهولة.

10- اجعل الرد طويلاً ومشوقاً وسينمائياً.

11- اجعل الشخصيات تتذكر اللاعب.

12- اجعل العالم يتطور باستمرار.

13- اختم دائماً بموقف يحتاج إلى قرار جديد.

اكتب الرد الآن.
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
أنت مدير لعبة RPG عربي احترافي.

مهم جداً:

- الحفاظ على استمرارية القصة.
- تذكر جميع الشخصيات المهمة.
- تذكر الأحداث السابقة.
- عدم تغيير العالم فجأة.
- عدم نسيان تاريخ اللاعب.
- استخدام العربية الفصحى فقط.
- منع الكلمات الأجنبية.
- جعل العالم حياً ومتطوراً.
- جعل كل قرار يؤثر على المستقبل.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.9,
        max_tokens=1400
    )

    raw_text = completion.choices[0].message.content

    return clean_arabic_text(raw_text)


# =========================
# 📖 تحديث ملخص القصة
# =========================

async def generate_summary(
    current_summary: str,
    history: str
):

    prompt = f"""
قم بتحديث ملخص القصة التالي.

الملخص الحالي:

{current_summary}

الأحداث الجديدة:

{history}

التعليمات:

- احتفظ بالشخصيات المهمة.
- احتفظ بالأماكن المهمة.
- احتفظ بالعلاقات والعداوات.
- احتفظ بالمكاسب والخسائر.
- تجاهل التفاصيل غير المهمة.
- أنشئ ملخصاً واضحاً ومختصراً.
- لا يتجاوز 700 كلمة.
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
أنت مسؤول عن تلخيص قصص RPG.

احتفظ فقط بالأحداث المهمة
والشخصيات المهمة
والمعلومات التي يجب تذكرها مستقبلاً.
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5,
        max_tokens=800
    )

    raw_text = completion.choices[0].message.content

    return clean_arabic_text(raw_text)
