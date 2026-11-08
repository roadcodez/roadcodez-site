# roadcodez.com — site source

Static site (HTML + CSS + a little JS). No frameworks, no build tools beyond Python 3.

```
roadcodez-site/
├── src/            page sources + shared header/footer  (EDIT HERE)
│   ├── _header.html   persistent header: logo top-left -> index.html on every page
│   ├── _footer.html
│   ├── index.html · trucking.html · training.html · ai.html · 404.html
├── site/           deployable output (upload THIS folder)  — generated, don't hand-edit *.html
├── _source_drive/  original logo/mascot files copied from Google Drive "Shard" (not published)
└── build.py        python3 build.py  -> regenerates site/*.html, sitemap.xml, robots.txt
```

## Edit + preview
1. Edit files in `src/` (copy lives in `site/css/styles.css`, `site/js/site.js` and `site/assets/` — those are edited in place).
2. `python3 build.py`
3. Preview: `python3 -m http.server 4173 --directory site` then open http://localhost:4173

## Brand assets (site/assets)
Derived from the Drive "Shard" folder. Black backgrounds were converted to transparency for the header/hero.
`rc-mark.png` (header monogram) · `rc-wordmark.png` (header wordmark, tagline cropped off) · `rc-mark-hero.png` · `ogre-mascot.jpg` · `og-image.jpg` (social share) · icons.

## Before going live — confirm
- Contact email (`matt@roadcodez.com`) in `_footer.html` and the CTA buttons.
- Every claim on the pages (statuses: Operating / Working prototype / In development / Concept).
- The logo's baked-in tagline reads "Logistics | Digital Assets | App Development"; the site uses only the monogram + wordmark so it doesn't conflict with Trucking / Training / AI.

## Deploying (not done yet)
Any static host works: upload the contents of `site/`. Cloudflare Pages, Netlify or GitHub Pages are free; point roadcodez.com at the host via DNS at your registrar.

## Generated artwork (tools/)
The truck drawing and the backing diagrams are generated, not hand-drawn, so they stay accurate:

    python3 tools/rig.py        # side view of the rig  -> src/_parts/rig.svg   (edit GAP, colours, decals at the top/in the cab block)
    python3 tools/backing.py    # 3 top-view backing diagrams -> src/_parts/backing_*.svg + tools/backing_report.json
    python3 build.py            # pastes src/_parts/* into pages via {{include:name.svg}}
    python3 tools/verify.py     # independent audit (geometry, arrows, valid XML, duplicate ids, links, no carrier text). Must say 0 FAIL.

`sim.py` is a kinematic tractor-semitrailer model (same dimensions as the side-view drawing). Backing paths are planned for the
trailer axle, the tractor angle and steering are derived, and the steering is replayed through the model to prove the path.
Reference photos live in Google Drive `Shard` (not copied into the site). Carrier names/logos are intentionally not drawn.
