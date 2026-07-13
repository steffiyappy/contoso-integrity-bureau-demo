#!/usr/bin/env python3
"""
Rebuild index.html for Contoso Integrity Bureau KPK demo
6 exercises + cleaned bonus tab
"""
import subprocess, re

# Read from git HEAD for static/structural sections (CSS, password gate, Ex4, footer)
result = subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True)
src = result.stdout.decode('utf-8', errors='replace')

# Read from current index.html for bonus modal content (stable after first rebuild)
try:
    with open('index.html', 'r', encoding='utf-8') as _f:
        cur = _f.read()
    # Verify this is the rebuilt version with modal-overlay divs
    if 'modal-kx-b56798a9' not in cur:
        cur = src  # fall back to git HEAD if not yet rebuilt
except FileNotFoundError:
    cur = src

# ── Extract verbatim sections ──────────────────────────────────────────────────

# Keep everything up to and including </style></head>
css_end = src.index('</style></head>') + len('</style></head>')
head = src[:css_end]

# Keep password gate (from <body ...> to start of layout div)
body_tag = src.index('<body class="ihh-active">')
layout_start = src.index('<div class="layout"')
lock_section = src[body_tag:layout_start]

# Keep Ex 4 verbatim but update the Next button label
ex4_start = src.index('<div class="view-ihh" id="view-ex4">')
ex5_marker = '<div class="view-ihh" id="view-ex5">'
ex4_raw = src[ex4_start:src.index(ex5_marker)]
# Update the nav button that said "Report to Deck" to "Analysis to Deliverable"
ex4_raw = ex4_raw.replace(
    'Next: Report to Deck', 'Next: Analysis to Deliverable'
)

# Keep B0 modal content (governance posters) - extracted from current index.html
# which has stable ID modal-kx-b56798a9 from the first rebuild
b0_start = cur.index('<div class="modal-overlay" id="modal-kx-b56798a9">')
# Find end by balanced-bracket counting
def extract_modal_balanced(html, start_id):
    start = html.index(f'<div class="modal-overlay" id="{start_id}">')
    depth = 0
    pos = start
    while pos < len(html):
        next_open = html.find('<div', pos)
        next_close = html.find('</div>', pos)
        if next_open != -1 and (next_close == -1 or next_open < next_close):
            depth += 1
            pos = next_open + 4
        elif next_close != -1:
            depth -= 1
            pos = next_close + 6
            if depth == 0:
                return html[start:pos]
        else:
            break
    return html[start:]

modal_b0 = extract_modal_balanced(cur, 'modal-kx-b56798a9')
modal_b1 = extract_modal_balanced(cur, 'modal-kx-new-b1')   # prompt tips
modal_b2 = extract_modal_balanced(cur, 'modal-kx-new-b2')   # outlook catch-up
modal_b3 = extract_modal_balanced(cur, 'modal-kx-new-b3')   # outlook reply
modal_b4 = extract_modal_balanced(cur, 'modal-kx-new-b4')   # word interrogate
modal_b5 = extract_modal_balanced(cur, 'modal-kx-new-b5')   # quick fact check

# Keep footer scripts verbatim
footer_scripts_start = src.index('\n<script>\ntry{localStorage')
footer_scripts = src[footer_scripts_start:]

# Keep session-ID footer div
session_div_start = src.index('<div style="margin-top:48px')
session_div_end = src.index('</div>', session_div_start) + len('</div>')
session_footer = src[session_div_start:session_div_end]

# ── Build new sections ─────────────────────────────────────────────────────────

SIDEBAR = '''<aside>
<div class="brand"><div class="logo">CC</div><h1>M365 Copilot<br/>GM Immersion</h1></div>
<div class="tag">Executive Immersion</div>
<nav>
<h3>Overview</h3>
<a href="#files">&#128193; Sample files (start here)</a>
<a href="#overview">About this session</a>
<a href="#story">The Story</a>
<h3>Exercises</h3>
<a href="#ex1">1 &#183; Daily Briefing</a>
<a href="#ex2">2 &#183; OSINT Scraping + Sweep</a>
<a href="#ex3">3 &#183; Procurement Anomalies</a>
<a href="#ex4">4 &#183; Meeting Minutes</a>
<a href="#ex5">5 &#183; Analysis to Deliverable</a>
<a href="#ex6">6 &#183; Build Your Own Agent</a>
<h3>Extras</h3>
<a href="#extras">&#65291; Bonus tab (6 more Copilot moves)</a>
<h3>Resources</h3>
<a href="#tips">Prompt tips</a>
</nav>
</aside>'''

TABS = '''<nav class="tabs-ihh"><div class="tabs-inner"><button class="tab active" data-view="intro"><span class="tab-num">0</span> Get Started</button>
<button class="tab" data-view="files"><span class="tab-num">&#128193;</span> Sample Files</button>
<button class="tab" data-view="ex1"><span class="tab-num">1</span> Daily Briefing</button>
<button class="tab" data-view="ex2"><span class="tab-num">2</span> OSINT Scraping + Sweep</button>
<button class="tab" data-view="ex3"><span class="tab-num">3</span> Procurement Anomalies</button>
<button class="tab" data-view="ex4"><span class="tab-num">4</span> Meeting Minutes</button>
<button class="tab" data-view="ex5"><span class="tab-num">5</span> Analysis to Deliverable</button>
<button class="tab" data-view="ex6"><span class="tab-num">6</span> Build Your Own Agent</button>
<button class="tab" data-view="extras"><span class="tab-num">&#65291;</span> Bonus</button>
</div></nav>'''

HERO = '''<header class="hero-ihh">
<div class="hero-ihh-inner">
<div class="hero-brand-ihh">
<div class="hero-logo-ihh">CR</div>
<div class="brand-rule-ihh"></div>
<div>
<h1>Contoso Integrity Bureau</h1>
<h2>Microsoft 365 Copilot &#183; GM Immersion</h2>
</div>
</div>
<div class="hero-meta-ihh">
<div>Workshop Edition &#183; 2026</div>
<div style="margin-top:6px">
<span class="pill">6 Exercises + Bonus</span>
</div>
</div>
</div>
<div class="hero-title-ihh">
<h3>One workday, one Task Force Head, six Copilot moments</h3>
<p>A hands-on immersion for Contoso Integrity Bureau executives, tailored to the Coordination and Supervision Task Force. Every prompt is copy-and-paste ready. Every exercise is grounded on the sample files.</p>
</div>
</header>'''

