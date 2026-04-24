# FoodPersona: A Data Collection Framework for Personalized Information Retrieval in Food with Contextual User Signals

## Overview

This repository contains the supplementary material for Food Persona. The project includes:

- A data collection web application for gathering user food narratives and preferences
- The Food Persona dataset: Structured datasets linking free-form biographies to questionnaire responses and recipe ratings
- Benchmark tasks evaluating LLMs on user representation inference, item relevance estimation, and personalized text generation
- Experimental results from multiple open-source LLM evaluations

Each module contains its own README.md file with more details.

## Repository Structure

### [`webapp/`](./webapp)

Interactive web application for conducting the food preferences study.

### [`data/`](./data)

Collected study data in structured CSV format.

### [`task-results/`](./task-results)

Experimental results from benchmarking LLMs across three information retrieval tasks:
1. **User Representation Inference** - Converting narratives to structured responses
2. **Item Relevance Estimation** - Predicting user-specific relevance scores
3. **Personalized Text Generation** - Generating user-adapted reviews

Contains performance metrics, category-level breakdowns, and visualization plots.

### [`benchmarking/`](./benchmarking)

Code for executing the benchmark tasks.