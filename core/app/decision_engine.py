from constants import RiskLevel, SkinType, UserProfile
from typing import Dict, List, Optional


# ----- Deterministic rule engine ----- #
def recommend(product: Dict, user_profile: Optional[UserProfile] = None) -> Dict:
    """
    Given a product and optional user profile, return a decision summary including:
    - outcome (good/mixed/avoid)
    - rationale (why it's recommended or not)
    - personalization flag
    """
    outcome = "✅ Good match"
    rationale: List[str] = []
    personalized = False

    # --- Product skin type conflict check --- #
    skin_types: List = product.get("skin_types", [])
    if SkinType.DRY.value in skin_types and SkinType.OILY.value in skin_types:
        outcome = "⚠️ Mixed match"
        rationale.append(
            "Product suitable for both dry and oily skin types — mixed suitability."
        )

    # --- Comedogenic / sensitivity risk --- #
    if product.get("comedogenic_risk", RiskLevel.LOW.value) == RiskLevel.HIGH.value:
        outcome = "⚠️ Use with caution"
        rationale.append("High comedogenic risk — may cause breakouts.")

    if product.get("sensitivity_risk", RiskLevel.LOW.value) == RiskLevel.HIGH.value:
        outcome = "⚠️ Use with caution"
        rationale.append("High sensitivity risk — may irritate skin.")

    # --- Explicit avoid_for skin types --- #
    avoid: List = product.get("avoid_for", [])
    if avoid:
        rationale.append(f"Not ideal for: {', '.join(avoid)}")

    # --- Benefits and limitations --- #
    pros: List = product.get("pros", [])
    if pros:
        rationale.append("Key benefits: " + ", ".join(pros))

    cons: List = product.get("cons", [])
    if cons:
        rationale.append("Limitations: " + ", ".join(cons))

    # --- Personalization logic --- #
    if user_profile:
        personalized = True
        user_profile_dict = user_profile.model_dump()

        user_skin_type = user_profile_dict.get("skin_type", None)
        user_concerns = user_profile_dict.get("concerns", [])
        user_sensitive = user_profile_dict.get("sensitive", False)

        # --- Skin type alignment --- #
        if user_skin_type:
            if user_skin_type in skin_types:
                rationale.append(
                    f"Well aligned with your {user_skin_type} skin type.")
            elif user_skin_type in product.get("avoid_for", []):
                outcome = "❌ Not recommended"
                rationale.append(
                    f"Not suitable for your {user_skin_type} skin type.")

        # --- Concern targeting --- #
        concerns_targeted = product.get("concerns_targeted", [])
        concerns_not_ideal = product.get("concerns_not_ideal", [])

        matched_concerns = [c for c in user_concerns if c in concerns_targeted]
        if matched_concerns:
            rationale.append(
                f"Targets your concerns: {', '.join(matched_concerns)}")

        conflicting_concerns = [
            c for c in user_concerns if c in concerns_not_ideal]
        if conflicting_concerns:
            outcome = "⚠️ Use with caution"
            rationale.append(
                f"May not be ideal for your concerns: {', '.join(conflicting_concerns)}"
            )

        # --- Sensitivity override --- #
        if user_sensitive and product.get("sensitivity_risk", RiskLevel.LOW.value) == RiskLevel.HIGH.value:
            outcome = "❌ Not recommended"
            rationale.append(
                "High sensitivity risk and you indicated sensitive skin.")

    # --- Final summary --- #
    summary = {
        "outcome": outcome,
        "rationale": rationale,
        "personalized": personalized,
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
        "comedogenic_risk": product.get("comedogenic_risk", RiskLevel.LOW.value),
        "sensitivity_risk": product.get("sensitivity_risk", RiskLevel.LOW.value)
    }

    return summary
