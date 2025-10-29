from google import genai

GEMINI_API_KEY = "AIzaSyAXfe3uvZ54HPNOt53SC7ZPcOQyTCromtQ"

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=(
        "Дай ровно список из 4 английских слов на тему 'Food' в формате Python. "
        "Ответ должен содержать ТОЛЬКО список, без текста, без кавычек ```python```, "
        "без комментариев и без пояснений. Пример правильного формата: ['apple', 'bread', 'milk', 'cheese']"
    )
)

response2 = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=(
f"""
Сгенерируй английское слово по теме: "Food"
И 1 правильный и 3 неправильных русских перевода

Формат строго:
WORD: <слово>
CORRECT: <правильный перевод>
WRONG:
- вариант1
- вариант2
- вариант3
"""    )
)

print(response2.text)
