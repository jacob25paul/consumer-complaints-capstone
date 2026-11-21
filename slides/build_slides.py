"""Build slides/Capstone_Final_Slides.pptx (with speaker notes) and slides/notes.md from one source.

    python slides/build_slides.py
Every number on the slides comes from reports/model_metrics.* or the executed notebooks (see slides/notes.md).
"""
from pathlib import Path

import numpy as np

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIG = ROOT / "reports" / "figures"
OUT = HERE / "Capstone_Final_Slides.pptx"
NOTES_MD = HERE / "notes.md"

BLUE, RED, INK, GREY = RGBColor(0x4C, 0x78, 0xA8), RGBColor(0xE4, 0x57, 0x56), RGBColor(0x1D, 0x1D, 0x1F), RGBColor(0x6B, 0x6F, 0x76)
LIGHT, LIGHT_RED, WHITE = RGBColor(0xEE, 0xF3, 0xF9), RGBColor(0xFC, 0xEC, 0xEC), RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Arial"
W, H = 13.333, 7.5
MARGIN = 0.55

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]
SLIDES = []          # (title, minutes, notes) for notes.md


# ----------------------------------------------------------------------------------------------------- helpers
def text(slide, left, top, width, height, paras, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=6):
    """paras: list of strings or lists of (text, {bold, color, size, italic}) runs."""
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(spacing)
        runs = [(para, {})] if isinstance(para, str) else para
        for t, fmt in runs:
            r = p.add_run()
            r.text = t
            f = r.font
            f.name, f.size = FONT, Pt(fmt.get("size", size))
            f.bold = fmt.get("bold", bold)
            f.italic = fmt.get("italic", False)
            f.color.rgb = fmt.get("color", color)
    return tb


def box(slide, left, top, width, height, fill=LIGHT, line=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shp.adjustments[0] = 0.06
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
    shp.shadow.inherit = False
    return shp


def picture(slide, name, left, top, max_w, max_h, center=True):
    """Insert a figure scaled to fit (max_w x max_h) inches, centred in that box."""
    w_px, h_px = Image.open(FIG / name).size
    scale = min(max_w / w_px, max_h / h_px)
    w, h = w_px * scale, h_px * scale
    x = left + (max_w - w) / 2 if center else left
    y = top + (max_h - h) / 2
    slide.shapes.add_picture(str(FIG / name), Inches(x), Inches(y), Inches(w), Inches(h))
    return x, y, w, h


def tile(slide, left, top, width, height, big, label, color=BLUE, fill=LIGHT, big_size=30):
    box(slide, left, top, width, height, fill=fill)
    text(slide, left + 0.15, top + 0.08, width - 0.3, height * 0.5, [big], size=big_size, color=color, bold=True,
         anchor=MSO_ANCHOR.MIDDLE, spacing=0)
    text(slide, left + 0.15, top + height * 0.52, width - 0.3, height * 0.46, [label], size=13, color=INK, spacing=0)


def card(slide, left, top, width, height, heading, body, color=BLUE, fill=LIGHT, body_size=15):
    box(slide, left, top, width, height, fill=fill)
    text(slide, left + 0.2, top + 0.15, width - 0.4, 0.5, [heading], size=18, color=color, bold=True, spacing=0)
    text(slide, left + 0.2, top + 0.68, width - 0.4, height - 0.8, body, size=body_size, spacing=5)


def new_slide(kicker, title, minutes, notes, number=True):
    s = prs.slides.add_slide(BLANK)
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.18), Inches(H))
    bar.fill.solid()
    bar.fill.fore_color.rgb = BLUE
    bar.line.fill.background()
    if kicker:
        text(s, MARGIN, 0.32, 10, 0.35, [kicker.upper()], size=12, color=BLUE, bold=True, spacing=0)
    text(s, MARGIN, 0.6, W - 2 * MARGIN, 0.95, [title], size=27, bold=True, spacing=0)
    if number:
        idx = len(prs.slides)
        text(s, MARGIN, H - 0.42, 8, 0.3, ["Consumer complaint routing & relief prediction · Jacob Paul"], size=10, color=GREY, spacing=0)
        text(s, W - MARGIN - 1, H - 0.42, 1, 0.3, [str(idx)], size=10, color=GREY, align=PP_ALIGN.RIGHT, spacing=0)
    s.notes_slide.notes_text_frame.text = notes
    SLIDES.append((title, minutes, notes))
    return s


def caption(slide, top, s):
    text(slide, MARGIN, top, W - 2 * MARGIN, 0.35, [s], size=11, color=GREY, spacing=0)