VIEW_INTRO = '''<div class="view-ihh active" id="view-intro"><section id="overview">
<div class="hero">
<h2>Contoso Integrity Bureau &#183; Task Force Copilot Immersion</h2>
<p>A national anti-corruption agency, modelled on the Directorate of Coordination and Supervision. A hands-on, Task-Force-level immersion covering both mission functions: Enforcement (turning open-source news into structured SPDP cases) and Prevention (turning provincial procurement disclosures into anomaly red flags), ending with a declarative Copilot agent the team can use daily.</p>
<div class="meta-row">
<span><b>Audience</b> Task Force Head, Enforcement Lead, Prevention Lead, Data Analyst, Legal Advisor, OSINT Specialist</span>
<span><b>Duration</b> 90 minutes</span>
<span><b>Format</b> Six live exercises plus a Bonus tab with 6 more Copilot moves</span>
</div>
</div>
</section>
<section id="story">
<div style="margin:8px 0 20px;background:rgba(200,155,60,.10);border-left:4px solid #C89B3C;padding:14px 18px;border-radius:8px">
<div style="font-size:13px;font-weight:700;color:#C89B3C;text-transform:uppercase;letter-spacing:.5px;margin-bottom:10px">Your requirements, mapped</div>
<table style="width:100%;font-size:13px;color:var(--ink);border-collapse:collapse">
<tr><td style="padding:4px 12px 4px 0;vertical-align:top;white-space:nowrap;color:var(--ink)"><b>OSINT news, structured extraction</b></td><td style="padding:4px 0;color:var(--muted)">Exercise 2, Task 2.1 (flagship - Researcher scrapes one URL with G-C-S-E prompt)</td></tr>
<tr><td style="padding:4px 12px 4px 0;vertical-align:top;white-space:nowrap;color:var(--ink)"><b>OSINT batch sweep + SPDP register update</b></td><td style="padding:4px 0;color:var(--muted)">Exercise 2, Task 2.2 (Cowork - the customer's own term from the Bahasa requirements doc. On-demand only; Pak Bambang re-runs each morning.)</td></tr>
<tr><td style="padding:4px 12px 4px 0;vertical-align:top;white-space:nowrap;color:var(--ink)"><b>Procurement anomaly detection</b></td><td style="padding:4px 0;color:var(--muted)">Exercise 3 (flagship - Copilot in Excel Chat + Edit, six anomaly patterns seeded)</td></tr>
<tr><td style="padding:4px 12px 4px 0;vertical-align:top;white-space:nowrap;color:var(--ink)"><b>Teams recap saved as Word minutes</b></td><td style="padding:4px 0;color:var(--muted)">Exercise 4 (generic prompts, works with any meeting)</td></tr>
<tr><td style="padding:4px 12px 4px 0;vertical-align:top;white-space:nowrap;color:var(--ink)"><b>Word polish and PowerPoint auto-gen</b></td><td style="padding:4px 0;color:var(--muted)">Exercise 5, Tasks 5.1 and 5.2 (plus Cowork alternative in Task 5.4)</td></tr>
<tr><td style="padding:4px 12px 4px 0;vertical-align:top;white-space:nowrap;color:var(--ink)"><b>Excel governance dashboard</b></td><td style="padding:4px 0;color:var(--muted)">Exercise 3 Task 3.2 (build) and Exercise 5 Task 5.3 (sharpen for deck)</td></tr>
<tr><td style="padding:4px 12px 4px 0;vertical-align:top;white-space:nowrap;color:var(--ink)"><b>Governance infographic and posters</b></td><td style="padding:4px 0;color:var(--muted)">Bonus B0 (four Copilot Create prompts - outputs are flat images, not editable slides)</td></tr>
<tr><td style="padding:4px 12px 4px 0;vertical-align:top;white-space:nowrap;color:var(--ink)"><b>Build a declarative Copilot agent</b></td><td style="padding:4px 0;color:var(--muted)">Exercise 6 (Copilot Chat agent builder - no Copilot Studio licence needed)</td></tr>
</table>
</div>
<div class="modulehead" style="margin-top:8px">
<div class="num" style="background:linear-gradient(135deg,var(--brand),var(--accent));font-size:14px">&#9658;</div>
<h2>The Story<small>One Task Force workday, six Copilot moments, plus a Bonus tab</small></h2>
</div>
<div style="border:1px solid var(--border);border-radius:14px;overflow:hidden;box-shadow:var(--shadow);margin-bottom:24px;background:var(--panel)">
<div style="background:linear-gradient(180deg,var(--sidebar-a),var(--sidebar-b));padding:22px 26px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;align-items:center">
<div>
<p style="margin:0;font-size:10px;letter-spacing:2px;font-weight:700;color:var(--brand);text-transform:uppercase">Microsoft 365 Copilot</p>
<h3 style="margin:4px 0 0;font-size:22px;font-weight:800;color:#fff;line-height:1.15">AI Assistant<br/>to AI Doer</h3>
</div>
<div>
<p style="margin:0 0 4px;font-size:9.5px;letter-spacing:1.5px;font-weight:700;color:var(--brand);text-transform:uppercase">Persona</p>
<p style="margin:0;font-size:15px;font-weight:700;color:#fff">Pak Bambang Kusumo</p>
<p style="margin:3px 0 10px;font-size:12px;color:#94a3b8">Head, Coordination and Supervision Task Force, Contoso Integrity Bureau</p>
<p style="margin:0 0 4px;font-size:9.5px;letter-spacing:1.5px;font-weight:700;color:var(--brand);text-transform:uppercase">The Mission</p>
<p style="margin:0;font-size:12px;color:#cbd5e1;line-height:1.55">Two functions running in parallel: (1) Enforcement - coordinating and supervising corruption case handling by prosecutors and police, using SPDP data plus OSINT sweeps; (2) Prevention - evaluating provincial and regency governance for anomalies in budget, procurement, and licensing.</p>
</div>
<div style="padding:14px;background:rgba(255,255,255,.06);border-radius:10px;border:1px solid rgba(255,255,255,.1)">
<p style="margin:0 0 5px;font-size:9.5px;letter-spacing:1.5px;font-weight:700;color:var(--brand);text-transform:uppercase">The Punchline</p>
<p style="margin:0;font-size:14px;font-weight:700;font-style:italic;color:#fff;line-height:1.4">One Task Force workday.<br/>Six Copilot moments.<br/>From OSINT sweep to declarative agent.</p>
</div>
</div>
<div style="padding:22px 22px 18px">
<h3 style="margin:0 0 16px;font-size:18px;font-weight:700;color:var(--ink)">Six Copilot moments for the Task Force <span style="font-size:12px;color:var(--muted);font-weight:500">+ 6 more moves in the Bonus tab</span></h3>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px">
<div style="min-height:230px;border:1px solid var(--border);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;background:var(--panel2)">
<div style="background:#0B2A4A;padding:10px 14px;display:flex;align-items:center;gap:8px;flex:0 0 auto">
<span style="font-size:22px;font-weight:800;color:rgba(255,255,255,.95);line-height:1">01</span>
<span style="font-size:12px;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.5px;line-height:1.2">Daily Briefing</span>
</div>
<div style="padding:14px;display:flex;flex-direction:column;gap:6px;flex:1 1 auto">
<p style="margin:0;font-size:16px;font-weight:700;color:var(--ink);line-height:1.3">Two briefing variants</p>
<p style="margin:0;font-size:12px;font-style:italic;color:var(--brand);font-weight:600">Copilot Chat (5 min) + Researcher (15 min)</p>
<p style="margin:0;font-size:13px;color:var(--muted);line-height:1.45">Task 1.1 is a fast Copilot Chat scan with no citations. Task 1.2 is a structured, cited Researcher brief with SPDP updates, calendar prep, and pending decisions. Pick the version that fits the morning.</p>
</div>
</div>
<div style="min-height:230px;border:1px solid var(--border);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;background:var(--panel2)">
<div style="background:#0B2A4A;padding:10px 14px;display:flex;align-items:center;gap:8px;flex:0 0 auto">
<span style="font-size:22px;font-weight:800;color:rgba(255,255,255,.95);line-height:1">02</span>
<span style="font-size:12px;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.5px;line-height:1.2">OSINT Scraping + Sweep</span>
</div>
<div style="padding:14px;display:flex;flex-direction:column;gap:6px;flex:1 1 auto">
<p style="margin:0;font-size:16px;font-weight:700;color:var(--ink);line-height:1.3">One URL to full register update</p>
<p style="margin:0;font-size:12px;font-style:italic;color:var(--brand);font-weight:600">Researcher (Task 2.1) + Cowork (Task 2.2)</p>
<p style="margin:0;font-size:13px;color:var(--muted);line-height:1.45">Task 2.1 uses Researcher to extract SPDP-style fields from a single article. Task 2.2 uses Cowork to sweep the full Google News RSS feed, deduplicate against the case register, and draft the morning Teams post.</p>
</div>
</div>
<div style="min-height:230px;border:1px solid var(--border);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;background:var(--panel2)">
<div style="background:#0B2A4A;padding:10px 14px;display:flex;align-items:center;gap:8px;flex:0 0 auto">
<span style="font-size:22px;font-weight:800;color:rgba(255,255,255,.95);line-height:1">03</span>
<span style="font-size:12px;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.5px;line-height:1.2">Procurement Anomalies</span>
</div>
<div style="padding:14px;display:flex;flex-direction:column;gap:6px;flex:1 1 auto">
<p style="margin:0;font-size:16px;font-weight:700;color:var(--ink);line-height:1.3">Red flags across the province</p>
<p style="margin:0;font-size:12px;font-style:italic;color:var(--brand);font-weight:600">Copilot in Excel Chat + Edit</p>
<p style="margin:0;font-size:13px;color:var(--muted);line-height:1.45">Task 3.1 uses Chat mode for four targeted questions. Task 3.2 uses Edit mode to build a Risk_Score column and a Governance Dashboard sheet. The dashboard from this exercise is the direct input to Exercise 5.</p>
</div>
</div>
<div style="min-height:230px;border:1px solid var(--border);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;background:var(--panel2)">
<div style="background:#0B2A4A;padding:10px 14px;display:flex;align-items:center;gap:8px;flex:0 0 auto">
<span style="font-size:22px;font-weight:800;color:rgba(255,255,255,.95);line-height:1">04</span>
<span style="font-size:12px;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.5px;line-height:1.2">Meeting Minutes</span>
</div>
<div style="padding:14px;display:flex;flex-direction:column;gap:6px;flex:1 1 auto">
<p style="margin:0;font-size:16px;font-weight:700;color:var(--ink);line-height:1.3">Any meeting to formal minutes</p>
<p style="margin:0;font-size:12px;font-style:italic;color:var(--brand);font-weight:600">Teams + Word Copilot</p>
<p style="margin:0;font-size:13px;color:var(--muted);line-height:1.45">Three generic prompts that turn any Teams meeting, budget review, licensing panel, or board update into house-style minutes with a decisions box, action register, and executive summary. Five minutes end-to-end, not 90.</p>
</div>
</div>
<div style="min-height:230px;border:1px solid var(--border);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;background:var(--panel2)">
<div style="background:#0B2A4A;padding:10px 14px;display:flex;align-items:center;gap:8px;flex:0 0 auto">
<span style="font-size:22px;font-weight:800;color:rgba(255,255,255,.95);line-height:1">05</span>
<span style="font-size:12px;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.5px;line-height:1.2">Analysis to Deliverable</span>
</div>
<div style="padding:14px;display:flex;flex-direction:column;gap:6px;flex:1 1 auto">
<p style="margin:0;font-size:16px;font-weight:700;color:var(--ink);line-height:1.3">Ex 3 output to the Deputy briefing pack</p>
<p style="margin:0;font-size:12px;font-style:italic;color:var(--brand);font-weight:600">Word + PowerPoint + Excel + Cowork</p>
<p style="margin:0;font-size:13px;color:var(--muted);line-height:1.45">Polish the Word report (5.1), generate a deck from the polished Word doc (5.2), sharpen the Excel dashboard (5.3), then see the same three artefacts produced in one Cowork prompt (5.4) so you can see the tradeoff.</p>
</div>
</div>
<div style="min-height:230px;border:1px solid var(--border);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;background:var(--panel2)">
<div style="background:#0B2A4A;padding:10px 14px;display:flex;align-items:center;gap:8px;flex:0 0 auto">
<span style="font-size:22px;font-weight:800;color:rgba(255,255,255,.95);line-height:1">06</span>
<span style="font-size:12px;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.5px;line-height:1.2">Build Your Own Agent</span>
</div>
<div style="padding:14px;display:flex;flex-direction:column;gap:6px;flex:1 1 auto">
<p style="margin:0;font-size:16px;font-weight:700;color:var(--ink);line-height:1.3">A grounded Q and A agent for the Task Force</p>
<p style="margin:0;font-size:12px;font-style:italic;color:var(--brand);font-weight:600">Copilot Chat agent builder (declarative)</p>
<p style="margin:0;font-size:13px;color:var(--muted);line-height:1.45">Build a declarative Copilot Chat agent grounded on the procurement and SPDP files. No Copilot Studio licence. Four starter prompts that the full Task Force can use immediately. Honest about what declarative agents can and cannot do.</p>
</div>
</div>
<div style="min-height:230px;border:1px solid var(--border);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;background:var(--panel2)">
<div style="background:#C89B3C;padding:10px 14px;display:flex;align-items:center;gap:8px;flex:0 0 auto">
<span style="font-size:22px;font-weight:800;color:rgba(255,255,255,.95);line-height:1">+</span>
<span style="font-size:12px;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.5px;line-height:1.2">Bonus Tab</span>
</div>
<div style="padding:14px;display:flex;flex-direction:column;gap:6px;flex:1 1 auto">
<p style="margin:0;font-size:16px;font-weight:700;color:var(--ink);line-height:1.3">6 more Copilot moves for the Task Force</p>
<p style="margin:0;font-size:12px;font-style:italic;color:var(--brand);font-weight:600">Posters, prompt tips, Outlook, Word</p>
<p style="margin:0;font-size:13px;color:var(--muted);line-height:1.45">Four Copilot Create governance poster prompts, the G-C-S-E prompt framework card, two Outlook Copilot moves, a Word interrogation prompt, and a pre-send fact-check prompt.</p>
</div>
</div>
</div>
</div>
</div>
</section>
<div class="lab-nav-ihh"><button class="secondary" disabled="">← Previous</button><button data-go="files">Next: Sample Files →</button></div></div>'''

