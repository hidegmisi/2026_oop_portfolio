# 2026_oop_portfolio

Quarto portfolio site for an Object-Oriented Programming (OOP) course project.

## Live site

The Quarto site for this portfolio is published via GitHub Pages:

https://jugdemon.github.io/2026_oop_portfolio/

Also available on Posit Connect Cloud (example):

https://019c0abb-84a7-0b13-4068-0e4f305e4b63.share.connect.posit.cloud

## Repository structure

- `_quarto.yml`: Quarto website config (navbar/theme/css/includes).
- `index.qmd`, `about.qmd`, `projects/*.qmd`: site pages.
- `projects/_generated_projects.qmd`, `projects/_generated_pinned_projects.qmd`: generated partials (do not edit manually).
- `data/projects.csv`: source-of-truth project metadata.
- `assets/project_thumbs/`: project thumbnails.
- `portfolio_content/`: OOP content pipeline package:
  - `models.py`: typed domain model (`Project`).
  - `csv_row_parser.py`: CSV row -> `Project` parser/validation.
  - `repository.py`: CSV loading, filtering, deterministic sorting.
  - `specs.py`: immutable render spec(s).
  - `viewmodels.py`: `Project` -> UI viewmodels.
  - `renderers.py`: Quarto/HTML rendering.
  - `text_utils.py`: shared presentation utilities.
- `scripts/build_site_content.py`: build orchestration (`SiteContentBuilder`).
- `tests/`: parser/sorting tests.

## Local setup

From repo root:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Content workflow

1. Update project data in `data/projects.csv`.
2. Add thumbnail files to `assets/project_thumbs/` using slug naming:
   - default: `assets/project_thumbs/<slug>.png`
   - if `Thumbnail` column has another extension (e.g. `.jpg`), use `assets/project_thumbs/<slug>.<ext>`
3. Regenerate generated content:

```bash
python scripts/build_site_content.py
```

## Verification loop

From repo root:

```bash
python scripts/build_site_content.py
quarto render
pytest
```

## Local development server

```bash
quarto preview
```

Quarto prints a local URL and auto-reloads on file changes.

## Deployment

Preferred flow:

```bash
quarto publish gh-pages
```