# decision_engine.py
from typing import Dict, List


# ----- Deterministic rule engine ----- #
def recommend(product: Dict) -> Dict:
    """
    Given a product dict, return a decision summary including:
    - outcome (good/mixed/avoid)
    - rationale (why it's recommended or not)
    """
    outcome = "✅ Good match"
    rationale: List[str] = []

    # --- Check if product has conflicting skin types --- #
    skin_types = product.get("skin_types", [])
    if "dry" in skin_types and "oily" in skin_types:
        outcome = "⚠️ Mixed match"
        rationale.append(
            "Product suitable for both dry and oily skin types — mixed suitability.")

    # --- Comedogenic / sensitivity risk --- #
    if product.get("comedogenic_risk", "low") == "high":
        outcome = "⚠️ Use with caution"
        rationale.append("High comedogenic risk — may cause breakouts.")

    if product.get("sensitivity_risk", "low") == "high":
        outcome = "⚠️ Use with caution"
        rationale.append("High sensitivity risk — may irritate skin.")

    # --- Check if product explicitly avoids any skin types (if we expand later) --- #
    avoid = product.get("avoid_for", [])
    if avoid:
        rationale.append(f"Not ideal for: {', '.join(avoid)}")

    # --- Provide textual summary of benefits --- #
    pros = product.get("pros", [])
    if pros:
        rationale.append("Key benefits: " + ", ".join(pros))

    cons = product.get("cons", [])
    if cons:
        rationale.append("Limitations: " + ", ".join(cons))

    # --- Return deterministic summary --- #
    summary = {
        "outcome": outcome,
        "rationale": rationale,
        "skin_types": product.get("skin_types", []),
        "texture": product.get("texture", ""),
        "finish": product.get("finish", ""),
        "ingredient_intent": product.get("ingredient_intent", ""),
        "pros": product.get("pros", []),
        "cons": product.get("cons", []),
        "category": product.get("category", ""),
        "coverage": product.get("coverage"),
        "best_for": product.get("best_for", []),
        "avoid_for": product.get("avoid_for", []),
        "concerns_targeted": product.get("concerns_targeted", []),
        "concerns_not_ideal": product.get("concerns_not_ideal", []),
        "comedogenic_risk": product.get("comedogenic_risk", "low"),
        "sensitivity_risk": product.get("sensitivity_risk", "low")
    }

    return summary
