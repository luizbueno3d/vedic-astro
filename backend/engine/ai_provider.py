"""AI Provider Manager — supports multiple LLM providers.

Providers:
- OpenAI (GPT-4o, GPT-4o-mini, etc.)
- Anthropic (Claude Sonnet, Haiku, etc.)
- MiniMax (M2.7)
- Groq (Llama 3, Mixtral — free tier)
- OpenRouter (access to 100+ models)
- Ollama (local models)
- Custom (any OpenAI-compatible endpoint)
"""

import json
import os
import requests
from pathlib import Path
from dataclasses import dataclass, asdict

CONFIG_PATH = Path(__file__).parent.parent / 'data' / 'ai_config.json'


@dataclass
class AIProvider:
    name: str           # 'openai', 'anthropic', 'minimax', 'groq', 'openrouter', 'ollama', 'custom'
    label: str          # Display name
    api_key: str        # API key (encrypted or plain)
    model: str          # Model name
    base_url: str       # API base URL
    enabled: bool       # Is this provider active?
    max_tokens: int     # Max tokens for response
    temperature: float  # Creativity (0-1)


# Default provider configs
DEFAULT_PROVIDERS = {
    'openai': AIProvider(
        name='openai',
        label='OpenAI',
        api_key='',
        model='gpt-4o-mini',
        base_url='https://api.openai.com/v1',
        enabled=False,
        max_tokens=4000,
        temperature=0.7,
    ),
    'anthropic': AIProvider(
        name='anthropic',
        label='Anthropic (Claude)',
        api_key='',
        model='claude-sonnet-4-20250514',
        base_url='https://api.anthropic.com/v1',
        enabled=False,
        max_tokens=4000,
        temperature=0.7,
    ),
    'minimax': AIProvider(
        name='minimax',
        label='MiniMax',
        api_key='',
        model='MiniMax-M2.5',
        base_url='https://api.minimax.chat/v1',
        enabled=False,
        max_tokens=4000,
        temperature=0.7,
    ),
    'groq': AIProvider(
        name='groq',
        label='Groq (Free)',
        api_key='',
        model='llama-3.3-70b-versatile',
        base_url='https://api.groq.com/openai/v1',
        enabled=False,
        max_tokens=4000,
        temperature=0.7,
    ),
    'openrouter': AIProvider(
        name='openrouter',
        label='OpenRouter',
        api_key='',
        model='meta-llama/llama-3.1-70b-instruct',
        base_url='https://openrouter.ai/api/v1',
        enabled=False,
        max_tokens=4000,
        temperature=0.7,
    ),
    'ollama': AIProvider(
        name='ollama',
        label='Ollama (Local)',
        api_key='',
        model='llama3.1',
        base_url='http://localhost:11434/v1',
        enabled=False,
        max_tokens=4000,
        temperature=0.7,
    ),
}

# Models available per provider
PROVIDER_MODELS = {
    'openai': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    'anthropic': ['claude-sonnet-4-20250514', 'claude-haiku-3.5-20241022', 'claude-opus-4-20250514'],
    'minimax': ['MiniMax-M2.5', 'MiniMax-M2.7', 'abab6.5s-chat'],
    'groq': ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768', 'gemma2-9b-it'],
    'openrouter': [
        'meta-llama/llama-3.1-70b-instruct',
        'meta-llama/llama-3.1-8b-instruct',
        'google/gemma-2-9b-it',
        'mistralai/mixtral-8x7b-instruct',
        'openai/gpt-4o-mini',
    ],
    'ollama': ['llama3.1', 'llama3.2', 'mistral', 'qwen2.5', 'phi3', 'gemma2'],
}


def load_config() -> dict:
    """Load AI provider configuration."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            data = json.load(f)
            # Convert dicts back to AIProvider objects
            result = {}
            for k, v in data.items():
                if isinstance(v, dict):
                    result[k] = AIProvider(**v)
                else:
                    result[k] = v
            return result
    return {k: v for k, v in DEFAULT_PROVIDERS.items()}


def save_config(config: dict):
    """Save AI provider configuration."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    for k, v in config.items():
        if isinstance(v, AIProvider):
            data[k] = asdict(v)
        else:
            data[k] = v
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=2)