def table(slide, left, top, width, rows, col_w, header_fill=BLUE, highlight_row=1, font=14):
    nrows, ncols = len(rows), len(rows[0])
    shp = slide.shapes.add_table(nrows, ncols, Inches(left), Inches(top), Inches(width), Inches(0.42 * nrows))
    tbl = shp.table
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = val
            r.font.name, r.font.size = FONT, Pt(font)
            r.font.bold = i == 0 or i == highlight_row
            r.font.color.rgb = WHITE if i == 0 else INK
            p.alignment = PP_ALIGN.RIGHT if (j > 0 and i > 0) else PP_ALIGN.LEFT
            cell.fill.solid()
            cell.fill.fore_color.rgb = header_fill if i == 0 else (LIGHT if i == highlight_row else WHITE)
            cell.margin_top = cell.margin_bottom = Inches(0.05)
    return shp


# ----------------------------------------------------------------------------------------------------- slides
# 1. Title
s = prs.slides.add_slide(BLANK)
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
band.fill.solid()
band.fill.fore_color.rgb = BLUE
band.line.fill.background()
text(s, 0.9, 1.7, 11.5, 0.4, ["SPRINGBOARD DATA SCIENCE CAREER TRACK · CAPSTONE THREE"], size=14, color=WHITE, bold=True)
text(s, 0.9, 2.25, 11.5, 2.0, ["Routing consumer complaints and finding the ones that end in monetary relief"],
     size=40, color=WHITE, bold=True, spacing=0)
text(s, 0.9, 4.35, 11.5, 0.9, ["NLP and gradient boosting on the CFPB Consumer Complaint Database, 2015–2025"],
     size=20, color=WHITE)
text(s, 0.9, 5.6, 11.5, 0.5, ["Jacob Paul · November 2026"], size=16, color=WHITE)
NOTE1 = ("Hi, thanks for making time. In the next twenty minutes I'll walk through my third capstone: two models that help a "
         "complaint-handling team at a bank or credit bureau. The first routes each complaint to the right product team. "
         "The second ranks complaints by how likely they are to end with the company paying money back, so the review team "
         "can look at those first. I'll cover the problem, the data and its limits, the key wrangling and EDA findings, how I "
         "set up a leakage-free time-based evaluation, the models, the test results, and what I'd recommend. I'll keep the "
         "last ten minutes for your questions.")
s.notes_slide.notes_text_frame.text = NOTE1
SLIDES.append(("Routing consumer complaints and finding the ones that end in monetary relief", 0.75, NOTE1))

# 2. Problem
s = new_slide("The problem", "Complaint teams do two jobs by hand: route each complaint, and decide which to review first", 1.25,
              "Banks, lenders and credit bureaus receive large volumes of complaints through the CFPB. Two things happen to "
              "every one of them. First, someone reads it and routes it to the team that handles that product: mortgages, "
              "cards, credit reports and so on. Second, a compliance team decides which complaints to look at first, ideally "
              "the ones involving real financial harm. My proposal turned these into two supervised tasks. Routing: predict "
              "the product, judged by macro-F1 so that small products count as much as big ones. Relief: rank complaints by "
              "the chance the company closes them with monetary relief rather than just an explanation, judged by average "
              "precision and precision in the top ten percent, because that is how a review queue would use it. And one "
              "question runs through the whole project: does the consumer's free-text narrative add anything beyond the "
              "fields of the complaint form?")
card(s, MARGIN, 1.85, 5.95, 3.3, "1 · Routing",
     ["Predict the product (11 classes) from the narrative and form fields.",
      [("Success: ", {"bold": True}), ("macro-F1 clearly above a majority-class baseline, with per-class results.", {})]])
card(s, MARGIN + 6.3, 1.85, 5.95, 3.3, "2 · Relief prioritisation",
     ["Rank complaints by the chance the company pays money back (monetary relief vs closed with explanation).",
      [("Success: ", {"bold": True}), ("average precision above the base rate and above a form-fields-only model, on a "
                                       "later period; precision in the top 10%.", {})]], color=RED, fill=LIGHT_RED)
box(s, MARGIN, 5.45, W - 2 * MARGIN, 1.15, fill=WHITE, line=BLUE)
text(s, MARGIN + 0.25, 5.5, W - 2 * MARGIN - 0.5, 1.05,
     [[("The question throughout: ", {"bold": True, "color": BLUE}),
       ("does the consumer's narrative add information beyond what the complaint form already records?", {})]],
     size=19, anchor=MSO_ANCHOR.MIDDLE)

