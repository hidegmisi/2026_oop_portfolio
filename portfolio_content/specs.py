from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CardDisplayOptions:
    show_org_for: bool = True
    show_time_period: bool = True
    show_tags: bool = True
    show_pinned_status: bool = True
    show_featured: bool = True
    featured_stack: bool = False


@dataclass(frozen=True)
class TagsPanelOptions:
    show_panel: bool = True


@dataclass(frozen=True)
class ProjectsPageRenderSpec:
    columns: int = 2
    link_prefix: str = ""
    asset_prefix: str = ""
    card_display: CardDisplayOptions = CardDisplayOptions()
    tags_panel: TagsPanelOptions = TagsPanelOptions()

    @property
    def show_org_for(self) -> bool:
        return self.card_display.show_org_for

    @property
    def show_time_period(self) -> bool:
        return self.card_display.show_time_period

    @property
    def show_tags(self) -> bool:
        return self.card_display.show_tags

    @property
    def show_pinned_status(self) -> bool:
        return self.card_display.show_pinned_status

    @property
    def show_featured(self) -> bool:
        return self.card_display.show_featured

    @property
    def featured_stack(self) -> bool:
        return self.card_display.featured_stack

    @property
    def show_tags_panel(self) -> bool:
        return self.tags_panel.show_panel
