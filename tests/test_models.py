from __future__ import annotations

import pytest

from portfolio_content.models import Project


def _base_project(**kwargs: object) -> Project:
    payload = {
        "title": "Valid Project",
        "slug": "valid-project",
        "link": "https://example.com/project",
        "excerpt": "",
        "org_for": "",
        "tags": ("python", " data ", ""),
        "pinned": False,
        "published": True,
        "publish_date": None,
        "time_period": "",
        "thumbnail_path": None,
    }
    payload.update(kwargs)
    return Project(**payload)


def test_project_normalizes_tags_to_immutable_tuple() -> None:
    project = _base_project()
    assert project.tags == ("python", "data")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", " "),
        ("slug", " "),
        ("slug", "bad slug"),
        ("link", "/relative"),
    ],
)
def test_project_rejects_invalid_invariants(field: str, value: str) -> None:
    with pytest.raises(ValueError):
        _base_project(**{field: value})
