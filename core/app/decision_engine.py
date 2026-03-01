from constants import RiskLevel, SkinType, UserProfile
from typing import Dict, List, Optional


# ----- Fit score calculation ----- #
def compute_fit_score(product: Dict, user_profile: UserProfile) -> int:
    """
    Compute a 0-100 fit score for a product given a user profile.
    The score reflects how well the product's attributes align with
    the user's skin type, concerns, and sensitivities.
    """
    score = 65  # Start with a neutral score

    # --- Extract attributes from the user profile --- #
    user_profile_dict = user_profile.model_dump()
    user_skin_type: Optional[SkinType] = user_profile_dict.get(
        "skin_type", None)
    user_skin_type_val = user_skin_type.value if user_skin_type else ""
    user_concerns = user_profile_dict.get("concerns", [])
    user_sensitive = user_profile_dict.get("sensitive", False)

    # --- Extract attributes from the product --- #
    skin_types: List = product.get("skin_types", [])
    avoid_for: List = product.get("avoid_for", [])
    concerns_targeted: List = product.get(
        "concerns_targeted", [])
    concerns_not_ideal: List = product.get(
        "concerns_not_ideal", [])

    # --- Perform the skin type alignment --- #
    if user_skin_type_val:
        if user_skin_type_val in skin_types:
            score += 20
        elif user_skin_type_val in avoid_for:
            score -= 35

    # --- Perform concern matching --- #
    matched_concerns = [
        concern for concern in user_concerns if concern in concerns_targeted]
    # amplify the score by a positive factor to get a wider range
    score += len(matched_concerns) * 5
    conflicting_concerns = [
        concern for concern in user_concerns if concern in concerns_not_ideal]
    # assign a higher factor to conflicting concerns to get a tighter bound
    score -= len(conflicting_concerns) * 10

    # --- Risk penalties --- #
    if user_sensitive and product.get("sensitivity_risk", RiskLevel.LOW.value) == RiskLevel.HIGH.value:
        score -= 20

    # oily
    if user_skin_type_val and user_skin_type_val in [SkinType.OILY.value, SkinType.COMBINATION.value]:
        if product.get("comedogenic_risk", RiskLevel.LOW.value) == RiskLevel.HIGH.value:
            score -= 10

    fit_score = max(0, min(100, score))  # Ensure a score is between 0-100
    return fit_score


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
    fit_score = None

    # --- Product skin type conflict check --- #
    skin_types: List = product.get("skin_types", [])
    if SkinType.DRY.value in skin_types and SkinType.OILY.value in skin_types:
        outcome = "⚠️ Mixed match"
        rationale.append(
            "This product is suitable for both dry and oily skin types."
        )

    # --- Comedogenic / sensitivity risk --- #
    if product.get("comedogenic_risk", RiskLevel.LOW.value) == RiskLevel.HIGH.value:
        outcome = "⚠️ Use this product with caution"
        rationale.append(
            "This product has a high comedogenic risk and may cause breakouts."
        )

    if product.get("sensitivity_risk", RiskLevel.LOW.value) == RiskLevel.HIGH.value:
        outcome = "⚠️ Use this product with caution"
        rationale.append(
            "This product has a high sensitivity risk and may irritate the skin."
        )

    # --- Explicit avoid_for skin types --- #
    avoid: List = product.get("avoid_for", [])
    if avoid:
        rationale.append(
            f"This product is not ideal for: {', '.join(avoid)}")

    # --- Benefits and limitations --- #
    pros: List = product.get("pros", [])
    if pros:
        rationale.append(
            "The key benefits of this product include: " + ", ".join(pros)
        )

    cons: List = product.get("cons", [])
    if cons:
        rationale.append(
            "The limitations of this product include: " + ", ".join(cons)
        )

    # --- Personalization logic --- #
    if user_profile:
        personalized = True
        user_profile_dict = user_profile.model_dump()

        user_skin_type: Optional[SkinType] = user_profile_dict.get(
            "skin_type", None)
        user_skin_type_val = user_skin_type.value if user_skin_type else ""
        user_concerns = user_profile_dict.get("concerns", [])
        user_sensitive = user_profile_dict.get("sensitive", False)

        # --- Skin type alignment --- #
        if user_skin_type_val:
            if user_skin_type_val in skin_types:
                rationale.append(
                    f"This product is well aligned with your {user_skin_type_val} skin type."
                )
            elif user_skin_type_val in product.get("avoid_for", []):
                outcome = "❌ This product is not recommended"
                rationale.append(
                    f"This product is not suitable for your {user_skin_type_val} skin type."
                )

        # --- Concern targeting --- #
        concerns_targeted = product.get("concerns_targeted", [])
        concerns_not_ideal = product.get("concerns_not_ideal", [])

        matched_concerns = [
            concern for concern in user_concerns if concern in concerns_targeted]
        if matched_concerns:
            rationale.append(
                f"This product targets your concerns: {', '.join(matched_concerns)}"
            )

        conflicting_concerns = [
            concern for concern in user_concerns if concern in concerns_not_ideal]
        if conflicting_concerns:
            outcome = "⚠️ Use this product with caution"
            rationale.append(
                f"This product may not be ideal for your concerns: {', '.join(conflicting_concerns)}"
            )

        # --- Sensitivity override --- #
        if user_sensitive and product.get("sensitivity_risk", RiskLevel.LOW.value) == RiskLevel.HIGH.value:
            outcome = "❌ This product is not recommended"
            rationale.append(
                "This product has a high sensitivity risk level and you indicated having sensitive skin."
            )

        # --- Compute fit score --- #
        fit_score = compute_fit_score(product, user_profile)

    # --- Final summary --- #
    summary = {
        "outcome": outcome,
        "rationale": rationale,
        "personalized": personalized,
        "fit_score": fit_score,
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
