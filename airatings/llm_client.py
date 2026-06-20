import os
import re
from django.conf import settings

# ---------------------------------------------------------------------------
# Provider backends
# Each backend receives (system, user, json_mode) and returns a plain string.
# To add a new provider: write one function here + one branch in _dispatch().
# ---------------------------------------------------------------------------

def _gemini(system: str, user: str, json_mode: bool) -> str:
    from google import genai
    from google.genai import types

    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise RuntimeError('GEMINI_API_KEY is not set')

    model = getattr(settings, 'AI_MODEL', 'gemini-2.0-flash')

    client = genai.Client(api_key=api_key)

    system_text = system
    if json_mode:
        system_text += '\n\nReturn ONLY raw JSON. No markdown fences, no explanation, no trailing text.'

    response = client.models.generate_content(
        model=model,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system_text,
        ),
    )

    return response.text


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def _dispatch(provider: str, system: str, user: str, json_mode: bool) -> str:
    if provider == 'gemini':
        return _gemini(system, user, json_mode)
    raise ValueError(f"Unknown AI_PROVIDER '{provider}'. Supported: gemini")


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def complete(system: str, user: str, json_mode: bool = False) -> str:
    provider = getattr(settings, 'AI_PROVIDER', os.environ.get('AI_PROVIDER', 'gemini')).lower()
    raw = _dispatch(provider, system, user, json_mode)
    if json_mode:
        raw = _strip_json_fences(raw)
    return raw