# 3. Data
s = new_slide("Data and its limits", "17.5 million complaints, but narratives exist for only about one in five, and almost none after 2025", 1.25,
              "The data is the CFPB's narratives archive: 21 exports with 17,533,918 complaints from 2011 to August 2026. "
              "It is too big for my laptop, so I used a uniform random 20 percent sample, which keeps every rate unbiased. "
              "Two limits shaped everything. First, narratives are opt-in: about 22 percent of complaints have one, they only "
              "start in 2015, and the right panel shows opt-in collapsing in January 2026 before the CFPB stopped publishing "
              "narratives in August. Second, outcome maturity: the left panel shows the share of complaints still in progress. "
              "It is near zero until mid-2026, then 16 percent in July and 56 percent in August. Training on those months "
              "would teach the model that recent complaints never get relief, so I excluded them, and I treat the rest of 2026 "
              "as a separate out-of-distribution check. That leaves 758,548 usable narratives.")
picture(s, "20_outcome_maturity.png", MARGIN, 1.65, W - 2 * MARGIN, 3.55)
tile(s, MARGIN, 5.35, 3.95, 1.55, "17,533,918", "complaints in 21 CFPB archive exports (Dec 2011 – Aug 2026)")
tile(s, MARGIN + 4.17, 5.35, 3.95, 1.55, "758,548", "usable narratives in the 20% random sample (21.9% opt-in)")
tile(s, MARGIN + 8.34, 5.35, 3.95, 1.55, "16% · 56%", "still 'in progress' in Jul · Aug 2026: immature, excluded",
     color=RED, fill=LIGHT_RED)

# 4. Wrangling
s = new_slide("Data wrangling", "Four wrangling decisions, each forced by what the data showed", 1.25,
              "Four wrangling decisions mattered most, and each came from checking the data rather than assuming. "
              "Duplicates: the obvious rule, same text, company, product, issue and date, flagged 61,142 narratives, but most "
              "of those groups came from different ZIP codes. They are template letters sent by different people, not "
              "re-submissions, so I dropped only the 3,726 true same-consumer repeats and flagged the templates. Products: the "
              "CFPB renamed and split its product list over the years, so I mapped 21 raw labels onto today's 11 products, "
              "using the sub-product to resolve labels that were later split. Relief: I mapped each of the eight response "
              "labels explicitly and followed the proposal's target. And I flagged outliers instead of deleting them, and kept "
              "missing values as explicit categories, because the missingness is informative.")
cw, ch = 5.95, 2.35
card(s, MARGIN, 1.75, cw, ch, "Duplicates: drop only re-submissions",
     ["61,142 narratives repeat text, company, product, issue and date, but most groups span different ZIP codes.",
      "Dropped only 3,726 same-consumer re-submissions; 209,868 templated complaints flagged."])
card(s, MARGIN + 6.3, 1.75, cw, ch, "Products: 21 labels → 11",
     ["The CFPB renamed and split products over time.",
      "Mapped to the current taxonomy; labels that were later split are resolved by sub-product."])
card(s, MARGIN, 4.3, cw, ch, "Relief label: mapped response by response",
     ["8 response labels; labels with no final outcome are excluded.",
      "Target (proposal): monetary relief vs closed with explanation."], color=RED, fill=LIGHT_RED)
card(s, MARGIN + 6.3, 4.3, cw, ch, "Flag, don't delete",
     ["7,606 near-empty and 3,486 very long narratives flagged, not removed.",
      "No imputation: missing values kept as explicit categories."])

# 5. EDA 1
s = new_slide("Exploratory analysis · 1", "Relief depends mostly on the product and the company", 1.25,
              "The first EDA finding is the most important for modelling. Whether a complaint ends in monetary relief depends "
              "mostly on what it is about and who it is against. Among narrative complaints, prepaid cards get relief almost "
              "20 percent of the time and credit reporting 0.1 percent. By company, large banks and card issuers are far above "
              "the credit bureaus and debt buyers, which are near zero. The categorical association tests agree: issue, "
              "product and company have the strongest association with relief, a Cramér's V of about a third, while state and "
              "ZIP are weak. The implication: a model that only uses the form fields will already rank complaints well, so the "
              "bar for showing that the narrative adds value is high. These bars use notebook 1's exploratory relief "
              "definition; the modelling uses the proposal's definition.")