VIEW_FILES = '''<div class="view-ihh" id="view-files"><section id="files">
<div class="modulehead"><div class="num">&#128193;</div><h2>Sample files - start here<small>Download these first, then run the exercises</small></h2></div>
<div class="card">
<p class="lead">All data is fictional and labelled <b>Contoso</b>. Do not use for any operational decision. <b>Step 1:</b> download every file. <b>Step 2:</b> upload the six files to your OneDrive and the <b>Applicants/</b> folder to any SharePoint document library. <b>Step 3:</b> wait about 2 minutes for Microsoft Graph to index. Then begin Exercise 1.</p>
<div style="margin:14px 0 18px;display:flex;flex-wrap:wrap;gap:12px;align-items:center">
<a download="" href="samples.zip" id="dl-all-btn" style="display:inline-flex;align-items:center;gap:10px;padding:12px 22px;background:#0B2A4A;color:#fff;font-weight:700;font-size:15px;border-radius:10px;text-decoration:none;box-shadow:var(--shadow);transition:transform .12s ease">
  &#11015;&#65039; Download all sample files (ZIP)
 </a>
<span style="font-size:12.5px;color:var(--muted)">One click, all files in a single ZIP. Unzip, then upload the contents to OneDrive and SharePoint.</span>
</div>
<table>
<tr><th>#</th><th>File</th><th>Type</th><th>Used in</th><th>What it contains</th></tr>
<tr><td>01</td><td><a href="samples/01 Contoso_Task_Force_Overview.docx">01 Contoso_Task_Force_Overview.docx</a></td><td><span class="badge yellow">Word</span></td><td>All exercises (context)</td><td>One-page context brief on Contoso Integrity Bureau, the Coordination and Supervision Task Force, and the two mission functions. Includes the persona bio for Pak Bambang Kusumo.</td></tr>
<tr><td>02</td><td><a href="samples/02 Contoso_Direct_Procurement_Q3.xlsx">02 Contoso_Direct_Procurement_Q3.xlsx</a></td><td><span class="badge blue">Excel</span></td><td>Ex 3, Ex 5, Ex 6</td><td>180 rows of provincial and regency direct-procurement disclosures. Six anomaly patterns seeded intentionally: split contracts under the 200M IDR threshold, vendor concentration, price outliers, new-vendor high-value awards, shared vendor addresses, weekend awards.</td></tr>
<tr><td>03</td><td><a href="samples/03 Contoso_SPDP_Case_Register.xlsx">03 Contoso_SPDP_Case_Register.xlsx</a></td><td><span class="badge blue">Excel</span></td><td>Ex 2, Ex 6</td><td>Existing SPDP case tracker used by the Task Force, roughly 40 rows. This is the append target for the OSINT sweep in Exercise 2 Task 2.2 and the grounding source for the agent in Exercise 6.</td></tr>
<tr><td>04</td><td><a href="samples/04 Contoso_Sample_News_URLs.md">04 Contoso_Sample_News_URLs.md</a></td><td><span class="badge yellow">Markdown</span></td><td>Ex 2</td><td>Five Indonesian corruption news URLs, including the Jember bansos article from Antara News. Used for the OSINT extraction exercise.</td></tr>
<tr><td>05</td><td><a href="samples/05 Contoso_Governance_Report_Draft.docx">05 Contoso_Governance_Report_Draft.docx</a></td><td><span class="badge yellow">Word</span></td><td>Ex 5</td><td>Four-page Q3 procurement supervision draft, deliberately wordy, with weak topic-only headings and no executive summary. Input for the polish exercise and the PowerPoint auto-generation.</td></tr>
<tr><td>06</td><td><a href="samples/06 Contoso_Task_Force_Meeting_Transcript.docx">06 Contoso_Task_Force_Meeting_Transcript.docx</a></td><td><span class="badge yellow">Word</span></td><td>Ex 4</td><td>Realistic 40-turn transcript from a 30-minute weekly coordination meeting with Pak Bambang and five direct reports. Covers SPDP backlog, red-flag agencies, and one urgent OSINT case from Jember.</td></tr>
<tr><td>07</td><td><a href="samples/Applicants/">samples/Applicants/ (12 files)</a></td><td><span class="badge yellow">Word &#215;12</span></td><td>Not used in current edition</td><td>Twelve candidate integrity profiles (Applicant_01 through Applicant_12). The applicant screening exercise was removed in this edition. Files are retained for reference.</td></tr>
</table>
<div class="callout warn" style="margin-top:14px"><b>Why OneDrive and SharePoint?</b> Microsoft 365 Copilot can only analyse files stored in OneDrive or SharePoint. Files on your local Desktop are invisible to Copilot.</div>
</div>
</section><div class="lab-nav-ihh"><button class="secondary" data-go="intro">← Get Started</button><button data-go="ex1">Next: Daily Briefing →</button></div></div>'''