def get_active_provider() -> AIProvider | None:
    """Get the currently active (enabled) provider."""
    config = load_config()
    for provider in config.values():
        if isinstance(provider, AIProvider) and provider.enabled:
            return provider
    return None


def update_provider(name: str, **kwargs):
    """Update a provider's settings."""
    config = load_config()
    if name in config and isinstance(config[name], AIProvider):
        for key, value in kwargs.items():
            if hasattr(config[name], key):
                setattr(config[name], key, value)
        save_config(config)


def generate_reading(system_prompt: str, user_prompt: str) -> str:
    """Generate a reading using the active AI provider.

    Args:
        system_prompt: System instruction
        user_prompt: User message with chart data

    Returns:
        Generated reading text
    """
    provider = get_active_provider()

    if not provider:
        return _no_provider_message()

    try:
        if provider.name == 'anthropic':
            return _call_anthropic(provider, system_prompt, user_prompt)
        elif provider.name in ('openai', 'groq', 'openrouter', 'ollama', 'minimax'):
            return _call_openai_compatible(provider, system_prompt, user_prompt)
        else:
            return _call_openai_compatible(provider, system_prompt, user_prompt)
    except Exception as e:
        return f"Error with {provider.label}: {str(e)}\n\nCheck your API key and try again."


def _call_anthropic(provider: AIProvider, system: str, user: str) -> str:
    """Call Anthropic API (different format)."""
    try:
        import anthropic
    except ImportError:
        return "Install anthropic package: pip install anthropic"

    client = anthropic.Anthropic(api_key=provider.api_key)
    message = client.messages.create(
        model=provider.model,
        max_tokens=provider.max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    return message.content[0].text


def _call_openai_compatible(provider: AIProvider, system: str, user: str) -> str:
    """Call any OpenAI-compatible API (OpenAI, Groq, OpenRouter, Ollama, MiniMax)."""
    headers = {
        'Content-Type': 'application/json',
    }

    # Auth header varies by provider
    if provider.name == 'minimax':
        headers['Authorization'] = f'Bearer {provider.api_key}'
    elif provider.api_key:
        headers['Authorization'] = f'Bearer {provider.api_key}'

    # OpenRouter needs extra headers
    if provider.name == 'openrouter':
        headers['HTTP-Referer'] = 'https://vedic-astro.app'
        headers['X-Title'] = 'Vedic Astro'

    payload = {
        'model': provider.model,
        'max_tokens': provider.max_tokens,
        'temperature': provider.temperature,
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user},
        ],
    }

    # MiniMax uses slightly different format
    if provider.name == 'minimax':
        payload['model'] = provider.model
        url = f'{provider.base_url}/chat/completions'
    else:
        url = f'{provider.base_url}/chat/completions'

    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    result = data['choices'][0]['message']['content']

    # Clean up: remove <think> tags (some models include reasoning)
    import re
    result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()

    return result


def test_provider(name: str) -> dict:
    """Test if a provider is working.

    Returns:
        dict with 'success', 'message', 'model' keys
    """
    config = load_config()
    if name not in config:
        return {'success': False, 'message': f'Provider {name} not found'}

    provider = config[name]
    if not provider.api_key and name != 'ollama':
        return {'success': False, 'message': 'No API key set'}

    try:
        result = generate_reading(
            'You are a helpful assistant. Reply with exactly: "Connection successful!"',
            'Test connection. Reply with: Connection successful!'
        )
        if 'successful' in result.lower() or 'Connection' in result:
            return {'success': True, 'message': f'{provider.label} connected!', 'model': provider.model}
        else:
            return {'success': True, 'message': f'{provider.label} responded (unexpected format)', 'model': provider.model}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def _no_provider_message() -> str:
    return """No AI provider configured.

To enable AI readings:
1. Go to the AI Interpretations page
2. Choose a provider (Groq is free, OpenRouter has many options)
3. Enter your API key
4. Enable the provider
5. Click "Generate AI Reading"

For free options:
- **Groq**: Sign up at groq.com, get free API key, use llama-3.3-70b
- **Ollama**: Install locally (ollama.ai), no API key needed
- **OpenRouter**: Sign up at openrouter.ai, some free models available"""
