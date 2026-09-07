"""Targeted copy changes for FPI_SUBSCRIBER_LAUNCH_RC1.

Every entry is (page, original, replacement, reason, approval) and is applied as an exact-match
replacement (the build fails loudly if an original string is not found exactly once), so the
record below is also the source for COPY_CHANGES.md. `approval` names a factual claim that still
needs the owner's confirmation; None means the change is editorial and needs no sign-off.
"""

EDITS = [
    # ------------------------------------------------------------------ HOME
    ('home', 'Join restaurant owners and operators.',
             'For independent restaurant owners.',
     'Prelaunch: nobody has joined yet, so the note now states who the newsletter is for instead of implying an existing audience.', None),
    ('home', '<p class="micro">Free forever. One email a week. No fluff.</p>',
             '<p class="micro" id="signup-help">{weekly_hero_help}</p>',
     'States the immediate value and what happens after signup (confirmation email, then the newsletter), driven by the launch-state configuration.', None),
    ('home', "<span><b>PROFIT</b>What's left to grow your business</span>",
             '<span><b>PROFIT</b>What remains after these costs</span>',
     'Profit is not automatically cash available to grow the business; neutral wording per the restaurant-finance credibility review.', None),
    ('home', '      Turn numbers into <span>better decisions.</span></p>',
             '      Turn numbers into <span>better decisions.</span></p>\n    <p class="plate-disclaimer">Illustrative example, not an industry benchmark. Actual costs and profit vary. Percentages are shares of sales using simplified categories.</p>',
     'Visible qualifier for the illustrative cost breakdown (percentages total 100% but are not a sourced benchmark).', None),
    ('home', '<p>Upload your numbers. Instantly benchmark against similar restaurants by revenue, concept, and location. See where you stand and where to improve.</p>',
             '<p>Compare your numbers with similar restaurants by revenue, concept, and location. See where you stand and where to improve. Paid tools, in development.</p>',
     'Removes the "instantly" claim for an unbuilt tool and states that Benchmark tools will be paid.', None),
    ('home', '<p>A twice-yearly snapshot of key financial metrics, cost trends, and operator sentiment across independent restaurants, so you can see where the industry stands.</p>',
             '<p>A twice-yearly snapshot of key financial metrics, cost trends, and operator sentiment across independent restaurants, so you can see where the industry stands. Paid, per edition.</p>',
     'States the commercial model of the Index on the homepage card.', None),
    ('home', '<h3>Trusted by restaurant owners because:</h3>',
             '<h3>Built for restaurant owners:</h3>',
     'No subscribers or clients of Full Plate Intelligence exist yet to substantiate "trusted by"; keeps the section without fabricated social proof.', None),
    ('home', "<span>We're in your corner: operators helping operators.</span>",
             "<span>We're in your corner: restaurant-focused advice, built around operators.</span>",
     'Replaces "operators helping operators" with supported language (advisory background, not operating experience).', 'Steve to confirm whether he has direct restaurant-operating experience; if so the original line can return.'),
    ('home', '<span>Your data is protected and never sold.</span>',
             '<span>Your information is protected and never sold.</span>',
     'Only an email address is collected in this release; wording no longer implies financial-data handling.', None),

    # ------------------------------------------------------------------ SHOW
    ('show', '<p class="body">Every episode is a sit-down with owners, chefs, operators, investors, lenders, technologists, and the specialists they lean on.</p>',
             '<p class="body">Each episode will be a sit-down with owners, chefs, operators, investors, lenders, technologists, and the specialists they lean on.</p>',
     'Future tense: no episodes have been published.', None),
    ('show', '<p class="body">Every conversation ends with something you can <u>act on</u>, not just something to think about.</p>',
             '<p class="body">Every conversation will end with something you can <u>act on</u>, not just something to think about.</p>',
     'Future tense: no episodes have been published.', None),

    # ------------------------------------------------------------------ INDEX
    ('index', 'Real operating data from independent restaurants, read by someone who has run them.',
              'Real operating data from independent restaurants, interpreted through more than 25 years of advising restaurant owners and operators.',
     'The supported biography is advisory (CPA and advisor), not restaurant operation.', 'Steve to confirm whether he has run a restaurant; if so "read by someone who has run them" may return.'),
    ('index', '<p class="paid-note"><span class="pill">PAID REPORT</span> Purchased per edition. Early-access subscribers hear first.</p>',
              '<p class="paid-note"><span class="pill">PAID REPORT</span> Purchased per edition when published. The early-access list gets launch updates first.</p>',
     'Clarifies that the report is bought separately and that the list only provides updates.', None),
    ('index', '<button class="rii-btn rii-btn-primary" type="button" data-scroll="index-join">GET EARLY ACCESS</button>',
              '<button class="rii-btn rii-btn-primary" type="button" data-scroll="index-join" data-interest="index">JOIN THE EARLY-ACCESS LIST</button>',
     'Truthful CTA: signing up joins a list; it does not grant report access.', None),
    ('index', '<p class="rii-micro">A paid report, published twice a year for independent restaurant operators. Early access opens through the list below.</p>',
              '<p class="rii-micro">A paid report, published twice a year for independent restaurant operators. Join the list below for launch updates.</p>',
     'Separates list membership from purchase.', None),
    ('index', '<p class="rii-lead">Each edition follows the same structure, so you can track what has moved from one report to the next.</p>',
              '<p class="rii-lead">Each edition will follow the same structure, so you can track what has moved from one report to the next.</p>',
     'Future tense for an unpublished report.', None),
    ('index', '<p class="rii-lead">A disciplined research line: real operating data goes in, individual restaurants stay protected, and experience turns the patterns into something you can use.</p>',
              '<p class="rii-lead">The planned research line: real operating data goes in, individual restaurants stay protected, and experience turns the patterns into something you can use.</p>',
     'Describes the intended process explicitly as planned.', None),
    ('index', '<h3>Anonymized</h3><p>Identifiers are removed. No individual restaurant is ever named or recognizable.</p>',
              '<h3>Anonymized</h3><p>Identifiers are removed before analysis. No individual restaurant is named, and results are reported only in aggregate.</p>',
     'Replaces an absolute guarantee ("never recognizable") with the concrete safeguards intended.', 'Owner/legal: confirm the anonymization and aggregation standard before data collection opens.'),
    ('index', '<p>The Index reports patterns across many restaurants, never the position of any one of them. Contributed data is used only to build the Index.</p>',
              '<p>The Index will report patterns across many restaurants, not the position of any one of them. How contributed data may be used, including any use across other Full Plate Intelligence products, will be set out in the participation terms before any data is collected.</p>',
     'The "used only to build the Index" promise conflicts with possible cross-product use (Benchmark); consent scope must be decided, not silently broadened.', 'Steve/legal: decide the permitted uses of contributed data and whether SDC client information may ever be included.'),
    ('index', '<h2>Intelligence Index coming soon.',
              '<h2>Intelligence Index coming soon.',
     'Unchanged (listed for completeness).', None),
    ('index', '<br>Get <span class="free">early access</span> through Full Plate Weekly.</h2>',
              '<br>Join the <span class="free">early-access list</span> through Full Plate Weekly.</h2>',
     'Signup joins a list; it does not grant access to a report.', None),
    ('index', '<button class="rii-btn rii-btn-primary" type="submit">GET EARLY ACCESS</button>',
              '<button class="rii-btn rii-btn-primary" type="submit">GET LAUNCH UPDATES</button>',
     'Truthful CTA label.', None),

    # ------------------------------------------------------------------ BENCHMARK
    ('benchmark', 'Full Plate Benchmark matches your restaurant with the right peers and turns your numbers into <u>actions</u>.',
                  'Full Plate Benchmark is being built to match your restaurant with the right peers and turn your numbers into <u>actions</u>.',
     'Prelaunch: the tool does not exist yet.', None),
    ('benchmark', 'Both the Quick Calculator and the Full Benchmark Report are paid tools.',
                  'Both the Quick Calculator and the Full Benchmark Report will be paid tools.',
     'Future tense; prices are not set.', None),
    ('benchmark', '<li>Get an instant performance snapshot</li>',
                  '<li>Get a quick performance snapshot</li>',
     'No verified real-time output exists.', None),
    ('benchmark', '<li>No sign-up required</li>',
                  '<li>Built for a fast first look</li>',
     'Misleading next to a paid tag and an email-signup action.', None),
    ('benchmark', '<button class="bm-btn bm-btn-quiet" type="button" data-scroll="benchmark-join">Try the Calculator</button>',
                  '<button class="bm-btn bm-btn-quiet" type="button" data-scroll="benchmark-join" data-interest="benchmark-calculator">Notify Me About the Calculator</button>',
     'The control scrolls to a signup form; label now says so. Interest is captured before scrolling.', None),
    ('benchmark', '<button class="bm-btn bm-btn-primary" type="button" data-scroll="benchmark-join">Get Your Benchmark Report</button>',
                  '<button class="bm-btn bm-btn-primary" type="button" data-scroll="benchmark-join" data-interest="benchmark-report">Notify Me About the Benchmark Report</button>',
     'Same as above for the report.', None),
    ('benchmark', '<h2 class="bm-h2">How Full Plate Benchmark works</h2>',
                  '<h2 class="bm-h2">How Full Plate Benchmark will work</h2>',
     'Planned functionality stated explicitly.', None),
    ('benchmark', '<p>Our AI maps your chart of accounts to our standard framework.</p>',
                  '<p>Your chart of accounts will be mapped to our standard framework, with a review step before anything is scored.</p>',
     'Removes a present-tense AI claim that cannot be verified.', 'Steve to confirm the intended mapping method (automated, reviewed, or both).'),
    ('benchmark', '<p>AI-powered insights and operator actions you can implement today.</p>',
                  '<p>Clear insights and operator actions you can put to work.</p>',
     'Removes an unsupported present-tense AI claim.', None),
    ('benchmark', '<h2 class="bm-h2">Your data is safe</h2>',
                  '<h2 class="bm-h2">How your data will be protected</h2>',
     'Planned safeguards, not a present guarantee; uploads are not open.', None),
    ('benchmark', '<p class="bm-safe-note">Secure. Anonymized. Never shared.</p>',
                  '<p class="bm-safe-note">Planned safeguards. Financial uploads are not open yet.</p>',
     'States the prelaunch fact plainly.', None),
    ('benchmark', '<p>Upload your P&amp;L and chart of accounts through our secure portal.</p>',
                  '<p>You will upload your P&amp;L and chart of accounts through an encrypted portal, once Benchmark opens.</p>',
     'Future tense; no portal exists.', None),
    ('benchmark', '<p>Your data is encrypted using bank-level protocols during transmission.</p>',
                  '<p>Data will be encrypted in transit (TLS) and at rest.</p>',
     '"Bank-level" is unsubstantiated marketing language; concrete, checkable wording instead.', None),
    ('benchmark', '<p>We remove identifiers and sensitive data so your identity is never known.</p>',
                  '<p>Identifying details will be separated from your financial data before analysis.</p>',
     'Replaces an absolute claim with the intended safeguard.', 'Owner/legal: confirm the de-identification standard.'),
    ('benchmark', '<p>Your data is combined with thousands of other restaurants to create powerful insights.</p>',
                  '<p>Peer comparisons will be built from aggregated data across participating restaurants, not from any single restaurant.</p>',
     'No dataset of "thousands" exists.', None),
    ('benchmark', '<p>You receive benchmarks and scores built on anonymous, aggregate comparisons.</p>',
                  '<p>You will receive benchmarks and scores built on aggregate comparisons.</p>',
     'Future tense.', None),
    ('benchmark', '<p>Your individual data is never sold, shared, or used for any other purpose.</p>',
                  '<p>Your individual data will not be sold. Permitted uses, including any contribution to aggregate research, will be stated in the participation terms you accept before uploading.</p>',
     'Absolute "never shared / any other purpose" conflicts with aggregate use; consent scope to be decided.', 'Steve/legal: define permitted uses of uploaded financial data.'),
    ('benchmark', '<li>Private</li><li>Secure</li><li>Anonymized</li><li>Aggregated</li><li>Never shared</li>',
                  '<li>Private</li><li>Encrypted</li><li>De-identified</li><li>Aggregated</li><li>Not sold</li>',
     'Matches the revised safeguards.', None),
    ('benchmark', '<br>Get <span class="free">early access</span> through Full Plate Weekly.</h2>',
                  '<br>Get <span class="free">launch updates</span> through Full Plate Weekly.</h2>',
     'Signup provides updates, not access.', None),

    # ------------------------------------------------------------------ STEVE
    ('steve', '<h2>Join restaurant owners who rely on <span class="free">Full Plate Weekly</span>',
              '<h2>Join <span class="free">Full Plate Weekly</span> for practical restaurant financial insights.',
     'No one relies on an unpublished newsletter; prospective wording.', None),
    ('steve', '<br>for actionable insights every week.</h2>',
              '<br>Free to subscribe.</h2>',
     'Completes the prospective CTA.', None),
    ('steve', '<p class="ms-tag">Every restaurant has a story.<br><span class="ms-tag-u">The numbers simply tell it.</span></p>',
              '<p class="ms-identity">Steve Dillberg. Founder of Full Plate Intelligence and founding partner of Schofer Dillberg &amp; Company.</p>\n        <p class="ms-tag">Every restaurant has a story.<br><span class="ms-tag-u">The numbers simply tell it.</span></p>',
     'Visible founder identity line in real text for discoverability (name and both roles). RC5: owner instruction 2026-09-07: no "Steven", no quoted nickname, no CPA credential (Steve is not a CPA).', None),
    # ------------------------------------------------------------------ RC4/RC5 owner-directed product wording (2026-09-07)
    ('index', '<p class="paid-note"><span class="pill">PAID REPORT</span> Purchased per edition when published. The early-access list gets launch updates first.</p>',
              '<p class="paid-note"><span class="pill">PREMIUM RESEARCH REPORT</span> Available for individual purchase with each twice-yearly edition. Join the early-access list for launch details and first access.</p>',
     'Owner wording: the pill describes the product, not the checkout process.', None),
    ('benchmark', '<p class="paid-note"><span class="pill">PAID PRODUCT</span> Both the Quick Calculator and the Full Benchmark Report will be paid tools.</p>',
                  '<p class="paid-note"><span class="pill">BENCHMARKING MEMBERSHIP</span> Paid, per-location benchmarking with options ranging from a quick performance snapshot to ongoing monthly reporting. Join the early-access list for launch details and founding-member access.</p>',
     'Owner wording: the pill describes the product, not the checkout process.', None),
    ('benchmark', '<p class="bm-product-sub">A fast gut-check. <span class="pill">PAID</span></p>',
                  '<p class="bm-product-sub">A fast gut-check. <span class="pill">BENCHMARKING MEMBERSHIP</span></p>',
     'Owner wording (product-card pill).', None),
    ('benchmark', '<p class="bm-product-sub">In-depth analysis. Action-oriented insight. <span class="pill">PAID</span></p>',
                  '<p class="bm-product-sub">In-depth analysis. Action-oriented insight. <span class="pill">BENCHMARKING MEMBERSHIP</span></p>',
     'Owner wording (product-card pill).', None),
    # ------------------------------------------------------------------ REVIEW PASS (present-tense and absolute claims)
    ('index', '<p>Every edition combines restaurant operating data with more than 25 years of experience working alongside restaurant owners and operators.</p>',
              '<p>Every edition will combine restaurant operating data with more than 25 years of experience working alongside restaurant owners and operators.</p>',
     'Future tense for an unpublished report.', None),
    ('index', 'Each edition shows what is changing across the industry, why it matters, and what deserves your attention next.',
              'Each edition will show what is changing across the industry, why it matters, and what deserves your attention next.',
     'Future tense for an unpublished report.', None),
    ('index', '<h2>Numbers, not anecdotes</h2><p>Built from the operating data of independent restaurants, so you see what the industry is actually doing.</p>',
              '<h2>Numbers, not anecdotes</h2><p>To be built from the operating data of independent restaurants, so you see what the industry is actually doing.</p>',
     'Planned functionality stated explicitly.', None),
    ('benchmark', '<p>Our model goes beyond averages to show what actually drives performance.</p>',
                  '<p>Our model is designed to go beyond averages and show what actually drives performance.</p>',
     'Present-tense claim about an unbuilt model.', None),
    ('benchmark', '<h3>Never Shared</h3>', '<h3>Not Sold</h3>',
     'Heading matched the removed absolute guarantee; aligned with the revised body text.', None),
    ('benchmark', '<h3>You own your data. <span class="bm-own-accent">We protect it.</span></h3>',
                  '<h3>You own your data. <span class="bm-own-accent">We will protect it.</span></h3>',
     'Planned safeguard, not a present guarantee.', None),
    ('weekly', 'Straight talk. Real numbers. Actionable insights you can use right now to build a stronger restaurant.',
               'Straight talk. Real numbers. Actionable insights you can use to build a stronger restaurant.',
     '"Right now" implies the newsletter is already sending.', None),
    ('weekly', '<p>Every issue is written with one goal: help you make <u>better decisions</u>.</p>',
               '<p>Every issue will be written with one goal: help you make <u>better decisions</u>.</p>',
     'Future tense for an unpublished newsletter.', None),
    ('home', '<span>Your information is protected and never sold.</span>', '<span>Your information is protected and not sold.</span>',
     'Matches the privacy policy wording ("do not sell") without an absolute "never".', None),
]

