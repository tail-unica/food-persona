# Food Preferences Study - Data Documentation

This directory contains the data we collected.

## Overview

The study collects data about food preferences through multiple instruments:
1. **Biography/Context** - Personal food story and relationship with food
2. **Food Choice Questionnaire (FCQ)** - Factors influencing food choices
3. **Nutritionist Questionnaire** - Demographics, lifestyle, and dietary habits
4. **Recipe Ratings** - Ratings and reviews of various recipes

All files use `user_id` as the primary identifier.

## Data Files

### context_submissions.csv

**Purpose:** Contains user-written biographies about their relationship with food.
**Columns:**
- `user_id` (string) - Unique identifier for each participant
- `context_text` (text) - Free-text biography written by the user describing their food journey, preferences, dietary restrictions, and background
- `char_count` (integer) - Number of characters in the context text
- `word_count` (integer) - Number of words in the context text

---

### FCQ_gt_structured.csv

**Purpose:** Food Choice Questionnaire (FCQ) responses in structured long format - one row per question per user.

**Columns:**
- `user_id` (string) - Unique participant identifier
- `category` (string) - Category of the food choice factor
- `questions` (string) - Question text (lowercase)
- `score` (integer) - Importance rating (1-4 scale)

**Score Scale:**
- `1` = Not important at all
- `2` = Slightly important
- `3` = Very important
- `4` = Extremely important

---

### JC_gt_structured.csv

**Purpose:** Nutritionist Questionnaire responses in structured long format - one row per question per user.

**Columns:**
- `user_id` (string) - Unique participant identifier
- `category` (string) - Category of information collected
- `questions` (string) - Question identifier or field name
- `answer` (string/numeric) - User's answer to the question

---

### recipe_ratings.csv

**Purpose:** User ratings and reviews of recipes shown during the study.

**Columns:**
- `user_id` (string) - Unique participant identifier
- `recipe_id` (integer) - Unique identifier for the recipe
- `recipe_name` (string) - Name/title of the recipe
- `score` (integer) - Rating score (1-5 stars)
- `review` (text) - Written review explaining the rating
- `review_length` (integer) - Number of characters in the review

---