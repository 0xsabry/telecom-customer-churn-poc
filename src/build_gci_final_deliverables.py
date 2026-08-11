from pathlib import Path
import json
import textwrap

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.utils import ImageReader


BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "data_outputs"
CHARTS = BASE / "charts"
PDF = BASE / "docs" / "GCI_Telecom_Churn_Proposal.pdf"
NB = BASE / "notebooks" / "GCI_Telecom_Churn_Analysis.ipynb"
REFS = BASE / "docs" / "references_for_omnicampus.txt"

W, H = landscape((13.333 * inch, 7.5 * inch))
M = 0.48 * inch


with open(OUT / "analysis_summary.json", encoding="utf-8") as f:
    DATA = json.load(f)

summary = DATA["summary"]
metrics = DATA["metrics"]
impact = DATA["impact"]

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="BodyDeck",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=15,
    leading=20,
    textColor=colors.HexColor("#1F2937"),
    alignment=TA_LEFT,
))
styles.add(ParagraphStyle(
    name="SmallDeck",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=colors.HexColor("#64748B"),
))


def hex_color(value):
    return colors.HexColor(value)


def footer(c, n, source="Internal analysis of Company A Client.csv + Record.csv unless noted."):
    c.setFont("Helvetica", 7.5)
    c.setFillColor(hex_color("#64748B"))
    c.drawString(M, 0.22 * inch, source)
    c.drawRightString(W - M, 0.22 * inch, f"{n}/14")


def title(c, text, subtitle=None):
    c.setFillColor(hex_color("#111827"))
    c.setFont("Helvetica-Bold", 25)
    c.drawString(M, H - 0.72 * inch, text)
    if subtitle:
        c.setFillColor(hex_color("#0F766E"))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(M, H - 0.95 * inch, subtitle.upper())


def p(c, text, x, y, w, h, style="BodyDeck"):
    para = Paragraph(text, styles[style])
    para.wrapOn(c, w, h)
    para.drawOn(c, x, y + h - para.height)


def bullet_list(c, items, x, y, w, size=14, leading=19):
    c.setFont("Helvetica", size)
    c.setFillColor(hex_color("#1F2937"))
    yy = y
    for item in items:
        wrapped = textwrap.wrap(item, width=72)
        c.setFillColor(hex_color("#0F766E"))
        c.circle(x + 4, yy + 6, 3, fill=1, stroke=0)
        c.setFillColor(hex_color("#1F2937"))
        for j, line in enumerate(wrapped):
            c.drawString(x + 18, yy - j * leading, line)
        yy -= leading * max(1, len(wrapped)) + 8


def kpi(c, label, value, x, y, w, color="#0F766E"):
    c.setFillColor(hex_color("#F8FAFC"))
    c.roundRect(x, y, w, 0.95 * inch, 8, fill=1, stroke=0)
    c.setFillColor(hex_color(color))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(x + 0.18 * inch, y + 0.48 * inch, value)
    c.setFillColor(hex_color("#475569"))
    c.setFont("Helvetica", 9.5)
    c.drawString(x + 0.18 * inch, y + 0.18 * inch, label)


def add_chart(c, image, x, y, w, h):
    c.drawImage(ImageReader(str(CHARTS / image)), x, y, width=w, height=h, preserveAspectRatio=True, mask="auto")


def slide_1(c):
    c.setFillColor(hex_color("#0F172A"))
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(hex_color("#14B8A6"))
    c.rect(0, 0, 0.22 * inch, H, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 38)
    c.drawString(0.75 * inch, 4.55 * inch, "Predictive Retention Program")
    c.setFont("Helvetica", 21)
    c.drawString(0.75 * inch, 4.08 * inch, "A machine-learning-based business proposal for Company A")
    c.setFont("Helvetica", 13)
    c.setFillColor(hex_color("#CBD5E1"))
    c.drawString(0.75 * inch, 3.55 * inch, "GCI World 2026 Final Assignment | Telecom customer churn PoC")
    kpi(c, "Dataset size", "100k customers", 0.75 * inch, 1.45 * inch, 2.35 * inch, "#14B8A6")
    kpi(c, "ML task", "Churn prediction", 3.35 * inch, 1.45 * inch, 2.35 * inch, "#14B8A6")
    kpi(c, "Proposal theme", "Targeted save desk", 5.95 * inch, 1.45 * inch, 2.55 * inch, "#14B8A6")
    footer(c, 1, "Source: Company A dataset and assignment materials.")


