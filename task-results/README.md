# Task Results Directory

This directory contains experimental results from benchmarking tasks conducted on the dataset.

## Overview

The experiments evaluate large language models (LLMs) across three IR-oriented tasks that correspond to distinct stages of the personalized IR pipeline:

1. **Task 1: User Representation Inference** - Converting free-form narratives into structured questionnaire responses (pre-retrieval modeling)
2. **Task 2: Item Relevance Estimation** - Predicting user-specific relevance scores using contextual information (ranking stage)
3. **Task 3: Personalized Text Generation** - Generating user-adapted reviews and explanations (post-retrieval interaction)

## Directory Structure

```
task-results/
├── tables/
│   ├── tabRQ1.csv
│   └── tab_section_metrics_.csv
└── plots/
    ├── plots_tab1/
    │   ├── barplot_RQ1.png
    │   └── scatterplot_RQ1.png
    └── scatterplot_tab1/
        └── scatterplot_RQ1_general.png
```

## Files Description

### Tables

#### `tabRQ1.csv`
**Task 1: User Representation Inference Results**

This file contains comprehensive metrics evaluating how well large language models can infer structured questionnaire responses from free-form narrative inputs.

**Columns:**
- `Questionnaire` - The target questionnaire type
- `Model` - The LLM variant used (e.g., deepseek-r1_70b, qwen2.5_32b, llama3.1_8b)
- `User Coverage (%)` - Percentage of users processed
- `Model valid answer (%)` - answers unknown and known (non-unknown)
- `Accuracy Overall (%)` - Exact match with ground-truth responses
- `Accuracy Unknown (%)` - Performance on "unknown" responses matched to ground truth
- `Accuracy Unknown Relative (%)` - Relative accuracy for unknown predictions
- `Unknown representation prediction (%)` - Rate of predicting unknown values
- `Unknown representation (%)` - Ground-truth unknown rate
- `Accuracy known (%)` - Accuracy on known (non-unknown) responses matched ground truth divided by all predicted answers
- `Accuracy Known Relative (%)` - Relative accuracy for known predictions
- `LLM known representation` - Proportion of known values predicted by LLM
- `Human known representation (%)` - Proportion of known values in ground truth
- `MAE` - Mean Absolute Error
- `MSE` - Mean Squared Error
- `RMSE` - Root Mean Squared Error

#### `tab_section_metrics_.csv`
**Task 1: Category-Level Performance Breakdown**

This file provides granular analysis of model performance across different food choice motivation categories within the FCQ questionnaire.

**Columns:**
- `Questionnaire`
- `Model` - The LLM variant evaluated
- `Category` - Food choice motivation dimension
- `Category MAE` - Mean Absolute Error for this specific category
- `LLM known representation Categ` - Percentage of known representations predicted by the LLM for this category

**Categories Analyzed:**
1. **Convenience** - Ease of food preparation and availability
2. **Ethical Concern** - Environmental and animal welfare considerations
3. **Familiarity** - Preference for known foods
4. **Health** - Nutritional value and health benefits
5. **Mood** - Emotional and psychological effects
6. **Natural Content** - Preference for natural/unprocessed foods
7. **Price** - Cost considerations
8. **Sensory Appeal** - Taste, smell, and appearance
9. **Weight Control** - Dietary management considerations

### Plots

This folder contains the plots from the paper.

## Evaluated Models

All experiments were conducted using open-source large language models:

- **DeepSeek-R1-70B** and **DeepSeek-R1-32B** - Reasoning-focused models
- **Qwen-3-32B** and **Qwen-2.5-32B** - Alibaba's Qwen model family
- **LLaMA-3.1-8B** - Meta's LLaMA model
