# McMillan Woods Global E-Invoicing Platform

## Architecture, Domain Design, and Delivery Plan

**Prepared for:** McMillan Woods Worldwide (MCMWW) member firms and Global Secretariat
**Source studied:** [https://www.mcmillanwoods.com/](https://www.mcmillanwoods.com/) (About, Services, Global Offices, Taxation, Outsourcing, Accountancy, Malaysia e-Invoice seminar)
**Cloud:** Amazon Web Services (caller already has an AWS account)
**Document status:** Final plan for go / no-go and Phase-0 kickoff
**Date:** 5 September 2026

---

## 1. Direct answer: how long, and what “end to end” actually means

This is **not a few-day build**. A paperless, legally valid e-invoice platform that member firms can run for payroll, logistics, manufacturers, traders, and SCM clients — at **thousands to lakhs of documents per day**, with a path to **network-wide crore-scale** — is a regulated, multi-tenant product.

| What you want live | Realistic calendar | Why it cannot be faster |
| --- | --- | --- |
| **First production go-live** — one jurisdiction (India GST **or** Malaysia MyInvois), one domain (e.g. trading B2B), thousands of invoices/day, member-firm portal | **90 days** | Government sandbox credentials, schema certification, GSP/MyInvois onboarding, idempotent IRN/UIN write-back, QR/PDF, audit trail |
| **Multi-domain production** — payroll-adjacent, logistics, manufacturing, trading, SCM packs + lakhs/day throughput | **180 days** | Domain tax rules, ERP connectors, e-way bill / consignment linkage, bulk ingest, retry/poison queues, ops dashboards |
| **Network-wide end-to-end** — India + Malaysia live, UAE/KSA adapters started, 250+ independent firms as tenants, crore-scale **aggregate** tracking | **270–360 days** | Independent-firm isolation, Peppol/ZATCA adapters, SOC 2 / PDPA / DPDP, GSP/Peppol commercial contracts, disaster recovery |

**AWS is not the bottleneck.** NIC Invoice Registration Portal (India) and LHDN MyInvois (Malaysia) are. A single GSTIN cannot legally push crores of IRNs per day through IRP rate limits. Crore-scale is **the network aggregate** across thousands of client GSTINs/TINs, not one company.

**Recommended first production target (Day 90):** India GST e-invoice (IRN) **or** Malaysia MyInvois — pick the market where the first paying clients sit. Second jurisdiction in Phase 5.

**Team for the 90-day critical path:** 8–10 people (see §12). One person with an AWS account cannot deliver this in days.

---

## 2. What the McMillan Woods website actually tells us

McMillan Woods is **not a software vendor**. It is a **global association of independent chartered accountancy and advisory firms**.

| Fact from the site | Implication for this product |
| --- | --- |
| 77+ countries, 250+ offices, 3,200+ staff | Multi-tenant SaaS. Each **member firm** is a tenant; each **client company** is a sub-tenant. |
| Independent firms, no equity in each other; Constitutions / By-Laws / Accession Contracts | Strict data isolation. Firm A must never see Firm B’s invoices. Global Secretariat is operator, not owner of client data. |
| Secretariat: Petaling Jaya, Malaysia; association HQ: London | Legal entity, billing, and data-residency split: `ap-southeast-1` (MY/SG) + `ap-south-1` (IN) + `eu-west-2` (UK/EU later). |
| Brand services: **TAX • AUDIT • ADVISORY** | E-invoicing is a **tax-technology + outsourcing** product, not a replacement for audit. |
| Accountancy: bookkeeping, **payroll**, management accounts, annual reports | Natural ingest sources already exist inside member firms. |
| Outsourcing: bookkeeper-cum-accountant for start-ups and foreign-owned companies | Member firms will **issue invoices on behalf of clients** (ASP / outsourced AP+AR). |
| Taxation: VAT/GST registration and returns, corporate tax, RPGT, stamp duty | E-invoice data must feed GST/VAT returns, not sit in a silo. |
| Cochin partner expertise: SAP, Dynamics GP/Navision, Tally, QuickBooks, MYOB, Xero, Focus; GCC VAT (KSA, Bahrain, Oman, Qatar, Kuwait) | Connector pack is a first-class workstream, not an afterthought. |
| June 2024 seminar **“Beyond e-Invoice Compliance in Malaysia”** with **YGL-World** | Do **not** compete with YGL on Day 1 in Malaysia. Wrap them (and a GSP in India) behind a McM adapter. Become the **network control plane**. |
| SME financing collaboration (DBS Solutions) | Invoice status (cleared / rejected / overdue) can later feed working-capital products. |

**Positioning for the network**

> McMillan Woods E-Invoice Cloud is the shared compliance fabric for member firms: ingest from payroll, ERP, WMS, and TMS → validate → clear with the tax authority → store IRN/UIN/QR → track every document at thousands-to-lakhs scale → feed books, GST/VAT returns, and audit.

Member firms keep the client relationship. The platform is the engine.

---

## 3. Scope: what “e-invoicing for all domains” means in law vs in operations

Paper invoices are already legally insufficient in the two markets that matter first.

### 3.1 India (GST) — clearance model

- Legal invoice = JSON registered on NIC IRP, IRN (hash) returned, signed QR on the print copy.
- Documents: Invoice, Credit Note, Debit Note; optional **e-Way Bill by IRN**.
- Schema: GSTN INV-01 JSON 1.1 (mandatory seller/buyer GSTIN, HSN, POS, tax breakup).
- Auth token ~6 hours in production. Duplicate IRN is error **2150**; design must be **idempotent** on `(GSTIN, FY, DocType, DocNo)`.
- Access: **GSP** (GST Suvidha Provider) or NIC-direct after registration. McM should operate as **ASP** on a licensed GSP for 12–24 months, not apply to become a GSP on Day 1.
- Turnover threshold historically notified in phases; confirm current notified turnover with tax partners before go-live. Sandbox first, always.

### 3.2 Malaysia (LHDN / IRBM MyInvois) — clearance-first model

- Invoice must be validated by MyInvois and receive a **UIN + QR** *before* it is a legal document.
- Documents: Invoice, Credit Note, Debit Note, Refund Note, **Self-Billed**, **Consolidated** (monthly, within 7 days after month-end, with RM10,000 per-transaction cap on consolidation from 1 Jan 2026).
- Phase 4 (RM1m–RM5m) is live; relaxation / penalty-free period currently described through **31 Dec 2027**; full enforcement **1 Jan 2028**. Below RM1m currently exempt (confirm related-company rules).
- McM already trained member firms on this (June 2024). YGL is an existing showcase partner — treat as Malaysia adapter option.

### 3.3 Later jurisdictions (Phase 5–6, not Day 90)

| Country | Regime | Why McM cares |
| --- | --- | --- |
| UAE | FTA Peppol / e-invoicing rollout | Dubai / Abu Dhabi offices |
| Saudi Arabia | ZATCA Fatoora Phase 2 (XML, cryptographic stamp) | KSA office + Cochin GCC VAT practice |
| EU | Peppol / ViDA | UK, NL, DE, ES, IT member firms |
| Singapore | InvoiceNow (Peppol) | Lark/Singapore partners meeting footprint |

Core engine must be **UBL 2.1 / Peppol-ready** even if India JSON and MyInvois XML/JSON are the first two adapters.

### 3.4 Domain map (what actually generates a legal e-invoice)

Payroll **salary** is generally **not** a GST/MyInvois supply. The payroll *module* still belongs in this product because member firms already run payroll, and several adjacent documents **are** e-invoiceable.

| Domain | Typical source systems | Documents that become e-invoices | High-volume pattern |
| --- | --- | --- | --- |
| **Corporate / professional services** (McM’s own billing + client AR) | Practice management, Xero, Tally | Fee invoices, retainers, disbursements | Hundreds–thousands/day per firm |
| **Payroll-adjacent** | Payroll, HRMS | Contractor invoices, staff reimbursements, employment perquisites (MY), expenses incurred by employee on behalf of employer (MY self-bill rules), secondment cross-charges | Month-end spike |
| **Trading** | Tally, SAP SD, POS | B2B tax invoices, CN/DN, B2C consolidated (MY) | Thousands–lakhs/day |
| **Manufacturing** | SAP PP/SD, Dynamics, YGL ERP | Finished-goods invoices, job-work, scrap, CN for returns | Thousands/day, HSN-heavy |
| **Logistics / 3PL** | TMS, WMS | Freight invoices, warehouse charges, detention, fuel surcharge | Event-driven, POD-gated |
| **SCM / procurement** | Coupa, SAP MM | Self-billed (import of services, agent commissions, individual sellers), debit notes | Inbound spike |

---

## 4. Product architecture (target state)

### 4.1 Principle

One **canonical invoice graph** inside McM. Many **jurisdiction adapters** and **domain ingest adapters** around it. Never let Tally JSON or SAP IDoc talk to NIC/LHDN directly.

```
                    +------------------+
                    | Member Firm Portal|
                    | (web + mobile)    |
                    +---------+--------+
                              |
                         API Gateway
                              |
         +--------------------+--------------------+
         |                    |                    |
   Ingest Plane         Control Plane         Clearance Plane
   (connectors)         (canonical)           (tax authorities)
         |                    |                    |
  Payroll / ERP /     Validate, tax engine,    GSP → NIC IRP
  TMS / WMS / CSV     number, idempotency      MyInvois API
  SFTP / webhook      store, QR/PDF            Peppol AP (later)
         |                    |                    |
         +--------------------+--------------------+
                              |
                    Observability + Data lake
                    (track thousands → crores)
```

### 4.2 Logical components

1. **Identity & tenancy** — Cognito (or Auth0) with org hierarchy: Network → Member Firm → Practice office → Client entity → GSTIN/TIN/BRN. Fine-grained IAM via Cedar/OPA policies. SCIM for firm staff.
2. **Ingest gateway** — REST, GraphQL BFF, SFTP, S3 drop-zone, webhook, SAP IDoc, Tally XML, Xero/QB OAuth.
3. **Canonical invoice service** — versioned `Invoice` aggregate: header, parties, lines, tax, references (PO, GRN, POD, payslip id), attachments.
4. **Tax determination** — pluggable rules: GST (CGST/SGST/IGST/CESS), SST/MyInvois classification codes, GCC VAT. Never hard-code rates in connectors.
5. **Clearance orchestrator** — Step Functions per document: validate → map schema → sign/encrypt → submit → poll → persist IRN/UIN/QR → notify ERP.
6. **Document factory** — PDF/A + QR (India signed QR; Malaysia UIN QR). Store in S3 Object Lock (WORM) for retention.
7. **Tracking & search** — OpenSearch + DynamoDB status store. Every document has a lifecycle: `INGESTED → VALIDATED → QUEUED → SUBMITTED → CLEARED | REJECTED → CORRECTED → CANCELLED`.
8. **Returns bridge** — GSTR-1 / IFF extract (IN); MyInvois already is the tax record (MY). Push journals to Xero/Tally.
9. **Partner ops** — firm dashboard: rejection reasons, stuck queues, SLA, client onboarding, GSP credential vault.
10. **Data lake** — S3 + Glue + Athena + QuickSight for “lakhs/crores tracking” without hitting OLTP.

### 4.3 AWS reference architecture

**Regions:** `ap-south-1` (Mumbai) primary for India clients; `ap-southeast-1` (Singapore) primary for Malaysia/ASEAN. Shared control plane can live in Singapore with data residency partitions.

```
                         Route 53 + CloudFront + WAF
                                      |
                          API Gateway (REST) + Cognito
                                      |
                    +-----------------+------------------+
                    |                                    |
              Amazon EKS                            AWS Lambda
         (ingest, tax, PDF workers)            (webhooks, token refresh)
                    |                                    |
         SQS / SNS / EventBridge  <---------------------+
         (per-jurisdiction queues, DLQ, FIFO by GSTIN)
                    |
         +----------+-----------+------------------+
         |                      |                  |
   Aurora PostgreSQL      DynamoDB            ElastiCache Redis
   (canonical OLTP,       (idempotency,        (GSP tokens,
    multi-tenant RLS)      rate-limit,          GSTIN cache)
                           status hot path)
                    |
         +----------+-----------+------------------+
         |                      |                  |
   Step Functions         S3 (SSE-KMS)        Kinesis → S3 data lake
   (clearance saga)       invoices, QR,       Glue / Athena / QuickSight
                          signed JSON,        OpenSearch Service
                          audit packs
                    |
              AWS Secrets Manager + KMS + CloudHSM (later ZATCA)
              PrivateLink to GSP / on-prem ERP
              CloudTrail, GuardDuty, Security Hub, Config
              Backup + PITR; secondary region for DR
```

**Why these services (volume-driven)**

| Volume band | Invoices / day | AWS pattern |
| --- | --- | --- |
| Thousands | 1,000–50,000 | API Gateway + ECS/EKS (2–4 pods) + Aurora Serverless v2 + SQS |
| Lakhs | 100,000–1,000,000 | EKS HPA, SQS partitioned by GSTIN hash, Aurora writer + read replicas, Kinesis, OpenSearch |
| Crores (network aggregate) | 10,000,000+ | Multi-region, Kafka (MSK) or Kinesis On-Demand, Aurora Limitless or DynamoDB invoice-status shard, S3 data lake only for analytics, no dashboard queries on OLTP |

**Hard rate-limit design (India):** one FIFO queue **per GSTIN** (or per GSP credential). Workers respect IRP ~100–500 req/min (confirm contracted GSP SLA). Adaptive backoff. Never burst identical payloads (NIC blocks for ~1 hour).

**Idempotency key:** `sha256(jurisdiction + supplierTaxId + fiscalYear + docType + docNumber)`. Store in DynamoDB with TTL + conditional put. IRP duplicate 2150 → treat as success and fetch existing IRN.

### 4.4 Canonical data model (minimum)

```
Network
  └── MemberFirm (tenant_id)
        └── Office
              └── ClientOrganisation
                    └── LegalEntity (GSTIN / TIN / BRN / VATIN)
                          └── InvoiceDocument
                                ├── Parties (seller, buyer, ship-to, payee)
                                ├── Lines (HSN/SAC, qty, UQC, tax)
                                ├── TaxSummary
                                ├── ClearanceArtifact (IRN/UIN, ack, QR, signed blob)
                                ├── DomainLink (payroll_run_id | consignment_id | po_id | grn_id)
                                └── EventLog (immutable)
```

Row-level security in Aurora: `tenant_id` on every table; IAM database auth; no cross-tenant joins in app code.

### 4.5 Domain adapters

Each adapter translates source events into the canonical invoice and attaches a `DomainLink`.

**Payroll adapter**

- Ingest: salary register is **out of GST**; still stored as a run for audit.
- Emit e-invoices for: contractor / consultant bills, reimbursement recharge to group companies, Malaysia perquisites / employee-on-behalf expenses per IRBM Specific Guideline §§6–7, self-billed where mandated.
- Month-end batch window: T+0 payroll lock → T+1 invoice generate → T+2 clearance.

**Logistics adapter**

- Gate invoice on POD / proof of delivery event.
- India: generate IRN then **e-Way Bill by IRN** when goods movement applies.
- Split charges: linehaul, handling, detention, fuel — separate SAC codes.

**Manufacturing adapter**

- Map material master → HSN; plant → POS; STO vs sale.
- Job-work and scrap invoices as first-class document types.
- Credit notes tied to original IRN (mandatory for GST).

**Trading / SCM adapter**

- High-SKU invoices: async validate lines in parallel (Lambda map).
- Malaysia: auto-route B2C below threshold to **consolidated** monthly job; force individual e-invoice if line > RM10,000.
- Self-billed pack: imports, agents/dealers, individual sellers.

### 4.6 Application topology (build)

| Layer | Choice | Reason |
| --- | --- | --- |
| API | TypeScript (NestJS) or Java (Spring Boot) | Tax/finance teams hire Java; TS ships UI faster. **Recommendation: Java core + TS BFF/UI.** |
| Workers | Same core, Kafka/SQS consumers | |
| Web | Next.js, McM colours (red / maroon / white / black) | Member and client portals |
| Mobile | Later (Phase 6); PWA first | Field logistics POD capture |
| Infra | Terraform + GitHub Actions + EKS | Repeatable for second region |

---

## 5. Security, legal, and operating model

McM member firms are **independent**. The platform must assume a hostile cross-tenant world.

- **Encryption:** KMS CMKs per tenant (or per region + envelope per tenant). TLS 1.2+. S3 Object Lock on cleared artifacts (7–10 year retention by jurisdiction).
- **Secrets:** GSP client id/secret, MyInvois digital certs, ERP tokens in Secrets Manager; rotation.
- **Access:** Partner staff see only their `tenant_id`. Global Secretariat sees **aggregated ops metrics**, not invoice line items, unless a client letter of engagement authorises a review.
- **Compliance track:** Malaysia PDPA, India DPDP Act, UK GDPR for EU/UK firms. SOC 2 Type I by Day 180, Type II by Day 360. ISO 27001 if pitching banks (DBS collaboration).
- **Audit:** every clearance request/response stored (redact secrets). CloudTrail organisation trail.
- **Legal:** Master SaaS agreement from the network entity; Accession addendum per member firm; DPA; client engagement letter that McM firm is issuing/clearing as agent.
- **Do not** store full PAN / Aadhaar / NRIC unless a domain legally requires it; tokenise.

**GSP / MyInvois commercial reality**

| Role | Who | When |
| --- | --- | --- |
| ASP (application service provider) | McMillan Woods platform | Day 1 |
| GSP (India) | Licensed partner (contract) | Must be signed in Phase 0 (week 1–2) |
| MyInvois integrator / Peppol SP | YGL-World and/or MDEC-accredited SP | Reuse June 2024 relationship |
| Taxpayer | Client legal entity | Onboarded by member firm |

---

## 6. Delivery plan (calendar days, overlapping streams)

Assumptions: AWS account exists; 8–10 core people; GSP/MyInvois partner contract starts in week 1; first jurisdiction chosen in week 1; no parallel “build our own GSP”.

```
Day    0        30        60        90       120       150       180       270       360
       |---------|---------|---------|---------|---------|---------|---------|---------|
P0     [Discover & contracts]
P1          [AWS landing + tenancy + canonical invoice]
P2               [Clearance adapter #1 sandbox → prod]
P3                    [Domain packs: trade → mfg → logistics → payroll]
P4                         [Bulk scale: lakhs/day, lake, ops]
P5                                   [Jurisdiction #2 + member rollout]
P6                                              [Harden, SOC2, UAE/KSA start, DR]
Go-live #1 .......................... ^ Day 90
Go-live #2 (multi-domain, lakhs) ...................... ^ Day 180
Network GA ................................................................ ^ Day 270–360
```

### Phase 0 — Discovery and legal (Days 0–15)

**Outcome:** written jurisdiction choice, GSP/YGL contract, 3 pilot clients, data-residency decision.

- Workshop with tax partners (Malaysia secretariat + India offices: Delhi, Bangalore, Cochin, Kolkata, Chennai, Hyderabad, etc.).
- Pick **Pilot A**: one manufacturer/trader in India **or** one MY SME already in Phase 4.
- Sign GSP (IN) and/or MyInvois integrator (MY). Start sandbox credential paperwork **immediately** (this is the longest external lead time).
- Information security questionnaire, data processing agreement template.
- Confirm: McM is ASP, not GSTN GSP, not MDEC Peppol SP, in v1.

**Exit criteria:** signed partner API access; pilot GSTIN/TIN list; architecture decision record (this document, frozen).

### Phase 1 — Foundation on AWS (Days 5–45, overlaps P0)

**Outcome:** empty but secure platform; a human can log in as a member firm and create a client entity.

- Terraform org: VPC, EKS, Aurora, DynamoDB, KMS, WAF, CI/CD, environments `dev / sandbox / uat / prod`.
- Tenant model + Cognito + RLS.
- Canonical `InvoiceDocument` API (CRUD + state machine stub).
- S3 WORM buckets, CloudTrail, GuardDuty.
- Design system: McM maroon/red header, “Professionalism at the Forefront” unused in product UI except login chrome; product name e.g. **McM Invoice Cloud**.

**Exit criteria:** `dev` and `sandbox` deployed; threat model reviewed; hello-world invoice persisted.

### Phase 2 — First clearance adapter (Days 20–90)

**Outcome:** sandbox IRN **or** MyInvois UIN for a real pilot GSTIN/TIN; PDF+QR; error catalogue.

**India path (if chosen first)**

- Auth token manager (6-hour refresh, Redis cache, per GSTIN).
- INV-01 JSON mapper + JSON Schema validation.
- Generate IRN, Get IRN, Cancel IRN (within allowed window), Generate EWB by IRN (stub if logistics not yet live).
- Handle 2150 duplicate as success.
- Signed QR on PDF/A.
- UAT against NIC sandbox; production cutover checklist.

**Malaysia path (if chosen first)**

- MyInvois document submit / get / cancel / reject.
- UIN + QR persist.
- Self-billed and consolidated jobs (consolidated can slip to Phase 3 if needed).
- Prefer calling YGL or MDEC SP rather than reverse-engineering LHDN if that gets production faster.

**Shared**

- Step Functions saga, SQS FIFO, DLQ console for tax ops.
- Webhook back to ERP (IRN/UIN write-back).

**Exit criteria:** 1,000 successful sandbox documents; 50 production documents for Pilot A; rejection rate understood.

**This is the Day-90 go-live.**

### Phase 3 — Domain packs (Days 50–150)

Ship in this order (volume and legal urgency):

1. **Trading B2B** (Days 50–90) — needed for go-live.
2. **Manufacturing** (Days 80–120) — HSN master, plants, job-work.
3. **Logistics** (Days 100–140) — POD gate, e-way bill.
4. **Payroll-adjacent** (Days 110–150) — month-end batch, MY perquisite/self-bill rules; **not** salary-as-invoice.
5. **SCM self-billed** (Days 120–150) — imports, agents.

Connectors in parallel: **Tally** and **CSV/SFTP** first (covers most Indian SMEs McM already books), then **Xero / QuickBooks**, then **SAP / Dynamics**.

**Exit criteria:** each pack has one pilot client clearing production documents.

### Phase 4 — Bulk scale and tracking (Days 90–180)

This is the “thousands / lakhs / crores tracking” workstream.

- Load test: 50k docs/hour sustained, 200k peak, per-GSTIN pacing.
- OpenSearch ops UI: search by IRN, GSTIN, consignment, payroll run, rejection code.
- QuickSight: firm-level and network-level volume, clearance SLA, top rejection reasons.
- Replay from DLQ; poison-message quarantine; back-pressure.
- Data lake partitions `year/month/day/tenant_id`.
- Cost alarms (IRP retries are money and ban-risk).

**Exit criteria:** 48-hour soak at lakhs/day in UAT; p99 clearance submit < 3s excluding IRP wait; zero cross-tenant leaks in chaos test.

### Phase 5 — Second jurisdiction + network rollout (Days 150–240)

- Stand up the other of {India, Malaysia}.
- Member-firm onboarding kit: 1-day training, engagement letter, credential vault.
- Roll out to 10 member firms, then 50.
- GSTR-1 / VAT return extract for tax teams (this sells the Advisory practice).

### Phase 6 — Harden and expand (Days 210–360)

- SOC 2 Type I, DR failover (RPO 15 min, RTO 4 h).
- UAE Peppol / ZATCA adapter spikes (not full production unless a paying GCC client is signed).
- Optional: invoice financing hooks for DBS-style SME products (cleared invoice as receivable).
- Mobile PWA for POD + invoice status.

---

## 7. Day-by-day view of the first 90 days (go-live #1)

| Days | Engineering | Tax / partner | AWS / security |
| --- | --- | --- | --- |
| 1–5 | Freeze ADR, repo, CI | Choose IN vs MY; shortlist 3 pilots | Org, IAM Identity Center, billing alarms |
| 6–15 | Tenant + Invoice API | Sign GSP/YGL; collect GSTIN/TIN | VPC, EKS, Aurora, KMS |
| 16–30 | Ingest CSV + Tally | Sandbox credentials in hand | WAF, secrets, environments |
| 31–50 | Mapper + validator + SQS workers | Schema field dictionary signed off | Step Functions, Observability |
| 51–70 | IRP/MyInvois adapter, PDF/QR | Sandbox test pack (happy + 20 error codes) | Pen-test of authz |
| 71–80 | ERP write-back, ops console | UAT with Pilot A books | Backup / restore drill |
| 81–85 | Production cutover | First live invoices (controlled volume) | Prod KMS, Object Lock |
| 86–90 | Hypercare, dashboards | Rejection war-room | Cost and rate-limit review |

If sandbox credentials slip past Day 15, **Day 90 slips by the same number of days.** That is the #1 schedule risk.

---

## 8. What a “complete” v1 looks like on screen (member firm)

1. Login as Cochin / KL / Delhi member firm.
2. Onboard client legal entity (GSTIN/TIN, GSP mapping, ERP type).
3. Drop a day’s sales register (CSV) or sync Tally.
4. See queue: Validated / Submitted / Cleared / Rejected.
5. Open a rejected row: NIC/LHDN code, human explanation, fix-and-resubmit.
6. Download PDF with QR; IRN/UIN written back to Tally.
7. Month-end: consolidated MY job or GSTR-1 extract.
8. Firm dashboard: documents today, p95 time-to-clear, top 5 errors.

Client (optional later): read-only status portal so traders stop emailing “where is my IRN?”.

---

## 9. Non-goals for v1 (explicit)

- Becoming a GSTN-licensed GSP or MDEC Peppol Service Provider.
- Replacing YGL ERP on the shop floor.
- Full payroll engine (PF, ESI, EPF, payslips) — integrate, do not rebuild.
- Crypto stamping for ZATCA in the first 90 days.
- AI “auto-code HSN” as a legal authority (assistive only, human confirm).
- One shared database for all 250 firms without RLS.

---

## 10. Capacity math (so “crores” is not a slogan)

Assume 8 working hours peak-spread, 3× peak factor.

| Ambition | Docs/day | Average docs/sec | Peak docs/sec | Feasible? |
| --- | --- | --- | --- | --- |
| Single SME | 500 | 0.02 | 0.1 | Trivial |
| Busy trader | 10,000 | 0.35 | 1 | Easy on AWS; watch IRP |
| Large 3PL / manufacturer | 100,000 (1 lakh) | 3.5 | 12 | AWS yes; **many GSTINs** + GSP contract |
| Marketplace / network slice | 1,000,000 (10 lakh) | 35 | 120 | AWS yes with MSK/Kinesis; IRP only if sharded by GSTIN |
| Network crore | 10,000,000 | 116 | 400+ | AWS data-lake + sharded status store; **not** one IRP credential |

**Design rule:** scale-out is **per tax identity**, not one giant pipe.

---

## 11. Indicative AWS monthly cost (order of magnitude, not a quote)

| Stage | Volume | Ballpark AWS | Plus GSP/MyInvois fees |
| --- | --- | --- | --- |
| Pilot (Day 90) | < 20k/day | USD 1.5k–4k | Per-GSTIN / per-doc GSP tariff |
| Multi-domain (Day 180) | 1–5 lakh/day network | USD 8k–25k | Dominant cost may be GSP, not AWS |
| Network GA | 10 lakh–1 crore/day aggregate | USD 40k–120k | Negotiate enterprise GSP |

Run FinOps from Day 1 (Cost Explorer + budgets). Retry storms against IRP can 10× cost and get the GSP suspended.

---

## 12. Team (90-day squad)

| Role | Count | Notes |
| --- | --- | --- |
| Product / domain (CA + GST/MyInvois) | 1 | Must sit with McM tax partners |
| Engineering lead | 1 | |
| Backend (invoice + adapters) | 3 | |
| Frontend (portals) | 1–2 | |
| Data / integration (Tally, SFTP) | 1 | |
| AWS / platform / security | 1 | |
| QA (schema + load) | 1 | |

From Day 90 add: customer success for member firms, second jurisdiction engineer, SOC 2 consultant.

---

## 13. Risks and controls

| Risk | Impact | Control |
| --- | --- | --- |
| Sandbox/prod credentials delayed | Schedule | Start paperwork Day 1; have backup GSP |
| Building a GSP instead of an ASP | 6–12 month delay | Out of scope v1 |
| Duplicate IRN / lost write-back | Legal invalid invoices | Idempotency store + Get IRN fallback |
| Cross-tenant data leak | Network-ending event | RLS + automated tenant isolation tests |
| IRP throttling / 1-hour ban | Business stop | Per-GSTIN FIFO, jitter, circuit breaker |
| Treating salary as e-invoice | Wrong law | Payroll adapter allow-list |
| Malaysia consolidation after RM10k rule | Penalties | Hard stop in validator |
| Independent firms sharing one AWS account badly | Legal | Org SCPs, per-tenant KMS, contracts |
| Scope explosion (UAE+KSA+EU in v1) | Never ships | Two jurisdictions max in 180 days |

---

## 14. Decision needed in week 1

1. **First jurisdiction:** India GST or Malaysia MyInvois?
2. **First domain:** trading B2B is the correct default.
3. **GSP / YGL:** which named partner, and who signs.
4. **Operating entity:** which McM legal entity holds the AWS org and customer contracts.
5. **Pilot clients:** three named entities with live volume.

Until those five are answered, engineering can only build the empty landing zone (Phase 1), not clearance.

---

## 15. Recommendation

Build **McM Invoice Cloud** as a **multi-tenant ASP on AWS**, not a one-off RPA on Tally.

- **Day 90:** first legal e-invoices in one country, thousands/day, one domain, three pilots.
- **Day 180:** five domain packs, lakhs/day tracking, two countries started.
- **Day 270–360:** network product for 250 offices, crore-scale **aggregate** analytics, SOC 2.

That is the honest end-to-end plan. Anything advertised as “we will finish this in a week because we have AWS” will produce PDFs, not IRNs/UINs, and PDFs are still paper in electronic clothing under GST and MyInvois.

---

## Appendix A — Site pages used

- Home: network positioning, TAX/AUDIT/ADVISORY, 77+ / 250+ / 3200+
- About Us: independent association, peer review, Executive Committee
- Services: Accountancy (payroll, bookkeeping), Outsourcing, Taxation Advisory (VAT/GST)
- Global Offices: ASEAN, South Asia (multiple India cities), GCC, UK, Africa, Americas
- Event: [Beyond e-Invoice Compliance in Malaysia](https://www.mcmillanwoods.com/2024/06/26/beyond-e-invoice-compliance-in-malaysia/) (26 Jun 2024, YGL-World collaboration)
- Contacts: 305 Block E, Phileo Damansara 1, Petaling Jaya, Malaysia

## Appendix B — External standards the adapters must implement

- GSTN e-invoice JSON schema v1.1 / NIC sandbox APIs (Generate IRN, Get IRN, Cancel, EWB by IRN)
- IRBM e-Invoice Guideline + Specific Guideline (MyInvois; self-billed; consolidated; perquisites)
- UBL 2.1 / Peppol BIS Billing (future UAE, SG, EU)
- ZATCA 1.0 XML (future KSA)
- ISO 20022 not required for v1 invoicing (payments later)

## Appendix C — Suggested repositories (when build starts)

```
mcm-invoice-cloud/
  infra/                 Terraform
  services/invoice-core  Canonical + tax
  services/clearance-in  NIC adapter
  services/clearance-my  MyInvois adapter
  services/ingest        Connectors
  apps/firm-portal
  apps/ops-console
  packages/schema        JSON Schema + OpenAPI
```

Do not start all of these on Day 1. Start `infra`, `invoice-core`, `firm-portal`, and **one** clearance adapter.