VIEW_EX1 = '''<div class="view-ihh" id="view-ex1"><section id="ex1">
<div class="modulehead"><div class="num">1</div><h2>Exercise 1 &#183; Daily Briefing<small>Two variants &#183; Petrosea pattern &#183; Copilot Chat (5 min) + Researcher (15 min)</small></h2></div>
<div class="callout good"><b>How Pak Bambang starts the day.</b> Two tools, same question, different depth. Task 1.1 is a fast five-minute Copilot Chat scan - no citations, no waiting. Task 1.2 is a structured fifteen-minute Researcher brief with sources, SPDP new filings, calendar prep, and pending decisions filed as a working paper. Pick the one that fits the morning.</div>
<div class="card">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:6px">
<div style="background:var(--panel2);border:1px solid var(--border);border-radius:10px;padding:14px">
<div style="font-size:11px;font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Task 1.1 &#183; Copilot Chat</div>
<div style="font-size:13px;color:var(--muted)">5 minutes &#183; Fast &#183; No citations</div>
<div style="font-size:13px;color:var(--muted);margin-top:4px">Use when you have five minutes before your first meeting</div>
</div>
<div style="background:var(--panel2);border:1px solid var(--border);border-radius:10px;padding:14px">
<div style="font-size:11px;font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Task 1.2 &#183; Researcher</div>
<div style="font-size:13px;color:var(--muted)">15 minutes &#183; Structured &#183; Cited</div>
<div style="font-size:13px;color:var(--muted);margin-top:4px">Use when you need a filing-grade working paper to start the day</div>
</div>
</div>

<div class="activity">
<div class="head"><span class="num">Task 1.1</span><span class="file">&#128172; Copilot Chat &#183; five-minute morning scan</span></div>
<h4>Fast morning brief - five minutes, no citations</h4>
<p class="lead">Open Microsoft 365 Copilot Chat at <a href="https://copilot.microsoft.com" target="_blank">copilot.microsoft.com</a>. Paste the prompt below. This is the fast variant: Copilot Chat will scan your inbox, calendar, and Teams messages and return a plain three-section brief in under two minutes.</p>
<div class="prompt">Goal: give me a five-minute morning brief covering everything I need to know before I start work today.

Context: I am Pak Bambang Kusumo, Head of the Coordination and Supervision Task Force at Contoso Integrity Bureau. My two functions are Enforcement (tracking corruption case progress via SPDP and OSINT news) and Prevention (evaluating procurement anomalies at provincial and regency agencies). I need a fast scan, not a deep analysis.

Source: my Outlook inbox (unread emails since yesterday 5 pm), my calendar for today, my Teams messages from the last 24 hours.

Expectation: three short sections, each under five bullet points:
1. Overnight developments - any new SPDP filing notifications received by email, any corruption news that mentions cases my Task Force is tracking, or urgent messages from direct reports.
2. Today's calendar - meetings today in chronological order, each with a one-line topic and what I need to bring or decide.
3. Pending decisions - anything I said I would decide or respond to yesterday that is still open.

Rules: no citations needed. This is a fast scan. Use plain language. If nothing was found in a section, say "nothing flagged" rather than leaving it blank.<button class="copy" onclick="cp(this)">Copy</button></div>
<div class="callout"><b>What success looks like:</b> a clean three-section brief on screen in under two minutes. No footnotes, no source links - just the three things Pak Bambang needs before his first meeting.</div>
</div>

<div class="activity">
<div class="head"><span class="num">Task 1.2</span><span class="file">&#128269; Researcher &#183; fifteen-minute audit-grade brief</span></div>
<h4>Structured daily briefing - cited, deeper, suitable for filing</h4>
<p class="lead">Open Microsoft 365 Copilot at <a href="https://copilot.microsoft.com" target="_blank">copilot.microsoft.com</a> and click <b>Researcher</b>. Keep the model picker on <b>Auto</b>. Paste the prompt below. Researcher will read your inbox, Teams channels, calendar, and recent files, then hand you a single structured briefing with citations you can save as a working paper.</p>
<div class="prompt">Goal: produce a structured daily briefing for the Coordination and Supervision Task Force Head, suitable for filing as an official working paper.

Context: I am Pak Bambang Kusumo, Head of the Coordination and Supervision Task Force at Contoso Integrity Bureau. The briefing covers two functions: Enforcement (SPDP case tracking and OSINT news) and Prevention (procurement anomaly oversight). This brief will be saved to my OneDrive as the reference document for today's work.

Source: my Outlook inbox (last 24 hours), my Teams channels "Task Force - Daily OSINT" and "Task Force - Coordination", my calendar for today and tomorrow, and any open documents or chat threads I have not yet responded to.

Expectation - four sections with citations:
1. Enforcement update - new SPDP filing notifications received by email or Teams since yesterday, any corruption news that directly names a case in my Task Force portfolio, and the name and stage of each. Cite the email subject line or message thread for each item.
2. Prevention update - any procurement anomaly reports, agency responses, or supervision letter deadlines in the last 24 hours. Cite source.
3. Today's calendar - a table with columns: Time, Meeting Title, Organiser, Suggested Preparation (one sentence each). Mark any meeting where I am the decision-maker.
4. Pending actions from yesterday - anything assigned to me in a Teams message or email that I have not yet completed. Cite source and original request date.

Rules: cite source for every item (email subject line, Teams thread name, or document name). If a section has no new items, state that clearly. Neutral, third-person tone for items 1 and 2. Do not speculate about cases not mentioned in the sources.<button class="copy" onclick="cp(this)">Copy</button></div>
<div class="callout"><b>What success looks like:</b> a four-section brief with inline citations for every item. Each item in the Enforcement and Prevention sections is traceable back to a specific email or Teams thread. The calendar table shows preparation notes for today's meetings. Pending actions lists anything unanswered.</div>
</div>

<div class="callout warn"><b>Reality Check &#183; Exercise 1.</b>
<br/>Copilot Chat (Task 1.1): reads your tenant data reliably but does not cite sources - it is a fast scan, not an audit trail.
<br/>Researcher (Task 1.2): web freshness varies. Items grounded on your tenant data (inbox, calendar, Teams) are reliable. Any claim that references external web results should be treated as a starting point and verified. Researcher does not have real-time access to SPDP Online - new filings in this brief come from email notifications in your inbox, not from a live database connection.
<br/>Neither variant is a replacement for the official SPDP Online system. Use as a morning orientation, then verify critical items from the primary source.</div>
</div>
</section><div class="lab-nav-ihh"><button class="secondary" data-go="files">← Sample Files</button><button data-go="ex2">Next: OSINT Scraping + Sweep →</button></div></div>'''

VIEW_EX2 = '''<div class="view-ihh" id="view-ex2"><section id="ex2">
<div class="modulehead"><div class="num">2</div><h2>Exercise 2 &#183; OSINT Scraping + Sweep<small>Task 2.1: Researcher &#183; Task 2.2: Cowork &#183; Flagship for Enforcement</small></h2></div>
<div class="callout good"><b>Why this matters.</b> Many corruption cases are not reported through the official SPDP Online system in time for the morning review. The Task Force must sweep open-source news, extract the facts, and update the case register. Task 2.1 uses Researcher to extract audit-grade data from a single article. Task 2.2 uses Cowork to sweep the full Google News RSS feed, deduplicate against the existing register, and draft the morning communications.</div>

<div class="card">
<div class="activity">
<div class="head"><span class="num">Task 2.1</span><span class="file">&#128269; Researcher &#183; single URL audit-grade extraction</span></div>
<h4>Extract SPDP-style fields from one news article</h4>
<p class="lead">Open Microsoft 365 Copilot at <a href="https://copilot.microsoft.com" target="_blank">copilot.microsoft.com</a>, click <b>Researcher</b>, and paste the G-C-S-E prompt below. The sample URL is the Antara News article about the Jember bansos case. Run the initial prompt first, then run the refinement prompt to add Stage, Confidence, and Source URL.</p>

<div class="task-step"><div class="step-label">Step 1 of 2 &#183; Initial extraction (Bahasa Indonesia columns)</div></div>
<div class="prompt">Goal: extract the corruption case facts from the news article at the URL below and return them as a structured table row I can paste into my SPDP case register.

Context: I am Pak Bambang Kusumo, Head of the Coordination and Supervision Task Force at Contoso Integrity Bureau. I sweep Indonesian news sources daily for corruption cases that may not yet appear in SPDP Online. I need clean, structured data to add to the register.

Source: https://jatim.antaranews.com/berita/261998/saksi-bpkp-sebut-kerugian-negara-korupsi-hibah-bansos-jember-capai-rp104-miliar

Expectation: return a Markdown table with one data row and these five columns in order:
- Nama Perkara (short descriptive case name in Indonesian)
- Periode Perkara (year or year range as stated in the article)
- Tersangka / Terdakwa (suspect or defendant names, comma-separated, as reported)
- Jumlah Kerugian Keuangan Negara (estimated state financial loss in IDR - numeric value plus a human-readable form such as "104 miliar IDR")
- APH Menangani (law enforcement agency handling the case - KPK, Kejaksaan, Polri, or as reported)

Rules: use only facts explicitly stated in the article. If a field is not stated, write "tidak disebutkan". Do not guess or infer.<button class="copy" onclick="cp(this)">Copy</button></div>

<div class="task-step"><div class="step-label">Step 2 of 2 &#183; Refinement - add Stage, Confidence, Source URL, Notes</div></div>
<div class="prompt">Refine the extraction table from the article at:
https://jatim.antaranews.com/berita/261998/saksi-bpkp-sebut-kerugian-negara-korupsi-hibah-bansos-jember-capai-rp104-miliar

Expand the table by adding four columns after APH Menangani:
- Tahap Perkara (current case stage - penyidikan, penuntutan, persidangan, putusan, banding, or as reported in the article)
- Tingkat Keyakinan (extraction confidence: Tinggi if the article clearly states the field, Sedang if it is implied, Rendah if uncertain)
- URL Sumber (the source URL, repeated)
- Catatan (one short note on any ambiguity - for example, if the state-loss figure is attributed to a witness rather than a final court ruling)

Keep all five original columns. Maintain the rule: if a field is not explicitly stated, write "tidak disebutkan" and set Tingkat Keyakinan to Rendah for that field.<button class="copy" onclick="cp(this)">Copy</button></div>

<div class="callout"><b>What success looks like:</b> a nine-column table with every field grounded on the article text. Jumlah Kerugian and APH should be Tinggi. Tahap Perkara may be Sedang or Rendah if the article does not clearly name the stage. The Catatan column should flag the BPKP witness attribution on the state-loss figure.</div>
</div>

<div class="activity">
<div class="head"><span class="num">Task 2.2</span><span class="file">&#128260; Cowork &#183; batch sweep &#183; Variant A: Outlook RSS folder</span></div>
<h4>Batch sweep - read the RSS feed, update the register, draft communications</h4>
<p class="lead"><b>Cowork is on-demand.</b> Pak Bambang re-runs this prompt each morning. The prompt reads the Outlook RSS folder "OSINT - Google News", extracts SPDP-style fields from each article, deduplicates against <code>03 Contoso_SPDP_Case_Register.xlsx</code>, appends new rows, and drafts a Teams post and a distribution email. It stops before sending anything.</p>
<p class="lead" style="margin-top:8px">The Google News RSS URL pattern the Task Force already uses:<br/><code style="font-size:12px;word-break:break-all">https://news.google.com/rss/search?q=korupsi+OR+tipikor+OR+%22kerugian+negara%22+OR+%22OTT+KPK%22+OR+%22dugaan+korupsi%22+OR+%22tersangka+korupsi%22+OR+SPDP&amp;hl=id&amp;gl=ID&amp;ceid=ID:id</code></p>
<div class="prompt">Goal: sweep this morning's Google News corruption alerts, extract SPDP-style fields from each article, update the case register with new rows, and prepare communications for my review.

Context: I am Pak Bambang Kusumo, Head of the Coordination and Supervision Task Force at Contoso Integrity Bureau. I subscribe to Google News alerts via Outlook RSS for Indonesian corruption keywords (korupsi, OTT KPK, kerugian negara, dugaan korupsi, SPDP). New alert emails arrive overnight. I run this sweep each morning before my first meeting.

Source:
- Outlook: RSS folder "OSINT - Google News", emails received in the last 24 hours only.
- Excel: 03 Contoso_SPDP_Case_Register.xlsx on my OneDrive, sheet "Cases", existing rows.
- Teams: channel "Task Force - Daily OSINT" in the Task Force team.

Expectation - complete these steps in order and stop at the end for my review:
1. In Outlook, list every unread RSS item in "OSINT - Google News" from the last 24 hours. For each item, follow the article link and extract these fields: Nama Perkara, Periode Perkara, Tersangka/Terdakwa, Jumlah Kerugian Keuangan Negara, APH Menangani, Tahap Perkara, Tingkat Keyakinan, URL Sumber, Catatan.
2. Open 03 Contoso_SPDP_Case_Register.xlsx. For each extracted case, check whether a matching row already exists in sheet "Cases" with the same suspect names AND overlapping case period. If a match exists: do not add a new row; instead, update the Notes column of the matching row with the new source URL and today's date. If no match: prepare a new row to append.
3. Append all new-case rows to sheet "Cases". Preserve the existing column order. Set the Owner column to "Pak Bambang - to assign".
4. Draft a summary Teams message for channel "Task Force - Daily OSINT" with: total articles read, total new cases added, total cases updated, a table of the new cases, and a note flagging the highest-state-loss new case for priority review.
5. Draft an Outlook email to the Task Force distribution list. Subject: "Laporan OSINT Sweep - [today's date] - [N] kasus baru". Body: same summary as step 4.

STOP before sending the Teams message or the email. Show me all drafts and the list of rows to be appended first. I will review and approve before anything is sent.

Closing line: once I approve, this run replaces roughly 45 minutes of my morning routine.<button class="copy" onclick="cp(this)">Copy</button></div>
<div class="callout warn" style="margin-top:8px"><b>STOP callout.</b> Cowork will not send anything until Pak Bambang explicitly approves. The Teams message draft and email draft are shown for review first. The rows to be appended to the Excel file are listed before any write happens. This is the safety check that makes the pipeline trustworthy for a government context.</div>
</div>

<div class="activity">
<div class="head"><span class="num">Task 2.2 alt</span><span class="file">&#128260; Cowork &#183; Variant B: pasted URL list (demo-friendly)</span></div>
<h4>Batch sweep - paste five URLs directly (simpler for live demos)</h4>
<p class="lead">For demos where the RSS folder is not set up, paste the five URLs from <code>04 Contoso_Sample_News_URLs.md</code> directly into the prompt. The same deduplication and communications logic applies.</p>
<div class="prompt">Goal: extract SPDP-style case data from the five article URLs below, deduplicate against my existing case register, and prepare a consolidated summary with communications drafts.

Context: I am Pak Bambang Kusumo, Head of the Coordination and Supervision Task Force at Contoso Integrity Bureau. I am running a manual OSINT sweep using a set of news URLs from my sample file.

Source:
1. https://jatim.antaranews.com/berita/261998/saksi-bpkp-sebut-kerugian-negara-korupsi-hibah-bansos-jember-capai-rp104-miliar
2. [paste URL 2 from 04 Contoso_Sample_News_URLs.md]
3. [paste URL 3]
4. [paste URL 4]
5. [paste URL 5]
Also: 03 Contoso_SPDP_Case_Register.xlsx (my OneDrive), sheet "Cases", existing rows.

Expectation: follow the same five steps as Variant A (extract, deduplicate, prepare rows, draft Teams message, draft email). Deduplication rule: same suspect names plus overlapping case period equals an existing case - do not append a new row; update the Notes column instead.

STOP before sending any message or email. Show me all drafts and the proposed new rows first. I will review and click send myself once I have verified the new SPDP rows.

Closing line: once I approve, this run replaces roughly 45 minutes of my morning routine.<button class="copy" onclick="cp(this)">Copy</button></div>
</div>

<div class="callout warn"><b>Reality Check &#183; Exercise 2.</b>
<br/><b>Researcher (Task 2.1):</b> fails on paywalled pages or JavaScript-heavy news sites that block server-side rendering. If Researcher cannot load the page, fall back to manually copying the article text and pasting it into the Copilot Chat window with the same extraction prompt.
<br/><b>Cowork (Task 2.2):</b> Cowork is on-demand only. There is no "run this every morning automatically" setting in Cowork. Pak Bambang re-runs the same prompt each morning. If the customer wants the sweep to run unattended on a schedule, that requires a different product tier (beyond pure M365 Copilot) - we are not selling that today.
<br/><b>Deduplication:</b> the deduplicate-by-suspect-plus-period rule works well for clear cases. For cases with multiple suspects listed differently across articles, manual review is still needed before the row is added to the register. Tingkat Keyakinan Rendah rows should always be reviewed by a human before filing.
<br/><b>Cowork is the customer's own term</b> from the Bahasa requirements document. That is exactly the capability we are demoing here.</div>
</div>
</section><div class="lab-nav-ihh"><button class="secondary" data-go="ex1">← Daily Briefing</button><button data-go="ex3">Next: Procurement Anomalies →</button></div></div>'''

