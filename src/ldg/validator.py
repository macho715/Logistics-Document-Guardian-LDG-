"""Validate OCR JSON output against LDG rules."""

import re
from typing import Dict

from .rules import TOP10_RULES


def validate(data: Dict[str, str]) -> Dict[str, bool]:
    """Return dict mapping field -> bool indicating rule pass/fail."""
    result = {}
    for field, pattern in TOP10_RULES.items():
        value = data.get(field, "")
        result[field] = bool(re.match(pattern, value))
    return result
