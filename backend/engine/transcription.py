"""Voice transcription using faster-whisper (local, no API needed)."""

import os
import tempfile

# Lazy load model (loads on first use)
_model = None


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel('small', device='cpu', compute_type='int8')
    return _model


def transcribe_audio(audio_bytes: bytes, filename: str = 'audio.ogg') -> dict:
    """Transcribe audio bytes to text.

    Args:
        audio_bytes: Raw audio data (ogg, mp3, wav, m4a, etc.)
        filename: Original filename (for format detection)

    Returns:
        dict with 'text', 'language', 'duration'
    """
    import tempfile

    # Write to temp file
    suffix = os.path.splitext(filename)[1] or '.ogg'
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name

    try:
        model = _get_model()
        segments, info = model.transcribe(tmp_path, language=None, beam_size=5)

        text_parts = []
        for segment in segments:
            text_parts.append(segment.text)

        return {
            'text': ''.join(text_parts).strip(),
            'language': info.language,
            'language_probability': round(info.language_probability, 2),
            'duration': round(info.duration, 1),
        }
    finally:
        os.unlink(tmp_path)


def transcribe_file(file_path: str) -> dict:
    """Transcribe an audio file from disk."""
    with open(file_path, 'rb') as f:
        return transcribe_audio(f.read(), os.path.basename(file_path))
