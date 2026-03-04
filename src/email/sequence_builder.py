"""
Email sequence builder — renders Jinja2 templates with venue-specific tokens.

Personalization tokens available in all templates:
  {{ contact_name }}         — "Sarah" or "Hello" if unknown
  {{ venue_name }}           — display name of venue
  {{ city }}                 — city name
  {{ state }}                — state abbreviation
  {{ seating_capacity_tier }}— "Small (100-199 seats)" | "Mid (200-299 seats)" | "Large (300-400 seats)"
  {{ programming_focus }}    — e.g. "family programming" | "educational series"
  {{ mission_excerpt }}      — short phrase from venue's mission (optional)
  {{ sender_name }}          — "Zachary Gartrell"
  {{ show_name }}            — "Princess Peigh's Sword Fighting Tea Party"
  {{ reply_to_email }}       — reply-to address
  {{ physical_address }}     — mailing address (CAN-SPAM required)
  {{ unsubscribe_url }}      — unsubscribe link (CAN-SPAM required)
  {{ next_season }}          — e.g. "Spring 2027"

Usage:
    from src.email.sequence_builder import SequenceBuilder
    builder = SequenceBuilder("templates/email")
    subject, body = builder.render(step=1, context={...})
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound

STEP_TEMPLATES = {
    1: "initial_outreach.j2",
    2: "followup_1.j2",
    3: "followup_2.j2",
    4: "breakup.j2",
}

DEFAULT_CONTEXT: dict[str, Any] = {
    "sender_name": "Zachary Gartrell",
    "show_name": "Princess Peigh's Sword Fighting Tea Party",
    "physical_address": "# Replace with mailing address",
    "unsubscribe_url": "# Replace with unsubscribe URL",
    "reply_to_email": "# Replace with reply-to email",
}


def _capacity_tier_label(tier: str | None) -> str:
    labels = {
        "Small": "Small (100-199 seats)",
        "Mid": "Mid (200-299 seats)",
        "Large": "Large (300-400 seats)",
    }
    return labels.get(tier or "", "community") if tier else "community"


class SequenceBuilder:
    """Renders email sequence steps using Jinja2 templates."""

    def __init__(self, templates_dir: str | Path = "templates/email"):
        self.templates_dir = Path(templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            undefined=StrictUndefined,    # raise on undefined tokens
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, step: int, context: dict[str, Any]) -> tuple[str, str]:
        """
        Render a sequence step.

        Args:
            step: 1-4
            context: venue/contact personalization data

        Returns:
            (rendered_subject, rendered_body) tuple
        """
        if step not in STEP_TEMPLATES:
            raise ValueError(f"Invalid step: {step}. Must be 1-4.")

        template_name = STEP_TEMPLATES[step]
        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound as e:
            raise FileNotFoundError(
                f"Template not found: {self.templates_dir / template_name}"
            ) from e

        # Merge defaults with caller-supplied context
        full_context = {**DEFAULT_CONTEXT, **context}

        # Normalize capacity tier label
        full_context["seating_capacity_tier"] = _capacity_tier_label(
            full_context.get("seating_capacity_tier")
        )

        # Render subject (first line of template) and body (rest)
        rendered = template.render(**full_context)
        lines = rendered.split("\n", 1)
        subject = lines[0].strip().removeprefix("SUBJECT:").strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        return subject, body

    def render_all(self, context: dict[str, Any]) -> list[dict[str, str]]:
        """Render all 4 steps. Returns list of {step, subject, body} dicts."""
        results = []
        for step in range(1, 5):
            subject, body = self.render(step, context)
            results.append({"step": step, "subject": subject, "body": body})
        return results

    def check_tokens(self, step: int, context: dict[str, Any]) -> list[str]:
        """
        Dry-run render — returns list of missing token errors without raising.
        Use for pre-send QA.
        """
        errors = []
        try:
            self.render(step, context)
        except Exception as e:
            errors.append(str(e))
        return errors
