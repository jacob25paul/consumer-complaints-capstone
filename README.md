# Routing Consumer Financial Complaints and Predicting Which Ones End in Relief

Springboard Data Science Career Track, Capstone Three

**Status:** proposal stage. Notebooks, results and the final report will be added as the project progresses.

## Problem

Banks, lenders and credit bureaus receive large numbers of consumer complaints. Each one has to be sent to the right team, and someone has to decide which to review first. This project uses the text of a complaint to predict:

1. its product and issue category, so that it can be routed, and
2. whether the company closed it with monetary relief rather than with an explanation, so that a compliance team can review the complaints most likely to involve real financial harm first.

It also tests whether the narrative adds information beyond what the complaint form already records (product, company, state, how it was submitted).

The full proposal is in [`proposal/consumer-complaints-capstone-Proposal.pdf`](proposal/consumer-complaints-capstone-Proposal.pdf).

## Data

CFPB [Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/), as the [Hugging Face snapshot](https://huggingface.co/datasets/consumer-finance-complaints): 3,079,747 complaints. Narratives are present only for consumers who opted in to publication, so the text-based work uses that subset.

The CFPB stopped publishing complaint narratives on August 14, 2026. The snapshot is a fixed historical extract, so results describe past complaints and cannot be refreshed with new narratives.

The data is not included in this repository. Download the snapshot and place it in `data/`.

## Planned approach

1. Wrangling and exploratory analysis: count narratives, clean the text, measure relief rates by product, company and year.
2. Baselines: majority class, and models on the structured fields alone.
3. Text models: TF-IDF with logistic regression, then sentence embeddings with a linear or boosted model.
4. Evaluation on a later time period than the training data: macro F1 for routing; average precision and precision in the top 10 percent for relief; error analysis of relief cases the model misses.
5. Output: final report, slides and notebooks in this repository.

## Repository structure

```
consumer-complaints-capstone/
├── proposal/    Project proposal (PDF)
├── data/        Place the downloaded snapshot here (not tracked)
├── notebooks/   Analysis notebooks (to be added)
├── reports/     Final report and figures (to be added)
└── README.md
```

## Author

**Jacob Paul**: [LinkedIn](https://www.linkedin.com/in/jacob25paul) · [GitHub](https://github.com/jacob25paul)
