from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

from .models import Project
from .specs import ProjectsPageRenderSpec
from .text_utils import format_project_meta_line, strip_parens_url


def _project_page_href(slug: str, link_prefix: str) -> str:
    prefix = (link_prefix or "").lstrip("/")
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    return f"{prefix}{slug}.html"


def _thumb_src(thumbnail_path: Optional[str], asset_prefix: str) -> str:
    if not thumbnail_path:
        return ""
    prefix = (asset_prefix or "").lstrip("/")
    return f"{prefix}{thumbnail_path}"


@dataclass(frozen=True)
class ProjectCardVM:
    href: str
    thumb_src: str
    title: str
    meta: str
    org: str
    excerpt: str
    tags: Sequence[str]
    pinned: bool
    variant: str  # "grid" | "hero" | "fullwidth"


@dataclass(frozen=True)
class TagCountVM:
    name: str
    count: int


@dataclass(frozen=True)
class ProjectsBlockVM:
    tags: Sequence[TagCountVM]
    show_tags_panel: bool
    hero: Optional[ProjectCardVM]
    cards: Sequence[ProjectCardVM]

    def tags_param(self) -> str:
        # "name:count|name:count|..."
        return "|".join(f"{t.name}:{t.count}" for t in self.tags)


def build_projects_block_vm(projects: Iterable[Project], *, spec: ProjectsPageRenderSpec) -> ProjectsBlockVM:
    ps = list(projects)
    featured_stack = spec.featured_stack
    hero_p: Optional[Project] = ps[0] if (spec.show_featured and ps and not featured_stack) else None
    rest = ps[1:] if hero_p else ps

    tags: list[TagCountVM] = []
    if spec.show_tags_panel:
        counts: dict[str, int] = {}
        for p in ps:
            for t in p.tags:
                counts[t] = counts.get(t, 0) + 1
        for name, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].lower())):
            tags.append(TagCountVM(name=name, count=count))

    def to_card_vm(p: Project, variant: str) -> ProjectCardVM:
        return ProjectCardVM(
            href=_project_page_href(p.slug, spec.link_prefix),
            thumb_src=_thumb_src(p.thumbnail_path, spec.asset_prefix),
            title=p.title,
            meta=format_project_meta_line(p, show_time_period=spec.show_time_period),
            org=strip_parens_url(p.org_for) if spec.show_org_for else "",
            excerpt=p.excerpt or "",
            tags=tuple(p.tags) if spec.show_tags else tuple(),
            pinned=p.pinned,
            variant=variant,
        )

    hero_vm = to_card_vm(hero_p, "hero") if hero_p else None
    card_variant = "fullwidth" if featured_stack else "grid"
    cards_vm = tuple(to_card_vm(p, card_variant) for p in rest)
    return ProjectsBlockVM(tags=tuple(tags), show_tags_panel=spec.show_tags_panel, hero=hero_vm, cards=cards_vm)

