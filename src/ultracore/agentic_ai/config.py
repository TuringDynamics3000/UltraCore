import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY', 'your_key_here'))

AI_CONFIG = {
    'model': 'gpt-4-turbo-preview',
    'max_tokens': 4096,
    'temperature': 0.7
}
