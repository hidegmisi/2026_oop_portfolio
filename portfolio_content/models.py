from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional, Sequence
from urllib.parse import urlparse


@dataclass(frozen=True)
class Project:
    title: str
    slug: str
    link: str
    excerpt: str
    org_for: str
    tags: Sequence[str]
    pinned: bool
    published: bool
    publish_date: Optional[date]
    time_period: str
    thumbnail_path: Optional[str]

    def __post_init__(self) -> None:
        title = self.title.strip()
        slug = self.slug.strip()
        link = self.link.strip()
        if not title:
            raise ValueError("Project title must not be empty.")
        if not slug:
            raise ValueError("Project slug must not be empty.")
        if any(ch.isspace() for ch in slug):
            raise ValueError("Project slug must not contain whitespace.")

        parsed = urlparse(link)
        if not (parsed.scheme and parsed.netloc):
            raise ValueError(f"Project link must be an absolute URL: {self.link!r}")

        normalized_tags = tuple(t.strip() for t in self.tags if t and t.strip())
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "slug", slug)
        object.__setattr__(self, "link", link)
        object.__setattr__(self, "tags", normalized_tags)