# Copy that depends on the launch-state configuration (site.config.json -> launch.weekly).
STATE_COPY = {
    'coming_soon': {
        'weekly_hero_help': 'Free. Confirm your email and you are on the list; Full Plate Weekly starts sending when the first issue is ready. One short email a week, no fluff.',
        'weekly_pill': 'COMING SOON',
        'thanks_generic': 'Thanks. If this address is new to our list, a confirmation email is on its way.',
        'thanks_help': 'Already subscribed? You are all set. Unsubscribed before? Email Steve@FullPlateIntel.com to rejoin.',
        'thanks_pending': 'Almost there. Check your inbox for a confirmation email and click the link to finish signing up.',
        'thanks_subscribed': 'You are on the list. Full Plate Weekly will arrive when the first issue is ready.',
    },
    'live': {
        'weekly_hero_help': 'Free. Confirm your email and your first Full Plate Weekly follows. One short email a week, no fluff.',
        'weekly_pill': 'FREE',
        'thanks_generic': 'Thanks. If this address is new to our list, a confirmation email is on its way.',
        'thanks_help': 'Already subscribed? You are all set. Unsubscribed before? Email Steve@FullPlateIntel.com to rejoin.',
        'thanks_pending': 'Almost there. Check your inbox for a confirmation email and click the link to finish signing up.',
        'thanks_subscribed': 'You are on the list. Watch for your first issue of Full Plate Weekly.',
    },
}

