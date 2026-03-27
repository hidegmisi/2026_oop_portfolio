from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .models import Project
from .specs import ProjectsPageRenderSpec
from .text_utils import format_project_meta_line, strip_parens_url
from .viewmodels import ProjectCardVM, ProjectsBlockVM, build_projects_block_vm


def _escape_md(text: str) -> str:
    # Minimal escaping for our controlled content.
    return text.replace("\n", " ").strip()


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


class ProjectsPageRenderer:
    def __init__(self, spec: Optional[ProjectsPageRenderSpec] = None):
        self.spec = spec or ProjectsPageRenderSpec()

    def render(self, projects: Iterable[Project]) -> str:
        """Emit Quarto content using viewmodels + Lua shortcodes."""
        ps = list(projects)
        if not ps:
            return "_No published projects yet._\n"

        vm: ProjectsBlockVM = build_projects_block_vm(ps, spec=self.spec)
        tags_param = vm.tags_param() if (vm.show_tags_panel and vm.tags) else ""

        lines: list[str] = []
        lines.append("```{=html}")
        block_classes = "ProjectsBlock"
        if not vm.show_tags_panel:
            block_classes += " ProjectsBlock--single"
        lines.append(f'<div class="{block_classes}">')
        lines.append('<section class="ProjectsBlock_content">')
        lines.append("```")
        lines.append("")

        if self.spec.featured_stack:
            lines.append("```{=html}")
            lines.append('<div class="project-featuredStack">')
            lines.append("```")
            lines.append("")
            for card in vm.cards:
                lines.extend(self._render_card_vm(card))
                lines.append("")
            lines.append("```{=html}")
            lines.append("</div>")
            lines.append("```")
            lines.append("")
        elif vm.hero:
            lines.append("```{=html}")
            lines.append('<div class="project-hero">')
            lines.append("```")
            lines.extend(self._render_card_vm(vm.hero))
            lines.append("```{=html}")
            lines.append("</div>")
            lines.append("```")
            lines.append("")

        if vm.cards and not self.spec.featured_stack:
            lines.append("```{=html}")
            lines.append('<div class="project-grid">')
            lines.append("```")
            lines.append("")
            for card in vm.cards:
                lines.extend(self._render_card_vm(card))
                lines.append("")
            lines.append("```{=html}")
            lines.append("</div>")
            lines.append("```")
            lines.append("")

        lines.append("```{=html}")
        lines.append("</section>")
        lines.append("```")

        if self.spec.show_tags_panel and tags_param:
            lines.append(f'{{{{< tags_panel tags="{_escape_html(tags_param)}" >}}}}')

        lines.append("```{=html}")
        lines.append("</div>")
        lines.append("```")
        lines.append("")
        return "\n".join(lines)

    def _render_card_vm(self, card: ProjectCardVM) -> list[str]:
        title = _escape_html(card.title)
        pinned_flag = card.pinned if self.spec.show_pinned_status else False
        parts = [
            f'href="{_escape_html(card.href)}"',
            f'title="{title}"',
            f'pinned="{"true" if pinned_flag else "false"}"',
            f'variant="{_escape_html(card.variant)}"',
        ]
        if card.thumb_src:
            parts.append(f'thumb_src="{_escape_html(card.thumb_src)}"')
        if card.meta:
            parts.append(f'meta="{_escape_html(card.meta)}"')
        if card.org:
            parts.append(f'org="{_escape_html(card.org)}"')
        if card.excerpt:
            parts.append(f'excerpt="{_escape_html(card.excerpt)}"')
        if card.tags:
            tags_param = "|".join(_escape_md(t) for t in card.tags)
            parts.append(f'tags="{_escape_html(tags_param)}"')
        return [f"{{{{< project_card {' '.join(parts)} >}}}}"]


@dataclass(frozen=True)
class ProjectDetailPageRenderSpec:
    asset_prefix: str = "../"
    body_include_prefix: str = "bodies"


class ProjectDetailPageRenderer:
    def __init__(self, spec: Optional[ProjectDetailPageRenderSpec] = None):
        self.spec = spec or ProjectDetailPageRenderSpec()

    def render(self, p: Project, *, body_include: Optional[str] = None) -> str:
        title = _escape_md(p.title)
        lines: list[str] = []
        lines.append("---")
        lines.append(f'title: "{_escape_html(title)}"')
        lines.append("format: html")
        lines.append("---")
        lines.append("")
        lines.append("```{=html}")
        lines.append('<div class="ProjectDetail">')
        lines.append("```")
        lines.append("")

        lines.extend(self._render_header_card(p))
        lines.append("")
        if body_include:
            lines.extend(self._render_body_include(body_include))
            lines.append("")

        lines.append("```{=html}")
        lines.append("</div>")
        lines.append("```")
        lines.append("")
        return "\n".join(lines)

    def _render_header_card(self, p: Project) -> list[str]:
        meta = _escape_md(format_project_meta_line(p, show_time_period=True))

        org_for = strip_parens_url(_escape_md(p.org_for)) if p.org_for else ""
        excerpt = _escape_md(p.excerpt) if p.excerpt else ""

        prefix = (self.spec.asset_prefix or "").lstrip("/")
        thumb_src = f'{_escape_html(prefix)}{_escape_html(p.thumbnail_path)}' if p.thumbnail_path else ""

        tag_spans = "\n".join(
            f'<span class="project-tag">{_escape_html(_escape_md(t))}</span>' for t in p.tags
        )

        lines: list[str] = []
        lines.append("```{=html}")
        lines.append('<header class="project-detailHeader">')
        lines.append('<article class="project-detailCard">')
        if thumb_src:
            lines.append(
                f'<a class="project-thumbLink" href="{_escape_html(p.link)}" target="_blank" rel="noopener noreferrer">'
                f'<img class="project-thumb project-detailThumb" src="{thumb_src}" alt="{_escape_html(p.title)} thumbnail" loading="lazy" />'
                "</a>"
            )
        lines.append('<div class="project-detailBody">')
        lines.append('<div class="project-head">')
        lines.append(f'<div class="project-detailTitle">{_escape_html(p.title)}</div>')
        if meta:
            lines.append(f'<div class="project-meta">{_escape_html(meta)}</div>')
        if org_for:
            lines.append(f'<div class="project-org">{_escape_html(org_for)}</div>')
        lines.append("</div>")
        if excerpt:
            lines.append(f'<p class="project-excerpt">{_escape_html(excerpt)}</p>')
        if tag_spans:
            lines.append(f'<div class="project-tags">{tag_spans}</div>')
        lines.append(
            f'<div class="project-detailActions"><a class="project-detailLink" href="{_escape_html(p.link)}" target="_blank" rel="noopener noreferrer">Open project ↗</a></div>'
        )
        lines.append("</div>")
        lines.append("</article>")
        lines.append("</header>")
        lines.append("```")
        return lines

    def _render_body_include(self, include_path: str) -> list[str]:
        lines: list[str] = []
        lines.append(f"{{{{< include {include_path} >}}}}")
        return lines