def slide_2(c):
    title(c, "Executive recommendation", "Answer first")
    kpi(c, "Current churn rate", f"{summary['churn_rate']:.1%}", M, 4.9 * inch, 2.25 * inch, "#DC2626")
    kpi(c, "Monthly revenue exposed to churn", f"${impact['full_base_monthly_revenue_at_risk']/1e6:.2f}M", 3.0 * inch, 4.9 * inch, 2.6 * inch, "#DC2626")
    kpi(c, "Estimated net margin impact", f"${impact['estimated_net_margin_impact']/1000:.0f}k", 5.95 * inch, 4.9 * inch, 2.6 * inch, "#0F766E")
    kpi(c, "Campaign ROI", f"{impact['roi_multiple']:.1f}x", 8.9 * inch, 4.9 * inch, 2.05 * inch, "#0F766E")
    bullet_list(c, [
        "Company A should launch a predictive retention program focused on the top 20% highest-risk customers, not a broad discount campaign.",
        "The first offer should combine handset refresh support, proactive service outreach, and right-sized plan consultation.",
        "Use churn risk scores weekly so frontline teams intervene before customers stop using the service or replace the handset elsewhere.",
    ], M, 4.05 * inch, 11 * inch)
    footer(c, 2)


def slide_3(c):
    title(c, "Market context", "Why retention is the right business problem")
    bullet_list(c, [
        "Telecom is structurally competitive: switching barriers are limited, and churn is treated as a core management KPI in the literature [S1, S4].",
        "Recent consumer research shows switching is driven by practical needs: better customer service, better network reliability, device upgrade discounts, plan pricing, and affordable 5G [S2].",
        "AI-enabled customer journey improvements can create revenue and churn-reduction upside when embedded into retention operations rather than used as a dashboard only [S3].",
    ], M, 5.4 * inch, 7.5 * inch)
    c.setFillColor(hex_color("#ECFDF5"))
    c.roundRect(8.7 * inch, 1.5 * inch, 3.55 * inch, 4.55 * inch, 10, fill=1, stroke=0)
    p(c, "<b>Implication for Company A</b><br/><br/>The business case is not just predicting who will leave. The value comes from matching the reason-to-stay: device, service, price, and plan fit.", 9.05 * inch, 2.0 * inch, 2.85 * inch, 3.5 * inch)
    footer(c, 3, "Sources: [S1] Ribeiro et al. 2024; [S2] KPMG 2024 Telecom Consumer Survey; [S3] McKinsey 2026 telco AI report; [S4] MDPI Algorithms 2024.")


def slide_4(c):
    title(c, "Business objective and ML task", "PoC framing")
    bullet_list(c, [
        "Client problem: Company A has customer usage, revenue, handset, and demographic data but no in-house method to prioritize retention action.",
        "Target variable: churn, defined in the dataset as an instance of churn 31-60 days after the observation date.",
        "ML task: binary classification to estimate each customer's probability of churn.",
        "Decision use: rank customers for a save campaign, then evaluate whether targeted intervention beats untargeted retention spending.",
    ], M, 5.35 * inch, 8.2 * inch)
    kpi(c, "Rows after join", f"{summary['rows']:,}", M, 1.7 * inch, 2.3 * inch)
    kpi(c, "Features used", "98", 3.0 * inch, 1.7 * inch, 2.0 * inch)
    kpi(c, "Target horizon", "31-60 days", 5.45 * inch, 1.7 * inch, 2.2 * inch)
    kpi(c, "Holdout test", f"{metrics['test_rows']:,} rows", 8.1 * inch, 1.7 * inch, 2.3 * inch)
    footer(c, 4)


