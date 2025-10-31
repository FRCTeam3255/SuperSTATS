# Copilot instructions for SuperSTATs

Purpose: Make AI coding agents immediately productive in this repo by documenting the “how it works” and the non-obvious developer workflows.

## Big-picture
- This is a Streamlit, multi-page app for FRC scouting and analytics.
- Core package: `src/SuperSTATs` with pages in `src/SuperSTATs/pages/` (Streamlit discovers pages automatically).
- Entry point for local dev: `src/SuperSTATs/Main.py` (homepage overview). Pages are ordered by filename prefix like `1_`, `2_` plus emoji.
- All pages/components rely on a single initializer: always call `load.app_init()` at the top of any page/module that touches `st.session_state`.

## Key modules and responsibilities
- `load.py` (critical)
  - Initializes session state: sheets, configs, TBA client, colors, matches, presets, forms, analytics flags.
  - External IO:
    - Google Sheets CSV export via IDs in `st.secrets`.
    - The Blue Alliance via `tbapy`.
    - frc-colors.com for team colors.
    - Optional Nexus API for queue status.
  - Data shaping helpers: `download_sheets_raw`, `organize_df`, `get_matches`, `get_unplayed`, `get_team_info`, `get_team_colors`, `get_match_data`, etc.
- `build.py`
  - Reusable UI/visualization builders: `gen_bar`, `gen_match_comp`, `scouting_expander`, `calc_projected`.
  - Uses Altair/Matplotlib and relies on columns naming conventions (see below).
- `analytics.py`
  - Lightweight event logging to Google Forms via prefill URL. Controlled by `st.session_state.console["collect_analytics"]` and per-event toggles.
- `form.py`
  - Scrapes Google Form field entry IDs, caches mappings for `STATS_FORM` and `SCOUTING_FORM` so pages can submit responses programmatically.
- `styles.py`
  - Small CSS helpers for headings/effects.
- `pages/*`
  - Feature pages that compose the above: stats, match previews, tracker, input UIs, data check, console/admin.

## Session state contract (do not break)
`load.app_init()` must be called before using any of these keys: `df`, `configs`, `console`, `tba`, `tba_ranks`, `team_info`, `team_colors`, `match_data`, `matches`, `unplayed_matches`, `nexus_data`, `picked`, `scouting`, `scouts`/`assigned`, `phases`, `presets`, `forms`, `analytics_settings`, `analytics`, `uid`, `page`, `logged_in`, `chat`.

## Secrets required (stored in `.streamlit/secrets.toml`)
- Core: `DEFAULT_EVENT_KEY`, `TEAM_NUMBER`, `TBA_API`, `GSHEET_DOC_ID`
- Sheet tabs (GIDs): `GID_RAW`, `GID_CONFIG`, `GID_MATCHES`, `GID_PICKED`, `GID_SCOUTS`, `GID_SCOUTING`, `GID_TBA_JSON`
- Forms: `STATS_FORM`, `SCOUTING_FORM`, `ANALYTICS_FORM`
- Optional: `NEXUS_API`, `MODERATORS` (list), `APP_PASSWORD`
Note: setup script moves a template from `src/setup/streamlit/secrets.toml` to `.streamlit/secrets.toml`.

## Data conventions (columns and scoring)
- Raw stats columns follow a convention like `PHASE_FEATURE_WEIGHT_TYPE`, e.g. `AUTO_SPEAKER_3_INT`.
  - `get_point_values` and `add_cols` derive scoring by multiplying columns by the trailing numeric weight and summing all columns sharing the same `PHASE`.
  - Phases are parsed from column prefixes; `st.session_state.phases` is computed from headers.
- `COMMENT_GENERAL_STR_1` holds comma-separated “features” used for filtering and team feature lists.
- Match naming: `"Match Name" == comp_level + " " + number`, with comp levels normalized to `Quals`, `Playoffs`, `Finals`.

## External integrations
- TBA via `tbapy` for event teams, rankings, matches, score breakdowns.
- Google Sheets CSV for all editable data and configs (by GID).
- Google Forms for programmatic submissions (prefill URLs assembled from scraped entry IDs).
- frc-colors.com for team primary/secondary hex colors (cached in `src/pickles/colors.pickle`).
- Local caches under `src/pickles/`: `configs.pickle`, `colors.pickle`, `presets.pickle`, `scouts.pickle`, optional `map.pickle`.

## Common workflows
- Setup (Windows-first project): run `python3 -m src/setup/setup.py` (creates `.venv`, moves secrets template, installs deps). On macOS/Linux, ensure venv activation uses `source .venv/bin/activate`.
- Run locally: `streamlit run src/SuperSTATs/Main.py` (ensure venv active and secrets present).
- Add a page: create a file in `src/SuperSTATs/pages/` named like `8_✨_My_Page.py`, then:
  - `import SuperSTATs.load as load`; call `load.app_init()`
  - Optional: `import SuperSTATs.analytics as analytics`; call `analytics.collect_analytics("page_change", "my_page")`
  - Reuse `build.gen_bar` or `build.gen_match_comp` as needed.
- Presets/colors/scouts are managed via the Console page and persisted to pickles; avoid editing pickles directly in code.

## Project-specific gotchas
- Paths in code use Windows separators (e.g., `"src\\pickles"`). If you implement cross-platform fixes, prefer `os.path.join` and test on Windows. Preserve existing behavior unless explicitly changing platform support.
- Several imports are used implicitly by Streamlit (e.g., pandas, numpy, altair). If you add new libs, add them to `pyproject.toml` `[project.dependencies]` and reinstall with `pip install -e .`.
- Many functions assume `st.secrets` keys exist. Don’t hardcode tokens; guard external calls and keep fallbacks (e.g., sheets-only flows when TBA is unavailable).
- Google Form scraping (`form.get_entries`) depends on current form HTML structure; changes to the Forms can break it—test after form updates.

## Examples in the codebase
- Bar/ranking chart: `build.gen_bar(st.session_state.df, st.session_state.picked, st.session_state.tba_ranks)` as used in `pages/1_🏆_Stats.py`.
- Match preview flow: `pages/2_🔮_Preview.py` shows alliance assembly, projections (`build.calc_projected`), and actual TBA scores.
- Team tracker: `pages/3_🎯_Tracker.py` demonstrates deep-dive for a single team with match context via URL params.
- Data verification: `pages/6_👾_Data_Check.py` cross-checks SN vs TBA and surfaces missing teams/comments and score variances.

If anything here is unclear or you need more detail (e.g., full secrets template or expected column names), tell me what to expand and I’ll refine this doc.