VIEW_EX3 = '''<div class="view-ihh" id="view-ex3"><section id="ex3">
<div class="modulehead"><div class="num">3</div><h2>Exercise 3 &#183; Procurement Anomalies<small>Copilot in Excel &#183; Chat mode (Task 3.1) + Edit mode (Task 3.2) &#183; Flagship for Prevention</small></h2></div>
<div class="callout good"><b>Why this matters.</b> Provincial and regency governments submit Excel procurement disclosures every quarter. Buried in 180 rows of the Q3 file are the exact patterns the Task Force cares about: contracts split to stay under the direct-procurement threshold, one vendor dominating an agency, price outliers, brand-new vendors winning large awards, shared vendor addresses, and awards signed on Sundays. <b>Important:</b> the data and dashboard you build here are the direct input to Exercise 5 - that is where you turn this analysis into the Deputy briefing pack.</div>

<div class="card">
<p class="lead">Open <code>02 Contoso_Direct_Procurement_Q3.xlsx</code> in Excel. The file must be in a named Excel Table (select any cell, Insert - Table). This is required for Copilot in Excel to work. Click the <b>Copilot</b> icon in the ribbon.</p>

<div class="activity">
<div class="head"><span class="num">Task 3.1</span><span class="file">&#128202; Copilot in Excel &#183; Chat mode &#183; explore the data</span></div>
<h4>Four targeted Chat questions to surface the main patterns</h4>
<p class="lead">In the Copilot pane, make sure the mode is set to <b>Chat</b> (not Edit). Ask these four questions one at a time. Each takes about 20 seconds. Copy the results to a notes document as you go.</p>

<div class="task-step"><div class="step-label">Chat question 1 &#183; vendor concentration</div></div>
<div class="prompt">Which 5 vendors have the highest total contract value across all agencies in this file? Show vendor name, total value in IDR, number of contracts, and which agencies they appear in.<button class="copy" onclick="cp(this)">Copy</button></div>

<div class="task-step"><div class="step-label">Chat question 2 &#183; weekend awards</div></div>
<div class="prompt">List every contract in this file where the Award Date falls on a Saturday or Sunday and the Contract Value is above 500,000,000 IDR. Show Contract ID, Agency, Vendor Name, Contract Value IDR, and Award Date.<button class="copy" onclick="cp(this)">Copy</button></div>

<div class="task-step"><div class="step-label">Chat question 3 &#183; direct-award threshold clustering</div></div>
<div class="prompt">Which agencies have the most contracts with a Contract Value below 200,000,000 IDR? List the top 5 agencies by count of such contracts. The 200-million-IDR figure is the Indonesian direct-procurement threshold - contracts clustered just below it are a classic split-contract indicator.<button class="copy" onclick="cp(this)">Copy</button></div>

<div class="task-step"><div class="step-label">Chat question 4 &#183; shared vendor addresses</div></div>
<div class="prompt">Find vendor records where the same Vendor Address appears under two or more different Vendor Names. List the shared address, all Vendor Names that share it, and the total number of contracts and total IDR value for each vendor at that address.<button class="copy" onclick="cp(this)">Copy</button></div>

<div class="callout"><b>What success looks like:</b> four plain-language answers, each returned in under 30 seconds. The shared-address question may return 2-3 vendor clusters. Note the addresses and vendor names - these will show up again as flags in Task 3.2.</div>
</div>

<div class="activity">
<div class="head"><span class="num">Task 3.2</span><span class="file">&#128202; Copilot in Excel &#183; Edit mode &#183; build the risk layer and dashboard</span></div>
<h4>Add Risk_Score column and build the Governance Dashboard</h4>
<p class="lead">Switch the Copilot pane to <b>Edit</b> mode. Paste the prompt below. This is a single Edit prompt that adds the risk-scoring layer and creates the Governance Dashboard sheet. It may take up to two minutes to complete.</p>
<div class="prompt">Goal: add a risk-scoring layer and build a Governance Dashboard sheet for the Q3 procurement audit.

Context: I am Pak Bambang Kusumo, Head of the Coordination and Supervision Task Force. This file contains 180 direct-procurement contracts. The direct-award threshold under Indonesian rules is 200 million IDR. Contracts split just below that threshold by the same vendor at the same agency are a classic red flag.

Source: the Contracts table in this workbook. Columns: Contract ID, Procurement Year, Agency, Procurement Package Name, Vendor Name, Vendor Address, Vendor NPWP, Contract Value IDR, Award Date, Procurement Method, Contract Start, Contract End, Notes.

Expectation:
1. Add a Risk_Score column equal to the sum of these six signal columns (each returns 1 or 0):
   - Split_Contract_Flag: 1 if the same Vendor Name and Agency combination has 3 or more contracts each under 200,000,000 IDR within any rolling 30-day window by Award Date.
   - Vendor_Concentration_Flag: 1 if the vendor's total IDR value at that agency for Q3 exceeds 60 percent of that agency's total Q3 spend.
   - Price_Outlier_Flag: 1 if Contract Value IDR for a given Procurement Package Name is more than 2 times the median value for the same package name across all agencies.
   - New_Vendor_High_Value_Flag: 1 if the NPWP registration date in the Notes column is less than 6 months before the Award Date AND Contract Value IDR exceeds 1,000,000,000 IDR. If NPWP date cannot be parsed from Notes, leave as 0.
   - Shared_Address_Flag: 1 if the exact Vendor Address is shared by two or more different Vendor Names anywhere in the file.
   - Weekend_Award_Flag: 1 if Award Date falls on a Saturday or Sunday.
2. Add a Risk_Tier column: 0 = Clean, 1 to 2 = Watch, 3 to 4 = Elevated, 5 to 6 = Critical.
3. Apply conditional formatting to Risk_Score: green for 0, yellow for 1 to 2, orange for 3 to 4, red for 5 to 6.
4. Create a new sheet named "Governance Dashboard" with:
   - Title cell: "Q3 Procurement Governance Scorecard - Contoso Integrity Bureau".
   - An Agency slicer and a Risk_Tier slicer connected to the data.
   - A bar chart showing count of Critical-tier contracts per agency, sorted descending, with bars in deep navy.
   - A top-10 risk contracts callout table: Contract ID, Agency, Vendor Name, Contract Value IDR, Risk_Score, sorted by Risk_Score descending then Contract Value descending.
   - A "Where to look first" summary text box naming the single agency with the most Critical-tier contracts.

Rules: add columns to the right of the existing table. Do not delete any rows. Keep the Contracts sheet intact. If a flag formula cannot be computed, leave the flag as 0 and note this in a comment cell.<button class="copy" onclick="cp(this)">Copy</button></div>
<div class="callout"><b>What success looks like:</b> the Contracts sheet gains eight new columns (six flags, Risk_Score, Risk_Tier) with colour-coded conditional formatting. The Governance Dashboard sheet shows which agencies cluster in Elevated and Critical tiers, with the bar chart and top-10 callout table ready to be screenshot for a supervision letter.</div>
</div>

<div style="background:rgba(11,42,74,.08);border-left:4px solid #0B2A4A;border-radius:8px;padding:14px 18px;margin:12px 0">
<div style="font-size:12px;font-weight:700;color:#0B2A4A;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px">&#128279; Bridge to Exercise 5</div>
<p style="margin:0;font-size:14px;color:var(--ink);line-height:1.55">The risk-flagged workbook and Governance Dashboard sheet you just built in Exercise 3 are the direct input to Exercise 5. In Exercise 5, you will take this analysis and turn it into the Deputy for Enforcement briefing pack: a polished Word report (Task 5.1), an executive deck (Task 5.2), and a sharpened dashboard (Task 5.3). You can also see all three artefacts produced in one Cowork prompt (Task 5.4) so you understand the tradeoff between speed and iteration control.</p>
</div>

<div class="callout warn"><b>Reality Check &#183; Exercise 3.</b>
<br/><b>Table format is mandatory.</b> Copilot in Excel works only on named Excel Tables. If the file is not in Table format before you open Copilot, go to Insert - Table first.
<br/><b>Excel Plan mode:</b> this mode is still rolling out and may not be available on all tenants. If you do not see "Plan" as an option in the Copilot pane, it is not yet available on your tenant. Task 3.1 (Chat) and Task 3.2 (Edit) do not require Plan mode and will work on any M365 Copilot-enabled tenant.
<br/><b>Verify the formulas:</b> before you rely on Risk_Score for a supervision decision, spot-check three Critical-tier rows against the raw disclosure to confirm the flag formulas match the Bureau's official Q3 scoring rubric. Copilot builds the exhibit fast; the auditor still signs it.
<br/><b>Slicers:</b> interactive slicers sometimes need to be reapplied after a Copilot Edit run. If the slicer does not filter the chart, click the slicer connection icon on the chart and reconnect it manually.</div>
</div>
</section><div class="lab-nav-ihh"><button class="secondary" data-go="ex2">← OSINT Scraping + Sweep</button><button data-go="ex4">Next: Meeting Minutes →</button></div></div>'''

