# Strategic HealthCare BI Analyst — Portfolio

Source for the Strategic HealthCare BI Analyst portfolio site, built as a
multi-page static site (no build step, no framework) and served via
GitHub Pages.

## Pages

| Page | File | Purpose |
|---|---|---|
| Home | `index.html` | Hero, three-pillar summary, one featured project |
| About | `about.html` | Background and how you work |
| Approach | `approach.html` | The four-step process behind every project |
| Certifications | `certifications.html` | Credentials — currently template placeholders |
| Projects | `projects.html` | Full project list |
| Case Studies | `case-studies.html` | In-depth problem → approach → result write-ups |
| Blog | `blog.html` | Placeholder — planned topics, no posts yet |
| Contact | `contact.html` | Email, phone, LinkedIn, GitHub |

Every page shares the same header, nav, and footer for consistency —
see `build_site.py` for how they're generated (that script is an
authoring convenience only; it isn't needed to run or deploy the site).

## Structure

```
.
├── index.html, about.html, approach.html, certifications.html,
│   projects.html, case-studies.html, blog.html, contact.html
├── style.css        # all styling, shared across pages
├── build_site.py    # generates the .html files above (optional to keep)
├── assets/
│   └── logo.png      # transparent brand logo
└── README.md
```

## Before you publish — things to edit

1. ✅ **Repository links** — already wired to
   `https://github.com/sohail5993/Strategic-HealthCare-Analyst`
   throughout, and the results links point to your live Pages site at
   `https://sohail5993.github.io/Strategic-HealthCare-Analyst/`.
2. ✅ **About page** — filled in with Sohail Bashir Butt's real bio (10+ years
   experience, cross-functional BI/data science/strategy/healthcare background).
3. ✅ **Certifications page** — all 26 verified credentials, grouped into four
   categories (Healthcare & Life Sciences; Data, Analytics & BI Platforms;
   Strategy & Business Analytics; Delivery, Governance & Professional
   Development), each with issuer, year, a healthcare-relevance blurb, and a
   live verification link.
4. **Placeholder projects/case studies** — the second and third
   project entries and the "coming soon" case-study note are there to
   show the site scales; replace or remove as you build more projects.

Email, phone, and LinkedIn are already filled in with the details you
provided.

**Note on the readmission project repo:** the live site at
`sohail5993.github.io/Strategic-HealthCare-Analyst` currently shows a
simplified version (chart images and a CSV at the repo root, with your
own README) rather than the fuller package originally put together
(which included the one-pager PDF, logo, and a nested `outputs/`
folder). That's completely fine as-is — the portfolio's links point to
the live results page itself rather than a specific PDF path, so
nothing will 404. If you'd like the one-pager PDF linkable directly
later, push it into that repo and I can point the link straight at it
instead.

## Adding a new project or case study later

- **Projects list**: copy one `<article class="project">...</article>`
  block in `projects.html` (and optionally `index.html`'s featured
  section), following the existing pattern — category tag with a color
  from the logo's arc, title, one paragraph, up to three stats, links.
- **Case study**: copy the `<section class="case-study">...</section>`
  block in `case-studies.html` and follow the Problem / Approach /
  Result structure.
- **Certifications**: don't hand-edit `certifications.html` — it's
  generated from the `CERTIFICATIONS` list near the top of
  `build_site.py`. Add a new dict (`name`, `issuer`, `year`, `link`,
  `blurb`) to the relevant category, or add a new category block
  entirely, then regenerate.

If you're using `build_site.py`, add new content there instead and
regenerate (`python3 build_site.py`) so the shared header/nav/footer
stay in sync across every page automatically.

## Running locally

No build step — just open `index.html` in a browser, or serve it:

```bash
python3 -m http.server 8000
```

then visit `http://localhost:8000`.

## Deploying (GitHub Pages)

1. Push this repo to GitHub as `strategic-healthcare-analyst-portfolio`
   (or any name you like — see note below on custom domains).
2. In the repo, go to **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **Deploy from a branch**.
4. Branch: `main`, folder: `/ (root)`. Save.
5. GitHub will publish the site at:
   `https://YOUR-USERNAME.github.io/strategic-healthcare-analyst-portfolio/`

**Note:** if you name the repo exactly `YOUR-USERNAME.github.io`, GitHub
Pages will publish it at your bare `https://YOUR-USERNAME.github.io/`
instead — the cleaner URL for a primary portfolio site, if you don't
plan to host anything else there.
