import os
import json
import re
from openai import OpenAI


# ============================================================
# OPENROUTER CLIENT
# ============================================================

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)


# ============================================================
# RESPONSE HELPERS
# ============================================================

ALLOWED_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def _clean_json_response(content):
    """
    Convert the model response into a Python dictionary.

    The model is instructed to return JSON, but some providers may
    still wrap it in markdown or add a short sentence before/after it.
    This helper keeps the dashboard stable in those cases.
    """
    if not content:
        raise ValueError("Empty response received from the AI service.")

    text = str(content).strip()

    # Remove common markdown fences.
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text).strip()

    # First attempt: the complete response is JSON.
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        # Second attempt: extract the outermost JSON object.
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError("The AI response did not contain a valid JSON object.")

        parsed = json.loads(text[start:end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("The AI response was not a JSON object.")

    return parsed


def _normalise_severity(value):
    """
    Keep severity values consistent with the dashboard.
    """
    if value is None:
        return "UNKNOWN"

    severity = str(value).strip().upper()

    if severity in ALLOWED_SEVERITIES:
        return severity

    # Handle responses such as "HIGH RISK" or "Severity: HIGH".
    for allowed in ALLOWED_SEVERITIES:
        if allowed in severity:
            return allowed

    return "UNKNOWN"


def _text_value(value, fallback):
    """
    Ensure expected text fields are returned as strings.
    """
    if value is None:
        return fallback

    text = str(value).strip()
    return text if text else fallback


# ============================================================
# AI EXCEPTION EXPLAINER
# ============================================================

def explain_exception(exception_data):

    """
    Analyse one reconciliation exception.

    The function intentionally keeps the same name and return fields
    expected by the dashboard so the existing UI does not need to change.
    """

    prompt = f"""
You are a finance operations analyst reviewing a payment reconciliation exception.

Your job is to explain the transaction clearly for a human finance team.
Do not sound like a chatbot and do not use generic filler such as
"after careful analysis" or "this indicates a potential issue".

TRANSACTION DETAILS
Payment ID: {exception_data.get("payment_id")}
Merchant ID: {exception_data.get("merchant_id")}
Payment Amount: ₹{exception_data.get("payment_amount")}
Settled Amount: ₹{exception_data.get("settled_amount")}
Difference: ₹{exception_data.get("difference")}
Settlement Count: {exception_data.get("settlement_count")}
Exception Type: {exception_data.get("exception_type")}
Confidence Score: {exception_data.get("confidence_score")}%

Return ONLY one valid JSON object using exactly these fields:

{{
    "severity": "LOW | MEDIUM | HIGH | CRITICAL",
    "explanation": "A concise explanation of what the transaction data shows.",
    "financial_impact": "The financial or operational impact supported by the supplied data.",
    "recommended_action": "A practical next step a finance operations analyst should take.",
    "prevention": "A practical control or process improvement relevant to this exception."
}}

Rules:
- Use only facts present in the transaction details.
- Do not invent gateway responses, customer behaviour, fraud, root causes,
  dates, policies, or amounts that are not provided.
- Do not claim that money was lost unless the supplied data proves it.
- If the exact root cause cannot be established, say that it requires verification.
- The difference amount may be described, but do not invent additional financial exposure.
- Severity must be exactly LOW, MEDIUM, HIGH, or CRITICAL.
- Base severity on the exception type, difference, settlement state, and supplied confidence.
- Keep each text field concise and useful to a finance operations team.
- Write in plain professional language.
- Do not mention that you are an AI.
"""


    try:

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a finance operations analyst. "
                        "Return only valid JSON. "
                        "Use evidence from the supplied data and avoid unsupported assumptions."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = response.choices[0].message.content
        parsed_result = _clean_json_response(result)

        return {
            "severity": _normalise_severity(
                parsed_result.get("severity")
            ),
            "explanation": _text_value(
                parsed_result.get("explanation"),
                "No explanation was returned."
            ),
            "financial_impact": _text_value(
                parsed_result.get("financial_impact"),
                "Financial impact could not be determined from the supplied data."
            ),
            "recommended_action": _text_value(
                parsed_result.get("recommended_action"),
                "Manual finance operations review is recommended."
            ),
            "prevention": _text_value(
                parsed_result.get("prevention"),
                "Review the reconciliation control related to this exception."
            )
        }


    except Exception as e:

        return {
            "severity": "UNKNOWN",
            "explanation": (
                f"AI analysis could not be completed: {str(e)}"
            ),
            "financial_impact": (
                "Financial impact could not be determined."
            ),
            "recommended_action": (
                "Manual finance operations review required."
            ),
            "prevention": (
                "Review the reconciliation process manually."
            )
        }


# ============================================================
# AI FINANCE SUMMARY
# ============================================================

def explain_finance_summary(summary_text):

    """
    Generate a short operational summary of the current
    reconciliation results.

    The return structure is kept compatible with the existing dashboard.
    """

    prompt = f"""
You are a finance operations analyst.

Review the reconciliation summary below and identify the most important
operational risk that a finance team should pay attention to.

RECONCILIATION SUMMARY
{summary_text}

Return ONLY one valid JSON object using exactly these fields:

{{
    "severity": "LOW | MEDIUM | HIGH | CRITICAL",
    "explanation": "A short, evidence-based summary of the main issue.",
    "recommended_action": "A short and practical next step for the finance team."
}}

Rules:
- Use only information present in the reconciliation summary.
- Do not invent causes, amounts, transaction details, fraud, or business impact.
- If the summary does not establish a root cause, do not claim one.
- Severity must be exactly LOW, MEDIUM, HIGH, or CRITICAL.
- Focus on the most important operational risk.
- Keep the response concise and suitable for a finance operations dashboard.
- Do not mention that you are an AI.
"""


    try:

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a finance operations analyst. "
                        "Return only valid JSON and stay strictly within the supplied evidence."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        result = response.choices[0].message.content
        parsed_result = _clean_json_response(result)

        return {
            "severity": _normalise_severity(
                parsed_result.get("severity")
            ),
            "explanation": _text_value(
                parsed_result.get("explanation"),
                "No risk summary was returned."
            ),
            "recommended_action": _text_value(
                parsed_result.get("recommended_action"),
                "Manual finance operations review required."
            )
        }


    except Exception as e:

        return {
            "severity": "UNKNOWN",
            "explanation": (
                f"AI summary could not be completed: {str(e)}"
            ),
            "recommended_action": (
                "Manual finance operations review required."
            )
        }
