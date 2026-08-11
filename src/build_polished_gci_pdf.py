from pathlib import Path
import json

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "data_outputs"
PDF = BASE / "docs" / "GCI_Telecom_Churn_Proposal.pdf"

W, H = landscape((13.333 * inch, 7.5 * inch))
M = 0.55 * inch

NAVY = colors.HexColor("#0B1220")
INK = colors.HexColor("#111827")
SLATE = colors.HexColor("#475569")
MUTED = colors.HexColor("#64748B")
LINE = colors.HexColor("#D8E0EA")
PANEL = colors.HexColor("#F6F8FB")
TEAL = colors.HexColor("#0F766E")
TEAL2 = colors.HexColor("#14B8A6")
RED = colors.HexColor("#DC2626")
AMBER = colors.HexColor("#D97706")
BLUE = colors.HexColor("#2563EB")
GREEN_BG = colors.HexColor("#EAFBF5")
RED_BG = colors.HexColor("#FEF2F2")
BLUE_BG = colors.HexColor("#EEF5FF")
AMBER_BG = colors.HexColor("#FFF7ED")


TITLE = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=INK)
SUB = ParagraphStyle("Sub", fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=TEAL, spaceAfter=0)
BODY = ParagraphStyle("Body", fontName="Helvetica", fontSize=12.5, leading=17, textColor=colors.HexColor("#273449"))
BODY_CENTER = ParagraphStyle("BodyCenter", parent=BODY, alignment=TA_CENTER)
SMALL = ParagraphStyle("Small", fontName="Helvetica", fontSize=8.2, leading=10.5, textColor=MUTED)
CARD_HEAD = ParagraphStyle("CardHead", fontName="Helvetica-Bold", fontSize=12.5, leading=15, textColor=INK)
CARD_BODY = ParagraphStyle("CardBody", fontName="Helvetica", fontSize=10.6, leading=14, textColor=SLATE)


def money(x):
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:.2f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:.0f}k"
    return f"${x:,.0f}"


def pct(x):
    return f"{x:.1%}"


def para(c, text, x, y, w, h, style=BODY):
    p = Paragraph(text, style)
    p.wrapOn(c, w, h)
    p.drawOn(c, x, y + h - p.height)


def page(c, n, section="GCI World 2026 Final Assignment"):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(0, H - 0.12 * inch, W, 0.12 * inch, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.5)
    c.drawString(M, 0.22 * inch, "Internal analysis of Company A Client.csv + Record.csv unless otherwise noted.")
    c.drawRightString(W - M, 0.22 * inch, f"{section}  |  {n}/13")


def heading(c, title, kicker=None):
    if kicker:
        para(c, kicker.upper(), M, H - 0.73 * inch, 8.5 * inch, 0.16 * inch, SUB)
    para(c, title, M, H - 1.16 * inch, 11.6 * inch, 0.38 * inch, TITLE)
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.line(M, H - 1.32 * inch, W - M, H - 1.32 * inch)


def card(c, x, y, w, h, fill=PANEL, stroke=None, radius=10):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1 if stroke else 0)


def kpi(c, x, y, w, h, label, value, accent=TEAL, note=None):
    card(c, x, y, w, h, colors.white, LINE, 9)
    c.setFillColor(accent)
    c.roundRect(x, y, 0.08 * inch, h, 4, fill=1, stroke=0)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(x + 0.22 * inch, y + h - 0.42 * inch, value)
    c.setFillColor(SLATE)
    c.setFont("Helvetica-Bold", 8.7)
    c.drawString(x + 0.22 * inch, y + 0.24 * inch, label.upper())
    if note:
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.8)
        c.drawRightString(x + w - 0.15 * inch, y + 0.24 * inch, note)


def bullets(c, items, x, y, w, leading=0.46 * inch):
    yy = y
    for item in items:
        c.setFillColor(TEAL)
        c.circle(x + 0.06 * inch, yy + 0.15 * inch, 3.2, fill=1, stroke=0)
        para(c, item, x + 0.22 * inch, yy - 0.05 * inch, w - 0.25 * inch, 0.37 * inch, BODY)
        yy -= leading


