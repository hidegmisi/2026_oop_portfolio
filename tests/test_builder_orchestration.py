from __future__ import annotations

from datetime import date
from pathlib import Path

from portfolio_content.models import Project
from scripts.build_site_content import BuildPaths, SiteContentBuilder


class StubRepository:
    def __init__(self, projects: list[Project]):
        self._projects = projects

    def load(self) -> list[Project]:
        return list(self._projects)

    def load_published(self) -> list[Project]:
        return [p for p in self._projects if p.published]

    def sorted(self, projects, spec=None, sorter=None) -> list[Project]:
        data = list(projects)
        if sorter is not None:
            return sorted(data, key=sorter.key)
        return sorted(data, key=lambda p: p.title.lower())

    def pinned(self, projects) -> list[Project]:
        return [p for p in projects if p.pinned]


def _project(*, title: str, pinned: bool, published: bool) -> Project:
    return Project(
        title=title,
        slug=title.lower().replace(" ", "-"),
        link="https://example.com/project",
        excerpt="",
        org_for="",
        tags=("oop",),
        pinned=pinned,
        published=published,
        publish_date=date(2026, 1, 1),
        time_period="2026",
        thumbnail_path="assets/project_thumbs/demo.png",
    )


def test_site_content_builder_orchestrates_outputs(tmp_path: Path) -> None:
    paths = BuildPaths(repo_root=str(tmp_path))
    (tmp_path / "projects" / "bodies").mkdir(parents=True)

    repo = StubRepository(
        [
            _project(title="Pinned One", pinned=True, published=True),
            _project(title="Hidden Project", pinned=False, published=False),
        ]
    )
    builder = SiteContentBuilder(paths, repository=repo)
    builder.build_all()

    generated_projects = (tmp_path / "projects" / "_generated_projects.qmd").read_text(encoding="utf-8")
    generated_pinned = (tmp_path / "projects" / "_generated_pinned_projects.qmd").read_text(encoding="utf-8")
    project_page = (tmp_path / "projects" / "pinned-one.qmd").read_text(encoding="utf-8")

    assert "THIS FILE IS GENERATED." in generated_projects
    assert "project_card" in generated_projects
    assert "project_card" in generated_pinned
    assert "Hidden Project" not in generated_projects
    assert "Open project" in project_page