VIEW_EX5 = '''<div class="view-ihh" id="view-ex5"><section id="ex5">
<div class="modulehead"><div class="num">5</div><h2>Exercise 5 &#183; Analysis to Deliverable<small>Word + PowerPoint + Excel + Cowork &#183; Four tasks, one briefing pack</small></h2></div>
<div class="callout good"><b>The frame.</b> Take what you produced in Exercise 3 - the risk-flagged workbook and Governance Dashboard - and turn it into the Deputy for Enforcement briefing pack: a polished Word report, an executive deck, and a sharpened dashboard. Tasks 5.1 to 5.3 show the manual path, one artefact at a time. Task 5.4 shows the same three artefacts produced in one Cowork prompt so you can see the tradeoff between speed and per-artefact iteration control. Neither approach is "right" - the choice depends on how much manual polish the pack needs.</div>

<div class="card">
<div class="activity">
<div class="head"><span class="num">Task 5.1</span><span class="file">&#128221; Word Copilot &#183; polish the governance report</span></div>
<h4>Turn the Q3 draft into a board-ready governance report</h4>
<p class="lead">Open <code>05 Contoso_Governance_Report_Draft.docx</code> in Word. Click the Copilot icon, then Draft with Copilot or Rewrite. Paste the prompt below. <b>Note:</b> you must type the risk numbers from Exercise 3 into the prompt text - Word Copilot cannot read the Excel file directly.</p>
<div class="prompt">Goal: polish this Q3 governance report so it reads like a Task Force board paper, not a working draft.

Context: I am Pak Bambang Kusumo, Head of the Coordination and Supervision Task Force. This report goes to the Bureau leadership meeting on Friday. It covers procurement supervision findings across three provinces for Q3. From my Exercise 3 analysis: 12 contracts are at Critical tier, 31 contracts are at Elevated tier, across 7 agencies, with a combined value at risk of approximately IDR 18.4 billion.

Source: use only the content already in this Word document, plus the risk numbers I have provided above.

Expectation:
1. Improve clarity and readability throughout - shorten wordy phrases, remove redundant sentences, replace jargon with plain language that a legal advisor with no procurement background can follow.
2. Rewrite to a professional Bureau house style: neutral third-person voice, active verbs, no informal phrases.
3. Add a two-page executive summary immediately after the report title, structured as three paragraphs: (a) the single most important finding; (b) the two next-most-important findings with the risk numbers I provided above; (c) the one decision the Bureau leadership meeting is being asked to make.
4. Rewrite each section heading as an action title that states the conclusion (for example, instead of "Findings", write "Seven agencies show contract patterns requiring supervision escalation").

Rules: do not add any figures, agency names, or vendor names not already in the document or in the risk numbers I supplied. If a claim in the document is not backed by data in the document, flag it inline with "(source not stated in draft)".<button class="copy" onclick="cp(this)">Copy</button></div>
<div class="callout"><b>What success looks like:</b> action-title headings, a three-paragraph executive summary on page one referencing the risk numbers, improved sentence clarity throughout. The report should read like a filing-ready board paper.</div>
</div>

<div class="activity">
<div class="head"><span class="num">Task 5.2</span><span class="file">&#127775; PowerPoint Copilot &#183; deck from the polished Word doc</span></div>
<h4>Auto-generate the deck, then run a critique-and-rewrite pass</h4>
<p class="lead">Open PowerPoint. In Copilot, choose <b>"Create presentation from file"</b> and point it at the polished <code>05 Contoso_Governance_Report_Draft.docx</code> from Task 5.1. After the deck is generated, run the prompt below as a critique-and-rewrite pass to style and tighten it.</p>
<div class="prompt">Goal: turn this auto-generated deck into the Deputy for Enforcement briefing pack - branded, eight slides maximum, one clear message per slide.

Context: I am Pak Bambang Kusumo, Head of the Coordination and Supervision Task Force. I am presenting to the Bureau leadership meeting on Friday. Twenty minutes, eight slides maximum. Audience includes two Deputies and the Bureau Secretariat.

Source: the deck you just generated from 05 Contoso_Governance_Report_Draft.docx (the polished version).

Expectation:
1. Rewrite every slide title into action-title format: state the conclusion, not the topic. No topic headings like "Findings" - replace with "Seven agencies exceed the anomaly threshold in Q3".
2. Each body slide must have one key message only. If a slide has more than one main point, split it.
3. Apply a colour scheme using deep navy blue for headings and section dividers, institutional gold as the accent colour for callouts and key numbers, and muted grey body text on white. Do not use bright reds or greens.
4. Add speaker notes to each body slide - three short bullets that a presenter can read in 30 seconds.
5. Keep the slide count at or below eight, excluding the title slide and any appendix.

Rules: do not invent numbers not in the Word document. Do not change any agency name. If a slide cannot be generated from the document content, leave a placeholder with a note stating "(content needed)".<button class="copy" onclick="cp(this)">Copy</button></div>
<div class="callout warn"><b>Important sequence:</b> PowerPoint Copilot "Create presentation from file" respects the Word document heading structure. Always run Task 5.1 first (polish the Word doc and save it), then feed the polished file to PowerPoint. If you feed it the original unpolished draft, the deck inherits the weak topic-only headings. Also: PowerPoint Copilot cannot read Excel directly - the risk numbers must be in the Word document body already, not in a linked spreadsheet.</div>
</div>

<div class="activity">
<div class="head"><span class="num">Task 5.3</span><span class="file">&#128202; Excel Copilot &#183; Edit &#183; sharpen the dashboard for the data slide</span></div>
<h4>Make the Governance Dashboard screenshot-ready for the deck</h4>
<p class="lead">Go back to <code>02 Contoso_Direct_Procurement_Q3.xlsx</code>. Navigate to the Governance Dashboard sheet built in Exercise 3. Open Copilot in Excel in Edit mode. Paste the prompt below.</p>
<div class="prompt">Goal: sharpen the Governance Dashboard sheet so it is screenshot-ready for inclusion in the leadership briefing pack.

Context: I am Pak Bambang Kusumo, Head of the Coordination and Supervision Task Force. The dashboard needs to look like a finished audit exhibit, not a working spreadsheet.

Source: the Governance Dashboard sheet in 02 Contoso_Direct_Procurement_Q3.xlsx.

Expectation:
1. Add a KPI callout row at the top of the dashboard with four cells in a row: Total Contracts Reviewed, Total IDR Value (formatted in billions with one decimal place), Critical-Tier Count, Agencies with Critical Contracts. Format each cell with a bold large number on top and a short label below in smaller font.
2. Format all IDR value cells in the dashboard as millions with thousand separators (for example, "18,400" represents 18.4 billion IDR). Add an "(IDR millions)" label to each column header that contains a monetary value.
3. Add a text box at the bottom of the dashboard with this text: "Source: 02 Contoso_Direct_Procurement_Q3.xlsx - Contracts sheet. Risk scoring by Copilot in Excel. Review date: [today's date]. For Task Force internal use only."

Rules: do not delete any existing data, chart, or slicer. Only add the KPI row, reformat the monetary columns, and add the source text box.<button class="copy" onclick="cp(this)">Copy</button></div>
</div>

<div class="activity">
<div class="head"><span class="num">Task 5.4</span><span class="file">&#128260; Cowork &#183; one prompt for the whole briefing pack</span></div>
<h4>The Cowork alternative: Tasks 5.1 + 5.2 + 5.3 in one prompt</h4>
<p class="lead">This is the same three artefacts (polished Word report, PowerPoint deck, sharpened Excel dashboard) produced in one Cowork session. Run this after seeing the manual path in Tasks 5.1 to 5.3 so you can compare the tradeoff.</p>
<div class="prompt">Goal: produce the complete Q3 supervision briefing pack in one run - a polished Word report, a brand-styled PowerPoint deck, and a sharpened Excel dashboard.

Context: I am Pak Bambang Kusumo, Head of the Coordination and Supervision Task Force. I am preparing for the Bureau leadership meeting on Friday. From my Exercise 3 analysis: 12 Critical-tier contracts, 31 Elevated-tier contracts, 7 flagged agencies, combined value at risk approximately IDR 18.4 billion.

Source:
- Word: 05 Contoso_Governance_Report_Draft.docx (working draft to be polished, on my OneDrive).
- Excel: 02 Contoso_Direct_Procurement_Q3.xlsx, Governance Dashboard sheet (built in Exercise 3, on my OneDrive).

Expectation:
1. Polish the Word report: improve clarity and readability, rewrite to Bureau house style, add a two-page executive summary referencing the risk numbers above, rewrite headings as action titles. Save the polished version as "05 Contoso_Governance_Report_Polished.docx" in the same OneDrive folder.
2. Create a PowerPoint deck from the polished Word file using Create presentation from file. Apply deep navy headings, institutional gold accents, maximum eight slides. Rewrite all slide titles as action titles. Add three-bullet speaker notes to each body slide. Save as "05 Contoso_Governance_Deck.pptx" in the same OneDrive folder.
3. Sharpen the Governance Dashboard in the Excel file: add a KPI callout row at the top with four numbers, format IDR values in millions with thousand separators, add a source text box at the bottom.

STOP after completing all three artefacts. Show me a one-paragraph summary of what was produced and the three file links before I review.<button class="copy" onclick="cp(this)">Copy</button></div>

<div style="background:rgba(200,155,60,.1);border-left:4px solid #C89B3C;border-radius:8px;padding:14px 18px;margin:10px 0">
<div style="font-size:12px;font-weight:700;color:#C89B3C;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px">The Tradeoff</div>
<p style="margin:0;font-size:14px;color:var(--ink);line-height:1.55"><b>Cowork (Task 5.4):</b> faster - one prompt, three artefacts in sequence, no switching between apps. But you lose the per-artefact iteration control you get in Tasks 5.1 to 5.3. If the Word polish is not quite right, you cannot easily re-run just that step without restarting the whole Cowork session.</p>
<p style="margin:8px 0 0;font-size:14px;color:var(--ink);line-height:1.55"><b>Manual path (Tasks 5.1 to 5.3):</b> more steps, but you can inspect and refine each artefact before moving to the next. If the Pack is going to the Deputy for Enforcement, the manual path gives you the review checkpoints you want. Neither approach is wrong - the choice depends on how much polish the pack needs and how much time you have.</p>
</div>
</div>

<div class="callout warn"><b>Reality Check &#183; Exercise 5.</b>
<br/><b>PowerPoint cannot read Excel directly.</b> To get the risk numbers into the deck, they must be in the Word document body first. Always run Task 5.1 (polish Word, including the risk numbers) before Task 5.2 (generate deck from Word). You cannot skip Word and go straight from Excel to PowerPoint.
<br/><b>Word Copilot cannot read Excel.</b> The risk numbers (12 Critical-tier, 31 Elevated, 7 agencies, IDR 18.4 billion) were typed into the Task 5.1 prompt explicitly. If your real numbers from Exercise 3 are different, update the prompt text before running.
<br/><b>Copilot Create outputs are flat images.</b> If you use Copilot Create (Bonus B0) to generate a governance poster for the leadership wall, that output is a printable image, not an editable PowerPoint slide. Do not expect to edit it in PowerPoint.
<br/><b>Cowork is on-demand only.</b> Task 5.4 is a single on-demand Cowork run. There is no "generate the briefing pack automatically every week" setting in Cowork. Pak Bambang runs it each time he needs the pack.</div>
</div>
</section><div class="lab-nav-ihh"><button class="secondary" data-go="ex4">← Meeting Minutes</button><button data-go="ex6">Next: Build Your Own Agent →</button></div></div>'''