picture(s, "08_relief_rate_by_group.png", 5.45, 1.5, 7.35, 5.1)
text(s, MARGIN, 1.85, 4.75, 4.8,
     [[("19.8% vs 0.1%", {"bold": True, "color": RED, "size": 26})],
      "relief rate: prepaid card vs credit reporting",
      [("Company matters as much", {"bold": True, "color": BLUE, "size": 20})],
      "large banks and card issuers far above the credit bureaus",
      [("Cramér's V with relief", {"bold": True, "color": BLUE, "size": 20})],
      "issue 0.36 · product 0.34 · company 0.33; state and ZIP weak",
      [("→ a form-fields-only model is a strong baseline", {"bold": True, "size": 18})]], size=16, spacing=8)
caption(s, 6.75, "Narrative complaints, 95% Wilson intervals; notebook 01 definition (monetary relief vs any other closure).")

# 6. EDA 2
s = new_slide("Exploratory analysis · 2", "Everything drifts over time, so the evaluation has to be time-based", 1.25,
              "The second finding is drift. The left panel shows narrative volume growing quickly from 2022. The middle panel "
              "shows the product mix shifting toward credit reporting, which becomes about three quarters of narratives. The "
              "right panel shows the relief rate falling from 7.8 percent in 2015 to 1.3 percent in 2025. Much of that fall is "
              "the mix change, since credit reporting almost never ends in relief. Then 2026 jumps to 6.7 percent, but that is "
              "a composition effect: credit reporting drops to 4 percent of 2026 narratives. Two consequences. A random "
              "train-test split would mix years and overstate performance, so I split by time. And 2026 is a different "
              "population, so it is kept out of training and testing and reported separately.")
picture(s, "14_time_drift.png", MARGIN, 1.6, W - 2 * MARGIN, 3.3)
tile(s, MARGIN, 5.15, 3.95, 1.6, "7.8% → 1.3%", "relief rate, 2015 → 2025 (narrative complaints)", color=RED, fill=LIGHT_RED)
tile(s, MARGIN + 4.17, 5.15, 3.95, 1.6, "74%", "of 2025 narratives are about credit reporting")
tile(s, MARGIN + 8.34, 5.15, 3.95, 1.6, "4% · 6.7%", "2026: credit-reporting share · relief rate → reported as a separate slice")

# 7. EDA 3
s = new_slide("Exploratory analysis · 3", "The narrative carries signal, a quoted dollar amount most of all", 1.0,
              "The third finding is that the text itself carries signal. Complaints whose narrative quotes a dollar amount get "
              "relief 7.6 percent of the time, against 1.2 percent when no amount is quoted. That is the largest effect among "
              "the text-shape features, with a rank-biserial of 0.45. Relief narratives are also longer. And complaints whose "
              "exact text appears in another complaint, the template letters, almost never get relief: 0.01 percent against "
              "3.6 percent for unique narratives. These are all things a TF-IDF model can pick up, so there is reason to "
              "expect the narrative to help, and the question becomes how much beyond the form fields.")
picture(s, "13_text_length.png", MARGIN, 1.55, W - 2 * MARGIN, 3.65)
tile(s, MARGIN, 5.3, 3.95, 1.5, "7.6% vs 1.2%", "relief rate when the narrative quotes a $ amount vs not", color=RED, fill=LIGHT_RED)
tile(s, MARGIN + 4.17, 5.3, 3.95, 1.5, "0.45", "rank-biserial effect of $ mentions, the largest text-shape effect")
tile(s, MARGIN + 8.34, 5.3, 3.95, 1.5, "0.01% vs 3.6%", "relief rate for templated vs unique narratives")
caption(s, 6.85, "Notebook 01 (exploratory relief definition: monetary relief vs any other closure).")

# 8. Pre-processing
s = new_slide("Pre-processing", "Fitted on the past, tested on the future, with no leakage", 1.5,
              "This is the training-data design. The split is by complaint date: train on March 2015 to June 2024, validate on "
              "the second half of 2024, and test once on all of 2025. Template letters could leak across that boundary, so any "
              "validation or test narrative whose exact text appeared earlier is removed. Every transformer is fitted on "
              "training rows only, inside scikit-learn pipelines. Categorical fields get one-hot dummies, with rare levels "
              "lumped together, so 3,687 companies become 506 columns and new companies in 2025 are handled safely. The skewed "
              "count features are log-transformed and standardised for the linear models; I don't scale them for the trees, "
              "because tree splits don't depend on scale. Text becomes TF-IDF on words and word pairs. And for leakage: "
              "post-outcome fields are never loaded, the date isn't a feature, and for routing I exclude issue and "
              "sub-product, which are chosen together with the product.")
