# Google Search Console indexing

The production canonical URL is `https://gyansutraapp.com`. The sitemap, HTML
canonicals, and structured data only use that hostname.

## Cloudflare redirects

Cloudflare Pages exposes two duplicate hosts that cannot be redirected from the
repository alone. In **Cloudflare Dashboard → Bulk Redirects**, create these
two permanent rules:

| Source URL | Target URL | Status | Options |
| --- | --- | --- | --- |
| `https://www.gyansutraapp.com` | `https://gyansutraapp.com` | 301 | Preserve query string, subpath matching, preserve path suffix |
| `https://gyansutraapp.pages.dev` | `https://gyansutraapp.com` | 301 | Preserve query string, subpath matching, preserve path suffix |

Keep the `www` DNS record proxied in Cloudflare so the first rule can run.
The deployment also sends `X-Robots-Tag: noindex, follow` for both hosts until
the redirects propagate.

## Search Console follow-up

1. Submit `https://gyansutraapp.com/sitemap.xml` in the **Sitemaps** report.
2. Use **URL Inspection** on the homepage, `/bhagavad-gita`, `/ramayana`, and
   one Vishnu Purana section. Confirm Google-selected canonical is the apex
   HTTPS URL, then request indexing for these representative pages only.
3. Start validation for the duplicate-canonical issue after the two redirects
   return `301`. A page listed as **Page with redirect** is expected and should
   remain excluded.

The sitemap deliberately contains only canonical URLs and has no generated
`lastmod`, `changefreq`, or `priority` values. These values must reflect real
content updates; regenerating them on every deploy produces misleading crawl
signals.
