from __future__ import annotations
from typing import Iterator
import tiktoken

# Use cl100k_base as a universal conservative approximation
ENCODER = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(ENCODER.encode(text))


def chunk_text(text: str, max_tokens: int = 4000) -> Iterator[str]:
    """
    Semantic chunker.
    Splits on double newlines (paragraphs), then single newlines, then spaces,
    falling back to raw token boundaries if necessary.
    Yields chunks up to max_tokens in size.
    """
    if not text:
        return

    if count_tokens(text) <= max_tokens:
        yield text
        return

    # Semantic split boundaries in order of preference
    separators = ["\n\n", "\n", " ", ""]

    def _split_recursively(text_segment: str, depth: int = 0) -> Iterator[str]:
        if not text_segment:
            return

        if count_tokens(text_segment) <= max_tokens:
            yield text_segment
            return

        if depth >= len(separators):
            # Fallback: slice by tokens directly
            tokens = ENCODER.encode(text_segment)
            for i in range(0, len(tokens), max_tokens):
                yield ENCODER.decode(tokens[i : i + max_tokens])
            return

        sep = separators[depth]
        if sep == "":
            splits = list(text_segment)
        else:
            splits = text_segment.split(sep)

        current_chunk = ""
        current_tokens = 0

        for part in splits:
            part_str = part + sep if sep else part
            part_tokens = count_tokens(part_str)

            if current_tokens + part_tokens > max_tokens and current_chunk:
                yield current_chunk.strip()
                current_chunk = ""
                current_tokens = 0

            if part_tokens > max_tokens:
                # Part itself is too big, go deeper
                yield from _split_recursively(part, depth + 1)
            else:
                current_chunk += part_str
                current_tokens += part_tokens

        if current_chunk:
            yield current_chunk.strip()

    yield from _split_recursively(text)
