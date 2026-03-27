from __future__ import annotations

from datetime import date, datetime
from typing import Optional, Protocol, Sequence

from .models import Project
from .paths import ThumbnailPathResolver


class ProjectParser(Protocol):
    def parse(self, row: dict[str, str]) -> Project:
        ...


class ProjectCsvRowParser:
    def __init__(self, thumbnail_resolver: Optional[ThumbnailPathResolver] = None):
        self.thumbnail_resolver = thumbnail_resolver or ThumbnailPathResolver()

    def parse(self, row: dict) -> Project:
        title = (row.get("Title") or "").strip()
        slug = (row.get("Slug") or "").strip()
        link = (row.get("link") or "").strip()
        excerpt = (row.get("Excerpt") or "").strip()
        org_for = (row.get("For") or "").strip()

        pinned = self._parse_bool(row.get("Pinned", ""))
        published = self._parse_bool(row.get("Published", ""))
        publish_date = self._parse_date(row.get("Publish Date", ""))
        time_period = (row.get("Time Period") or "").strip()
        tags = self._parse_tags(row.get("Tags", ""))
        thumbnail_path = self.thumbnail_resolver.resolve(raw_thumbnail=row.get("Thumbnail", ""), slug=slug)

        if not title:
            raise ValueError(f"Project row missing Title: {row}")
        if not slug:
            raise ValueError(f"Project row missing Slug for {title!r}")
        if not link:
            raise ValueError(f"Project row missing link for {title!r}")

        return Project(
            title=title,
            slug=slug,
            link=link,
            excerpt=excerpt,
            org_for=org_for,
            tags=tags,
            pinned=pinned,
            published=published,
            publish_date=publish_date,
            time_period=time_period,
            thumbnail_path=thumbnail_path,
        )

    @staticmethod
    def _parse_bool(value: str) -> bool:
        v = (value or "").strip().lower()
        if v in {"yes", "true", "1"}:
            return True
        if v in {"no", "false", "0", ""}:
            return False
        raise ValueError(f"Unsupported boolean value: {value!r}")

    @staticmethod
    def _parse_date(value: str) -> Optional[date]:
        v = (value or "").strip()
        if not v:
            return None
        return datetime.strptime(v, "%B %d, %Y").date()

    @staticmethod
    def _parse_tags(value: str) -> Sequence[str]:
        v = (value or "").strip()
        if not v:
            return tuple()
        return tuple(t.strip() for t in v.split(",") if t.strip())
