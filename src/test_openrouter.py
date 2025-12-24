import requests

API_KEY = "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"

response = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:8000',
        'X-Title': 'RAG App Test'
    },
    json={
        'model': 'qwen/qwen3-4b:free',
        'messages': [
            {'role': 'user', 'content': 'Say hello in one word'}
        ]
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