VIEW_EX6 = '''<div class="view-ihh" id="view-ex6"><section id="ex6">
<div class="modulehead"><div class="num">6</div><h2>Exercise 6 &#183; Build Your Own Agent<small>Copilot Chat agent builder &#183; Declarative &#183; No Copilot Studio licence needed</small></h2></div>
<div class="callout good"><b>The finale.</b> Build a declarative Copilot Chat agent grounded on the two key Task Force data files. Any member of the Task Force can then ask natural-language questions against the procurement register and the SPDP case register without opening Excel. No code, no tool calls, no Copilot Studio licence.</div>

<div class="card">
<p class="lead">Before you start, upload <code>02 Contoso_Direct_Procurement_Q3.xlsx</code> and <code>03 Contoso_SPDP_Case_Register.xlsx</code> to a SharePoint site the Task Force team has access to. Note the SharePoint URLs for both files - you will need them as grounding sources. Optionally also upload <code>01 Contoso_Task_Force_Overview.docx</code> as a glossary context file.</p>

<div class="activity">
<div class="head"><span class="num">Step 1</span><span class="file">&#128172; Copilot Chat &#183; Open the agent builder</span></div>
<h4>Start the agent builder in Copilot Chat</h4>
<p class="lead">Open Microsoft 365 Copilot at <a href="https://copilot.microsoft.com" target="_blank">copilot.microsoft.com</a>. In the left panel, look for <b>Agents</b> or the pencil/create icon. Select <b>"Create an agent"</b> or <b>"Build your own agent"</b>. You will be taken to the agent builder interface. No Copilot Studio licence is required - this is the built-in agent builder in Copilot Chat.</p>
</div>

<div class="activity">
<div class="head"><span class="num">Step 2</span><span class="file">&#128172; Agent configuration</span></div>
<h4>Name, instructions, and grounding sources</h4>
<p class="lead">Fill in the agent configuration fields as shown below. Copy the instructions text and paste it into the "Instructions" field of the agent builder.</p>

<div class="task-step"><div class="step-label">Agent name</div></div>
<div class="prompt">Korsup Integrity Analyst<button class="copy" onclick="cp(this)">Copy</button></div>

<div class="task-step"><div class="step-label">Agent description</div></div>
<div class="prompt">A data assistant for the Coordination and Supervision Task Force. Answers questions about Q3 procurement contracts and SPDP corruption cases grounded on the two Task Force register files.<button class="copy" onclick="cp(this)">Copy</button></div>

<div class="task-step"><div class="step-label">Agent instructions (paste into the Instructions field)</div></div>
<div class="prompt">You are the Korsup Integrity Analyst, a data assistant for the Coordination and Supervision Task Force at Contoso Integrity Bureau.

Your role: answer questions about procurement contracts and SPDP corruption cases using only the grounded data sources provided. Do not use general knowledge about Indonesian corruption cases beyond what is in the files.

Voice and style: neutral, precise, government-audit register. Respond in the same language as the question (Indonesian or English). Always cite the specific row ID or cell reference that supports your answer (for example: "Contracts row 47, Contract ID CON-2025-047"). Flag any data quality issues you notice, such as missing values, inconsistent formats, or apparent duplicate entries.

If the answer requires information not in the grounded files, say: "Data ini tidak tersedia di register saya" (this data is not available in my register).

Rules: cite specific rows and cells for every factual claim. Do not guess. Do not name individuals not already in the data files. If a question requires a judgment call, present the relevant data and let the Task Force Head decide.<button class="copy" onclick="cp(this)">Copy</button></div>

<div class="task-step"><div class="step-label">Grounding sources - add these in the Knowledge section</div></div>
<p class="lead">In the agent builder Knowledge section, click "Add" and paste the SharePoint URLs for each file:</p>
<ul>
<li><code>02 Contoso_Direct_Procurement_Q3.xlsx</code> - the Q3 procurement register with Risk_Score column from Exercise 3</li>
<li><code>03 Contoso_SPDP_Case_Register.xlsx</code> - the SPDP case tracker</li>
<li><code>01 Contoso_Task_Force_Overview.docx</code> - optional, provides glossary context for terminology</li>
</ul>
</div>

<div class="activity">
<div class="head"><span class="num">Step 3</span><span class="file">&#128172; Starter prompts &#183; four pre-built questions</span></div>
<h4>Add four starter prompts so the Task Force can use the agent immediately</h4>
<p class="lead">In the agent builder, look for the "Starter prompts" or "Conversation starters" section. Add these four prompts one at a time. They will appear as clickable buttons when any team member opens the agent.</p>

<div class="task-step"><div class="step-label">Starter prompt 1</div></div>
<div class="prompt">Which agency has the most Critical-tier contracts this quarter? Show me the agency name, the count of Critical-tier contracts, and the total IDR value.<button class="copy" onclick="cp(this)">Copy</button></div>

<div class="task-step"><div class="step-label">Starter prompt 2</div></div>
<div class="prompt">Show every contract signed on a Saturday or Sunday with a Contract Value over 500 million IDR. List Contract ID, Agency, Vendor Name, Contract Value IDR, and Award Date.<button class="copy" onclick="cp(this)">Copy</button></div>

<div class="task-step"><div class="step-label">Starter prompt 3</div></div>
<div class="prompt">List vendors whose Vendor Address appears under two or more different Vendor Names in the procurement register. Show the shared address, all vendor names, and total contract count and total IDR value for each.<button class="copy" onclick="cp(this)">Copy</button></div>

<div class="task-step"><div class="step-label">Starter prompt 4</div></div>
<div class="prompt">Which SPDP cases in the case register have no update note in the last 30 days? Cross-reference these against the procurement register: do any of the suspects or agency names in those stalled SPDP cases also appear as vendors or agencies in the Critical-tier contracts?<button class="copy" onclick="cp(this)">Copy</button></div>
</div>

<div class="activity">
<div class="head"><span class="num">Step 4</span><span class="file">&#128172; Share &#183; make it available to the Task Force team</span></div>
<h4>Share the agent with the Task Force</h4>
<p class="lead">Once you have saved and tested the agent, use the Share button in the agent builder to share it with your Task Force Microsoft Teams team or specific individuals. Team members will be able to find the agent in their Copilot Chat agents list and start using the four starter prompts immediately.</p>
</div>

<div class="callout warn"><b>Reality Check &#183; Exercise 6.</b>
<br/><b>Declarative agents are grounded Q and A only.</b> The Korsup Integrity Analyst will answer questions about data in the grounded files. It will not autonomously scan for new anomalies, send alerts, or run overnight. Every interaction requires a human to ask a question.
<br/><b>No autonomous overnight runs.</b> If the customer wants the agent to "detect anomalies overnight and send a Teams alert", that is a different product category - Copilot Studio autonomous agents, which is on the Microsoft roadmap. We are not selling that today.
<br/><b>No code, no tool calls.</b> The agent builder in Copilot Chat produces declarative agents only: instructions plus grounding sources plus starter prompts. There are no API calls, no code execution, no loops.
<br/><b>Grounding freshness:</b> the agent reads the files as they exist in SharePoint at the time of each conversation. If you update the Excel files with new data, the agent picks up the new data automatically on the next conversation - no rebuild needed.
<br/><b>Scope of answers:</b> the agent can only answer questions about data explicitly present in the grounded files. It cannot query SPDP Online directly, browse the web for news, or access files not in the grounding sources list.</div>
</div>
</section><div class="lab-nav-ihh"><button class="secondary" data-go="ex5">← Analysis to Deliverable</button><button data-go="extras">Next: Bonus →</button></div></div>'''

