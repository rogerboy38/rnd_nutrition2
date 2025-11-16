# Nutrition Utils

This single doctype stores all utility configurations and provides common functions for the R&D Nutrition module.

## Features

- Centralized configuration for nutrition calculations
- Daily recommended values storage
- API connection settings
- Utility methods for:
  - Normalizing nutrition values
  - Calculating percentages
  - API integration

## Usage

```python
from rnd_nutrition.utils import get_daily_values

daily_values = get_daily_values()
