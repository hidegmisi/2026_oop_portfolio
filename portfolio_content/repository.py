from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from typing import Iterable, List, Optional, Protocol, Sequence, Tuple

from .csv_row_parser import ProjectCsvRowParser, ProjectParser
from .models import Project


@dataclass(frozen=True)
class ProjectSortSpec:
    pinned_first: bool = True
    newest_first: bool = True


class ProjectSorter(Protocol):
    def key(self, project: Project) -> Tuple[object, ...]:
        ...


@dataclass(frozen=True)
class PinnedThenDateSorter:
    pinned_first: bool = True
    newest_first: bool = True

    def key(self, project: Project) -> Tuple[object, ...]:
        pinned_rank = 0 if (self.pinned_first and project.pinned) else 1
        sort_date = project.publish_date or date(1900, 1, 1)
        date_rank = -sort_date.toordinal() if self.newest_first else sort_date.toordinal()
        return (pinned_rank, date_rank, project.title.lower())


class DateOnlySorter:
    def key(self, project: Project) -> Tuple[object, ...]:
        sort_date = project.publish_date or date(1900, 1, 1)
        return (-sort_date.toordinal(), project.title.lower())


class ProjectRepositoryProtocol(Protocol):
    def load(self) -> List[Project]:
        ...

    def load_published(self) -> List[Project]:
        ...

    def sorted(
        self,
        projects: Iterable[Project],
        spec: Optional[ProjectSortSpec] = None,
        sorter: Optional[ProjectSorter] = None,
    ) -> List[Project]:
        ...

    def pinned(self, projects: Iterable[Project]) -> List[Project]:
        ...


class ProjectRepository:
    REQUIRED_COLUMNS = {
        "Title",
        "Excerpt",
        "For",
        "Pinned",
        "Publish Date",
        "Published",
        "Slug",
        "Tags",
        "Thumbnail",
        "Time Period",
        "link",
    }

    def __init__(self, csv_path: str, parser: Optional[ProjectParser] = None):
        self.csv_path = csv_path
        self.parser = parser or ProjectCsvRowParser()

    def load(self) -> List[Project]:
        with open(self.csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError(f"CSV has no header row: {self.csv_path}")

            missing = self.REQUIRED_COLUMNS.difference(set(reader.fieldnames))
            if missing:
                raise ValueError(f"CSV missing required columns {sorted(missing)} in {self.csv_path}")

            projects: List[Project] = []
            for row in reader:
                projects.append(self.parser.parse(row))
            return projects

    def load_published(self) -> List[Project]:
        return [p for p in self.load() if p.published]

    def sorted(
        self,
        projects: Iterable[Project],
        spec: Optional[ProjectSortSpec] = None,
        sorter: Optional[ProjectSorter] = None,
    ) -> List[Project]:
        active_sorter = sorter
        if active_sorter is None:
            active_spec = spec or ProjectSortSpec()
            active_sorter = PinnedThenDateSorter(
                pinned_first=active_spec.pinned_first,
                newest_first=active_spec.newest_first,
            )
        return sorted(list(projects), key=active_sorter.key)

    def pinned(self, projects: Iterable[Project]) -> List[Project]:
        return [p for p in projects if p.pinned]