VIEW_EXTRAS = '''<div class="view-ihh" id="view-extras"><section id="extras">
<div class="modulehead"><div class="num">+</div><h2>Bonus Tab<small>Governance posters + five more Copilot moves for the Task Force</small></h2></div>
<div class="callout good"><b>What lives here.</b> Four Copilot Create governance poster prompts (B0), the G-C-S-E prompt framework card (B1), two Outlook Copilot moves (B2, B3), a Word interrogation prompt (B4), and a pre-send fact-check prompt (B5).</div>

<div class="bonus-grid"><button class="bcard" onclick="openModal('kx-b56798a9')"><span class="ico">&#127912;</span><h4>B0 &#183; Governance Poster (Copilot Create &#183; four prompts)</h4><p>Open Copilot Create. Paste any of the four prompts to generate a bureau-branded infographic: Q3 priorities, case journey strip, regional heatmap, or year-in-review poster. Outputs are flat images, not editable slides.</p></button><button class="bcard" onclick="openModal('kx-new-b1')"><span class="ico">&#128196;</span><h4>B1 &#183; Prompt tips card (G-C-S-E framework)</h4><p>The Goal, Context, Source, Expectation framework used across all major prompts in this immersion. Copy it into any prompt you write.</p></button><button class="bcard" onclick="openModal('kx-new-b2')"><span class="ico">&#128236;</span><h4>B2 &#183; Outlook Copilot &#183; catch up on a long thread</h4><p>In Outlook, open the longest unread email thread. Copilot summarises it and drafts a reply in Bureau tone.</p></button><button class="bcard" onclick="openModal('kx-new-b3')"><span class="ico">&#8617;&#65039;</span><h4>B3 &#183; Outlook Copilot &#183; draft an executive reply</h4><p>Draft a reply from the Task Force Head to the Deputy for Prevention. Formal, four sentences, specific date commitment.</p></button><button class="bcard" onclick="openModal('kx-new-b4')"><span class="ico">&#128214;</span><h4>B4 &#183; Word &#183; interrogate a long governance report</h4><p>Five questions to ask Copilot about any Word document before you present it. Finds weak claims, number conflicts, and missing sections.</p></button><button class="bcard" onclick="openModal('kx-new-b5')"><span class="ico">&#9989;</span><h4>B5 &#183; Copilot Chat &#183; quick fact check before you send</h4><p>Paste any paragraph or table into Copilot Chat before sending. Returns a "cleared" or "revise" verdict with source citations.</p></button></div>
</section><div class="lab-nav-ihh"><button class="secondary" data-go="ex6">&#8592; Build Your Own Agent</button><button data-go="intro">Back to start &#8634;</button></div></div>'''

# Bonus modals B1-B5 are already extracted with correct IDs from current index.html
NEW_MODAL_B1 = modal_b1
NEW_MODAL_B2 = modal_b2
NEW_MODAL_B3 = modal_b3
NEW_MODAL_B4 = modal_b4
NEW_MODAL_B5 = modal_b5

# ── Assemble the new HTML ──────────────────────────────────────────────────────

LAYOUT = (
    '<div class="layout" id="main" style="display:none">\n'
    + SIDEBAR + '\n'
    + '<main>\n'
    + '<!--IHH-INJECT-START-->\n'
    + HERO + '\n'
    + TABS + '<div class="ihh-main">'
    + VIEW_INTRO
    + VIEW_FILES
    + VIEW_EX1
    + VIEW_EX2
    + VIEW_EX3
    + ex4_raw
    + VIEW_EX5
    + VIEW_EX6
    + VIEW_EXTRAS
    + '</div>\n'  # closes ihh-main
    + '\n'
    + session_footer + '\n'
    + '</main>\n</div>\n'  # closes main + layout
    + '\n'
    + modal_b0
    + NEW_MODAL_B1
    + NEW_MODAL_B2
    + NEW_MODAL_B3
    + NEW_MODAL_B4
    + NEW_MODAL_B5
    + '\n'
)

new_html = (
    head
    + '\n'
    + lock_section
    + LAYOUT
    + footer_scripts
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print('Done. index.html written.')

# Quick validation
txt = new_html
em_count = txt.count('\u2014') + txt.count('\u2013')
print(f'Em/en dash count: {em_count}')

open_divs = txt.count('<div')
close_divs = txt.count('</div>')
print(f'<div count: {open_divs}, </div> count: {close_divs}, diff: {open_divs - close_divs}')

import re
hex_in_prompts = re.findall(r'#[0-9a-fA-F]{6}', txt)
# Filter out CSS hex codes (in style attributes or <style> tags)
# We want to check only inside .prompt divs
prompt_sections = re.findall(r'<div class="prompt">(.*?)</div>', txt, re.DOTALL)
hex_in_prompt_content = []
for p in prompt_sections:
    found = re.findall(r'#[0-9a-fA-F]{6}', p)
    if found:
        hex_in_prompt_content.extend(found)
print(f'Hex codes in prompt content: {hex_in_prompt_content}')
