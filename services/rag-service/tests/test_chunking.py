from app.infrastructure.chunking import chunk_text


def test_chunk_text_normalizes_whitespace_and_preserves_content() -> None:
    text = "First sentence.  Second sentence!\nThird sentence?"

    chunks = chunk_text(text, chunk_size=25, overlap=5)

    assert chunks
    assert " ".join(chunks).replace("  ", " ").startswith("First sentence.")
    assert all(len(chunk) <= 25 for chunk in chunks)


def test_chunk_text_empty_input_returns_no_chunks() -> None:
    assert chunk_text(" \n\t ", chunk_size=20, overlap=4) == []


def test_chunk_text_long_input_makes_forward_progress() -> None:
    text = "word " * 100

    chunks = chunk_text(text, chunk_size=40, overlap=10)

    assert len(chunks) > 1
    assert all(len(chunk) <= 40 for chunk in chunks)