def slide_5(c):
    title(c, "Churn is large enough to be the central business problem", "EDA")
    add_chart(c, "churn_rate.png", M, 1.35 * inch, 5.7 * inch, 4.3 * inch)
    kpi(c, "Avg monthly revenue", f"${summary['avg_monthly_revenue']:.2f}", 6.8 * inch, 4.75 * inch, 2.4 * inch)
    kpi(c, "Churners' avg monthly revenue", f"${summary['avg_monthly_revenue_churners']:.2f}", 9.45 * inch, 4.75 * inch, 2.6 * inch, "#DC2626")
    bullet_list(c, [
        f"{impact['full_base_churners']:,} customers in the dataset churned during the target window.",
        f"The churned customers represent approximately ${impact['full_base_monthly_revenue_at_risk']/1e6:.2f}M of monthly revenue exposure.",
        "This supports a revenue-protection proposal rather than a generic customer analytics report.",
    ], 6.75 * inch, 3.7 * inch, 5.2 * inch, 13, 18)
    footer(c, 5)


def slide_6(c):
    title(c, "Device age and usage decline point to actionable retention levers", "EDA")
    add_chart(c, "equipment_age_churn.png", M, 1.0 * inch, 5.85 * inch, 4.45 * inch)
    add_chart(c, "usage_churn.png", 6.7 * inch, 1.0 * inch, 5.85 * inch, 4.45 * inch)
    p(c, "Interpretation: churn rises from 39.9% for handsets under 90 days old to 57.9% for devices older than 731 days. Current usage is also lower among churners, making declining engagement a practical trigger for outreach.", M, 5.55 * inch, 11.6 * inch, 0.55 * inch, "BodyDeck")
    footer(c, 6)


def slide_7(c):
    title(c, "Model result is modest but useful for prioritization", "ML model")
    kpi(c, "Model name", "L2 Logistic Regression", M, 4.95 * inch, 3.1 * inch)
    kpi(c, "Evaluation metric", "ROC-AUC", 3.55 * inch, 4.95 * inch, 2.25 * inch)
    kpi(c, "Score", f"{metrics['roc_auc']:.3f}", 6.25 * inch, 4.95 * inch, 1.85 * inch, "#0F766E")
    kpi(c, "PR-AUC", f"{metrics['pr_auc']:.3f}", 8.55 * inch, 4.95 * inch, 1.85 * inch, "#0F766E")
    bullet_list(c, [
        "Preprocessing: median imputation for numeric variables, standardization, and top-category one-hot encoding for categorical fields.",
        "Why logistic regression: transparent, stable for a PoC, and aligned with common telecom churn literature using statistical classification [S1].",
        "Executive meaning: the model is not perfect, but it separates higher-risk customers well enough to improve campaign targeting.",
    ], M, 3.95 * inch, 11.2 * inch)
    footer(c, 7)


def slide_8(c):
    title(c, "Risk ranking creates a better retention queue than random targeting", "ML insight")
    add_chart(c, "model_gain_deciles.png", M, 1.05 * inch, 6.2 * inch, 4.7 * inch)
    kpi(c, "Top 20% actual churn", f"{impact['top20_churn_rate']:.1%}", 7.1 * inch, 4.7 * inch, 2.35 * inch, "#DC2626")
    kpi(c, "Lift vs average", f"{impact['top20_lift_vs_average']:.2f}x", 9.75 * inch, 4.7 * inch, 1.95 * inch, "#0F766E")
    p(c, f"The highest-risk 20% captures {impact['top20_capture_rate']:.1%} of all holdout churners. The top decile alone has a 66.9% churn rate versus the {impact['baseline_churn_rate']:.1%} baseline.", 7.1 * inch, 2.1 * inch, 4.6 * inch, 1.4 * inch)
    footer(c, 8)


def slide_9(c):
    title(c, "The drivers translate into a concrete save playbook", "Model interpretability")
    add_chart(c, "feature_importance.png", M, 1.0 * inch, 5.9 * inch, 4.6 * inch)
    bullet_list(c, [
        "Aging equipment is the strongest model signal: offer upgrade credits or financing only when predicted churn risk is high.",
        "Usage change and monthly minutes indicate disengagement: contact customers before the line becomes inactive.",
        "Household/subscriber structure matters: family and multi-subscriber accounts need plan-fit checks, not individual-line offers only.",
    ], 6.65 * inch, 4.9 * inch, 5.2 * inch, 13, 18)
    footer(c, 9)


