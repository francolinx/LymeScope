# Separate local demo overlay

Open `index.html` directly. All display data are embedded; no server, package, model, CDN or remote connection is required. The existing frozen viewer remains linked and unchanged. `build_overlay.py` regenerates only this new versioned demo layer from saved evidence and its template; it does not write scientific files or original manifests.

The overlay keeps three populations distinct: 202 fully covered alignment columns, 162 observed mapped 1GGQ residues, and their 159-column intersection. Columns 154/173 remain alignment-only and display 1/30 coverage. Masked-original-residue NLL and all model benchmark results remain NOT RUN.

Biological labels come from the saved UniProt features for Q07337/Q44717. Signal 1–18 and Chain beginning 19 agree, but the supplied evidence is prediction/rule based. We describe an annotated boundary and do not claim measured cleavage or remove any frozen residue. The segment between the annotated mature-chain start and the construct is a tether candidate, with no claim of measured flexibility/accessibility.

Before computing the displayed minimum interchain C-alpha distance, the builder validates the actual deposited 1GGQ assembly 1: polymer chains A/B, identity operator, dimeric designation. Other deposited assemblies are recorded. A predeclared 8 Å cutoff labels proximity only; this is not solvent accessibility, antibody accessibility or an antigen ranking.

The separate 1G5Z view requires a unique exact 164-residue construct match to Q44717 native 40–203, with author numbering, residue identities and insertion codes checked against observed atoms. Its historical O31117 reference annotation remains in the data. Its biological dimer requires symmetry operator 2, so this overlay does not calculate a secondary interchain proxy. Missing information stays explicit.

`context.json` records original source hashes and these new presentation annotations. Static/data and UI-handler fixture checks do not establish actual browser rendering; the browser-tool result must be reported separately. No molecular 3D enhancement is a submission prerequisite.

## Original presentation assets

`render_assets.py` uses existing local Pillow/NumPy to render six 960×640 GIFs and static PNG alternatives from the saved data. Camera motion is a rigid transformation, never folding or dynamics. The exact inventory, source hashes, dimensions, byte sizes, frame counts and captions are in `assets/manifest.json`. All 360 GIF frames decode; representative frames are inspected in `qa/animation-contact-sheet.png`. These are media checks, not browser playback verification.

The main page starts with a static coverage scene. The scene selector and play/stop button make motion optional; switching scenes restores a static image. The research card separates observed data, unmeasured model information, published evidence, limitations and a follow-up hypothesis. `build_presentation.py` supplies the accessible original SVG timeline and a separate local README preview. No CDN, server or remote model is needed.

The approved browser path returned “The browser access host is unavailable.” No browser screenshot or rendered-page verification is claimed. Source links, generated data and JS controls are checked offline. See the current `submission/` package for the presenter checklist.