picture(s, "21_split_timeline.png", MARGIN, 1.5, W - 2 * MARGIN, 2.7)
c3w = 3.98
card(s, MARGIN, 4.3, c3w, 2.65, "Time split",
     ["Train 2015-03 → 2024-06 (404,004)", "Validation 2024 H2 (71,822)", "Test 2025 (205,922), used once",
      "Repeated text never crosses splits"], body_size=13)
card(s, MARGIN + 4.17, 4.3, c3w, 2.65, "Features (fit on train only)",
     ["One-hot, rare levels lumped: 3,687 companies → 506 columns", "log + StandardScaler for linear models only",
      "TF-IDF 1–2-grams, 100,000 terms"], body_size=13)
card(s, MARGIN + 8.34, 4.3, c3w, 2.65, "Leakage controls",
     ["Post-outcome fields never loaded", "No date feature", "Routing excludes issue and sub-fields (they give the product away)"],
     color=RED, fill=LIGHT_RED, body_size=13)

# 9. Models
s = new_slide("Models", "Five models per task: text plus form fields wins both", 1.25,
              "I compared five models per task, from trivial to strongest, all tuned on the 2024 validation half-year only. "
              "For routing, the majority class scores a macro-F1 of 0.079. The form fields alone, mostly the company, reach "
              "0.557. The narrative alone reaches 0.679, and narrative plus form fields is best at 0.733. LightGBM on selected "
              "TF-IDF features came close at 0.713 but didn't beat the regularised linear model, which is common with sparse "
              "text. For relief, the ranking is LightGBM on text and structured fields at an AP of 0.406, then the text plus "
              "structured logistic regression, then the structured-only models. The structured-only LightGBM reaches 0.386, "
              "which shows how much the form already explains. I treated class weighting as a setting to tune: balanced "
              "weights actually lowered routing macro-F1 in every model.")
text(s, MARGIN, 1.6, 6, 0.4, ["Routing (product) · validation macro-F1"], size=16, bold=True, color=BLUE)
table(s, MARGIN, 2.05, 5.95, [["Model", "Macro-F1"], ["TF-IDF + structured LogReg", "0.733"], ["LightGBM (text + structured)", "0.713"],
                              ["TF-IDF LogReg (text only)", "0.679"], ["Structured-only LogReg", "0.557"],
                              ["Majority class", "0.079"]], [4.45, 1.5])
text(s, MARGIN + 6.3, 1.6, 6, 0.4, ["Relief · validation average precision"], size=16, bold=True, color=RED)
table(s, MARGIN + 6.3, 2.05, 5.95, [["Model", "AP"], ["LightGBM (text + structured)", "0.406"], ["TF-IDF + structured LogReg", "0.397"],
                                    ["Structured-only LightGBM", "0.386"], ["Structured-only LogReg", "0.356"],
                                    ["Base rate (random ranking)", "0.031"]], [4.45, 1.5], header_fill=RED)
text(s, MARGIN, 4.85, W - 2 * MARGIN, 1.6,
     ["• Tuned on validation (2024 H2) only; the winner of each task is refitted on train + validation and scored once on 2025.",
      "• Class weighting was treated as a setting to tune: balanced weights lowered routing macro-F1 in every model.",
      "• LightGBM used χ²-selected TF-IDF (20,000 columns); for routing it was trained on a 150,000-row subsample."],
     size=15, spacing=6)

# 10. Routing results
s = new_slide("Results · routing (test set: 2025)", "Routing on 2025: macro-F1 0.70, against 0.56 with form fields only and 0.08 for the majority class", 1.25,
              "Now the test year, 2025, which the model never saw. Routing reaches a macro-F1 of 0.702 and accuracy of 0.90, "
              "against 0.558 for the form-fields-only model and 0.076 for always predicting credit reporting. So the narrative "
              "clearly helps routing. The left matrix is recall by true product, the right is precision by predicted product. "
              "Eight of the eleven products have precision and recall of at least 0.65. The biggest single error is debt "
              "collection being routed to credit reporting, 31 percent of debt-collection complaints. Collections appear on "
              "credit reports, and when I read the most confident cases, they are entirely credit-report disputes, so part of "
              "this is label noise. The weak classes are small and overlapping: debt or credit management, prepaid cards, and "
              "payday loans.")
