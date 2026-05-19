Data pipeline and analysis code for:

**Morality, Justificatory Gaps, and AI Governance: Multilingual NLP for Classifying Ethical Concerns, Justificatory Logics, and Governance Arrangements in Swiss Parliamentary Debate, 2000–2025**

Schwarzenbach, Eldably & Alhineidi

---

## Overview

This repository contains code for retrieving, segmenting, annotating, and classifying Swiss parliamentary speeches on AI-related topics between 2000 and 2025.

The project develops multilingual NLP classifiers for identifying:

- AI-related parliamentary speech
- ethical concerns
- justificatory logics
- governance arrangements

The broader aim is to measure **justificatory gaps**: mismatches between the ethical concerns raised, the justificatory logic used to address them, and the governance responses proposed.

By linking these patterns to parliamentary affairs, vote shares, and proposal adoption, the project examines when AI ethics becomes institutionally consequential and when it remains primarily symbolic.

---

## Data

Speeches were retrieved from official Swiss parliamentary records using the Swiss Parliament Web Services / OData interface.

AI-related speeches were identified through multilingual keyword filtering in:

- German
- French
- Italian

Each speech is segmented into argumentative units and linked to affair-level voting records.

| Property | Value |
|---|---:|
| Period | 2000–2025 |
| Languages | German, French, Italian |
| Parliamentary interventions | 394 |
| Speech segments | 2,758 |

> Note: Raw parliamentary data may be subject to source-specific access and reuse conditions. See the data documentation for details.

---

## Pipeline

| Step | Description |
|---|---|
| Collect | Retrieve official parliamentary records via the Swiss Parliament OData API |
| Filter | Identify AI-related speeches using multilingual keyword queries |
| Segment | Segment speeches into argumentative units using LLM-assisted preprocessing and human correction |
| Annotate | Code argumentative units according to the project codebook |
| Classify | Train and evaluate SVM, transformer-based, and LLM-assisted classifiers |
| Analyse | Aggregate segment-level predictions to speeches, interventions, parliamentary affairs, and voting outcomes |

---

## Classification tasks

The project evaluates classifier performance for four task families.

| Classifier | Task | F1 | Cohen's κ |
|---|---|---:|---:|
| AI relevance | Is the segment about AI or algorithmic systems? | 0.88 | 0.76 |
| Ethical concerns | Rights, safety, democracy, discrimination, accountability, and related concerns | TBD | TBD |
| Justificatory logics | Civic, market, industrial, domestic, and related justification types | 0.70–0.75 | 0.39–0.50 |
| Governance arrangements | Oversight, standards, legal protection, transparency, and related arrangements | TBD | TBD |

Pilot inter-annotator agreement for AI relevance, based on 50 segments:

| Measure | Value |
|---|---:|
| Cohen's κ | 0.874 |

---

## Preliminary findings

Current analyses suggest that:

- AI-related parliamentary debate has grown sharply since 2017.
- Approximately one third of AI-related segments raise ethical concerns.
- Ethical concerns appear less frequently when market-based justificatory logics dominate.
- This pattern may indicate systematic justificatory gaps in AI governance debates.

These findings are preliminary and will be updated as coding and model evaluation progress.

---
## Working paper
Schwarzenbach, A., Eldably, A., & Alhineidi, A. (2025). Morality, Justificatory Gaps, and AI Governance: Multilingual NLP for Classifying Ethical Concerns, Justificatory Logics, and Governance Arrangements in Swiss Parliamentary Debate, 2000–2025. Working paper, Institute of Penal Law and Criminology & Data Science Lab, University of Bern.



