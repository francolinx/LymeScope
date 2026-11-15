# Workbench publication status

**Prepared, not configured or verified live.** GitHub repository metadata rechecked for this release: PUBLIC, default branch `main`, `has_pages: false`. The connection reports admin/maintain permission; no hosting setting was changed. Open `index.html` locally from the reviewed feature checkout until main is approved and published. It embeds the same data and controls as `demo/v0.2.0/index.html`, with original scientific figures and required media copied byte-for-byte into `workbench-assets/`.

No server, JavaScript build, model or network is needed for the guided experience. Local scientific media and controls work offline; optional primary-paper and GitHub evidence links require a network. A browser still has to be checked separately. The most recent normal Chrome tool request returned “The browser access host is unavailable”; that does not establish rendering.

`build_workbench.py` prepares a zero-build `/docs` source with `.nojekyll`. It never changes GitHub Pages, DNS, repository visibility or other hosting settings. The candidate project-site address is `https://francolinx.github.io/LymeScope/`; do not advertise it as a working demo without a successful publication/readback.

The proposed source is **Deploy from a branch → `main` → `/docs`**, after the separately approved main integration. This is supported for public repositories and a repository maintainer/admin can configure it. [Official GitHub instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site). `.nojekyll`, an index at the source root and project-relative local assets are prepared; no custom domain or build installation is needed.

The workbench's local resources stay inside `/LymeScope/`. Evidence outside the hosted `/docs` tree links to GitHub: frozen scientific packages use exact pinned source commits; current submission documents use `main`, the intended release target. Hosting the pre-release checkout while main is still old would leave those main links premature. Approve and publish main before enabling this source.

After explicit **separate hosting authorization**, use the repository's normal Pages settings, wait for its deployment workflow, then verify the actual URL returns the expected page, media, all four stories and missing-data states. Read back the published commit and run browser checks. Until that succeeds, do not replace the offline instructions with an unverified live-demo claim. The static compatibility checks do not prove deployment or browser rendering.

Rebuild presentation only, using existing dependencies:

```text
python -B demo/v0.2.0/build_overlay.py
python -B docs/build_claim_index.py
python -B docs/build_workbench.py
```

The [manifest](workbench-manifest.json) records original source paths, sizes and hashes. Scientific outputs, original checksum manifests and the frozen viewer are untouched. No weight/cache/archive is included. The older workbench and fallback branch remain available.