def note_box(c, x, y, w, h, title, body, fill=GREEN_BG, accent=TEAL):
    card(c, x, y, w, h, fill, None, 10)
    c.setFillColor(accent)
    c.roundRect(x, y, 0.08 * inch, h, 4, fill=1, stroke=0)
    para(c, title, x + 0.22 * inch, y + h - 0.38 * inch, w - 0.4 * inch, 0.22 * inch, CARD_HEAD)
    para(c, body, x + 0.22 * inch, y + 0.25 * inch, w - 0.45 * inch, h - 0.72 * inch, CARD_BODY)


def bar_chart(c, x, y, w, h, labels, values, color_fn, baseline=None, percent=True, maxv=None):
    maxv = maxv or max(values + ([baseline] if baseline else [])) * 1.18
    plot_y = y + 0.45 * inch
    plot_h = h - 0.78 * inch
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.line(x, plot_y, x + w, plot_y)
    n = len(values)
    gap = 0.12 * inch
    bw = (w - gap * (n - 1)) / n
    for i, (lab, val) in enumerate(zip(labels, values)):
        bx = x + i * (bw + gap)
        bh = max(0.02 * inch, val / maxv * plot_h)
        c.setFillColor(color_fn(i, val))
        c.roundRect(bx, plot_y, bw, bh, 4, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8.2)
        txt = pct(val) if percent else f"{val:.2f}"
        c.drawCentredString(bx + bw / 2, plot_y + bh + 0.08 * inch, txt)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawCentredString(bx + bw / 2, y + 0.16 * inch, str(lab))
    if baseline is not None:
        by = plot_y + baseline / maxv * plot_h
        c.setStrokeColor(INK)
        c.setDash(4, 3)
        c.line(x, by, x + w, by)
        c.setDash()
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawRightString(x + w, by + 0.05 * inch, f"Avg {pct(baseline)}")


