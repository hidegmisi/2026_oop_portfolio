# AGENTS.md

This repository is a **Quarto** website for an **Object-Oriented Programming (OOP)** course portfolio. The primary grading focus is the **quality of your OOP design and maintainability**, not visual polish.

## Repo structure
- **`_quarto.yml`**: Quarto website configuration (navbar, theme, CSS).
- **`index.qmd`**: Home page.
- **`projects/`**: Project pages and generated project listing.
  - **`projects/_generated_projects.qmd`**: Generated project grid (do not edit by hand).
  - **`projects/_generated_pinned_projects.qmd`**: Generated pinned projects block.
- **`data/projects.csv`**: Source-of-truth project data.
- **`assets/project_thumbs/`**: Project thumbnail images.
- **`portfolio_content/`**: OO content pipeline package.
  - **`models.py`**: Domain model (`Project`).
  - **`csv_row_parser.py`**: CSV row parsing + field validation.
  - **`repository.py`**: CSV loading/filtering/sorting.
  - **`specs.py`**: Typed immutable render specs.
  - **`viewmodels.py`**: `Project` -> viewmodel mapping.
  - **`renderers.py`**: Quarto/HTML rendering.
  - **`text_utils.py`**: Shared formatting utilities.
- **`scripts/build_site_content.py`**: Build orchestration via `SiteContentBuilder`.

## Content workflow (how to update projects)
1. **Edit data** in `data/projects.csv`.
2. **Add thumbnails** to `assets/project_thumbs/`.
   - **Convention**: thumbnail file name is the project slug:
     - `assets/project_thumbs/<slug>.png` (default)
     - If the CSV `Thumbnail` column contains a filename with a different extension (e.g. `.jpg`), the generator uses that extension for the slug file.
   - Therefore: you only need to ensure `assets/project_thumbs/<slug>.<ext>` exists.
3. Regenerate the partial:

```bash
python scripts/build_site_content.py
```

4. Preview the site (see “Local dev server” below).

## OOP standards (what we’re demonstrating)
- **Single Responsibility Principle (SRP)**: keep parsing, sorting, and rendering in separate classes/modules.
- **Typed domain model**: `Project` is the central data model; avoid passing around raw dicts.
- **Deterministic output**: the generator should always produce the same output given the same inputs (stable sorting).
- **No “stringly-typed” templates** scattered across `.qmd`: Quarto pages should mostly include generated partials.

## Local dev server
From repo root:

```bash
# (Optional) regenerate generated content first
python scripts/build_site_content.py

# Start Quarto live preview server
quarto preview
```

Quarto will print a local URL (typically `http://localhost:xxxx`) and auto-reload on changes.

## Baseline verification loop (run before/after changes)
From repo root:

```bash
# Regenerate generated content (partials + per-project pages)
python scripts/build_site_content.py

# Render site to _site/
quarto render

# Run unit tests for pipeline boundaries
pytest
```

### Visual spot-check (fast)
- **Home**: `index.qmd` → Featured Projects section is clean and not broken.
- **Projects listing**: `projects/index.qmd` → featured card + tags panel + grid layout looks correct.
- **One project detail page**: `projects/<slug>.qmd` (e.g. `projects/vox-populi-us2024.qmd`) → header renders, external link works, optional body include doesn’t error if missing.

## Shiny app (optional)
The example Shiny app lives in `projects/data/app.py`.

```bash
pip install -r requirements.txt
cd projects/data
shiny run app.py
```

## Deployment (GitHub Pages)
Preferred: publish with Quarto’s built-in GitHub Pages publishing.

```bash
# one-time setup may be required in GitHub repo settings
quarto publish gh-pages
```

This publishes the rendered site to the `gh-pages` branch and configures Pages to serve it.

If you prefer a manual flow, you can render locally and push the output branch, but avoid committing `_site/` unless your chosen workflow explicitly requires it.