def slide_10(c):
    title(c, "Proposal: Predictive Save Desk", "Business model")
    bullet_list(c, [
        "Weekly scoring: refresh churn scores for all active customers and flag top 20% risk plus high revenue exposure.",
        "Offer routing: device refresh for old-handset customers, plan right-sizing for usage decline, and human support for repeated service contacts.",
        "Controlled rollout: A/B test targeted offers against a random-holdout group to measure incremental retention.",
        "Operating loop: feed campaign outcomes back into the score to improve precision and offer economics.",
    ], M, 5.45 * inch, 7.3 * inch)
    c.setFillColor(hex_color("#F1F5F9"))
    c.roundRect(8.35 * inch, 1.4 * inch, 3.75 * inch, 4.8 * inch, 10, fill=1, stroke=0)
    p(c, "<b>Customer promise</b><br/><br/>Company A notices service disengagement early and solves the practical reason the customer is about to leave: device, plan, price, or support.", 8.75 * inch, 2.0 * inch, 3.0 * inch, 3.55 * inch)
    footer(c, 10)


def slide_11(c):
    title(c, "Quantified impact case", "Assumptions made explicit")
    kpi(c, "Targets", f"{impact['campaign_targets_full_base']:,}", M, 4.85 * inch, 2.0 * inch)
    kpi(c, "Expected churners in targets", f"{impact['expected_churners_in_targets']:,.0f}", 2.55 * inch, 4.85 * inch, 2.6 * inch, "#DC2626")
    kpi(c, "Saved customers at 15%", f"{impact['expected_saved_customers']:,.0f}", 5.7 * inch, 4.85 * inch, 2.4 * inch)
    kpi(c, "Net margin impact", f"${impact['estimated_net_margin_impact']/1000:.0f}k", 8.65 * inch, 4.85 * inch, 2.5 * inch, "#0F766E")
    bullet_list(c, [
        "Campaign scope: top 20% of full base, or 20,000 customers.",
        "Offer cost assumption: $10 per targeted customer.",
        "Retention effectiveness assumption: 15% of otherwise-churning targeted customers are saved.",
        "Value assumption: saved customer keeps 12 months of revenue at 55% gross margin.",
        f"Estimated economics: ${impact['estimated_gross_margin_saved']/1000:.0f}k gross margin saved - ${impact['estimated_offer_cost']/1000:.0f}k offer cost = ${impact['estimated_net_margin_impact']/1000:.0f}k net impact.",
    ], M, 3.9 * inch, 11.4 * inch, 12.7, 17)
    footer(c, 11)


def slide_12(c):
    title(c, "90-day implementation roadmap", "From PoC to pilot")
    phases = [
        ("Weeks 1-2", "Data QA", "Confirm churn definition, remove leakage, validate customer eligibility."),
        ("Weeks 3-5", "Pilot scoring", "Automate weekly risk scoring and produce agent-ready reason codes."),
        ("Weeks 6-9", "A/B campaign", "Run device, plan, and support offers with a clean control group."),
        ("Weeks 10-12", "Scale decision", "Measure incremental retention, margin ROI, and operational load."),
    ]
    x = M
    for i, (time, head, body) in enumerate(phases):
        y = 4.65 * inch - i * 0.9 * inch
        c.setFillColor(hex_color("#0F766E"))
        c.roundRect(x, y, 1.25 * inch, 0.45 * inch, 6, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x + 0.625 * inch, y + 0.16 * inch, time)
        c.setFillColor(hex_color("#111827"))
        c.setFont("Helvetica-Bold", 16)
        c.drawString(x + 1.55 * inch, y + 0.22 * inch, head)
        c.setFont("Helvetica", 12.5)
        c.setFillColor(hex_color("#334155"))
        c.drawString(x + 3.25 * inch, y + 0.22 * inch, body)
    footer(c, 12)


def slide_13(c):
    title(c, "Risks and governance", "What must be controlled")
    bullet_list(c, [
        "Causality risk: a high churn score does not prove why the customer leaves; offer tests must measure incremental impact.",
        "Fairness risk: demographic variables should be monitored and can be excluded from production decisions if they create unfair treatment.",
        "Operational risk: do not overload call-center teams; cap daily queues and prioritize high-risk/high-value customers first.",
        "Privacy risk: use customer data only for clearly explained service improvement and retention purposes.",
    ], M, 5.35 * inch, 10.7 * inch)
    footer(c, 13)


