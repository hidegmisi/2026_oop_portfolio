from __future__ import annotations

from .models import Project


def strip_parens_url(text: str) -> str:
    if " (" in text and text.rstrip().endswith(")"):
        return text.split(" (", 1)[0].strip()
    return text


def format_project_meta_line(project: Project, *, show_time_period: bool = True) -> str:
    bits: list[str] = []
    if show_time_period and project.time_period:
        bits.append(project.time_period)
    if project.publish_date:
        bits.append(project.publish_date.strftime("%Y-%m-%d"))
    return " • ".join(bits)
