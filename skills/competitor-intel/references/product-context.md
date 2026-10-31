# Getting our product's context, and checking gaps against it

Work with whatever the user has. The source the user gives is the truth for "what we have". Never use memory, and never use the research agents' claims.

## 1. Pick the input mode (more than one can apply)
| The user gives | How to read it | Evidence format for the gap check |
|---|---|---|
| **An idea only** (a sentence, a paragraph, notes; nothing built yet) | Restate it as a one-line product, a buyer and a problem. Ask ONE batch of up to 3 questions only if the market or buyer is unclear. List the planned capabilities from their words. | A quote from the user's description, e.g. "idea: 'patients book on WhatsApp'" |
| **A website URL** (product, landing page or company site) | Fetch the home, features, pricing, docs/help and changelog pages. Note claims versus shown screens. | URL plus the section heading |
| **App store / Product Hunt link** | Listing text, screenshots, release notes, rating and reviews (reviews of our own product are gold) | Listing URL |
| **Deck, PRD, spec or doc** (file or link) | Read the features, roadmap and pricing sections | File name plus page or section |
| **Code repos** | README and module overview docs. **List the module or folder names first**, since they reveal features a grep misses. Then grep, excluding tests. | `path:line`, or "grep 'x' = 0 hits" |
| **Live app or demo login** | Walk each main screen and take screenshots | Screen name plus screenshot |
| **Nothing but a category** ("a CRM for dentists") | Treat it as idea mode and say so in the assumptions | "category only" |

If sources disagree (the site claims a feature the code lacks), the stronger evidence wins: code or live app > docs > website > idea. Note the conflict in the callout.

## 2. Brief template (15 lines or fewer, handed to the research agents)
- Product line (one line), stage (idea / pre-launch / live), market or geography, buyer.
- One line per module or area: what it does or will do.
- Platform, pricing model, channels (only if known).

## 3. Journey and capabilities for the page
- **Stages:** 5–8 steps of the customer journey in the buyer's own language. A SaaS example is Discover → Evaluate → Onboard → Use → Pay → Retain. A clinic example is Enquiry → Booking → Arrival → Consult → Checkout → Pharmacy → Retention.
- **Capabilities:** 20–45 items across the stages. Include ours, and the ones competitors have that we lack.

## 4. Gap check: what the statuses mean in each mode
| Status | Built product (code, app, site) | Idea / pre-launch |
|---|---|---|
| Already built / Built | Works end to end | In the stated MVP scope |
| Partial | Modelled or queued but not delivered, or a manual workaround exists | Mentioned as "later" or only vaguely |
| Missing | No relevant evidence | Not mentioned anywhere |

For idea mode, set `meta.json` `subtitle` to say "status = in your plan", so readers don't take the ring as shipped features.

## False positives to rule out (from the Clinozy worked example)
- A keyword can mean something else: `membership` meant staff membership, and `Wallet` was only an icon name.
- **Queued-but-not-delivered**: an outbox or integration flag exists, but nothing sends. This reads as built and is not. In the Clinozy run, WhatsApp delivery was exactly this case.
- Marketing pages claim "coming soon" features. Mark those Partial, not Built.

## Running a product locally (optional, for screenshots)
Follow its setup doc and check the exact runtime versions. In cloud sandboxes, registries may be blocked or rate-limited. Try at most 2 alternatives, then fall back to docs, site or code, and say so in the report.