picture(s, "30_routing_test_confusion_recall_precision.png", MARGIN, 1.6, W - 2 * MARGIN, 4.45)
text(s, MARGIN, 6.2, W - 2 * MARGIN, 0.7,
     [[("Accuracy 0.90 · ", {"bold": True}), ("8 of 11 products with precision and recall ≥ 0.65 · ", {}),
       ("largest error: ", {"bold": True}), ("31% of debt collection routed to credit reporting · weakest: debt/credit "
                                             "management (recall 0.10), prepaid, payday", {})]], size=14)

# 11. Routing confidence
s = new_slide("Results · routing", "The model's confidence is usable: 76% of complaints could be auto-routed at 96.5% accuracy", 0.75,
              "Because a routing team has to trust the model, I checked whether its confidence means anything. The left chart "
              "compares the top-class probability with actual accuracy: they track each other closely. That makes a simple "
              "policy possible. If we auto-route only complaints where the model is at least 90 percent confident, that covers "
              "76 percent of complaints with 96.5 percent accuracy. The remaining quarter, where accuracy is 69 percent, goes "
              "to a person. The right chart shows the whole trade-off, so a team can pick its own threshold.")
picture(s, "31_routing_confidence_and_automation.png", MARGIN, 1.6, W - 2 * MARGIN, 3.85)
tile(s, MARGIN, 5.55, 3.95, 1.3, "76.4%", "of complaints routed automatically at confidence ≥ 0.9")
tile(s, MARGIN + 4.17, 5.55, 3.95, 1.3, "96.5%", "accuracy of the auto-routed complaints")
tile(s, MARGIN + 8.34, 5.55, 3.95, 1.3, "68.8%", "accuracy of the rest → human triage queue", color=RED, fill=LIGHT_RED)

# 12. Relief results
s = new_slide("Results · relief (test set: 2025)", "Relief on 2025: the top 10% of the review queue holds 86% of all relief cases", 1.25,
              "For relief on 2025, the final LightGBM model reaches an average precision of 0.322. The base rate is only 2.2 "
              "percent, and the form-fields-only model reaches 0.296. The left chart is the precision-recall curve: the final "
              "model, in red, sits above the structured-only one, especially at the high-precision end. The right chart is "
              "the one a review team cares about. If they read complaints in score order, the top 10 percent of the queue "
              "already contains 85.9 percent of all relief cases, 2,574 of 2,997. That is a lift of 8.6 over reading at "
              "random. Precision in the top decile is 0.189, close to its ceiling of 0.22, since there are fewer relief "
              "cases than slots in the top decile.")
picture(s, "32_relief_test_pr_and_gains.png", MARGIN, 1.6, W - 2 * MARGIN, 3.95)
tile(s, MARGIN, 5.65, 3.95, 1.25, "AP 0.322", "vs 0.296 form fields only · 0.022 base rate", color=RED, fill=LIGHT_RED)
tile(s, MARGIN + 4.17, 5.65, 3.95, 1.25, "85.9%", "of relief cases in the top 10% (2,574 of 2,997)")
tile(s, MARGIN + 8.34, 5.65, 3.95, 1.25, "8.6×", "lift in the top decile over random review")

# 13. Narrative value
s = new_slide("Results · does the narrative help?", "The narrative's gain is real but small, and largest where the form fields can't help", 1.25,
              "Back to the central question: does the narrative add value for relief? A bootstrap over the test set gives an "
              "AP gain of 0.026 with a 95 percent interval from 0.013 to 0.038, and the gain is positive in every one of the "
              "thousand resamples. So it's real. But it's small in operational terms: top-decile precision only moves by about "
              "0.003. Where does it help? The left chart shows it's at the very top of the queue: 46 percent of the top 1 "
              "percent are relief cases, against 43 percent for structured-only. The right chart computes AP within each "
              "product, where the product can't help. In credit reporting the narrative lifts AP from 0.047 to 0.178, and "
              "similarly in debt collection. These are the products where relief is rare and the form fields can't find it, "
              "but the text can.")
picture(s, "25_relief_test_precision_at_k_and_by_product.png", MARGIN, 1.6, W - 2 * MARGIN, 3.85)
tile(s, MARGIN, 5.55, 3.95, 1.35, "+0.026 AP", "95% bootstrap CI [0.013, 0.038], positive in every resample", color=RED, fill=LIGHT_RED)
tile(s, MARGIN + 4.17, 5.55, 3.95, 1.35, "0.178 vs 0.047", "AP within credit reporting: with vs without the narrative")
tile(s, MARGIN + 8.34, 5.55, 3.95, 1.35, "46% vs 43%", "relief cases in the top 1% of the queue")

