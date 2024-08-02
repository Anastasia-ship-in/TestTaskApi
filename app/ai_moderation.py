from better_profanity import profanity


def contains_profanity(text: str) -> bool:
    return profanity.contains_profanity(text)
