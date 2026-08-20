import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def improve_caption(text: str) -> str:

    prompt = f"""
You are a professional social media caption editor.

Rewrite the caption below to make it more engaging.

STRICT RULES:
1. Preserve every factual detail from the original.
2. NEVER invent facts, products, features, prices, dates, discounts,
   locations, claims, or events.
3. NEVER add new hashtags.
4. You may improve the hook, wording, structure, readability and CTA.
5. You may add a small number of emojis if appropriate.
6. Keep the original meaning.
7. Keep the caption concise.
8. Return ONLY the rewritten caption.
9. Do not explain your changes.
10. Do not write phrases such as "Here's an improved version".

Original caption:

{text}
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        improved = data.get("response", "").strip()

        if not improved:
            raise RuntimeError(
                "The local LLM returned an empty response."
            )

        return improved

    except requests.exceptions.ConnectionError:

        raise RuntimeError(
            "Ollama is not running. Please start Ollama."
        )

    except requests.exceptions.Timeout:

        raise RuntimeError(
            "The local LLM took too long to respond."
        )

    except requests.exceptions.RequestException as e:

        raise RuntimeError(
            f"LLM request failed: {str(e)}"
        )