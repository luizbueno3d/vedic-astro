"""AI Provider Manager — supports multiple LLM providers.

Providers:
- OpenAI (GPT-4o, GPT-4o-mini, etc.)
- ChatGPT OAuth Proxy (local community proxy using ChatGPT/Codex auth)
- Anthropic (Claude Sonnet, Haiku, etc.)
- MiniMax (M2.7)
- Groq (Llama 3, Mixtral — free tier)
- OpenRouter (access to 100+ models)
- Ollama (local models)
- Custom (any OpenAI-compatible endpoint)
"""

import json
import os
import random
import time
import requests
from pathlib import Path
from dataclasses import dataclass, asdict

try:
    from data.database import load_user_ai_settings, save_user_ai_settings
except ImportError:
    from ..data.database import load_user_ai_settings, save_user_ai_settings

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


class ProviderMessageError(Exception):
    """Friendly provider error already formatted for the UI."""


# Default provider configs
DEFAULT_PROVIDERS = {
    'openai': AIProvider(
        name='openai',
        label='OpenAI',
        api_key='',
        model='gpt-4o-mini',
        base_url='https://api.openai.com/v1',
        enabled=False,
        max_tokens=8000,
        temperature=0.7,
    ),
    'openai_oauth': AIProvider(
        name='openai_oauth',
        label='ChatGPT OAuth (Local)',
        api_key='',
        model='gpt-5.4',
        base_url='http://127.0.0.1:10531/v1',
        enabled=False,
        max_tokens=8000,
        temperature=0.7,
    ),
    'anthropic': AIProvider(
        name='anthropic',
        label='Anthropic (Claude)',
        api_key='',
        model='claude-sonnet-4-20250514',
        base_url='https://api.anthropic.com/v1',
        enabled=False,
        max_tokens=8000,
        temperature=0.7,
    ),
    'minimax': AIProvider(
        name='minimax',
        label='MiniMax',
        api_key='',
        model='MiniMax-M2.5',
        base_url='https://api.minimax.io',
        enabled=False,
        max_tokens=8000,
        temperature=0.7,
    ),
    'groq': AIProvider(
        name='groq',
        label='Groq (Free)',
        api_key='',
        model='llama-3.3-70b-versatile',
        base_url='https://api.groq.com/openai/v1',
        enabled=False,
        max_tokens=8000,
        temperature=0.7,
    ),
    'openrouter': AIProvider(
        name='openrouter',
        label='OpenRouter',
        api_key='',
        model='meta-llama/llama-3.1-70b-instruct',
        base_url='https://openrouter.ai/api/v1',
        enabled=False,
        max_tokens=8000,
        temperature=0.7,
    ),
    'ollama': AIProvider(
        name='ollama',
        label='Ollama (Local)',
        api_key='',
        model='llama3.1',
        base_url='http://localhost:11434/v1',
        enabled=False,
        max_tokens=8000,
        temperature=0.7,
    ),
}

# Models available per provider
PROVIDER_MODELS = {
    'openai': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    'openai_oauth': ['gpt-5.4', 'gpt-5.4-mini', 'gpt-5.3-codex', 'gpt-4o', 'gpt-4o-mini'],
    'anthropic': ['claude-sonnet-4-20250514', 'claude-haiku-3.5-20241022', 'claude-opus-4-20250514'],
    'minimax': ['MiniMax-M2.5', 'MiniMax-M2.5-highspeed', 'MiniMax-M2.7', 'MiniMax-M2.7-highspeed', 'M2-her'],
    'groq': ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'mixtral-8x7b-32768', 'gemma2-9b-it'],
    'openrouter': [
        'google/gemma-4-31b-it:free',
        'qwen/qwen3.6-plus:free',
        'meta-llama/llama-3.1-70b-instruct',
        'meta-llama/llama-3.1-8b-instruct',
        'google/gemma-2-9b-it',
        'mistralai/mixtral-8x7b-instruct',
        'openai/gpt-4o-mini',
    ],
    'ollama': ['llama3.1', 'llama3.2', 'mistral', 'qwen2.5', 'phi3', 'gemma2'],
}

OPENROUTER_FALLBACK_MODELS = [
    'google/gemma-4-31b-it:free',
    'qwen/qwen3.6-plus:free',
]


