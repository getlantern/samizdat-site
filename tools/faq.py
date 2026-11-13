#!/usr/bin/env python3
"""The FAQ: one list that generates both the visible FAQ section and its
schema.org FAQPage markup in index.html, so the two can't drift apart.

Edit FAQ below, then run: python3 tools/faq.py
Answers are HTML (links allowed); the JSON-LD gets the same text with tags
stripped.
"""
import html
import json
import re
from pathlib import Path

SITE = "https://samizdat.lantern.io/"

FAQ = [
    ("What is Samizdat?",
     "Samizdat is an open-source censorship-circumvention protocol from "
     "<a href=\"https://lantern.io\">Lantern</a>. It carries proxy traffic inside "
     "TLS&nbsp;1.3 and HTTP/2 connections that look like a browser visiting a real "
     "website. The server authenticates its own clients inside the TLS handshake and "
     "hands everything else to a real cover site, and the first records after the "
     "handshake are shaped to match a model of real TLS traffic."),
    ("How is Samizdat different from VLESS and XTLS Vision?",
     "VLESS sends its client ID inside TLS and falls back to a server the operator "
     "runs, behind the operator's own certificate. Vision adds padding to the inner "
     "TLS handshake. Neither shapes the start of the connection: CenKL (IEEE S&amp;P "
     "2027) found both send telltale 1,208-byte packets right after the handshake, and "
     "71.7% of Vision connections start with one. Samizdat sends probes to a real "
     "cover site, multiplexes over HTTP/2, turns off the record sizing behind those "
     "1,208-byte packets, and shapes its first 10 records. See the "
     "<a href=\"#compare\">comparison</a>."),
    ("Is Samizdat the same as REALITY?",
     "No, but its version 2 authentication follows REALITY's design: an X25519 secret "
     "between the client's key share and the server's key, sealing a time and short ID "
     "into the TLS SessionID, bound to the whole ClientHello. Samizdat adds a replay "
     "filter (REALITY has none, and a 2026 proof of concept detects REALITY by "
     "replaying handshakes), checks the time by default, doesn't need the cover site "
     "to be reachable for its own clients, multiplexes over HTTP/2, and shapes the "
     "start of each connection."),
    ("Can censors detect Samizdat?",
     "No proxy that carries real traffic is invisible, and nobody outside Lantern has "
     "evaluated Samizdat yet. Measured against CenKL's model of 326.5 million real TLS "
     "flows, Samizdat's connection starts score 12.4 nats of divergence, against 11.3 "
     "for real TLS sampled from the same model and 63.0 before shaping. Timing isn't "
     "shaped, and tunnelled TLS is still inside the connection; see "
     "<a href=\"#limits\">Limits</a>."),
    ("How does Samizdat resist active probing?",
     "A handshake without a valid authentication tag, or one that has been used "
     "before, is forwarded byte for byte to the real cover site, so a prober sees that "
     "site's certificate, TLS behaviour and pages. The server remembers the SessionIDs "
     "it has accepted for 24 to 48 hours, and version 2 tags expire 12 hours either "
     "side of the server's clock, so replaying a captured handshake doesn't work "
     "either."),
    ("What is connection-start shaping?",
     "Researchers found that proxies stand out in the first few packets after the TLS "
     "handshake, before much user data flows. Samizdat's client and server derive a "
     "shared seed from the TLS session, draw the same schedule of 10 record sizes and "
     "directions from CenKL's model of real TLS, and send exactly those records, "
     "carrying their own data and padding the rest. After the tenth record, data "
     "passes straight through."),
    ("Does Samizdat avoid TLS-in-TLS detection?",
     "Partly. Applications tunnelled through Samizdat bring their own TLS, so there is "
     "TLS inside Samizdat's TLS, as with any proxy. Samizdat multiplexes every stream "
     "over HTTP/2, which Xue et al. (USENIX Security 2024) found lowers their attack's "
     "true positive rate by over 70% when two or more streams share a connection, and "
     "much less with one. Samizdat hasn't been measured against that attack."),
    ("How is Samizdat different from Shadowsocks?",
     "Shadowsocks traffic is encrypted from its first byte, and China's Great Firewall "
     "has flagged it by the length and entropy of the first packet (IMC 2020). "
     "Samizdat opens with a standard TLS&nbsp;1.3 ClientHello with Chrome's "
     "fingerprint, like a browser."),
    ("Does Samizdat use UDP or QUIC?",
     "No. Samizdat runs over TCP only, so networks that block UDP, as some in Russia "
     "do, don't affect it."),
    ("Is Samizdat open source?",
     "Yes. Samizdat is written in Go and released under the Apache License 2.0 at "
     "<a href=\"https://github.com/getlantern/samizdat\">github.com/getlantern/samizdat</a>. "
     "The library has no sing-box dependency; <a href=\"https://github.com/getlantern/lantern-box\">lantern-box</a> "
     "adds a sing-box inbound and outbound."),
    ("How do I use Samizdat?",
     "The easiest way is to <a href=\"https://lantern.io/download\">download Lantern</a>, "
     "which uses Samizdat among its protocols. Developers can use the Go library or "
     "lantern-box's sing-box inbound and outbound; see <a href=\"#use\">Use it</a>."),
    ("Who makes Samizdat?",
     "<a href=\"https://lantern.io\">Lantern</a>, a nonprofit VPN and censorship-"
     "circumvention project run by Brave New Software Project, Inc."),
    ("Why is it called Samizdat?",
     "Samizdat (Russian самиздат, \"self-published\") was the practice of copying "
     "banned writing by hand and passing it on in secret in the Soviet Union."),
]


