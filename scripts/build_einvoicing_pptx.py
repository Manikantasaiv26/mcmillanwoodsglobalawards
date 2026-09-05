#!/usr/bin/env python3
"""Build McMillan Woods e-invoicing architecture PowerPoint."""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

# Brand (from mcmillanwoods.com: red / maroon / white / black)
MAROON = RGBColor(0x8B, 0x1A, 0x1A)
MAROON_DARK = RGBColor(0x5C, 0x0F, 0x12)
BLACK = RGBColor(0x14, 0x14, 0x14)
CHARCOAL = RGBColor(0x2B, 0x2B, 0x2B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
OFFWHITE = RGBColor(0xF7, 0xF4, 0xF2)
GOLD = RGBColor(0xC4, 0xA3, 0x5A)
GRAY = RGBColor(0x5A, 0x5A, 0x5A)
LIGHT_GRAY = RGBColor(0xE8, 0xE2, 0xDC)
MUTED = RGBColor(0x6E, 0x6A, 0x66)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

FONT = "Calibri"
FONT_SERIF = "Georgia"


def set_run(run, text, size, color, bold=False, font=FONT, italic=False):
    run.text = text
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font


def add_text_box(slide, l, t, w, h, text, size, color, bold=False, font=FONT, align=PP_ALIGN.LEFT, italic=False, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    try:
        tf._txBody.bodyPr.set("anchor", {MSO_ANCHOR.TOP: "t", MSO_ANCHOR.MIDDLE: "ctr", MSO_ANCHOR.BOTTOM: "b"}[anchor])
    except Exception:
        pass
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    set_run(run, text, size, color, bold, font, italic)
    return box


def _ensure_run(p):
    if p.runs:
        return p.runs[0]
    return p.add_run()


def fill_shape(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def rect(slide, l, t, w, h, color):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    fill_shape(s, color)
    return s


def round_rect(slide, l, t, w, h, color):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    fill_shape(s, color)
    # tighter corners
    try:
        s.adjustments[0] = 0.08
    except Exception:
        pass
    return s


def footer(slide, page, total=16):
    rect(slide, 0, Inches(7.22), SLIDE_W, Inches(0.28), MAROON_DARK)
    add_text_box(
        slide, Inches(0.5), Inches(7.22), Inches(9.5), Inches(0.28),
        "McMillan Woods  |  Confidential  |  E-Invoice Cloud  |  September 2026",
        10, WHITE, font=FONT, anchor=MSO_ANCHOR.MIDDLE,
    )
    add_text_box(
        slide, Inches(11.4), Inches(7.22), Inches(1.5), Inches(0.28),
        f"{page}  /  {total}",
        10, WHITE, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE,
    )


def header_bar(slide, kicker="McM Invoice Cloud"):
    rect(slide, 0, 0, SLIDE_W, Inches(0.12), MAROON)
    add_text_box(slide, Inches(0.5), Inches(0.22), Inches(8), Inches(0.28), kicker, 11, MAROON, bold=True)
    add_text_box(
        slide, Inches(8.5), Inches(0.22), Inches(4.3), Inches(0.28),
        "TAX  ·  AUDIT  ·  ADVISORY",
        11, GOLD, align=PP_ALIGN.RIGHT, bold=True,
    )


def title_block(slide, title, subtitle=None):
    header_bar(slide)
    add_text_box(slide, Inches(0.5), Inches(0.48), Inches(12.3), Inches(0.5), title, 28, BLACK, bold=True, font=FONT_SERIF)
    rect(slide, Inches(0.5), Inches(1.02), Inches(1.4), Inches(0.06), MAROON)
    if subtitle:
        add_text_box(slide, Inches(0.5), Inches(1.12), Inches(12.3), Inches(0.36), subtitle, 14, GRAY, italic=True)


def card(slide, l, t, w, h, title, body, title_size=15, body_size=12):
    round_rect(slide, l, t, w, h, WHITE)
    # left accent
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, Inches(0.08), h)
    fill_shape(r, MAROON)
    add_text_box(slide, l + Inches(0.22), t + Inches(0.12), w - Inches(0.34), Inches(0.36), title, title_size, MAROON, bold=True)
    box = slide.shapes.add_textbox(l + Inches(0.22), t + Inches(0.48), w - Inches(0.34), h - Inches(0.58))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    set_run(_ensure_run(p), body, body_size, CHARCOAL)
    return box


def bullets(slide, l, t, w, h, items, size=15, color=CHARCOAL, spacing=8):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = 0
        p.space_after = Pt(spacing)
        run = _ensure_run(p)
        set_run(run, "▸  " + item, size, color)
    return box


def add_table(slide, l, t, w, h, rows, col_w=None, header=True):
    table_shape = slide.shapes.add_table(len(rows), len(rows[0]), l, t, w, h)
    table = table_shape.table
    if col_w:
        for i, cw in enumerate(col_w):
            table.columns[i].width = cw
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            is_header = header and r_idx == 0
            set_run(
                _ensure_run(p),
                val,
                12 if is_header else 12,
                WHITE if is_header else CHARCOAL,
                bold=is_header,
            )
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            fill = MAROON if is_header else (OFFWHITE if r_idx % 2 == 0 else WHITE)
            cell.fill.solid()
            cell.fill.fore_color.rgb = fill
            try:
                cell.margin_left = Inches(0.08)
                cell.margin_right = Inches(0.08)
                cell.margin_top = Inches(0.05)
                cell.margin_bottom = Inches(0.05)
            except Exception:
                pass
    return table_shape


def blank_slide(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    rect(slide, 0, 0, SLIDE_W, SLIDE_H, OFFWHITE)
    return slide


def build():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    total = 16

    # ----- 1 Title -----
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, SLIDE_W, SLIDE_H, BLACK)
    rect(s, 0, 0, Inches(0.22), SLIDE_H, MAROON)
    rect(s, 0, Inches(6.85), SLIDE_W, Inches(0.65), MAROON_DARK)
    add_text_box(s, Inches(0.7), Inches(1.15), Inches(11.5), Inches(0.35), "McMILLAN WOODS WORLDWIDE", 14, GOLD, bold=True)
    add_text_box(
        s, Inches(0.7), Inches(1.55), Inches(12), Inches(1.5),
        "E-Invoice Cloud",
        48, WHITE, bold=True, font=FONT_SERIF,
    )
    add_text_box(
        s, Inches(0.7), Inches(3.15), Inches(11.5), Inches(0.9),
        "Paperless invoicing for every domain — payroll, logistics,\nmanufacturing, trading and SCM — on Amazon Web Services",
        20, LIGHT_GRAY,
    )
    add_text_box(
        s, Inches(0.7), Inches(4.4), Inches(11.5), Inches(0.4),
        "TAX  ·  AUDIT  ·  ADVISORY     ·     Professionalism at the Forefront",
        14, GOLD, bold=True,
    )
    add_text_box(
        s, Inches(0.7), Inches(5.2), Inches(11.5), Inches(0.7),
        "Architecture and delivery plan  ·  90 / 180 / 270–360 days\nPrepared from mcmillanwoods.com  ·  5 September 2026",
        15, RGBColor(0xC8, 0xC8, 0xC8),
    )
    add_text_box(
        s, Inches(0.7), Inches(6.95), Inches(12), Inches(0.4),
        "Global association of independent firms  ·  77+ countries  ·  250+ offices  ·  3,200+ staff",
        13, WHITE, anchor=MSO_ANCHOR.MIDDLE,
    )

    # ----- 2 Direct answer -----
    s = blank_slide(prs)
    title_block(s, "How long will this take?", "Direct answer — this is not a few-day build. AWS is ready; tax-authority clearance is the bottleneck.")
    metrics = [
        ("90 days", "Go-live #1", "One country (India GST or Malaysia MyInvois).\nOne domain (trading B2B).\nThousands of invoices per day.\nThree named pilot clients."),
        ("180 days", "Multi-domain", "Payroll-adjacent, logistics,\nmanufacturing, trading, SCM.\nLakhs of invoices per day.\nOps search and tracking."),
        ("270–360 days", "Network GA", "250+ member firms as tenants.\nTwo countries live.\nCrore-scale aggregate analytics.\nSOC 2 and disaster recovery."),
    ]
    for i, (n, h, b) in enumerate(metrics):
        x = Inches(0.5) + i * Inches(4.2)
        round_rect(s, x, Inches(1.65), Inches(3.95), Inches(4.85), WHITE)
        rect(s, x, Inches(1.65), Inches(3.95), Inches(1.35), MAROON if i == 0 else MAROON_DARK)
        add_text_box(s, x + Inches(0.2), Inches(1.72), Inches(3.55), Inches(0.7), n, 32, WHITE, bold=True, font=FONT_SERIF)
        add_text_box(s, x + Inches(0.2), Inches(2.38), Inches(3.55), Inches(0.45), h, 16, GOLD, bold=True)
        add_text_box(s, x + Inches(0.25), Inches(3.2), Inches(3.45), Inches(3.0), b, 15, CHARCOAL)
    footer(s, 2, total)

    # ----- 3 What McM is -----
    s = blank_slide(prs)
    title_block(s, "What the website tells us", "McMillan Woods is not a software vendor. It is a global association of independent CA and advisory firms.")
    facts = [
        ("Independent firms", "No equity in each other. Firm A must never see Firm B’s invoices. Secretariat operates; it does not own client data."),
        ("Services already in house", "Bookkeeping, payroll, GST/VAT returns, outsourcing for start-ups and foreign-owned companies."),
        ("ERP reality", "Member firms already sit on Tally, SAP, Dynamics, Xero, QuickBooks — connectors are first-class work, not an afterthought."),
        ("Malaysia head-start", "June 2024 seminar “Beyond e-Invoice Compliance in Malaysia” with YGL-World. Wrap partners; do not rebuild them on Day 1."),
    ]
    for i, (h, b) in enumerate(facts):
        col = i % 2
        row = i // 2
        card(s, Inches(0.5) + col * Inches(6.35), Inches(1.6) + row * Inches(2.5), Inches(6.1), Inches(2.3), h, b, 16, 14)
    footer(s, 3, total)

    # ----- 4 Positioning -----
    s = blank_slide(prs)
    title_block(s, "Product positioning", "Member firms keep the client relationship. The platform is the engine.")
    round_rect(s, Inches(0.5), Inches(1.6), Inches(12.3), Inches(1.7), WHITE)
    add_text_box(
        s, Inches(0.75), Inches(1.8), Inches(11.8), Inches(1.35),
        "McMillan Woods E-Invoice Cloud is the shared compliance fabric: ingest from payroll, ERP, WMS and TMS  →  validate  →  clear with the tax authority  →  store IRN / UIN / QR  →  track every document at thousands-to-lakhs scale  →  feed books, GST/VAT returns and audit.",
        16, CHARCOAL,
    )
    roles = [
        ("ASP (McM platform)", "Application layer, portals, tracking, domain packs. This is what we build."),
        ("GSP / MyInvois partner", "Licensed pipe to NIC IRP (India) and LHDN (Malaysia). Contract in week 1. YGL is the existing MY option."),
        ("Taxpayer", "Client legal entity (GSTIN / TIN / BRN). Onboarded by the member firm."),
        ("Member firm", "Tenant. Issues invoices as outsourced accountant. Owns the engagement letter."),
    ]
    for i, (h, b) in enumerate(roles):
        card(s, Inches(0.5) + i * Inches(3.18), Inches(3.55), Inches(3.05), Inches(3.05), h, b, 14, 13)
    footer(s, 4, total)

    # ----- 5 Domains -----
    s = blank_slide(prs)
    title_block(s, "E-invoicing across all domains", "Salary itself is not a GST / MyInvois supply. Adjacent documents are. Paper is already not a legal invoice.")
    rows = [
        ["Domain", "What becomes an e-invoice", "Volume pattern"],
        ["Professional / McM AR", "Fee invoices, retainers, disbursements", "Hundreds–thousands / day per firm"],
        ["Payroll-adjacent", "Contractors, reimbursements, MY perquisites, employee-on-behalf expenses", "Month-end spike"],
        ["Trading", "B2B tax invoices, credit/debit notes, MY B2C consolidated", "Thousands–lakhs / day"],
        ["Manufacturing", "Finished goods, job-work, scrap, returns tied to original IRN", "HSN-heavy thousands / day"],
        ["Logistics / 3PL", "Freight, warehouse, detention — gated on proof of delivery", "Event-driven bursts"],
        ["SCM / procurement", "Self-billed imports, agents/dealers, individual sellers", "Inbound spike"],
    ]
    add_table(
        s, Inches(0.5), Inches(1.55), Inches(12.3), Inches(5.35),
        rows,
        col_w=[Inches(2.6), Inches(6.3), Inches(3.4)],
    )
    footer(s, 5, total)

    # ----- 6 Two markets -----
    s = blank_slide(prs)
    title_block(s, "Two clearance regimes first", "Pick the market where the first paying clients sit. Second country in Phase 5 — not Day 90.")
    # India card
    round_rect(s, Inches(0.5), Inches(1.6), Inches(6.1), Inches(5.15), WHITE)
    rect(s, Inches(0.5), Inches(1.6), Inches(6.1), Inches(0.7), MAROON)
    add_text_box(s, Inches(0.7), Inches(1.7), Inches(5.7), Inches(0.5), "India  ·  GST  ·  NIC IRP", 20, WHITE, bold=True, font=FONT_SERIF)
    bullets(s, Inches(0.75), Inches(2.5), Inches(5.55), Inches(4.0), [
        "Legal invoice = JSON registered on IRP",
        "Returns IRN (hash) + signed QR on the print copy",
        "Invoice, credit note, debit note; optional e-way bill by IRN",
        "Idempotent key: GSTIN + FY + doc type + number",
        "Duplicate IRN (error 2150) = treat as success",
        "McM is ASP on a licensed GSP — do not become a GSP in v1",
        "Auth token ~6 hours; per-GSTIN rate limit ~100–500/min",
    ], 14, CHARCOAL, 6)
    # Malaysia card
    round_rect(s, Inches(6.8), Inches(1.6), Inches(6.05), Inches(5.15), WHITE)
    rect(s, Inches(6.8), Inches(1.6), Inches(6.05), Inches(0.7), MAROON_DARK)
    add_text_box(s, Inches(7.0), Inches(1.7), Inches(5.7), Inches(0.5), "Malaysia  ·  LHDN MyInvois", 20, WHITE, bold=True, font=FONT_SERIF)
    bullets(s, Inches(7.05), Inches(2.5), Inches(5.55), Inches(4.0), [
        "Clearance-first: UIN + QR before the document is legal",
        "Invoice, CN, DN, refund, self-billed, consolidated",
        "Consolidated monthly, within 7 days after month-end",
        "From 1 Jan 2026: line over RM10,000 cannot be consolidated",
        "Phase 4 (RM1m–RM5m) live; penalties from 1 Jan 2028",
        "Reuse YGL-World / MDEC-accredited provider",
        "McM already trained member firms (June 2024 seminar)",
    ], 14, CHARCOAL, 6)
    footer(s, 6, total)

    # ----- 7 Architecture -----
    s = blank_slide(prs)
    title_block(s, "Architecture principle", "One canonical invoice graph inside McM. Many domain ingest adapters and jurisdiction clearance adapters around it.")
    layers = [
        ("1. Ingest", "REST, SFTP, CSV,\nTally, SAP, Xero,\npayroll, TMS, WMS"),
        ("2. Canonical", "Invoice aggregate,\ntax engine, numbers,\ntenant isolation"),
        ("3. Clearance", "Step Functions saga,\nGSP → NIC IRP,\nMyInvois / YGL"),
        ("4. Artefacts", "PDF/A + QR, IRN/UIN,\nS3 Object Lock (WORM),\nERP write-back"),
        ("5. Tracking", "OpenSearch ops,\ndata lake, QuickSight,\nlakhs → crores view"),
    ]
    for i, (h, b) in enumerate(layers):
        x = Inches(0.45) + i * Inches(2.55)
        round_rect(s, x, Inches(1.7), Inches(2.4), Inches(3.15), WHITE)
        rect(s, x, Inches(1.7), Inches(2.4), Inches(0.7), MAROON if i % 2 == 0 else MAROON_DARK)
        add_text_box(s, x + Inches(0.1), Inches(1.82), Inches(2.2), Inches(0.5), h, 16, WHITE, bold=True, align=PP_ALIGN.CENTER)
        add_text_box(s, x + Inches(0.12), Inches(2.55), Inches(2.15), Inches(2.1), b, 14, CHARCOAL, align=PP_ALIGN.CENTER)
        if i < 4:
            add_text_box(s, x + Inches(2.15), Inches(2.85), Inches(0.45), Inches(0.4), "→", 22, MAROON, bold=True)
    round_rect(s, Inches(0.5), Inches(5.1), Inches(12.3), Inches(1.7), WHITE)
    add_text_box(s, Inches(0.75), Inches(5.25), Inches(11.8), Inches(0.4), "Hard rule", 14, MAROON, bold=True)
    add_text_box(
        s, Inches(0.75), Inches(5.65), Inches(11.8), Inches(0.95),
        "Tally JSON or SAP IDoc must never call NIC or LHDN directly. Scale-out is per tax identity (one FIFO queue per GSTIN / TIN), not one giant pipe. Crore-scale is the network aggregate across thousands of clients — a single GSTIN cannot legally push crores of IRNs per day.",
        15, CHARCOAL,
    )
    footer(s, 7, total)

    # ----- 8 AWS -----
    s = blank_slide(prs)
    title_block(s, "AWS reference architecture", "Regions: Mumbai (ap-south-1) for India clients · Singapore (ap-southeast-1) for Malaysia / ASEAN.")
    aws_rows = [
        ["Layer", "AWS services", "Why"],
        ["Edge", "Route 53, CloudFront, WAF, Cognito", "Member-firm login, DDoS, geo DNS"],
        ["API / compute", "API Gateway, EKS, Lambda", "Ingest, tax, PDF workers, token refresh"],
        ["Orchestration", "SQS FIFO, EventBridge, Step Functions", "Per-GSTIN pacing, retries, DLQ, saga"],
        ["Data", "Aurora PostgreSQL + RLS, DynamoDB, Redis", "Canonical OLTP, idempotency, GSP tokens"],
        ["Documents", "S3 (SSE-KMS) + Object Lock", "Signed JSON, QR, PDF/A, 7–10 year retention"],
        ["Tracking", "Kinesis, Glue, Athena, OpenSearch, QuickSight", "Lakhs/crores analytics off the OLTP path"],
        ["Security", "KMS, Secrets Manager, GuardDuty, CloudTrail", "Per-tenant keys, GSP certs, audit"],
    ]
    add_table(
        s, Inches(0.5), Inches(1.5), Inches(12.3), Inches(5.4),
        aws_rows,
        col_w=[Inches(2.2), Inches(5.5), Inches(4.6)],
    )
    footer(s, 8, total)

    # ----- 9 Volume -----
    s = blank_slide(prs)
    title_block(s, "Capacity: thousands, lakhs, crores", "AWS will scale. NIC IRP and MyInvois will not. Design per tax identity.")
    vol = [
        ["Ambition", "Docs / day", "Peak / sec", "Feasible?"],
        ["Single SME", "500", "0.1", "Trivial"],
        ["Busy trader", "10,000", "~1", "Easy on AWS; watch IRP"],
        ["Large 3PL / plant", "1 lakh", "~12", "AWS yes — many GSTINs + GSP contract"],
        ["Network slice", "10 lakh", "~120", "Kinesis/MSK; IRP only if sharded"],
        ["Network crore", "1 crore+", "400+", "Data lake + sharded status. Not one IRP credential."],
    ]
    add_table(
        s, Inches(0.5), Inches(1.55), Inches(12.3), Inches(4.15),
        vol,
        col_w=[Inches(2.6), Inches(2.2), Inches(2.2), Inches(5.3)],
    )
    round_rect(s, Inches(0.5), Inches(5.85), Inches(12.3), Inches(1.05), WHITE)
    add_text_box(
        s, Inches(0.7), Inches(6.0), Inches(11.9), Inches(0.8),
        "Indicative AWS: USD 1.5k–4k / month at pilot  ·  USD 8k–25k at 1–5 lakh / day network  ·  GSP per-document fees often exceed AWS. Retry storms can 10× cost and get the GSP suspended.",
        14, CHARCOAL,
    )
    footer(s, 9, total)

    # ----- 10 90-day plan -----
    s = blank_slide(prs)
    title_block(s, "First 90 days — go-live #1", "Team of 8–10. Sandbox credentials must be in hand by Day 15 or the date slips by the same number of days.")
    plan = [
        ["Days", "Engineering", "Tax / partner", "AWS / security"],
        ["1–5", "Freeze architecture, repo, CI", "Choose India vs Malaysia; 3 pilots", "Org, IAM, billing alarms"],
        ["6–15", "Tenant + Invoice API", "Sign GSP / YGL; GSTIN/TIN list", "VPC, EKS, Aurora, KMS"],
        ["16–30", "CSV + Tally ingest", "Sandbox credentials in hand", "WAF, secrets, environments"],
        ["31–50", "Mapper, validator, SQS workers", "Schema field dictionary signed off", "Step Functions, observability"],
        ["51–70", "IRP / MyInvois adapter, PDF+QR", "Sandbox pack + 20 error codes", "Authorisation pen-test"],
        ["71–85", "ERP write-back, ops console", "UAT then first live invoices", "Backup drill, Object Lock"],
        ["86–90", "Hypercare dashboards", "Rejection war-room", "Cost and rate-limit review"],
    ]
    add_table(
        s, Inches(0.4), Inches(1.48), Inches(12.5), Inches(5.45),
        plan,
        col_w=[Inches(1.3), Inches(3.9), Inches(4.0), Inches(3.3)],
    )
    footer(s, 10, total)

    # ----- 11 Phases -----
    s = blank_slide(prs)
    title_block(s, "Phases after Day 90", "Ship domain packs in volume order. Second country only after the first is boringly reliable.")
    phases = [
        ("P3  Days 50–150", "Domain packs", "1. Trading B2B (needed for go-live)\n2. Manufacturing (HSN, plants, job-work)\n3. Logistics (POD gate, e-way bill)\n4. Payroll-adjacent (month-end batch)\n5. SCM self-billed (imports, agents)\nConnectors: Tally + CSV first, then Xero/QB, then SAP."),
        ("P4  Days 90–180", "Lakhs / day tracking", "Load test 50k docs/hour, 200k peak.\nOpenSearch by IRN, GSTIN, consignment.\nQuickSight for firms and the network.\nDLQ replay, back-pressure, cost alarms.\n48-hour soak. Zero cross-tenant leaks."),
        ("P5–P6  150–360", "Network + harden", "Stand up the other of India / Malaysia.\nOnboard 10 then 50 member firms.\nGSTR-1 / VAT extract for Advisory.\nSOC 2 Type I, DR (RPO 15 min).\nUAE Peppol / ZATCA only with a paying client."),
    ]
    for i, (k, h, b) in enumerate(phases):
        x = Inches(0.45) + i * Inches(4.2)
        round_rect(s, x, Inches(1.6), Inches(4.0), Inches(5.2), WHITE)
        rect(s, x, Inches(1.6), Inches(4.0), Inches(1.15), MAROON if i == 0 else MAROON_DARK)
        add_text_box(s, x + Inches(0.18), Inches(1.68), Inches(3.65), Inches(0.4), k, 13, GOLD, bold=True)
        add_text_box(s, x + Inches(0.18), Inches(2.05), Inches(3.65), Inches(0.5), h, 18, WHITE, bold=True, font=FONT_SERIF)
        add_text_box(s, x + Inches(0.2), Inches(2.95), Inches(3.6), Inches(3.6), b, 13, CHARCOAL)
    footer(s, 11, total)

    # ----- 12 Team -----
    s = blank_slide(prs)
    title_block(s, "90-day squad and non-goals", "One person with an AWS account cannot deliver legal e-invoices in days.")
    team = [
        ["Role", "Count", "Notes"],
        ["Product / domain (CA + GST/MyInvois)", "1", "Must sit with McM tax partners"],
        ["Engineering lead", "1", "Owns architecture and cutover"],
        ["Backend (invoice + adapters)", "3", "Canonical, clearance, ingest"],
        ["Frontend (firm + ops portals)", "1–2", "McM maroon / red / white / black"],
        ["Data / integration", "1", "Tally, SFTP, CSV"],
        ["AWS / platform / security", "1", "Terraform, tenancy, KMS"],
        ["QA (schema + load)", "1", "IRP error catalogue + soak"],
    ]
    add_table(
        s, Inches(0.5), Inches(1.5), Inches(7.6), Inches(5.4),
        team,
        col_w=[Inches(3.7), Inches(1.0), Inches(2.9)],
    )
    round_rect(s, Inches(8.3), Inches(1.5), Inches(4.5), Inches(5.4), WHITE)
    add_text_box(s, Inches(8.5), Inches(1.7), Inches(4.15), Inches(0.45), "Out of scope for v1", 16, MAROON, bold=True)
    bullets(s, Inches(8.5), Inches(2.25), Inches(4.1), Inches(4.4), [
        "Becoming a GSTN GSP or MDEC Peppol SP",
        "Replacing YGL on the shop floor",
        "Full payroll engine (PF, ESI, payslips)",
        "ZATCA crypto-stamping in 90 days",
        "AI HSN coding as legal authority",
        "One shared DB without row-level security",
        "All 77 countries in the first release",
    ], 13, CHARCOAL, 8)
    footer(s, 12, total)

    # ----- 13 Risks -----
    s = blank_slide(prs)
    title_block(s, "Risks that actually slip the date", "Schedule risk #1 is sandbox credentials. Legal risk #1 is a cross-tenant leak.")
    risks = [
        ["Risk", "Impact", "Control"],
        ["Sandbox / prod credentials delayed", "Go-live slips 1:1", "Start paperwork Day 1; backup GSP"],
        ["Building a GSP instead of an ASP", "6–12 month delay", "Out of scope for v1"],
        ["Duplicate IRN / lost write-back", "Legally invalid invoices", "Idempotency store + Get IRN fallback"],
        ["Cross-tenant data leak", "Network-ending event", "RLS + automated isolation tests"],
        ["IRP throttle / 1-hour ban", "Business stop", "Per-GSTIN FIFO, jitter, circuit breaker"],
        ["Treating salary as e-invoice", "Wrong law", "Payroll adapter allow-list"],
        ["MY consolidation after RM10k rule", "Penalties", "Hard stop in the validator"],
        ["Scope: UAE + KSA + EU in v1", "Never ships", "Two jurisdictions max in 180 days"],
    ]
    add_table(
        s, Inches(0.4), Inches(1.48), Inches(12.5), Inches(5.45),
        risks,
        col_w=[Inches(4.3), Inches(3.5), Inches(4.7)],
    )
    footer(s, 13, total)

    # ----- 14 Week 1 -----
    s = blank_slide(prs)
    title_block(s, "Five decisions needed in week 1", "Until these are answered, engineering can only stand up an empty AWS landing zone — not legal e-invoices.")
    decisions = [
        ("1", "First jurisdiction", "India GST or Malaysia MyInvois? Pick where the first paying clients sit."),
        ("2", "First domain", "Trading B2B is the correct default. Payroll and logistics follow."),
        ("3", "Named partners", "Which GSP (India) and/or YGL (Malaysia). Contracts, not workshops."),
        ("4", "Operating entity", "Which McM legal entity owns the AWS org and customer contracts."),
        ("5", "Three pilots", "Named companies with live volume and a partner firm ready to operate them."),
    ]
    for i, (n, h, b) in enumerate(decisions):
        y = Inches(1.55) + i * Inches(1.05)
        round_rect(s, Inches(0.5), y, Inches(12.3), Inches(0.95), WHITE)
        circ = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.7), y + Inches(0.18), Inches(0.58), Inches(0.58))
        fill_shape(circ, MAROON)
        add_text_box(s, Inches(0.7), y + Inches(0.22), Inches(0.58), Inches(0.5), n, 18, WHITE, bold=True, align=PP_ALIGN.CENTER)
        add_text_box(s, Inches(1.5), y + Inches(0.12), Inches(10.9), Inches(0.35), h, 16, MAROON, bold=True)
        add_text_box(s, Inches(1.5), y + Inches(0.46), Inches(10.9), Inches(0.4), b, 14, CHARCOAL)
    footer(s, 14, total)

    # ----- 15 Security -----
    s = blank_slide(prs)
    title_block(s, "Security and operating model", "Assume a hostile cross-tenant world. Independent firms share a brand, not a ledger.")
    items = [
        ("Encryption", "KMS CMKs per tenant (or envelope per tenant). TLS 1.2+. S3 Object Lock on cleared artefacts for 7–10 years."),
        ("Access", "Partner staff see only their tenant. Global Secretariat sees aggregated ops metrics, not line items, unless an engagement letter authorises a review."),
        ("Compliance", "Malaysia PDPA, India DPDP, UK GDPR. SOC 2 Type I by Day 180, Type II by Day 360. ISO 27001 if pitching banks (DBS SME financing)."),
        ("Legal pack", "Network SaaS master, Accession addendum per firm, DPA, client letter that the McM firm issues/clears as agent."),
        ("Secrets", "GSP client id/secret, MyInvois certificates, ERP tokens in Secrets Manager with rotation. Never store PAN / Aadhaar / NRIC unless legally required."),
        ("Audit", "Every clearance request/response stored. CloudTrail organisation trail. Immutable event log on the invoice aggregate."),
    ]
    for i, (h, b) in enumerate(items):
        col = i % 3
        row = i // 3
        card(s, Inches(0.45) + col * Inches(4.2), Inches(1.55) + row * Inches(2.6), Inches(4.0), Inches(2.4), h, b, 15, 13)
    footer(s, 15, total)

    # ----- 16 Close -----
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, SLIDE_W, SLIDE_H, BLACK)
    rect(s, 0, 0, Inches(0.22), SLIDE_H, MAROON)
    add_text_box(s, Inches(0.7), Inches(0.7), Inches(12), Inches(0.4), "RECOMMENDATION", 13, GOLD, bold=True)
    add_text_box(
        s, Inches(0.7), Inches(1.1), Inches(12), Inches(1.2),
        "Build McM Invoice Cloud as a multi-tenant ASP on AWS.",
        28, WHITE, bold=True, font=FONT_SERIF,
    )
    recs = [
        "Day 90 — real IRNs or UINs for three pilots, thousands per day, one country, one domain.",
        "Day 180 — five domain packs at lakhs per day, tracking that Advisory can actually use.",
        "Day 270–360 — network product for 250 offices, crore-scale aggregate analytics, SOC 2.",
        "Do not advertise this as a week of work because an AWS account exists. That produces PDFs. Under GST and MyInvois, a PDF is still paper.",
    ]
    y = Inches(2.5)
    for r in recs:
        add_text_box(s, Inches(0.7), y, Inches(11.8), Inches(0.7), "▸   " + r, 16, LIGHT_GRAY)
        y += Inches(0.75)
    rect(s, 0, Inches(6.85), SLIDE_W, Inches(0.65), MAROON_DARK)
    add_text_box(
        s, Inches(0.7), Inches(6.95), Inches(12), Inches(0.45),
        "mcmillanwoods.com   ·   Full plan: docs/e-invoicing-architecture-and-delivery-plan.md",
        13, WHITE, anchor=MSO_ANCHOR.MIDDLE,
    )

    out = Path("/workspace/docs/McMillan-Woods-E-Invoicing-Architecture-Plan.pptx")
    prs.save(out)
    print(f"Wrote {out} ({out.stat().st_size} bytes)")
    return out


if __name__ == "__main__":
    build()
