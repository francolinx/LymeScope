# Workbench publication status

**Prepared, not configured or verified live.** Open `index.html` locally after downloading the feature branch. It embeds the same data and controls as `demo/v0.2.0/index.html`, with original scientific figures and required media copied byte-for-byte into `workbench-assets/`.

No server, JavaScript build, model or network is needed for the guided experience. Local scientific media and controls work offline; optional primary-paper and GitHub evidence links require a network. A browser still has to be checked separately. The most recent normal Chrome tool request returned “The browser access host is unavailable”; that does not establish rendering.

`build_workbench.py` prepares a zero-build `/docs` source with `.nojekyll`. It never changes GitHub Pages, DNS, repository visibility or other hosting settings. The candidate project-site address is `https://francolinx.github.io/LymeScope/`; do not advertise it as a working demo without a successful publication/readback.

After explicit hosting authorization, choose the intended branch and `/docs` source using the repository's normal Pages workflow, then verify the deployed URL, media, all four stories and the missing-data states. This instruction is preparation, not authorization. Until then, the feature branch and offline HTML are the delivery route.

Rebuild presentation only, using existing dependencies:

```text
python -B demo/v0.2.0/build_overlay.py
python -B docs/build_claim_index.py
python -B docs/build_workbench.py
```

The [manifest](workbench-manifest.json) records original source paths, sizes and hashes. Scientific outputs, original checksum manifests and the frozen viewer are untouched. No weight/cache/archive is included. The older workbench and fallback branch remain available.
