"""Prompt templates for different summary modes."""

from __future__ import annotations

from app.domain.entities.summary import SummaryMode

# Human-readable language names used inside the system prompt.
# ``auto`` means "echo the source transcript's language".
_LANG_NAMES: dict[str, str] = {
    "ru": "Russian",
    "en": "English",
    "pl": "Polish",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "uk": "Ukrainian",
    "auto": "the same language as the transcript",
}

_MODE_INSTRUCTIONS: dict[SummaryMode, str] = {
    SummaryMode.SUMMARY: (
        "Write a concise summary (5-8 sentences) capturing the key ideas of the video."
    ),
    SummaryMode.BULLETS: (
        "Produce a structured bullet list of the main points. Use short, information-dense bullets."
    ),
    SummaryMode.DETAILED: (
        "Write a detailed, sectioned breakdown with headings, covering all important "
        "topics, examples, and conclusions from the video."
    ),
    SummaryMode.QA: (
        "Generate a Q&A digest: 5-10 question/answer pairs covering the most important "
        "information from the video."
    ),
}


def _language_name(lang: str) -> str:
    """Return a human-readable language name, falling back to the raw code."""
    return _LANG_NAMES.get(lang, lang)


def build_system_prompt(mode: SummaryMode, lang: str) -> str:
    """Build the system prompt.

    The prompt explicitly instructs the model to **translate** when the
    transcript is in a different language than the requested output. This
    matters for videos whose YouTube captions are not auto-translatable.
    """
    target_language = _language_name(lang)
    instruction = _MODE_INSTRUCTIONS[mode]
    return (
        f"Summarize this YouTube transcript in {target_language}. "
        f"Translate if needed. {instruction} "
        "Be factual. Preserve proper nouns."
    )


def build_user_prompt(
    transcript_text: str,
    custom_prompt: str | None,
    *,
    transcript_language: str | None = None,
) -> str:
    """Build the user prompt.

    Including the transcript language helps the LLM disambiguate edge cases
    (e.g. mixed-language captions) and produce higher-fidelity translations.
    """
    header = "Transcript:"
    if transcript_language:
        header = f"Transcript (source language: {_language_name(transcript_language)}):"

    base = f'{header}\n"""\n{transcript_text}\n"""'
    if custom_prompt:
        return f"{base}\n\nUser request: {custom_prompt.strip()}"
    return base
