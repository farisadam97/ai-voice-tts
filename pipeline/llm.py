from openai import OpenAI
import re
import config

_client = OpenAI(base_url=config.LM_STUDIO_URL, api_key="lm-studio")


def get_response(user_input: str, history: list | None = None) -> str:
    history = history or []
    messages = [{"role": "system", "content": config.CHARACTER_SYSTEM_PROMPT}]
    messages += history[-10:]
    messages.append({"role": "user", "content": user_input})

    try:
        response = _client.chat.completions.create(
            model=config.LM_STUDIO_MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=60,
        )
    except Exception as e:
        err = str(e).lower()
        if "connection" in err:
            print(
                f"[LLM] Cannot reach LM Studio at {config.LM_STUDIO_URL}. Is it running?"
            )
        else:
            print(f"[LLM] Error: {e}")
        return ""

    content = response.choices[0].message.content
    if not content:
        print("[LLM] Warning: empty response received.")
        return ""
    content = re.sub(r'<think.*?>.*?</think\s*>', '', content, flags=re.DOTALL).strip()
    content = re.sub(r'[\U00010000-\U0010ffff]', '', content).strip()
    content = re.sub(r'\s*—\s*', ', ', content)
    content = re.sub(r'\s*–\s*', ', ', content)
    content = re.sub(r'\s*--\s*', ', ', content)
    return content
