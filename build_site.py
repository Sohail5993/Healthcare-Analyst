"""
Generates the multi-page static site from shared header/nav/footer + per-page
content. Output is plain .html files with no JS/build dependency at runtime —
this script is just an authoring convenience, not part of the shipped site.
"""
import os

OUT_DIR = "/home/claude/portfolio_site"

NAV_ITEMS = [
    ("index.html", "Home"),
    ("about.html", "About"),
    ("approach.html", "Approach"),
    ("certifications.html", "Certifications"),
    ("projects.html", "Projects"),
    ("case-studies.html", "Case Studies"),
    ("blog.html", "Blog"),
    ("contact.html", "Contact"),
]

def render_nav(active_page):
    links = []
    for href, label in NAV_ITEMS:
        cls = "nav-link active" if href == active_page else "nav-link"
        links.append(f'<a href="{href}" class="{cls}">{label}</a>')
    return "\n        ".join(links)

PAGE_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Strategic HealthCare BI Analyst</title>
<meta name="description" content="{description}">
<link rel="icon" type="image/png" href="assets/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>

  <header class="site-header">
    <div class="wrap header-inner">
      <a href="index.html" class="brand-link">
        <img src="assets/logo.png" alt="Strategic HealthCare BI Analyst logo" class="brand-mark">
        <div class="brand-block">
          <span class="brand-name">Strategic HealthCare BI Analyst</span>
          <span class="brand-tagline">Transforming HealthCare Complexities into Growth Blueprints</span>
        </div>
      </a>
    </div>
    <nav class="site-nav">
      <div class="wrap nav-inner">
        {nav}
      </div>
    </nav>
  </header>

  <main>
"""

PAGE_FOOT = """
  </main>

  <footer class="site-footer wrap">
    <div class="footer-row">
      <span>Strategic HealthCare BI Analyst</span>
      <div class="footer-links">
        <a href="mailto:strategichealthcarebianalyst@gmail.com">Email</a>
        <a href="tel:+923004984892">Phone</a>
        <a href="https://www.linkedin.com/in/aimms-consulting-35895439">LinkedIn</a>
        <a href="https://github.com/sohail5993">GitHub</a>
      </div>
    </div>
  </footer>

