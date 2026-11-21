# Routing Consumer Financial Complaints and Predicting Which Ones End in Relief

Springboard Data Science Career Track, Capstone Three

**Status:** data wrangling and EDA complete ([`notebooks/01_data_wrangling_and_eda.ipynb`](notebooks/01_data_wrangling_and_eda.ipynb)). Modelling notebooks and the final report will follow.

## Problem

Banks, lenders and credit bureaus receive large numbers of consumer complaints. Each one has to be sent to the right team, and someone has to decide which to review first. This project uses the text of a complaint to predict:

1. its product and issue category, so that it can be routed, and
2. whether the company closed it with monetary relief rather than with an explanation, so that a compliance team can review the complaints most likely to involve real financial harm first.

It also tests whether the narrative adds information beyond what the complaint form already records (product, company, state, how it was submitted).

The full proposal is in [`proposal/consumer-complaints-capstone-Proposal.pdf`](proposal/consumer-complaints-capstone-Proposal.pdf).

## Data

CFPB [Consumer Complaint Database Narratives Archive](https://www.consumerfinance.gov/foia-requests/foia-electronic-reading-room/cfpb-consumer-complaint-database-narratives-archive/): 21 CSV exports (1.43 GB zipped, about 9 GB unzipped) with **17,533,918 complaints** received from December 2011 to August 2026. **3,851,415** of them (22%) include a consumer narrative. Narratives are present only for consumers who opted in to publication, so the text-based work uses that subset. Narrative publication began in March 2015 and nearly stopped in 2026.

The CFPB stopped publishing complaint narratives on August 14, 2026. The archive is a fixed historical extract, so results describe past complaints and cannot be refreshed with new narratives.

The raw data is not included in this repository. Download all 21 `CCDB_Export_*.zip` files from the archive page and unzip them into `data/raw/`. The notebook analyses a uniform random 20% of rows (`SAMPLE_FRAC = 0.20`) so that it runs on a 16 GB laptop. A 5,000-row sample of cleaned narrative complaints is committed in [`data/sample/`](data/sample/).

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
├── data/
│   ├── raw/        The 21 CFPB archive exports (not tracked)
│   ├── processed/  Cleaned data written by the notebook (not tracked)
│   └── sample/     5,000-row cleaned sample (tracked)
├── notebooks/   01_data_wrangling_and_eda.ipynb
├── reports/     figures/ from the EDA; final report to be added
└── README.md
```

## Author

**Jacob Paul**: [LinkedIn](https://www.linkedin.com/in/jacob25paul) · [GitHub](https://github.com/jacob25paul)