def slide_14(c):
    title(c, "References", "For Omnicampus reference field")
    refs = [
        "[S1] Ribeiro, H. et al. (2024). Determinants of churn in telecommunication services: a systematic literature review. Management Review Quarterly. https://link.springer.com/article/10.1007/s11301-023-00335-7",
        "[S2] KPMG (2024). KPMG 2024 Telecom Consumer Survey. https://kpmg.com/kpmg-us/content/dam/kpmg/pdf/2024/carriers-embrace-genai-wireless-customers-share-what-really-matters.pdf",
        "[S3] McKinsey & Company (2026). The telco reinvention: How AI can fuel value creation. https://www.mckinsey.com/~/media/mckinsey/industries/technology%20media%20and%20telecommunications/telecommunications/our%20insights/the%20telco%20reinvention%20how%20ai%20can%20fuel%20value%20creation/the-telco-reinvention-how-ai-can-fuel-value-creation.pdf",
        "[S4] Amin et al. / Algorithms (2024). Prediction of Customer Churn Behavior in the Telecommunication Industry Using Machine Learning Models. https://www.mdpi.com/2805466",
        "[D1] GCI World 2026 Final Assignment README and Company A Dataset Overview, provided course materials.",
    ]
    y = 5.8 * inch
    for ref in refs:
        p(c, ref, M, y - 0.45 * inch, 11.8 * inch, 0.55 * inch, "SmallDeck")
        y -= 0.72 * inch
    footer(c, 14, "Add the same URLs to Omnicampus References; include the AI chat URL if required by your submission policy.")


def build_pdf():
    c = canvas.Canvas(str(PDF), pagesize=(W, H))
    for fn in [slide_1, slide_2, slide_3, slide_4, slide_5, slide_6, slide_7, slide_8, slide_9, slide_10, slide_11, slide_12, slide_13, slide_14]:
        fn(c)
        c.showPage()
    c.save()


def build_references():
    refs = [
        "https://link.springer.com/article/10.1007/s11301-023-00335-7",
        "https://kpmg.com/kpmg-us/content/dam/kpmg/pdf/2024/carriers-embrace-genai-wireless-customers-share-what-really-matters.pdf",
        "https://www.mckinsey.com/~/media/mckinsey/industries/technology%20media%20and%20telecommunications/telecommunications/our%20insights/the%20telco%20reinvention%20how%20ai%20can%20fuel%20value%20creation/the-telco-reinvention-how-ai-can-fuel-value-creation.pdf",
        "https://www.mdpi.com/2805466",
        "GCI World 2026 Final Assignment README and Company A Dataset Overview, provided course materials.",
        "Add your generative AI chat history URL here before submission, if required by Omnicampus.",
    ]
    REFS.write_text("\n".join(refs) + "\n", encoding="utf-8")


def build_notebook():
    code = Path(BASE / "gci_telecom_churn_analysis.py").read_text(encoding="utf-8")
    code = code.replace(
        "BASE = Path(__file__).resolve().parent",
        "BASE_CANDIDATES = [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent, Path(r'D:\\\\New Folder (4)\\\\Desktop\\\\GIC\\\\final')]\n"
        "BASE = next(p for p in BASE_CANDIDATES if (p / 'Client.csv').exists() and (p / 'Record.csv').exists())",
    )
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# GCI World 2026 Final Assignment - Company A Telecom Churn PoC\n",
                    "\n",
                    "This notebook loads `Client.csv` and `Record.csv`, performs EDA, trains an L2-regularized logistic regression churn model using pandas/numpy, and writes chart/summary outputs used in the final slides.\n",
                ],
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Method summary\n",
                    "- Target: `churn`, defined as churn 31-60 days after the observation date.\n",
                    "- Model: L2-regularized logistic regression.\n",
                    "- Metric: ROC-AUC on a 25% holdout set.\n",
                    "- Business use: rank the customer base and target the top-risk 20% with a retention offer.\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": code.splitlines(keepends=True),
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ["main()\n"],
            },
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NB.write_text(json.dumps(nb, indent=1), encoding="utf-8")


if __name__ == "__main__":
    build_pdf()
    build_references()
    build_notebook()
    print(PDF)
    print(NB)
    print(REFS)
