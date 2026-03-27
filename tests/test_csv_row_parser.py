from __future__ import annotations

import pytest

from portfolio_content.csv_row_parser import ProjectCsvRowParser


def _valid_row() -> dict[str, str]:
    return {
        "Title": "Sample Project",
        "Excerpt": "Demo excerpt",
        "For": "Demo Org (https://example.com)",
        "Pinned": "yes",
        "Publish Date": "March 14, 2026",
        "Published": "true",
        "Slug": "sample-project",
        "Tags": "python, data",
        "Thumbnail": "Website%20DB/sample.jpg",
        "Time Period": "2025-2026",
        "link": "https://example.com/project",
    }


def test_parse_uses_thumbnail_extension_from_csv_basename() -> None:
    parser = ProjectCsvRowParser()
    project = parser.parse(_valid_row())
    assert project.thumbnail_path == "assets/project_thumbs/sample-project.jpg"


def test_parse_empty_tags_yields_empty_list() -> None:
    parser = ProjectCsvRowParser()
    row = _valid_row()
    row["Tags"] = ""
    project = parser.parse(row)
    assert project.tags == ()


@pytest.mark.parametrize("field", ["Title", "Slug", "link"])
def test_parse_rejects_missing_required_fields(field: str) -> None:
    parser = ProjectCsvRowParser()
    row = _valid_row()
    row[field] = ""
    with pytest.raises(ValueError):
        parser.parse(row)


def test_parse_rejects_invalid_boolean_values() -> None:
    parser = ProjectCsvRowParser()
    row = _valid_row()
    row["Pinned"] = "sometimes"
    with pytest.raises(ValueError, match="Unsupported boolean value"):
        parser.parse(row)


def test_parse_uses_injected_thumbnail_resolver() -> None:
    class StubResolver:
        def resolve(self, *, raw_thumbnail: str, slug: str) -> str | None:
            return f"custom/{slug}.webp"

    parser = ProjectCsvRowParser(thumbnail_resolver=StubResolver())
    project = parser.parse(_valid_row())
    assert project.thumbnail_path == "custom/sample-project.webp"
