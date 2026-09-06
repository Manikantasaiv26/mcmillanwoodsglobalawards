# McMillan Woods — E-Invoice Cloud plan

This repository holds the architecture and delivery plan for a network-wide **e-invoicing** platform for [McMillan Woods Worldwide](https://www.mcmillanwoods.com/) member firms.

McMillan Woods is a global association of independent chartered accountancy and advisory firms (TAX • AUDIT • ADVISORY), with 77+ countries, 250+ offices, and 3,200+ staff. Member firms already provide bookkeeping, payroll, GST/VAT advisory, and outsourcing. This plan turns that into a paperless, tax-authority-cleared invoice fabric on **AWS**.

## Download

**[docs/McMillan-Woods-E-Invoicing-Architecture-Plan.pptx](docs/McMillan-Woods-E-Invoicing-Architecture-Plan.pptx)** — 16-slide PowerPoint (widescreen 16:9). Open in PowerPoint, Keynote, or Google Slides.

Slide 3 is a 2×2 of live `mcmillanwoods.com` pages (Home, About Us, Accountancy, Malaysia e-invoice seminar with YGL-World).

## Document

**[docs/e-invoicing-architecture-and-delivery-plan.md](docs/e-invoicing-architecture-and-delivery-plan.md)** — full written plan:

- How McMillan Woods actually operates (from the public site)
- India GST IRP and Malaysia MyInvois clearance models
- Domain packs: payroll-adjacent, logistics, manufacturing, trading, SCM
- AWS architecture for thousands → lakhs → crore-scale **aggregate** tracking
- Honest timeline: **90 / 180 / 270–360 days**, not a few days
- Team, cost bands, risks, and week-1 decisions

## Timeline at a glance

| Milestone | Calendar | Ships |
| --- | --- | --- |
| Go-live #1 | **90 days** | One jurisdiction, one domain, thousands of invoices/day |
| Multi-domain production | **180 days** | Five domain packs, lakhs/day tracking |
| Network GA | **270–360 days** | 250+ member firms, two countries, crore-scale aggregate analytics |