def line_chart(c, x, y, w, h, labels, values, accent=RED):
    ymin = min(values) * 0.92
    ymax = max(values) * 1.08
    plot_y = y + 0.45 * inch
    plot_h = h - 0.78 * inch
    c.setStrokeColor(LINE)
    c.line(x, plot_y, x + w, plot_y)
    pts = []
    for i, v in enumerate(values):
        px = x + i * w / (len(values) - 1)
        py = plot_y + (v - ymin) / (ymax - ymin) * plot_h
        pts.append((px, py))
    c.setStrokeColor(accent)
    c.setLineWidth(3)
    for a, b in zip(pts, pts[1:]):
        c.line(a[0], a[1], b[0], b[1])
    for (px, py), lab, v in zip(pts, labels, values):
        c.setFillColor(accent)
        c.circle(px, py, 4.5, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(px, py + 0.12 * inch, pct(v))
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawCentredString(px, y + 0.16 * inch, str(lab))


def section_tag(c, text, x, y, color=TEAL):
    c.setFillColor(color)
    c.roundRect(x, y, 1.18 * inch, 0.26 * inch, 7, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(x + 0.59 * inch, y + 0.08 * inch, text.upper())


def load_data():
    with open(OUT / "analysis_summary.json", encoding="utf-8") as f:
        payload = json.load(f)
    return {
        **payload,
        "equip": pd.read_csv(OUT / "equipment_age_churn.csv"),
        "usage": pd.read_csv(OUT / "usage_churn.csv"),
        "gains": pd.read_csv(OUT / "model_gain_deciles.csv"),
        "coef": pd.read_csv(OUT / "logistic_coefficients.csv"),
    }


def cover(c, d):
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(TEAL2)
    c.rect(0, 0, 0.22 * inch, H, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1E293B"))
    c.circle(11.4 * inch, 5.8 * inch, 1.5 * inch, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#0F766E"))
    c.circle(12.2 * inch, 4.8 * inch, 1.0 * inch, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 38)
    c.drawString(0.78 * inch, 4.72 * inch, "Predictive Retention Program")
    c.setFont("Helvetica", 20)
    c.setFillColor(colors.HexColor("#DDE7F3"))
    c.drawString(0.78 * inch, 4.25 * inch, "Machine-learning-based business proposal for Company A")
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(TEAL2)
    c.drawString(0.78 * inch, 3.72 * inch, "GCI WORLD 2026 FINAL ASSIGNMENT | TELECOM CHURN POC")
    x = 0.78 * inch
    for label, value in [("Data", "100,000 customers"), ("Target", "31-60 day churn"), ("Proposal", "Targeted Save Desk")]:
        card(c, x, 1.2 * inch, 2.55 * inch, 0.9 * inch, colors.HexColor("#111827"), colors.HexColor("#334155"), 10)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 17)
        c.drawString(x + 0.18 * inch, 1.63 * inch, value)
        c.setFillColor(colors.HexColor("#94A3B8"))
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x + 0.18 * inch, 1.36 * inch, label.upper())
        x += 2.85 * inch
    c.showPage()


def slide2(c, d):
    page(c, 2); heading(c, "Recommendation: target likely churners before they disengage", "Executive answer")
    s, m, i = d["summary"], d["metrics"], d["impact"]
    kpi(c, M, 5.1 * inch, 2.25 * inch, 0.82 * inch, "Current churn rate", pct(s["churn_rate"]), RED)
    kpi(c, 3.15 * inch, 5.1 * inch, 2.55 * inch, 0.82 * inch, "Monthly revenue at risk", money(i["full_base_monthly_revenue_at_risk"]), RED)
    kpi(c, 6.0 * inch, 5.1 * inch, 2.45 * inch, 0.82 * inch, "Model ROC-AUC", f"{m['roc_auc']:.3f}", TEAL)
    kpi(c, 8.75 * inch, 5.1 * inch, 2.45 * inch, 0.82 * inch, "Net margin upside", money(i["estimated_net_margin_impact"]), TEAL)
    bullets(c, [
        "<b>Launch a Predictive Save Desk</b> for the highest-risk 20% of customers instead of discounting the whole base.",
        "<b>Use reason-based offers</b>: handset refresh for old devices, plan right-sizing for usage decline, and human support for complex service issues.",
        "<b>Measure incrementality</b> through an A/B pilot, then scale only the offers that beat their cost.",
    ], M, 4.24 * inch, 7.4 * inch)
    note_box(c, 8.3 * inch, 2.05 * inch, 3.5 * inch, 2.0 * inch, "Business case", f"Targeting the model's top 20% risk queue gives {pct(i['top20_churn_rate'])} actual churn, {i['top20_lift_vs_average']:.2f}x the base rate. Under conservative assumptions, the pilot creates about {money(i['estimated_net_margin_impact'])} net margin.", GREEN_BG, TEAL)
    c.showPage()


def slide3(c, d):
    page(c, 3); heading(c, "Market research supports a retention-led proposal", "External context")
    note_box(c, M, 4.25 * inch, 3.55 * inch, 1.55 * inch, "Churn is strategic", "Telecom is highly competitive; the literature treats retention as a priority because acquisition is expensive and customers can switch repeatedly. [S1]", BLUE_BG, BLUE)
    note_box(c, 4.55 * inch, 4.25 * inch, 3.55 * inch, 1.55 * inch, "Customers value practical fixes", "KPMG consumer research highlights customer service, network reliability, device upgrade discounts, plan pricing, and affordable 5G as switching factors. [S2]", GREEN_BG, TEAL)
    note_box(c, 8.55 * inch, 4.25 * inch, 3.55 * inch, 1.55 * inch, "AI must be operational", "McKinsey argues AI creates value when embedded across the customer journey, including retention and churn reduction. [S3]", AMBER_BG, AMBER)
    para(c, "<b>Implication for Company A:</b> the correct PoC is not a technical churn dashboard. It is a retention operating model that uses ML to decide who to contact, why to contact them, and which offer has a measurable payback.", M, 2.2 * inch, 10.9 * inch, 0.8 * inch, BODY)
    c.showPage()


def slide4(c, d):
    page(c, 4); heading(c, "PoC design: define churn, rank customers, quantify the save case", "Method")
    steps = [
        ("1", "Join data", "Merged Client.csv and Record.csv on Customer_ID; final table has 100,000 customers and 100 columns."),
        ("2", "Define target", "Use dataset churn field: customer churn between 31-60 days after observation."),
        ("3", "Train model", "Build a transparent L2-regularized logistic regression using usage, revenue, device, account, and household fields."),
        ("4", "Use ranking", "Sort customers by predicted churn risk and test whether top-risk segments justify retention spend."),
    ]
    for idx, (num, head, body) in enumerate(steps):
        y = 4.95 * inch - idx * 0.88 * inch
        c.setFillColor(TEAL)
        c.circle(M + 0.18 * inch, y + 0.2 * inch, 0.18 * inch, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(M + 0.18 * inch, y + 0.155 * inch, num)
        para(c, f"<b>{head}</b><br/>{body}", M + 0.55 * inch, y - 0.02 * inch, 9.8 * inch, 0.52 * inch, BODY)
    c.showPage()


def slide5(c, d):
    page(c, 5); heading(c, "The churn problem is large and revenue-relevant", "EDA finding 1")
    s, i = d["summary"], d["impact"]
    kpi(c, M, 4.95 * inch, 2.35 * inch, 0.95 * inch, "Churned customers", f"{i['full_base_churners']:,}", RED)
    kpi(c, 3.15 * inch, 4.95 * inch, 2.35 * inch, 0.95 * inch, "Base churn rate", pct(s["churn_rate"]), RED)
    kpi(c, 5.95 * inch, 4.95 * inch, 2.45 * inch, 0.95 * inch, "Avg monthly revenue", money(s["avg_monthly_revenue"]), TEAL)
    kpi(c, 8.85 * inch, 4.95 * inch, 2.65 * inch, 0.95 * inch, "Monthly revenue at risk", money(i["full_base_monthly_revenue_at_risk"]), RED)
    bar_chart(c, M, 1.25 * inch, 4.8 * inch, 2.8 * inch, ["Retained", "Churned"], [1 - s["churn_rate"], s["churn_rate"]], lambda idx, v: TEAL if idx == 0 else RED, maxv=0.65)
    note_box(c, 6.0 * inch, 1.42 * inch, 4.9 * inch, 2.25 * inch, "Interpretation", "Nearly half the customer base churned in the target window. Churners have similar monthly revenue to retained customers, so the problem is not limited to low-value accounts.", RED_BG, RED)
    c.showPage()


def slide6(c, d):
    page(c, 6); heading(c, "Device age and lower current usage are actionable warning signals", "EDA finding 2")
    equip = d["equip"]; usage = d["usage"]
    line_chart(c, M, 3.55 * inch, 5.4 * inch, 2.2 * inch, equip["equipment_age_band"].astype(str).tolist(), equip["churn_rate"].tolist(), RED)
    para(c, "<b>Handset age:</b> churn rises from 39.9% for devices under 90 days old to 57.9% for devices older than 731 days.", M, 2.85 * inch, 5.4 * inch, 0.45 * inch, BODY)
    bar_chart(c, 6.55 * inch, 3.55 * inch, 5.4 * inch, 2.2 * inch, usage["usage_band"].astype(str).tolist(), usage["churn_rate"].tolist(), lambda idx, v: RED if idx < 2 else TEAL if idx > 2 else MUTED, maxv=0.62)
    para(c, "<b>Usage:</b> lower minutes of use are an early signal of disengagement, so outreach should happen before the customer goes quiet.", 6.55 * inch, 2.85 * inch, 5.4 * inch, 0.45 * inch, BODY)
    c.showPage()


def slide7(c, d):
    page(c, 7); heading(c, "Model performance is enough for prioritization, not automatic decisions", "ML result")
    m = d["metrics"]
    kpi(c, M, 4.9 * inch, 3.1 * inch, 0.95 * inch, "Model name", "L2 Logistic Regression", TEAL)
    kpi(c, 3.85 * inch, 4.9 * inch, 2.35 * inch, 0.95 * inch, "Evaluation metric", "ROC-AUC", TEAL)
    kpi(c, 6.75 * inch, 4.9 * inch, 1.75 * inch, 0.95 * inch, "Score", f"{m['roc_auc']:.3f}", TEAL)
    kpi(c, 9.05 * inch, 4.9 * inch, 1.75 * inch, 0.95 * inch, "PR-AUC", f"{m['pr_auc']:.3f}", BLUE)
    note_box(c, M, 2.45 * inch, 5.25 * inch, 1.65 * inch, "Why this model", "Logistic regression is transparent, stable for a PoC, and easy to explain to executives. It also provides feature directions that can be translated into retention actions.", BLUE_BG, BLUE)
    note_box(c, 6.25 * inch, 2.45 * inch, 5.25 * inch, 1.65 * inch, "How to read the score", "AUC 0.628 is modest, but useful for ranking. The business test is whether the top-risk queue has higher actual churn than random targeting.", GREEN_BG, TEAL)
    c.showPage()


def slide8(c, d):
    page(c, 8); heading(c, "The model creates a better retention queue", "Targeting lift")
    gains = d["gains"]; i = d["impact"]
    bar_chart(c, M, 2.05 * inch, 6.2 * inch, 3.5 * inch, gains["risk_decile"].astype(str).tolist(), gains["churn_rate"].tolist(), lambda idx, v: RED if idx < 2 else colors.HexColor("#94A3B8"), baseline=i["baseline_churn_rate"], maxv=0.75)
    note_box(c, 7.15 * inch, 3.95 * inch, 3.9 * inch, 1.35 * inch, "Top-risk concentration", f"The top decile churns at 66.9%; the top 20% churns at {pct(i['top20_churn_rate'])}, capturing {pct(i['top20_capture_rate'])} of all churners.", RED_BG, RED)
    note_box(c, 7.15 * inch, 2.1 * inch, 3.9 * inch, 1.35 * inch, "Business translation", "Use the score to rank the sales/service queue. Do not use it as a standalone reason to discount every customer.", GREEN_BG, TEAL)
    c.showPage()


def slide9(c, d):
    page(c, 9); heading(c, "Drivers become a reason-based intervention menu", "From model to action")
    coef = d["coef"][d["coef"]["feature"] != "intercept"].head(7)
    bar_chart(c, M, 2.0 * inch, 5.3 * inch, 3.35 * inch, [str(x)[:12] for x in coef["feature"]], coef["abs_coefficient"].tolist(), lambda idx, v: BLUE, percent=False, maxv=max(coef["abs_coefficient"]) * 1.25)
    note_box(c, 6.25 * inch, 4.35 * inch, 4.7 * inch, 1.0 * inch, "Device refresh", "Older equipment is the clearest operational trigger. Offer upgrade credit/financing only where churn risk is high.", GREEN_BG, TEAL)
    note_box(c, 6.25 * inch, 3.05 * inch, 4.7 * inch, 1.0 * inch, "Usage recovery", "Usage decline should trigger plan-fit and service-quality outreach before the customer stops engaging.", BLUE_BG, BLUE)
    note_box(c, 6.25 * inch, 1.75 * inch, 4.7 * inch, 1.0 * inch, "Household plan fit", "Multiple subscribers should be treated as account-level retention opportunities, not isolated lines.", AMBER_BG, AMBER)
    c.showPage()


def slide10(c, d):
    page(c, 10); heading(c, "Proposed solution: Predictive Save Desk", "Business proposal")
    xs = [M, 3.35 * inch, 6.15 * inch, 8.95 * inch]
    items = [
        ("Score", "Refresh churn risk weekly for every active customer."),
        ("Explain", "Attach reason codes: device age, usage decline, plan/revenue fit."),
        ("Route", "Send customers to the best channel: app, store, live agent, or care desk."),
        ("Learn", "Feed offer outcome and churn results back into the next scoring cycle."),
    ]
    for x, (head, body) in zip(xs, items):
        card(c, x, 3.25 * inch, 2.35 * inch, 1.95 * inch, colors.white, LINE, 10)
        section_tag(c, head, x + 0.18 * inch, 4.72 * inch)
        para(c, body, x + 0.2 * inch, 3.65 * inch, 1.92 * inch, 0.7 * inch, CARD_BODY)
    c.setStrokeColor(TEAL)
    c.setLineWidth(2)
    for x in xs[:-1]:
        c.line(x + 2.35 * inch, 4.2 * inch, x + 2.65 * inch, 4.2 * inch)
    note_box(c, M, 1.35 * inch, 10.75 * inch, 0.95 * inch, "Customer promise", "Company A notices churn risk early and solves the practical reason the customer is likely to leave: device, plan, price, or service support.", GREEN_BG, TEAL)
    c.showPage()


def slide11(c, d):
    page(c, 11); heading(c, "Financial impact is positive even with conservative assumptions", "Quantified impact")
    i = d["impact"]
    kpi(c, M, 5.0 * inch, 2.15 * inch, 0.85 * inch, "Targets", f"{i['campaign_targets_full_base']:,}", TEAL)
    kpi(c, 2.85 * inch, 5.0 * inch, 2.35 * inch, 0.85 * inch, "Expected churners", f"{i['expected_churners_in_targets']:,.0f}", RED)
    kpi(c, 5.85 * inch, 5.0 * inch, 2.15 * inch, 0.85 * inch, "Saved at 15%", f"{i['expected_saved_customers']:,.0f}", TEAL)
    kpi(c, 8.65 * inch, 5.0 * inch, 2.45 * inch, 0.85 * inch, "Net margin", money(i["estimated_net_margin_impact"]), TEAL)
    bullets(c, [
        f"Campaign scope: top 20% of customers, or {i['campaign_targets_full_base']:,} customers.",
        f"Offer cost: ${i['assumed_offer_cost_per_target']:.0f} per targeted customer, or {money(i['estimated_offer_cost'])} total.",
        f"Value logic: saved customers keep 12 months of revenue at 55% gross margin.",
        f"Estimated result: {money(i['estimated_gross_margin_saved'])} gross margin saved less {money(i['estimated_offer_cost'])} campaign cost.",
    ], M, 4.02 * inch, 10.5 * inch, 0.42 * inch)
    c.showPage()


def slide12(c, d):
    page(c, 12); heading(c, "Pilot roadmap and controls", "Implementation")
    rows = [
        ("Weeks 1-2", "Data QA", "Validate target, leakage, eligibility, and missing values."),
        ("Weeks 3-5", "Scoring pilot", "Automate score output and build agent-readable reason codes."),
        ("Weeks 6-9", "A/B retention test", "Run targeted offers against a control group to measure incremental save rate."),
        ("Weeks 10-12", "Scale decision", "Compare margin ROI, complaints, conversion, and operational load."),
    ]
    for idx, (time, head, body) in enumerate(rows):
        y = 5.1 * inch - idx * 0.9 * inch
        c.setFillColor(TEAL)
        c.roundRect(M, y, 1.3 * inch, 0.35 * inch, 8, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(M + 0.65 * inch, y + 0.12 * inch, time)
        para(c, f"<b>{head}</b>", 2.1 * inch, y - 0.02 * inch, 2.0 * inch, 0.35 * inch, CARD_HEAD)
        para(c, body, 4.2 * inch, y - 0.03 * inch, 6.8 * inch, 0.38 * inch, BODY)
    note_box(c, M, 1.0 * inch, 10.9 * inch, 0.88 * inch, "Governance", "Monitor fairness, privacy, customer complaints, and offer profitability. A churn score should prioritize human review and experimentation, not create automatic customer treatment.", AMBER_BG, AMBER)
    c.showPage()


def slide13(c, d):
    page(c, 13); heading(c, "References", "Citations")
    refs = [
        "[S1] Ribeiro, H. et al. (2024). Determinants of churn in telecommunication services: a systematic literature review. Management Review Quarterly. https://link.springer.com/article/10.1007/s11301-023-00335-7",
        "[S2] KPMG (2024). KPMG 2024 Telecom Consumer Survey. https://kpmg.com/kpmg-us/content/dam/kpmg/pdf/2024/carriers-embrace-genai-wireless-customers-share-what-really-matters.pdf",
        "[S3] McKinsey & Company (2026). The telco reinvention: How AI can fuel value creation. https://www.mckinsey.com/~/media/mckinsey/industries/technology%20media%20and%20telecommunications/telecommunications/our%20insights/the%20telco%20reinvention%20how%20ai%20can%20fuel%20value%20creation/the-telco-reinvention-how-ai-can-fuel-value-creation.pdf",
        "[S4] Algorithms / MDPI (2024). Prediction of Customer Churn Behavior in the Telecommunication Industry Using Machine Learning Models. https://www.mdpi.com/2805466",
        "[D1] GCI World 2026 Final Assignment README and Company A Dataset Overview, provided course materials.",
        "Add the generative AI chat-history URL in Omnicampus if required by course policy.",
    ]
    y = 5.65 * inch
    for ref in refs:
        para(c, ref, M, y - 0.4 * inch, 11.6 * inch, 0.45 * inch, SMALL)
        y -= 0.63 * inch
    c.showPage()


def build():
    d = load_data()
    c = canvas.Canvas(str(PDF), pagesize=(W, H))
    cover(c, d)
    for fn in [slide2, slide3, slide4, slide5, slide6, slide7, slide8, slide9, slide10, slide11, slide12, slide13]:
        fn(c, d)
    c.save()
    print(PDF)


if __name__ == "__main__":
    build()
