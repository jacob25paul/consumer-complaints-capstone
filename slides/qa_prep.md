# Q&A preparation: the 10 hardest questions

Honest answers grounded in the executed notebooks and `reports/model_metrics.*`. Lead with the short answer, then give the evidence.

---

### 1. "How do you know there's no leakage?"
**Short answer:** leakage was controlled at three levels, and the results behave like a model without it. Test scores are *lower* than validation scores, not suspiciously high.

- **Columns.** Post-outcome fields (`company_public_response`, `timely_response`, `date_sent_to_company`, `days_to_company`) are not even loaded in notebook 02. `company_response` is used only to build the label. The date is not a feature.
- **Routing.** `issue`, `sub_issue` and `sub_product` are excluded. They are chosen together with the product (Cramér's V with product 0.72–0.87), so they would give it away. For relief they are legitimate inputs, because they are known when the complaint is filed.
- **Rows and time.**
  - The split is by complaint date.
  - Every encoder, scaler and TF-IDF vocabulary is fitted on training rows only, inside a `Pipeline`.
  - Any validation or test narrative whose exact text appeared in an earlier split is removed (18,639 and 33,798 rows), so template letters can't be memorised.
- **Selection.** Models were chosen on validation; the test set was scored once. Validation → test fell from 0.7333 → 0.7021 (routing) and 0.4057 → 0.3220 (relief AP), as you'd expect under drift.

### 2. "Relief is only about 2% positive. How did you handle the imbalance?"
**Short answer:** with the right metrics first, and class weighting treated as a tuned setting rather than a default.

- **Metrics.** I use AP, precision in the top 10% and lift, all from the proposal. Accuracy would be about 98% for a model that never predicts relief.
- **Class weighting.** `class_weight="balanced"` / `is_unbalance` were tried on validation:
  - weighting helped the relief logistic regression (AP 0.397 vs 0.373);
  - it made no real difference to LightGBM (0.402 vs 0.406);
  - it *lowered* routing macro-F1 in every model.
- **No resampling.** I didn't use SMOTE or undersampling, because they distort probabilities and the ranking is what matters. The final relief model's probabilities are reasonably calibrated: mean predicted 2.9% vs 2.2% actual, ECE 0.0071, Brier skill 0.18.

### 3. "Why a time-based split instead of random cross-validation?"
**Short answer:** because the target and the inputs drift, and the model would be used on *future* complaints.

- The relief rate falls from 7.8% (2015) to 1.3% (2025), and credit reporting grows to 74% of 2025 narratives. A random split would let the model learn from future months and overstate performance.
- The proposal explicitly asks for evaluation "on complaints from a later period".
- The cost: one test year instead of k folds. The bootstrap CI on the test set (section 3.4 of notebook 03) quantifies the uncertainty instead.

### 4. "Why macro-F1 and average precision? Why not accuracy or ROC-AUC?"
**Short answer:** each answers the business question.

- **Macro-F1** weights the 538-complaint *debt or credit management* class the same as the 146,809-complaint credit-reporting class. Accuracy (0.90) is dominated by credit reporting.
- **AP and top-10% precision** describe a review queue: *of the complaints we read first, how many are relief cases?*
- **ROC-AUC is about 0.96 for every relief model**, including structured-only (0.9556 vs 0.9588), because most negatives are easy. It can't separate the models; AP can.

### 5. "The narrative only adds 0.026 AP for relief. Is the NLP worth it?"
**Short answer:** for routing, clearly yes. For relief, it is statistically real but operationally modest, and I say so.

- **Routing:** the narrative lifts macro-F1 from 0.558 (form fields only) to 0.702.
- **Relief:**
  - The gain is +0.0259 AP, 95% bootstrap CI [0.0131, 0.0380], positive in all 1,000 resamples.
  - The top-10% precision gain is only +0.0034.
  - The value is concentrated inside low-relief products, where the form can't help: credit reporting AP 0.178 vs 0.047, debt collection 0.144 vs 0.047. It also shows at the very top of the queue: 46% vs 43% of the top 1% are relief cases.
- **The honest framing:** product, company and issue explain most of relief. The proposal anticipated this and asked for it to be reported.

### 6. "Why not BERT or sentence embeddings? Would deep learning do better?"
**Short answer:** possibly for routing, but probably not much for relief, and it was out of the compute budget.

- Sentence embeddings were the proposal's "if time allows" item. They need torch and a model download, and inference on about 760k narratives (758,548) on a MacBook Air is slow.
- For routing, the errors are mostly genuinely overlapping products and label noise. The most confident "mis-routes" are credit-report disputes filed as debt collection, which no model can fix.
- For relief, the error analysis shows missed cases are short, generic disputes with no textual signal of money. A better text encoder can't find what isn't in the text.
- It's the first experiment I'd run next, on the same split, so the comparison is fair.

### 7. "What would change with more data, or the full archive instead of a 20% sample?"
**Short answer:** little for the headline numbers, more for the small classes.

- The 20% sample is uniform, so rates are unbiased, and the large classes already have hundreds of thousands of examples.
- Gains would show up in the small classes (debt or credit management: 538 test complaints) and in the rare relief cases inside low-relief products (90 credit-reporting relief cases in test).
- *More recent* data matters more than *more* data, because of drift, but the CFPB stopped publishing narratives in 2026, so the archive is frozen.

### 8. "The 2026 results are much worse. Doesn't that undermine the model?"
**Short answer:** it shows the model's limits honestly. 2026 is a different population, not just a later year.

- Narrative opt-in collapsed from 22.3% (2025) to 2.5% (2026), and credit reporting fell from 74% to 4% of narratives.
- Routing macro-F1 drops to 0.6486, and the relief lift falls to 4.73, although AP is 0.3598 because the base rate is much higher (7.84%).
- 2026 was kept out of training and testing for exactly this reason. My recommendation is to re-validate before any use on a differently selected population.

### 9. "Isn't the relief model just learning which companies pay?"
**Short answer:** partly, yes, and that is a finding, not a bug.

- Company identity has the largest coefficients (Equifax is the strongest negative), and Cramér's V with relief is 0.33 for company.
- The label is the company's *recorded* response, not verified consumer harm. The proposal lists this as a constraint.
- That is why the model is recommended for *ordering a review queue*, not deciding outcomes, and why a fairness and stability check by company and state is a next step.

### 10. "Your test-set relief AP (0.322) is well below validation (0.406). Is the model overfit?"
**Short answer:** no. The drop tracks the falling base rate and drift.

- The base rate falls from 3.22% in validation to 2.20% in test, and AP scales with prevalence. The test lift in the top decile (8.59) is close to the validation lift (8.37).
- The structured-only reference drops similarly (validation 0.3856 → test 0.2962), so it isn't specific to the text model.
- The models were refitted on train + validation before testing, so the test year is the first truly unseen period.

---

**Back-pocket numbers:**
- **Data:** 17,533,918 complaints; 758,548 usable narratives in the 20% sample; test = 205,922 routing and 136,440 relief complaints (2,997 relief cases).
- **Routing:** macro-F1 0.702; 76.4% of complaints auto-routable at 96.5% accuracy.
- **Relief:** AP 0.322; 85.9% of relief cases in the top 10%.
