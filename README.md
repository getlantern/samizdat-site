# samizdat.lantern.io

The website for [Samizdat](https://github.com/getlantern/samizdat), Lantern's censorship-circumvention protocol: one static `index.html` with no build step, served by Cloudflare Pages.

Cloudflare Pages builds this repository straight from GitHub: every push to `main` deploys it, with no build command and the repository root as the output directory. Pull requests get preview deployments. `_headers` sets the response headers.

To preview locally, open `index.html` in a browser, or run `python3 -m http.server`.

## The FAQ and structured data

The FAQ lives in `tools/faq.py`, which writes both the visible FAQ section and the schema.org `FAQPage` markup into `index.html`, so the two always say the same thing. To change a question or answer, edit the list there and run `python3 tools/faq.py`. The same script writes the rest of the JSON-LD graph (`Organization`, `WebSite`, `WebPage`, `SoftwareSourceCode`).

`og.png` is the 1200×630 link-preview image, a screenshot of `tools/og.html`. `robots.txt` and `sitemap.xml` point crawlers at the one page.

## Keeping it accurate

Every claim about another protocol links to its source code, its authors' documentation, or a peer-reviewed measurement. Xray-core was read at `c456141` and REALITY at `4a26e87` (November 2026). When those projects change, recheck the comparison table against them. Samizdat's own numbers come from its pull requests ([#25](https://github.com/getlantern/samizdat/pull/25), [#28](https://github.com/getlantern/samizdat/pull/28), [#29](https://github.com/getlantern/samizdat/pull/29)).

Fonts are self-hosted from Google Fonts under the SIL Open Font License 1.1: PT Serif, Courier Prime and Big Shoulders Stencil (licenses in `fonts/`).