# Form-adjacent helper text per signup placement (all seven), keyed by data-source.
FORM_HELP = {
    'homepage-hero':       None,   # the hero already carries #signup-help
    'homepage-bottom-cta': 'Free newsletter. We will send a confirmation email first. Unsubscribe anytime.',
    'show-page':           'Joins the free Full Plate Weekly newsletter; you will hear about the show when it launches. Unsubscribe anytime.',
    'weekly-page-bottom':  'Free newsletter. We will send a confirmation email first. Unsubscribe anytime.',
    'index-page':          'Joins the free Full Plate Weekly newsletter for Index launch updates. Each edition is purchased separately when available.',
    'benchmark-page':      'Joins the free Full Plate Weekly newsletter for launch updates. The Benchmark tools themselves will be paid.',
    'steve-page':          'Free newsletter. We will send a confirmation email first. Unsubscribe anytime.',
}


def apply(pages, launch):
    """pages: dict page-id -> html. Returns (pages, applied_records)."""
    state = STATE_COPY[launch['weekly']]
    out = dict(pages)
    records = []
    for page, old, new, reason, approval in EDITS:
        new = new.format(**state) if '{' in new else new
        n = out[page].count(old)
        if n != 1:
            raise SystemExit(f'copy edit not applied exactly once ({n}x) on {page}: {old[:80]}')
        out[page] = out[page].replace(old, new)
        records.append({'page': page, 'original': old, 'replacement': new, 'reason': reason, 'approval': approval})
    return out, records
