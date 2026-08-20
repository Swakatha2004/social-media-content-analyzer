import re


def clean_ocr_text(text: str) -> str:
    """
    Removes common OCR noise while keeping useful social-media text.
    """

    # Remove common OCR symbols appearing before the actual text
    text = re.sub(r"^[^A-Za-z0-9#@]+", "", text.strip())

    # Collapse excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def analyze_content(text: str) -> dict:
    """
    Lightweight rule-based social media engagement analyzer.
    No external API or LLM required.
    """

    clean_text = clean_ocr_text(text)
    lower_text = clean_text.lower()

    words = clean_text.split()
    word_count = len(words)

    suggestions = []
    strengths = []

    # =================================================
    # 1. CONTENT LENGTH
    # =================================================

    if word_count == 0:

        suggestions.append(
            "Add some content before analyzing the post."
        )

    elif word_count < 10:

        suggestions.append(
            "Consider adding more context so the audience understands the post."
        )

    elif word_count <= 80:

        strengths.append(
            "The post has a concise length."
        )

    else:

        suggestions.append(
            "Consider shortening the post to make it easier to read."
        )

    # =================================================
    # 2. CALL TO ACTION
    # =================================================

    cta_patterns = [
        r"\bbuy\b",
        r"\bshop\b",
        r"\bsubscribe\b",
        r"\bfollow\b",
        r"\bclick\b",
        r"\blearn more\b",
        r"\bvisit\b",
        r"\bdownload\b",
        r"\btry\b",
        r"\bjoin\b",
        r"\bshare\b",
        r"\bcomment\b",
        r"\bsign up\b",
        r"\border\b",
        r"\bget yours\b",
    ]

    has_cta = any(
        re.search(pattern, lower_text)
        for pattern in cta_patterns
    )

    if has_cta:

        strengths.append(
            "The post contains a call-to-action."
        )

    else:

        suggestions.append(
            "Add a clear call-to-action such as "
            "'Learn more', 'Shop now', or 'Comment below'."
        )

    # =================================================
    # 3. AUDIENCE INTERACTION
    # =================================================

    interaction_patterns = [
        r"\?",
        r"\btell us\b",
        r"\blet us know\b",
        r"\bwhat do you think\b",
        r"\bshare your thoughts\b",
        r"\bwhich one\b",
        r"\bwhich do you prefer\b",
        r"\bchoose your favorite\b",
        r"\byour favorite\b",
        r"\bcomment below\b",
    ]

    has_interaction = any(
        re.search(pattern, lower_text)
        for pattern in interaction_patterns
    )

    if has_interaction:

        strengths.append(
            "The post encourages audience interaction."
        )

    else:

        suggestions.append(
            "Consider asking a question to encourage comments and interaction."
        )

    # =================================================
    # 4. HASHTAGS
    # =================================================

    hashtags = re.findall(
        r"#\w+",
        clean_text
    )

    if hashtags:

        strengths.append(
            f"The post uses {len(hashtags)} "
            f"hashtag{'s' if len(hashtags) != 1 else ''}."
        )

    else:

        suggestions.append(
            "Consider adding relevant hashtags to improve discoverability."
        )

    # =================================================
    # 5. OPENING HOOK
    # =================================================

    # Take first meaningful sentence
    first_sentence = re.split(
        r"[.!?\n]",
        clean_text
    )[0].strip()

    first_sentence_lower = first_sentence.lower()

    hook_patterns = [
        r"^new\b",
        r"^discover\b",
        r"^introducing\b",
        r"^breaking\b",
        r"^important\b",
        r"^exclusive\b",
        r"^limited\b",
        r"^how\b",
        r"^why\b",
        r"^what\b",
        r"^don't\b",
        r"^did you know\b",
        r"^save\b",
        r"^meet\b",
        r"^finally\b",
        r"^just launched\b",
    ]

    has_hook = any(
        re.search(pattern, first_sentence_lower)
        for pattern in hook_patterns
    )

    if has_hook:

        strengths.append(
            "The opening contains a strong hook."
        )

    else:

        suggestions.append(
            "Start with a stronger hook to capture attention in the first line."
        )

    # =================================================
    # 6. EMOJI USAGE
    # =================================================

    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001F5FF"
        "\U0001F600-\U0001F64F"
        "\U0001F680-\U0001F6FF"
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FAFF"
        "]+"
    )

    emojis = emoji_pattern.findall(clean_text)

    if emojis:

        strengths.append(
            "The post uses visual elements such as emojis."
        )

    else:

        suggestions.append(
            "Consider using a small number of relevant emojis where appropriate."
        )

    # =================================================
    # 7. SCORE
    # =================================================

    total_checks = 6

    passed_checks = (
        int(10 <= word_count <= 80)
        + int(has_cta)
        + int(has_interaction)
        + int(bool(hashtags))
        + int(has_hook)
        + int(bool(emojis))
    )

    score = round(
        (passed_checks / total_checks) * 100
    )

    # =================================================
    # FINAL RESPONSE
    # =================================================

    return {
        "score": score,
        "word_count": word_count,
        "has_cta": has_cta,
        "has_question": has_interaction,
        "has_hashtags": bool(hashtags),
        "has_hook": has_hook,
        "has_emoji": bool(emojis),
        "strengths": strengths,
        "suggestions": suggestions,
    }