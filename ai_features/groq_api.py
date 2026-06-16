import requests
from django.conf import settings

def call_groq_completions(messages, temperature=0.7, max_tokens=1024):
    """
    Executes a chat completion request to the Groq API using Llama 3.
    Returns None if the API key is not configured or in case of errors.
    """
    api_key = getattr(settings, 'GROQ_API_KEY', '')
    if not api_key or api_key.strip() == '' or api_key.startswith('gsk_xxxx'):
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=12
        )
        if response.status_code == 200:
            res_data = response.json()
            return res_data['choices'][0]['message']['content']
        else:
            print(f"Groq API Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to connect to Groq API: {e}")
    return None