def load_config(owner_email: str | None = None) -> dict:
    """Load AI provider configuration."""
    if owner_email:
        data = load_user_ai_settings(owner_email)
        if data:
            result = {k: v for k, v in DEFAULT_PROVIDERS.items()}
            for k, v in data.items():
                if isinstance(v, dict):
                    result[k] = AIProvider(**v)
                else:
                    result[k] = v
            _upgrade_provider_limits(result)
            return result

    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            data = json.load(f)
            # Convert dicts back to AIProvider objects
            result = {k: v for k, v in DEFAULT_PROVIDERS.items()}
            for k, v in data.items():
                if isinstance(v, dict):
                    result[k] = AIProvider(**v)
                else:
                    result[k] = v
            _upgrade_provider_limits(result)
            return result
    result = {k: v for k, v in DEFAULT_PROVIDERS.items()}
    _upgrade_provider_limits(result)
    return result


def _upgrade_provider_limits(config: dict):
    """Raise stale low output limits from older configs."""
    for provider in config.values():
        if not isinstance(provider, AIProvider):
            continue
        if provider.max_tokens < 8000:
            provider.max_tokens = 8000


def save_config(config: dict, owner_email: str | None = None):
    """Save AI provider configuration."""
    data = {}
    for k, v in config.items():
        if isinstance(v, AIProvider):
            data[k] = asdict(v)
        else:
            data[k] = v

    if owner_email:
        save_user_ai_settings(owner_email, data)
        return

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=2)


def get_active_provider(owner_email: str | None = None) -> AIProvider | None:
    """Get the currently active (enabled) provider."""
    config = load_config(owner_email)
    for provider in config.values():
        if isinstance(provider, AIProvider) and provider.enabled:
            return provider
    return None


def update_provider(name: str, owner_email: str | None = None, **kwargs):
    """Update a provider's settings."""
    config = load_config(owner_email)
    if name in config and isinstance(config[name], AIProvider):
        for key, value in kwargs.items():
            if hasattr(config[name], key):
                setattr(config[name], key, value)
        save_config(config, owner_email)


def generate_reading(system_prompt: str, user_prompt: str, owner_email: str | None = None) -> str:
    """Generate a reading using the active AI provider.

    Args:
        system_prompt: System instruction
        user_prompt: User message with chart data

    Returns:
        Generated reading text
    """
    provider = get_active_provider(owner_email)

    if not provider:
        return _no_provider_message()

    try:
        if provider.name == 'anthropic':
            return _call_anthropic(provider, system_prompt, user_prompt)
        elif provider.name == 'minimax':
            return _call_minimax(provider, system_prompt, user_prompt)
        elif provider.name in ('openai', 'openai_oauth', 'groq', 'openrouter', 'ollama', 'minimax'):
            return _call_openai_compatible(provider, system_prompt, user_prompt)
        else:
            return _call_openai_compatible(provider, system_prompt, user_prompt)
    except ProviderMessageError as e:
        return str(e)
    except requests.HTTPError as e:
        return _format_http_error(provider, e)
    except Exception as e:
        return f"Error with {provider.label}: {str(e)}\n\nCheck your API key and try again."


