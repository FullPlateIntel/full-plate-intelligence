# SEO_MAP.md

Production origin (CONFIRM): `https://fullplateintel.com`. Sitemap: `/sitemap.xml`. Robots: `/robots.txt` (staging variant in `hosting/robots.staging.txt`, to be paired with an `X-Robots-Tag: noindex` header and HTTP auth).

Trailing-slash URLs are canonical; the host must 301 the bare path to the slash form (rules included in `hosting/candidates/`). Canonical host (apex vs www) must be chosen before DNS; the build refuses localhost/staging origins.

| Page | URL | Search intent | Title | Meta description | Share image | Structured data |
|---|---|---|---|---|---|---|
| home | / | Full Plate Intelligence, Full Plate Intel, restaurant financial insights, restaurant business intelligence | Full Plate Intelligence \| Restaurant Financial Insights for Independent Restaurants | Full Plate Intelligence (Full Plate Intel) helps independent restaurant owners see their numbers the way top operators do: a free weekly newsletter on food cost, labor, cash flow and profitability, with restaurant research and benchmarking tools on the way. | /assets/share/og-home.png (1200x630) | Organization (#organization), Person (#person), WebSite (#website), WebPage |
| weekly | /weekly/ | restaurant newsletter, restaurant financial newsletter, food cost / labor cost / cash flow / profitability education | Full Plate Weekly \| Free Restaurant Financial Newsletter | Full Plate Weekly is a free restaurant newsletter with practical financial insights for independent owners: food cost, labor cost, cash flow, occupancy and profitability, in one short email a week. | /assets/share/og-weekly.png (1200x630) | WebPage; Organization; Person; WebSite (@graph) |
| show | /show/ | restaurant podcast, restaurant-business conversations | The Full Plate Show \| Restaurant Business Conversations | The Full Plate Show is an upcoming restaurant podcast: practical conversations with owners, chefs, investors, lenders and technologists about the decisions that shape a restaurant business. | /assets/share/og-show.png (1200x630) | WebPage; Organization; Person; WebSite (@graph) |
| index | /restaurant-intelligence-index/ | restaurant industry report, independent restaurant data, restaurant financial trends, food and beverage costs, labor and productivity | Restaurant Intelligence Index \| Independent Restaurant Industry Report | The Restaurant Intelligence Index is a planned twice-yearly restaurant industry report built from independent restaurant data: sales and profitability, food and beverage costs, labor and productivity, operator sentiment and technology. Paid per edition. | /assets/share/og-index.png (1200x630) | WebPage; Organization; Person; WebSite (@graph) |
| benchmark | /benchmark/ | restaurant benchmarking, restaurant financial benchmarks, food cost / labor / prime cost topics | Full Plate Benchmark \| Restaurant Financial Benchmarking | Full Plate Benchmark is a planned restaurant benchmarking tool: compare food cost, labor, prime cost and profitability against restaurants like yours by concept, cuisine, revenue and market. Paid Quick Calculator and Full Benchmark Report. | /assets/share/og-benchmark.png (1200x630) | WebPage; Organization; Person; WebSite (@graph) |
| steve | /steve/ | Steve Dillberg, restaurant accountant and advisor, Schofer Dillberg & Company, Full Plate Intelligence founder | Steve Dillberg \| Founder of Full Plate Intelligence | Meet Steve Dillberg, restaurant accountant and advisor, founder of Full Plate Intelligence and founding partner of Schofer Dillberg & Company, with more than 25 years advising restaurant owners and operators. | /assets/share/og-steve.png (1200x630) | ProfilePage with mainEntity -> Person (#person); Organization; WebSite |
| privacy | /privacy/ | (utility page) | Privacy Policy \| Full Plate Intelligence | How Full Plate Intelligence collects and uses your email address and what happens when you join the Full Plate Weekly list. | /assets/share/og-home.png (1200x630) | WebPage; Organization; Person; WebSite (@graph) |
| terms | /terms/ | (utility page) | Terms of Use \| Full Plate Intelligence | Terms of use for the Full Plate Intelligence website and Full Plate Weekly newsletter. | /assets/share/og-home.png (1200x630) | WebPage; Organization; Person; WebSite (@graph) |
| contact | /contact/ | (utility page) | Contact \| Full Plate Intelligence | Questions, feedback or ideas for Full Plate Intelligence? Email Steve directly. | /assets/share/og-home.png (1200x630) | WebPage; Organization; Person; WebSite (@graph) |

## Old route -> new URL (client-side allowlist in `assets/js/site.js`; fragments never reach the server)

| Legacy hash | New URL |
|---|---|
| `#/show` | `/show/` |
| `#/weekly` | `/weekly/` |
| `#/index` | `/restaurant-intelligence-index/` |
| `#/benchmark` | `/benchmark/` |
| `#/steve` | `/steve/` |
| `#/privacy` | `/privacy/` |
| `#/terms` | `/terms/` |
| `#/contact` | `/contact/` |
| `#/home` | `/` |

Section anchors (`#signup`, `#ecosystem`, `#show-join`, `#weekly-join`, `#index-join`, `#benchmark-join`, `#signup-steve`) are preserved. A legacy hash with tracking appended (`#/index?utm_source=x`) is migrated with the tracking kept. Without JavaScript a legacy hash link shows the homepage (documented limitation).

## Not in the sitemap / noindex

- `/subscribe/thanks/` and `/subscribe/error/` (no-JavaScript form results): `noindex, nofollow`, also disallowed in robots.txt.
- `/404.html`: noindex; served with a real 404 status for unknown paths.
- `/api/subscribe`: POST only (`config.method` in the Netlify function); a GET is rejected by the platform before the handler runs — observe the actual deployed response (runbook §4.3).

## Founder discoverability

Visible text on /steve/: `Steve Dillberg. Founder of Full Plate Intelligence and founding partner of Schofer Dillberg & Company.` plus the existing biography. Person JSON-LD uses `name: Steve Dillberg`, `affiliation: Schofer Dillberg & Company` (no credential; owner instruction). No SDC link is rendered because no verified URL was supplied (`site.config.json: sdc_url`). No bookkeeping-service wording was added.

## AI-search note

Discoverability by AI answer engines relies on the same crawlable HTML, clear titles, descriptive body copy and structured data above; no separate speculative work was done.
