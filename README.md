# ashtontink.com (My personal website)

Source for **[www.ashtontink.com](https://www.ashtontink.com/)** — my personal
site for the games, software and learning projects I'm building.

Static HTML and CSS. **No framework, no build step, no tracking**: GitHub Pages
serves the files exactly as they are committed.

> The résumé/portfolio site at **[me.ashtontink.com](https://me.ashtontink.com/)**
> lives in [`digital_resume`](https://github.com/T1nkiePlayz/digital_resume).
> Both sites share the same design language — see [Design](#design).

## Pages

| Path | Page |
| --- | --- |
| `/` | Home — hero, featured project, project grid, latest activity |
| `/projects/` | Every project, grouped by games, software, learning material and system/web |
| `/projects/aetheria/` | Long-term multiplayer 2D ARPG (Godot + C#) |
| `/projects/embermark-forgery/` | 2D smithing game (Rust + Bevy) |
| `/projects/mochi/` | Cross-platform desktop game launcher (Tauri 2 + Rust + React) |
| `/projects/rust-handbook/` | *Rust from Zero* — 21-chapter visual handbook |
| `/projects/java-handbook/` | *Java & Kotlin from Zero* — 32-chapter visual handbook |
| `/about/` | Who I am, what I'm building, skills and interests |
| `/contact/` | Email, GitHub, Reddit and opportunities |
| `/404.html` | Custom not-found page (used automatically by GitHub Pages) |
| `/robots.txt`, `/sitemap.xml` | Crawling and indexing |

## Structure

```text
.
├── index.html                  home
├── 404.html                    not-found page
├── robots.txt
├── sitemap.xml
├── favicon.svg                 SVG icon (violet orb mark)
├── CNAME                       custom domain: www.ashtontink.com
├── css/
│   └── style.css               the entire stylesheet, shared by every page
├── about/
├── contact/
└── projects/
    ├── index.html
    ├── aetheria/
    ├── embermark-forgery/
    ├── mochi/
    ├── rust-handbook/
    └── java-handbook/
```

## Design

`css/style.css` is the single source of truth for styling and is deliberately
aligned with `me.ashtontink.com`:

- **Tokens** — `--bg: #07090d`, `--accent: #7c5cff`, `--accent-light: #a78bfa`,
  `--green: #4ade80`, 18px radius, 1100px container.
- **Type** — Inter for text, JetBrains Mono for labels (`// section_label`),
  tags, metadata and the footer.
- **Surfaces** — translucent `rgba(17, 23, 34, 0.72)` cards with a 15px backdrop
  blur, 1px borders and a lift on hover.
- **Chrome** — a fixed, blurred pill navbar; a violet + cyan background glow
  behind a faint, masked grid.
- **Shared markup** — every page uses the same navbar, footer, skip link and
  `<head>` boilerplate. When you add a page, copy an existing one and change
  the content: keep the skip link, `<main id="main">`, canonical/OG tags and
  the `active` class on the current nav item.

Accessibility and motion: visible `:focus-visible` outlines, a skip-to-content
link, semantic landmarks, `rel="noopener"` on every external link, and a
`prefers-reduced-motion` block that disables transitions.

## Local development

Any static server works — the paths are absolute (`/css/style.css`), so open
the site through a server rather than `file://`:

```sh
python3 -m http.server 8000
# → http://localhost:8000/
```

## Deployment

GitHub Pages publishes the `main` branch as-is.

- `CNAME` holds `www.ashtontink.com`.
- `robots.txt` and `sitemap.xml` point crawlers at every page — update
  `sitemap.xml` whenever a page is added.
- A `404.html` at the repo root is picked up automatically.

## Checks

`check_site.py` is a dependency-free (Python standard library only) sanity
check that runs on every push via `.github/workflows/checks.yml`:

```sh
python3 check_site.py
```

It verifies tag balance, `<title>`/meta/viewport/canonical presence, skip-link
landmarks, duplicate ids, that every internal link resolves to a real file, that
every CSS class used in HTML exists in `style.css`, and that `style.css` contains
**no stray markdown code fences** — which is exactly what once broke the live
site's stylesheet.

## Adding a project

1. Create `projects/<slug>/index.html` — copy an existing project page.
2. Add a card to `projects/index.html` under the right category.
3. Add it to the home page (`index.html`): the hero, "more projects" grid or
   the `// latest` list.
4. Add the URL to `sitemap.xml`.