# 14. Errors
s = new_slide("Error analysis", "What the model gets wrong is mostly not visible in the text", 1.25,
              "What does the model get wrong? Three patterns. Mis-routes cluster where products genuinely overlap. The biggest "
              "is debt collection going to credit reporting, and the confident cases read like credit-report disputes, so "
              "part of that is label noise. Missed relief cases, 423 or 14 percent of them, fall outside the top decile. They "
              "are concentrated in low-relief products, they are shorter, and they quote a dollar amount far less often. "
              "Typically they are generic credit-report disputes where nothing in the text points to money. False alarms at "
              "the top of the queue are mostly fee and unrecognised-charge complaints at banks and card issuers. They look "
              "exactly like relief cases but were closed with an explanation, and many probably still deserve a look. Finally, "
              "the model partly learns which companies tend to pay. It predicts the company's recorded response, not whether "
              "the consumer was harmed.")
cw3 = 3.98
card(s, MARGIN, 1.75, cw3, 4.0, "Mis-routes",
     ["Debt collection → credit reporting: 5,476 complaints (31%).",
      "The most confident 'errors' are pure credit-report disputes, so this is partly label noise.",
      "Small overlapping classes stay weak."], body_size=16)
card(s, MARGIN + 4.17, 1.75, cw3, 4.0, "Missed relief (423, 14%)",
     ["Concentrated in low-relief products.", "Shorter: median 137 vs 204 words.", "Quote a $ amount less often: 32% vs 68%.",
      "Typically a generic credit-report dispute; nothing in the text points to money."], color=RED, fill=LIGHT_RED, body_size=16)
card(s, MARGIN + 8.34, 1.75, cw3, 4.0, "False alarms",
     ["Fee and unrecognised-charge complaints at banks and card issuers.",
      "Checking/savings: 5,515 of 6,419 top-decile complaints were closed with an explanation.",
      "They look like relief cases; many still merit review."], body_size=16)
text(s, MARGIN, 5.95, W - 2 * MARGIN, 0.9,
     [[("The model partly learns which companies pay ", {"bold": True}),
       ("(Equifax is the strongest negative signal). It predicts the company's recorded response, not consumer harm.", {})]],
     size=15)

# 15. Recommendations, limitations, next steps
s = new_slide("Recommendations", "Recommendations, limitations and next steps", 1.5,
              "Three recommendations. One: automate routing for confident predictions. A 0.9 threshold covers about three "
              "quarters of complaints at about 96 percent accuracy, and the rest, plus the three weak classes, go to a triage "
              "queue. Two: use the relief score to order the review queue, not to decide outcomes. Reviewing the top 10 "
              "percent finds 86 percent of relief cases. Three: recalibrate the probabilities on recent months before showing "
              "them as percentages, because they run a bit high, 2.9 percent predicted against 2.2 percent actual. On "
              "limitations, I want to be direct. The narrative adds only a little to relief prediction overall. Issue routing "
              "is weak at 0.31 macro-F1. The labels are company-recorded, the narratives are opt-in, and the archive is "
              "frozen. On the changed 2026 population, routing drops to 0.65 and relief lift falls to 4.7, so the models must "
              "be re-validated before use. Next I'd harmonise issue labels, test sentence embeddings, and recalibrate.")
card(s, MARGIN, 1.7, 5.95, 5.2, "Recommendations",
     [[("1  Auto-route confident predictions. ", {"bold": True}), ("Threshold 0.9: about three quarters of volume at about 96% "
                                                                  "accuracy; the rest and the 3 weak classes go to triage.", {})],
      [("2  Order the review queue by relief score, ", {"bold": True}), ("don't automate outcomes: the top 10% holds 86% of "
                                                                        "relief cases.", {})],
      [("3  Recalibrate on recent months ", {"bold": True}), ("before showing scores as percentages (2.9% predicted vs 2.2% "
                                                             "actual).", {})]], body_size=18)
card(s, MARGIN + 6.3, 1.7, 5.95, 5.2, "Limitations → next steps",
     [[("Narrative adds little to relief overall ", {"bold": True}), ("→ test sentence embeddings on the same split.", {})],
      [("Issue routing weak (macro-F1 0.31) ", {"bold": True}), ("→ harmonise the issue taxonomy.", {})],
      [("Company-recorded labels; opt-in narratives; frozen archive ", {"bold": True}), ("→ results describe that group only.", {})],
      [("2026 shift: routing 0.65, relief lift 4.7 ", {"bold": True}), ("→ re-validate before any use; check fairness by "
                                                                       "company and state.", {})]],
     color=RED, fill=LIGHT_RED, body_size=18)

