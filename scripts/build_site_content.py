from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from portfolio_content.renderers import (  # noqa: E402
    ProjectDetailPageRenderer,
    ProjectsPageRenderer,
)
from portfolio_content.repository import ProjectRepository, ProjectRepositoryProtocol  # noqa: E402
from portfolio_content.specs import (  # noqa: E402
    CardDisplayOptions,
    ProjectsPageRenderSpec,
    TagsPanelOptions,
)


@dataclass(frozen=True)
class BuildPaths:
    repo_root: str

    @property
    def projects_csv(self) -> str:
        return os.path.join(self.repo_root, "data", "projects.csv")

    @property
    def generated_projects_qmd(self) -> str:
        return os.path.join(self.repo_root, "projects", "_generated_projects.qmd")

    @property
    def generated_pinned_projects_qmd(self) -> str:
        return os.path.join(self.repo_root, "projects", "_generated_pinned_projects.qmd")

    @property
    def project_pages_dir(self) -> str:
        return os.path.join(self.repo_root, "projects")

    @property
    def project_bodies_dir(self) -> str:
        return os.path.join(self.repo_root, "projects", "bodies")


def _write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


class SiteContentBuilder:
    def __init__(self, paths: BuildPaths, repository: ProjectRepositoryProtocol | None = None):
        self.paths = paths
        self.repository = repository or ProjectRepository(paths.projects_csv)

    @staticmethod
    def _generated_header() -> str:
        return "\n".join(
            [
                "<!--",
                "THIS FILE IS GENERATED.",
                "Run: python scripts/build_site_content.py",
                "-->",
                "",
            ]
        )

    def build_projects_partial(self) -> None:
        generator = ProjectsPartialGenerator(self.paths, self.repository, self._generated_header())
        generator.build()

    def build_pinned_projects_partial(self) -> None:
        generator = PinnedProjectsGenerator(self.paths, self.repository, self._generated_header())
        generator.build()

    def build_project_pages(self) -> None:
        generator = ProjectDetailPagesGenerator(self.paths, self.repository)
        generator.build()

    def build_all(self) -> None:
        self.build_projects_partial()
        self.build_pinned_projects_partial()
        self.build_project_pages()


@dataclass(frozen=True)
class ProjectsPartialGenerator:
    paths: BuildPaths
    repository: ProjectRepositoryProtocol
    generated_header: str

    def build(self) -> None:
        projects = self.repository.sorted(self.repository.load_published())
        renderer = ProjectsPageRenderer(
            ProjectsPageRenderSpec(
                link_prefix="",
                asset_prefix="../",
                card_display=CardDisplayOptions(show_featured=False),
                tags_panel=TagsPanelOptions(show_panel=True),
            )
        )
        body = renderer.render(projects)
        _write_text(self.paths.generated_projects_qmd, self.generated_header + body)


@dataclass(frozen=True)
class PinnedProjectsGenerator:
    paths: BuildPaths
    repository: ProjectRepositoryProtocol
    generated_header: str

    def build(self) -> None:
        published = self.repository.load_published()
        pinned = self.repository.sorted(self.repository.pinned(published))
        renderer = ProjectsPageRenderer(
            ProjectsPageRenderSpec(
                link_prefix="projects",
                asset_prefix="",
                card_display=CardDisplayOptions(
                    show_featured=True,
                    featured_stack=True,
                    show_pinned_status=False,
                ),
                tags_panel=TagsPanelOptions(show_panel=False),
            )
        )
        body = renderer.render(pinned)
        _write_text(self.paths.generated_pinned_projects_qmd, self.generated_header + body)


@dataclass(frozen=True)
class ProjectDetailPagesGenerator:
    paths: BuildPaths
    repository: ProjectRepositoryProtocol

    def build(self) -> None:
        projects = self.repository.sorted(self.repository.load_published())
        renderer = ProjectDetailPageRenderer()
        for p in projects:
            out_path = os.path.join(self.paths.project_pages_dir, f"{p.slug}.qmd")
            body_path = os.path.join(self.paths.project_bodies_dir, f"{p.slug}.qmd")
            body_include = f"bodies/{p.slug}.qmd" if os.path.exists(body_path) else None
            _write_text(out_path, renderer.render(p, body_include=body_include))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Quarto content from structured data.")
    parser.add_argument(
        "--repo-root",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        help="Path to repository root (default: inferred).",
    )
    args = parser.parse_args()

    paths = BuildPaths(repo_root=os.path.abspath(args.repo_root))
    SiteContentBuilder(paths).build_all()


if __name__ == "__main__":
    main()

