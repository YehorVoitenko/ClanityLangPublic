import asyncio

from openai import OpenAI

from config.openai_config import OPENAI_TOKEN

openai_client = OpenAI(api_key=OPENAI_TOKEN)


async def ask_gpt_async(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        executor=None,
        func=lambda: openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        ),
    )
    return response.choices[0].message.content.strip()


def make_check_prompt(word, correct_translation, user_translation):
    return f"""
        Оцініть, чи правильний переклад українською слову "{word}".
        
        Правила:
        1. Якщо переклад правильний, відповідайте: "✅ Правильно!"
        2. Якщо переклад схожий або містить помилки, але близький за змістом, або буде відрізнятись 1-2 літери 
        (можливо користувач помилився в самому слові, але знає переклад). Тому якщо відрізнається 1-2 літери або переклад схожий – 
        відповідайте:
        "ℹ Схоже за змістом, але правильніше буде: {correct_translation}"
        3. Якщо переклад неправильний, відповідайте:
        "❌ Неправильно! Правильний переклад: {correct_translation}"
        
        Відповідь користувача: {user_translation}
""".strip()