def _format_http_error(provider: AIProvider, error: requests.HTTPError) -> str:
    status = error.response.status_code if error.response is not None else None
    body = ''
    if error.response is not None:
        try:
            body = error.response.text[:500]
        except Exception:
            body = ''

    if status == 429:
        return (
            f"Error with {provider.label}: Rate limited (429).\n\n"
            f"This usually means the model or free tier is temporarily overloaded, not that your API key is wrong. "
            f"Wait a bit and try again, or switch to a non-free / less crowded model."
        )

    if status == 401:
        return f"Error with {provider.label}: Authentication failed (401). Check your API key."

    if status == 402:
        return f"Error with {provider.label}: Payment or quota required (402)."

    if status == 403:
        return f"Error with {provider.label}: Access forbidden (403). Model access may be restricted for this account."

    return f"Error with {provider.label}: HTTP {status}.\n\n{body or str(error)}"


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
    if provider.api_key:
        headers['Authorization'] = f'Bearer {provider.api_key}'

    # OpenRouter needs extra headers
    if provider.name == 'openrouter':
        headers['HTTP-Referer'] = 'https://vedic-astro.app'
        headers['X-Title'] = 'Vedic Astro'

    url = f'{provider.base_url}/chat/completions'

    models_to_try = [provider.model]
    if provider.name == 'openrouter' and provider.model.endswith(':free'):
        models_to_try.extend([m for m in OPENROUTER_FALLBACK_MODELS if m != provider.model])

    attempts_log = []
    last_error = None
    for model_name in models_to_try:
        payload = {
            'model': model_name,
            'max_tokens': provider.max_tokens,
            'temperature': provider.temperature,
            'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user},
            ],
        }
        for attempt in range(1, 4):
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            if resp.status_code != 429:
                resp.raise_for_status()
                data = resp.json()
                result = data['choices'][0]['message']['content']
                import re
                result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
                return result

            attempts_log.append(f'{model_name} attempt {attempt}')
            last_error = requests.HTTPError(response=resp)
            if attempt < 3:
                time.sleep((1.5 * (2 ** (attempt - 1))) + random.uniform(0.2, 0.9))

    if last_error is not None:
        tried = ', '.join(attempts_log) if attempts_log else provider.model
        raise ProviderMessageError(
            f'Error with {provider.label}: Rate limited (429).\n\n'
            f'Tried {tried}. Free models are likely overloaded right now. '
            f'Wait a bit and try again, or switch to a less crowded / paid model.'
        )

    raise ProviderMessageError(f'Error with {provider.label}: No model could be tried.')


def _call_minimax(provider: AIProvider, system: str, user: str) -> str:
    if provider.model == 'M2-her':
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {provider.api_key}',
        }
        payload = {
            'model': provider.model,
            'temperature': provider.temperature,
            'max_completion_tokens': min(provider.max_tokens, 2048),
            'messages': [
                {'role': 'system', 'name': 'Vedic Astro', 'content': system},
                {'role': 'user', 'name': 'User', 'content': user},
            ],
        }
        data = _post_with_429_retry(
            f'{provider.base_url}/v1/text/chatcompletion_v2',
            headers=headers,
            payload=payload,
            provider_label=provider.label,
            model_label=provider.model,
        )
        return data['choices'][0]['message']['content'].strip()

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': provider.api_key,
        'anthropic-version': '2023-06-01',
    }
    payload = {
        'model': provider.model,
        'max_tokens': min(provider.max_tokens, 4096),
        'temperature': max(0.01, min(provider.temperature, 1.0)),
        'system': system,
        'messages': [
            {'role': 'user', 'content': user},
        ],
    }
    data = _post_with_429_retry(
        f'{provider.base_url}/anthropic/v1/messages',
        headers=headers,
        payload=payload,
        provider_label=provider.label,
        model_label=provider.model,
    )
    parts = []
    for item in data.get('content', []):
        if item.get('type') == 'text':
            parts.append(item.get('text', ''))
    return '\n'.join(part for part in parts if part).strip()


def _post_with_429_retry(url: str, headers: dict, payload: dict, provider_label: str, model_label: str) -> dict:
    last_error = None
    for attempt in range(1, 4):
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        if resp.status_code != 429:
            resp.raise_for_status()
            return resp.json()
        last_error = requests.HTTPError(response=resp)
        if attempt < 3:
            time.sleep((1.5 * (2 ** (attempt - 1))) + random.uniform(0.2, 0.9))

    if last_error is not None:
        raise ProviderMessageError(
            f'Error with {provider_label}: Rate limited (429).\n\n'
            f'Tried {model_label} 3 times with backoff. The provider is likely overloaded right now. '
            f'Wait a bit and try again.'
        )
    raise ProviderMessageError(f'Error with {provider_label}: Request failed before retry handling could complete.')


def test_provider(name: str, owner_email: str | None = None) -> dict:
    """Test if a provider is working.

    Returns:
        dict with 'success', 'message', 'model' keys
    """
    config = load_config(owner_email)
    if name not in config:
        return {'success': False, 'message': f'Provider {name} not found'}

    provider = config[name]
    if not provider.api_key and name not in ('ollama', 'openai_oauth'):
        return {'success': False, 'message': 'No API key set'}

    try:
        result = generate_reading(
            'You are a helpful assistant. Reply with exactly: "Connection successful!"',
            'Test connection. Reply with: Connection successful!',
            owner_email,
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
