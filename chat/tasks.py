from celery import shared_task
import requests

TOGETHER_AI_API_KEY = "8b283a377efef633e1ca5ab57de868d6ac25b1af08c8ecd7a2b41a79ede116ef"


@shared_task
def test_celery_task():
    print("✅ Celery is running a background task!")
    return "Success"


@shared_task
def generate_response(character, user_message, retrieved_dialogue):
    
    context = f"Character: {character}\nUser: {user_message}\nCharacter:"
    if retrieved_dialogue:
        context = f"Character: {character}\nMovie Dialogue: {retrieved_dialogue}\nUser: {user_message}\nCharacter:"

    payload = {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "messages": [{"role": "system", "content": context}],
        "temperature": 0.7,
        "max_tokens": 50
    }

    headers = {"Authorization": f"Bearer {TOGETHER_AI_API_KEY}", "Content-Type": "application/json"}

    response = requests.post("https://api.together.xyz/v1/chat/completions", json=payload, headers=headers)
    return response.json()
