# AI ToolRank — $0 MVP

A static, searchable AI tools directory and a Python bot that collects **pending** release announcements from public Atom/RSS feeds. No paid APIs, dependencies, tracking pixels, or credentials required.

## Quick start

Requires Python 3.10+.

```bash
python bot/build.py
python -m http.server 8000 --directory site
```

Open http://localhost:8000 in your browser. **Do not** double-click `index.html`; browsers may block local JSON loading.

## Run research

```bash
python bot/research.py
```

This accesses the public feeds listed in `data/sources.json`, and writes `data/review_queue.json`. Internet access is required for live discovery. A failed source prints a warning without crashing other sources. Release announcements are not new-tool discoveries by themselves; they are change-monitoring candidates. Additional trusted feeds can be added to expand discovery.

## Editorial workflow

1. Inspect `data/review_queue.json` for newly discovered release announcements.
2. Visit original sources and verify claims, product category, and pricing.
3. Add or edit tool entries in `data/tools.json` with `status: "approved"` only after review. Set `score: null` until hands-on testing is complete.
4. Run `python bot/build.py` to update `site/tools.json`.
5. Commit changes to publish. The bot **never** automatically approves a listing, creates an unsupported rating, or writes affiliate links.

## Automated research on GitHub

The `.github/workflows/research.yml` workflow runs once daily (GitHub schedules are not guaranteed exact), and can be triggered manually from the Actions tab. It commits pending candidates to the repository. GitHub Actions minutes and permissions are subject to plan/repository limits. For zero-cost simplicity, use a **public** repository, where standard hosted Actions and GitHub Pages are typically free under current platform terms. Review third-party GitHub Actions before using them in sensitive repositories.

## Publish the website for free

1. Create a GitHub account and a **public** repository, e.g. `aitoolrank`.
2. Upload the files in this folder, preserving paths. You can use GitHub's **Add file → Upload files** interface, or Git locally.
3. Go to **Settings → Pages**, choose **Deploy from a branch**, branch `main`, folder `/docs`. A prebuilt `docs/` directory is included. After editing `data/tools.json`, run `python bot/build.py` and copy updated `site/` files into `docs/` before committing.
4. Open the Pages URL GitHub provides, typically `https://USERNAME.github.io/aitoolrank/`.

## Constraints and next steps

- The directory currently includes a small **illustrative seed set**; summaries and pricing are not live-verified and should be reviewed before production launch.
- The bot monitors release feeds, not the entire internet; it does not run a local language model or automatically test tools. This is intentional for a reliable $0 MVP.
- `score: null` means **not tested/ranked**. Future rankings should include repeatable test cases, citations, test dates, and human editorial approval.
- Feed hosts can rate-limit, move URLs, or change format. The bot logs failures.
- GitHub Pages is static hosting; no server-side personalized AI chatbot is included.
- Free services may have quotas; no cloud infrastructure is deployed automatically from this archive.
- Add an affiliate disclosure before monetizing, and a privacy policy before collecting visitor data.

## Tests

```bash
python -m unittest discover -s tests -v
```
