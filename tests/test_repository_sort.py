from __future__ import annotations

from datetime import date

from portfolio_content.models import Project
from portfolio_content.repository import DateOnlySorter, ProjectRepository, ProjectSortSpec


def _project(
    *,
    title: str,
    pinned: bool,
    publish_date: date | None,
) -> Project:
    return Project(
        title=title,
        slug=title.lower().replace(" ", "-"),
        link="https://example.com",
        excerpt="",
        org_for="",
        tags=[],
        pinned=pinned,
        published=True,
        publish_date=publish_date,
        time_period="",
        thumbnail_path=None,
    )


def test_sorted_prioritizes_pinned_then_newest_then_title() -> None:
    repo = ProjectRepository("unused.csv")
    projects = [
        _project(title="beta", pinned=False, publish_date=date(2025, 1, 1)),
        _project(title="Alpha", pinned=True, publish_date=date(2024, 1, 1)),
        _project(title="Gamma", pinned=True, publish_date=date(2026, 1, 1)),
        _project(title="aardvark", pinned=False, publish_date=date(2025, 1, 1)),
    ]

    sorted_projects = repo.sorted(projects)
    assert [p.title for p in sorted_projects] == ["Gamma", "Alpha", "aardvark", "beta"]


def test_sorted_supports_oldest_first_when_configured() -> None:
    repo = ProjectRepository("unused.csv")
    projects = [
        _project(title="Second", pinned=False, publish_date=date(2025, 1, 1)),
        _project(title="First", pinned=False, publish_date=date(2024, 1, 1)),
    ]

    sorted_projects = repo.sorted(projects, spec=ProjectSortSpec(pinned_first=True, newest_first=False))
    assert [p.title for p in sorted_projects] == ["First", "Second"]


def test_sorted_supports_sorter_strategy_override() -> None:
    repo = ProjectRepository("unused.csv")
    projects = [
        _project(title="PinnedOld", pinned=True, publish_date=date(2024, 1, 1)),
        _project(title="UnpinnedNew", pinned=False, publish_date=date(2026, 1, 1)),
    ]
    sorted_projects = repo.sorted(projects, sorter=DateOnlySorter())
    assert [p.title for p in sorted_projects] == ["UnpinnedNew", "PinnedOld"]