# 16. Summary
s = new_slide("Summary", "Three takeaways", 0.75,
              "To sum up in three points. Routing works and is ready for confident cases: a macro-F1 of 0.70 on an unseen "
              "year, with three quarters of complaints routable automatically at 96.5 percent accuracy. Relief ranking works: "
              "the top 10 percent of the queue holds 86 percent of relief cases, but most of that comes from the product and "
              "the company. And the narrative helps, significantly but modestly, and most where the form fields are "
              "uninformative. Everything is in the repo: three notebooks, the report and the metrics file. Thank you, I'm "
              "happy to take questions.")
items = [("1", "Routing is ready for confident cases", "macro-F1 0.70 on an unseen year; 76% auto-routable at 96.5% accuracy", BLUE, LIGHT),
         ("2", "Relief ranking works, driven mostly by the form fields", "the top 10% of the queue holds 86% of relief cases", RED, LIGHT_RED),
         ("3", "The narrative helps significantly but modestly", "most where the form fields are uninformative (credit reporting, debt collection)", BLUE, LIGHT)]
for k, (n, head, sub, col, fill) in enumerate(items):
    top = 1.75 + k * 1.45
    box(s, MARGIN, top, W - 2 * MARGIN, 1.25, fill=fill)
    text(s, MARGIN + 0.25, top + 0.1, 0.8, 1.05, [n], size=40, bold=True, color=col, anchor=MSO_ANCHOR.MIDDLE)
    text(s, MARGIN + 1.1, top + 0.12, W - 2 * MARGIN - 1.4, 0.5, [head], size=21, bold=True, spacing=0)
    text(s, MARGIN + 1.1, top + 0.64, W - 2 * MARGIN - 1.4, 0.5, [sub], size=15, color=GREY, spacing=0)
text(s, MARGIN, 6.2, W - 2 * MARGIN, 0.6,
     [[("Questions?  ", {"bold": True, "color": BLUE, "size": 22}),
       ("github.com/jacob25paul/consumer-complaints-capstone · reports/project_report.pdf", {"size": 15, "color": GREY})]])

prs.save(OUT)

# ----------------------------------------------------------------------------------------------------- notes.md
total = sum(m for _, m, _ in SLIDES)
lines = ["# Speaker notes and rehearsal sheet", "",
         "Deck: `slides/Capstone_Final_Slides.pptx` (PDF: `slides/Capstone_Final_Slides.pdf`). The same notes are in the "
         "PowerPoint notes pane. Generated by `slides/build_slides.py`; every number comes from `reports/model_metrics.*` or "
         "the executed notebooks.", "",
         "## Rehearsal sheet (one page)", "",
         f"Target: **{total:.2f} minutes** of talk (notes read at about 140 words per minute, plus time to point at each chart), "
         "then 10 minutes of questions in a 30-minute call. Rehearse with a timer; "
         "if you are behind at a checkpoint, shorten the slide after it, not the results slides.", "",
         "| # | Slide | Min | Ends at |", "|---|---|---|---|"]
t = 0.0
for i, (title, mins, _) in enumerate(SLIDES, 1):
    t += mins
    mm, ss = int(t), int(round((t - int(t)) * 60))
    lines.append(f"| {i} | {title} | {mins:g} | {mm}:{ss:02d} |")
cum = np.cumsum([m for _, m, _ in SLIDES])
fmt = lambda x: f"{int(x)}:{int(round((x - int(x)) * 60)):02d}"
lines += ["",
          "**Checkpoints:** " + " · ".join(f"end of slide {k} ≈ {fmt(cum[k - 1])}" for k in (4, 9, 13)) + f" · finish ≈ {fmt(cum[-1])}.", "",
          "**If running long, cut:** slide 7 (fold its numbers into slide 5), then slide 11 (state its one number on slide 10).", "",
          "**Three sentences to land no matter what:** routing macro-F1 0.70 on an unseen year; the top 10% of the queue holds "
          "86% of relief cases; the narrative's gain is real (CI [0.013, 0.038]) but small.", "",
          "## Speaker notes", ""]
for i, (title, mins, notes) in enumerate(SLIDES, 1):
    lines += [f"### {i}. {title} ({mins:g} min)", "", notes, ""]
NOTES_MD.write_text("\n".join(lines))
print(f"Wrote {OUT.relative_to(ROOT)} ({len(prs.slides)} slides, {total:.1f} min) and {NOTES_MD.relative_to(ROOT)}")
