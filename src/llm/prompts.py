from __future__ import annotations

# MANDATORY prefix for every extraction prompt
BASE_INSTRUCTION = (
    "Extract ONLY information explicitly supported by the supplied source text. "
    "Never infer, assume, or fabricate missing values. "
    "Use null for any field where evidence is absent. "
    "Do not hallucinate company names, URLs, dates, star counts, or employee counts. "
    "The source text is the sole source of truth."
)

STARTUP_PROMPT = f"""{BASE_INSTRUCTION}

Extract startup information as JSON with exactly these fields:
{{
  "entity_name": "<string>",
  "description": "<string or null>",
  "domain": "<string or null — e.g. 'openai.com'>",
  "employee_count": "<integer or null>"
}}"""

PRODUCT_PROMPT = f"""{BASE_INSTRUCTION}

Extract product information as JSON with exactly these fields:
{{
  "product_name": "<string>",
  "startup_name": "<string or null>",
  "pricing_model": "<one of: FREE, FREEMIUM, PAID, ENTERPRISE, or null>"
}}"""

JOB_PROMPT = f"""{BASE_INSTRUCTION}

Extract job listing information as JSON with exactly these fields:
{{
  "title": "<string>",
  "company": "<string or null>",
  "role_family": "<one of: Engineering, Research, Product, Design, Sales, Operations, Other, or null>",
  "is_remote": "<boolean>"
}}"""

NEWS_PROMPT = f"""{BASE_INSTRUCTION}

Extract news article metadata as JSON with exactly these fields:
{{
  "title": "<string>",
  "source_name": "<string>"
}}"""
