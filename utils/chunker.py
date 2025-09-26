def chunk_text(text: str, max_chars: int = 4000):
    for i in range(0, len(text), max_chars):
        yield text[i:i+max_chars]