</body>
</html>
"""

def write_page(filename, title, description, body_html):
    html = PAGE_HEAD.format(title=title, description=description, nav=render_nav(filename)) \
           + body_html + PAGE_FOOT
    path = os.path.join(OUT_DIR, filename)
    with open(path, "w") as f:
        f.write(html)
    print(f"wrote {path}")


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------
write_page(
    "index.html",
    "Home",
    "Healthcare data science portfolio — turning clinical, operational, and claims data into decisions hospitals can act on.",
    """
    <section class="hero wrap">
      <h1>I turn messy hospital data into decisions someone can act on Monday morning.</h1>
      <p class="lede">
        Every project here starts with a question a hospital actually pays to answer —
        readmissions, cost overruns, care-quality gaps — and works it through end to end:
        the data, the model, why it can be trusted, and what it's worth in dollars.
      </p>
    </section>

    <section class="pillars wrap">
      <div class="pillar">
        <div class="pillar-rule" style="background:#0F5C5C;"></div>
        <div class="pillar-body">
          <h3>Analytics &amp; Modeling</h3>
          <p>Predictive risk models built on real clinical and claims features, validated the way a hospital's own quality team would validate them.</p>
        </div>
      </div>
      <div class="pillar">
        <div class="pillar-rule" style="background:#C96F14;"></div>
        <div class="pillar-body">
          <h3>Strategic Translation</h3>
          <p>Every model ends in a dollar figure and an operational recommendation — not just an AUC score nobody outside the data team can use.</p>
        </div>
      </div>
      <div class="pillar">
        <div class="pillar-rule" style="background:#6C3483;"></div>
        <div class="pillar-body">
          <h3>Healthcare Domain Depth</h3>
          <p>Built around the real constraints hospitals operate under — HRRP penalties, care-management capacity, and what clinicians will actually trust.</p>
        </div>
      </div>
    </section>

    <section class="featured wrap">
      <h2>Featured work</h2>
      <article class="project">
        <div class="project-rule" style="background:#0F5C5C;"></div>
        <div class="project-body">
          <div class="project-head">
            <span class="tag" style="color:#0F5C5C; border-color:#0F5C5C;">Cost &amp; Quality</span>
            <h3>Hospital 30-Day Readmission Prediction</h3>
          </div>
          <p>Flagging the patients most likely to be readmitted within 30 days, so a limited-capacity care-management program targets the people who need it most.</p>
          <div class="stat-row">
            <div class="stat"><span class="stat-num">0.67</span><span class="stat-label">ROC-AUC</span></div>
            <div class="stat"><span class="stat-num">2x</span><span class="stat-label">precision lift, top 10% risk</span></div>
            <div class="stat"><span class="stat-num">$918K</span><span class="stat-label">est. annual net savings</span></div>
          </div>
          <div class="project-links">
            <a href="case-studies.html">Read the case study</a>
            <a href="https://github.com/sohail5993/Strategic-HealthCare-BI-Analyst/tree/main/hospital-readmission-prediction">View repository</a>
          </div>
        </div>
      </article>
      <p class="see-all"><a href="projects.html">See all projects →</a></p>
    </section>
    """
)

# ---------------------------------------------------------------------------
# ABOUT
# ---------------------------------------------------------------------------
write_page(
    "about.html",
    "About",
    "About Strategic HealthCare BI Analyst — background, focus, and how I work.",
    """
    <section class="page-header wrap">
      <h1>About</h1>
    </section>

    <section class="prose wrap">
      <p>
        I'm <strong>Sohail Bashir Butt</strong>, a Strategic HealthCare BI Analyst with
        <strong>10+ years of professional experience</strong> and a credentialed background
        spanning business intelligence platforms, data science, enterprise systems, and
        corporate strategy. My focus is healthcare: turning clinical, operational, and
        claims data into the kind of decisions a hospital finance or care-management leader
        can actually act on.
      </p>
      <p>
        That focus isn't just a specialization — it's backed by dedicated study across
        medical billing and coding, genomic data analysis, and pharmaceutical and medical
        device commercialization, layered on top of enterprise-grade credentials in BI
        platforms (Power BI, Tableau, Google Business Intelligence), data science (Google
        Data Analytics, Executive Data Science, Johns Hopkins' data science series), and
        systems delivery (SAP, Google Project Management, Google Cybersecurity). The
        combination is deliberate: healthcare analytics fails when it's only technical or
        only strategic — it has to be both.
      </p>
      <p>
        What I care about isn't the model — it's whether a hospital can act on it.
        A 0.90 AUC that nobody trusts is worth less than a 0.68 AUC that a care-management
        team actually uses. That's the standard every project on this site is held to.
      </p>

      <h2>How I work</h2>
      <ul class="prose-list">
        <li>Start from the business question, not the dataset — the model serves the decision, not the other way around.</li>
        <li>Report honest performance ceilings, not inflated metrics — healthcare stakeholders can tell the difference, and trust is the whole point.</li>
        <li>Every deliverable ends with a number a finance or operations leader can act on.</li>
      </ul>

      <h2>Background</h2>
      <p>
        Over 10+ years, I've built a deliberately cross-functional foundation —
        strategic management and decision science from Wharton and Copenhagen Business
        School, applied data science from Johns Hopkins, enterprise BI and cybersecurity
        from Google, SAP, and Microsoft, and healthcare-specific grounding in billing,
        genomics, and med-device commercialization. The full list, with verification links,
        is on the <a href="certifications.html">Certifications</a> page.
      </p>
    </section>
    """
)

# ---------------------------------------------------------------------------
# APPROACH
# ---------------------------------------------------------------------------
write_page(
    "approach.html",
    "Approach",
    "The analytical approach behind every project — from business question to measurable impact.",
    """
    <section class="page-header wrap">
      <h1>Approach</h1>
      <p class="lede">The same four-step process runs through every project on this site.</p>
    </section>

    <section class="steps wrap">
      <div class="step">
        <div class="step-rule" style="background:#0F5C5C;"></div>
        <div class="step-body">
          <span class="step-num">01</span>
          <h3>Define the business question</h3>
          <p>Before any data is touched: what decision is this for, who makes it, and what does it cost to get it wrong? A readmission model is worthless without knowing what a hospital would actually do with a risk score.</p>
        </div>
      </div>
      <div class="step">
        <div class="step-rule" style="background:#C96F14;"></div>
        <div class="step-body">
          <span class="step-num">02</span>
          <h3>Engineer clinically-grounded features</h3>
          <p>Features come from how clinicians and care managers actually think about risk — prior utilization, discharge disposition, comorbidity burden — not just whatever columns happen to be in the file.</p>
        </div>
      </div>
      <div class="step">
        <div class="step-rule" style="background:#1E8A8A;"></div>
        <div class="step-body">
          <span class="step-num">03</span>
          <h3>Model, validate, and explain honestly</h3>
          <p>Multiple models compared on metrics that match the real operating constraint (precision at a realistic capacity, not just AUC), with SHAP explanations so a care team can see why a patient was flagged.</p>
        </div>
      </div>
      <div class="step">
        <div class="step-rule" style="background:#6FA82F;"></div>
        <div class="step-body">
          <span class="step-num">04</span>
          <h3>Translate to a business case</h3>
          <p>Every project ends the same way: a dollar figure, an ROI estimate, and an honest account of what would need to happen operationally to realize it.</p>
        </div>
      </div>
    </section>
    """
)

# ---------------------------------------------------------------------------
# CERTIFICATIONS
# ---------------------------------------------------------------------------
CERTIFICATIONS = [
    {
        "category": "Healthcare & Life Sciences",
        "color": "#0F5C5C",
        "items": [
            {
                "name": "Medical Billing and Coding Fundamentals",
                "issuer": "Coursera — MedCerts",
                "year": "2024",
                "link": "https://coursera.org/verify/specialization/LRSZ1A3W8B1O",
                "blurb": "ICD-10, CPT, and HCPCS classification systems alongside revenue cycle management — standardizing clinical diagnoses and procedure data for claims analysis, reimbursement modeling, and fraud detection.",
            },
            {
                "name": "Introduction to Genomic Technologies",
                "issuer": "Coursera — Johns Hopkins University",
                "year": "2017",
                "link": "https://www.coursera.org/account/accomplishments/verify/JK2DLNKD37YK",
                "blurb": "Computational molecular biology, high-throughput sequencing analysis, and genomic algorithms — enabling extraction and processing of genetic data to advance precision medicine and personalized care strategies.",
            },
            {
                "name": "Pharmaceutical and Medical Device Innovations",
                "issuer": "Coursera — University of Minnesota",
                "year": "2017",
                "link": "https://www.coursera.org/account/accomplishments/verify/F22U6KDZWSQV",
                "blurb": "The end-to-end commercialization lifecycle, FDA regulatory pathways, IP protection, and market access strategy — domain context for modeling drug performance and clinical technology adoption.",
            },
        ],
    },
    {
        "category": "Data, Analytics &amp; BI Platforms",
        "color": "#C96F14",
        "items": [
            {
                "name": "Google Data Analytics",
                "issuer": "Coursera — Google Career Certificate",
                "year": "2025",
                "link": "https://coursera.org/verify/professional-cert/Y5UV9UGQ26V9",
                "blurb": "The end-to-end analytical workflow from data cleaning and SQL querying to R programming and visualization — transforming complex electronic health records into clean, compliant, actionable insight.",
            },
            {
                "name": "Google Business Intelligence",
                "issuer": "Coursera — Google Career Certificate",
                "year": "2024",
                "link": "https://coursera.org/verify/professional-cert/B8F3U6D20QBW",
                "blurb": "Data modeling, ETL pipeline architecture, and dashboard development — unifying disparate hospital records and automating clinical KPI reporting for real-time decision-making.",
            },
            {
                "name": "Data Analytics For Lean Six Sigma",
                "issuer": "Coursera — University of Amsterdam",
                "year": "2017",
                "link": "https://www.coursera.org/account/accomplishments/verify/YYBCWL5HTJCM",
                "blurb": "Statistical hypothesis testing, regression analysis, and Minitab-driven process improvement under the Lean Six Sigma framework — root-causing inefficiencies in hospital workflows and clinical operations.",
            },
            {
                "name": "Microsoft Power BI Data Analyst",
                "issuer": "Coursera — Microsoft",
                "year": "2024",
                "link": "https://coursera.org/verify/professional-cert/8SAFXVFKMO5N",
                "blurb": "Advanced DAX metric engineering, semantic data modeling, and row-level security — secure executive dashboards tracking hospital operations and patient outcomes while safeguarding sensitive data.",
            },
            {
                "name": "Tableau BI Analyst",
                "issuer": "Coursera — Tableau",
                "year": "2024",
                "link": "https://coursera.org/verify/professional-cert/GN4PZ7VUSP3J",
                "blurb": "Advanced visual analytics, dynamic parameterization, and spatial plotting — turning epidemiological data and patient-flow patterns into intuitive visual stories for clinical leadership.",
            },
            {
                "name": "Executive Data Science Capstone",
                "issuer": "Coursera — Johns Hopkins University",
                "year": "2017",
                "link": "https://www.coursera.org/account/accomplishments/specialization/MALCTXT4K628",
                "blurb": "Leading end-to-end data science projects, pipeline governance, and executive storytelling — translating clinical models and statistical findings into strategic decisions for health system leaders.",
            },
            {
                "name": "A Crash Course in Data Science",
                "issuer": "Coursera — Johns Hopkins University",
                "year": "2017",
                "link": "https://www.coursera.org/account/accomplishments/verify/2ERV3HM5RYFU",
                "blurb": "Core principles of machine learning, statistical inference, and data science workflows — a practical foundation for evaluating clinical data methodologies against strategic goals.",
            },
            {
                "name": "Managing Data Analysis",
                "issuer": "Coursera — Johns Hopkins University",
                "year": "2017",
                "link": "https://www.coursera.org/account/accomplishments/verify/6HKZWGMXW8PE",
                "blurb": "Oversight of analytical workflows, statistical model iteration, and pipeline governance — quality-control frameworks that keep clinical analyses reproducible and compliant before they reach decision-makers.",
            },
            {
                "name": "Data Science in Real Life",
                "issuer": "Coursera — Johns Hopkins University",
                "year": "2017",
                "link": "https://www.coursera.org/account/accomplishments/verify/YZACWBZLEEYL",
                "blurb": "Managing messy datasets, unexpected pipeline disruptions, and applied statistical modeling — cleaning incomplete electronic health records and producing reliable insight under real-world conditions.",
            },
        ],
    },
    {
        "category": "Strategy &amp; Business Analytics",
        "color": "#6C3483",
        "items": [
            {
                "name": "Strategic Management",
                "issuer": "Coursera — Copenhagen Business School",
                "year": None,
                "link": "https://www.coursera.org/account/accomplishments/verify/BZV246U5373G",
                "blurb": "A framework for formulating and executing strategy under market volatility and digital disruption — the same lens applied to navigating shifting healthcare policy and payer dynamics.",
            },
            {
                "name": "Strategy Formulation",
                "issuer": "Coursera — Copenhagen Business School",
                "year": None,
                "link": "https://www.coursera.org/account/accomplishments/verify/7GEGT99XPYR5",
                "blurb": "Tools for identifying growth vectors and designing corporate strategy from market analysis through execution — applied to positioning analytics initiatives around real organizational value.",
            },
            {
                "name": "Decision-Making &amp; Scenarios",
                "issuer": "Coursera — University of Pennsylvania",
                "year": None,
                "link": "https://www.coursera.org/account/accomplishments/verify/YXH42AHE58CN",
                "blurb": "Financial modeling, scenario planning, and capital-budgeting methods for stress-testing decisions under uncertainty — the discipline behind turning a readmission model into a defensible ROI case.",
            },
            {
                "name": "Operations Analytics",
                "issuer": "Coursera — Wharton, University of Pennsylvania",
                "year": "2017",
                "link": "https://www.coursera.org/account/accomplishments/verify/FBACTTKB6BGN",
                "blurb": "Capacity planning, supply chain optimization, and demand forecasting — streamlining hospital bed management, clinical staffing schedules, and pharmaceutical inventory.",
            },
            {
                "name": "People Analytics",
                "issuer": "Coursera — Wharton, University of Pennsylvania",
                "year": "2017",
                "link": "https://www.coursera.org/account/accomplishments/verify/PES32EM9CADV",
                "blurb": "Workforce planning, performance modeling, and retention analytics — optimizing nurse-to-patient staffing ratios and reducing clinical burnout and turnover.",
            },
            {
                "name": "Customer Analytics",
                "issuer": "Coursera — Wharton, University of Pennsylvania",
                "year": "2017",
                "link": "https://www.coursera.org/account/accomplishments/verify/99F5R86ZCE6W",
                "blurb": "Patient segmentation, behavioral modeling, and satisfaction tracking — personalizing patient engagement and optimizing telehealth adoption strategies.",
            },
            {
                "name": "Accounting Analytics",
                "issuer": "Coursera — Wharton, University of Pennsylvania",
                "year": "2017",
                "link": "https://www.coursera.org/account/accomplishments/verify/CHMQ4EGHHZKU",
                "blurb": "Financial statement modeling, cost accounting, and revenue cycle analysis — optimizing hospital billing workflows and tracking cost-per-patient metrics.",
            },
            {
                "name": "Business Metrics for Data-Driven Companies",
                "issuer": "Coursera — Duke University",
                "year": "2017",
                "link": "https://www.coursera.org/account/accomplishments/verify/KVB8BPFJN6D9",
                "blurb": "Key performance indicators, metric alignment, and data-driven decision frameworks — translating clinical and financial data into metrics that optimize hospital performance and patient satisfaction.",
            },
        ],
    },
    {
        "category": "Delivery, Governance &amp; Professional Development",
        "color": "#1E8A8A",
        "items": [
            {
                "name": "Google Project Management",
                "issuer": "Coursera — Google",
                "year": None,
                "link": "https://www.coursera.org/account/accomplishments/professional-cert/6FME71P1HTZE",
                "blurb": "End-to-end project delivery across Waterfall and Agile methodologies — scope, stakeholder management, and quality control for shipping analytics work on time and on budget.",
            },
            {
                "name": "Google Agile Project Management",
                "issuer": "Coursera — Google",
                "year": None,
                "link": "https://www.coursera.org/account/accomplishments/verify/8VZCL5XBADVV",
                "blurb": "Scrum and Kanban frameworks, backlog management, and sprint retrospectives — running analytics work in short, stakeholder-responsive cycles rather than big-bang releases.",
            },
            {
                "name": "SAP Business Analyst",
                "issuer": "Coursera — SAP",
                "year": "2025",
                "link": "https://coursera.org/verify/professional-cert/VRQ38MNEYNB2",
                "blurb": "Enterprise business process modeling, requirements engineering, and SAP S/4HANA module integration — streamlining hospital supply chains and clinical procurement workflows.",
            },
            {
                "name": "SAP Technology Consultant",
                "issuer": "Coursera — SAP",
                "year": "2025",
                "link": "https://coursera.org/verify/professional-cert/8B6W3FME5IH6",
                "blurb": "Technical system architecture, SAP S/4HANA infrastructure implementation, and data integration protocols — securing cross-system pipelines and EHR interoperability while maintaining high availability for critical hospital IT operations.",
            },
            {
                "name": "Google Cybersecurity (incl. SQL &amp; Python)",
                "issuer": "Coursera — Google Career Certificate",
                "year": "2025",
                "link": "https://coursera.org/verify/professional-cert/LXXDXPKA66CQ",
                "blurb": "Threat modeling, network hardening, and incident response, plus hands-on Python and SQL — grounding for protecting sensitive patient data across healthcare data pipelines.",
            },
            {
                "name": "Strategic Career Self-Management",
                "issuer": "Coursera — The State University of New York",
                "year": None,
                "link": "https://www.coursera.org/account/accomplishments/verify/D4VNCVHCVZJX",
                "blurb": "Treating a career as a strategic portfolio — market positioning, gap analysis, and personal branding — the same analytical rigor turned inward.",
            },
            {
                "name": "What is Social?",
                "issuer": "Coursera — Northwestern University",
                "year": None,
                "link": "https://www.coursera.org/account/accomplishments/verify/4MNL3E3P2KQR",
                "blurb": "Social media strategy and audience analytics fundamentals — rounding out the toolkit for communicating healthcare analytics work to a wider professional audience.",
            },
        ],
    },
]

def render_certifications_body():
    parts = ['<section class="page-header wrap">',
             '<h1>Certifications</h1>',
             '<p class="lede">27 verified credentials spanning healthcare domain knowledge, '
             'data science, BI platforms, and strategic delivery — each links to its official '
             'verification page.</p>',
             '</section>']
    for group in CERTIFICATIONS:
        parts.append(f'<section class="cert-group wrap"><h2 class="cert-category">{group["category"]}</h2><div class="cert-list">')
        for item in group["items"]:
            meta = f'{item["issuer"]} · {item["year"]}' if item["year"] else item["issuer"]
            parts.append(f'''
      <div class="cert">
        <div class="cert-rule" style="background:{group["color"]};"></div>
        <div class="cert-body">
          <h3>{item["name"]}</h3>
          <p class="cert-meta">{meta}</p>
          <p>{item["blurb"]}</p>
          <div class="cert-links"><a href="{item["link"]}">Verify credential</a></div>
        </div>
      </div>''')
        parts.append('</div></section>')
    return "\n".join(parts)

write_page(
    "certifications.html",
    "Certifications",
    "27 verified professional certifications spanning healthcare, data science, BI platforms, and strategic delivery.",
    render_certifications_body()
)

# ---------------------------------------------------------------------------
# PROJECTS
# ---------------------------------------------------------------------------
write_page(
    "projects.html",
    "Projects",
    "Healthcare data science and analytics projects.",
    """
    <section class="page-header wrap">
      <h1>Projects</h1>
    </section>

    <section class="projects wrap">
      <article class="project">
        <div class="project-rule" style="background:#0F5C5C;"></div>
        <div class="project-body">
          <div class="project-head">
            <span class="tag" style="color:#0F5C5C; border-color:#0F5C5C;">Cost &amp; Quality</span>
            <h3>Hospital 30-Day Readmission Prediction</h3>
          </div>
          <p>
            Predicts which patients are likely to be readmitted within 30 days of discharge,
            so a care-management team can target a limited-capacity intervention program at
            the patients who need it most — rather than spreading it thin across everyone.
          </p>
          <div class="stat-row">
            <div class="stat"><span class="stat-num">0.67</span><span class="stat-label">ROC-AUC, in line with published readmission models</span></div>
            <div class="stat"><span class="stat-num">2x</span><span class="stat-label">precision lift in the top 10% risk tier</span></div>
            <div class="stat"><span class="stat-num">$918K</span><span class="stat-label">est. annual net savings at a 20K-discharge hospital</span></div>
          </div>
          <div class="project-links">
            <a href="https://github.com/sohail5993/Strategic-HealthCare-BI-Analyst/tree/main/hospital-readmission-prediction">View repository</a>
            <a href="case-studies.html">Read the case study</a>
          </div>
        </div>
      </article>

      <article class="project">
        <div class="project-rule" style="background:#C96F14;"></div>
        <div class="project-body">
          <div class="project-head">
            <span class="tag" style="color:#C96F14; border-color:#C96F14;">Access &amp; Network</span>
            <h3>Provider Network Adequacy Analysis</h3>
          </div>
          <p>
            Evaluates whether a payer's provider network meets access standards across
            specialty, distance, and wait-time thresholds — and finds a network that looks
            adequate on paper but isn't adequate in practice.
          </p>
          <div class="stat-row">
            <div class="stat"><span class="stat-num">78.3%</span><span class="stat-label">members fully compliant, all 3 standards</span></div>
            <div class="stat"><span class="stat-num">99.7%</span><span class="stat-label">distance compliance</span></div>
            <div class="stat"><span class="stat-num">78.6%</span><span class="stat-label">wait-time compliance — the binding constraint</span></div>
          </div>
          <div class="project-links">
            <a href="https://github.com/sohail5993/Strategic-HealthCare-BI-Analyst">View repository</a>
            <a href="case-studies.html#provider-network-adequacy">Read the case study</a>
          </div>
        </div>
      </article>

      <article class="project project-placeholder">
        <div class="project-rule" style="background:#6C3483;"></div>
        <div class="project-body">
          <div class="project-head">
            <span class="tag" style="color:#6C3483; border-color:#6C3483;">Chronic Disease</span>
            <h3>Care-Gap Prediction for Chronic Disease Management</h3>
          </div>
          <p>In progress — identifying patients likely to miss recommended screenings
             or follow-ups, to close gaps before they become costly complications.</p>
          <div class="project-links"><span class="coming-soon">Coming soon</span></div>
        </div>
      </article>
    </section>
    """
)

# ---------------------------------------------------------------------------
# CASE STUDIES
# ---------------------------------------------------------------------------
write_page(
    "case-studies.html",
    "Case Studies",
    "In-depth case studies: the business problem, the approach, and the measurable outcome.",
    """
    <section class="page-header wrap">
      <h1>Case Studies</h1>
      <p class="lede">Case studies go deeper than the project list — walking through the business problem, the approach, and the measurable outcome.</p>
    </section>

    <section class="case-study wrap">
      <div class="cs-tag" style="color:#0F5C5C; border-color:#0F5C5C;">Cost &amp; Quality</div>
      <h2>Hospital 30-Day Readmission Prediction</h2>

      <h3>The problem</h3>
      <p>
        Under CMS's Hospital Readmissions Reduction Program, hospitals with excess 30-day
        readmissions face payment penalties of up to 3% of total Medicare inpatient
        reimbursement — on top of the roughly $15,000 each avoidable readmission costs
        outright. Care-management teams have enough capacity to actively manage a fraction
        of discharged patients, so the real question isn't "who might be readmitted" —
        it's "who should we call first."
      </p>

      <h3>The approach</h3>
      <p>
        Three models — logistic regression, random forest, and XGBoost — were trained on
        encounter-level clinical and demographic features, with class imbalance handled via
        weighting rather than resampling to keep predicted probabilities trustworthy for
        risk-stratification. Models were compared on precision at realistic staffing
        thresholds (top 10–20% of discharges), not just ROC-AUC, since that's what
        determines whether a limited-capacity program actually catches the right patients.
        SHAP explanations were layered on top so a care coordinator can see <em>why</em> a
        specific patient was flagged, not just their score.
      </p>

      <h3>The result</h3>
      <p>
        The best model reached 0.67 ROC-AUC — in line with published readmission models,
        including CMS's own — and delivered 2x the baseline precision in the top 10% risk
        tier. Simulating a transitional-care program targeted at just the top 5% highest-risk
        discharges produced the best return of any capacity tier tested: 1.84x ROI, an
        estimated $918K in annual net savings for a 20,000-discharge hospital.
      </p>

      <div class="cs-links">
        <a href="https://github.com/sohail5993/Strategic-HealthCare-BI-Analyst/tree/main/hospital-readmission-prediction">View repository</a>
        <a href="https://github.com/sohail5993/Strategic-HealthCare-BI-Analyst/blob/main/hospital-readmission-prediction/reports/readmission_one_pager.pdf">View one-pager</a>
      </div>
    </section>

    <section class="case-study wrap" id="provider-network-adequacy">
      <div class="cs-tag" style="color:#C96F14; border-color:#C96F14;">Access &amp; Network</div>
      <h2>Provider Network Adequacy Analysis</h2>

      <h3>The problem</h3>
      <p>
        Health plans are required — by CMS Medicare Advantage rules, state Medicaid
        contracts, and NCQA accreditation — to prove their provider networks give members
        reasonable access to care, typically measured across three dimensions: distance to
        the nearest provider, appointment wait time, and provider-to-member ratio. Failing
        any of these risks regulatory penalties and corrective action plans — but the
        deeper risk is members who technically have a network but can't actually get seen.
      </p>

      <h3>The approach</h3>
      <p>
        A synthetic regional network of 672 providers across 10 specialties and 48,000
        members across 8 counties (urban, suburban, and rural) was tested against a
        benchmark table modeled on CMS Medicare Advantage Time &amp; Distance criteria and
        state Medicaid MCO wait-time standards. For a stratified member sample, haversine
        distance to the nearest accepting in-network provider, next-available-appointment
        wait time, and provider-to-member ratio were each checked against their standard,
        then rolled up into a gap score ranking every county-by-specialty combination by
        severity.
      </p>

      <h3>The result</h3>
      <p>
        The network passes distance (99.7%) and provider-ratio (100%) standards almost
        everywhere — but appointment wait-time compliance falls to 78.6%, driven by
        Neurology and Behavioral Health backlogs of 22–46 days. Headcount on the roster
        isn't the same as capacity a member can actually access. A second, counterintuitive
        finding: suburban compliance (70.5%) is worse than rural (85.7%), because dense
        suburban demand overwhelms a thin specialist panel more than sparse rural demand
        does — a pattern that urban/suburban/rural bucketing alone would miss.
      </p>

      <div class="cs-links">
        <a href="https://github.com/sohail5993/Strategic-HealthCare-BI-Analyst">View repository</a>
        <a href="https://github.com/sohail5993/Strategic-HealthCare-BI-Analyst/blob/main/outputs/Provider_Network_Adequacy_One_Pager.pdf">View one-pager</a>
      </div>
    </section>

    <section class="cs-placeholder wrap">
      <p class="coming-soon">More case studies coming soon.</p>
    </section>
    """
)

# ---------------------------------------------------------------------------
# BLOG
# ---------------------------------------------------------------------------
write_page(
    "blog.html",
    "Blog",
    "Notes on healthcare analytics, model explainability, and translating data into strategy.",
    """
    <section class="page-header wrap">
      <h1>Blog</h1>
      <p class="lede">Notes on healthcare analytics, model explainability, and translating data into strategy. New posts coming soon.</p>
    </section>

    <section class="prose wrap">
      <h2>Planned topics</h2>
      <ul class="prose-list">
        <li>Why ROC-AUC is the wrong headline metric for readmission models</li>
        <li>Reading a SHAP plot as a non-technical stakeholder</li>
        <li>What CMS's HRRP penalty formula actually rewards</li>
      </ul>
      <p class="coming-soon">First post coming soon.</p>
    </section>
    """
)

# ---------------------------------------------------------------------------
# CONTACT
# ---------------------------------------------------------------------------
write_page(
    "contact.html",
    "Contact",
    "Get in touch — email, LinkedIn, or GitHub.",
    """
    <section class="page-header wrap">
      <h1>Contact</h1>
      <p class="lede">Have a healthcare data problem worth solving? Let's talk.</p>
    </section>

    <section class="contact-list wrap">
      <a class="contact-item" href="mailto:strategichealthcarebianalyst@gmail.com">
        <span class="contact-label">Email</span>
        <span class="contact-value">strategichealthcarebianalyst@gmail.com</span>
      </a>
      <a class="contact-item" href="tel:+923004984892">
        <span class="contact-label">Phone</span>
        <span class="contact-value">+92-300-498-4892</span>
      </a>
      <a class="contact-item" href="https://www.linkedin.com/in/aimms-consulting-35895439">
        <span class="contact-label">LinkedIn</span>
        <span class="contact-value">linkedin.com/in/aimms-consulting-35895439</span>
      </a>
      <a class="contact-item" href="https://github.com/sohail5993">
        <span class="contact-label">GitHub</span>
        <span class="contact-value">github.com/sohail5993</span>
      </a>
    </section>
    """
)

print("\nAll pages generated.")