def strip(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).replace(" ", " ")


def faq_html() -> str:
    items = []
    for i, (q, a) in enumerate(FAQ):
        slug = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")
        items.append(
            f'      <div class="qa" id="{slug}">\n'
            f'        <h3><span class="q">Q.</span> {html.escape(q)}</h3>\n'
            f'        <p><span class="a">A.</span> {a}</p>\n'
            f'      </div>'
        )
    return "\n".join(items)


def faq_jsonld() -> dict:
    return {
        "@type": "FAQPage",
        "@id": SITE + "#faq",
        "isPartOf": {"@id": SITE + "#webpage"},
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
            for q, a in FAQ
        ],
    }


def graph() -> dict:
    org = {
        "@type": "Organization",
        "@id": "https://lantern.io/#organization",
        "name": "Lantern",
        "legalName": "Brave New Software Project, Inc.",
        "url": "https://lantern.io",
        "sameAs": ["https://github.com/getlantern"],
    }
    return {
        "@context": "https://schema.org",
        "@graph": [
            org,
            {
                "@type": "WebSite",
                "@id": SITE + "#website",
                "url": SITE,
                "name": "Samizdat",
                "publisher": {"@id": org["@id"]},
                "inLanguage": "en",
            },
            {
                "@type": "WebPage",
                "@id": SITE + "#webpage",
                "url": SITE,
                "name": "Samizdat: a censorship-circumvention protocol from Lantern",
                "isPartOf": {"@id": SITE + "#website"},
                "about": {"@id": SITE + "#software"},
                "primaryImageOfPage": SITE + "og.png",
                "inLanguage": "en",
            },
            {
                "@type": "SoftwareSourceCode",
                "@id": SITE + "#software",
                "name": "Samizdat",
                "description": strip(FAQ[0][1]),
                "codeRepository": "https://github.com/getlantern/samizdat",
                "programmingLanguage": "Go",
                "license": "https://www.apache.org/licenses/LICENSE-2.0",
                "url": SITE,
                "author": {"@id": org["@id"]},
                "keywords": "censorship circumvention, proxy protocol, TLS, HTTP/2, "
                            "REALITY, VLESS, XTLS Vision, traffic shaping, active probing",
            },
            faq_jsonld(),
        ],
    }


def main() -> None:
    p = Path(__file__).resolve().parent.parent / "index.html"
    s = p.read_text()
    s = re.sub(r"(<!-- faq:start -->).*?(\n[ \t]*<!-- faq:end -->)",
               lambda m: m.group(1) + "\n" + faq_html() + m.group(2), s, flags=re.S)
    ld = json.dumps(graph(), ensure_ascii=False, indent=1)
    s = re.sub(r'(<script type="application/ld\+json">\n).*?(\n</script>)',
               lambda m: m.group(1) + ld + m.group(2), s, flags=re.S)
    p.write_text(s)


if __name__ == "__main__":
    main()
