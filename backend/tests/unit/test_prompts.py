"""Tests for the prompt builders."""

from __future__ import annotations

from app.application.use_cases.prompts import build_system_prompt, build_user_prompt
from app.domain.entities.summary import SummaryMode


def test_system_prompt_lists_target_language_polish() -> None:
    prompt = build_system_prompt(SummaryMode.SUMMARY, "pl")
    assert "Polish" in prompt
    assert "translate" in prompt.lower()


def test_system_prompt_lists_target_language_russian() -> None:
    prompt = build_system_prompt(SummaryMode.BULLETS, "ru")
    assert "Russian" in prompt
    assert "translate" in prompt.lower()


def test_system_prompt_unknown_lang_falls_back_to_code() -> None:
    prompt = build_system_prompt(SummaryMode.SUMMARY, "xx")
    assert "xx" in prompt


def test_user_prompt_includes_source_language_hint() -> None:
    prompt = build_user_prompt(
        "Cze\u015b\u0107 \u015bwiat",
        custom_prompt=None,
        transcript_language="pl",
    )
    assert "Polish" in prompt
    assert "Cze\u015b\u0107 \u015bwiat" in prompt


def test_user_prompt_omits_language_when_unknown() -> None:
    prompt = build_user_prompt("hello", custom_prompt=None)
    assert prompt.startswith("Transcript:")
    assert "source language" not in prompt


def test_user_prompt_appends_custom_prompt() -> None:
    prompt = build_user_prompt(
        "hello",
        custom_prompt="focus on greetings",
        transcript_language="en",
    )
    assert "focus on greetings" in prompt
    assert "User request:" in prompt
