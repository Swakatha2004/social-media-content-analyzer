import os
import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash-lite:generateContent"
)


def build_prompt(text: str) -> str:
    return f"""
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


def improve_caption(text: str) -> str:
    prompt = build_prompt(text)

    # -----------------------------------------
    # RENDER / PRODUCTION
    # -----------------------------------------
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if gemini_api_key:
        try:
            response = requests.post(
                GEMINI_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": gemini_api_key,
                },
                json={
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2
                    }
                },
                timeout=60,
            )

            response.raise_for_status()

            data = response.json()

            candidates = data.get("candidates", [])

            if not candidates:
                raise RuntimeError(
                    "Gemini returned no candidates."
                )

            parts = candidates[0].get("content", {}).get("parts", [])

            improved = "".join(
                part.get("text", "")
                for part in parts
            ).strip()

            if not improved:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return improved

        except requests.exceptions.Timeout:
            raise RuntimeError(
                "The production LLM took too long to respond."
            )

        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Production LLM request failed: {str(e)}"
            )

    # -----------------------------------------
    # LOCAL DEVELOPMENT
    # -----------------------------------------
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2
                },
            },
            timeout=60,
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